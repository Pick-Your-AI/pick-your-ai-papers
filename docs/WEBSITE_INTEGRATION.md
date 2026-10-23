# Website integration contract

The existing [website](https://github.com/Pick-Your-AI/pick-your-ai-website) owns public pages, navigation, search interfaces, accessibility, SEO and production deployment. This repository prepares scholarly research and a proposed receiving contract. No website code or production data is changed by this package.

The website's existing [data integration](https://github.com/Pick-Your-AI/pick-your-ai-website/blob/main/docs/DATA_INTEGRATION.md) and [research mapping](https://github.com/Pick-Your-AI/pick-your-ai-website/blob/main/docs/RESEARCH_MAPPING.md) describe its builder consumer. The scholarly `0.1.0` proposals are separate; passing them through a builder component schema is not a valid integration strategy.

## Producer responsibilities

Supply stable work/revision/manifestation identities, original summaries, qualified publication metadata, explicit citation checks, source provenance, authorized field projections, correction history and documented unknowns. Export only records/fields that pass the exact release gate. Preserve all schema and source-policy versions used to decide eligibility.

An immutable release manifest should identify schema version, exact content hashes, producer commit, record and edge counts, excluded/withheld scope, rights decisions and notices, editorial acceptance, review receipts, provenance/date semantics and correction/revocation instructions. The initial [release manifest](../planning/release-manifest.json) is a planning record, not a public scholarly-data release.

## Consumer responsibilities

The website must validate the declared schema and hashes, enforce eligible projections and required notices, display uncertainty and exact version/source context, and reject unknown schema/status values safely. It must preserve source distinctions when caching, indexing, exporting or generating previews. A permitted display projection does not automatically permit a bulk-download endpoint or generated third-party snippets.

Keep original contributor summaries distinct from author abstracts. Cite the exact version behind a claim. Label preprint, peer-review status, publication events and reproduction state independently. A withdrawn or retracted record needs clear sourced context; an unassessed paper must not look independently verified because it appears in a polished card.

## Planned discovery behavior

| User need | Proposed consumer behavior |
| --- | --- |
| Find a topic, method or historical work | Search and filters based on versioned taxonomy and original summaries. |
| Follow an author or laboratory | Show resolved identities and dated affiliations with uncertainty preserved. |
| Compare experimental claims | Display eligible, protocol-qualified claims and limitations; no unsupported cross-protocol ranking. |
| Trace related artifacts | Link exact datasets, benchmarks, models and code versions through their owning contracts. |
| Inspect reliability | Show citation check, editorial review, rights and reproduction states separately. |
| Understand changed evidence | Surface correction/withdrawal/retraction events and affected revisions. |

These are backlog requirements, not implemented features. Recommendation, embedding or graph-ranking methods need their own evaluation and rights review; citation counts alone do not measure scientific quality.

## Acceptance tests and failure states

The receiving owner must exercise a bounded eligible snapshot and reject malformed identities, unsupported schema versions, unresolved required endpoints, absent rights decisions, disallowed fields, unaccepted records and contradictory status combinations. Synthetic fixtures stay visibly synthetic and cannot become production examples.

Test missing source metadata, failed refresh, disputed claims, corrected identities, withdrawn permissions and source removal. A failed fetch should preserve permitted historical provenance and show current uncertainty; it must not silently treat old facts as current or replace them with demo data. Keep current published data separate from withheld proposals and diagnostic fixtures.

## Release and rollback

Obtain actual receiving acceptance for the exact contract and projection before enabling public publication. Preserve a release pointer that can be rolled back independently of research notes. Rights or correction events can require field-specific suppression across pages, search indexes, caches and exports, not merely a new README note.

Record the accepted consumer commit and deployment evidence only when they exist. Website #15/#24 remain their owners' work; creating this plan or a local passing validator does not satisfy them.
