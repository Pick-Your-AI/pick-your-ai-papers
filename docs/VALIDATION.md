# Establishment validation and remaining execution

This checkpoint combines the validated source foundation with remote observations from **2026-10-23**. Each receipt preserves its own observation time. These files cannot predict their own eventual commit SHA: the finalization report, temporary-workflow deletion commit and latest PR checks provide the later exact publication evidence. Local validation, contribution-branch publication, hosted CI, independent GitHub approval, default-branch acceptance and scholarly release are distinct outcomes.

## Result

The source baseline passed the offline planning/research validators, deterministic generated-file checks and **130 regression tests** after the bounded native reconciler was added. The explicit scholarly publication gate rejected all four withheld candidates as intended. These checkpoint documentation and API-enumeration changes require their own exact-revision validation before submission.

The later independent audit verified all **85 foundation files** at contribution commit [`dd2de102f81c3d573003795ab8352fda13bafc85`](https://github.com/Pick-Your-AI/pick-your-ai-papers/commit/dd2de102f81c3d573003795ab8352fda13bafc85) and all **165 planning issues**, with exact titles, bodies and stable identities. The program's native parent research #509 is verified. All seventeen Project fields and option lists, and eleven saved views' names, field sets, filters, grouping and sorting have been read back. The later native run and independent checkpoint audit verify all 164 reciprocal parents and 270 blockers. Its complete Project snapshot also verifies all eleven table views, API field enumerations and empty vertical grouping. Physical UI order is separately observed. The later complete item collection independently matches all 165 memberships and 2,805 controlled values, preserving actual native assignees. Access/rules, final-push CI and independent review, merge and default-branch establishment remain separate gates.

### Graph evidence-binding correction (2026-10-23)

The [PR #166 review](https://github.com/Pick-Your-AI/pick-your-ai-papers/pull/166) found that `validate_research.py` accepted a `metadata_checked` edge supported by any matched check that shared one of its sources. A check of a different revision, or of the same revision without the citation, passed. The reviewer's synthetic `cites` edge was reproduced at `0588c222fd3c787c2f13a8dd391c497cb21b44a5` in both variants: zero errors and nine edges.

The correction requires each such edge to be supported by a check that observed its exact subject, predicate, object and revision. For the rule itself, see [edge evidence binding](../evidence/README.md#content-bound-checks-and-reviews). Checks gain an optional `observed_relations` list, which none of the four real checks populates. All eight seed identity edges still validate unchanged, and no research evidence was added.

Local validation of the correction (Python 3.14; hosted CI uses 3.12):

- All 139 tests passed: the 130 baseline tests plus 9 `EdgeEvidenceBindingReviewTests`.
- All 16 new assertions fail on the uncorrected validator.
- The plan, research, render and project-spec checks pass.
- Publication mode still rejects with the same 80 unmet gates.

Hosted CI on the pushed head is the authoritative result.

At 13:35 UTC, four active repository rulesets and the team grants were applied and read back:

- **Rulesets:** default-branch boundary, branch boundary, tag boundary, and review required. The review ruleset requires one approval, approval of the latest push and the `validate` check, with no bypass.
- **Team grants:** Maintainers and Research triage, Research Maintainers write, Research Lead Maintainers admin.

These supersede the earlier Confirm access observation. They do not constitute independent approval.

The temporary [publisher run](https://github.com/Pick-Your-AI/pick-your-ai-papers/actions/runs/39900496348) concluded **failure** after its final issue inventory comparison; it is not reported as a passing validation run. Its prior writes were independently reconciled and all 165 issues were found exact. No cause is asserted for the earlier collection mismatch. Actual resource verification is recorded separately from that workflow conclusion.

| Check | Actual result and scope |
| --- | --- |
| `python3 scripts/validate_plan.py` | Source baseline passed hierarchy, schema, dependency DAG, coverage and release consistency |
| `python3 scripts/validate_research.py` | Source baseline passed: 4 proposals, 4 sources, 4 metadata checks, 8 typed edges, 0 experiments, 0 eligible records, 0 published records |
| `python3 scripts/render_docs.py --check` | Source baseline delivery plan and backlog matched canonical planning; checkpoint output must be regenerated and checked |
| `python3 scripts/build_project_spec.py --check` | Source baseline matched; `PAPER-DEC-017` changes only the eleven API field enumerations used by the comparator and requires a fresh check |
| `python3 -m unittest discover -s tests -q` | 130 source-baseline tests passed; this is not hosted CI |
| `python3 scripts/validate_research.py --publication` | Expected rejection, exit code 1; 80 unmet publication-gate messages across 4 withheld candidates |
| Exact contribution foundation | 85 of 85 files matched prepared source `42dc48999577c49a4b3a78eb7eef5d5186fc03ed` at observed head `dd2de102f81c3d573003795ab8352fda13bafc85` |
| Exact native issue contents | 165 of 165 matched; zero missing, duplicate or extra stable IDs at 04:45:58 UTC |
| External parent | Papers program #1 has native parent research #509 |
| Project definitions | 17 of 17 requested fields/options verified; 11 of 11 view names/field sets/filters/grouping/sorting verified |
| Project membership and saved views | All 165 memberships present; eleven table-view API configurations and field enumerations at 05:50:41 UTC. Separate UI observations: Research Domains saved/reloaded at 06:27:50 UTC; hierarchy physical headers recorded at 06:34:41 UTC |
| Project item values | All 2,805 actual controlled values match; 165 unique expected memberships and native assignees recorded; collection ended `2026-10-23T06:18:07+00:00` |
| Native internal graph | All 164 reciprocal parents and 270 blockers verified; 434 unique readback-verified attempts, no identity or planned-edge differences |
| Project access | At 06:29:42 UTC: public, organization base Write, organization owners Admin, one listed CompleteDotTech/Admin collaborator and no listed teams; no access changes |
| Repository access/rules | Both pages still showed Confirm access at 06:27:50 UTC; zero access grants or rule saves applied by this execution |
| Workflow files and actual map | Both canonical workflow blobs and the exact issue map verified at `20435598c490c87cb2d6ff8eafaaa89d14620fac`; temporary publisher absent |
| Native hosted run | [#39904044419](https://github.com/Pick-Your-AI/pick-your-ai-papers/actions/runs/39904044419) completed successfully at 05:50:43 UTC; full checkpoint independently audited |
| Dated PR and observed-head CI | [PR #166](https://github.com/Pick-Your-AI/pick-your-ai-papers/pull/166) was open/draft at the 05:33 UTC observation, head `20435598c490c87cb2d6ff8eafaaa89d14620fac`; [run #39905405514](https://github.com/Pick-Your-AI/pick-your-ai-papers/actions/runs/39905405514) passed |
| Final-push approval, merge and default-branch CI | Pending; the successful earlier PR-head run does not establish these gates |
| Complete live CLI bootstrap/API compatibility | Not executed; actual Browser, bounded Actions and readback results are recorded separately |

## Scope counts

| Planned object | Count |
| --- | ---: |
| Program | 1 |
| Epics | 20 |
| Independently reviewable work packages | 144 |
| Native planning issue outcomes | 165 |
| Internal native parent relationships | 164 |
| Additional parent-audit relationship | 1 |
| Hard prerequisite relationships | 270 |
| Checklist tasks | 432 |
| Nested subtasks | 864 |
| Coverage entries | 102 |
| Coverage dimensions | 7 |
| Decision records | 17 |
| Requested Project fields | 17 |
| Requested saved views | 11 |
| Planning and scholarly schemas | 11 |

These are planning-scope counts. Separately, the remote issue audit verifies all 165 planned native issue outcomes. The later successful native run separately verifies all 164 internal parents and 270 blockers, with an independent exact-edge checkpoint audit. The canonical planning baseline remains Backlog and Not Accepted, and all 165 native assignees were empty at the recorded issue audit. The separate final actual Project readback verifies all 2,805 controlled values against that baseline. No scientifically accepted catalog is implied; literature denominators remain unmeasured where no bounded corpus has been enumerated.

## What the tests substantiate

The test suite includes **34 planning**, **51 research**, **25 GitHub-setup/readback**, and **20 bounded native-relationship** tests. Synthetic grants, notices, reviews and experimental labels exist only in temporary test fixtures; they are never copied into real evidence registers.

Planning tests reject duplicate/cross-owner identifiers, invalid native parents, missing prerequisites, dependency cycles, false completion, unsafe paths/URLs, invented denominators, unmapped scope, missing release evidence and generated-document drift. They also distinguish future deliverable paths from files that must already exist.

Research tests reject malformed and credential-bearing URLs, unsupported schema assertions, duplicate JSON keys, copied abstract/full-text fields, unknown objects, incompatible identities and dangling graph edges. They verify that citation checks bind the exact observed fields; accepted reviews bind their content and relevant evidence dependencies; display permission does not imply export permission; all contributing sources require field/use review; correction and retraction relationships require a scoped authoritative notice; and a reproduction relationship needs a real independent experiment. Positive synthetic cases prevent a reject-everything implementation from passing.

Setup tests use local mocks. They verify preservation of existing status, assignees, closed issues, archived memberships, private Projects, branch edits and approval boundaries. They reject duplicate markers/fields/memberships, incorrect option/view readback and undeclared bypass actors. They also reject missing acceptance text or checklist syntax even when a scope marker remains unchanged, while allowing checked tasks and additional execution notes. They do not prove that a future live API call will succeed.

Native-relationship tests exercise exact repository/branch/actor pins, complete observed issue maps, immutable branch-head checks, one-request mutation behavior, rate-window pauses and credential-free checkpoint reporting. These tests do not establish that remote hierarchy or dependency writes have occurred.

## Evidence and rights limits

The upstream citation audit is bounded to fifteen selected research files and three website files at recorded immutable revisions. The sixty-one distinct arXiv work identifiers in that sample are discovery inputs, not a complete organization-wide inventory or a verified catalog. Four exact-revision bibliographic proposals were checked against their primary arXiv landing pages. No benchmark or reproduction experiment was performed.

Only descriptive metadata, original short summaries, identity/provenance records and permitted links are included. The source-specific notes distinguish observed arXiv CC0 metadata terms from pending internal production-catalog review. Public repository inclusion is distribution; `withheld` never means a committed file is private. No abstracts, article text, copyrighted figures, private datasets, credentials or model binaries are part of this package.

Digest checks detect inconsistent or stale recorded evidence. They are not signatures, authentication of human reviewers, proof of scientific validity, or a substitute for source-rights and editorial judgment. Automated file checks are not a guarantee that every possible sensitive string has been detected.

## Remaining execution gates

1. Preserve the verified Project configuration, native ownership and Project access roles while completing the remaining repository and review gates.
2. Preserve the verified 164-parent/270-blocker native graph and complete actual edge inventory; include its self-contained identity/edge hashes and hosted-run link in the final receipts.
3. Complete GitHub's sudo reauthentication for the authorized repository team-access/rules saves, then verify the actual settings. A prepared form is not configuration evidence.
4. Validate and add the final dated receipts to existing PR #166; read back successful hosted CI after that final push. The earlier run at 20435598 passed.
5. Obtain the organization's independent GitHub approval of the latest push, merge through the approved process, and verify exact default-branch files, checks and governance. Keep Foundation unaccepted until its complete gates are met.

The original mission authorizes administrative setup. The current sensitive-settings blocker is GitHub's sudo reauthentication wall, distinct from routine approval and from the earlier resolved Browser connection problem. The independent-review gate comes from the organization's contribution policy and research shared instructions; local agent review does not satisfy it. No scholarly publication, scientific validity or reproduction is established by issue creation or a passed software check.

See [Project setup](PROJECT_SETUP.md) for precise resource identities, resumable commands, safeguards and API references, and [the actual GitHub receipt](../planning/github-receipt.json) for machine-readable execution progress.
