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


if __name__ == '__main__':
    unittest.main()
