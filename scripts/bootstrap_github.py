#!/usr/bin/env python3
"""Plan or apply resumable papers-repository setup through an authenticated gh client.

Default is entirely offline. --inspect is read-only. --apply never merges a PR,
changes a team membership, overwrites a live issue or resets populated Project
fields. See docs/PROJECT_SETUP.md for the remaining independent review gate.
"""
from __future__ import annotations

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path

from github_support import (API_VERSION, FIELD_FRAGMENT, FULL_NAME, ORG, PARENT_NUMBER,
    PARENT_REPO, REPO, VIEW_FRAGMENT, ApiError, BudgetStop, GitHub, SetupError,
    connection_nodes, digest, fetch_items, field_values, issue_index, project_query,
    read_json, records, render_issue, timestamp, write_json)

BRANCH = "contrib/papers-bootstrap/foundation"
POLICY_PATH = "repos/Pick-Your-AI/.github/contents/CONTRIBUTING.md"
POLICY_SHA = "18b247ac191ce57ae20b856c2b9374a6009c6854"
FIELD_NAMES = ["Status", "Priority", "Record Type", "Readiness", "Workstream", "Research Domain",
    "Publication Type", "Research Method", "Evidence Confidence", "Reproducibility Status",
    "Source Rights Status", "Citation Verification", "Publication Status", "Dependency Status",
    "Effort", "Release Phase", "Acceptance Status"]


def offline_plan(root):
    backlog = read_json(root / "planning/project-backlog.json")
    spec = read_json(root / "planning/project-spec.json")
    scope = list(records(backlog))
    return {"mode": "offline-plan", "remote_mutations": 0, "repository": FULL_NAME,
            "project_title": spec["title"], "project_number": None,
            "native_issues": len(scope), "native_parent_edges": len(scope),
            "internal_parent_edges": len(scope) - 1, "parent_audit_edges": 1,
            "internal_blocker_edges": sum(len(row.get("blocked_by", [])) for row in scope),
            "custom_and_status_fields": len(spec["fields"]), "saved_views": len(spec["views"]),
            "default_branch_delivery": "Pull request; independent approval and CI required",
            "scientific_publication": "No catalog release or reproduced results are created by setup"}


def validate_locally(root):
    for command in ([sys.executable, "scripts/validate_plan.py"],
                    [sys.executable, "scripts/validate_research.py"],
                    [sys.executable, "scripts/render_docs.py", "--check"],
                    [sys.executable, "scripts/build_project_spec.py", "--check"],
                    [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]):
        result = subprocess.run(command, cwd=root, check=False)
        if result.returncode:
            raise SetupError("Local validation failed; no GitHub changes attempted")


def inspect_organization(client):
    """Complete live preflight; this must run before creating repository/Project."""
    viewer = client.api("user")
    membership = client.api(f"user/memberships/orgs/{ORG}")
    if membership.get("state") != "active" or membership.get("role") != "admin":
        raise SetupError("Setup needs an existing authorized organization-admin session. It does not request broader token permissions or change membership.")
    policy = client.api(POLICY_PATH)
    if policy["sha"] != POLICY_SHA:
        raise SetupError("Organization contribution policy changed since the inspected baseline. Review it and update the recorded policy SHA before applying setup.")
    projects, after, org_id = [], None, None
    while True:
        result = client.graphql("""query($org:String!,$after:String){organization(login:$org){id
          projectsV2(first:100,after:$after){nodes{id number title url public closed
          repositories(first:100){nodes{nameWithOwner}pageInfo{hasNextPage}}}
          pageInfo{hasNextPage endCursor}}}}""", {"org": ORG, "after": after})["organization"]
        org_id = result["id"]
        page = result["projectsV2"]
        projects.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            break
        after = page["pageInfo"]["endCursor"]
    # The user requested inspection of these exact existing Projects.
    inspected = []
    for number in range(1, 8):
        found = [p for p in projects if p["number"] == number]
        if len(found) != 1:
            raise SetupError(f"Requested reference Project #{number} is not accessible; complete that read-only inspection before creating a replacement structure")
        project = found[0]
        fields = connection_nodes(client, project["id"], "fields", FIELD_FRAGMENT)
        views = connection_nodes(client, project["id"], "views", VIEW_FRAGMENT)
        inspected.append({"number": number, "public": project["public"],
                          "fields_inspected": len(fields), "views_inspected": len(views)})
    upstream_teams = client.api(f"repos/{ORG}/{PARENT_REPO}/teams?per_page=100", paginate=True)
    team_plan = []
    for name, permission in [("Maintainers", "triage"), ("Research", "triage"), ("Research Lead Maintainers", "admin")]:
        matches = [team for team in upstream_teams if team["name"] == name]
        if len(matches) != 1 or matches[0].get("permission") != permission:
            raise SetupError(f"Current research team policy is not the inspected {name}/{permission} mapping. Resolve the access decision without adding individual collaborators.")
        team = matches[0]
        team_plan.append({key: team[key] for key in ("id", "node_id", "name", "slug") } | {"permission": permission})
    return {"viewer": viewer["login"], "organization_id": org_id, "projects": projects,
            "reference_projects": inspected, "teams": team_plan,
            "repository": client.optional(f"repos/{FULL_NAME}")}


def select_project(projects, title):
    matches = []
    for project in projects:
        if project["repositories"]["pageInfo"]["hasNextPage"]:
            raise SetupError("An organization Project has more than 100 linked repositories; complete its inventory before selecting an equivalent Project")
        linked = any(r["nameWithOwner"] == FULL_NAME for r in project["repositories"]["nodes"])
        if project["title"] == title or linked:
            matches.append(project)
    if len(matches) > 1:
        raise SetupError("Multiple equivalent papers Projects exist; preserve them and reconcile the duplicate inventory before continuing")
    return matches[0] if matches else None


def ensure_repository(client, preflight, spec):
    repository = preflight["repository"]
    if repository:
        if repository["private"] or repository["archived"] or repository.get("disabled"):
            raise SetupError("Existing target is private, archived or disabled; setup will not expose or reactivate it")
        return repository
    repository = client.api(f"orgs/{ORG}/repos", "POST", {"name": REPO, "private": False,
        "description": spec["repository_description"], "auto_init": True,
        "has_issues": True, "has_wiki": False, "has_projects": True,
        "delete_branch_on_merge": True})
    client.state["created_repository_id"] = repository["id"]
    client.state["repository_metadata_initialized"] = False
    client.checkpoint()
    return repository


def ensure_teams_and_rules(client, preflight, root):
    existing = client.api(f"repos/{FULL_NAME}/teams?per_page=100", paginate=True)
    by_id = {team["id"]: team for team in existing}
    for team in preflight["teams"]:
        if team["id"] in by_id:
            if by_id[team["id"]].get("permission") != team["permission"]:
                raise SetupError(f"Existing team {team['name']} has a different repository role; preserving it for review")
        else:
            client.api(f"orgs/{ORG}/teams/{team['slug']}/repos/{FULL_NAME}", "PUT", {"permission": team["permission"]})
    rule_spec = read_json(root / "planning/ruleset-spec.json")
    current = client.api(f"repos/{FULL_NAME}/rulesets?includes_parents=true&per_page=100", paginate=True)
    by_name = {rule["name"]: rule for rule in current}
    lead = next(team for team in preflight["teams"] if team["name"] == "Research Lead Maintainers")
    for source in rule_spec["rulesets"]:
        # Never overwrite or remove an existing rule; verify it below and report drift.
        if source["name"] in by_name:
            continue
        desired = {key: source[key] for key in ("name", "target", "enforcement", "conditions", "rules", "bypass_actors")}
        desired = json.loads(json.dumps(desired))
        if source["name"].startswith("Contributor boundary:"):
            desired["bypass_actors"].append({"actor_id": lead["id"], "actor_type": "Team", "bypass_mode": "always"})
        client.api(f"repos/{FULL_NAME}/rulesets", "POST", desired)


def ensure_project(client, preflight, repository, spec):
    project = select_project(preflight["projects"], spec["title"])
    if project:
        if (project["id"] == client.state.get("created_project_id")
                and not client.state.get("project_public_initialization_complete")
                and not project["public"] and not project["closed"]):
            project = client.mutate("updateProjectV2", "UpdateProjectV2Input",
                {"projectId": project["id"], "public": True, "shortDescription": spec["description"], "readme": spec["readme"]},
                "projectV2{id number title url public closed}")["projectV2"]
        if not project["public"] or project["closed"]:
            raise SetupError("Equivalent Project is private or closed; setup will preserve its visibility/state and stop for a scoped decision")
        if project["title"] != spec["title"]:
            raise SetupError("An equivalent linked Project has a different title; preserve it and reconcile the desired Project identity first")
    else:
        project = client.mutate("createProjectV2", "CreateProjectV2Input",
            {"ownerId": preflight["organization_id"], "repositoryId": repository["node_id"], "title": spec["title"]},
            "projectV2{id number title url public closed}")["projectV2"]
        client.state["created_project_id"] = project["id"]
        client.state["project_public_initialization_complete"] = False
        client.state["project_fields_initialized"] = False
        client.state["project_team_access_requested"] = False
        client.checkpoint()
        project = client.mutate("updateProjectV2", "UpdateProjectV2Input",
            {"projectId": project["id"], "public": True, "shortDescription": spec["description"],
             "readme": spec["readme"]}, "projectV2{id number title url public closed}")["projectV2"]
    if project["id"] == client.state.get("created_project_id"):
        client.state["project_public_initialization_complete"] = True
        client.checkpoint()
    linked = project.get("repositories", {}).get("nodes", [])
    if not any(row.get("nameWithOwner") == FULL_NAME for row in linked):
        client.mutate("linkProjectV2ToRepository", "LinkProjectV2ToRepositoryInput",
                      {"projectId": project["id"], "repositoryId": repository["node_id"]}, "repository{id}")
    if project["id"] == client.state.get("created_project_id") and not client.state.get("project_team_access_requested"):
        lead = next(team for team in preflight["teams"] if team["name"] == "Research Lead Maintainers")
        client.mutate("linkProjectV2ToTeam", "LinkProjectV2ToTeamInput",
            {"projectId": project["id"], "teamId": lead["node_id"]}, "team{id}")
        client.mutate("updateProjectV2Collaborators", "UpdateProjectV2CollaboratorsInput",
            {"projectId": project["id"], "collaborators": [{"teamId": lead["node_id"], "role": "ADMIN"}]},
            "collaborators{totalCount}")
        client.state["project_team_access_requested"] = True
        client.checkpoint()
    return project


def ensure_fields(client, project, spec):
    fields = connection_nodes(client, project["id"], "fields", FIELD_FRAGMENT)
    by_name = {field["name"]: field for field in fields}
    if len(by_name) != len(fields):
        raise SetupError("Duplicate Project field names detected; no field mutations attempted")
    for wanted in spec["fields"]:
        old = by_name.get(wanted["name"])
        if old:
            if old["dataType"] != wanted["data_type"]:
                raise SetupError(f"Project field type conflict: {wanted['name']}")
            options = [dict(option) for option in old.get("options", [])]
            renamed = False
            if (wanted["name"] == "Status" and project["id"] == client.state.get("created_project_id")
                    and not client.state.get("project_fields_initialized")):
                for option in options:
                    corrected = {"Todo": "Backlog", "In progress": "In Progress"}.get(option["name"])
                    if corrected and corrected not in {entry["name"] for entry in options}:
                        option["name"] = corrected
                        renamed = True
            names = {option["name"] for option in options}
            missing = [name for name in wanted.get("options", []) if name not in names]
            if missing or renamed:
                # Preserve IDs for all existing options, including options outside the baseline.
                options += [{"name": name, "color": "GRAY", "description": name} for name in missing]
                client.mutate("updateProjectV2Field", "UpdateProjectV2FieldInput",
                    {"fieldId": old["id"], "singleSelectOptions": options}, "projectV2Field{... on ProjectV2FieldCommon{id}}")
        else:
            payload = {"projectId": project["id"], "name": wanted["name"], "dataType": wanted["data_type"]}
            if wanted.get("options"):
                payload["singleSelectOptions"] = [{"name": name, "color": "GRAY", "description": name} for name in wanted["options"]]
            client.mutate("createProjectV2Field", "CreateProjectV2FieldInput", payload,
                          "projectV2Field{... on ProjectV2FieldCommon{id}}")
    result = {field["name"]: field for field in connection_nodes(client, project["id"], "fields", FIELD_FRAGMENT)}
    if project["id"] == client.state.get("created_project_id"):
        client.state["project_fields_initialized"] = True
        client.checkpoint()
    return result


def ensure_views(client, project, spec, fields):
    existing = connection_nodes(client, project["id"], "views", VIEW_FRAGMENT)
    names = [view["name"] for view in existing]
    if len(names) != len(set(names)):
        raise SetupError("Duplicate saved-view names detected; no additional views created")
    for view in spec["views"]:
        if view["name"] in names:
            continue
        referenced = view["visible_fields"] + view.get("group_by", []) + view.get("vertical_group_by", []) + [item[0] for item in view.get("sort_by", [])]
        for name in referenced:
            if name not in fields or fields[name].get("databaseId") is None:
                raise SetupError(f"Native/Project field {name!r} is unavailable; do not substitute a fake text field")
        payload = {"name": view["name"], "layout": view["layout"], "filter": view["filter"],
            "visible_fields": [fields[name]["databaseId"] for name in view["visible_fields"]],
            "sort_by": [[fields[name]["databaseId"], direction] for name, direction in view.get("sort_by", [])],
            "group_by": [fields[name]["databaseId"] for name in view.get("group_by", [])],
            "vertical_group_by": [fields[name]["databaseId"] for name in view.get("vertical_group_by", [])]}
        client.api(f"orgs/{ORG}/projectsV2/{project['number']}/views", "POST", payload)


def ensure_issues(client, backlog):
    existing = issue_index(client.api(f"repos/{FULL_NAME}/issues?state=all&per_page=100", paginate=True))
    for record in records(backlog):
        if record["id"] in existing:
            continue
        issue = client.api(f"repos/{FULL_NAME}/issues", "POST", {
            "title": f"[{record['id']}] {record['title']}", "body": render_issue(record)})
        existing[record["id"]] = issue
        client.state.setdefault("issues", {})[record["id"]] = {key: issue[key] for key in ("id", "node_id", "number", "html_url")}
        client.checkpoint()
    return existing


def ensure_relationships(client, backlog, index):
    audit = client.api(f"repos/{ORG}/{PARENT_REPO}/issues/{PARENT_NUMBER}")
    for record in records(backlog):
        child = index[record["id"]]
        expected = index[record["parent"]] if record.get("parent") else audit
        parent = client.optional(f"repos/{FULL_NAME}/issues/{child['number']}/parent")
        if parent and parent["id"] != expected["id"]:
            raise SetupError(f"Conflicting native parent for {record['id']}; never reparent automatically")
        if not parent:
            parent_repo = FULL_NAME if record.get("parent") else f"{ORG}/{PARENT_REPO}"
            client.api(f"repos/{parent_repo}/issues/{expected['number']}/sub_issues", "POST", {"sub_issue_id": child["id"], "replace_parent": False})
        existing = client.api(f"repos/{FULL_NAME}/issues/{child['number']}/dependencies/blocked_by?per_page=100", paginate=True)
        ids = {row["id"] for row in existing}
        for blocker in record.get("blocked_by", []):
            if index[blocker]["id"] not in ids:
                client.api(f"repos/{FULL_NAME}/issues/{child['number']}/dependencies/blocked_by", "POST", {"issue_id": index[blocker]["id"]})


def ensure_items(client, project, spec, backlog, index, fields):
    observed = [row for row in fetch_items(client, project["id"]) if row.get("content")]
    items = {row["content"]["id"]: row for row in observed}
    if len(items) != len(observed):
        raise SetupError("Duplicate Project memberships detected; no item mutations attempted")
    for record in records(backlog):
        issue_id = index[record["id"]]["node_id"]
        item = items.get(issue_id)
        if item and item["isArchived"]:
            raise SetupError(f"Existing Project item for {record['id']} is archived; preserving live state")
        if not item:
            item = client.mutate("addProjectV2ItemById", "AddProjectV2ItemByIdInput",
                {"projectId": project["id"], "contentId": issue_id}, "item{id}")["item"]
            item["fieldValues"] = {"nodes": [], "pageInfo": {"hasNextPage": False}}
        populated = field_values(item)
        for desired in spec["fields"]:
            name = desired["name"]
            if name in populated:  # Never reset an existing live status, classification or owner.
                continue
            value = record[desired["record_key"]]
            if isinstance(value, list):
                value = "; ".join(value)
            field = fields[name]
            if desired["data_type"] == "SINGLE_SELECT":
                matches = [option for option in field["options"] if option["name"] == value]
                if len(matches) != 1:
                    raise SetupError(f"Unknown/ambiguous option {value!r} in field {name}")
                payload_value = {"singleSelectOptionId": matches[0]["id"]}
            else:
                payload_value = {"text": str(value)}
            client.mutate("updateProjectV2ItemFieldValue", "UpdateProjectV2ItemFieldValueInput",
                {"projectId": project["id"], "itemId": item["id"], "fieldId": field["id"], "value": payload_value}, "projectV2Item{id}")


def scaffold_entries(root):
    allowed_roots = {"README.md", "AGENTS.md", "CONTRIBUTING.md", "SECURITY.md", "LICENSE", "requirements.txt", ".gitignore", ".github", "docs", "planning", "schemas", "catalog", "sources", "research", "evidence", "templates", "examples", "scripts", "tests"}
    result = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if relative.parts[0] not in allowed_roots or "__pycache__" in relative.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise SetupError(f"Symlink is not allowed in scaffold upload: {relative}")
        if not path.is_file():
            continue
        if path.stat().st_size > 3_000_000:
            raise SetupError(f"Unexpectedly large scaffold file: {relative}")
        result.append({"path": relative.as_posix(), "mode": "100644", "type": "blob", "content": path.read_text(encoding="utf-8")})
    if not result:
        raise SetupError("No scaffold files found")
    return result


def stage_scaffold_pr(client, repository, root):
    default = repository["default_branch"]
    default_ref = client.api(f"repos/{FULL_NAME}/git/ref/heads/{default}")
    remote_branch = client.optional(f"repos/{FULL_NAME}/git/ref/heads/{BRANCH}")
    expected = client.state.get("scaffold_branch_head")
    if remote_branch and remote_branch["object"]["sha"] != expected:
        raise SetupError("Bootstrap branch already exists or changed outside the recorded checkpoint; preserving it")
    parent_sha = remote_branch["object"]["sha"] if remote_branch else default_ref["object"]["sha"]
    parent = client.api(f"repos/{FULL_NAME}/git/commits/{parent_sha}")
    tree = client.api(f"repos/{FULL_NAME}/git/trees", "POST", {"base_tree": parent["tree"]["sha"], "tree": scaffold_entries(root)})
    if tree["sha"] != parent["tree"]["sha"]:
        commit = client.api(f"repos/{FULL_NAME}/git/commits", "POST", {"message": "Establish scholarly research planning and validation foundation", "tree": tree["sha"], "parents": [parent_sha]})
        if remote_branch:
            current = client.api(f"repos/{FULL_NAME}/git/ref/heads/{BRANCH}")
            if current["object"]["sha"] != parent_sha:
                raise SetupError("Branch changed while staging scaffold; no ref update attempted")
            client.api(f"repos/{FULL_NAME}/git/refs/heads/{BRANCH}", "PATCH", {"sha": commit["sha"], "force": False})
        else:
            client.api(f"repos/{FULL_NAME}/git/refs", "POST", {"ref": f"refs/heads/{BRANCH}", "sha": commit["sha"]})
        client.state["scaffold_branch_head"] = commit["sha"]
        client.checkpoint()
    pulls = client.api(f"repos/{FULL_NAME}/pulls?state=open&head={ORG}:{BRANCH}&base={default}&per_page=100", paginate=True)
    if len(pulls) > 1:
        raise SetupError("More than one matching scaffold PR exists")
    if pulls:
        return pulls[0]
    return client.api(f"repos/{FULL_NAME}/pulls", "POST", {"title": "Establish the AI Papers & Research Index foundation", "head": BRANCH, "base": default,
        "body": "The organization needs a separately versioned scholarly index linked to existing technical research.\n\nThis PR adds the charter, citation and identity model, rights and editorial gates, complete planning hierarchy, metadata-only pilot proposals, validators, tests and CI. It preserves the frozen builder contract and technical ownership in the existing research repository.\n\nValidation and live setup readback are recorded separately. No verified scientific catalog, publication clearance or operating search engine is claimed.\n\nIndependent review of the latest commit and successful CI are required before merge. This setup script does not self-approve or bypass review.\n\nRefs https://github.com/Pick-Your-AI/pick-your-ai-research/issues/509"})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--inspect", action="store_true")
    parser.add_argument("--max-writes", type=int, default=300)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not 1 <= args.max_writes <= 400:
        parser.error("--max-writes must be between 1 and 400")
    if not args.apply and not args.inspect:
        print(json.dumps(offline_plan(root), indent=2))
        return 0
    if args.apply:
        validate_locally(root)
    client = GitHub(root / ".bootstrap/state.json", apply=args.apply, max_writes=args.max_writes)
    try:
        preflight = inspect_organization(client)
        if args.inspect:
            print(json.dumps({"viewer": preflight["viewer"], "reference_projects": preflight["reference_projects"],
                "target_exists": bool(preflight["repository"]), "equivalent_project": select_project(preflight["projects"], read_json(root / "planning/project-spec.json")["title"]),
                "team_access_plan": preflight["teams"], "remote_mutations": 0}, indent=2))
            return 0
        spec = read_json(root / "planning/project-spec.json")
        backlog = read_json(root / "planning/project-backlog.json")
        repository = ensure_repository(client, preflight, spec)
        client.state["repository_id"] = repository["id"]
        client.checkpoint()
        if (client.state.get("created_repository_id") == repository["id"]
                and not client.state.get("repository_metadata_initialized")):
            current_topics = client.api(f"repos/{FULL_NAME}/topics").get("names", [])
            wanted_topics = sorted(set(current_topics) | set(spec["repository_topics"]))
            if sorted(current_topics) != wanted_topics:
                client.api(f"repos/{FULL_NAME}/topics", "PUT", {"names": wanted_topics})
            client.state["repository_metadata_initialized"] = True
            client.checkpoint()
        ensure_teams_and_rules(client, preflight, root)
        project = ensure_project(client, preflight, repository, spec)
        client.state["project"] = {key: project[key] for key in ("id", "number", "url", "title")}
        client.checkpoint()
        fields = ensure_fields(client, project, spec)
        ensure_views(client, project, spec, fields)
        index = ensure_issues(client, backlog)
        ensure_relationships(client, backlog, index)
        ensure_items(client, project, spec, backlog, index, fields)
        from verify_github import audit_live
        audit = audit_live(client, root, project["number"])
        write_json(root / "planning/github-receipt.json", audit)
        pull = stage_scaffold_pr(client, repository, root)
        # Stable PR identity can be included in its own commit without a circular
        # self-reference to the commit SHA. Approval/head readback is a later gate.
        audit["pull_request"] = {key: pull[key] for key in ("number", "html_url", "state")}
        audit["pull_request"]["approval_status"] = "not_verified_by_setup"
        audit["status"] = "awaiting_independent_review" if not audit["problems"] else "partially_configured"
        write_json(root / "planning/github-receipt.json", audit)
        # Stage the final receipt too; otherwise the PR would contain the earlier
        # observation without its real PR identity. No approval or merge follows.
        pull = stage_scaffold_pr(client, repository, root)
        print(json.dumps({"repository": repository["html_url"], "project": project["url"], "pull_request": pull["html_url"],
                          "staged_head_sha": pull["head"]["sha"],
                          "status": audit["status"], "readback_problems": audit["problems"]}, indent=2))
        return 0 if not audit["problems"] else 1
    finally:
        client.checkpoint()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BudgetStop as error:
        print(f"PAUSED: {error}", file=sys.stderr)
        raise SystemExit(3)
    except (SetupError, OSError, subprocess.TimeoutExpired) as error:
        print(f"BLOCKED: {error}", file=sys.stderr)
        raise SystemExit(2)
