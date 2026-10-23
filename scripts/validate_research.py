#!/usr/bin/env python3
"""Offline structural, provenance and publication gates for scholarly proposals.

Uses only the Python standard library. The deliberately small schema interpreter
supports every assertion keyword used by this repository's research schemas and
rejects unsupported keywords. It is not a general JSON Schema implementation.
Passing checks does not verify source truth, scientific validity or legal rights.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import ipaddress
import json
from pathlib import Path, PurePosixPath
import re
from urllib.parse import parse_qsl, urlsplit


SCHEMA_FILES = {
    'sources/register.json': 'research-source',
    'sources/rights.json': 'source-rights',
    'evidence/research-evidence.json': 'research-evidence',
    'evidence/research-events.json': 'research-event',
    'evidence/upstream-inspection.json': 'research-inspection',
    'research/graph.json': 'graph-edge',
}
SCHEMA_KEYWORDS = {
    '$schema', '$id', 'title', 'description', 'type', 'const', 'enum', 'anyOf',
    'properties', 'required', 'additionalProperties', 'items', 'minItems',
    'uniqueItems', 'minLength', 'maxLength', 'pattern', 'format', 'minimum',
}
MATERIAL_ROOTS = ('sources', 'research', 'evidence', 'catalog', 'examples')
FORBIDDEN_COMPONENTS = {'private', 'raw', 'fulltext', 'full-text', 'manuscripts', 'weights', 'credentials'}
FORBIDDEN_KEYS = {'abstract', 'full_text', 'fulltext', 'paper_text', 'raw_dataset',
                  'dataset_rows', 'credentials', 'private_email', 'access_token',
                  'api_key', 'password', 'figure_bytes', 'binary_data', 'pdf_bytes'}
SECRET_PATTERNS = (
    re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{40,}'),
    re.compile(r'AKIA[0-9A-Z]{16}'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
)
PUBLIC_FIELDS = {'/work/title', '/work/identifiers', '/manifestation', '/revision',
                 '/authors', '/summary/text', '/research_domains', '/research_method'}
METADATA_FIELDS = {'/work/title', '/work/identifiers', '/manifestation', '/revision', '/authors'}


def public_url(value: str) -> bool:
    try:
        if not isinstance(value, str) or re.search(r'[\x00-\x20\x7f\\]', value):
            return False
        url = urlsplit(value)
        host = (url.hostname or '').lower()
        if url.scheme != 'https' or not host or '@' in url.netloc:
            return False
        if url.port is not None and not 1 <= url.port <= 65535:
            return False
        if url.netloc.endswith(':'):
            return False
        if host == 'localhost' or host.endswith(('.local', '.internal', '.localhost')):
            return False
        try:
            if not ipaddress.ip_address(host).is_global:
                return False
        except ValueError:
            # Reject noncanonical IP forms (127.1, integer/hex IPv4) that some
            # resolvers normalize, and require a syntactically public DNS name.
            if re.fullmatch(r'[0-9.]+', host) or re.fullmatch(r'0x[0-9a-f]+', host):
                return False
            if len(host) > 253 or '.' not in host or host.endswith('.'):
                return False
            if not all(re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label)
                       for label in host.split('.')):
                return False
            if not re.fullmatch(r'[a-z][a-z0-9-]*', host.rsplit('.', 1)[1]):
                return False
        sensitive = {'token', 'access_token', 'api_key', 'apikey', 'authorization',
                     'password', 'signature', 'x-amz-credential', 'x-amz-signature'}
        return not any(k.lower() in sensitive for k, _ in parse_qsl(url.query))
    except ValueError:
        return False


def no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate JSON key: ' + key)
        result[key] = value
    return result


def load_json(path: Path):
    def bad_constant(value):
        raise ValueError('non-JSON numeric constant: ' + value)
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=no_duplicate_keys,
                      parse_constant=bad_constant)


def json_equal(left, right):
    """JSON value equality: booleans differ from numbers, 1 equals 1.0."""
    if type(left) in (int, float) and type(right) in (int, float):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(json_equal(left[k], right[k]) for k in left)
    if isinstance(left, list):
        return len(left) == len(right) and all(json_equal(x, y) for x, y in zip(left, right))
    return left == right


def schema_keywords(schema, at='schema'):
    """Reject unsupported or malformed assertions before evaluating data."""
    errors = []
    if not isinstance(schema, dict):
        return [at + ': schema must be an object']
    unknown = set(schema) - SCHEMA_KEYWORDS
    if unknown:
        errors.append(at + ': unsupported schema keyword(s): ' + ', '.join(sorted(unknown)))
    for name in ('$schema', '$id', 'title', 'description'):
        if name in schema and not isinstance(schema[name], str):
            errors.append(at + ': ' + name + ' must be a string')
    if 'type' in schema and (not isinstance(schema['type'], str) or schema['type'] not in
                            {'object', 'array', 'string', 'integer', 'boolean', 'null'}):
        errors.append(at + ': unsupported schema type')
    if 'properties' in schema:
        if not isinstance(schema['properties'], dict):
            errors.append(at + ': properties must be an object')
        else:
            for name, child in schema['properties'].items():
                errors.extend(schema_keywords(child, at + '/properties/' + name))
    if 'items' in schema:
        errors.extend(schema_keywords(schema['items'], at + '/items'))
    if 'anyOf' in schema:
        if not isinstance(schema['anyOf'], list) or not schema['anyOf']:
            errors.append(at + ': anyOf must be a nonempty array of schemas')
        else:
            for i, child in enumerate(schema['anyOf']):
                errors.extend(schema_keywords(child, at + '/anyOf/' + str(i)))
    if 'required' in schema:
        value = schema['required']
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value) or len(value) != len(set(value)):
            errors.append(at + ': required must be an array of unique strings')
    if 'enum' in schema:
        value = schema['enum']
        if not isinstance(value, list) or not value or any(json_equal(x, y) for i, x in enumerate(value) for y in value[:i]):
            errors.append(at + ': enum must be a nonempty array of distinct JSON values')
    for name in ('minItems', 'minLength', 'maxLength'):
        if name in schema and (type(schema[name]) is not int or schema[name] < 0):
            errors.append(at + ': ' + name + ' must be a nonnegative integer')
    for name in ('uniqueItems', 'additionalProperties'):
        if name in schema and type(schema[name]) is not bool:
            errors.append(at + ': ' + name + ' must be boolean in this finite schema vocabulary')
    if 'minimum' in schema and type(schema['minimum']) not in (int, float):
        errors.append(at + ': minimum must be a number')
    if 'pattern' in schema:
        try:
            if not isinstance(schema['pattern'], str):
                raise TypeError('pattern')
            re.compile(schema['pattern'])
        except (TypeError, re.error):
            errors.append(at + ': pattern must be a valid regular expression string')
    if 'format' in schema and schema['format'] not in ('date', 'uri'):
        errors.append(at + ': unsupported format')
    return errors


def schema_errors(value, schema, at):
    """Validate the finite assertion vocabulary used by our authored schemas."""
    errors = []
    if 'anyOf' in schema:
        candidates = [schema_errors(value, item, at) for item in schema['anyOf']]
        if all(candidates):
            errors.append(at + ': does not match an allowed shape')
    if 'const' in schema and not json_equal(value, schema['const']):
        errors.append(at + ': wrong constant value')
    if 'enum' in schema and not any(json_equal(value, option) for option in schema['enum']):
        errors.append(at + ': value is not in the declared vocabulary')
    expected = schema.get('type')
    tests = {
        'object': lambda v: isinstance(v, dict), 'array': lambda v: isinstance(v, list),
        'string': lambda v: isinstance(v, str), 'integer': lambda v: type(v) is int,
        'boolean': lambda v: type(v) is bool, 'null': lambda v: v is None,
    }
    if expected and (expected not in tests or not tests[expected](value)):
        return errors + [at + ': expected ' + str(expected)]
    if isinstance(value, dict):
        properties = schema.get('properties', {})
        for key in schema.get('required', []):
            if key not in value:
                errors.append(at + ': missing required field ' + key)
        if schema.get('additionalProperties') is False:
            for key in sorted(set(value) - set(properties)):
                errors.append(at + ': unexpected field ' + key)
        for key in sorted(set(properties) & set(value)):
            errors.extend(schema_errors(value[key], properties[key], at + '/' + key))
    elif isinstance(value, list):
        if len(value) < schema.get('minItems', 0):
            errors.append(at + ': too few items')
        if schema.get('uniqueItems'):
            if any(json_equal(x, y) for i, x in enumerate(value) for y in value[:i]):
                errors.append(at + ': duplicate list item')
        if 'items' in schema:
            for i, item in enumerate(value):
                errors.extend(schema_errors(item, schema['items'], at + '/' + str(i)))
    elif isinstance(value, str):
        if len(value) < schema.get('minLength', 0) or len(value) > schema.get('maxLength', float('inf')):
            errors.append(at + ': invalid string length')
        if 'pattern' in schema and re.search(schema['pattern'], value) is None:
            errors.append(at + ': invalid identifier or field format')
        if schema.get('format') == 'uri' and not public_url(value):
            errors.append(at + ': source URI must be a public HTTPS URL without credentials')
        if schema.get('format') == 'date':
            try:
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                    raise ValueError('date')
                date.fromisoformat(value)
            except ValueError:
                errors.append(at + ': invalid ISO calendar date')
    elif type(value) in (int, float) and value < schema.get('minimum', value):
        errors.append(at + ': below minimum')
    return errors


def pointer_value(value, pointer):
    if not pointer.startswith('/'):
        raise ValueError('pointer must begin with /')
    for part in pointer[1:].split('/'):
        if re.search(r'~(?![01])', part):
            raise ValueError('invalid pointer escape')
        part = part.replace('~1', '/').replace('~0', '~')
        if isinstance(value, list):
            if not re.fullmatch(r'0|[1-9]\d*', part):
                raise ValueError('invalid array index')
            value = value[int(part)]
        elif isinstance(value, dict):
            value = value[part]
        else:
            raise ValueError('pointer does not resolve')
    return value


def pointer_exists(value, pointer):
    try:
        pointer_value(value, pointer)
        return True
    except (KeyError, IndexError, ValueError):
        return False


def canonical_sha256(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     ensure_ascii=False).encode('utf-8')).hexdigest()


def checked_fields_sha256(record, observations):
    """Bind a check to the exact stored values at its declared JSON pointers."""
    try:
        return canonical_sha256({p: pointer_value(record, p) for p in sorted(observations)})
    except (KeyError, IndexError, ValueError):
        return None


def review_scope_sha256(kind, target_id, documents):
    """Hash the target and material dependencies; review objects are excluded.

    Records bind sources, rights, checked values, runs, notices and owned graph
    edges. Rights bind affected record snapshots and terms-source observations.
    Notice/edge reviews bind affected records plus their explicit evidence.
    Only review IDs appear in those objects, so this creates no digest cycle.
    A changed approval/status/projection requires a freshly scoped review.
    """
    def indexed(rows):
        return {row['id']: row for row in rows}
    evidence = documents['evidence/research-evidence.json']
    sources = indexed(documents['sources/register.json']['sources'])
    rights = indexed(documents['sources/rights.json']['decisions'])
    checks = indexed(evidence['checks'])
    experiments = indexed(evidence['experiments'])
    events = indexed(documents['evidence/research-events.json']['events'])
    graph = documents['research/graph.json']
    nodes, edges = indexed(graph['nodes']), indexed(graph['edges'])
    records = {r['record_id']: r for path, r in documents.items() if path.startswith('catalog/proposals/')}

    def selected(registry, identifiers):
        return {key: registry.get(key) for key in sorted(set(identifiers))}

    def decision_sources(decision):
        return [decision['source_id']] + [ref for permission in decision['permissions'] for ref in permission['evidence_refs']]

    def snapshot(record):
        rid = record['record_id']
        selected_rights = selected(rights, record['rights_decision_ids'])
        selected_checks = selected(checks, record['citation_check_ids'] + record['integrity_check_ids'])
        selected_runs = selected(experiments, record['experiment_ids'])
        selected_events = selected(events, record['integrity_event_ids'])
        owned_edges = {key: edge for key, edge in edges.items() if any(nodes.get(edge[end], {}).get('record_id') == rid for end in ('subject', 'object'))}
        source_ids = list(record['source_refs'])
        source_ids += [ref for row in selected_rights.values() if row for ref in decision_sources(row)]
        source_ids += [row['source_id'] for row in selected_checks.values() if row]
        source_ids += [ref for row in selected_runs.values() if row for ref in row['source_refs']]
        source_ids += [row['source_id'] for row in selected_events.values() if row]
        source_ids += [ref for row in owned_edges.values() for ref in row['source_refs']]
        return {'record': record, 'sources': selected(sources, source_ids), 'rights': selected_rights,
                'checks': selected_checks, 'experiments': selected_runs, 'events': selected_events,
                'edges': owned_edges, 'nodes': {key: row for key, row in nodes.items() if row['record_id'] == rid}}

    if kind == 'rights':
        target = rights.get(target_id)
        if not target:
            return None
        content = {'decision': target, 'sources': selected(sources, decision_sources(target)),
                   'affected_records': {rid: snapshot(r) for rid, r in records.items() if target_id in r['rights_decision_ids']}}
    elif kind == 'integrity':
        target = events.get(target_id)
        if not target:
            return None
        content = {'event': target, 'source': sources.get(target['source_id']),
                   'checks': {key: row for key, row in checks.items() if row['source_id'] == target['source_id'] and row['revision_id'] in target['revision_ids']},
                   'affected_record': snapshot(records[target['work_id']]) if target['work_id'] in records else None}
    elif kind in ('editorial', 'scientific', 'reproduction') and target_id in records:
        content = snapshot(records[target_id])
    elif kind in ('scientific', 'reproduction') and target_id in edges:
        target = edges[target_id]
        owners = {nodes.get(target[end], {}).get('record_id') for end in ('subject', 'object')}
        content = {'edge': target, 'sources': selected(sources, target['source_refs']),
                   'checks': selected(checks, target['check_ids']),
                   'endpoints': selected(nodes, [target['subject'], target['object']]),
                   'experiment': experiments.get(target['subject']),
                   'affected_records': {rid: snapshot(records[rid]) for rid in owners if rid in records}}
    else:
        return None
    return canonical_sha256({'kind': kind, 'target_id': target_id, 'content': content})


def material_errors(root):
    errors = []
    for dirname in MATERIAL_ROOTS:
        directory = root / dirname
        if not directory.exists():
            errors.append(dirname + ': required material directory is missing')
            continue
        if directory.is_symlink():
            errors.append(dirname + ': symlinks are forbidden in research material')
            continue
        for path in sorted(directory.rglob('*')):
            label = str(path.relative_to(root))
            if path.is_symlink():
                errors.append(label + ': symlinks are forbidden in research material')
                continue
            if set(x.lower() for x in path.relative_to(directory).parts) & FORBIDDEN_COMPONENTS:
                errors.append(label + ': private/raw material path is forbidden')
            if not path.is_file():
                continue
            if path.suffix.lower() not in ('.json', '.md'):
                errors.append(label + ': raw/binary/unregistered material format is forbidden')
                continue
            try:
                content = path.read_text(encoding='utf-8')
            except (UnicodeError, OSError):
                errors.append(label + ': text decoding failed')
                continue
            if any(p.search(content) for p in SECRET_PATTERNS):
                errors.append(label + ': credential-like material is forbidden')
            if path.suffix == '.json':
                try:
                    data = load_json(path)
                except (ValueError, OSError) as exc:
                    errors.append(label + ': invalid JSON (' + str(exc) + ')')
                    continue
                def scan(value, location):
                    if isinstance(value, dict):
                        for key, item in value.items():
                            if key.lower() in FORBIDDEN_KEYS:
                                errors.append(location + ': restricted material field ' + key)
                            scan(item, location + '/' + key)
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            scan(item, location + '/' + str(i))
                    elif isinstance(value, str) and value.startswith(('http://', 'https://')) and not public_url(value):
                        errors.append(location + ': unsafe/private source URL')
                scan(data, label)
    return errors


def validate(root: Path, publication=False):
    """Return sorted errors and bounded statistics; perform no network or writes."""
    root = Path(root)
    errors = material_errors(root)
    stats = {'records': 0, 'sources': 0, 'edges': 0, 'checks': 0, 'experiments': 0,
             'eligible_records': 0, 'published_records': 0}
    paths = dict(SCHEMA_FILES)
    for path in sorted((root / 'catalog/proposals').glob('*.json')):
        paths[str(path.relative_to(root))] = 'scholarly-record'
    for dirname in MATERIAL_ROOTS:
        for path in sorted((root / dirname).rglob('*.json')):
            if str(path.relative_to(root)) not in paths:
                errors.append(str(path.relative_to(root)) + ': unregistered JSON artifact; define its validation contract')
    schemas, documents = {}, {}
    shape_errors = []
    for name in sorted(set(paths.values())):
        try:
            schema = load_json(root / 'schemas' / (name + '.schema.json'))
            schema_issues = schema_keywords(schema, 'schemas/' + name + '.schema.json')
            shape_errors.extend(schema_issues)
            if not schema_issues:
                schemas[name] = schema
        except (OSError, ValueError) as exc:
            shape_errors.append('schemas/' + name + '.schema.json: ' + str(exc))
    for path, name in sorted(paths.items()):
        try:
            data = load_json(root / path)
            documents[path] = data
            if name in schemas:
                shape_errors.extend(schema_errors(data, schemas[name], path))
        except (OSError, ValueError) as exc:
            shape_errors.append(path + ': ' + str(exc))
    if shape_errors:
        return sorted(set(errors + shape_errors)), stats

    def index(rows, label):
        out = {}
        for row in rows:
            if row['id'] in out:
                errors.append(label + ': duplicate id ' + row['id'])
            out[row['id']] = row
        return out

    sources = index(documents['sources/register.json']['sources'], 'sources')
    rights = index(documents['sources/rights.json']['decisions'], 'rights')
    evidence = documents['evidence/research-evidence.json']
    checks = index(evidence['checks'], 'checks')
    reviews = index(evidence['reviews'], 'reviews')
    experiments = index(evidence['experiments'], 'experiments')
    receipts = index(evidence['publication_receipts'], 'publication receipts')
    events = index(documents['evidence/research-events.json']['events'], 'integrity events')
    graph = documents['research/graph.json']
    nodes = index(graph['nodes'], 'graph nodes')
    index(graph['edges'], 'graph edges')
    records = {path: data for path, data in documents.items() if path.startswith('catalog/proposals/')}
    by_id = {}
    for path, record in records.items():
        if record['record_id'] in by_id:
            errors.append(path + ': duplicate scholarly record id')
        by_id[record['record_id']] = record
    by_revision = {r['revision']['id']: r for r in records.values()}
    stats.update(records=len(records), sources=len(sources), edges=len(graph['edges']),
                 checks=len(checks), experiments=len(experiments),
                 eligible_records=sum(r['publication_status'] == 'eligible' for r in records.values()),
                 published_records=sum(r['publication_status'] == 'published' for r in records.values()))
    if not records:
        errors.append('catalog/proposals: no scholarly records; empty validation cannot establish readiness')
    if len({r['work']['id'] for r in records.values()}) != len(records):
        errors.append('catalog/proposals: duplicate work identity')
    all_ids = [*sources, *rights, *checks, *reviews, *experiments, *receipts, *events]
    if len(all_ids) != len(set(all_ids)):
        errors.append('registries: identifiers collide across evidence registries')

    def require_refs(refs, registry, label):
        for ref in refs:
            if ref not in registry:
                errors.append(label + ': unresolved reference ' + ref)

    review_digests = {}

    def current_review_digest(kind, target):
        key = (kind, target)
        if key not in review_digests:
            review_digests[key] = review_scope_sha256(kind, target, documents)
        return review_digests[key]

    def accepted_review(ref, kind, target):
        row = reviews.get(ref)
        return bool(row and row['kind'] == kind and row['target_id'] == target
                    and row['decision'] == 'accepted' and row['independent']
                    and row['reviewer_id'] != row['author_id'] and row['source_refs']
                    and current_review_digest(kind, target) == row['target_sha256'])

    today = date.today().isoformat()
    for source in sources.values():
        require_refs(source['rights_decision_ids'], rights, source['id'])
        if source['accessed_on'] > today:
            errors.append(source['id'] + ': future source access date')
        for ref in source['rights_decision_ids']:
            if ref in rights and rights[ref]['source_id'] != source['id']:
                errors.append(source['id'] + ': rights decision belongs to another source')
    for review in reviews.values():
        require_refs(review['source_refs'], sources, review['id'])
        require_refs(review['evidence_refs'], {**checks, **experiments, **events, **sources}, review['id'])
        if review['reviewed_on'] > today:
            errors.append(review['id'] + ': future review date')
        if review['independent'] and review['reviewer_id'] == review['author_id']:
            errors.append(review['id'] + ': self-review cannot be independent')
        if review['decision'] == 'accepted' and review['target_sha256'] != current_review_digest(review['kind'], review['target_id']):
            errors.append(review['id'] + ': accepted review target or dependent evidence content changed')
    for check in checks.values():
        require_refs([check['source_id']], sources, check['id'])
        if check['checked_on'] > today:
            errors.append(check['id'] + ': future check date')
        if check['source_id'] in sources and check['checked_on'] < sources[check['source_id']]['accessed_on']:
            errors.append(check['id'] + ': check predates the referenced source observation')
        checked_record = by_revision.get(check['revision_id'])
        if check['status'] == 'matched' and (not checked_record or not check['observations'] or
                not check['observed_fields_sha256'] or
                checked_fields_sha256(checked_record, check['observations']) != check['observed_fields_sha256']):
            errors.append(check['id'] + ': matched check does not bind the current observed field values')
        if check['kind'] == 'integrity_notice' and check['source_id'] in sources and sources[check['source_id']]['source_role'] not in ('authoritative_notice', 'publisher_metadata'):
            errors.append(check['id'] + ': integrity check requires an authoritative notice/publisher source')
    for decision in rights.values():
        require_refs([decision['source_id']], sources, decision['id'])
        pairs = [(p['field'], p['operation']) for p in decision['permissions']]
        if len(pairs) != len(set(pairs)):
            errors.append(decision['id'] + ': duplicate field/operation permission')
        for permission in decision['permissions']:
            require_refs(permission['evidence_refs'], sources, decision['id'])
            if permission['decision'] in ('allowed', 'conditional'):
                if not permission['evidence_refs'] or not decision['assessed_on']:
                    errors.append(decision['id'] + ': permission requires dated source evidence')
                if not any(sources.get(ref, {}).get('source_role') in ('terms', 'original_artifact') for ref in permission['evidence_refs']):
                    errors.append(decision['id'] + ': permission needs applicable terms or original-artifact evidence')
                if not accepted_review(permission['review_id'], 'rights', decision['id']):
                    errors.append(decision['id'] + ': permission requires independent accepted rights review')
                if permission['decision'] == 'conditional' and not permission['conditions']:
                    errors.append(decision['id'] + ': conditional permission lacks explicit conditions')

    seen_identifiers = {}
    revision_to_record = {}
    for path, record in sorted(records.items()):
        rid = record['record_id']; revision = record['revision']; revision_to_record[revision['id']] = rid
        prefix = path + ' [' + rid + ']'
        if record['work']['id'] != rid or revision['work_id'] != rid:
            errors.append(prefix + ': work/record/revision identity mismatch')
        if len({rid, record['manifestation']['id'], revision['id']}) != 3:
            errors.append(prefix + ': work, manifestation and revision must have distinct identities')
        if revision['first_submitted_on'] > revision['revised_on']:
            errors.append(prefix + ': revision predates first submission')
        for ident in record['work']['identifiers']:
            if ident['scope'] != 'work':
                errors.append(prefix + ': work identifier has incorrect scope')
            key = (ident['scheme'], ident['value'].strip().lower())
            if key in seen_identifiers:
                errors.append(prefix + ': duplicate scholarly identifier already used by ' + seen_identifiers[key])
            seen_identifiers[key] = rid
            if ident['scheme'] == 'doi' and (ident['value'] != ident['value'].lower() or not re.fullmatch(r'10\.\d{4,9}/\S+', ident['value'])):
                errors.append(prefix + ': DOI must be normalized identifier, without resolver prefix')
        require_refs(record['source_refs'], sources, prefix)
        require_refs(record['rights_decision_ids'], rights, prefix)
        if any(rights.get(ref, {}).get('source_id') not in record['source_refs'] for ref in record['rights_decision_ids'] if ref in rights):
            errors.append(prefix + ': rights decision belongs to an undeclared source')
        require_refs(record['citation_check_ids'] + record['integrity_check_ids'], checks, prefix)
        require_refs(record['scientific_review_ids'] + record['editorial_review_ids'] + record['reproduction_review_ids'], reviews, prefix)
        require_refs(record['experiment_ids'], experiments, prefix)
        require_refs(record['integrity_event_ids'], events, prefix)
        for provenance in record['upstream_refs']:
            p = PurePosixPath(provenance['path'])
            if p.is_absolute() or '..' in p.parts:
                errors.append(prefix + ': unsafe upstream repository path')
        for author in record['authors']:
            if (author['identity_status'] == 'unresolved') != (author['entity_id'] is None):
                errors.append(prefix + ': unresolved author must not acquire an invented entity identity')
            if author['entity_id'] is not None and nodes.get(author['entity_id'], {}).get('kind') != 'person':
                errors.append(prefix + ': author identity lacks a person graph node')
            for affiliation in author['affiliations']:
                require_refs(affiliation['source_refs'], sources, prefix)
                if author['identity_status'] == 'unresolved' or nodes.get(affiliation['organization_id'], {}).get('kind') != 'organization':
                    errors.append(prefix + ': affiliation requires resolved person and organization evidence')
                if affiliation['valid_from'] and affiliation['valid_to'] and affiliation['valid_from'] > affiliation['valid_to']:
                    errors.append(prefix + ': reversed affiliation interval')
        for ident in revision['identifiers']:
            if ident['scope'] != 'revision':
                errors.append(prefix + ': revision identifier has incorrect scope')
            if ident['scheme'] == 'arxiv':
                if not re.fullmatch(r'\d{4}\.\d{4,5}v[1-9]\d*', ident['value']):
                    errors.append(prefix + ': arXiv revision must include explicit vN')
                expected = 'https://arxiv.org/abs/' + ident['value']
                if record['manifestation']['canonical_url'] != expected:
                    errors.append(prefix + ': citation URL does not identify the exact arXiv revision')
                work_arxiv = [x['value'] for x in record['work']['identifiers'] if x['scheme'] == 'arxiv']
                if not work_arxiv or any(ident['value'] != value + revision['version_label'] for value in work_arxiv):
                    errors.append(prefix + ': arXiv work and revision identifiers disagree')
        for check_id in record['citation_check_ids']:
            check = checks.get(check_id)
            if check and (check['revision_id'] != revision['id'] or check['source_id'] not in record['source_refs'] or check['kind'] != 'bibliographic_metadata'):
                errors.append(prefix + ': citation check does not cover this revision/source')
        if record['citation_verification'] == 'metadata_checked':
            scoped = [checks[c] for c in record['citation_check_ids'] if c in checks and checks[c]['status'] == 'matched' and checks[c]['revision_id'] == revision['id']]
            observed = {field for c in scoped for field in c['observations']}
            if not scoped or not METADATA_FIELDS <= observed:
                errors.append(prefix + ': metadata_checked requires actual matched checks for all bibliographic fields')
            if not any(sources.get(c['source_id'], {}).get('url') == record['manifestation']['canonical_url'] for c in scoped):
                errors.append(prefix + ': matched citation evidence lacks the exact revision URL')
        evidence_by_field = {}
        for entry in record['field_evidence']:
            evidence_by_field.setdefault(entry['field'], []).append(entry)
            if not pointer_exists(record, entry['field']):
                errors.append(prefix + ': field evidence points to a nonexistent field ' + entry['field'])
            if entry['source_id'] not in record['source_refs']:
                errors.append(prefix + ': field source is absent from record source_refs')
            if entry['check_id'] is not None:
                check = checks.get(entry['check_id'])
                if not check or check['source_id'] != entry['source_id'] or check['revision_id'] != revision['id'] or entry['field'] not in check['observations']:
                    errors.append(prefix + ': field check does not bind this field/source/revision')
                elif entry['scope'] == 'bibliographic_metadata' and record['citation_verification'] == 'metadata_checked' and check['status'] != 'matched':
                    errors.append(prefix + ': checked metadata contradicts its field check')
            elif entry['scope'] == 'bibliographic_metadata' and record['citation_verification'] == 'metadata_checked':
                errors.append(prefix + ': checked metadata field lacks its source check')
        if not PUBLIC_FIELDS <= set(record['publication_fields']):
            errors.append(prefix + ': publication projection omits a required factual field')
        for field in record['publication_fields']:
            if not pointer_exists(record, field) or field not in evidence_by_field:
                errors.append(prefix + ': publication field lacks explicit field provenance: ' + field)
        if record['scientific_validity'] != 'not_assessed' or record['evidence_confidence'] != 'not_assessed':
            if not any(accepted_review(x, 'scientific', rid) for x in record['scientific_review_ids']):
                errors.append(prefix + ': scientific/confidence assessment requires independent scientific review')
        for claim in record['claims']:
            if claim['source_id'] not in record['source_refs']:
                errors.append(prefix + ': claim lacks a declared source')
            if claim['origin'] == 'independently_measured' and claim['experiment_id'] not in record['experiment_ids']:
                errors.append(prefix + ': independently measured claim lacks a scoped experiment')
            if claim['origin'] == 'independently_measured':
                exp = experiments.get(claim['experiment_id'])
                if not exp or not exp['actual_execution'] or not exp['independent_from_authors'] or exp['record_id'] != rid or exp['revision_id'] != revision['id']:
                    errors.append(prefix + ': independently measured claim requires actual independent execution evidence')
                if not any(accepted_review(x, 'scientific', rid) or accepted_review(x, 'reproduction', rid) for x in claim['review_ids']):
                    errors.append(prefix + ': independently measured claim requires independent review of its evidence')
            if claim['origin'] == 'reviewer_interpretation' and not any(accepted_review(x, 'scientific', rid) for x in claim['review_ids']):
                errors.append(prefix + ': interpretation lacks scientific review')
        if record['claims'] and '/claims' not in record['publication_fields']:
            errors.append(prefix + ': claims require explicit publication scope and provenance')
        if len({c['id'] for c in record['claims']}) != len(record['claims']):
            errors.append(prefix + ': duplicate claim identity')
        if record['reproducibility_status'] != 'not_attempted':
            if not record['experiment_ids'] or not any(accepted_review(x, 'reproduction', rid) for x in record['reproduction_review_ids']):
                errors.append(prefix + ': reproduction status requires scoped artifacts and independent reproduction review')
        for experiment_id in record['experiment_ids']:
            exp = experiments.get(experiment_id)
            if exp and (exp['record_id'] != rid or exp['revision_id'] != revision['id']):
                errors.append(prefix + ': experiment belongs to another work/revision')
            if exp and record['reproducibility_status'] in ('independent_attempt', 'partially_reproduced', 'reproduced', 'failed_to_reproduce') and not (exp['actual_execution'] and exp['independent_from_authors']):
                errors.append(prefix + ': independent reproduction requires actual independent execution evidence')
        if record['editorial_status'] == 'accepted' and not any(accepted_review(x, 'editorial', rid) for x in record['editorial_review_ids']):
            errors.append(prefix + ': editorial acceptance requires independent accepted review')
        if record['integrity_status'] != 'not_assessed':
            if not any(checks.get(x, {}).get('kind') == 'integrity_notice' and checks[x]['revision_id'] == revision['id'] and checks[x]['status'] == 'matched' for x in record['integrity_check_ids']):
                errors.append(prefix + ': integrity status requires a scoped authoritative check')
            if '/integrity_status' not in evidence_by_field or '/integrity_status' not in record['publication_fields']:
                errors.append(prefix + ': assessed integrity status requires explicit field evidence and publication scope')
            for c in record['integrity_check_ids']:
                if c in checks and checks[c]['source_id'] not in record['source_refs']:
                    errors.append(prefix + ': integrity check source is absent from record source_refs')
        if record['integrity_status'] in ('notice_present', 'withdrawn', 'retracted') and not record['integrity_event_ids']:
            errors.append(prefix + ': integrity notice status requires a sourced event')
        needed_event = {'withdrawn': 'withdrawal', 'retracted': 'retraction'}.get(record['integrity_status'])
        if needed_event and not any(events.get(e, {}).get('kind') == needed_event for e in record['integrity_event_ids']):
            errors.append(prefix + ': integrity status lacks the matching notice kind')
        for event_id in record['integrity_event_ids']:
            event = events.get(event_id)
            if event and (event['work_id'] != rid or revision['id'] not in event['revision_ids']):
                errors.append(prefix + ': integrity event is scoped to a different work/revision')

        gated = publication or record['publication_status'] in ('eligible', 'published') or record['rights_status'] == 'reviewed_for_requested_uses'
        if gated:
            if publication and record['publication_status'] == 'withheld':
                errors.append(prefix + ': publication gate rejects a withheld proposal')
            if record['publication_status'] in ('eligible', 'published') or publication:
                if record['editorial_status'] != 'accepted' or not any(accepted_review(x, 'editorial', rid) for x in record['editorial_review_ids']):
                    errors.append(prefix + ': publication requires independent editorial acceptance')
                if record['citation_verification'] != 'metadata_checked':
                    errors.append(prefix + ': publication requires checked citation metadata')
                if record['rights_status'] != 'reviewed_for_requested_uses':
                    errors.append(prefix + ': publication rights remain unresolved')
                if record['integrity_status'] == 'not_assessed':
                    errors.append(prefix + ': publication requires a dated integrity-notice check')
            for field in record['publication_fields']:
                for field_source in {x['source_id'] for x in evidence_by_field.get(field, [])}:
                    applicable = [rights[r] for r in record['rights_decision_ids'] if r in rights and rights[r]['source_id'] == field_source]
                    for operation in record['publication_operations']:
                        permitted = []
                        for decision in applicable:
                            for p in decision['permissions']:
                                if p['field'] == field and p['operation'] == operation:
                                    permitted.append((decision, p))
                        if not permitted or any(p['decision'] not in ('allowed', 'conditional') or not p['conditions_satisfied'] or not p['evidence_refs'] or not accepted_review(p['review_id'], 'rights', decision['id']) or (decision['valid_until'] and decision['valid_until'] < today) for decision, p in permitted):
                            errors.append(prefix + ': publication permission missing/conflicting for ' + field + ' / ' + field_source + ' / ' + operation)
            for event_id in record['integrity_event_ids']:
                event = events.get(event_id)
                if event and not accepted_review(event['handling_review_id'], 'integrity', event_id):
                    errors.append(prefix + ': publication requires explicit handling of integrity notice ' + event_id)
        if record['publication_status'] == 'published':
            receipt = receipts.get(record['publication_receipt_id'])
            if not receipt or receipt['record_id'] != rid or receipt['record_sha256'] != hashlib.sha256((root / path).read_bytes()).hexdigest():
                errors.append(prefix + ': published status lacks an exact-byte publication receipt')
        elif record['publication_receipt_id'] is not None:
            errors.append(prefix + ': unpublished proposal cannot claim a publication receipt')

    for exp in experiments.values():
        require_refs(exp['source_refs'], sources, exp['id'])
        if exp['record_id'] not in by_id:
            errors.append(exp['id'] + ': experiment references an unknown work')
        elif exp['id'] not in by_id[exp['record_id']]['experiment_ids']:
            errors.append(exp['id'] + ': experiment is omitted from its scholarly record')
        if not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', exp['code_revision']):
            errors.append(exp['id'] + ': experiment code must be pinned to a full immutable revision')
        if exp['environment_sha256'] == '0' * 64 or exp['results_sha256'] == '0' * 64:
            errors.append(exp['id'] + ': placeholder artifact digest is forbidden')
    for receipt in receipts.values():
        require_refs(receipt['review_ids'], reviews, receipt['id'])
        record = by_id.get(receipt['record_id'])
        if not record or record['publication_receipt_id'] != receipt['id'] or record['publication_status'] != 'published':
            errors.append(receipt['id'] + ': publication receipt is not linked by a published record')
        if not any(accepted_review(r, 'editorial', receipt['record_id']) for r in receipt['review_ids']):
            errors.append(receipt['id'] + ': publication receipt requires accepted editorial review')
        if receipt['published_on'] > today:
            errors.append(receipt['id'] + ': future publication receipt')
    for event in events.values():
        require_refs([event['source_id']], sources, event['id'])
        if sources.get(event['source_id'], {}).get('source_role') not in ('authoritative_notice', 'publisher_metadata'):
            errors.append(event['id'] + ': correction/withdrawal/retraction requires an authoritative source')
        if event['announced_on'] > today:
            errors.append(event['id'] + ': future integrity event date')
        if event['work_id'] not in by_id or any(revision_to_record.get(r) != event['work_id'] for r in event['revision_ids']):
            errors.append(event['id'] + ': integrity event identity does not resolve')
        elif event['id'] not in by_id[event['work_id']]['integrity_event_ids']:
            errors.append(event['id'] + ': integrity event is omitted from the affected record')

    allowed = {
        'has_revision': ({'scholarly_work'}, {'revision'}),
        'has_manifestation': ({'scholarly_work'}, {'manifestation'}),
        'authored_by': ({'scholarly_work', 'revision'}, {'person'}),
        'affiliated_with': ({'person'}, {'organization'}),
        'introduces_method': ({'revision'}, {'method'}),
        'uses_dataset': ({'revision', 'experiment'}, {'dataset'}),
        'evaluated_on': ({'revision', 'experiment', 'model'}, {'benchmark', 'dataset'}),
        'releases_model': ({'revision'}, {'model'}),
        'releases_code': ({'revision'}, {'code_release'}),
        'cites': ({'revision'}, {'scholarly_work', 'revision'}),
        'supports': ({'revision', 'experiment'}, {'claim'}),
        'contradicts': ({'revision', 'experiment'}, {'claim'}),
        'reproduces': ({'reproduction', 'experiment'}, {'claim', 'experiment'}),
        'corrects': ({'integrity_notice'}, {'revision'}),
        'withdraws': ({'integrity_notice'}, {'revision'}),
        'retracts': ({'integrity_notice'}, {'revision'}),
        'raises_question': ({'revision'}, {'research_question'}),
    }
    expected_nodes = {identity: (kind, r['record_id']) for r in records.values() for identity, kind in [(r['record_id'], 'scholarly_work'), (r['manifestation']['id'], 'manifestation'), (r['revision']['id'], 'revision')]}
    expected_nodes.update({event['id']: ('integrity_notice', event['work_id']) for event in events.values()})
    for identity, (kind, owner) in expected_nodes.items():
        if nodes.get(identity, {}).get('kind') != kind or nodes.get(identity, {}).get('record_id') != owner:
            errors.append('graph: missing or mistyped scholarly node ' + identity)
    for node in nodes.values():
        if node['record_id'] is not None and node['record_id'] not in by_id:
            errors.append(node['id'] + ': node references an unknown record')
        if node['id'] not in expected_nodes and node['external_ref'] is None:
            errors.append(node['id'] + ': extra entity requires pinned external provenance')
    seen_edges = set()
    for edge in graph['edges']:
        require_refs(edge['source_refs'], sources, edge['id'])
        require_refs(edge['check_ids'], checks, edge['id'])
        require_refs(edge['review_ids'], reviews, edge['id'])
        triple = (edge['subject'], edge['predicate'], edge['object'])
        if triple in seen_edges:
            errors.append(edge['id'] + ': duplicate semantic edge')
        seen_edges.add(triple)
        kinds = allowed[edge['predicate']]
        if nodes.get(edge['subject'], {}).get('kind') not in kinds[0] or nodes.get(edge['object'], {}).get('kind') not in kinds[1]:
            errors.append(edge['id'] + ': graph predicate has invalid or unresolved endpoint types')
        if edge['assertion_level'] == 'metadata_checked' and not any(checks.get(c, {}).get('status') == 'matched' and checks[c]['source_id'] in edge['source_refs'] for c in edge['check_ids']):
            errors.append(edge['id'] + ': metadata edge lacks a matching source check')
        if edge['predicate'] in ('supports', 'contradicts', 'reproduces'):
            review_kind = 'reproduction' if edge['predicate'] == 'reproduces' else 'scientific'
            if edge['assertion_level'] != 'reviewed' or not any(accepted_review(r, review_kind, edge['id']) for r in edge['review_ids']):
                errors.append(edge['id'] + ': scientific relation cannot be inferred from a metadata citation')
            if edge['predicate'] == 'reproduces':
                experiment = experiments.get(edge['subject'])
                if not experiment or not experiment['actual_execution'] or not experiment['independent_from_authors'] or experiment['record_id'] != nodes.get(edge['subject'], {}).get('record_id'):
                    errors.append(edge['id'] + ': reproduces relation requires an actual scoped independent experiment')
        if edge['predicate'] in ('corrects', 'withdraws', 'retracts'):
            event = events.get(edge['subject'])
            expected_kind = {'corrects': 'correction', 'withdraws': 'withdrawal', 'retracts': 'retraction'}[edge['predicate']]
            if (not event or event['kind'] != expected_kind or edge['object'] not in event['revision_ids']
                    or event['work_id'] != nodes.get(edge['object'], {}).get('record_id')
                    or event['source_id'] not in edge['source_refs'] or edge['assertion_level'] != 'reviewed'
                    or not any(r == event['handling_review_id'] and accepted_review(r, 'integrity', event['id']) for r in edge['review_ids'])
                    or not any(checks.get(c, {}).get('kind') == 'integrity_notice' and checks[c]['source_id'] == event['source_id']
                               and checks[c]['revision_id'] == edge['object'] and checks[c]['status'] == 'matched' for c in edge['check_ids'])):
                errors.append(edge['id'] + ': integrity relation requires a matching authoritative reviewed notice and affected revision')
        if edge['predicate'] in ('has_revision', 'has_manifestation'):
            record = by_id.get(edge['subject'])
            expected = record['revision' if edge['predicate'] == 'has_revision' else 'manifestation']['id'] if record else None
            if edge['object'] != expected:
                errors.append(edge['id'] + ': identity edge binds the wrong scholarly object')
            if record and not set(edge['source_refs']) <= set(record['source_refs']):
                errors.append(edge['id'] + ': identity edge uses a source for another record')
            if record and edge['assertion_level'] == 'metadata_checked' and not any(checks.get(c, {}).get('revision_id') == record['revision']['id'] and checks[c]['source_id'] in edge['source_refs'] and checks[c]['status'] == 'matched' for c in edge['check_ids']):
                errors.append(edge['id'] + ': identity edge check belongs to another revision')
        if edge['assertion_level'] == 'reviewed' and edge['predicate'] not in ('corrects', 'withdraws', 'retracts'):
            if not any(accepted_review(r, reviews.get(r, {}).get('kind'), edge['id']) for r in edge['review_ids']):
                errors.append(edge['id'] + ': reviewed edge lacks an independent accepted review')
    audit = documents['evidence/upstream-inspection.json']
    counts = audit['observed_counts']
    if counts['market_documented'] + counts['market_unknown'] != counts['market_cells']:
        errors.append('upstream inspection: feature-cell arithmetic mismatch')
    manifest_keys = [(x['repository'], x['path']) for x in audit['files']]
    if len(manifest_keys) != len(set(manifest_keys)):
        errors.append('upstream inspection: duplicate inspected file')
    for repo, n in [('pick-your-ai-research', audit['sampled_research_file_count']), ('pick-your-ai-website', audit['sampled_website_file_count'])]:
        if sum(x['repository'] == 'Pick-Your-AI/' + repo for x in audit['files']) != n:
            errors.append('upstream inspection: sampled file denominator mismatch for ' + repo)
    return sorted(set(errors)), stats


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--publication', action='store_true', help='Require every proposal to satisfy release gates; withheld proposals fail.')
    args = parser.parse_args(argv)
    errors, stats = validate(args.root, args.publication)
    print(json.dumps({'status': 'failed' if errors else 'passed', 'mode': 'publication' if args.publication else 'research', 'counts': stats, 'errors': errors}, indent=2))
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
