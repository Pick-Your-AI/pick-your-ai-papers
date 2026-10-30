# Contributing

Contributions should make a scholarly record easier to identify, trace, challenge or maintain. A useful note can record an unresolved question; it need not pretend to be a complete publication-ready record.

The [organization contribution rules](https://github.com/Pick-Your-AI/.github/blob/main/CONTRIBUTING.md) govern access, reviews, credentials and merging. The [organization Code of Conduct](https://github.com/Pick-Your-AI/.github/blob/main/CODE_OF_CONDUCT.md) applies here. This guide adds the literature-specific workflow.

## Choose the correct contribution

| Contribution | Place it here | Required distinction |
| --- | --- | --- |
| Discovery, incomplete identity, candidate comparison | `research/` using the research-note template | A discovery candidate is not admitted catalog data. |
| Complete metadata proposal | `catalog/proposals/` | Source checking and publication eligibility remain separate. |
| New source or changed terms | `sources/` and a scoped rights review | Material, fields and operations must be named. |
| Relationship or experimental claim | Typed proposal with evidence | A citation alone does not establish support. |
| Reproduction assessment | Sanitized assessment/manifest | Available code is not an executed independent reproduction. |
| Correction, disputed identity or withdrawal | Correction issue and event record | Preserve source, prior revision and review history. |
| Search/filter/public page behavior | Website handoff | The website owns its interface and production integration. |

First check the backlog and existing issues to avoid duplicate ownership. Use the issue's stable ID and deliverable path. Open a new native sub-issue when the outcome needs separate ownership or review; otherwise add a small task to the current issue.

## Research workflow

1. State the user question, inclusion boundary, candidate sources and sampling method. Check existing T1/T5/T6 and market references before creating a second source record.
2. Resolve work, exact revision and manifestation independently. Retain source-provided identifiers and dates with their types. Record uncertain author matches rather than merging names by similarity.
3. Write an original summary. Attach claim-level primary citations, actual access dates, exact versions, conditions, uncertainty and limitations. Describe failed access honestly.
4. Evaluate source material and intended operations using the rights template. A source is not approved simply because another repository cited it.
5. Keep incomplete or unsupported facts in notes. Submit complete structured proposals against the applicable independent scholarly schema. Do not edit the frozen builder contract.
6. Run the checks. Have another person review the identity, source support, summary, rights and claims, then collect actual receiving decisions for material cross-repository handoffs.

## Branches, review and ownership

Repository access comes through teams. These files do not grant a collaborator or a team access. If you already have the organization's early-contributor access, use `contrib/<your-login>/<topic>`; otherwise work from a fork. Do not push to someone else's branch.

Native GitHub Assignees are the source of truth. Planning role descriptions describe the expertise required, not an assignment or permission. Preserve live assignees and delegation.

Every PR to `main` needs an approval from someone other than the author, including approval of the latest push. Follow required checks and current branch protections. A local automated review or another agent's review does not create that GitHub approval. Include the exact commit, review scope and unresolved gaps in any acceptance receipt.

## Validation

```bash
python3 scripts/validate_plan.py
python3 scripts/validate_research.py
python3 scripts/render_docs.py --check
python3 -m unittest discover -s tests -v
```

To update generated planning documents, run `python3 scripts/render_docs.py`, inspect the diff, then rerun `--check`. Use `--root` only when deliberately validating another checkout. The publication gate is `python3 scripts/validate_research.py --publication`; withheld records must fail that gate.

Automation checks file structure, references, typed statuses, graph/plan integrity and consistency within its documented scope. It does not establish factual truth, legal permission, peer review, reproduction, source freshness or live GitHub configuration. Explain remaining manual review explicitly.

## Acceptance and closure

Use `Refs #n` when contributing a partial slice. A closing directive is appropriate only when the merged content will satisfy every criterion, all necessary handoffs are accepted, and the current PR/commit metadata has been checked. A parent can finish only after its children and its own synthesis and acceptance are complete.

Delivery Status, paper publication status, editorial status, citation verification, rights, and reproducibility are separate. Never mark research accepted because an issue or schema was created. Do not delete duplicate issues; preserve unique information, link the canonical outcome, and close the duplicate through the normal process.

## Security and permitted material

Follow [SECURITY.md](SECURITY.md). Do not submit credentials, private correspondence, private author details, signed download URLs, restricted article contents, private datasets or model weights. Use small sanitized manifests for external artifacts. The MIT license covers original contributions only; declare third-party provenance and permissions separately.

## Routing decisions

For an unresolved decision, first read the existing issue, its assignees, relevant
decision record and related pull requests. Preserve accepted ownership and local
review, evidence, security and release requirements. Routing identifies a contact;
it does not grant access, appoint an owner, authorize publication or waive a gate.

Use the canonical [escalation guide](https://github.com/Pick-Your-AI/.github/blob/main/docs/governance/ESCALATION.md) and
[versioned routing policy](https://github.com/Pick-Your-AI/.github/blob/main/governance/escalation-policy.json). These links depend on the organization
governance change merging; until then, use its reviewed checkout and describe the
route as provisional. Do not claim the central tooling is installed or active.

The order is repository team → repository maintainer → repository lead maintainer
→ applicable parent teams → CompleteDotTech. Record a disposition at each level,
including unresolved, vacant, pending-acceptance or inaccessible roles; membership,
team-management status and repository permissions do not establish accepted
operational ownership. Keep owner placeholders for the final fallback. Do not
silently skip an unresolved role or treat a proposed mapping as accepted.

An operator with read access must refresh the private snapshot before resolving:

```sh
python /path/to/org-checkout/governance/router.py refresh --policy /path/to/org-checkout/governance/escalation-policy.json --snapshot /private/path/routing-snapshot.json --status /private/path/routing-status.json
python /path/to/org-checkout/governance/router.py resolve --policy /path/to/org-checkout/governance/escalation-policy.json --snapshot /private/path/routing-snapshot.json --repo Pick-Your-AI/pick-your-ai-papers --max-age-seconds 86400 --status /private/path/routing-status.json
```

Here `86400` is an **operator-selected example**, not an approved default. Select
an appropriate explicit maximum age; a proposed policy value does not supply one.
Check that refresh succeeded. If refresh fails, stop recipient selection and
report the failure; the last successful snapshot is retained for diagnosis, not
as a current route. Report stale or incomplete coverage explicitly. Keep snapshots,
raw API responses, rosters and private
identities outside public Git and public issues. Share only the necessary public
team destination and a sanitized decision summary.

When escalation is needed, include the decision needed, current responsible role,
prior disposition and proposed next recipient. Reuse information already in the
issue or PR; routine contributions need no full escalation history. Send nothing
and change no assignment automatically. Sensitive reports follow [SECURITY.md](SECURITY.md),
including its conditional reporting routes; this guidance establishes no new or
verified private intake.

The owner-selected scope of [organization issue #14](https://github.com/Pick-Your-AI/.github/issues/14)
is all changes in Research, Sustainability, Applications, Papers, Catalog Pipeline
and Datasets. This records scope only: current independent-review and branch/check
requirements remain in force. Any proposed enforcement change requires separate
approval; no review exception or CODEOWNERS change is established here.
