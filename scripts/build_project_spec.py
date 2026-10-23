#!/usr/bin/env python3
"""Deterministically derive a proposed Project configuration; no GitHub calls."""
import argparse
import json
from pathlib import Path
from github_support import FULL_NAME, records, read_json
from bootstrap_github import FIELD_NAMES


def build(backlog):
    scope = list(records(backlog))
    required = {
        "status": ["Backlog", "Ready", "In Progress", "In Review", "Blocked", "Done"],
        "priority": ["P0", "P1", "P2", "P3"],
        "record_type": ["Program", "Epic", "Work Package", "Task"],
        "readiness": ["Ready", "Needs Input", "Blocked", "Awaiting Decision"],
    }
    fields = []
    for name in FIELD_NAMES:
        key = name.lower().replace(" ", "_")
        values = required.get(key, list(backlog.get("options", {}).get(key, [])))
        values = list(values)
        for record in scope:
            value = record[key]
            value = "; ".join(value) if isinstance(value, list) else value
            if value not in values:
                values.append(value)
        fields.append({"name": name, "record_key": key, "data_type": "SINGLE_SELECT", "options": values})
    workstreams = {epic["id"]: epic["workstream"] for epic in backlog["epics"]}
    # PAPER-DEC-017: visible_fields follows ProjectV2View.fields enumeration.
    # Physical UI column order is recorded separately in the Project receipt.
    base = ["Title", "Assignees", "Status", "Priority", "Record Type"]
    progress = base[:3] + ["Sub-issues progress"] + base[3:]
    def view(name, filter_query, visible, group=None):
        return {"name": name, "layout": "table", "filter": filter_query,
                "visible_fields": visible, "group_by": [group] if group else [],
                "vertical_group_by": [], "sort_by": [["Priority", "asc"], ["Title", "asc"]]}
    discovery = workstreams["PAPER-02"].replace('"', '\\"')
    views = [
        view("Program Overview", "record-type:Program", progress + ["Release Phase", "Acceptance Status"]),
        view("Epic and Work-Package Hierarchy", 'record-type:Epic,"Work Package"', base[:3] + ["Parent issue", "Sub-issues progress"] + base[3:] + ["Readiness", "Workstream"], "Workstream"),
        view("Research Domains", "", base + ["Research Domain", "Publication Type", "Research Method"], "Research Domain"),
        view("Literature Discovery", f'workstream:"{discovery}"', base + ["Publication Type", "Source Rights Status", "Citation Verification"]),
        view("Evidence and Reproducibility", "", base + ["Research Method", "Evidence Confidence", "Reproducibility Status"], "Reproducibility Status"),
        view("Citation Verification", '-citation-verification:"Identity Verified"', base + ["Research Domain", "Publication Type", "Citation Verification"], "Citation Verification"),
        view("Rights and Publication Review", "", base + ["Source Rights Status", "Publication Status", "Acceptance Status"], "Source Rights Status"),
        view("High-Priority Work", "priority:P0,P1 -status:Done", base + ["Readiness", "Dependency Status", "Effort"]),
        view("Blocked Dependencies", 'dependency-status:"Prerequisites Open"', base[:3] + ["Parent issue"] + base[3:] + ["Readiness", "Dependency Status"], "Dependency Status"),
        view("Website Publication Readiness", 'release-phase:"Website Handoff"', base + ["Source Rights Status", "Citation Verification", "Publication Status", "Release Phase", "Acceptance Status"]),
        view("Unassigned Work", "no:assignee -status:Done", base + ["Readiness", "Workstream", "Effort"], "Workstream"),
    ]
    return {"schema_version": "0.1.0", "configuration_status": "proposed_not_applied",
        "repository": FULL_NAME, "title": "Pick Your AI — AI Papers & Research Index",
        "description": "Comprehensive AI academic literature discovery, scholarly metadata, research taxonomy, reproducibility, evidence, knowledge-graph relationships and website publication.",
        "repository_description": "Source-linked AI literature, methods, authors, labs, scholarly evidence and reproducibility planning for Pick Your AI.",
        "repository_topics": ["ai", "research", "papers", "scholarly-metadata", "reproducibility", "knowledge-graph"],
        "readme": "This Project tracks delivery of the scholarly index. Planning status is separate from a paper's scientific or publication status. Native Assignees and sub-issues are authoritative. A scaffold, metadata check or completed planning record does not establish scientific verification, publication permission or an operating search engine.",
        "number": None, "url": None, "visibility_for_new_project": "public",
        "native_fields": ["Title", "Assignees", "Parent issue", "Sub-issues progress"],
        "fields": fields, "views": views,
        "readback_requirements": ["Actual Project number and owner", "Field IDs and all options", "Active issue memberships and field values", "Native parents and blockers", "Saved view names, layout, filters, visible columns, grouping and sorting", "Repository team permissions and Project collaborator roles", "Default-branch scaffold and CI at its actual head"],
        "publication_status_semantics": "Scholarly publication state, separate from delivery Status and editorial Acceptance Status. Planning Program/Epic/Work Package records use Not Applicable; exact work-version publication facts remain in scholarly records.",
        "access_policy": {"individual_grants": [], "team_membership_changes": [], "assignee_policy": "Native Assignees only; leave unassigned until ownership is accepted", "new_repository_team_mapping": [{"current_team_name": "Maintainers", "permission": "triage"}, {"current_team_name": "Research", "permission": "triage"}, {"current_team_name": "Research Lead Maintainers", "permission": "admin"}], "condition": "Apply only after actual team identities/roles and current organizational policy are read. No team or individual identity is inferred from a slug."}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(build(read_json(args.root / "planning/project-backlog.json")), indent=2, ensure_ascii=False) + "\n"
    path = args.root / "planning/project-spec.json"
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            raise SystemExit("Project specification drift; run scripts/build_project_spec.py")
        print("Project specification is current; this is not a live configuration readback.")
    else:
        path.write_text(content, encoding="utf-8")
        print("Wrote proposed Project configuration (no remote mutation).")


if __name__ == "__main__":
    main()
