"""Offline safety regressions; synthetic issues and fake transports only."""
import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
import urllib.error
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('native_relations', ROOT / 'scripts/reconcile_native_relations.py')
native = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(native)


def tiny_backlog():
    return {'repository': native.REPOSITORY,
        'program': {'id': 'PAPER', 'parent': None, 'blocked_by': []},
        'epics': [{'id': 'PAPER-01', 'parent': 'PAPER', 'blocked_by': [], 'work_packages': [
            {'id': 'PAPER-01.01', 'parent': 'PAPER-01', 'blocked_by': []},
            {'id': 'PAPER-01.02', 'parent': 'PAPER-01', 'blocked_by': ['PAPER-01.01']}]}]}


def tiny_map(backlog_bytes):
    keys = ['PAPER', 'PAPER-01', 'PAPER-01.01', 'PAPER-01.02']
    # Deliberately nonsequential issue numbers, unrelated to stable-ID order.
    numbers = [73, 8, 211, 19]
    return {'schema_version': '0.1.0', 'repository': native.REPOSITORY,
            'repository_id': native.REPOSITORY_ID,
            'backlog_sha256': hashlib.sha256(backlog_bytes).hexdigest(),
            'issues': {key: {'id': 4_000_000_000 + number, 'node_id': 'I_synthetic_' + str(number),
                            'number': number, 'url': f'https://github.com/{native.REPOSITORY}/issues/{number}'}
                       for key, number in zip(keys, numbers)}}


def graph_identity(row):
    return {'id': row['node_id'], 'fullDatabaseId': str(row['id']), 'number': row['number'],
            'url': row['url'], 'repository': {'nameWithOwner': native.REPOSITORY}}


def connection(rows):
    return {'nodes': rows, 'totalCount': len(rows), 'pageInfo': {'hasNextPage': False}}


class FakeClient:
    def __init__(self, scope, honor_writes=True):
        self.nodes, self.posts, self.head_checks = {}, [], 0
        self.honor_writes = honor_writes
        for key, row in scope['identities'].items():
            self.nodes[row['node_id']] = {**graph_identity(row), '__typename': 'Issue',
                'body': f'<!-- pick-your-ai-papers:{key} -->\nSYNTHETIC TEST ONLY', 'state': 'OPEN',
                'createdAt': native.utc_timestamp(time.time() - 7200), 'parent': None,
                'blockedBy': connection([]), 'subIssues': connection([]),
                'timelineItems': {'nodes': [], 'pageInfo': {'hasNextPage': False}}}

    def read_nodes(self, identities):
        # Reverse results to prove mapping does not use response order.
        return [copy.deepcopy(self.nodes[row['node_id']]) for row in reversed(identities)]

    def verify_head(self, sha):
        self.head_checks += 1

    def request(self, path, method='GET', payload=None):
        if method != 'POST':
            raise AssertionError('Unexpected request in fake')
        self.posts.append((path, copy.deepcopy(payload)))
        if not self.honor_writes:
            return {'accepted': True}
        number = int(path.split('/issues/')[1].split('/')[0])
        target = next(n for n in self.nodes.values() if n['number'] == number)
        key = 'sub_issue_id' if path.endswith('/sub_issues') else 'issue_id'
        other = next(n for n in self.nodes.values() if int(n['fullDatabaseId']) == payload[key])
        if key == 'sub_issue_id':
            if other['parent'] is not None:
                raise AssertionError('Refused concurrent replacement')
            other['parent'] = graph_identity(native.normalized_identity(target))
            target['subIssues']['nodes'].append(graph_identity(native.normalized_identity(other)))
            target['subIssues']['totalCount'] += 1
        else:
            target['blockedBy']['nodes'].append(graph_identity(native.normalized_identity(other)))
            target['blockedBy']['totalCount'] += 1
        return {'accepted': True}


def fast_budget(activity, max_writes):
    clock = [time.time()]
    def sleep(seconds):
        clock[0] += seconds
    return native.MutationBudget(activity, max_writes, clock=lambda: clock[0], sleep=sleep)


def project_response(item_id='PVTI_synthetic', more=False, cursor=None):
    return {'data': {'organization': {'projectV2': {
        'id': 'PVT_synthetic', 'number': 9, 'title': 'Synthetic test Project',
        'url': native.PROJECT_URL, 'public': True, 'closed': False, 'shortDescription': 'Test only',
        'fields': connection([]), 'views': connection([]),
        'repositories': connection([{'nameWithOwner': native.REPOSITORY}]), 'teams': connection([]),
        'items': {'nodes': [{'id': item_id, 'isArchived': False, 'content': None, 'fieldValues': connection([])}],
                  'pageInfo': {'hasNextPage': more, 'endCursor': cursor}}
    }}}}


class ProjectClient:
    def __init__(self, responses):
        self.responses, self.calls = responses, []

    def request(self, path, method, payload):
        self.calls.append((path, method, copy.deepcopy(payload)))
        response = self.responses[len(self.calls) - 1]
        if isinstance(response, Exception):
            raise response
        return copy.deepcopy(response)


class NativeRelationshipTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='papers-native-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'planning').mkdir()
        self.backlog_bytes = (json.dumps(tiny_backlog(), indent=2) + '\n').encode()
        (self.root / 'planning/project-backlog.json').write_bytes(self.backlog_bytes)
        self.mapping = tiny_map(self.backlog_bytes)
        self.save_map()
        self.scope = native.load_scope(self.root)

    def save_map(self):
        (self.root / 'planning/issue-map.json').write_text(json.dumps(self.mapping))

    def run_reconcile(self, client, max_writes=450):
        report = native.new_report(self.scope, 'a' * 40)
        checkpoints = []
        native.reconcile(client, self.scope, 'a' * 40, report,
                         lambda: checkpoints.append(copy.deepcopy(report)),
                         max_writes=max_writes, budget_factory=fast_budget)
        return report, checkpoints

    def test_actual_map_identities_drive_every_mutation_and_rerun_is_idempotent(self):
        client = FakeClient(self.scope)
        report, _ = self.run_reconcile(client)
        self.assertTrue(report['verified'])
        self.assertEqual(len(client.posts), 4)
        self.assertIn((native.PREFIX + '/issues/73/sub_issues',
                       {'sub_issue_id': 4_000_000_008, 'replace_parent': False}), client.posts)
        self.assertIn((native.PREFIX + '/issues/19/dependencies/blocked_by',
                       {'issue_id': 4_000_000_211}), client.posts)
        repeated, _ = self.run_reconcile(client)
        self.assertTrue(repeated['verified'])
        self.assertEqual(repeated['mutation_attempts'], [])
        self.assertEqual(len(client.posts), 4)

    def test_map_cannot_escape_repository_or_reuse_identity(self):
        for change in ['repository', 'repository_id', 'url', 'duplicate', 'digest']:
            with self.subTest(change=change):
                self.mapping = tiny_map(self.backlog_bytes)
                if change == 'repository': self.mapping['repository'] = 'other/repo'
                elif change == 'repository_id': self.mapping['repository_id'] += 1
                elif change == 'url': self.mapping['issues']['PAPER']['url'] = 'https://github.com/other/repo/issues/73'
                elif change == 'duplicate': self.mapping['issues']['PAPER-01'] = self.mapping['issues']['PAPER']
                else: self.mapping['backlog_sha256'] = '0' * 64
                self.save_map()
                with self.assertRaises(native.ReconcileError): native.load_scope(self.root)

    def test_missing_identity_or_duplicate_json_keys_fail_before_network(self):
        del self.mapping['issues']['PAPER-01.02']; self.save_map()
        with self.assertRaises(native.ReconcileError): native.load_scope(self.root)
        (self.root / 'planning/issue-map.json').write_text('{"issues":{},"issues":{}}')
        with self.assertRaisesRegex(native.ReconcileError, 'Duplicate JSON'): native.load_scope(self.root)

    def test_live_identity_and_stable_marker_are_both_required(self):
        for change in ['id', 'marker', 'type', 'repository']:
            with self.subTest(change=change):
                client = FakeClient(self.scope)
                issue = client.nodes[self.scope['identities']['PAPER-01']['node_id']]
                if change == 'id': issue['fullDatabaseId'] = '1'
                elif change == 'marker': issue['body'] = '<!-- pick-your-ai-papers:PAPER-02 -->'
                elif change == 'type': issue['__typename'] = 'PullRequest'
                else: issue['repository']['nameWithOwner'] = 'other/repo'
                with self.assertRaises(native.ReconcileError): self.run_reconcile(client)
                self.assertEqual(client.posts, [])

    def test_conflicting_parent_stops_all_writes(self):
        client = FakeClient(self.scope)
        child = client.nodes[self.scope['identities']['PAPER-01']['node_id']]
        child['parent'] = graph_identity(self.scope['identities']['PAPER-01.01'])
        with self.assertRaisesRegex(native.ReconcileError, 'Conflicting native parent'): self.run_reconcile(client)
        self.assertEqual(client.posts, [])

    def test_cross_repository_program_parent_is_preserved_and_excluded(self):
        client = FakeClient(self.scope)
        root = client.nodes[self.scope['identities']['PAPER']['node_id']]
        root['parent'] = {'id': 'I_synthetic_parent', 'fullDatabaseId': '509000', 'number': 509,
            'url': 'https://github.com/Pick-Your-AI/pick-your-ai-research/issues/509',
            'repository': {'nameWithOwner': 'Pick-Your-AI/pick-your-ai-research'}}
        report, _ = self.run_reconcile(client)
        self.assertTrue(report['verified'])
        self.assertTrue(all(path.startswith(native.PREFIX + '/') for path, _ in client.posts))
        self.assertEqual(report['observed']['PAPER']['parent']['number'], 509)

    def test_accepted_response_without_readback_is_never_verified(self):
        client = FakeClient(self.scope, honor_writes=False)
        report = native.new_report(self.scope)
        snapshots = []
        with self.assertRaisesRegex(native.ReconcileError, 'readback did not match'):
            native.reconcile(client, self.scope, 'a' * 40, report,
                lambda: snapshots.append(copy.deepcopy(report)), budget_factory=fast_budget)
        self.assertFalse(report['verified'])
        self.assertEqual(len(client.posts), 1)
        self.assertEqual(report['mutation_attempts'][0]['outcome'], 'request_accepted_readback_pending')
        self.assertEqual(snapshots[-1]['mutation_attempts'][0]['outcome'], 'request_accepted_readback_pending')

    def test_partial_connections_are_never_treated_as_complete(self):
        for field in ['blockedBy', 'subIssues', 'timelineItems']:
            with self.subTest(field=field):
                client = FakeClient(self.scope)
                next(iter(client.nodes.values()))[field]['pageInfo']['hasNextPage'] = True
                with self.assertRaises(native.ReconcileError): self.run_reconcile(client)
                self.assertEqual(client.posts, [])

    def test_existing_extra_dependencies_are_preserved_but_cycles_are_rejected(self):
        client = FakeClient(self.scope)
        first = client.nodes[self.scope['identities']['PAPER-01.01']['node_id']]
        first['blockedBy'] = connection([graph_identity(self.scope['identities']['PAPER-01.02'])])
        with self.assertRaisesRegex(native.ReconcileError, 'cycle'): self.run_reconcile(client)
        self.assertEqual(client.posts, [])

    def test_budget_reconstructs_prior_activity_and_reserves_ambiguous_attempts(self):
        now = [10_000.0]
        activity = [{'at': native.utc_timestamp(9_999.0)} for _ in range(449)]
        sleeps = []
        def sleep(seconds): sleeps.append(seconds); now[0] += seconds
        budget = native.MutationBudget(activity, clock=lambda: now[0], sleep=sleep)
        budget.reserve()
        with self.assertRaises(native.BudgetPause): budget.reserve()
        self.assertEqual(len(budget.attempt_times), 1)
        self.assertEqual(sleeps, [5.0])
        now[0] = 13_601.0
        budget.reserve()
        self.assertEqual(len(budget.attempt_times), 2)

    def test_budget_caps_run_and_paces_writes(self):
        now = [10_000.0]
        sleeps = []
        def sleep(seconds): sleeps.append(seconds); now[0] += seconds
        budget = native.MutationBudget([], max_writes=2, clock=lambda: now[0], sleep=sleep)
        budget.reserve(); budget.reserve()
        with self.assertRaises(native.BudgetPause): budget.reserve()
        self.assertGreaterEqual(budget.attempt_times[1] - budget.attempt_times[0], 5.0)
        self.assertEqual(len(budget.attempt_times), 2)

    def test_head_recheck_follows_pacing_and_posts_wait_after_prior_completion(self):
        now, trace, post_times = [time.time()], [], []
        class TimedClient(FakeClient):
            def verify_head(self, sha):
                trace.append('head')
                now[0] += 8 if not self.posts else 0.1
                return super().verify_head(sha)
            def request(self, *args):
                trace.append('post'); post_times.append(now[0])
                result = super().request(*args)
                now[0] += 3
                return result
        def budget_factory(activity, max_writes):
            def sleep(seconds):
                trace.append('wait'); now[0] += seconds
            return native.MutationBudget(activity, max_writes, clock=lambda: now[0], sleep=sleep)
        report = native.new_report(self.scope)
        native.reconcile(TimedClient(self.scope), self.scope, 'a' * 40, report, lambda: None,
                         budget_factory=budget_factory)
        self.assertEqual(trace[:5], ['head', 'post', 'wait', 'head', 'post'])
        self.assertTrue(all(b - a >= 8 for a, b in zip(post_times, post_times[1:])))

    def test_failed_api_does_not_retry_or_print_token_or_server_payload(self):
        secret = 'SYNTHETIC_TOKEN_DO_NOT_PRINT'
        for status in [403, 429, 422, 500]:
            with self.subTest(status=status):
                class Opener:
                    calls = 0
                    def open(self, request, timeout):
                        self.calls += 1
                        raise urllib.error.HTTPError(request.full_url, status, 'SYNTHETIC private server error', {}, io.BytesIO(secret.encode()))
                opener = Opener(); client = native.GitHubClient(secret, opener)
                with self.assertRaises(native.ApiFailure) as caught:
                    client.request(native.PREFIX)
                self.assertEqual(opener.calls, 1)
                self.assertNotIn(secret, str(caught.exception))
                self.assertNotIn('private server error', str(caught.exception))

    def test_transport_rejects_external_targets_and_destructive_methods(self):
        client = native.GitHubClient('SYNTHETIC')
        for path, method, payload in [('https://evil.example', 'GET', None), ('/repos/other/repo', 'GET', None),
            (native.PREFIX + '/issues/1', 'PATCH', {'state': 'closed'}),
            (native.PREFIX + '/issues/1/sub_issues', 'POST', {'sub_issue_id': 2, 'replace_parent': True}),
            ('/graphql', 'POST', {'query': 'mutation { dangerous }'})]:
            with self.subTest(path=path, method=method):
                with self.assertRaises(native.ReconcileError): client.request(path, method, payload)
        self.assertEqual(client.requests, 0)

    def test_apply_context_requires_exact_repo_actor_branch_and_nonforced_push(self):
        env = {'GITHUB_ACTIONS': 'true', 'GITHUB_EVENT_NAME': 'push', 'GITHUB_REPOSITORY': native.REPOSITORY,
            'GITHUB_REPOSITORY_ID': str(native.REPOSITORY_ID), 'GITHUB_REF': 'refs/heads/' + native.BRANCH,
            'GITHUB_ACTOR': native.ACTOR, 'GITHUB_ACTOR_ID': str(native.ACTOR_ID),
            'GITHUB_TRIGGERING_ACTOR': native.ACTOR, 'GITHUB_SHA': 'a' * 40}
        event = {'after': 'a' * 40, 'ref': env['GITHUB_REF'], 'deleted': False, 'forced': False,
            'repository': {'id': native.REPOSITORY_ID, 'full_name': native.REPOSITORY, 'fork': False},
            'sender': {'login': native.ACTOR, 'id': native.ACTOR_ID}}
        self.assertEqual(native.validate_context(env, event), 'a' * 40)
        for field, value in [('GITHUB_REPOSITORY', 'other/repo'), ('GITHUB_EVENT_NAME', 'pull_request'),
                             ('GITHUB_REF', 'refs/heads/main'), ('GITHUB_ACTOR_ID', '123')]:
            with self.subTest(field=field):
                with self.assertRaises(native.ReconcileError): native.validate_context({**env, field: value}, event)
        with self.assertRaises(native.ReconcileError): native.validate_context(env, {**event, 'forced': True})

    def test_summary_contains_actual_observations_and_attempt_timestamps(self):
        report, _ = self.run_reconcile(FakeClient(self.scope))
        path = self.root / 'summary.md'
        native.summarize(report, path)
        text = path.read_text()
        self.assertIn('"attempted_at"', text)
        self.assertIn('"readback_verified"', text)
        self.assertIn('"number": 211', text)
        self.assertIn('Cross-repository research #509', text)

    def test_connector_checkpoint_is_actual_json_without_issue_body_material(self):
        client = FakeClient(self.scope)
        for row in client.nodes.values():
            row['body'] += '\nSYNTHETIC_PRIVATE_BODY_MUST_NOT_BE_LOGGED'
        report, _ = self.run_reconcile(client)
        line = native.checkpoint_log(report)
        self.assertTrue(line.startswith('PAPERS_NATIVE_CHECKPOINT_JSON='))
        self.assertEqual(json.loads(line.split('=', 1)[1]), report)
        self.assertNotIn('SYNTHETIC_PRIVATE_BODY_MUST_NOT_BE_LOGGED', line)
        self.assertIn('readback_verified', line)

    def test_optional_project_query_is_exact_read_only_and_paginates_actual_items(self):
        client = ProjectClient([project_response('PVTI_synthetic_1', True, 'next_page'),
                                project_response('PVTI_synthetic_2')])
        report = {'status': 'verified', 'verified': True}
        native.observe_optional_project(client, report)
        self.assertTrue(report['verified'])
        self.assertEqual(report['status'], 'verified')
        observation = report['project_readback']
        self.assertTrue(observation['connections_complete'])
        self.assertFalse(observation['configuration_accepted'])
        self.assertFalse(observation['collaborator_roles_verified'])
        self.assertEqual([row['id'] for row in observation['project']['items']],
                         ['PVTI_synthetic_1', 'PVTI_synthetic_2'])
        self.assertEqual([call[2]['variables'] for call in client.calls], [{'after': None}, {'after': 'next_page'}])
        self.assertTrue(all(call[:2] == ('/graphql', 'POST') and call[2]['query'] == native.PROJECT_QUERY
                            for call in client.calls))
        self.assertIn('organization(login:"Pick-Your-AI")', native.PROJECT_QUERY)
        self.assertIn('projectV2(number:9)', native.PROJECT_QUERY)
        transport = native.GitHubClient('SYNTHETIC')
        with self.assertRaises(native.ReconcileError):
            transport.request('/graphql', 'POST', {'query': native.PROJECT_QUERY.replace('number:9', 'number:10')})
        self.assertEqual(transport.requests, 0)

    def test_optional_project_denial_or_incomplete_data_never_changes_native_outcome(self):
        responses = [native.ApiFailure('GitHub HTTP 403; no retry'), native.ApiFailure('GitHub HTTP 429; no retry'),
                     {'errors': [{'message': 'SYNTHETIC private error'}]}, project_response(), project_response()]
        responses[-2]['data']['organization']['projectV2']['public'] = False
        responses[-1]['data']['organization']['projectV2']['fields']['pageInfo']['hasNextPage'] = True
        for response in responses:
            for status, verified in [('verified', True), ('budget_paused', False)]:
                with self.subTest(status=status, response=type(response).__name__):
                    client = ProjectClient([response]); report = {'status': status, 'verified': verified}
                    native.observe_optional_project(client, report)
                    self.assertEqual(report['status'], status)
                    self.assertIs(report['verified'], verified)
                    self.assertEqual(report['project_readback']['status'], 'unverified')
                    self.assertNotIn('project', report['project_readback'])
                    self.assertNotIn('SYNTHETIC private error', json.dumps(report))
                    self.assertEqual(len(client.calls), 1)
        client = ProjectClient([])
        native.observe_optional_project(client, {'status': 'blocked', 'verified': False})
        self.assertEqual(client.calls, [])

    def test_optional_project_has_a_hard_three_page_bound(self):
        client = ProjectClient([project_response('PVTI_' + str(i), True, 'cursor_' + str(i)) for i in range(3)])
        report = {'status': 'verified', 'verified': True}
        native.observe_optional_project(client, report)
        self.assertEqual(len(client.calls), 3)
        self.assertEqual(report['project_readback']['status'], 'unverified')
        self.assertTrue(report['verified'])


if __name__ == '__main__':
    unittest.main()
