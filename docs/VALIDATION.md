# Establishment validation and remaining execution

Offline baseline observed on **2026-10-22 at 20:13 UTC**; remote progress audited on **2026-10-23 at 01:15 UTC**. Local validation is not a GitHub Actions run, an independent GitHub approval, a rights clearance or a scientific verification result. After adding bounded native-relationship reconciliation, the full local suite was rerun on 2026-10-23 at 01:20 UTC and passed **130 tests**.

## Result

The baseline establishment package passed the offline planning and research validators, deterministic generated-file checks and **110 regression tests**. The explicit publication gate fails as intended because every current scholarly proposal remains withheld and unapproved. GitHub access subsequently recovered: the public repository was created and its ID, visibility, default branch and initial commit were read back. Public organization Project #9 has also been created with 17 fields. Sixteen option lists were fully read back, while the final Research Domain list, memberships, saved views and access remain incomplete. Connector writes stalled and both browser paths became unavailable; complete scaffold publication, issue creation and relationship verification are blocked. Later changes require their own validation receipt.

| Check | Actual result |
| --- | --- |
| `python3 scripts/validate_plan.py` | Passed; hierarchy, schema, dependency DAG, coverage and release consistency |
| `python3 scripts/validate_research.py` | Passed; 4 proposals, 4 sources, 4 metadata checks, 8 typed edges, 0 experiments, 0 eligible records, 0 published records |
| `python3 scripts/render_docs.py --check` | Passed; delivery plan and complete backlog match canonical planning |
| `python3 scripts/build_project_spec.py --check` | Passed; proposed fields/options/views match the canonical plan |
| `python3 -m unittest discover -s tests -q` | 130 tests passed in the latest combined run |
| `python3 scripts/validate_research.py --publication` | Expected rejection, exit code 1; 80 unmet publication-gate messages across 4 withheld candidates |
| Local Markdown destination audit | No missing local file links |
| `python3 scripts/bootstrap_github.py` | Offline plan; no live mutations by this CLI; actual browser-created Project is #9 |
| Complete live CLI bootstrap/API compatibility | Not executed; this run uses authenticated browser and supported connector operations |
| Actual repository initialization | Read back: repository `1430404173`, public, `main`, initial commit `f5a5084ec255f67b0a1c9e44fcba99098e10216d` |
| Actual organization Project creation | Public [Project #9](https://github.com/orgs/Pick-Your-AI/projects/9), 17 fields; final configuration not verified |
| Complete Project/issue/relationship/CI readback | Blocked; latest audit has 0 issues, 0 PRs, 0 rulesets, 0 hosted runs |

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
| Decision records | 16 |
| Requested Project fields | 17 |
| Requested saved views | 11 |
| Planning and scholarly schemas | 11 |

These are artifact/plan counts. They are not counts of created GitHub issues or scientifically accepted literature. Every planning record remains Backlog, unassigned and Not Accepted. Literature coverage denominators remain unmeasured where no bounded corpus has been enumerated.

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

1. Restore authenticated mutation access, then reconcile current resources. Projects #1–#7 overview inspection and target UI observations are recorded; source/target team access still requires verification.
2. Configure the dedicated Project, create all 165 native planning issues and actual relationships, and populate/read back memberships and views.
3. Record supported connector mutations and browser configuration separately; repository initialization alone does not satisfy complete setup acceptance.
4. Stage the complete scaffold PR, obtain the organization's independent approval of the latest push, and merge only through the approved process.
5. Read back exact default-branch files, successful CI, Project collaborator roles, actual PR approval and merge evidence. Keep Foundation unaccepted until these gates are satisfied.

The original user already authorized administrative setup. Read access remains available, but connector writes did not return and browser control became unavailable. Resumption requires a working connection, not routine approval. The separate independent-review gate comes from the organization's contribution policy and research shared instructions; local agent review does not satisfy it.

See [Project setup](PROJECT_SETUP.md) for precise resource identities, resumable commands, safeguards and API references, and [the actual GitHub receipt](../planning/github-receipt.json) for machine-readable execution progress.
