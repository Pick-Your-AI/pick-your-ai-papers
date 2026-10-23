#!/usr/bin/env python3
"""Shared, narrowly scoped GitHub helpers. No network access at import time."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ORG = "Pick-Your-AI"
REPO = "pick-your-ai-papers"
FULL_NAME = f"{ORG}/{REPO}"
PARENT_REPO = "pick-your-ai-research"
PARENT_NUMBER = 509
API_VERSION = "2026-03-10"
MARKER = re.compile(r"<!-- pick-your-ai-papers:(PAPER(?:-\d{2}(?:\.\d{2})?)?) -->")
FIELD_FRAGMENT = "... on ProjectV2FieldCommon { id name dataType databaseId } ... on ProjectV2SingleSelectField { options { id name color description } }"
VIEW_FRAGMENT = """id number name layout filter
 fields(first:100) { nodes { ... on ProjectV2FieldCommon { id name } } pageInfo { hasNextPage } }
 groupByFields(first:100) { nodes { ... on ProjectV2FieldCommon { id name } } pageInfo { hasNextPage } }
 verticalGroupByFields(first:100) { nodes { ... on ProjectV2FieldCommon { id name } } pageInfo { hasNextPage } }
 sortByFields(first:100) { nodes { direction field { ... on ProjectV2FieldCommon { id name } } } pageInfo { hasNextPage } }"""


class SetupError(RuntimeError):
    pass


class BudgetStop(SetupError):
    """A resumable stop, never an instruction to evade a GitHub limit."""


class ApiError(SetupError):
    def __init__(self, message, status=None):
        super().__init__(message)
        self.status = status


def timestamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def records(backlog):
    yield backlog["program"]
    for epic in backlog["epics"]:
        yield epic
        yield from epic["work_packages"]


def issue_index(issues):
    result = {}
    for issue in issues:
        if "pull_request" in issue:
            continue
        markers = MARKER.findall(issue.get("body") or "")
        if len(markers) > 1:
            raise SetupError(f"Issue #{issue['number']} has ambiguous stable markers")
        if markers:
            if markers[0] in result:
                raise SetupError(f"Duplicate live issue marker {markers[0]}; no new issues created")
            result[markers[0]] = issue
    return result


def render_issue(record):
    """Native children are not repeated as checklist items."""
    identifier = record["id"]
    lines = [f"<!-- pick-your-ai-papers:{identifier} -->", f"<!-- scope-sha256:{digest(record)} -->", "",
             "## Outcome", "", record.get("outcome", record["title"]), "",
             f"**Stable ID:** `{identifier}`  ", f"**Record Type:** {record['record_type']}  ",
             f"**Owner role:** {record.get('owner_role', 'Research maintainer')}  ",
             "**Ownership:** Native GitHub Assignees are authoritative; a role is not an assignment.", ""]
    if record.get("parent"):
        lines += [f"Planned native parent: `{record['parent']}`. The native relationship is verified separately.", ""]
    if record["record_type"] == "Program":
        lines += [f"Parent audit: https://github.com/{ORG}/{PARENT_REPO}/issues/{PARENT_NUMBER}", ""]
    scope = record.get("scope", {})
    for key, title in [("in", "Included scope"), ("out", "Excluded scope")]:
        if scope.get(key):
            lines += [f"## {title}", ""] + [f"- {item}" for item in scope[key]] + [""]
    for key, title in [("deliverables", "Deliverables"), ("readiness_reasons", "Readiness"),
                       ("acceptance_criteria", "Acceptance criteria"), ("completion_evidence", "Completion evidence"),
                       ("definition_of_done", "Definition of done")]:
        values = record.get(key, [])
        if isinstance(values, str):
            values = [values]
        if values:
            lines += [f"## {title}", ""] + [f"- {item}" for item in values] + [""]
    if record.get("tasks"):
        lines += ["## Tasks and subtasks", ""]
        for task in record["tasks"]:
            lines.append(f"- [ ] `{task['id']}` {task['title']}")
            for subtask in task.get("subtasks", []):
                lines.append(f"  - [ ] `{subtask['id']}` {subtask['title']}")
        lines.append("")
    if record.get("blocked_by"):
        lines += ["## Prerequisites", "", "Native blockers are created for these declared prerequisites:", ""]
        lines += [f"- `{item}`" for item in record["blocked_by"]] + [""]
    if record.get("references"):
        lines += ["## References", ""]
        for reference in record["references"]:
            if isinstance(reference, str):
                lines.append(f"- {reference}")
            else:
                lines.append(f"- [{reference.get('title', 'Source')}]({reference['url']}) — {reference.get('relation', 'context')}")
        lines.append("")
    lines += ["## Completion rule", "", "Keep unmet criteria open. Schema validity, source discovery, repository setup and Project status do not establish scientific verification, reproduction, publication permission or an operating service.", ""]
    return "\n".join(lines)


def project_query(client, project_id, selection):
    return client.graphql("query($id:ID!){node(id:$id){... on ProjectV2{" + selection + "}}}", {"id": project_id})["node"]


def connection_nodes(client, project_id, connection, selection):
    nodes, after = [], None
    while True:
        archive_filter = ",archivedStates:[ARCHIVED,NOT_ARCHIVED]" if connection == "items" else ""
        query = "query($id:ID!,$after:String){node(id:$id){... on ProjectV2{" + connection + "(first:100,after:$after" + archive_filter + "){nodes{" + selection + "}pageInfo{hasNextPage endCursor}}}}}"
        page = client.graphql(query, {"id": project_id, "after": after})["node"][connection]
        nodes.extend(page["nodes"])
        if not page["pageInfo"]["hasNextPage"]:
            return nodes
        after = page["pageInfo"]["endCursor"]


def field_values(item):
    result = {}
    connection = item["fieldValues"]
    if connection["pageInfo"]["hasNextPage"]:
        raise SetupError("Item has more than 100 fields; refusing a partial field read")
    for node in connection["nodes"]:
        field = node.get("field")
        if field:
            result[field["name"]] = node.get("name", node.get("text", node.get("number")))
    return result


def fetch_items(client, project_id):
    selection = """id isArchived content {... on Issue {id number url repository{nameWithOwner}}}
    fieldValues(first:100){nodes{
      ... on ProjectV2ItemFieldSingleSelectValue{name field{... on ProjectV2FieldCommon{name}}}
      ... on ProjectV2ItemFieldTextValue{text field{... on ProjectV2FieldCommon{name}}}
      ... on ProjectV2ItemFieldNumberValue{number field{... on ProjectV2FieldCommon{name}}}
    }pageInfo{hasNextPage}}"""
    return connection_nodes(client, project_id, "items", selection)


class GitHub:
    """gh-authenticated API calls; credentials never enter arguments, files or output."""
    def __init__(self, state_path=None, apply=False, max_writes=300):
        if not shutil.which("gh"):
            raise SetupError("GitHub CLI (gh) is unavailable. Restore an authenticated administration connection; do not paste credentials into files.")
        self.apply = apply
        self.max_writes = max_writes
        self.writes = 0
        self.state_path = Path(state_path) if state_path else None
        self.state = read_json(self.state_path) if self.state_path and self.state_path.exists() else {}
        self.state.setdefault("write_times", [])

    def checkpoint(self):
        if self.state_path:
            write_json(self.state_path, self.state)

    def before_write(self, units=1):
        if not self.apply:
            raise SetupError("Mutation attempted in read-only mode")
        now = time.time()
        times = [t for t in self.state["write_times"] if t > now - 3600]
        self.state["write_times"] = times
        if self.writes + units > self.max_writes or len(times) + units > 400:
            self.checkpoint()
            raise BudgetStop("Conservative mutation budget reached; checkpoint retained. Resume after the rolling rate window permits. Do not switch credentials to evade a limit.")
        if times:
            delay = 5.0 - (now - times[-1])
            if delay > 0:
                time.sleep(delay)
        now = time.time()
        self.state["write_times"].extend([now] * units)
        self.writes += units
        self.checkpoint()  # Count even interrupted/ambiguous requests conservatively.

    def api(self, endpoint, method="GET", payload=None, paginate=False, mutation_units=1):
        mutation = method not in ("GET", "HEAD") and endpoint != "graphql"
        if mutation:
            self.before_write(mutation_units)
        command = ["gh", "api", "--hostname", "github.com", endpoint, "--method", method,
                   "-H", "Accept: application/vnd.github+json", "-H", f"X-GitHub-Api-Version: {API_VERSION}"]
        if paginate:
            command += ["--paginate", "--slurp"]
        if payload is not None:
            command += ["--input", "-"]
        result = subprocess.run(command, input=json.dumps(payload) if payload is not None else None,
                                text=True, capture_output=True, timeout=60, check=False)
        if result.returncode:
            match = re.search(r"HTTP (\d{3})", result.stderr)
            status = int(match.group(1)) if match else None
            # Do not print API payloads, authentication information or arbitrary server responses.
            if status in (403, 429):
                raise ApiError(f"GitHub returned HTTP {status} for {method} {endpoint.split('?')[0]}. Check permissions or rate-limit/reset information using the authenticated client before resuming; no automatic retry.", status)
            raise ApiError(f"GitHub request failed ({status or 'CLI/transport error'}) for {method} {endpoint.split('?')[0]}; no mutation was blindly retried.", status)
        if not result.stdout.strip():
            return None
        data = json.loads(result.stdout)
        if paginate:
            if not all(isinstance(page, list) for page in data):
                raise SetupError(f"Unexpected pagination shape: {endpoint}")
            return [item for page in data for item in page]
        return data

    def optional(self, endpoint):
        try:
            return self.api(endpoint)
        except ApiError as error:
            if error.status == 404:
                return None
            raise

    def graphql(self, query, variables=None, mutation_units=1):
        if query.lstrip().startswith("mutation"):
            self.before_write(mutation_units)
        result = self.api("graphql", "POST", {"query": query, "variables": variables or {}})
        if result.get("errors"):
            raise ApiError("GraphQL returned errors. Preserve the checkpoint and inspect authenticated readback before retrying; no error is treated as successful setup.")
        return result["data"]

    def mutate(self, name, input_type, data, selection):
        query = f"mutation($input:{input_type}!){{{name}(input:$input){{{selection}}}}}"
        return self.graphql(query, {"input": data})[name]
