# Scientific and research-object taxonomy

The taxonomy is a proposed navigational vocabulary for the literature index. It is independent of the upstream builder's 29 component kinds. Classification does not establish scientific merit, a product capability, regulatory suitability or a source-use grant.

## Orthogonal classification axes

| Axis | Intended values or distinctions |
| --- | --- |
| Research object | Scholarly work, revision, publication manifestation, author, organization, venue/event, method, claim, experiment, artifact reference, reproduction assessment, correction event, open question. |
| Publication type | Preprint, journal article, conference paper, workshop paper, technical report, thesis/dissertation, book/chapter, survey/review, position/perspective, artifact/data/software paper, correction/withdrawal/retraction notice. |
| Research method | Theoretical analysis/proof, empirical controlled study, observational study, benchmark/dataset construction, simulation, systems/engineering evaluation, qualitative/user study, case study, systematic/scoping review, meta-analysis, position/proposal, mixed or unclassified. |
| Research task | Explicit task tags such as classification, retrieval, generation, forecasting, planning, control, detection, estimation, ranking or reasoning. Preserve source-specific definitions. |
| Modality | Text, image, video, audio/speech/music, tabular, time series, graph, spatial/3D, biological/chemical, multimodal or other evidenced modality. |
| Scientific state | Proposed, author-reported, disputed, independently assessed, corrected, withdrawn or retracted only when exact status evidence exists. |
| Access and rights | Availability and each permitted use; never a single “open” flag for all material. |

A survey can be a conference paper; a preprint can report a theorem; a model paper can include a benchmark. Axes are multi-valued where appropriate. Publication type and review status are separate. An unclassified record remains visible to curators without pretending that its classification is complete.

## Domain coverage

The initial coverage program spans foundational machine learning; statistical and probabilistic methods; optimization and learning theory; neural architectures; representation learning; language and information retrieval; computer vision and graphics; speech, audio and music; multimodal learning; generative modeling; reinforcement learning and decision making; agents, planning and tool use; robotics and embodied intelligence; graphs and relational learning; causal inference; time series and forecasting; scientific/biomedical AI; human–AI interaction; interpretability; evaluation and reproducibility; privacy, security, safety and alignment; fairness and societal analysis; and efficient/distributed/edge AI systems.

These are coverage strata, not a claim that every field has been researched. Domain boundaries and synonyms belong in versioned taxonomy decisions. Applied fields such as health, education, law, finance, industry and accessibility may have cross-cutting tags but do not confer professional suitability.

## Vocabulary rules

Use stable machine identifiers distinct from display labels. Keep a preferred label, definition, aliases, parent/broader links, related terms, provenance and change history. A tag can have multiple broader concepts; represent the classification graph explicitly and reject cycles in hierarchical broader/narrower relations. Related-to links are not hierarchy.

Map external taxonomies by source/version and relation: exact, close, broader, narrower or unresolved. Do not equate similarly named categories automatically or import licensed taxonomies without a source-use decision. Record a paper's source-assigned category separately from the project's editorial classification.

For each assignment, record the exact work/revision, assigned terms, evidence or original editorial rationale, assessor and review state. A term describing a paper's subject does not mean the paper demonstrated that capability.

## Coverage denominator

[planning/coverage-matrix.json](../planning/coverage-matrix.json) links scope dimensions to concrete work packages. It records planned coverage, not a literature census.

For each evaluated stratum, define a source population or query frame, its time window, included object types, deduplication method, access limits, known missing sources and count date. Report discovered, identity-resolved, source-checked, evidence-reviewed and publication-eligible counts separately. Work/revision/manifestation counts must not be mixed.

When the denominator is unknown, report counts and gaps rather than a completeness percentage. When sources overlap, use a documented deduplicated union or state that counts are not additive. Maintain language, geography, venue, historical-era and negative-result gaps so “near-exhaustive” does not silently mean English-language recent preprints only.

## Change control

Propose vocabulary changes with examples, migration effects, affected filters and backward compatibility. Preserve obsolete labels as historical aliases where appropriate. A classification disagreement needs an editorial decision with rationale, not silent record deletion. Website consumers must accept changed semantics before a release relies on them.
