# Maintenance and correction operations

Maintenance keeps identities, source observations, corrections and public projections traceable. The workflow below is a delivery requirement. It is not a running scheduled crawler, a monitoring service or authorization for background collection.

## Classes of change

| Change | Required response |
| --- | --- |
| New paper revision or manifestation | Preserve prior identities; inspect changed metadata/claims and supported relationships. |
| Author identity or affiliation correction | Review the primary evidence, merge/split provenance and dated scope; update affected edges. |
| Correction, withdrawal or retraction notice | Capture the exact authoritative event and affected revisions; review downstream summaries and release visibility. |
| Source outage or removed URL | Record access failure separately from publication status; preserve permitted history and unresolved current state. |
| Source terms or material license change | Review exact affected uses and projections; withhold or remove affected material when required. |
| Taxonomy/schema change | Version semantics, migrate explicitly and obtain consumer acceptance. |
| New independent reproduction | Link the actual assessment and scope without automatically upgrading unrelated claims. |

## Freshness

Follow the accepted upstream distinction: version-pinned facts do not expire through an invented time-to-live, while current-state facts carry actual access dates. A new version, correction, rights event or selected-input change is a reason to reassess the affected scope. Source-access dates do not overwrite scholarly publication dates.

Propose source-specific monitoring cadence only after permitted access, expected change behavior, operational cost, rate limits and ownership have been assessed. Record it as a decision rather than presenting an arbitrary interval as policy. Do not schedule automation merely by adding this document.

## Correction workflow

1. Triage the report, target record/revision, primary evidence, sensitive content and likely downstream impact.
2. Record what was observed and what remains an allegation or hypothesis. Broken access alone does not prove withdrawal or retraction.
3. Restrict affected public projections when the applicable rights or integrity rule requires it; keep unrelated work available within its permitted scope.
4. Review the correction, identity merge/split or event with an independent reviewer and the affected consumer when material.
5. Produce a versioned correction and update release/graph references. Preserve permitted prior evidence and redirect history.
6. Read back the actual affected outputs and record the result. A merged correction file does not prove that a downstream cache changed.

Private security or personal-data issues follow [SECURITY.md](../SECURITY.md). Avoid copying the sensitive content into the public correction log.

## Operational measurements

Track unresolved identity candidates, citation mismatches, unavailable sources, rights-unknown fields, review queues, correction backlog, pending handoffs, per-stratum coverage and eligible release counts. Define each measurement's scope, population, date and collection method. A lower error count can reflect less review rather than better quality; report review volume and denominators alongside it.

Keep scholarly quality metrics separate from contribution recognition. Do not rank authors, institutions or papers as trustworthy from citation volume, issue throughput or board completion percentages.

## Reconciliation and recovery

Reconcile the canonical planning records with live issue IDs, native parents, blockers, membership and Project field/view configuration through readback. Never reset existing assignees, status or concurrent edits from a stale planning file. Actual delivery state belongs to GitHub; stable scope belongs in the versioned plan.

Rebuild generated docs deterministically and rerun validators after input changes. Preserve immutable release metadata, permitted provenance and decision history sufficient to explain a release. Backups must respect source-use limits and exclude secrets. A recovered working tree is not evidence that remote configuration or a deployment recovered.

## Ownership transitions

Record actual native assignment changes and maintainers' accepted responsibilities. Transfer open decisions, source agreements, consumer dependencies and correction obligations explicitly. Organization administrators manage access under team policy; do not add individual grants or team members through editorial convenience.

If a source or capability cannot be maintained, record the scope reduction, retain eligible historical context, update coverage denominators and notify the relevant receiving work through its authorized project process. Do not leave a discontinued capability described as operational.
