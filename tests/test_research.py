"""Mutation tests exercise release boundaries, not scientific result validity.

All invented review/rights/integrity receipts exist only in temporary test copies
and use explicitly synthetic IDs and example.org URLs. They are never evidence.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('papers_research_validation', ROOT / 'scripts/validate_research.py')
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class ResearchValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='papers-research-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in (*validator.MATERIAL_ROOTS, 'schemas'):
            shutil.copytree(ROOT / name, self.root / name)
        self.proposal = 'catalog/proposals/arxiv-1803.09010.json'

    def read(self, name):
        return json.loads((self.root / name).read_text())

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

    def errors(self, publication=False):
        return validator.validate(self.root, publication)[0]

    def assert_rejected(self, text, publication=False):
        errors = self.errors(publication)
        self.assertTrue(errors, 'mutation unexpectedly accepted')
        self.assertTrue(any(text in error for error in errors), '\n'.join(errors))

    def change_record(self, **updates):
        record = self.read(self.proposal)
        record.update(updates)
        self.write(self.proposal, record)
        return record

    def refresh_synthetic_review_bindings(self):
        """Test-only generation of explicitly synthetic receipt digests."""
        paths = list(validator.SCHEMA_FILES)
        paths += [str(p.relative_to(self.root)) for p in (self.root / 'catalog/proposals').glob('*.json')]
        documents = {path: self.read(path) for path in paths}
        evidence = documents['evidence/research-evidence.json']
        for review in evidence['reviews']:
            self.assertTrue(review['id'].startswith('review.synthetic.'), 'Never rewrite a real review')
            review['target_sha256'] = validator.review_scope_sha256(review['kind'], review['target_id'], documents)
        self.write('evidence/research-evidence.json', evidence)

    def make_one_synthetically_eligible(self):
        """Supply complete synthetic scopes to test that no global grant is used."""
        record = self.read(self.proposal)
        source_data = self.read('sources/register.json')
        rights_data = self.read('sources/rights.json')
        evidence = self.read('evidence/research-evidence.json')
        sid = 'source.synthetic.notice'
        terms = 'source.synthetic.terms'
        notice_right = 'rights.synthetic.notice'
        cid = 'check.synthetic.integrity'
        for ident, role, url, rights_refs in [
            (sid, 'authoritative_notice', 'https://example.org/synthetic-notice', [notice_right]),
            (terms, 'terms', 'https://example.org/synthetic-terms', []),
        ]:
            source_data['sources'].append({'id': ident, 'url': url, 'publisher': 'SYNTHETIC TEST FIXTURE', 'source_role': role,
                'accessed_on': '2026-10-22', 'retrieval_method': 'manual_review', 'content_sha256': None,
                'public': True, 'rights_decision_ids': rights_refs, 'limitations': ['Synthetic fixture; never real evidence.']})
        evidence['checks'].append({'id': cid, 'kind': 'integrity_notice', 'source_id': sid,
            'revision_id': record['revision']['id'], 'checked_on': '2026-10-22',
            'checker_id': 'synthetic:checker', 'method': 'read_authoritative_notice', 'status': 'matched',
            'observations': ['/integrity_status'], 'observed_fields_sha256': None,
            'scope': 'SYNTHETIC TEST ONLY', 'notes': 'No real notice check.'})

        def review(ident, kind, target):
            evidence['reviews'].append({'id': ident, 'kind': kind, 'target_id': target,
                'reviewer_id': 'synthetic:independent-reviewer', 'author_id': 'synthetic:author',
                'independent': True, 'decision': 'accepted', 'reviewed_on': '2026-10-22',
                'source_refs': [terms], 'evidence_refs': [terms], 'scope': 'SYNTHETIC TEST ONLY',
                'target_sha256': '0' * 64, 'notes': 'Never a real approval or rights decision.'})

        original_right = next(d for d in rights_data['decisions'] if d['id'] == record['rights_decision_ids'][0])
        original_right['assessed_on'] = '2026-10-22'
        for permission in original_right['permissions']:
            permission.update(decision='allowed', evidence_refs=[terms], review_id='review.synthetic.rights', conditions_satisfied=True)
        review('review.synthetic.rights', 'rights', original_right['id'])
        review('review.synthetic.notice-rights', 'rights', notice_right)
        review('review.synthetic.editorial', 'editorial', record['record_id'])
        rights_data['decisions'].append({'id': notice_right, 'source_id': sid, 'artifact_scope': 'SYNTHETIC TEST ONLY',
            'assessed_on': '2026-10-22', 'valid_until': None,
            'permissions': [{'field': '/integrity_status', 'operation': op, 'decision': 'allowed',
                'evidence_refs': [terms], 'review_id': 'review.synthetic.notice-rights', 'conditions': [],
                'conditions_satisfied': True} for op in ['display', 'export']], 'notes': 'SYNTHETIC TEST ONLY'})
        record['source_refs'].append(sid)
        record['rights_decision_ids'].append(notice_right)
        record['publication_fields'].append('/integrity_status')
        record['field_evidence'].append({'field': '/integrity_status', 'source_id': sid, 'locator': 'SYNTHETIC TEST ONLY',
            'check_id': cid, 'scope': 'bibliographic_metadata'})
        record.update(editorial_status='accepted', editorial_review_ids=['review.synthetic.editorial'],
            rights_status='reviewed_for_requested_uses', integrity_status='notices_checked',
            integrity_check_ids=[cid], publication_status='eligible')
        evidence['checks'][-1]['observed_fields_sha256'] = validator.checked_fields_sha256(record, ['/integrity_status'])
        for path, data in [('sources/register.json', source_data), ('sources/rights.json', rights_data),
                           ('evidence/research-evidence.json', evidence), (self.proposal, record)]:
            self.write(path, data)
        self.refresh_synthetic_review_bindings()
        self.assertEqual(self.errors(), [])
        return record

    def test_baseline_is_withheld_metadata_and_zero_experiments(self):
        errors, stats = validator.validate(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(stats, {'records': 4, 'sources': 4, 'edges': 8, 'checks': 4,
            'experiments': 0, 'eligible_records': 0, 'published_records': 0})

    def test_publication_gate_rejects_all_current_candidates(self):
        self.assert_rejected('withheld proposal', publication=True)

    def test_scientific_verified_label_cannot_be_fabricated(self):
        self.change_record(scientific_validity='verified')
        self.assert_rejected('declared vocabulary')

    def test_verified_citation_label_is_not_a_legal_enum(self):
        self.change_record(citation_verification='verified')
        self.assert_rejected('declared vocabulary')

    def test_metadata_checked_requires_actual_scoped_check(self):
        self.change_record(citation_check_ids=[])
        self.assert_rejected('requires actual matched checks')

    def test_borrowed_check_from_other_revision_is_rejected(self):
        self.change_record(citation_check_ids=['check.arxiv.2104.08663.v4'])
        self.assert_rejected('does not cover this revision/source')

    def test_unversioned_arxiv_url_is_rejected(self):
        record = self.read(self.proposal)
        record['manifestation']['canonical_url'] = 'https://arxiv.org/abs/1803.09010'
        self.write(self.proposal, record)
        self.assert_rejected('exact arXiv revision')

    def test_work_revision_identity_mismatch_is_rejected(self):
        record = self.read(self.proposal)
        record['revision']['work_id'] = 'paper.arxiv.other'
        self.write(self.proposal, record)
        self.assert_rejected('identity mismatch')

    def test_false_author_resolution_is_rejected(self):
        record = self.read(self.proposal)
        record['authors'][0]['entity_id'] = 'person.invented'
        self.write(self.proposal, record)
        self.assert_rejected('invented entity identity')

    def test_full_text_or_abstract_field_is_rejected(self):
        self.change_record(abstract='SYNTHETIC restricted material example')
        self.assert_rejected('restricted material field')

    def test_raw_binary_document_is_rejected(self):
        (self.root / 'sources/paper.pdf').write_bytes(b'%PDF SYNTHETIC TEST')
        self.assert_rejected('raw/binary/unregistered')

    def test_private_material_path_is_rejected(self):
        target = self.root / 'evidence/private/notes.md'
        target.parent.mkdir()
        target.write_text('SYNTHETIC private fixture')
        self.assert_rejected('private/raw material path')

    def test_credentials_are_rejected_without_echoing_them(self):
        fake = 'ghp_' + 'A' * 36
        (self.root / 'evidence/secret.md').write_text(fake)
        self.assert_rejected('credential-like material')
        self.assertNotIn(fake, '\n'.join(self.errors()))

    def test_credential_bearing_url_is_rejected(self):
        sources = self.read('sources/register.json')
        sources['sources'][0]['url'] = 'https://synthetic:secret@example.org/paper'
        self.write('sources/register.json', sources)
        self.assert_rejected('private source URL')

    def test_private_network_url_is_rejected(self):
        sources = self.read('sources/register.json')
        sources['sources'][0]['url'] = 'https://127.0.0.1/paper'
        self.write('sources/register.json', sources)
        self.assert_rejected('private source URL')

    def test_unregistered_json_is_never_silently_skipped(self):
        self.write('sources/unchecked.json', {'data': 'SYNTHETIC'})
        self.assert_rejected('unregistered JSON artifact')

    def test_duplicate_json_key_is_rejected(self):
        target = self.root / self.proposal
        text = target.read_text()
        target.write_text(text.replace('"schema_version": "0.1.0",', '"schema_version": "0.1.0", "schema_version": "0.1.0",', 1))
        self.assert_rejected('duplicate JSON key')

    def test_unknown_schema_keyword_fails_closed(self):
        name = 'schemas/scholarly-record.schema.json'
        schema = self.read(name)
        schema['if'] = {'const': 'SYNTHETIC unsupported assertion'}
        self.write(name, schema)
        self.assert_rejected('unsupported schema keyword')

    def test_anyof_does_not_skip_sibling_constraints(self):
        schema = {'anyOf': [{'type': 'string'}, {'type': 'null'}], 'maxLength': 3}
        self.assertTrue(validator.schema_errors('too long', schema, 'fixture'))
        self.assertEqual(validator.schema_errors('yes', schema, 'fixture'), [])

    def test_malformed_schema_assertions_fail_before_data_evaluation(self):
        name = 'schemas/scholarly-record.schema.json'
        baseline = self.read(name)
        for key, value in [('type', 'imaginary'), ('type', ['string']), ('properties', []),
                           ('required', [1]), ('enum', []), ('anyOf', []), ('pattern', '['),
                           ('minItems', -1), ('uniqueItems', 'yes'), ('additionalProperties', {}),
                           ('minimum', True), ('format', None)]:
            with self.subTest(keyword=key, value=value):
                changed = copy.deepcopy(baseline); changed[key] = value
                self.write(name, changed)
                self.assertTrue(self.errors())
        self.write(name, baseline)
        self.assertEqual(self.errors(), [])

    def test_json_boolean_does_not_match_numeric_enum(self):
        self.assertTrue(validator.schema_errors(True, {'enum': [1]}, 'fixture'))
        self.assertEqual(validator.schema_errors(1.0, {'const': 1}, 'fixture'), [])

    def test_impossible_calendar_date_is_rejected(self):
        record = self.read(self.proposal)
        record['revision']['revised_on'] = '2026-02-31'
        self.write(self.proposal, record)
        self.assert_rejected('invalid ISO calendar date')

    def test_grant_without_review_is_rejected(self):
        rights = self.read('sources/rights.json')
        rights['decisions'][0]['permissions'][0]['decision'] = 'allowed'
        self.write('sources/rights.json', rights)
        self.assert_rejected('independent accepted rights review')

    def test_eligible_label_cannot_skip_publication_gates(self):
        self.change_record(publication_status='eligible')
        self.assert_rejected('publication rights remain unresolved')

    def test_confidence_cannot_be_laundered_from_metadata_check(self):
        self.change_record(evidence_confidence='high')
        self.assert_rejected('independent scientific review')

    def test_reproduction_cannot_be_claimed_without_run_evidence(self):
        self.change_record(reproducibility_status='reproduced')
        self.assert_rejected('scoped artifacts and independent reproduction review')

    def test_independently_measured_claim_requires_execution(self):
        record = self.read(self.proposal)
        record['claims'] = [{'id': 'claim.synthetic', 'statement': 'SYNTHETIC TEST ONLY',
            'origin': 'independently_measured', 'source_id': record['source_refs'][0],
            'locator': 'SYNTHETIC', 'experiment_id': None, 'review_ids': [], 'limitations': []}]
        self.write(self.proposal, record)
        self.assert_rejected('actual independent execution evidence')

    def test_dangling_graph_endpoint_is_rejected(self):
        graph = self.read('research/graph.json')
        graph['edges'][0]['object'] = 'paper.missing'
        self.write('research/graph.json', graph)
        self.assert_rejected('invalid or unresolved endpoint types')

    def test_scientific_support_is_not_inferred_from_citation(self):
        graph = self.read('research/graph.json')
        graph['edges'][0]['predicate'] = 'supports'
        self.write('research/graph.json', graph)
        self.assert_rejected('cannot be inferred from a metadata citation')

    def test_identity_edge_cannot_borrow_another_source_check(self):
        graph = self.read('research/graph.json')
        graph['edges'][0]['source_refs'] = ['source.arxiv.2104.08663.v4']
        graph['edges'][0]['check_ids'] = ['check.arxiv.2104.08663.v4']
        self.write('research/graph.json', graph)
        self.assert_rejected('identity edge check belongs to another revision')

    def test_retraction_claim_requires_authoritative_notice(self):
        self.change_record(integrity_status='retracted')
        self.assert_rejected('matching notice kind')

    def test_duplicate_work_identifier_is_rejected(self):
        record = self.read('catalog/proposals/arxiv-2104.08663.json')
        record['work']['identifiers'][1]['value'] = '10.48550/arxiv.1803.09010'
        self.write('catalog/proposals/arxiv-2104.08663.json', record)
        self.assert_rejected('duplicate scholarly identifier')

    def test_inspection_denominator_is_checked(self):
        audit = self.read('evidence/upstream-inspection.json')
        audit['sampled_research_file_count'] = 999
        self.write('evidence/upstream-inspection.json', audit)
        self.assert_rejected('sampled file denominator mismatch')

    def test_complete_synthetic_scope_can_be_eligible_without_scientific_claims(self):
        self.make_one_synthetically_eligible()
        errors, stats = validator.validate(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(stats['eligible_records'], 1)
        self.assertEqual(stats['experiments'], 0)

    def test_metadata_edit_invalidates_source_check(self):
        record = self.read(self.proposal)
        record['work']['title'] = 'SYNTHETIC UNCHECKED TITLE'
        self.write(self.proposal, record)
        self.assert_rejected('current observed field values')

    def test_summary_edit_invalidates_editorial_and_rights_scope(self):
        record = self.make_one_synthetically_eligible()
        record['summary']['text'] += ' Synthetic unreviewed addition.'
        self.write(self.proposal, record)
        self.assert_rejected('dependent evidence content changed')

    def test_changed_rights_condition_invalidates_approval(self):
        self.make_one_synthetically_eligible()
        rights = self.read('sources/rights.json')
        rights['decisions'][0]['permissions'][0]['conditions'] = ['SYNTHETIC changed condition']
        self.write('sources/rights.json', rights)
        self.assert_rejected('dependent evidence content changed')

    def test_changed_terms_observation_invalidates_approval(self):
        self.make_one_synthetically_eligible()
        sources = self.read('sources/register.json')
        next(s for s in sources['sources'] if s['id'] == 'source.synthetic.terms')['limitations'].append('SYNTHETIC changed terms observation')
        self.write('sources/register.json', sources)
        self.assert_rejected('dependent evidence content changed')

    def test_synthetic_integrity_edge_requires_exact_affected_revision(self):
        record = self.make_one_synthetically_eligible()
        event_id = 'event.synthetic.retraction'
        review_id = 'review.synthetic.integrity'
        record['integrity_status'] = 'retracted'
        record['integrity_event_ids'] = [event_id]
        events = self.read('evidence/research-events.json')
        events['events'].append({'id': event_id, 'kind': 'retraction', 'work_id': record['record_id'],
            'revision_ids': [record['revision']['id']], 'announced_on': '2026-10-22',
            'source_id': 'source.synthetic.notice', 'locator': 'SYNTHETIC TEST ONLY',
            'handling_review_id': review_id, 'notes': 'No real retraction is asserted.'})
        evidence = self.read('evidence/research-evidence.json')
        check = next(c for c in evidence['checks'] if c['id'] == 'check.synthetic.integrity')
        check['observed_fields_sha256'] = validator.checked_fields_sha256(record, check['observations'])
        evidence['reviews'].append({'id': review_id, 'kind': 'integrity', 'target_id': event_id,
            'reviewer_id': 'synthetic:independent-reviewer', 'author_id': 'synthetic:author',
            'independent': True, 'decision': 'accepted', 'reviewed_on': '2026-10-22',
            'source_refs': ['source.synthetic.notice'], 'evidence_refs': ['check.synthetic.integrity'],
            'scope': 'SYNTHETIC TEST ONLY', 'target_sha256': '0' * 64, 'notes': 'No real integrity review.'})
        graph = self.read('research/graph.json')
        graph['nodes'].append({'id': event_id, 'kind': 'integrity_notice', 'record_id': record['record_id'], 'external_ref': None})
        graph['edges'].append({'id': 'edge.synthetic.retraction', 'subject': event_id, 'predicate': 'retracts',
            'object': record['revision']['id'], 'source_refs': ['source.synthetic.notice'],
            'locator': 'SYNTHETIC TEST ONLY', 'assertion_level': 'reviewed',
            'check_ids': ['check.synthetic.integrity'], 'review_ids': [review_id]})
        for path, data in [(self.proposal, record), ('evidence/research-events.json', events),
                           ('evidence/research-evidence.json', evidence), ('research/graph.json', graph)]:
            self.write(path, data)
        self.refresh_synthetic_review_bindings()
        self.assertEqual(self.errors(), [])
        graph['edges'][-1]['object'] = 'paper.arxiv.2104.08663.v4'
        self.write('research/graph.json', graph)
        self.assert_rejected('matching authoritative reviewed notice and affected revision')

    def test_reviewed_reproduction_edge_requires_an_actual_experiment(self):
        record = self.read(self.proposal)
        graph = self.read('research/graph.json')
        upstream = record['upstream_refs'][0]
        for ident, kind in [('reproduction.synthetic', 'reproduction'), ('experiment.synthetic', 'experiment')]:
            graph['nodes'].append({'id': ident, 'kind': kind, 'record_id': record['record_id'], 'external_ref': upstream})
        edge = {'id': 'edge.synthetic.reproduction', 'subject': 'reproduction.synthetic', 'predicate': 'reproduces',
            'object': 'experiment.synthetic', 'source_refs': record['source_refs'],
            'locator': 'SYNTHETIC TEST ONLY', 'assertion_level': 'reviewed',
            'check_ids': [], 'review_ids': ['review.synthetic.edge']}
        graph['edges'].append(edge)
        evidence = self.read('evidence/research-evidence.json')
        evidence['reviews'].append({'id': 'review.synthetic.edge', 'kind': 'reproduction', 'target_id': edge['id'],
            'reviewer_id': 'synthetic:independent-reviewer', 'author_id': 'synthetic:author',
            'independent': True, 'decision': 'accepted', 'reviewed_on': '2026-10-22',
            'source_refs': record['source_refs'], 'evidence_refs': record['source_refs'],
            'scope': 'SYNTHETIC TEST ONLY', 'target_sha256': '0' * 64, 'notes': 'No real run exists.'})
        self.write('research/graph.json', graph)
        self.write('evidence/research-evidence.json', evidence)
        self.refresh_synthetic_review_bindings()
        self.assert_rejected('actual scoped independent experiment')

    def test_display_permission_does_not_imply_export_permission(self):
        record = self.make_one_synthetically_eligible()
        rights = self.read('sources/rights.json')
        decision = next(x for x in rights['decisions'] if x['id'] == record['rights_decision_ids'][0])
        next(p for p in decision['permissions'] if p['field'] == '/authors' and p['operation'] == 'export')['decision'] = 'unknown'
        self.write('sources/rights.json', rights)
        self.assert_rejected('/authors / source.arxiv.1803.09010.v8 / export')

    def test_mixed_source_field_cannot_inherit_permissive_source(self):
        record = self.make_one_synthetically_eligible()
        record['field_evidence'].append({'field': '/work/title', 'source_id': 'source.arxiv.2104.08663.v4',
            'locator': 'SYNTHETIC mixed-source fixture', 'check_id': None, 'scope': 'editorial_classification'})
        record['source_refs'].append('source.arxiv.2104.08663.v4')
        self.write(self.proposal, record)
        self.assert_rejected('/work/title / source.arxiv.2104.08663.v4 / display')

    def test_author_cannot_supply_independent_editorial_approval(self):
        self.make_one_synthetically_eligible()
        evidence = self.read('evidence/research-evidence.json')
        review = next(x for x in evidence['reviews'] if x['id'] == 'review.synthetic.editorial')
        review['reviewer_id'] = review['author_id']
        self.write('evidence/research-evidence.json', evidence)
        self.assert_rejected('self-review cannot be independent')

    def test_publication_receipt_must_bind_exact_record_bytes(self):
        record = self.make_one_synthetically_eligible()
        record['publication_status'] = 'published'
        record['publication_receipt_id'] = 'receipt.synthetic'
        self.write(self.proposal, record)
        self.refresh_synthetic_review_bindings()
        evidence = self.read('evidence/research-evidence.json')
        evidence['publication_receipts'].append({'id': 'receipt.synthetic', 'record_id': record['record_id'],
            'record_sha256': hashlib.sha256((self.root / self.proposal).read_bytes()).hexdigest(),
            'release_id': 'SYNTHETIC-TEST-ONLY', 'artifact_url': 'https://example.org/synthetic-release',
            'published_on': '2026-10-22', 'review_ids': ['review.synthetic.editorial']})
        self.write('evidence/research-evidence.json', evidence)
        self.assertEqual(self.errors(), [])
        record['summary']['text'] += ' Synthetic changed bytes.'
        self.write(self.proposal, record)
        self.assert_rejected('exact-byte publication receipt')

    def test_output_is_deterministic_and_does_not_mutate_data(self):
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*.json')}
        first = validator.validate(self.root)
        self.assertEqual(first, validator.validate(self.root))
        self.assertEqual(before, {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob('*.json')})


if __name__ == '__main__':
    unittest.main()
