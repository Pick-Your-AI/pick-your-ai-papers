"""Regressions discovered during independent local review of scholarly intake.

All fabricated graph relations exist only in disposable test copies. They are
deliberately unsupported assertions, never source evidence or real notices.
"""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    'papers_research_independent_review', ROOT / 'scripts/validate_research.py')
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class SourceUrlReviewTests(unittest.TestCase):
    def test_parser_normalization_cannot_hide_raw_control_or_whitespace(self):
        for value in [
            'https://arxiv.org/ab\ns/1803.09010v8',
            'https://arxiv.org/ab\ts/1803.09010v8',
            ' https://arxiv.org/abs/1803.09010v8',
            'https://arxiv.org/abs/1803.09010v8 ',
        ]:
            with self.subTest(value=repr(value)):
                self.assertFalse(validator.public_url(value))

    def test_empty_user_information_is_still_credential_syntax(self):
        self.assertFalse(validator.public_url('https://@arxiv.org/abs/1803.09010v8'))

    def test_invalid_and_out_of_range_ports_are_rejected(self):
        for value in [
            'https://arxiv.org:bad/abs/1803.09010v8',
            'https://arxiv.org:99999/abs/1803.09010v8',
        ]:
            with self.subTest(value=value):
                self.assertFalse(validator.public_url(value))

    def test_legacy_numeric_loopback_is_not_a_public_publisher(self):
        self.assertFalse(validator.public_url('https://127.1/paper'))

    def test_valid_primary_source_urls_remain_eligible_shapes(self):
        for value in [
            'https://arxiv.org/abs/1803.09010v8',
            'https://arxiv.org:443/abs/1803.09010v8',
            'https://info.arxiv.org/help/license/index.html#metadata-license',
        ]:
            with self.subTest(value=value):
                self.assertTrue(validator.public_url(value))


class IntegrityGraphReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='papers-integrity-review-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in (*validator.MATERIAL_ROOTS, 'schemas'):
            shutil.copytree(ROOT / name, self.root / name)

    def test_metadata_check_cannot_assert_correction_withdrawal_or_retraction(self):
        path = self.root / 'research/graph.json'
        original = json.loads(path.read_text())
        self.assertEqual(validator.validate(self.root)[0], [])
        for predicate in ('corrects', 'withdraws', 'retracts'):
            with self.subTest(predicate=predicate):
                graph = json.loads(json.dumps(original))
                graph['edges'].append({
                    'id': 'edge.synthetic.unsupported-integrity',
                    'subject': 'paper.arxiv.1803.09010.v8',
                    'predicate': predicate,
                    'object': 'paper.arxiv.2104.08663.v4',
                    'source_refs': ['source.arxiv.1803.09010.v8'],
                    'locator': 'SYNTHETIC ordinary bibliographic metadata only',
                    'assertion_level': 'metadata_checked',
                    'check_ids': ['check.arxiv.1803.09010.v8'],
                    'review_ids': [],
                })
                path.write_text(json.dumps(graph, ensure_ascii=False, indent=2) + '\n')
                errors, _ = validator.validate(self.root)
                self.assertTrue(errors, 'An ordinary citation check admitted an unsupported integrity assertion')


class EdgeEvidenceBindingReviewTests(unittest.TestCase):
    """PR #166 review: a check must have observed the exact edge it supports.

    Every observed relation below is a SYNTHETIC test input in a disposable copy.
    None is a real citation observation or research evidence.
    """
    UNOBSERVED = 'directly observed its exact subject, predicate and object'

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='papers-edge-binding-review-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in (*validator.MATERIAL_ROOTS, 'schemas'):
            shutil.copytree(ROOT / name, self.root / name)
        errors, stats = validator.validate(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(stats['edges'], 8)

    def edit(self, rel, change):
        path = self.root / rel
        data = json.loads(path.read_text())
        change(data)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')

    def add_edge(self, subject, object_='paper.arxiv.2402.04249', predicate='cites',
                 check='check.arxiv.1803.09010.v8', source='source.arxiv.1803.09010.v8'):
        self.edit('research/graph.json', lambda g: g['edges'].append({
            'id': 'edge.synthetic.' + predicate,
            'subject': subject,
            'predicate': predicate,
            'object': object_,
            'source_refs': [source],
            'locator': 'SYNTHETIC test input; not a citation observation',
            'assertion_level': 'metadata_checked',
            'check_ids': [check],
            'review_ids': [],
        }))

    def observe(self, check_id, subject, object_='paper.arxiv.2402.04249', predicate='cites'):
        def change(evidence):
            check = next(c for c in evidence['checks'] if c['id'] == check_id)
            check.setdefault('observed_relations', []).append(
                {'subject': subject, 'predicate': predicate, 'object': object_})
        self.edit('evidence/research-evidence.json', change)

    def errors(self):
        return validator.validate(self.root)[0]

    def test_citation_cannot_borrow_a_check_of_an_unrelated_revision(self):
        self.add_edge('paper.arxiv.2104.08663.v4')
        self.assertTrue(any(self.UNOBSERVED in e for e in self.errors()))

    def test_same_revision_check_that_did_not_observe_the_citation_is_rejected(self):
        self.add_edge('paper.arxiv.1803.09010.v8')
        self.assertTrue(any(self.UNOBSERVED in e for e in self.errors()))

    def test_directly_observed_citation_is_accepted(self):
        self.observe('check.arxiv.1803.09010.v8', 'paper.arxiv.1803.09010.v8')
        self.add_edge('paper.arxiv.1803.09010.v8')
        errors, stats = validator.validate(self.root)
        self.assertEqual(errors, [])
        self.assertEqual(stats['edges'], 9)

    def test_observation_of_a_different_object_does_not_transfer(self):
        self.observe('check.arxiv.1803.09010.v8', 'paper.arxiv.1803.09010.v8', 'paper.arxiv.2405.09673')
        self.add_edge('paper.arxiv.1803.09010.v8')
        self.assertTrue(any(self.UNOBSERVED in e for e in self.errors()))

    def test_observed_citation_cannot_be_reused_by_another_subject(self):
        self.observe('check.arxiv.1803.09010.v8', 'paper.arxiv.1803.09010.v8')
        self.add_edge('paper.arxiv.2104.08663.v4')
        self.assertTrue(any(self.UNOBSERVED in e for e in self.errors()))

    def test_check_cannot_record_a_relation_for_another_revision(self):
        self.observe('check.arxiv.2104.08663.v4', 'paper.arxiv.1803.09010.v8')
        self.add_edge('paper.arxiv.1803.09010.v8', check='check.arxiv.2104.08663.v4',
                      source='source.arxiv.2104.08663.v4')
        errors = self.errors()
        self.assertIn('check.arxiv.2104.08663.v4: observed relation subject is outside the checked revision', errors)
        self.assertTrue(any(self.UNOBSERVED in e for e in errors))

    def test_checks_cannot_directly_observe_reviewed_or_identity_predicates(self):
        for predicate in ('supports', 'reproduces', 'retracts', 'has_revision'):
            with self.subTest(predicate=predicate):
                self.setUp()
                self.observe('check.arxiv.1803.09010.v8', 'paper.arxiv.1803.09010.v8', predicate=predicate)
                self.assertIn('check.arxiv.1803.09010.v8: check cannot directly observe relation predicate ' + predicate,
                              self.errors())

    def test_other_relationship_predicates_require_exact_observation(self):
        for predicate, object_ in [('authored_by', 'person.synthetic'), ('introduces_method', 'method.synthetic'),
                                   ('uses_dataset', 'dataset.synthetic'), ('releases_code', 'code.synthetic'),
                                   ('cites', 'paper.arxiv.2402.04249.v2')]:
            with self.subTest(predicate=predicate):
                self.setUp()
                self.add_edge('paper.arxiv.1803.09010.v8', object_, predicate)
                self.assertTrue(any(self.UNOBSERVED in e for e in self.errors()))

    def test_identity_edge_requires_its_identity_observation(self):
        for index, pointer in [(0, '/revision'), (1, '/manifestation')]:
            with self.subTest(pointer=pointer):
                self.setUp()
                def drop(evidence):
                    check = next(c for c in evidence['checks'] if c['id'] == 'check.arxiv.1803.09010.v8')
                    check['observations'].remove(pointer)
                self.edit('evidence/research-evidence.json', drop)
                edge_id = json.loads((self.root / 'research/graph.json').read_text())['edges'][index]['id']
                self.assertTrue(any(e.startswith(edge_id + ': identity edge check belongs to another revision')
                                    for e in self.errors()))


if __name__ == '__main__':
    unittest.main()
