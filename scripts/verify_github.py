#!/usr/bin/env python3
"""Read actual GitHub state without mutating repositories, issues or Projects."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from github_support import (FIELD_FRAGMENT, FULL_NAME, ORG, PARENT_NUMBER, PARENT_REPO,
    VIEW_FRAGMENT, GitHub, SetupError, connection_nodes, fetch_items, field_values,
    digest, issue_index, read_json, records, render_issue, timestamp, write_json)


def view_problems(wanted, actual):
    problems = []
    if actual.get("layout", "").lower().removesuffix("_layout") != wanted["layout"]:
        problems.append("layout")
    if (actual.get("filter") or "").strip() != wanted["filter"].strip():
        problems.append("filter")
    for desired_key, live_key in [("visible_fields", "fields"), ("group_by", "groupByFields"),
                                  ("vertical_group_by", "verticalGroupByFields")]:
        connection = actual[live_key]
        if connection["pageInfo"]["hasNextPage"]:
            problems.append(f"{desired_key}:partial-read")
        if [node["name"] for node in connection["nodes"]] != wanted.get(desired_key, []):
            problems.append(desired_key)
    connection = actual["sortByFields"]
    if connection["pageInfo"]["hasNextPage"]:
        problems.append("sort_by:partial-read")
    observed = [[node["field"]["name"], node["direction"].lower()] for node in connection["nodes"]]
    if observed != wanted.get("sort_by", []):
        problems.append("sort_by")
    return problems


def field_problems(wanted, actual):
    if not actual:
        return ["missing"]
    problems = []
    if actual["dataType"] != wanted["data_type"]:
        problems.append("data-type")
    if wanted["data_type"] == "SINGLE_SELECT":
        observed = [option["name"] for option in actual.get("options", [])]
        if len(observed) != len(set(observed)):
            problems.append("duplicate-options")
        if set(observed) != set(wanted["options"]):
            problems.append("options")
    return problems


def ruleset_matches(expected, actual, lead_team_id):
    """Compare all controls, including boundary bypasses, without weakening them."""
    if not all(actual.get(key) == expected[key] for key in ("target", "enforcement", "conditions", "rules")):
        return False
    bypasses = list(expected["bypass_actors"])
    if expected["name"].startswith("Contributor boundary:"):
        if lead_team_id is None:
            return False
        bypasses.append({"actor_id": lead_team_id, "actor_type": "Team", "bypass_mode": "always"})
    def normalized(rows):
        return sorted(json.dumps(row, sort_keys=True) for row in rows)
    return normalized(actual.get("bypass_actors", [])) == normalized(bypasses)


def issue_body_problems(record, actual_body):
    """Require baseline content in its proper sections, preserving live notes/checks."""
    def sections(body):
        result, duplicates, heading = {"preamble": []}, set(), "preamble"
        for raw in body.splitlines():
            line = raw.rstrip()
            if line.startswith("## "):
                heading = line
                if heading in result:
                    duplicates.add(heading)
                result.setdefault(heading, [])
            elif line:
                # Checking off a real task is legitimate live progress; IDs in
                # ordinary prose are not substitutes for structured checklists.
                line = re.sub(r"^(\s*- \[)[xX](\] `PAPER-\d{2}\.\d{2}\.T\d+(?:\.S\d+)?` .*)$", r"\1 \2", line)
                result[heading].append(line)
        return result, duplicates
    expected, _ = sections(render_issue(record))
    observed, duplicates = sections(actual_body or "")
    problems = []
    for heading, required_lines in expected.items():
        if heading in duplicates:
            problems.append(f"duplicate section: {heading}")
            continue
        remaining = iter(observed.get(heading, []))
        if any(not any(candidate == required for candidate in remaining) for required in required_lines):
            problems.append(f"missing or changed content: {heading}")
    return problems


def audit_live(client, root, project_number):
    root = Path(root)
    backlog = read_json(root / "planning/project-backlog.json")
    spec = read_json(root / "planning/project-spec.json")
    repository = client.api(f"repos/{FULL_NAME}")
    project = client.graphql("""query($org:String!,$number:Int!){organization(login:$org){
        projectV2(number:$number){id number title url public closed shortDescription
        repositories(first:100){nodes{nameWithOwner}pageInfo{hasNextPage}}
        teams(first:100){nodes{name slug}pageInfo{hasNextPage}}}}}""", {"org": ORG, "number": project_number})["organization"]["projectV2"]
    if not project:
        raise SetupError("Requested Project is missing or inaccessible; no verification claimed")
    problems, pending = [], []
    if repository["private"]:
        problems.append("Repository visibility is not public")
    if repository.get("archived") or repository.get("disabled"):
        problems.append("Repository is archived or disabled")
    if repository.get("description") != spec["repository_description"]:
        problems.append("Repository description differs from the intended scholarly scope")
    topics = client.api(f"repos/{FULL_NAME}/topics").get("names", [])
    if not set(spec["repository_topics"]).issubset(topics):
        problems.append("Repository topic metadata is incomplete")
    if project["title"] != spec["title"] or project["shortDescription"] != spec["description"]:
        problems.append("Project title/description differ from the requested baseline")
    if not project["public"] or project["closed"]:
        problems.append("Project visibility/state differ from the intended public open Project")
    if project["repositories"]["pageInfo"]["hasNextPage"] or not any(row["nameWithOwner"] == FULL_NAME for row in project["repositories"]["nodes"]):
        problems.append("Repository membership in Project is missing or incompletely read")
    if project["teams"]["pageInfo"]["hasNextPage"]:
        problems.append("Project team links were only partially read")
    fields = connection_nodes(client, project["id"], "fields", FIELD_FRAGMENT)
    field_map = {field["name"]: field for field in fields}
    if len(field_map) != len(fields):
        problems.append("Project contains duplicate field names")
    fields_ok = True
    for desired in spec["fields"]:
        mismatch = field_problems(desired, field_map.get(desired["name"]))
        if mismatch:
            fields_ok = False
            problems.append(f"Field {desired['name']}: {', '.join(mismatch)}")
    views = connection_nodes(client, project["id"], "views", VIEW_FRAGMENT)
    view_map = {view["name"]: view for view in views}
    if len(view_map) != len(views):
        problems.append("Project contains duplicate saved-view names")
    views_ok = True
    for desired in spec["views"]:
        actual = view_map.get(desired["name"])
        mismatch = view_problems(desired, actual) if actual else ["missing"]
        if mismatch:
            views_ok = False
            problems.append(f"View {desired['name']}: {', '.join(mismatch)}")
    index = issue_index(client.api(f"repos/{FULL_NAME}/issues?state=all&per_page=100", paginate=True))
    items = fetch_items(client, project["id"])
    item_map = {}
    for item in items:
        content = item.get("content")
        if content:
            if content["id"] in item_map:
                problems.append(f"Duplicate Project membership for {content['url']}")
            item_map[content["id"]] = item
    parent_audit = client.api(f"repos/{ORG}/{PARENT_REPO}/issues/{PARENT_NUMBER}")
    issue_receipt, parents, blockers = {}, [], []
    membership_ok = True
    for record in records(backlog):
        issue = index.get(record["id"])
        if not issue:
            problems.append(f"Missing issue {record['id']}")
            membership_ok = False
            continue
        issue_receipt[record["id"]] = {"id": issue["id"], "node_id": issue["node_id"],
            "number": issue["number"], "url": issue["html_url"], "state": issue["state"],
            "assignees": [user["login"] for user in issue["assignees"]]}
        if f"<!-- scope-sha256:{digest(record)} -->" not in (issue.get("body") or ""):
            problems.append(f"Planning scope signature differs or is missing: {record['id']}; review without overwriting live work")
        for mismatch in issue_body_problems(record, issue.get("body")):
            problems.append(f"Issue body {record['id']}: {mismatch}; preserve and review live changes")
        for task in record.get("tasks", []):
            for subrecord in [task] + task.get("subtasks", []):
                if f"`{subrecord['id']}`" not in (issue.get("body") or ""):
                    problems.append(f"Missing checklist ID {subrecord['id']} in {record['id']}")
        expected_parent = index.get(record.get("parent")) if record.get("parent") else parent_audit
        parent = client.optional(f"repos/{FULL_NAME}/issues/{issue['number']}/parent")
        correct = bool(expected_parent and parent and parent["id"] == expected_parent["id"])
        parents.append({"child": record["id"], "expected_parent": record.get("parent") or parent_audit["html_url"],
                        "actual_parent_url": parent["html_url"] if parent else None, "matches": correct})
        if not correct:
            problems.append(f"Native parent mismatch: {record['id']}")
        actual_blockers = client.api(f"repos/{FULL_NAME}/issues/{issue['number']}/dependencies/blocked_by?per_page=100", paginate=True)
        issue_receipt[record["id"]]["actual_blockers"] = [{"id": row["id"], "url": row["html_url"], "state": row["state"]} for row in actual_blockers]
        ids = {row["id"] for row in actual_blockers}
        for prerequisite in record.get("blocked_by", []):
            match = prerequisite in index and index[prerequisite]["id"] in ids
            blockers.append({"issue": record["id"], "blocked_by": prerequisite, "matches": match})
            if not match:
                problems.append(f"Missing native blocker: {record['id']} <- {prerequisite}")
        item = item_map.get(issue["node_id"])
        if not item or item["isArchived"]:
            membership_ok = False
            problems.append(f"Missing active Project membership: {record['id']}")
            continue
        values = field_values(item)
        issue_receipt[record["id"]]["project_item_id"] = item["id"]
        issue_receipt[record["id"]]["project_fields"] = values
        for field in spec["fields"]:
            value = values.get(field["name"])
            if value is None or value == "":
                membership_ok = False
                problems.append(f"Missing {field['name']} on {record['id']}")
            elif field["data_type"] == "SINGLE_SELECT" and value not in field["options"]:
                problems.append(f"Unrecognized {field['name']} on {record['id']}")
        # Execution status may legitimately move; the hierarchy classification must stay accurate.
        if values.get("Record Type") != record["record_type"]:
            problems.append(f"Record Type disagrees with native hierarchy: {record['id']}")
        if values.get("Publication Status") != "Not Applicable":
            problems.append(f"Planning record has a scholarly publication status: {record['id']}")
    teams = client.api(f"repos/{FULL_NAME}/teams?per_page=100", paginate=True)
    team_map = {team["name"]: team for team in teams}
    teams_ok = True
    for name, permission in [("Maintainers", "triage"), ("Research", "triage"), ("Research Lead Maintainers", "admin")]:
        if team_map.get(name, {}).get("permission") != permission:
            teams_ok = False
            problems.append(f"Repository team access not verified: {name}/{permission}")
    rules = client.api(f"repos/{FULL_NAME}/rulesets?includes_parents=true&per_page=100", paginate=True)
    rule_map = {rule["name"]: rule for rule in rules}
    if len(rule_map) != len(rules):
        problems.append("Duplicate ruleset names require inspection")
    rules_ok, rule_receipt = True, []
    for expected in read_json(root / "planning/ruleset-spec.json")["rulesets"]:
        summary = rule_map.get(expected["name"])
        if not summary:
            problems.append(f"Missing ruleset: {expected['name']}")
            rules_ok = False
            continue
        actual = client.api(f"repos/{FULL_NAME}/rulesets/{summary['id']}")
        match = ruleset_matches(expected, actual, team_map.get("Research Lead Maintainers", {}).get("id"))
        rule_receipt.append({"name": actual["name"], "id": actual["id"], "matches_baseline": match})
        if not match:
            problems.append(f"Ruleset differs from inspected policy: {expected['name']}")
            rules_ok = False
    default = repository["default_branch"]
    head = client.api(f"repos/{FULL_NAME}/git/ref/heads/{default}")["object"]["sha"]
    # Verify every deliverable blob at the immutable default-branch tree, not just a README.
    tree = client.api(f"repos/{FULL_NAME}/git/trees/{head}?recursive=1")
    default_ready = not tree.get("truncated", False)
    remote_blobs = {row["path"]: row["sha"] for row in tree.get("tree", []) if row["type"] == "blob"}
    from bootstrap_github import scaffold_entries
    missing_files = []
    for entry in scaffold_entries(root):
        if entry["path"] == "planning/github-receipt.json":  # A dated observation, refreshed independently.
            continue
        content = entry["content"].encode("utf-8")
        blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
        if remote_blobs.get(entry["path"]) != blob:
            missing_files.append(entry["path"])
    if missing_files:
        default_ready = False
    if not default_ready:
        pending.append("Scaffold file blobs have not been verified on the actual default branch")
    pending.append("Read back the actual merged scaffold PR, latest reviewed push, independent approval and merge evidence; matching default-branch files alone do not establish approval")
    runs = client.api(f"repos/{FULL_NAME}/actions/runs?head_sha={head}&per_page=100").get("workflow_runs", [])
    matching = [run for run in runs if run.get("head_sha") == head and run.get("path") == ".github/workflows/ci.yml"]
    latest = max(matching, key=lambda run: (run.get("run_number", 0), run.get("run_attempt", 0))) if matching else None
    ci_ok = bool(latest and latest["status"] == "completed" and latest["conclusion"] == "success")
    if not ci_ok:
        pending.append("Successful CI for the exact default-branch head has not been verified")
    # Project team links are inspectable through GraphQL; administrative roles require an additional UI readback.
    pending.append("Read back Project collaborator roles in GitHub settings and record the approved team access")
    return {"schema_version": "0.1.0", "checked_at": timestamp(), "target_repository": FULL_NAME,
        "status": "verified" if not problems and not pending else "partially_configured",
        "repository": {"id": repository["id"], "url": repository["html_url"], "visibility": "private" if repository["private"] else "public", "default_branch": default, "head_sha": head, "description": repository.get("description"), "topics": topics},
        "project": project, "fields": fields, "views": views, "issues": issue_receipt,
        "native_relationships": parents, "dependencies": blockers,
        "repository_teams": [{"id": team["id"], "name": team["name"], "slug": team["slug"], "permission": team["permission"]} for team in teams],
        "rulesets": rule_receipt, "default_branch_missing_or_different_files": missing_files,
        "latest_default_branch_ci": {key: latest[key] for key in ("id", "html_url", "head_sha", "status", "conclusion")} if latest else None,
        "live_readback": {"verified": not problems and not pending, "fields": fields_ok,
            "memberships": membership_ok, "views": views_ok, "repository_teams": teams_ok,
            "rules": rules_ok, "default_branch_scaffold": default_ready, "ci": ci_ok,
            "independent_pull_request_approval": False,
            "native_relationships": all(row["matches"] for row in parents) and len(parents) == len(list(records(backlog))),
            "project_collaborator_roles": False},
        "problems": problems, "acceptance_pending": pending,
        "scientific_catalog": {"assessed_by_this_script": False, "scope": "GitHub configuration readback only; run research and release gates separately"}}


def discover_project_number(client, title):
    after, matches = None, []
    while True:
        page = client.graphql("""query($org:String!,$after:String){organization(login:$org){projectsV2(first:100,after:$after){
          nodes{number title}pageInfo{hasNextPage endCursor}}}}""", {"org": ORG, "after": after})["organization"]["projectsV2"]
        matches.extend(project["number"] for project in page["nodes"] if project["title"] == title)
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    if len(matches) != 1:
        raise SetupError("Exactly one matching organization Project must exist; no Project number is guessed")
    return matches[0]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--project-number", type=int)
    parser.add_argument("--output", type=Path, help="Optional local receipt path; GitHub remains read-only")
    args = parser.parse_args(argv)
    client = GitHub()
    spec = read_json(args.root / "planning/project-spec.json")
    number = args.project_number or discover_project_number(client, spec["title"])
    receipt = audit_live(client, args.root, number)
    if args.output:
        write_json(args.output, receipt)
    print(json.dumps({"status": receipt["status"], "project": receipt["project"]["url"],
                      "issues_read": len(receipt["issues"]), "problems": receipt["problems"],
                      "acceptance_pending": receipt["acceptance_pending"]}, indent=2))
    return 0 if receipt["live_readback"]["verified"] else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (SetupError, OSError, subprocess.TimeoutExpired) as error:
        print(f"UNVERIFIED: {error}", file=sys.stderr)
        raise SystemExit(2)
