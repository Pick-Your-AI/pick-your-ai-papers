# Scholarly identity and citations

Identity is a research result with provenance. The proposed scholarly contract is version `0.1.0`, separate from the frozen Pick Your AI builder contract. The concrete pilot shape is [scholarly-record.schema.json](../schemas/scholarly-record.schema.json); this document also describes planned identities that may require later reviewed schema versions.

## Work, revision and manifestation

| Identity | Meaning | Required care |
| --- | --- | --- |
| Work | The intellectual research contribution used to group supported related records. | Similar titles or authors are candidate matches, not proof of sameness. |
| Revision | An exact source-versioned form, such as an arXiv `v2`. | Claims and summaries attach to this version. A new revision can change them. |
| Manifestation | A particular publication/source appearance, such as a journal article or conference proceedings record. | Distinct identifiers, dates, title variants, licensing and review evidence may apply. |

A preprint and a published article can be related without being textually identical. Record the primary evidence for their association. A DOI resolver result or arXiv-issued DOI is not automatically a publisher-DOI association. Keep unresolved links as candidates, and preserve originals when a merge/split decision changes the grouping.

Internal IDs must be stable, namespaced and independent of filenames or titles. Preserve external identifiers exactly as sourced alongside a documented canonical comparison form. Store identifier kind and issuer; DOI, arXiv, PMID, OpenAlex and other identifiers are not interchangeable. Do not invent missing IDs. A stable project ID can exist while external resolution remains incomplete.

## Citation verification

For each citation check record the target, exact landing/source URL, identifier/version, title, author list/order, primary publisher/archive, actual access date, observed fields and limitations. A locator may refer to a metadata field or a manuscript section/table; the material may be cited without being copied.

The pilot's `citation_verification: metadata_checked` means the stated metadata was inspected. It does not assert peer review, scientific validity, author disambiguation, exact claim support, a successful DOI relation or publication permission. Preserve these limits in every consumer display.

Each stored check binds its declared field observations through `observed_fields_sha256`; accepted reviews bind their targets and relevant evidence dependencies through `target_sha256`. See [evidence manifests](../evidence/README.md#content-bound-checks-and-reviews) for canonicalization and scope. These digests make stale checks or approvals detectable when content changes. They do not authenticate the external source, establish that a person reviewed it or certify the observation's truth.

An unversioned arXiv link identifies a source endpoint whose current rendering can change. Use exact version links for a pinned assertion and retain the discovery URL separately. If a source exposes no stable version, preserve a dated observation and permitted evidence fingerprint; do not manufacture an immutable identity.

## Authors and organizations

Preserve the source's author spelling and order. Resolve people using explicit evidence such as a source-associated persistent identifier and corroborating public records. Name similarity, shared email domains or a common affiliation are insufficient alone. The pilot retains unresolved author identity with a nullable entity ID.

Affiliations are assertions with source, role and time context. An affiliation printed on a historical paper does not prove current employment or endorsement. Model laboratories, universities, companies, consortia and organizational units separately where evidence supports that distinction. Parent organizations and laboratory memberships can change over time.

Do not publish private contacts, infer sensitive personal attributes, scrape private profiles, or contact people merely to complete a record. Record contributions and collaboration only at the granularity supported by public evidence.

## Dates and publication events

Keep first submission, revision, acceptance, online publication, issue/proceedings publication, correction, withdrawal and retraction dates distinct. Record precision: an evidenced year is not January 1; a month is not its first day. Import date and access date are operational dates and never replace scholarly dates.

A publication-state change must cite the relevant publisher/archive/author notice and its scope. Do not infer a retraction from a broken URL, an inaccessible PDF or a social-media allegation. Preserve an unresolved report for review without repeating it as established fact.

## Deduplication and citation graph

Candidate matching may use exact IDs, titles, authors, dates and source-declared relations, but accepted merges need a logged rationale. Retain aliases, redirects, superseded IDs and rollback evidence. Do not merge revisions or manifestations just to reduce duplicates.

Namespace existing evidence pointers as repository + path + exact commit + local evidence ID. A local `Q5`, `E-F1` or `T22` is not globally unique. Keep upstream technical ownership and its original evidence interpretation.

The `cites` relationship says that a particular source includes a citation to a target; it does not say that the source supports, reproduces or endorses the target. Citation counts must record source, date and counting method and must not become scientific-confidence scores.
