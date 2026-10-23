#!/usr/bin/env python3
"""Reconcile only declared, same-repository papers issue relationships.

Offline by default. --apply is restricted to the pinned repository, actor and
foundation push context. No issue text/state/assignee, Project, branch, review,
scientific record or cross-repository parent is mutated. Every write is followed
by actual readback; request success alone never becomes a verified relationship.

planning/issue-map.json contains schema_version, repository, repository_id,
backlog_sha256 (exact file bytes), and issues keyed by stable PAPER identifier.
Each identity has actual REST id, GraphQL node_id, issue number and canonical url.
Relationship declarations come only from the hash-bound project-backlog.json.

GitHub API references (inspected 2026-10-23):
https://docs.github.com/en/rest/issues/sub-issues
https://docs.github.com/en/rest/issues/issue-dependencies
https://docs.github.com/en/graphql/reference/issues
https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPOSITORY = 'Pick-Your-AI/pick-your-ai-papers'
REPOSITORY_ID = 1430404173
BRANCH = 'contrib/papers-bootstrap/foundation'
ACTOR = 'CompleteDotTech'
ACTOR_ID = 5861166
API_VERSION = '2026-03-10'
OPT_IN = '[native-relationships]'
MAX_WRITES = 450
INTERVAL_SECONDS = 5.0
BATCH_SIZE = 20
MARKER = re.compile(r'<!-- pick-your-ai-papers:(PAPER(?:-\d{2}(?:\.\d{2})?)?) -->')
STABLE_ID = re.compile(r'PAPER(?:-\d{2}(?:\.\d{2})?)?\Z')
SHA = re.compile(r'[0-9a-f]{40}\Z')
NODE_ID = re.compile(r'[A-Za-z0-9_+=/-]{1,200}\Z')
PREFIX = '/repos/' + REPOSITORY
IDENTITY = 'id fullDatabaseId number url repository{nameWithOwner}'
READ_QUERY = '''query($ids:[ID!]!,$since:DateTime!){
 nodes(ids:$ids){__typename ... on Issue{
  id fullDatabaseId number url body state createdAt repository{nameWithOwner}
  parent{''' + IDENTITY + '''}
  blockedBy(first:100){nodes{''' + IDENTITY + '''}totalCount pageInfo{hasNextPage}}
  subIssues(first:100){nodes{''' + IDENTITY + '''}totalCount pageInfo{hasNextPage}}
  timelineItems(first:100,since:$since,itemTypes:[PARENT_ISSUE_ADDED_EVENT,BLOCKED_BY_ADDED_EVENT]){
   nodes{__typename ... on ParentIssueAddedEvent{id createdAt}
    ... on BlockedByAddedEvent{id createdAt}}
   pageInfo{hasNextPage}}
 }} rateLimit{remaining resetAt}}
'''
# Optional observation of the single Project the user authorized. No organization
# names, project numbers, credentials or query text are supplied by the caller.
PROJECT_NUMBER = 9
PROJECT_URL = 'https://github.com/orgs/Pick-Your-AI/projects/9'
PROJECT_QUERY = '''query($after:String){organization(login:"Pick-Your-AI"){
 projectV2(number:9){id number title url public closed shortDescription
  repositories(first:100){nodes{nameWithOwner}pageInfo{hasNextPage}}
  teams(first:100){nodes{name slug}pageInfo{hasNextPage}}
  fields(first:100){nodes{
   ... on ProjectV2FieldCommon{id name dataType databaseId}
   ... on ProjectV2SingleSelectField{options{id name color description}}
  }pageInfo{hasNextPage}}
  views(first:100){nodes{id number name layout filter
   fields(first:100){nodes{... on ProjectV2FieldCommon{id name}}pageInfo{hasNextPage}}
   groupByFields(first:100){nodes{... on ProjectV2FieldCommon{id name}}pageInfo{hasNextPage}}
   verticalGroupByFields(first:100){nodes{... on ProjectV2FieldCommon{id name}}pageInfo{hasNextPage}}
   sortByFields(first:100){nodes{direction field{... on ProjectV2FieldCommon{id name}}}pageInfo{hasNextPage}}
  }pageInfo{hasNextPage}}
  items(first:100,after:$after,archivedStates:[ARCHIVED,NOT_ARCHIVED]){nodes{id isArchived
   content{__typename ... on Issue{id number url repository{nameWithOwner}}}
   fieldValues(first:100){nodes{__typename
    ... on ProjectV2ItemFieldSingleSelectValue{name optionId field{... on ProjectV2FieldCommon{id name}}}
    ... on ProjectV2ItemFieldTextValue{text field{... on ProjectV2FieldCommon{id name}}}
    ... on ProjectV2ItemFieldNumberValue{number field{... on ProjectV2FieldCommon{id name}}}
   }pageInfo{hasNextPage}}
  }pageInfo{hasNextPage endCursor}}
 }}}
'''


class ReconcileError(RuntimeError):
    pass


class BudgetPause(ReconcileError):
    pass


class ApiFailure(ReconcileError):
    pass


def utc_timestamp(epoch=None):
    return datetime.fromtimestamp(time.time() if epoch is None else epoch, timezone.utc).isoformat(timespec='seconds')


def epoch(value):
    if not isinstance(value, str):
        raise ReconcileError('Missing or invalid observed activity timestamp')
    try:
        result = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if result.tzinfo is None:
            raise ValueError('timezone')
        return result.timestamp()
    except ValueError as error:
        raise ReconcileError('Missing or invalid observed activity timestamp') from error


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ReconcileError('Duplicate JSON key in planning input')
            result[key] = value
        return result
    try:
        return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=unique,
                          parse_constant=lambda _: (_ for _ in ()).throw(ReconcileError('Invalid JSON numeric constant')))
    except (ValueError, OSError) as error:
        raise ReconcileError('Cannot read a valid planning JSON file') from error


def write_report(path, report):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    temporary.replace(path)


def acyclic(edges):
    seen, active = set(), set()
    def visit(node):
        if node in active:
            raise ReconcileError('Declared or combined live dependency graph has a cycle')
        if node in seen:
            return
        active.add(node)
        for dependency in edges.get(node, []):
            visit(dependency)
        active.remove(node); seen.add(node)
    for node in edges:
        visit(node)


def load_scope(root):
    root = Path(root)
    map_path, backlog_path = root / 'planning/issue-map.json', root / 'planning/project-backlog.json'
    if map_path.is_symlink() or backlog_path.is_symlink():
        raise ReconcileError('Planning inputs must be regular repository files')
    issue_map, backlog = load_json(map_path), load_json(backlog_path)
    required = {'schema_version', 'repository', 'repository_id', 'backlog_sha256', 'issues'}
    if not isinstance(issue_map, dict) or set(issue_map) != required:
        raise ReconcileError('Issue map has an unsupported shape')
    if (issue_map['schema_version'] != '0.1.0' or issue_map['repository'] != REPOSITORY
            or type(issue_map['repository_id']) is not int or issue_map['repository_id'] != REPOSITORY_ID
            or backlog.get('repository') != REPOSITORY):
        raise ReconcileError('Planning input is outside the exact authorized repository')
    backlog_digest = hashlib.sha256(backlog_path.read_bytes()).hexdigest()
    if issue_map['backlog_sha256'] != backlog_digest:
        raise ReconcileError('Issue map does not bind the exact backlog bytes')
    try:
        rows = [backlog['program']]
        for epic in backlog['epics']:
            rows.append(epic); rows.extend(epic['work_packages'])
    except (KeyError, TypeError) as error:
        raise ReconcileError('Backlog hierarchy is malformed') from error
    records, identities = {}, issue_map['issues']
    if not isinstance(identities, dict) or not 1 <= len(rows) <= 200:
        raise ReconcileError('Issue identity inventory is missing or outside the bounded scope')
    for row in rows:
        key = row.get('id')
        if not isinstance(key, str) or not STABLE_ID.fullmatch(key) or key in records:
            raise ReconcileError('Invalid or duplicate stable planning identifier')
        expected_parent = None if key == 'PAPER' else ('PAPER' if '.' not in key else key.rsplit('.', 1)[0])
        if row.get('parent') != expected_parent:
            raise ReconcileError('Declared native parent does not match the stable hierarchy')
        records[key] = row
    if rows[0].get('id') != 'PAPER' or set(records) != set(identities):
        raise ReconcileError('Issue map must exactly cover the program, epics and work packages')
    seen = {'id': set(), 'node_id': set(), 'number': set()}
    for key, identity in identities.items():
        if not isinstance(identity, dict) or set(identity) != {'id', 'node_id', 'number', 'url'}:
            raise ReconcileError('Issue map identity has an unsupported shape')
        if any(type(identity[name]) is not int or identity[name] < 1 for name in ('id', 'number')):
            raise ReconcileError('REST issue identity and number must be positive integers')
        if not isinstance(identity['node_id'], str) or not NODE_ID.fullmatch(identity['node_id']):
            raise ReconcileError('GraphQL issue identity is missing or malformed')
        if identity['url'] != f"https://github.com/{REPOSITORY}/issues/{identity['number']}":
            raise ReconcileError('Issue URL is outside the exact mapped repository and number')
        for field in seen:
            if identity[field] in seen[field]:
                raise ReconcileError('An actual issue identity is reused by multiple stable records')
            seen[field].add(identity[field])
    dependencies, parents = {}, []
    for key, row in records.items():
        parent = row.get('parent')
        if parent:
            if parent not in records:
                raise ReconcileError('Native parent is outside the mapped program')
            parents.append((key, parent))
        blockers = row.get('blocked_by')
        if not isinstance(blockers, list) or not all(isinstance(other, str) for other in blockers) or len(blockers) != len(set(blockers)):
            raise ReconcileError('Dependencies must be a unique list')
        if any(not isinstance(other, str) or other not in records or other == key for other in blockers):
            raise ReconcileError('Dependency is outside the mapped program or refers to itself')
        dependencies[key] = blockers
    acyclic(dependencies)
    blockers = [(key, other) for key, others in dependencies.items() for other in others]
    if len(parents) + len(blockers) > MAX_WRITES:
        raise ReconcileError('Declared relationship graph exceeds this bounded bootstrap')
    return {'identities': identities, 'records': records, 'parents': parents, 'blockers': blockers,
            'backlog_sha256': backlog_digest, 'issue_map_sha256': hashlib.sha256(map_path.read_bytes()).hexdigest()}


def validate_context(environment, event):
    if (environment.get('GITHUB_ACTIONS') != 'true' or environment.get('GITHUB_EVENT_NAME') != 'push'
            or environment.get('GITHUB_REPOSITORY') != REPOSITORY
            or environment.get('GITHUB_REPOSITORY_ID') != str(REPOSITORY_ID)
            or environment.get('GITHUB_REF') != 'refs/heads/' + BRANCH
            or environment.get('GITHUB_ACTOR') != ACTOR
            or environment.get('GITHUB_ACTOR_ID') != str(ACTOR_ID)
            or environment.get('GITHUB_TRIGGERING_ACTOR') != ACTOR):
        raise ReconcileError('Execution is outside the authorized Actions push context')
    sha = environment.get('GITHUB_SHA', '')
    repository, sender = event.get('repository', {}), event.get('sender', {})
    if (not SHA.fullmatch(sha) or event.get('after') != sha or event.get('ref') != environment['GITHUB_REF']
            or event.get('deleted') is not False or event.get('forced') is not False
            or repository.get('id') != REPOSITORY_ID or repository.get('full_name') != REPOSITORY
            or repository.get('fork') is not False
            or sender.get('login') != ACTOR or sender.get('id') != ACTOR_ID):
        raise ReconcileError('Push event identity or immutable head does not match the authorized scope')
    return sha


class NoRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, target):
        return None


class GitHubClient:
    """Only fixed-host reads and the two explicitly scoped REST writes exist."""
    def __init__(self, token, opener=None):
        if not token:
            raise ReconcileError('The scoped Actions GITHUB_TOKEN is unavailable')
        self.token = token
        self.opener = opener or urllib.request.build_opener(NoRedirects())
        self.requests = 0

    def request(self, path, method='GET', payload=None):
        if path != '/graphql' and not path.startswith(PREFIX + '/') and path != PREFIX:
            raise ReconcileError('API request escaped the exact authorized repository')
        if method not in ('GET', 'POST'):
            raise ReconcileError('Unsupported API operation')
        if method == 'POST' and path != '/graphql':
            if not re.fullmatch(re.escape(PREFIX) + r'/issues/[1-9]\d*/(?:sub_issues|dependencies/blocked_by)', path):
                raise ReconcileError('Mutation is not a declared native relationship operation')
            if not isinstance(payload, dict):
                raise ReconcileError('Native relationship payload must be a scoped object')
            if path.endswith('/sub_issues'):
                if set(payload or {}) != {'sub_issue_id', 'replace_parent'} or payload['replace_parent'] is not False:
                    raise ReconcileError('Replacing a live parent is forbidden')
                target = payload['sub_issue_id']
            elif set(payload or {}) != {'issue_id'}:
                raise ReconcileError('Unexpected dependency mutation payload')
            else:
                target = payload['issue_id']
            if type(target) is not int or target < 1:
                raise ReconcileError('Native relationship requires a positive actual REST issue ID')
        if path == '/graphql' and (method != 'POST' or not isinstance(payload, dict)
                or payload.get('query') not in (READ_QUERY, PROJECT_QUERY)):
            raise ReconcileError('Only the fixed read-only GraphQL query is permitted')
        request = urllib.request.Request('https://api.github.com' + path,
            data=json.dumps(payload).encode('utf-8') if payload is not None else None,
            headers={'Authorization': 'Bearer ' + self.token, 'Accept': 'application/vnd.github+json',
                     'Content-Type': 'application/json', 'X-GitHub-Api-Version': API_VERSION,
                     'User-Agent': 'Pick-Your-AI-papers-native-relations'}, method=method)
        self.requests += 1
        try:
            with self.opener.open(request, timeout=30) as response:
                body = response.read(12_000_001)
                if len(body) > 12_000_000:
                    raise ApiFailure('GitHub response exceeded the bounded read size; no retry')
                return json.loads(body)
        except urllib.error.HTTPError as error:
            if error.code in (403, 429):
                raise ApiFailure(f'GitHub HTTP {error.code}; permission or rate-limit stop. No retry or alternate credential.') from None
            raise ApiFailure(f'GitHub HTTP {error.code}; operation unverified, no blind retry.') from None
        except (urllib.error.URLError, TimeoutError, OSError, ValueError):
            raise ApiFailure('GitHub transport or response failure; operation unverified, no blind retry.') from None

    def read_nodes(self, identities):
        output = []
        since = utc_timestamp(time.time() - 3600)
        for start in range(0, len(identities), BATCH_SIZE):
            chunk = identities[start:start + BATCH_SIZE]
            response = self.request('/graphql', 'POST', {'query': READ_QUERY,
                'variables': {'ids': [row['node_id'] for row in chunk], 'since': since}})
            if response.get('errors') or not isinstance(response.get('data', {}).get('nodes'), list):
                raise ApiFailure('GraphQL readback failed or is partial; no success is inferred')
            if len(response['data']['nodes']) != len(chunk):
                raise ApiFailure('GraphQL identity inventory is incomplete')
            output.extend(response['data']['nodes'])
        return output

    def verify_head(self, sha):
        result = self.request(PREFIX + '/git/ref/heads/' + BRANCH)
        if result.get('object', {}).get('sha') != sha:
            raise ReconcileError('Foundation branch changed; preserve concurrent work and stop')

    def verify_repository_and_commit(self, sha):
        repository = self.request(PREFIX)
        if (repository.get('id') != REPOSITORY_ID or repository.get('full_name') != REPOSITORY
                or repository.get('private') is not False or repository.get('fork') is not False
                or repository.get('archived') or repository.get('disabled')):
            raise ReconcileError('Live repository identity or state changed')
        self.verify_head(sha)
        commit = self.request(PREFIX + '/commits/' + sha)
        if (commit.get('sha') != sha or (commit.get('author') or {}).get('login') != ACTOR
                or (commit.get('author') or {}).get('id') != ACTOR_ID
                or OPT_IN not in commit.get('commit', {}).get('message', '')):
            raise ReconcileError('Head lacks the authorized author and explicit native-relationships opt-in')


def read_project_snapshot(client):
    """At most three read-only calls; no new scope or credentials on denial.

    Complete means the requested connections were read, not that the Project
    matches its plan or that collaborator roles were verified. Public team links
    do not establish access roles. No private/partial response is published.
    """
    after, project, items, seen_cursors = None, None, [], set()
    for _ in range(3):
        response = client.request('/graphql', 'POST', {'query': PROJECT_QUERY, 'variables': {'after': after}})
        if not isinstance(response, dict) or response.get('errors'):
            raise ApiFailure('Optional Project #9 query denied or incomplete; Project readback remains unverified')
        current = (response.get('data') or {}).get('organization')
        current = current.get('projectV2') if isinstance(current, dict) else None
        if (not isinstance(current, dict) or current.get('number') != PROJECT_NUMBER
                or current.get('url') != PROJECT_URL or current.get('public') is not True):
            raise ReconcileError('Optional Project #9 is inaccessible, not public, or differs from the exact target')
        def complete(connection):
            return (isinstance(connection, dict) and isinstance(connection.get('nodes'), list)
                    and connection.get('pageInfo', {}).get('hasNextPage') is False)
        for key in ('fields', 'views', 'repositories', 'teams'):
            if not complete(current.get(key)):
                raise ReconcileError('Optional Project #9 metadata connection is incomplete')
        for view in current['views']['nodes']:
            if not isinstance(view, dict) or any(not complete(view.get(key)) for key in
                    ('fields', 'groupByFields', 'verticalGroupByFields', 'sortByFields')):
                raise ReconcileError('Optional Project #9 saved-view configuration is incomplete')
        connection = current.get('items') or {}
        if (not isinstance(connection.get('nodes'), list)
                or type(connection.get('pageInfo', {}).get('hasNextPage')) is not bool):
            raise ReconcileError('Optional Project #9 membership connection is incomplete')
        for item in connection['nodes']:
            if not isinstance(item, dict) or not complete(item.get('fieldValues')):
                raise ReconcileError('Optional Project #9 item fields are incomplete')
        metadata = {key: value for key, value in current.items() if key != 'items'}
        if project is not None and metadata != project:
            raise ReconcileError('Optional Project #9 metadata changed during pagination; no coherent snapshot claimed')
        project = metadata
        items.extend(connection['nodes'])
        if len({item.get('id') for item in items}) != len(items) or any(not item.get('id') for item in items):
            raise ReconcileError('Optional Project #9 membership has duplicate or absent item identities')
        if not connection['pageInfo']['hasNextPage']:
            return {'status': 'complete_readback', 'connections_complete': True,
                    'configuration_accepted': False, 'collaborator_roles_verified': False,
                    'observed_at': utc_timestamp(), 'project': {**project, 'items': items},
                    'scope': 'Public Project #9 only; team links are not collaborator access roles.'}
        after = connection['pageInfo'].get('endCursor')
        if not isinstance(after, str) or not after or after in seen_cursors:
            raise ReconcileError('Optional Project #9 pagination cursor is absent or repeated')
        seen_cursors.add(after)
    raise ReconcileError('Optional Project #9 exceeds the bounded three-page membership read')


def observe_optional_project(client, report):
    """Never called after native failure, and never changes the native outcome."""
    if report.get('status') not in ('verified', 'budget_paused'):
        return
    try:
        report['project_readback'] = read_project_snapshot(client)
    except (ReconcileError, OSError, KeyError, TypeError, ValueError, AttributeError) as error:
        report['project_readback'] = {'status': 'unverified', 'connections_complete': False,
            'observed_at': utc_timestamp(), 'project_url': PROJECT_URL,
            'reason': str(error) if isinstance(error, ReconcileError) else 'Optional Project readback could not be validated.'}


def normalized_identity(node):
    if not isinstance(node, dict):
        raise ReconcileError('Native relationship refers to an inaccessible identity')
    try:
        numeric = node['fullDatabaseId']
        if isinstance(numeric, str) and re.fullmatch(r'[1-9]\d*', numeric):
            numeric = int(numeric)
        if type(numeric) is not int or numeric < 1 or type(node['number']) is not int or node['number'] < 1:
            raise ValueError('identity')
        repository = node['repository']['nameWithOwner']
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
            raise ValueError('repository')
        if node['url'] != f"https://github.com/{repository}/issues/{node['number']}":
            raise ValueError('url')
        if not isinstance(node['id'], str) or not NODE_ID.fullmatch(node['id']):
            raise ValueError('node')
        return {'id': numeric, 'node_id': node['id'], 'number': node['number'], 'url': node['url']}
    except (KeyError, TypeError, ValueError) as error:
        raise ReconcileError('Native relationship has malformed identity data') from error


def read_snapshot(client, scope, selected=None):
    keys = list(scope['identities']) if selected is None else list(dict.fromkeys(selected))
    expected = {scope['identities'][key]['node_id']: key for key in keys}
    observed, activity = {}, {}
    for node in client.read_nodes([scope['identities'][key] for key in keys]):
        if not isinstance(node, dict) or node.get('__typename') != 'Issue' or node.get('id') not in expected:
            raise ReconcileError('Mapped node is missing, unexpected or a pull request rather than an issue')
        key = expected[node['id']]
        identity = normalized_identity(node)
        if identity != scope['identities'][key] or node.get('repository', {}).get('nameWithOwner') != REPOSITORY:
            raise ReconcileError('Live issue identity differs from its exact recorded mapping')
        if key in observed or MARKER.findall(node.get('body') or '') != [key]:
            raise ReconcileError('Issue stable marker is absent, conflicting or duplicated')
        if node.get('state') not in ('OPEN', 'CLOSED'):
            raise ReconcileError('Issue state readback is missing')
        current = {**identity, 'state': node['state'], 'parent': normalized_identity(node['parent']) if node.get('parent') else None,
                   'blocked_by': [], 'sub_issues': [], 'observed_at': utc_timestamp()}
        for source, destination in [('blockedBy', 'blocked_by'), ('subIssues', 'sub_issues')]:
            connection = node.get(source, {})
            values = connection.get('nodes')
            if (not isinstance(values, list) or connection.get('pageInfo', {}).get('hasNextPage') is not False
                    or connection.get('totalCount') != len(values)):
                raise ReconcileError('Native relationship connection is incomplete; refusing a partial graph')
            current[destination] = [normalized_identity(row) for row in values]
            if len({row['id'] for row in current[destination]}) != len(values):
                raise ReconcileError('Native relationship readback contains duplicate identities')
        activity['issue:' + node['id']] = {'id': 'issue:' + node['id'], 'kind': 'issue_created', 'at': node.get('createdAt')}
        timeline = node.get('timelineItems', {})
        if timeline.get('pageInfo', {}).get('hasNextPage') is not False or not isinstance(timeline.get('nodes'), list):
            raise ReconcileError('Recent relationship activity is incomplete; cannot bound rolling writes')
        for event in timeline['nodes']:
            if event.get('__typename') not in ('ParentIssueAddedEvent', 'BlockedByAddedEvent') or not NODE_ID.fullmatch(event.get('id', '')):
                raise ReconcileError('Unexpected native relationship event in rate-budget inventory')
            activity[event['id']] = {'id': event['id'], 'kind': event['__typename'], 'at': event.get('createdAt')}
        observed[key] = current
    if set(observed) != set(keys):
        raise ReconcileError('Issue identity readback is incomplete')
    now = time.time()
    for entry in activity.values():
        if epoch(entry['at']) > now + 60:
            raise ReconcileError('Observed activity is implausibly in the future')
    return observed, list(activity.values())


def assess(scope, observed, require_complete=False):
    missing = []
    combined = {key: set(scope['records'][key].get('blocked_by', [])) for key in scope['records']}
    node_to_key = {row['node_id']: key for key, row in scope['identities'].items()}
    for child, parent in scope['parents']:
        actual = observed[child]['parent']
        if actual is not None and actual != scope['identities'][parent]:
            raise ReconcileError('Conflicting native parent for ' + child + '; never replace a parent')
        reciprocal = scope['identities'][child] in observed[parent]['sub_issues']
        if actual is None and reciprocal:
            raise ReconcileError('Native parent and child readback disagree')
        if actual is not None and not reciprocal:
            raise ReconcileError('Native parent lacks reciprocal sub-issue readback')
        if actual is None:
            missing.append(('parent', child, parent))
    for child, blocker in scope['blockers']:
        if scope['identities'][blocker] not in observed[child]['blocked_by']:
            missing.append(('blocker', child, blocker))
    for key, row in observed.items():
        for dependency in row['blocked_by']:
            if dependency['node_id'] in node_to_key:
                combined[key].add(node_to_key[dependency['node_id']])
    acyclic(combined)
    if require_complete and missing:
        raise ReconcileError('Native relationships remain missing after actual readback')
    return missing


class MutationBudget:
    def __init__(self, activity, max_writes=MAX_WRITES, clock=time.time, sleep=time.sleep):
        if type(max_writes) is not int or not 1 <= max_writes <= MAX_WRITES:
            raise ReconcileError('Mutation cap must be between 1 and 450')
        self.activity = [epoch(row['at']) for row in activity]
        self.attempt_times = []
        self.last_completed_at = None
        self.max_writes, self.clock, self.sleep = max_writes, clock, sleep

    def reserve(self):
        now = self.clock()
        if self.attempt_times:
            last = self.last_completed_at if self.last_completed_at is not None else self.attempt_times[-1]
            delay = INTERVAL_SECONDS - (now - last)
            if delay > 0:
                self.sleep(delay)
                now = self.clock()
        recent = sum(value > now - 3600 for value in self.activity + self.attempt_times)
        if len(self.attempt_times) >= self.max_writes or recent >= MAX_WRITES:
            raise BudgetPause('Conservative run or known-content rolling-hour budget reached; checkpoint retained. Resume after the rate window permits, with fresh live readback.')
        self.attempt_times.append(now)  # Count even ambiguous/failed requests.
        return utc_timestamp(now)

    def mark_dispatched(self):
        self.attempt_times[-1] = self.clock()
        return utc_timestamp(self.attempt_times[-1])

    def mark_completed(self):
        # Pacing from response completion also covers variable head-check and
        # network durations, ensuring at least five seconds between POSTs.
        self.last_completed_at = self.clock()


def new_report(scope, sha=None):
    return {'schema_version': '0.1.0', 'repository': REPOSITORY, 'repository_id': REPOSITORY_ID,
        'head_sha': sha, 'status': 'not_started', 'verified': False, 'started_at': utc_timestamp(),
        'backlog_sha256': scope['backlog_sha256'], 'issue_map_sha256': scope['issue_map_sha256'],
        'planned': {'issues': len(scope['identities']), 'internal_parents': len(scope['parents']), 'blockers': len(scope['blockers'])},
        'observed': {}, 'known_content_activity': [], 'mutation_attempts': [], 'errors': [],
        'limits': {'per_run': MAX_WRITES, 'known_content_per_rolling_hour': MAX_WRITES, 'seconds_between_writes': INTERVAL_SECONDS},
        'exclusions': ['Cross-repository program parent research#509 is not applied or verified here.',
            'No issue body/state/assignee, Project, permissions, branch, review, merge, catalog or scientific result is changed.',
            'Observed issue and native-event activity is a lower bound; sibling repositories and other UI/API activity may impose stricter limits.'],
        'completed_at': None}


def reconcile(client, scope, sha, report, checkpoint, max_writes=MAX_WRITES, budget_factory=MutationBudget):
    observed, activity = read_snapshot(client, scope)
    report.update(status='inspected', observed=observed, known_content_activity=activity)
    checkpoint()
    missing = assess(scope, observed)
    budget = budget_factory(activity, max_writes=max_writes)
    for kind, child, other in missing:
        # Fresh issue/parent/dependency reads prevent a stale initial inventory
        # from overwriting a concurrent parent or duplicate relationship.
        fresh, _ = read_snapshot(client, scope, [child, other])
        report['observed'].update(fresh)
        if kind == 'parent':
            parent = fresh[child]['parent']
            if parent is not None and parent != scope['identities'][other]:
                raise ReconcileError('Conflicting native parent for ' + child + '; preserving live state')
            if parent == scope['identities'][other]:
                if scope['identities'][child] not in fresh[other]['sub_issues']:
                    raise ReconcileError('Concurrent parent lacks reciprocal child readback')
                continue
        elif scope['identities'][other] in fresh[child]['blocked_by']:
            continue
        budget.reserve()
        client.verify_head(sha)  # Recheck after the pacing wait, immediately before the write checkpoint.
        attempted_at = budget.mark_dispatched()
        attempt = {'sequence': len(report['mutation_attempts']) + 1, 'kind': kind, 'child': child,
                   'other': other, 'attempted_at': attempted_at, 'outcome': 'unverified'}
        report['mutation_attempts'].append(attempt)
        report['status'] = 'applying'
        checkpoint()
        if kind == 'parent':
            path = PREFIX + f"/issues/{scope['identities'][other]['number']}/sub_issues"
            payload = {'sub_issue_id': scope['identities'][child]['id'], 'replace_parent': False}
        else:
            path = PREFIX + f"/issues/{scope['identities'][child]['number']}/dependencies/blocked_by"
            payload = {'issue_id': scope['identities'][other]['id']}
        client.request(path, 'POST', payload)
        budget.mark_completed()
        attempt['outcome'] = 'request_accepted_readback_pending'
        checkpoint()
        fresh, _ = read_snapshot(client, scope, [child, other])
        report['observed'].update(fresh)
        correct = ((fresh[child]['parent'] == scope['identities'][other] and scope['identities'][child] in fresh[other]['sub_issues'])
                   if kind == 'parent' else scope['identities'][other] in fresh[child]['blocked_by'])
        if not correct:
            raise ReconcileError('Mutation response was accepted but native relationship readback did not match')
        attempt['outcome'] = 'readback_verified'
        attempt['verified_at'] = utc_timestamp()
        checkpoint()
        if len(report['mutation_attempts']) % 10 == 0:
            print(f"Native relationship requests: {len(report['mutation_attempts'])}; latest readback verified.", flush=True)
    client.verify_head(sha)
    final, _ = read_snapshot(client, scope)
    report['observed'] = final
    checkpoint()
    assess(scope, final, require_complete=True)
    report.update(status='verified', verified=True, completed_at=utc_timestamp())
    checkpoint()


def summarize(report, path):
    attempts = report.get('mutation_attempts', [])
    lines = ['## Papers native relationship readback', '',
        f"Status: **{report.get('status', 'unavailable')}**. Full graph verified: **{report.get('verified', False)}**.", '',
        'The JSON below contains actual observations and request timestamps. A pending or accepted request is not a verified edge. ' +
        'Cross-repository research #509 and all scientific/editorial acceptance are excluded.', '',
        f"Requests attempted this run: {len(attempts)}; individually read back: {sum(x.get('outcome') == 'readback_verified' for x in attempts)}.", '',
        '<details><summary>Observed graph, checkpoints and rolling-budget evidence</summary>', '',
        '```json', json.dumps(report, indent=2, sort_keys=True), '```', '', '</details>', '']
    content = '\n'.join(lines)
    if len(content.encode('utf-8')) > 950_000:
        # Preserve every observation; omit indentation only, never evidence.
        lines[lines.index('```json') + 1] = json.dumps(report, sort_keys=True, separators=(',', ':'))
        content = '\n'.join(lines)
    if len(content.encode('utf-8')) > 950_000:
        raise ReconcileError('Readback summary exceeds bounded size; retain local report and do not truncate its claims')
    with Path(path).open('a', encoding='utf-8') as stream:
        stream.write(content)


def checkpoint_log(report):
    """Connector-readable copy of the same public, body-free step-summary data."""
    return 'PAPERS_NATIVE_CHECKPOINT_JSON=' + json.dumps(report, sort_keys=True, separators=(',', ':'))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--report', type=Path)
    parser.add_argument('--max-writes', type=int, default=MAX_WRITES)
    parser.add_argument('--summarize', type=Path, help='Only publish an existing actual report to GITHUB_STEP_SUMMARY; no network.')
    args = parser.parse_args(argv)
    if args.summarize:
        if args.apply or not os.environ.get('GITHUB_STEP_SUMMARY'):
            raise ReconcileError('Summary mode requires the Actions summary path and cannot apply changes')
        report = load_json(args.summarize) if args.summarize.exists() else {
            'status': 'report_unavailable', 'verified': False, 'errors': ['No application checkpoint was produced.']}
        summarize(report, os.environ['GITHUB_STEP_SUMMARY'])
        return 0
    scope = load_scope(args.root)
    report = new_report(scope)
    if not args.apply:
        print(json.dumps({'mode': 'offline', 'planned': report['planned'], 'remote_mutations': 0,
                          'backlog_sha256': scope['backlog_sha256'], 'excluded_program_parent': 'research#509'}, indent=2))
        return 0
    if args.report is None:
        raise ReconcileError('Apply mode requires a local checkpoint report path')
    def checkpoint():
        write_report(args.report, report)
    checkpoint()
    try:
        event = load_json(os.environ.get('GITHUB_EVENT_PATH', ''))
        sha = validate_context(os.environ, event)
        report['head_sha'] = sha
        report['run_id'] = os.environ.get('GITHUB_RUN_ID')
        report['run_attempt'] = os.environ.get('GITHUB_RUN_ATTEMPT')
        if args.root.resolve() != Path(os.environ.get('GITHUB_WORKSPACE', '')).resolve():
            raise ReconcileError('Apply root differs from the authorized Actions checkout')
        head = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=args.root, capture_output=True, text=True, check=False, timeout=10)
        if head.returncode or head.stdout.strip() != sha:
            raise ReconcileError('Checkout is not the exact authorized push commit')
        client = GitHubClient(os.environ.get('GITHUB_TOKEN'))
        client.verify_repository_and_commit(sha)
        reconcile(client, scope, sha, report, checkpoint, max_writes=args.max_writes)
        result = 0
    except BudgetPause as error:
        report.update(status='budget_paused', verified=False)
        report['errors'].append(str(error)); result = 3
    except (ReconcileError, OSError, subprocess.TimeoutExpired) as error:
        report.update(status='blocked', verified=False)
        report['errors'].append(str(error) if isinstance(error, ReconcileError) else 'Local runtime failure; retain checkpoint.')
        result = 2
    finally:
        if report['status'] in ('verified', 'budget_paused'):
            observe_optional_project(client, report)
        report['completed_at'] = utc_timestamp()
        checkpoint()
    print(json.dumps({'status': report['status'], 'verified': report['verified'],
                      'requests_attempted': len(report['mutation_attempts']), 'errors': report['errors']}, indent=2))
    print(checkpoint_log(report), flush=True)
    return result


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except ReconcileError as error:
        print('BLOCKED: ' + str(error), file=sys.stderr)
        raise SystemExit(2)
