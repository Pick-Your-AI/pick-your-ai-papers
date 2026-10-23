# Source rights and publication eligibility

This document defines conservative project admission rules. It records no new grant from an archive, publisher, author, metadata provider or dataset owner. Exact source terms and intended uses require their own dated evidence and review.

The canonical organizational inputs are the [accepted source policy](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/research/T0-configuration/catalog-data-sources.md), [source-use research](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/research/market/rights-validation.md), and [publication eligibility handoff](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/docs/PUBLICATION_ELIGIBILITY_HANDOFF.md). Their bounded decisions do not automatically cover new scholarly sources or new operations.

## Default material boundary

Store project-authored summaries, scoped bibliographic metadata observations, and permitted links. Do not copy article abstracts, paywalled or restricted manuscripts, copyrighted figures/tables, supplementary files, private datasets, raw crawls or credentials into this repository merely because they are reachable.

The repository MIT license covers original project software and documentation. It does not relicense third-party titles, metadata compilations, papers, code, datasets, figures or publisher services. A paper license does not automatically cover its code or data; an open-source code license does not automatically cover a paper or source compilation.

## Observed arXiv metadata basis — 2026-10-22

arXiv's [official license page, Metadata license](https://info.arxiv.org/help/license/index.html#metadata-license) states that its metadata uses CC0 1.0. Its [API terms](https://info.arxiv.org/help/api/tou.html) separately permit descriptive-metadata use and distinguish e-print redistribution, which depends on the applicable manuscript permissions. These primary pages were inspected on the session date above. The four seed records' factual bibliographic metadata can therefore be included as research proposals on that stated metadata basis; their short summaries are original project writing. No abstract, manuscript, figure, code or dataset content was copied into those proposals.

Public Git itself distributes the committed material. Here **withheld** means withheld from a production catalog release, not private or confidential. Remaining per-field/use review and independent editorial acceptance must still be recorded; this pending process does not mean that arXiv's observed metadata license is unknown.

The seed-specific [source rights notes](../sources/RIGHTS_NOTES.md) preserve this distinction between the observed metadata basis and the pending production field/use decisions in the machine-readable matrix.

For a future legacy API adapter, the inspected terms require at most one request every three seconds and one connection at a time, across controlled machines. Refresh and enforce applicable access limits before operation. This package performed no bulk ingestion and confers no arXiv endorsement.

## Decision unit

Every rights decision identifies:

- Exact source/service and source revision or dated terms observation.
- Specific material and field scope, including derived summaries and mixed-source fields.
- Intended operation, audience, destination and commercial/public context where relevant.
- Governing primary terms/license/permission evidence and actual access date.
- Decision state, basis, conditions, attribution/notice requirements and restrictions.
- Reviewer/decision receipt and unresolved ambiguities; no invented reviewer or acceptance.
- Effective interval, revocation/change events and affected records/releases where applicable.

The implemented record format is [source-rights.schema.json](../schemas/source-rights.schema.json), with current observations in [sources/rights.json](../sources/rights.json). Unknown applicable rights are explicit and block the affected production projection. They do not mean that a legal prohibition has been proven or cancel a separately observed metadata license.

## Operations are independent

| Operation | Review question |
| --- | --- |
| Automated retrieval | May the intended interface, authentication, rate and volume be used for this project and purpose? |
| Internal research | May the exact material be retained or analyzed in the intended environment? |
| Public/commercial display | May the selected fields or original derivative summary be shown to the intended audience with the required conditions? |
| Bulk redistribution/export | May the material be included in downloadable snapshots, APIs, archives or downstream redistribution? |

Permission for one operation does not imply the others. A public link, API key, subscription, robots instruction, attribution string, source citation or checksum is not a complete substitute for the relevant source-use decision. Maintain publisher content, API responses, metadata compilation, abstract/full text, figures, code and datasets as distinct material boundaries.

## Mixed-source records and publication projections

Map each published field to its provenance and use decision. A licensed identifier from one source does not clear a performance assertion or abstract imported from another. Define the precise public projection and its notices; omit uncleared fields rather than marking the entire mixed record approved.

Original summaries still need accurate citations and review of their source-use context. Do not represent a generated paraphrase as author text or use it to hide extensive copying. Keep quotation and manuscript-text admission out of the default pilot.

Publication eligibility requires an identity-valid record, supported citations, editorial acceptance, all applicable source/use conditions, an immutable release manifest, and receiving-consumer acceptance. The current pilot remains `publication_status: withheld` from production release while those project reviews are incomplete. The metadata-license observation above supports inclusion of the bounded research proposals; it does not claim a completed independent editorial review or consumer acceptance.

## Changed terms, corrections and takedowns

Record the actual notice and its date separately from the date discovered. Identify affected fields, records, graph edges, exports and cached releases. Suspend the affected public projection where required while preserving permitted non-sensitive decision history. Do not assume that old publication permission automatically continues or that a changed website invalidates all historical evidence.

Route rights ambiguities through the appropriate organizational review. A maintainer cannot invent author consent, a publication license or a legal determination. An unresolved source may remain in private or withheld research only within its permitted scope; continue independent work on other sources.

## Automated gate limits

The validator can require known decisions, conditions, reviewers and consistency; it cannot authenticate the truth or legal sufficiency of those fields. The [content-bound review format](../evidence/README.md#content-bound-checks-and-reviews) invalidates a stored approval when its target or relevant terms, source observations and affected records change. Its digest is an integrity check, not a signature, permission grant or proof that a reviewer acted. A fabricated permission record remains false even if it passes schema validation. Review the exact source, scope and receipt before release, and keep the actual decision link in the manifest.
