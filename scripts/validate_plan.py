#!/usr/bin/env python3
"""Validate the literature planning baseline offline with the standard library.

The finite JSON Schema evaluator shared with validate_research rejects unknown
assertion keywords. This module adds cross-record and cross-file semantics. It
performs no network requests and does not verify scientific or GitHub facts.
"""
from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path, PurePosixPath
import re
import sys

from validate_research import load_json, public_url, schema_errors, schema_keywords

ROOT = Path(__file__).resolve().parents[1]
FILES = {
    'backlog': ('project-backlog.json', 'planning-backlog.schema.json'),
    'coverage': ('coverage-matrix.json', 'planning-coverage.schema.json'),
    'decisions': ('decision-register.json', 'planning-decisions.schema.json'),
    'release': ('release-manifest.json', 'planning-release.schema.json'),
}
REQUIRED_OPTIONS = {
    'status': ['Backlog', 'Ready', 'In Progress', 'In Review', 'Blocked', 'Done'],
    'priority': ['P0', 'P1', 'P2', 'P3'],
    'record_type': ['Program', 'Epic', 'Work Package', 'Task'],
    'readiness': ['Ready', 'Needs Input', 'Blocked', 'Awaiting Decision'],
}
FIRST_EPIC_TITLES = [
    'Research mission and audience definition',
    'Relationship to existing Pick Your AI research',
    'Inclusion and exclusion criteria',
    'Publication and research-object taxonomy',
    'Scientific field and task classifications',
    'Evidence confidence and qualification levels',
    'Coverage denominator and completeness tracking',
    'Research ownership and decision governance',
]
FIRST_SOURCE_TITLES = [
    'arXiv and preprint metadata research',
    'DOI and Crossref publication metadata',
    'OpenAlex and scholarly graph references',
    'Publisher and journal metadata',
    'Conference and venue metadata',
]
SECRET_RE = re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')


def records(backlog):
    yield backlog['program']
    for epic in backlog['epics']:
        yield epic
        yield from epic['work_packages']


def packages(backlog):
    return [package for epic in backlog['epics'] for package in epic['work_packages']]


def count_backlog(backlog):
    work = packages(backlog)
    return {
        'programs': 1,
        'epics': len(backlog['epics']),
        'work_packages': len(work),
        'native_issue_records': 1 + len(backlog['epics']) + len(work),
        'native_parent_edges': len(backlog['epics']) + len(work),
        'checklist_tasks': sum(len(w['tasks']) for w in work),
        'checklist_subtasks': sum(len(t['subtasks']) for w in work for t in w['tasks']),
        'dependency_edges': sum(len(w['blocked_by']) for w in work),
    }


def walk_strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_strings(item)


def safe_local_path(value):
    if not isinstance(value, str) or not value or re.search(r'[\x00-\x20\x7f\\:]', value):
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in ('', '.', '..') for part in value.split('/')) and str(path) == value


def load_bundle(root=ROOT):
    return {name: load_json(Path(root) / 'planning' / files[0]) for name, files in FILES.items()}


def validate_shapes(bundle, root=ROOT):
    errors = []
    for name, (_, schema_file) in FILES.items():
        schema = load_json(Path(root) / 'schemas' / schema_file)
        defects = schema_keywords(schema, schema_file)
        errors.extend(defects)
        if not defects:
            errors.extend(schema_errors(bundle[name], schema, name))
    return errors


def validate_bundle(bundle, root=ROOT):
    errors = validate_shapes(bundle, root)
    if errors:
        return errors  # Do not traverse malformed shapes or imply partial validity.
    b = bundle['backlog']
    work = packages(b)
    all_records = list(records(b))
    by_id = {r['id']: r for r in all_records}
    by_package = {r['id']: r for r in work}
    ids = [r['id'] for r in all_records]
    for w in work:
        for t in w['tasks']:
            ids.append(t['id'])
            ids.extend(s['id'] for s in t['subtasks'])
    for key, count in Counter(ids).items():
        if count > 1:
            errors.append('Duplicate stable ID: ' + key)

    if b['program']['id'] != 'PAPER' or b['program']['record_type'] != 'Program':
        errors.append('Program identity must be PAPER / Program')
    for field, required in REQUIRED_OPTIONS.items():
        if b['options'][field] != required:
            errors.append('Required Project options differ for ' + field)
    for r in all_records:
        for field, allowed in b['options'].items():
            if r[field] not in allowed:
                errors.append(r['id'] + ': option outside declared ' + field)
        if r['publication_status'] != 'Not Applicable':
            errors.append(r['id'] + ': planning records require publication_status Not Applicable')
        if r['readiness'] == 'Ready' and not r['assignees']:
            errors.append(r['id'] + ': Ready requires accepted native assignment')
        if r['status'] == 'Done' and r['acceptance_status'] != 'Accepted':
            errors.append(r['id'] + ': Done requires accepted scope')
        expected_dependency = 'Prerequisites Open' if r['blocked_by'] else 'No Hard Prerequisites'
        if r['status'] == 'Backlog' and r['dependency_status'] != expected_dependency:
            errors.append(r['id'] + ': dependency classification disagrees with declared prerequisites')
        for ref in r['references']:
            if not public_url(ref['url']):
                errors.append(r['id'] + ': unsafe reference URL')
        for path in r['deliverables']:
            if not safe_local_path(path):
                errors.append(r['id'] + ': unsafe deliverable path ' + repr(path))
            else:
                resolved = (Path(root) / path).resolve()
                if not resolved.is_relative_to(Path(root).resolve()):
                    errors.append(r['id'] + ': deliverable escapes checkout through a symlink')
        if r['record_type'] != 'Work Package' and r['blocked_by']:
            errors.append(r['id'] + ': aggregate blockers must be explicit child outputs, not duplicated edges')

    for e in b['epics']:
        if not re.fullmatch(r'PAPER-[0-9]{2}', e['id']) or e['parent'] != 'PAPER' or e['record_type'] != 'Epic':
            errors.append(e['id'] + ': invalid epic identity or parent')
        for w in e['work_packages']:
            if not re.fullmatch(re.escape(e['id']) + r'\.[0-9]{2}', w['id']) or w['parent'] != e['id'] or w['record_type'] != 'Work Package':
                errors.append(w['id'] + ': invalid work-package identity or parent')
            if len(w['tasks']) < 3 or len(w['acceptance_criteria']) < 2 or len(w['deliverables']) < 2:
                errors.append(w['id'] + ': incomplete independently reviewable outcome')
            for t in w['tasks']:
                if not re.fullmatch(re.escape(w['id']) + r'\.T[1-9][0-9]*', t['id']):
                    errors.append(t['id'] + ': wrong task owner or ID')
                if len(t['subtasks']) < 2:
                    errors.append(t['id'] + ': at least two bounded subtasks are required')
                if t['done'] and not all(s['done'] for s in t['subtasks']):
                    errors.append(t['id'] + ': completed task has unfinished subtasks')
                for sub in t['subtasks']:
                    if not re.fullmatch(re.escape(t['id']) + r'\.S[1-9][0-9]*', sub['id']):
                        errors.append(sub['id'] + ': wrong subtask owner or ID')
            for dep in w['blocked_by']:
                if dep not in by_package:
                    errors.append(w['id'] + ': unknown prerequisite ' + dep)
                if dep == w['id']:
                    errors.append(w['id'] + ': self prerequisite')

    # The supplied first epic and first source names are explicit mission scope.
    for number, title in enumerate(FIRST_EPIC_TITLES, 1):
        r = by_package.get(f'PAPER-01.{number:02d}')
        if not r or r['title'] != title:
            errors.append('Required supplied Epic 01 package missing or renamed: ' + title)
    for number, title in enumerate(FIRST_SOURCE_TITLES, 1):
        r = by_package.get(f'PAPER-02.{number:02d}')
        if not r or r['title'] != title:
            errors.append('Required supplied Epic 02 package missing or renamed: ' + title)

    visiting, done = set(), set()
    def visit(key):
        if key in visiting:
            errors.append('Dependency cycle at ' + key)
            return
        if key in done or key not in by_package:
            return
        visiting.add(key)
        for dep in by_package[key]['blocked_by']:
            visit(dep)
        visiting.remove(key)
        done.add(key)
    for key in by_package:
        visit(key)
    if b['counts'] != count_backlog(b):
        errors.append('Derived backlog counts do not match records')
    deliverables = [d for w in work for d in w['deliverables']]
    if len(deliverables) != len(set(deliverables)):
        errors.append('Independent packages share a canonical deliverable path')

    coverage = bundle['coverage']
    cov_ids = [x['id'] for x in coverage['entries']]
    if len(cov_ids) != len(set(cov_ids)):
        errors.append('Duplicate coverage ID')
    subjects = [(x['dimension'], x['subject']) for x in coverage['entries']]
    if len(subjects) != len(set(subjects)):
        errors.append('Duplicate coverage subject within dimension')
    mapped = set()
    for row in coverage['entries']:
        if row['dimension'] not in coverage['dimensions']:
            errors.append(row['id'] + ': undeclared coverage dimension')
        for wid in row['work_packages']:
            mapped.add(wid)
            if wid not in by_package:
                errors.append(row['id'] + ': unknown mapped package ' + wid)
        denominator = row['denominator']
        if row['dimension'] == 'Workstream':
            if denominator['status'] != 'Planning Scope Enumerated' or denominator['size'] != len(row['work_packages']):
                errors.append(row['id'] + ': workstream denominator must match known planning scope')
        elif denominator['status'] == 'Not Measured' and denominator['size'] is not None:
            errors.append(row['id'] + ': unmeasured literature denominator must remain null')
        elif denominator['status'] == 'Measured' and denominator['size'] is None:
            errors.append(row['id'] + ': measured denominator requires a size and evidence')
    if mapped != set(by_package):
        errors.append('Coverage must map every planned package and no unknown package')
    actual_summary = {'entries': len(coverage['entries']), 'dimensions': len(set(r['dimension'] for r in coverage['entries'])), 'mapped_work_packages': len(mapped)}
    for key, value in actual_summary.items():
        if coverage['summary'][key] != value:
            errors.append('Coverage summary mismatch: ' + key)
    if set(coverage['dimensions']) != {r['dimension'] for r in coverage['entries']}:
        errors.append('Coverage dimension catalog differs from observed dimensions')
    if coverage['summary']['global_denominator'] is not None:
        errors.append('A global scientific-literature denominator is not established by this plan')
    if not coverage['summary']['measured_real_literature_coverage']:
        for row in coverage['entries']:
            if row['dimension'] != 'Workstream' and row['denominator']['status'] == 'Measured':
                errors.append('Measured coverage row conflicts with unmeasured-real-coverage summary')

    decisions = bundle['decisions']['decisions']
    dec_ids = [d['id'] for d in decisions]
    if len(dec_ids) != len(set(dec_ids)):
        errors.append('Duplicate decision ID')
    if 'PAPER-DEC-001' not in dec_ids:
        errors.append('Missing decision documenting the incomplete supplied epic list')
    for d in decisions:
        if bool(d['accepted_by']) != bool(d['acceptance_reference']):
            errors.append(d['id'] + ': acceptance requires both actual reviewer and receipt')
        for wid in d['affects']:
            if wid not in by_package:
                errors.append(d['id'] + ': unknown affected package ' + wid)

    release = bundle['release']
    phase_names = [p['name'] for p in release['phases']]
    if phase_names != b['options']['release_phase']:
        errors.append('Release phases must match declared order and options')
    release_targets = list(release['mandatory_for_any_public_literature_release'])
    for phase in release['phases']:
        release_targets.extend(phase['required_packages'])
    for gate in release['capability_gates']:
        release_targets.extend(gate['required_packages'])
    for wid in release_targets:
        if wid not in by_package:
            errors.append('Release references unknown package ' + wid)
    for index, phase in enumerate(b['options']['release_phase'][:4], 1):
        key = f'PAPER-20.{index:02d}'
        if key in by_package and by_package[key]['release_phase'] != phase:
            errors.append(key + ': release acceptance package has wrong phase')
    acceptance = [release['accepted_release'], release['accepted_by'], release['acceptance_reference']]
    if any(x is not None for x in acceptance) and not all(x is not None for x in acceptance):
        errors.append('Accepted release requires exact release, actual accepting owner and receipt')

    for text in walk_strings(bundle):
        if SECRET_RE.search(text):
            errors.append('Possible credential/private-key material in planning data')
        if re.search(r'/(?:Users|home)/[^/]+/|[A-Za-z]:[\\/](?:Users|home)[\\/]', text):
            errors.append('Private local path in planning data')
    return errors


def validate(root=ROOT):
    try:
        return validate_bundle(load_bundle(root), root)
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as exc:
        return ['Invalid planning input: ' + str(exc)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print('ERROR: ' + error, file=sys.stderr)
        return 1
    counts = count_backlog(load_bundle(args.root)['backlog'])
    print('Valid planning baseline: ' + ', '.join(f'{v} {k}' for k, v in counts.items()) + '.')
    print('Offline integrity only; no scientific truth, rights, independent acceptance or live GitHub state is verified.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
