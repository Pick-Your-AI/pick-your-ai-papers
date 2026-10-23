"""Independent offline regressions for live-state preservation during setup.

Clients are local fakes. No GitHub command, credential lookup or remote mutation
is performed by this suite.
"""
import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import bootstrap_github as bootstrap
from github_support import FULL_NAME, SetupError


class StateClient:
    def __init__(self, state=None):
        self.state = dict(state or {})
        self.calls = []

    def checkpoint(self):
        pass

    def mutate(self, name, input_type, data, selection):
        self.calls.append((name, copy.deepcopy(data)))
        if name == 'updateProjectV2':
            return {'projectV2': {**project(), 'public': True}}
        return {}


def project(public=False):
    return {'id': 'project.synthetic', 'number': 99, 'title': 'Synthetic target',
            'url': 'https://github.com/orgs/Pick-Your-AI/projects/99',
            'public': public, 'closed': False,
            'repositories': {'nodes': [{'nameWithOwner': FULL_NAME}], 'pageInfo': {'hasNextPage': False}}}


def preflight(row):
    return {'projects': [row], 'organization_id': 'org.synthetic',
            'teams': [{'name': 'Research Lead Maintainers', 'node_id': 'team.synthetic'}]}


class BootstrapStateReviewTests(unittest.TestCase):
    def test_preexisting_private_project_is_not_exposed(self):
        client = StateClient()
        with self.assertRaisesRegex(SetupError, 'private'):
            bootstrap.ensure_project(client, preflight(project()), {'node_id': 'repo.synthetic'},
                {'title': 'Synthetic target', 'description': 'Synthetic', 'readme': 'Synthetic'})
        self.assertEqual(client.calls, [])

    def test_interrupted_initial_public_toggle_does_not_authorize_later_reexposure(self):
        client = StateClient({'created_project_id': 'project.synthetic'})
        spec = {'title': 'Synthetic target', 'description': 'Synthetic', 'readme': 'Synthetic'}
        result = bootstrap.ensure_project(client, preflight(project()), {'node_id': 'repo.synthetic'}, spec)
        self.assertTrue(result['public'])
        self.assertTrue(any(name == 'updateProjectV2' for name, _ in client.calls))
        client.calls.clear()
        # A later administrator changes the previously initialized Project to private.
        with self.assertRaisesRegex(SetupError, 'private'):
            bootstrap.ensure_project(client, preflight(project()), {'node_id': 'repo.synthetic'}, spec)
        self.assertEqual(client.calls, [])

    def test_duplicate_field_names_stop_before_mutation(self):
        client = StateClient()
        fields = [{'id': ident, 'name': 'Status', 'dataType': 'SINGLE_SELECT',
                   'options': [{'id': 'option.' + ident, 'name': 'Backlog', 'color': 'GRAY', 'description': ''}]}
                  for ident in ('field.one', 'field.two')]
        with patch('bootstrap_github.connection_nodes', return_value=fields):
            with self.assertRaisesRegex(SetupError, '[Dd]uplicate'):
                bootstrap.ensure_fields(client, project(True), {'fields': [
                    {'name': 'Status', 'data_type': 'SINGLE_SELECT', 'options': ['Backlog', 'Blocked']}]})
        self.assertEqual(client.calls, [])

    def test_duplicate_memberships_cannot_hide_an_archived_item(self):
        client = StateClient()
        items = [{'id': ident, 'content': {'id': 'issue.synthetic'}, 'isArchived': archived,
                  'fieldValues': {'nodes': [], 'pageInfo': {'hasNextPage': False}}}
                 for ident, archived in [('item.archived', True), ('item.active', False)]]
        with patch('bootstrap_github.fetch_items', return_value=items):
            with self.assertRaisesRegex(SetupError, '[Dd]uplicate|ambiguous|archived'):
                bootstrap.ensure_items(client, project(True), {'fields': []},
                    {'program': {'id': 'PAPER'}, 'epics': []}, {'PAPER': {'node_id': 'issue.synthetic'}}, {})
        self.assertEqual(client.calls, [])

    def test_existing_closed_issue_and_assignees_are_preserved(self):
        original = {'number': 1, 'id': 10, 'node_id': 'issue.synthetic', 'state': 'closed',
                    'body': '<!-- pick-your-ai-papers:PAPER -->\nMaintainer-edited live text.',
                    'assignees': [{'login': 'synthetic-maintainer'}]}
        calls = []
        class Client(StateClient):
            def api(self, endpoint, method='GET', **kwargs):
                calls.append((endpoint, method))
                if method != 'GET':
                    raise AssertionError('Existing issue must not be rewritten')
                return [copy.deepcopy(original)]
        actual = bootstrap.ensure_issues(Client(), {'program': {'id': 'PAPER'}, 'epics': []})
        self.assertEqual(actual['PAPER'], original)
        self.assertEqual([method for _, method in calls], ['GET'])

    def test_branch_changed_during_staging_is_never_overwritten(self):
        class Client(StateClient):
            def optional(self, endpoint):
                return {'object': {'sha': 'branch-before'}}

            def api(self, endpoint, method='GET', payload=None, **kwargs):
                self.calls.append((method, endpoint))
                if endpoint.endswith('/git/ref/heads/main'):
                    return {'object': {'sha': 'default-head'}}
                if '/git/commits/branch-before' in endpoint:
                    return {'tree': {'sha': 'tree-before'}}
                if endpoint.endswith('/git/trees') and method == 'POST':
                    return {'sha': 'tree-after'}
                if endpoint.endswith('/git/commits') and method == 'POST':
                    return {'sha': 'new-commit'}
                if endpoint.endswith('/git/ref/heads/' + bootstrap.BRANCH):
                    return {'object': {'sha': 'concurrent-maintainer-commit'}}
                raise AssertionError('Unexpected API call: ' + method + ' ' + endpoint)
        client = Client({'scaffold_branch_head': 'branch-before'})
        with patch('bootstrap_github.scaffold_entries', return_value=[{'path': 'README.md', 'content': 'Synthetic'}]):
            with self.assertRaisesRegex(SetupError, 'Branch changed'):
                bootstrap.stage_scaffold_pr(client, {'default_branch': 'main'}, Path('/synthetic'))
        self.assertFalse(any(method == 'PATCH' or '/git/refs' in endpoint for method, endpoint in client.calls))


if __name__ == '__main__':
    unittest.main()
