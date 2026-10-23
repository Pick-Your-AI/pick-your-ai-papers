# Organization Project and repository establishment

## Actual state

**Repository and Project partially established; authenticated mutation access is blocked.** The [GitHub receipt](../planning/github-receipt.json), [Project UI readback](../planning/project-ui-readback.json) and [repository API readback](../planning/repository-readback.json) distinguish observed resources from intended configuration.

The public repository exists with ID `1430404173`, default branch `main` and initial head `f5a5084ec255f67b0a1c9e44fcba99098e10216d`. Public organization [Project #9](https://github.com/orgs/Pick-Your-AI/projects/9) exists with the exact requested name, description, README and default repository. All 17 fields exist; 16 full option lists and 14 exact defaults were read back. P0 was selected as the Priority default, with final option-specific confirmation still pending. Research Domain was created with all eight intended options, and its field identity and Cross-domain default were checked, but a final complete option-list readback remains open. Numeric settings-page identifiers are recorded as UI identifiers, not invented GraphQL IDs.

The 2026-10-23 01:15 UTC repository audit found only the initial branch, zero issues, zero pull requests, zero rulesets, zero topics and zero hosted workflow runs. The Project still has its initial View 1; none of the 11 requested saved views or issue memberships was created. Team and collaborator roles remain unverified. No permission grant or team membership change was made.

Three issue-creation requests failed to return a result, including an originating-context request canceled after 1399.5 seconds. Subsequent issue-list readback remained empty. The Browser control-browser connection then reported that its originating context was unavailable, and the alternate browser timed out. No authenticated GitHub CLI is present. These are execution-access blockers, not missing routine user authorization or an approval-review rejection.

Live browser inspection of Projects #1–#7 is preserved in the UI receipt: overview names, saved-view names and visible fields were inspected without changing those Projects. This was not an exhaustive read of all source options, collaborator roles or per-view settings.

The original user already authorized the administrative setup. Restore the originating browser connection and reconcile current resources before resuming. The separate organization requirement for independent review applies after a concrete scaffold PR exists; no self-approval, merge or bypass is implied.

## Intended resources and authoritative records

| Resource | Intended identity | Actual identity |
| --- | --- | --- |
| Public repository | `Pick-Your-AI/pick-your-ai-papers` | Created and read back; ID `1430404173`, public, default branch `main` |
| Organization Project | `Pick Your AI — AI Papers & Research Index` | Created as public [Project #9](https://github.com/orgs/Pick-Your-AI/projects/9); 17 fields created; complete configuration/readback blocked |
| Parent research audit | [pick-your-ai-research #509](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/509) | Existing inspected issue |
| Scaffold branch | `contrib/papers-bootstrap/foundation` | Not created; only initial main exists in the latest readback |
| Scaffold review | PR against the actual default branch | No PR has been opened |
| Program | `PAPER` | Planned native sub-issue of the parent audit |
| Hierarchy | 20 epics and 144 work packages | 165 native planning issues in total, including the program |
| Small work | 432 tasks and 864 subtasks | Nested checklists within the relevant work package |

The plan has 164 internal parent relationships and one additional cross-repository parent relationship to research #509. Its 270 declared hard dependencies are separate native blocker relationships. No child issue is duplicated as a checklist item.

The scope and acceptance baseline is [project-backlog.json](../planning/project-backlog.json). [project-spec.json](../planning/project-spec.json) describes proposed fields, options, views and access policy. [ruleset-spec.json](../planning/ruleset-spec.json) records inspected research ruleset structure and source IDs; those source IDs are not new papers-repository IDs. The GitHub receipt records observations only. Once execution starts, native GitHub status, assignees, relationships and review evidence are authoritative; a baseline generator must not reset live progress.

The supplied mission ended during `02.05 Conference and`. The remaining work-package decomposition is a reasoned proposal tied to the mission, explicitly recorded in the decision register. It is not represented as an unseen continuation of the user's text.

## Fields and semantics

All seventeen requested fields have been created as controlled single-select fields; the UI receipt identifies the remaining final option check. Native Title, Assignees, Parent issue and Sub-issues progress are reused. No substitute text-based owner field is created. Exact proposed options are in the generated Project specification.

| Field | Meaning |
| --- | --- |
| Status | Delivery state: Backlog, Ready, In Progress, In Review, Blocked, Done |
| Priority | P0, P1, P2, P3; urgency of planned work |
| Record Type | Program, Epic, Work Package, Task; baseline tasks are checklists, with Task reserved for later independently reviewable promotions |
| Readiness | Ready, Needs Input, Blocked, Awaiting Decision |
| Workstream | Program or one of the twenty epic workstreams |
| Research Domain | Scientific area under investigation |
| Publication Type | Type of scholarly object in the work scope |
| Research Method | Method of the planned investigation or implementation |
| Evidence Confidence | Explicit qualification, initially Not Assessed |
| Reproducibility Status | Scoped assessment, initially Not Assessed |
| Source Rights Status | Use-specific review, initially Unreviewed |
| Citation Verification | Identity verification state, initially Not Assessed |
| Publication Status | Scientific publication state; **Not Applicable on planning program, epic and work-package records** |
| Dependency Status | Whether declared prerequisites remain open or unresolved |
| Effort | Unestimated until an owner accepts an estimate |
| Release Phase | Foundation, Metadata Pilot, Evidence Pilot, Website Handoff, Maintained Index |
| Acceptance Status | Reviewer disposition, initially Not Accepted |

Delivery Status must not be used as a paper's peer-review, publication, validity or reproduction status. Source Inspected does not mean a scientific result is correct. Website publication eligibility is an independent per-record gate, not a Project option.

## Saved views

Each requested view is specified with explicit filters, visible native/custom fields, sorting and grouping. None of these eleven saved views has been created yet. A matching name alone is insufficient readback.

| Saved view | Intended use |
| --- | --- |
| Program Overview | Program record, child progress, release and acceptance |
| Epic and Work-Package Hierarchy | Epics and work packages with native parents and child progress |
| Research Domains | Domain, publication type and planned research method |
| Literature Discovery | Source-discovery workstream |
| Evidence and Reproducibility | Evidence qualifications and reproduction assessments |
| Citation Verification | Work whose citation identity is not yet verified |
| Rights and Publication Review | Use rights, scientific publication status and editorial acceptance |
| High-Priority Work | Open P0/P1 work |
| Blocked Dependencies | Work with open hard prerequisites |
| Website Publication Readiness | Website-handoff work and its separate review fields |
| Unassigned Work | Open work without a native GitHub assignee |

The proposed layout is table throughout so reviewers can compare fields directly. Views may evolve through an explicit reviewed change. The setup script preserves existing views and reports drift instead of silently replacing a team's live configuration.

## Organization access and review

The inspected organization policy uses teams rather than direct individual collaborator grants. Before applying access, the script reads actual teams and permissions on the research repository and checks the current organization contribution-policy blob SHA. It expects Maintainers/Triage, Research/Triage and Research Lead Maintainers/Admin. It resolves actual team IDs and slugs from that response. No team membership is added or removed. A repository-specific contributor team remains an explicit organizational decision; no existing unrelated child team is repurposed.

For a new Project created by this run, the script links the observed Research Lead Maintainers team and requests its Admin role. Existing Project access is preserved. Project collaborator roles need a subsequent settings-page readback because the inspected GraphQL Project team connection exposes links, not all collaborator roles. The API verifier leaves this acceptance item open. It never equates a linked team with a verified permission.

Repository rules follow the inspected research branch/tag boundaries and latest-push independent approval rule. Unknown source team bypass IDs are not copied. Boundary bypasses use only the live verified Research Lead Maintainers ID plus the source policy's organization/repository-role actors. The review rule gets no team bypass. Existing rules are never weakened or overwritten.

The complete scaffold must be staged in a PR; no scaffold PR currently exists. Organization contribution rules and the research shared instructions require a different GitHub account to approve the latest push. Local multi-agent code review is useful validation, but is not that approval. The script never approves, merges, force-pushes, changes a team membership or bypasses a check. Initial repository creation uses GitHub's README initialization; the complete scaffold remains pending until its PR is independently approved and merged.

CI is defined in `.github/workflows/ci.yml` with the job name `validate`, pinned GitHub-owned actions, read-only repository permissions and no third-party Python packages. Successful CI for the actual default-branch head must be read back after merge. The copied source rulesets do not invent a required-check rule; whether to add a required `validate` context is a tracked engineering decision after the context has actually run. Repository setup cannot be marked fully accepted while CI or review evidence is missing.

## Commands and safe resumption

Use Python 3.12. Local validation is offline and uses the standard library:

```bash
python3 scripts/validate_plan.py
python3 scripts/validate_research.py
python3 scripts/render_docs.py --check
python3 scripts/build_project_spec.py --check
python3 -m unittest discover -s tests -v
```

The following prints the intended setup with **zero remote calls and zero remote mutations**:

```bash
python3 scripts/bootstrap_github.py
```

With an already authorized GitHub CLI session, inspect live organization resources without changing them:

```bash
python3 scripts/bootstrap_github.py --inspect
```

Apply the user-authorized setup only through the authenticated connection:

```bash
python3 scripts/bootstrap_github.py --apply
```

The apply sequence is local validation, live organization/target/equivalent-Project inspection, repository and policy configuration, Project creation or reuse, fields/views, issue records, native parents/blockers, membership/field values, actual readback, and scaffold PR. The actual Project number is returned by GitHub and saved; no number is predicted from Projects #1–#7.

The CLI bootstrap's local `.bootstrap/state.json` checkpoint contains resource IDs and a conservative rolling request budget, never credentials. The connector-driven execution keeps its own `.bootstrap/connector-ledger.json`, with actual operation results and timestamps; browser observations are recorded separately. Keep these with the working tree for resumption. They are excluded from commits and the public delivery archive. Default CLI apply runs stop after 300 mutations; its persistent rolling cap is 400 mutations per hour, with at least five seconds between writes. Connector writes are also sequential and paced, with rate/permission errors stopping the run. These are conservative client limits, not a promise about GitHub quota. Never rotate identities or delete checkpoints to evade service limits. A transport-ambiguous mutation is reconciled with actual readback before resuming.

Issue markers contain stable planning IDs. Duplicate identities, conflicting parents, conflicting Project identities, changed bootstrap branches, partially read connections and archived existing Project items cause an explicit stop. Existing issue bodies, assignees, populated Project fields and view definitions are preserved. New options preserve existing option IDs; extra options cause a readback discrepancy rather than being deleted. No API data is inferred from array position.

The bootstrap branch is updated only when its actual head matches the checkpoint. The PR receipt includes stable PR identity, not a circular claim about the commit that contains itself. Its final receipt is staged too. A separate later audit checks exact default-branch blobs and CI.

## Prepared native relationship workflow

The prepared [native workflow](../.github/workflows/reconcile-native-relations.yml) and [reconciler](../scripts/reconcile_native_relations.py) use a complete actual issue map bound to the canonical backlog. They do not create the issues or configure the Project. The exact repository, actor, contribution branch and immutable head are checked before additive parent/blocker writes. A conflicting parent is preserved and stops execution; each successful write requires readback. The cross-repository audit parent is a separate operation.

The workflow is scoped to an intentional `planning/issue-map.json` push on the bootstrap branch whose commit includes `[native-relationships]`. It uses ephemeral repository permissions, never a stored token or paid coding agent. Known recent content writes and a five-second interval bound its rate; a 403/429 stops rather than retrying or changing identity. GitHub's actual limits and unrelated account activity can be stricter. Optional public Project readback does not establish collaborator roles, native assignees or final configuration acceptance.

No actual issue map, hosted run or native relationship result exists yet. Local tests establish behavior on controlled fixtures, not successful GitHub execution.

## Actual readback and completion

The audit performs only reads against GitHub:

```bash
python3 scripts/verify_github.py --output planning/github-receipt.json
```

The number is discovered by the exact Project title; an explicit `--project-number` may be supplied after that number is observed. The verifier checks:

1. Actual repository visibility, metadata, default branch and immutable head.
2. Project owner/number/title/description, open/public state and repository membership.
3. Field IDs, types and every option; duplicate field names and incomplete reads fail.
4. Every planned issue, stable scope signature, nested task/subtask IDs, native parent and declared blocker.
5. Active Project membership, actual field values and actual native assignees.
6. Each requested view's layout, filter, columns, grouping and sorting.
7. Repository team access and complete ruleset controls, including bypass actors.
8. Every scaffold blob on the actual default branch, plus successful CI at that exact head.

The receipt retains remaining problems separately from acceptance gates. It always leaves Project collaborator-role readback open until the settings UI is inspected and that observation is recorded by an authorized maintainer. It also leaves a distinct PR-approval gate open until the actual merged PR, latest reviewed push, independent approval and merge evidence are inspected. Matching default-branch files alone does not prove that review occurred. A partial API audit must not be relabeled fully verified. GitHub configuration readback makes no scientific-catalog assertion.

Foundation release requires the full repository, hierarchy, Project, CI and governance evidence. An explanation of missing access is a valid blocked-work record; it does not satisfy the release gate. Metadata, evidence, website and maintained-index releases have separate acceptance conditions in [release-manifest.json](../planning/release-manifest.json).

## API and policy references

These references justify the implementation surface; they are not receipts that any API call succeeded in this environment.

- [Organization contribution policy](https://github.com/Pick-Your-AI/.github/blob/main/CONTRIBUTING.md)
- [Shared research execution rules](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/prompts/SHARED.md)
- [GitHub Projects GraphQL reference](https://docs.github.com/en/graphql/reference/projects)
- [Projects REST views](https://docs.github.com/en/rest/projects/views?apiVersion=2026-03-10)
- [Native sub-issue API](https://docs.github.com/en/rest/issues/sub-issues?apiVersion=2026-03-10)
- [Native issue dependency API](https://docs.github.com/en/rest/issues/issue-dependencies?apiVersion=2026-03-10)
- [GitHub REST rate limits](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api)

The live API compatibility of the complete CLI apply sequence remains untested. Browser creation and field configuration succeeded partially; connector writes then stalled and browser access became unavailable. Mocked regression tests verify failure handling and state preservation, not successful remote deployment. Actual operation receipts are collected independently.
