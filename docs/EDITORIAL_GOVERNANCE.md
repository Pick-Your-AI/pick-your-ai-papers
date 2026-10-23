# Editorial governance

The literature index needs accountable review without turning popularity, institutional affiliation or contribution volume into scientific authority. Editorial acceptance is scoped to the submitted record and its evidence. It is not a universal endorsement of the work.

## Roles and access

| Role | Responsibility |
| --- | --- |
| Contributor | Prepare an original note or proposal with identity, sources, limitations and rights observations. |
| Metadata/citation reviewer | Check exact identifiers, revisions, dates, author strings and source-to-field mapping. |
| Scientific reviewer | Assess whether summaries and claim interpretations match the cited scope, conditions and uncertainty. |
| Rights reviewer | Review exact material/use evidence and publication conditions; escalate unresolved questions appropriately. |
| Receiving owner | Accept the precise producer artifact and semantics for its consumer. |
| Maintainer | Enforce the repository's review process, validation and release record. |
| Organization administrator | Manage authorized teams and protections under organization policy. |

These are functional roles, not named assignments. Native GitHub Assignees identify accepted ownership. Team access must be inspected and granted through organization policy. No role description, planning record or `CODEOWNERS` assumption creates a permission.

The organization requires independent GitHub approval for `main`, including the latest push. The submitting account cannot approve its own PR. Agent-generated review, structural CI and domain review can inform that process but cannot impersonate an independent GitHub approval. A setup PR can remain awaiting review while its artifacts and backlog are otherwise ready.

## Editorial workflow

Discovery candidates and incomplete notes are valid inputs. A complete proposal is eligible for review only when identity, provenance, intended use and limitations are explicit. Reviewers record the exact commit, files/claims considered, decision, conditions and remaining work. Do not attribute approval to an absent owner or interpret silence as acceptance.

Review passes are orthogonal: citation verification does not approve scientific claims; scientific review does not grant rights; rights clearance does not establish a valid experiment. Publication requires all applicable gates for the exact projection.

An accepted machine-readable review binds the target content and its relevant evidence dependencies using the [review-scope digest](../evidence/README.md#content-bound-checks-and-reviews). Changing the target, source observations, conditions or affected graph scope requires a fresh scoped review. The digest does not verify reviewer identity or independence; the contribution process and actual review receipt must establish those facts. No actual approvals are present in the initial scaffold.

Use concise original summaries that explain what the work investigates and the bounds of its evidence. Attribute author-reported findings. Avoid unsupported superlatives, universal claims, ranking badges or claims of novelty without the relevant comparison and source evidence.

## Conflicts of interest and disagreement

Contributors and reviewers disclose material involvement in the work, related commercial interests or relationships that could affect a review. Use an uninvolved reviewer where possible. A disclosure does not itself disqualify a contribution; preserve it and the review boundary.

Retain reasoned disagreements and sources. Distinguish factual metadata corrections, interpretation disputes and unresolved empirical questions. Escalate only the contested scope; do not block unrelated metadata work or erase prior accepted evidence. Record decisions in the decision register or a scoped editorial record with version history.

## Corrections and complaints

Anyone may report an error with a public primary source and exact affected record. Handle private or sensitive content through [SECURITY.md](../SECURITY.md). A report is not automatically a verified retraction or misconduct finding.

Triage the source, scope, severity and publication impact. Append an event, correct the affected assertion and record downstream releases/edges that need revision. Keep the old and corrected interpretations when permitted. Use attributed publisher/archive notices for withdrawals and retractions; avoid unsupported personal allegations.

## Acceptance and closure

Acceptance requires the work package's deliverables, evidence, validation, independent review and material handoffs. A partial PR uses `Refs` and records remaining criteria. Parent completion requires completed children and its own synthesis. A merged issue does not automatically update a paper's editorial, scientific or publication state.

Before each release, record outstanding corrections, unresolved identities, withheld material and accepted limitations. The maintainer signs off on the actual immutable projection, not a future intended state. Changing a policy requires rationale, examples, schema/consumer impact and a transition plan where needed.
