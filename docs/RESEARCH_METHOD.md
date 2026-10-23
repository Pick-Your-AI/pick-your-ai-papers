# Scholarly research method

This method adapts the organization's [research method](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/docs/RESEARCH_METHOD.md), [submission workflow](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/docs/RESEARCH_WORKFLOW.md), and [accepted source policy](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/research/T0-configuration/catalog-data-sources.md). It defines the papers repository's proposed intake. It does not alter the upstream frozen builder contract or confer scientific acceptance.

## Define the question before collecting records

Each work package states the reader decision, population, time span, publication types, domain/task boundary, search method, source set, exclusions and expected deliverable. Record the actual query or selection procedure, date, filters, source version and access limitations. A convenient set of returned results is a sample; do not call it a complete population without an independently justified denominator.

Start with existing organization references. Preserve their repository, path, commit, source-local evidence ID and acceptance scope. A reference found upstream is a discovery input; it is not proof that the cited metadata is current or its scientific assertions were reproduced.

## Intake sequence

1. **Discover:** record candidate URL/identifier and discovery source. Preserve incomplete candidates in notes rather than filling missing required fields.
2. **Resolve identity:** distinguish work, exact revision and manifestation; check title, author order, identifier assignment and typed dates against primary records. Unresolved associations remain explicit.
3. **Inspect source:** record actual access date, access result, exact location and the fields observed. A failed fetch is not a successful source check.
4. **Summarize originally:** describe the research question and scope in project-authored language. Do not paste abstracts or manufacture findings to make a record useful.
5. **Extract bounded assertions:** identify what the authors claim, which version contains it, and experimental conditions or assumptions. Keep summaries and scientific assertions distinct.
6. **Assess evidence and rights separately:** classify claim support, limitations, disputes and reproduction state; review each intended source-material use independently.
7. **Review:** obtain identity/citation, scientific/editorial and rights review appropriate to the material. Record actual reviewer, commit and decision scope.
8. **Hand off:** submit eligible records through an immutable versioned release only after the receiving owner accepts the contract and presentation requirements.

## Required evidence packet

| Question | Record |
| --- | --- |
| What was observed? | Exact fact or assertion, preserving whether it is author-reported, externally measured, inferred or unknown. |
| Where? | Primary URL, source ID, revision and section/table/equation or metadata field locator. |
| When? | Actual access date and separately typed publication/revision/event dates. |
| Under what conditions? | Applicable model/code/data versions, task, split, metric, hardware, controls and scope. Missing items remain unknown. |
| With what support? | Evidence grade, confidence rationale, limitations, conflicts and independent evidence when present. |
| May it be used? | Exact field/material, intended operation, governing terms evidence, conditions and review status. |
| What is unresolved? | Named follow-up issue, required expertise and missing input; native assignee only after accepted ownership. |

## Evidence grades and confidence

Retain the organization's four claim grades: **Primary documentation**, **Vendor claim**, **Independent measurement**, and **Estimate**. In a scholarly setting, an author's experimental assertion remains an author-reported claim even if the work evaluates another vendor's model. Preserve its original upstream grade and record the narrower interpretation; never silently recast it as a Pick Your AI reproduction.

Citation verification answers whether an identifier, title, revision or relationship was checked. Evidence confidence describes support for a particular assertion. Reproducibility records what was attempted and observed. Scientific validity is an explicitly scoped assessment. These states cannot be substituted for one another.

Confidence needs a reason: primary-source proximity, exact revision match, adequate method detail, independent corroboration, uncertainty and known conflicts. A numeric score, journal reputation, citation count or model-generated summary is not a sufficient reason. Unknown is a valid result.

## Conflicts, exclusions and negative evidence

Retain competing assertions and their sources. First reconcile normalization and identity, then compare eligible scope, exact revision/effective date, and authority for the fact type. A newer unrelated experiment does not refute an older experiment under different conditions. Record the deciding reasoning and unresolved disagreement.

Absence from an explicitly complete source can support a bounded exclusion; absence from a search result or unmarked list cannot. A reproduction that was never attempted, an inaccessible artifact and a failed reproduction are different outcomes. Include negative and inconclusive results when their provenance and scope qualify.

## Completion and validation limits

A research outcome is accepted only when its defined deliverable is reviewed, limitations and unknowns are recorded, structural checks pass, and required consuming-owner handoffs are actually accepted. Parent synthesis needs its children's completed outcomes and its own acceptance.

Offline checks can reject malformed identities, broken local references, invalid status combinations and unsupported release eligibility. They cannot read a paper on behalf of a reviewer, prove scientific truth, establish legal rights, or certify that a remote catalog or GitHub Project exists. The current pilot remains a withheld metadata proposal, not a scientific assessment.
