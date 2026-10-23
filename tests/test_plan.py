from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import validate_plan as plan
import render_docs


class PlanningIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline=plan.load_bundle(ROOT)

    def setUp(self):
        self.bundle=copy.deepcopy(self.baseline)
        self.package=self.bundle['backlog']['epics'][0]['work_packages'][0]

    def rejects(self,text):
        errors=plan.validate_bundle(self.bundle,ROOT)
        self.assertTrue(errors,'Invalid planning input unexpectedly accepted')
        self.assertTrue(any(text in e for e in errors),errors[:12])

    def test_complete_baseline_passes(self):
        self.assertEqual([],plan.validate_bundle(self.bundle,ROOT))
        self.assertEqual(165,plan.count_backlog(self.bundle['backlog'])['native_issue_records'])

    def test_schema_rejects_unknown_record_field(self):
        self.package['fabricated_permission']=True
        self.rejects('unexpected field')

    def test_schema_rejects_boolean_count(self):
        self.bundle['backlog']['counts']['programs']=True
        self.rejects('expected integer')

    def test_schema_rejects_nonboolean_completion(self):
        self.package['tasks'][0]['done']='false'
        self.rejects('expected boolean')

    def test_duplicate_subtask_id_is_rejected(self):
        tasks=self.package['tasks']
        tasks[1]['subtasks'][0]['id']=tasks[0]['subtasks'][0]['id']
        self.rejects('Duplicate stable ID')

    def test_wrong_native_parent_is_rejected(self):
        self.package['parent']='PAPER-02'
        self.rejects('invalid work-package identity or parent')

    def test_cross_package_task_id_is_rejected(self):
        self.package['tasks'][0]['id']='PAPER-02.01.T99'
        self.rejects('wrong task owner')

    def test_required_user_scope_cannot_disappear(self):
        self.package['title']='Generic scope placeholder'
        self.rejects('Required supplied Epic 01')

    def test_unknown_dependency_is_rejected(self):
        self.package['blocked_by']=['PAPER-99.99']
        self.rejects('unknown prerequisite')

    def test_dependency_cycle_is_rejected(self):
        # 01.03 already depends on 01.01. Adding the reverse edge is a real cycle.
        self.package['blocked_by']=['PAPER-01.03']
        self.package['dependency_status']='Prerequisites Open'
        self.bundle['backlog']['counts']=plan.count_backlog(self.bundle['backlog'])
        self.rejects('Dependency cycle')

    def test_self_dependency_is_rejected(self):
        self.package['blocked_by']=[self.package['id']]
        self.rejects('self prerequisite')

    def test_ready_without_accepted_owner_is_rejected(self):
        self.package['readiness']='Ready'
        self.rejects('Ready requires accepted native assignment')

    def test_work_status_cannot_be_scholarly_status(self):
        self.package['publication_status']='Published'
        self.rejects('planning records require publication_status Not Applicable')

    def test_done_without_acceptance_is_rejected(self):
        self.package['status']='Done'
        self.rejects('Done requires accepted scope')

    def test_completed_task_requires_its_subtasks(self):
        self.package['tasks'][0]['done']=True
        self.rejects('completed task has unfinished subtasks')

    def test_future_deliverable_does_not_have_to_exist_yet(self):
        self.package['deliverables'][0]='research/future/explicitly-planned-output.md'
        self.assertEqual([],plan.validate_bundle(self.bundle,ROOT))

    def test_path_traversal_is_rejected(self):
        self.package['deliverables'][0]='../private-record.json'
        self.rejects('unsafe deliverable path')

    def test_symlink_escape_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            shutil.copytree(ROOT/'schemas',root/'schemas')
            (root/'research').symlink_to('/tmp',target_is_directory=True)
            errors=plan.validate_bundle(self.bundle,root)
            self.assertTrue(any('symlink' in e for e in errors))

    def test_secret_url_query_is_rejected(self):
        self.package['references'][0]['url']='https://example.org/work?access_token=not-a-real-token'
        self.rejects('public HTTPS URL without credentials')

    def test_url_trailing_newline_is_rejected(self):
        self.package['references'][0]['url']='https://example.org/work\n'
        self.rejects('public HTTPS URL without credentials')

    def test_coverage_cannot_reference_missing_package(self):
        self.bundle['coverage']['entries'][0]['work_packages'].append('PAPER-99.99')
        self.rejects('unknown mapped package')

    def test_every_package_requires_coverage_mapping(self):
        for row in self.bundle['coverage']['entries']:
            row['work_packages']=[wid for wid in row['work_packages'] if wid!='PAPER-19.07']
        self.rejects('Coverage must map every planned package')

    def test_unmeasured_literature_denominator_cannot_be_zero(self):
        row=next(x for x in self.bundle['coverage']['entries'] if x['dimension']=='Research Domain')
        row['denominator']['size']=0
        self.rejects('unmeasured literature denominator must remain null')

    def test_known_workstream_scope_reconciles(self):
        self.bundle['coverage']['entries'][0]['denominator']['size']=999
        self.rejects('workstream denominator must match known planning scope')

    def test_global_denominator_is_not_invented(self):
        self.bundle['coverage']['summary']['global_denominator']=1000000
        self.rejects('global scientific-literature denominator')

    def test_release_reference_must_exist(self):
        self.bundle['release']['phases'][0]['required_packages'].append('PAPER-99.99')
        self.rejects('Release references unknown package')

    def test_release_phase_consistency(self):
        self.bundle['backlog']['epics'][19]['work_packages'][0]['release_phase']='Maintained Index'
        self.rejects('release acceptance package has wrong phase')

    def test_missing_scope_inference_decision_is_rejected(self):
        self.bundle['decisions']['decisions']=self.bundle['decisions']['decisions'][1:]
        self.rejects('incomplete supplied epic list')

    def test_release_acceptance_cannot_have_no_receipt(self):
        self.bundle['release']['accepted_release']='test-only-not-an-actual-release'
        self.rejects('Accepted release requires')

    def test_local_rendering_is_deterministic(self):
        first=render_docs.render(self.bundle,{})
        self.assertEqual(first,render_docs.render(self.bundle,{}))
        self.assertIn('144 independently reviewable work packages',first['docs/DELIVERY_PLAN.md'])
        self.assertIn('PAPER-20.07.T3.S2',first['docs/BACKLOG.md'])

    def test_unverified_receipt_cannot_create_published_link(self):
        receipt={'live_readback':{'verified':False},'issues':{'PAPER':{'url':'https://github.com/Pick-Your-AI/pick-your-ai-papers/issues/1'}}}
        self.assertIsNone(render_docs.published_url('PAPER',receipt))

    def test_verified_receipt_still_restricts_issue_destination(self):
        receipt={'live_readback':{'verified':True},'issues':{'PAPER':{'url':'https://example.org/not-a-github-issue'}}}
        self.assertIsNone(render_docs.published_url('PAPER',receipt))

    def test_verified_exact_issue_link_is_used(self):
        url='https://github.com/Pick-Your-AI/pick-your-ai-papers/issues/17'
        receipt={'live_readback':{'verified':True},'issues':{'PAPER':{'url':url}}}
        self.assertEqual(url,render_docs.published_url('PAPER',receipt))

    def test_document_drift_fails_cli_check(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            shutil.copytree(ROOT/'planning',root/'planning')
            shutil.copytree(ROOT/'schemas',root/'schemas')
            (root/'docs').mkdir()
            files=render_docs.render_files(root)
            for relative,content in files.items():
                (root/relative).write_text(content,encoding='utf-8')
            command=[sys.executable,str(ROOT/'scripts/render_docs.py'),'--root',str(root),'--check']
            clean=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(0,clean.returncode,clean.stderr)
            (root/'docs/DELIVERY_PLAN.md').write_text('stale content\n',encoding='utf-8')
            stale=subprocess.run(command,capture_output=True,text=True)
            self.assertEqual(1,stale.returncode)
            self.assertIn('Generated documentation is stale',stale.stderr)


if __name__=='__main__':
    unittest.main()
