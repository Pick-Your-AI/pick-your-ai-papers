# Papers contributor and agent instructions

Read `CONTRIBUTING.md`, `docs/charter.md`, `docs/RESEARCH_METHOD.md`, `docs/PUBLICATION_RIGHTS.md`, and the applicable issue before changing files. Follow the current [organization rules](https://github.com/Pick-Your-AI/.github/blob/main/CONTRIBUTING.md). This repository plans and researches a scholarly directory; it does not authorize a production deployment, paid compute, source subscription, manuscript redistribution, or contact with authors.

## Scope and authority

- Preserve the upstream technical owners and frozen builder contract. Scholarly proposal schemas are independent. A new schema does not make the website a compatible consumer.
- Inspect current issues, PRs, native parents, assignees, Project fields and comments before remote mutations. Preserve concurrent work. Never assign someone from a historical table or assume a team permission.
- Native Assignees own work. Native sub-issues track independently reviewed outcomes; small tasks use nested checklists. Do not duplicate native children in a checklist.
- Keep stable `PAPER-*` identifiers distinct from GitHub issue numbers and globally namespaced scholarly/source IDs. Read actual IDs back after creation.
- New scope, evidence policy and source-use decisions need explicit records. Do not silently reinterpret upstream accepted research or reopen it because a new consumer is unfinished.

## Scientific and source integrity

- Never invent citations, DOI relationships, author identities, affiliations, publication dates, peer-review state, scientific findings, reproduction results, licenses, or access grants.
- A work, exact revision and publication manifestation are distinct identities. Do not infer that a later version preserves an earlier claim.
- Record author-reported results as author-reported. Citation checking, code availability, statistical comparability, reproduction and scientific validity are separate states.
- Every factual assertion and graph relationship needs source provenance and scope. `cites` does not mean `supports`; an affiliation is dated and does not prove present employment.
- Keep unknowns explicit. Missing evidence is not evidence of absence. Numeric unknowns never become zero; non-reproduction never becomes failed reproduction.
- Default to original summaries and permitted links. Do not commit abstracts, manuscript text, figures, credentials, private data, raw datasets or weights without their exact reviewed admission basis.
- Source rights are per material/field and intended use. Public accessibility, an upstream software license, or a paper's license is not a grant over all related content.
- Keep test fixtures explicitly synthetic and outside real proposal intake. A synthetic receipt cannot authorize a real release.

## Validation and delivery

Run from the root with Python 3.12:

```bash
python3 scripts/validate_plan.py
python3 scripts/validate_research.py
python3 scripts/render_docs.py --check
python3 -m unittest discover -s tests -v
```

Do not edit generated documentation independently of its canonical planning input. Report actual commands, failures and validation limits. Publication mode must reject withheld/uncleared proposals.

Use a focused branch and PR. An agent review is useful analysis but not a different-account GitHub approval. Do not bypass independent review, branch protections, required checks, source-use restrictions or recorded owner holds. Use `Refs` for partial work; inspect PR body, commit messages and linked issues before using a closing directive. Close a parent only after its children, own acceptance and material handoffs are complete.

Read back remote settings, memberships, views, issue relationships and exact default-branch commit before reporting establishment complete. An API success, local receipt, simulated response or repository name is not proof of live configuration. Keep planned, created, submitted, merged, accepted and published distinct.

## Decisions and escalation

For unresolved decisions, follow [CONTRIBUTING.md#routing-decisions](CONTRIBUTING.md#routing-decisions)
and the [canonical escalation guide](https://github.com/Pick-Your-AI/.github/blob/main/docs/governance/ESCALATION.md).
Refresh private routing evidence before choosing a recipient. Report unresolved
roles and failed or stale lookups explicitly; do not infer accepted ownership from
membership or access. Preserve the existing assignee, local gates and private-reporting
boundaries. Central links depend on the governance change merging; no automatic
routing, permission change or recurring job is enabled by these instructions.
