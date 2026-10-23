# Existing references and consumer boundaries

Inspected 2026-10-22 (America/New_York). This is a bounded source and architecture audit, not an exhaustive scientific review or permission assessment. No existing repository was modified.

## Snapshot and method

Research default-branch commit: `da3d320e239a6d37a933963230f2eb3643d1d5c4`. Website default-branch commit: `f47f3ebaeb599d49ccd58eaf29994890d9f54d55`. Fifteen research files and three website files were retrieved through the GitHub connector. Their actual blob hashes match those commits' recursive trees; immutable file manifest in `../evidence/upstream-inspection.json` record the paths, hashes and immutable URLs. Four requested directories were inventoried at their top level. No recursive review of every research document is claimed.

The selected research files contain URLs for **61 distinct arXiv work identifiers** after removing revision suffixes, detected with `arxiv.org/(abs|html|pdf)/<identifier>`. This denominator describes this sample only. It excludes bare textual identifiers, non-arXiv scholarship and unsampled files. The source extraction is summarized in `../evidence/upstream-inspection.json`; the existing source files remain upstream. Automated extraction alone establishes neither bibliographic accuracy nor relevant scientific support.

## Existing data that must remain owned upstream

| Area | Observed baseline | Boundary |
| --- | --- | --- |
| T1 | `model-research-inventory.json`: 248 candidate records, 55 overlapping task-family tags; `model-research-sources.json`: 189 source groups | Both explicitly remain `in_progress`; inventory format is `research-notes-not-catalog`. Model identity, route-specific performance, entitlement and component facts stay with T1. |
| T5 | Dataset and fine-tuned-model decision records cite dataset documentation, deduplication, contamination, training methods and safety/forgetting studies | The papers index may link publication revisions and extracted claim references; it does not replace `training_dataset` or `fine_tuned_model` entities, dataset rights decisions or technical recommendations. |
| T6 | `evaluation.md` contains extensive paper, benchmark, judge and software references; `evaluation-catalog-qualification.md` documents 101 bounded source rows: 34 supported rows map to 33 distinct proposals, 47 remain notes, 20 are outside that intake | These counts are the upstream qualification's declared snapshot, not fresh evaluation results. Every proposal remains `unverified`; source and artifact review did not execute benchmarks. |
| Market | 39 competitor records, 58 source records, 1,872 feature cells: 121 `Documented`, 1,751 `Unknown` | Market methods and benchmark-comparability decisions remain upstream. Unknown is not unsupported. Existing citation index is a historical source map, not universal renewed verification. |
| Website | Frozen contract 1.0.0 pinned to `d4bdca479f78439b3b98e7418b37acbaccbaa63c`; fixture and HTTP provider interfaces, immutable artifact selection and runtime response validation | No native scholarly-work contract currently exists. New literature data needs a separately versioned contract, consumer acceptance and publication-gated immutable release, not additions silently inserted into frozen builder v1. |

Source links and blob hashes are recorded in `../evidence/upstream-inspection.json`. Primary entry points:

- [T1 source register](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/da3d320e239a6d37a933963230f2eb3643d1d5c4/research/T1-model-selection/model-research-sources.json)
- [T5 dataset decision record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/da3d320e239a6d37a933963230f2eb3643d1d5c4/research/T5-training-fine-tuning/training-dataset.md)
- [T5 fine-tuned-model decision record](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/da3d320e239a6d37a933963230f2eb3643d1d5c4/research/T5-training-fine-tuning/fine-tuned-model.md)
- [T6 evaluation](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/da3d320e239a6d37a933963230f2eb3643d1d5c4/research/T6-deployment-operations/evaluation.md)
- [T6 qualification](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/da3d320e239a6d37a933963230f2eb3643d1d5c4/research/T6-deployment-operations/evaluation-catalog-qualification.md)
- [Market sources](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/da3d320e239a6d37a933963230f2eb3643d1d5c4/research/market/sources.json)
- [Website integration](https://github.com/Pick-Your-AI/pick-your-ai-website/blob/f47f3ebaeb599d49ccd58eaf29994890d9f54d55/docs/DATA_INTEGRATION.md)

## Evidence and identity patterns

T1 source groups contain stable local IDs, publisher, one or more exact URLs, access date, evidence grade, observer group and an explicit checking limitation. Decision-record evidence tables further qualify source revisions, claim scope, measured/published/estimated status, conditions and confidence. A bibliography alone cannot certify a field. Source IDs such as `Q5`, `E-F1` and `T22` are document-local and must be namespaced by repository/path/revision before graph ingestion.

Maintain at least these separate objects: scholarly work; publication/preprint manifestation; exact revision; author identity; date-bounded affiliation; institution; research method; dataset identity/version; benchmark protocol; code/model release; reported claim; experiment/run; independently assessed reproduction; source capture; correction/withdrawal/retraction event. `cites` is not `supports`, association is not authorship, public code is not reproducibility, and citation count is not confidence.

The upstream `Independent measurement` grade can describe a paper evaluating other parties' models. It does **not** mean Pick Your AI independently reproduced that paper. A literature record therefore needs separate source-role, claim-origin and reproduction fields rather than copying the upstream grade into a reproduction badge.

## Publication and scientific-status gates

The [publication eligibility handoff](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/da3d320e239a6d37a933963230f2eb3643d1d5c4/docs/PUBLICATION_ELIGIBILITY_HANDOFF.md) clears no complete existing catalog or pricebook artifact. Its dated source-use decisions are narrow: for example, Harness Bench paper v2 has a different scope from repository tasks/trajectories. Code licensing does not license paper figures, datasets or publisher metadata. Mixed-source records cannot inherit their most permissive source's grant.

Preserve exact retrieval/display/export/redistribution decisions for each source, field, artifact and intended use. A public URL, available PDF, DOI, open-access indicator or model-code license is not a blanket permission. Keep unclear rights as unknown and withhold publication until review. Default proposals can contain minimal bibliographic metadata, original summaries and permitted links, never copied abstracts, figures or full text by assumption.

Separate project delivery status, editorial publication eligibility, scientific publication status, citation checking and reproduction status. A completed issue does not make a study peer reviewed, current, reliable, rights cleared or independently reproduced. Correction/retraction status needs a dated authoritative check; absence of a notice in a sampled source is not a universal negative.

## Existing coordination records (live readback)

| Record | State | Assignees | New papers repository relationship |
| --- | --- | --- | --- |
| [research #40](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/40) | Closed | zwright8, tynamite | Completed cross-domain schema/compatibility research; preserve frozen v1 and seek explicit versioned successor/consumer decisions when needed. Do not reopen the completed research merely for the new repository. |
| [research #41](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/41) | Closed | tynamite, PUSHINGSQUARES | Canonical source/freshness/evidence policy input. No blanket TTL: fixed revisions and changing current-state facts have different handling. |
| [research #60](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/60) | Closed | tynamite, appletechie | Completed bounded source-use research; no new scholarly-source permissions are implied. |
| [research #61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61) | Open | Mattycodes69, appletechie | Existing measured GPU-sizing work remains upstream. A paper quotation is not a replacement runtime measurement. |
| [research #62](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62) | Open | appletechie, PUSHINGSQUARES | Existing harness comparability work remains upstream. Immutable evaluated model/grader/run association is still missing; no replication is selected in its scoped desk result. |
| [website #15](https://github.com/Pick-Your-AI/pick-your-ai-website/issues/15) | Open | PUSHINGSQUARES | Existing real catalog/pricebook integration gate; all four original production criteria remain unchecked. Link it as a boundary/reference, not as proof a paper consumer exists. |
| [website #24](https://github.com/Pick-Your-AI/pick-your-ai-website/issues/24) | Open | PUSHINGSQUARES | Existing data-readiness epic still has catalog/pricebook, capacity and shared-build dependencies. New scholarly consumer work must be scoped separately without duplicating those outcomes. |

## Four primary-metadata pilot candidates

The following arXiv landing pages were actually inspected during this audit. Their identifiers, titles, author lists and revision dates were confirmed. This does not establish peer review, publication permissions, scientific accuracy or independent reproduction. The files in `../catalog/proposals/` store small metadata proposals and original scope summaries; all remain withheld from release pending rights/editorial review.

| Upstream local reference | Exact revision | Title | Revision date |
| --- | --- | --- | --- |
| T5 dataset `T22` | [1803.09010v8](https://arxiv.org/abs/1803.09010v8) | Datasheets for Datasets | 2021-12-01 |
| T6 evaluation `E-Q1` | [2104.08663v4](https://arxiv.org/abs/2104.08663v4) | BEIR: A Heterogenous Benchmark for Zero-shot Evaluation of Information Retrieval Models | 2021-10-21 |
| T5 fine-tuned model `Q5`; T6 evaluation `E-F1` | [2402.04249v2](https://arxiv.org/abs/2402.04249v2) | HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal | 2024-02-27 |
| T5 fine-tuned model `Q2` | [2405.09673v2](https://arxiv.org/abs/2405.09673v2) | LoRA Learns Less and Forgets Less | 2024-09-20 |

These are inputs for an eventual bounded pilot, not a scientifically verified catalog. The source pages expose arXiv-issued DOI identifiers separately from any publisher DOI; do not conflate the two. Dates of first submission and revision are separate values.
