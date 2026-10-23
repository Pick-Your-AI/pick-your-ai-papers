"""Offline regression tests for destructive/misleading setup failure modes."""
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from github_support import (BudgetStop, GitHub, SetupError, connection_nodes, issue_index, render_issue)
from bootstrap_github import ensure_items, ensure_relationships, select_project
from verify_github import field_problems, view_problems, ruleset_matches, issue_body_problems


def record():
    return {"id": "PAPER-01.01", "parent": "PAPER-01", "record_type": "Work Package",
            "title": "A scoped outcome", "outcome": "A reviewable decision", "status": "Backlog",
            "tasks": [{"id": "PAPER-01.01.T1", "title": "Read evidence", "subtasks": [{"id": "PAPER-01.01.T1.S1", "title": "Pin source"}]}],
            "blocked_by": []}


class FakeClient:
    def __init__(self):
        self.mutations = []
    def mutate(self, *args):
        self.mutations.append(args)
        return {"projectV2Item": {"id": "item-real"}}


class BootstrapTests(unittest.TestCase):
    def test_native_children_are_not_duplicated_as_checklists(self):
        example = record()
        example["work_packages"] = [{"id": "PAPER-01.02", "title": "Native child"}]
        body = render_issue(example)
        self.assertIn("<!-- pick-your-ai-papers:PAPER-01.01 -->", body)
        self.assertIn("- [ ] `PAPER-01.01.T1`", body)
        self.assertIn("  - [ ] `PAPER-01.01.T1.S1`", body)
        self.assertNotIn("- [ ] `PAPER-01.02`", body)

    def test_duplicate_remote_identity_stops_publication(self):
        issue = {"number": 1, "body": "<!-- pick-your-ai-papers:PAPER-01 -->"}
        with self.assertRaisesRegex(SetupError, "Duplicate"):
            issue_index([issue, {**issue, "number": 2}])

    def test_ambiguous_markers_rejected(self):
        with self.assertRaisesRegex(SetupError, "ambiguous"):
            issue_index([{"number": 1, "body": "<!-- pick-your-ai-papers:PAPER-01 -->\n<!-- pick-your-ai-papers:PAPER-02 -->"}])

    def test_pull_request_does_not_masquerade_as_planning_issue(self):
        self.assertEqual(issue_index([{"number": 1, "body": "<!-- pick-your-ai-papers:PAPER-01 -->", "pull_request": {}}]), {})

    def test_equivalent_linked_project_reused(self):
        project = {"title": "Different title", "repositories": {"nodes": [{"nameWithOwner": "Pick-Your-AI/pick-your-ai-papers"}], "pageInfo": {"hasNextPage": False}}}
        self.assertIs(select_project([project], "Target title"), project)

    def test_ambiguous_projects_rejected(self):
        project = {"title": "Target", "repositories": {"nodes": [], "pageInfo": {"hasNextPage": False}}}
        with self.assertRaisesRegex(SetupError, "Multiple"):
            select_project([project, copy.deepcopy(project)], "Target")

    def test_archived_memberships_are_inventoried(self):
        class Pages:
            def graphql(self, query, variables):
                self.query = query
                return {"node": {"items": {"nodes": [], "pageInfo": {"hasNextPage": False}}}}
        client = Pages()
        connection_nodes(client, "project", "items", "id")
        self.assertIn("archivedStates:[ARCHIVED,NOT_ARCHIVED]", client.query)

    def test_existing_status_is_never_reset(self):
        client = FakeClient()
        item = {"id": "item-real", "content": {"id": "issue-real"}, "isArchived": False,
                "fieldValues": {"nodes": [{"name": "In Progress", "field": {"name": "Status"}}], "pageInfo": {"hasNextPage": False}}}
        scope = {"program": {"id": "PAPER", "status": "Backlog"}, "epics": []}
        with patch("bootstrap_github.fetch_items", return_value=[item]):
            ensure_items(client, {"id": "project-real"}, {"fields": [{"name": "Status", "record_key": "status", "data_type": "SINGLE_SELECT"}]}, scope,
                         {"PAPER": {"node_id": "issue-real"}}, {"Status": {"id": "field-real", "options": [{"name": "Backlog", "id": "option-real"}]}})
        self.assertEqual(client.mutations, [])

    def test_archived_membership_not_silently_reactivated(self):
        client = FakeClient()
        scope = {"program": {"id": "PAPER", "status": "Backlog"}, "epics": []}
        item = {"id": "item-real", "content": {"id": "issue-real"}, "isArchived": True}
        with patch("bootstrap_github.fetch_items", return_value=[item]):
            with self.assertRaisesRegex(SetupError, "archived"):
                ensure_items(client, {"id": "project-real"}, {"fields": []}, scope, {"PAPER": {"node_id": "issue-real"}}, {})
        self.assertEqual(client.mutations, [])

    def test_conflicting_parent_is_not_replaced(self):
        class Client:
            def api(self, endpoint, *args, **kwargs):
                self.last_endpoint = endpoint
                if args or kwargs:
                    raise AssertionError("No mutation should occur")
                return {"id": 5090, "number": 509}
            def optional(self, endpoint):
                return {"id": 9999, "number": 99}
        with self.assertRaisesRegex(SetupError, "Conflicting native parent"):
            ensure_relationships(Client(), {"program": {"id": "PAPER", "blocked_by": []}, "epics": []}, {"PAPER": {"id": 100, "number": 1}})

    def test_read_only_mode_rejects_mutations(self):
        with patch("github_support.shutil.which", return_value="gh"):
            client = GitHub()
        with self.assertRaisesRegex(SetupError, "read-only"):
            client.before_write()

    def test_rolling_budget_survives_restart(self):
        with tempfile.TemporaryDirectory() as folder, patch("github_support.shutil.which", return_value="gh"), patch("github_support.time.time", return_value=10000):
            path = Path(folder) / "state.json"
            client = GitHub(path, apply=True)
            client.state["write_times"] = [9999] * 400
            client.checkpoint()
            resumed = GitHub(path, apply=True)
            with self.assertRaises(BudgetStop):
                resumed.before_write()

    def test_incorrect_option_readback_is_not_accepted(self):
        expected = {"data_type": "SINGLE_SELECT", "options": ["Backlog", "Done"]}
        actual = {"dataType": "SINGLE_SELECT", "options": [{"name": "Todo"}, {"name": "Done"}]}
        self.assertIn("options", field_problems(expected, actual))

    def test_view_names_alone_are_insufficient(self):
        expected = {"layout": "table", "filter": "no:assignee", "visible_fields": ["Title"], "group_by": [], "vertical_group_by": [], "sort_by": []}
        connection = {"nodes": [], "pageInfo": {"hasNextPage": False}}
        actual = {"layout": "TABLE_LAYOUT", "filter": "", "fields": {"nodes": [{"name": "Title"}], "pageInfo": {"hasNextPage": False}}, "groupByFields": connection, "verticalGroupByFields": connection, "sortByFields": connection}
        self.assertIn("filter", view_problems(expected, actual))

    def test_boundary_bypass_readback_rejects_extra_actor(self):
        wanted = {"name": "Contributor boundary: branches", "target": "branch", "enforcement": "active", "conditions": {}, "rules": [], "bypass_actors": []}
        actual = {**wanted, "bypass_actors": [{"actor_id": 12, "actor_type": "Team", "bypass_mode": "always"}]}
        self.assertTrue(ruleset_matches(wanted, actual, 12))
        actual["bypass_actors"].append({"actor_id": 99, "actor_type": "Team", "bypass_mode": "always"})
        self.assertFalse(ruleset_matches(wanted, actual, 12))

    def test_review_rule_rejects_team_bypass(self):
        wanted = {"name": "Review required: default branch", "target": "branch", "enforcement": "active", "conditions": {}, "rules": [], "bypass_actors": []}
        actual = {**wanted, "bypass_actors": [{"actor_id": 12, "actor_type": "Team", "bypass_mode": "always"}]}
        self.assertFalse(ruleset_matches(wanted, actual, 12))

    def test_body_acceptance_cannot_be_removed_behind_unchanged_marker(self):
        wanted = record()
        wanted["acceptance_criteria"] = ["A source-linked result must exist."]
        body = render_issue(wanted).replace("- A source-linked result must exist.\n", "")
        self.assertIn("missing or changed content: ## Acceptance criteria", issue_body_problems(wanted, body))

    def test_body_checklist_progress_and_additional_notes_are_preserved(self):
        wanted = record()
        body = render_issue(wanted).replace("- [ ]", "- [x]") + "\n## Execution notes\n\nA dated update.\n"
        self.assertEqual(issue_body_problems(wanted, body), [])

    def test_task_id_in_prose_does_not_count_as_checklist(self):
        wanted = record()
        body = render_issue(wanted).replace("- [ ] `PAPER-01.01.T1`", "Task ID `PAPER-01.01.T1`")
        self.assertIn("missing or changed content: ## Tasks and subtasks", issue_body_problems(wanted, body))


if __name__ == "__main__":
    unittest.main()
