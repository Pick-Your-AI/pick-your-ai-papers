# Evidence and reproducibility

This repository records reproducibility evidence and its limits. It does not infer independent reproduction from available code, a cited result table, a paper's peer-review status, or passing catalog validation. No scientific experiment is reported as executed by the initial metadata pilot.

The upstream [T6 evaluation research](https://github.com/Pick-Your-AI/pick-your-ai-research/blob/main/research/T6-deployment-operations/evaluation.md) retains its methodology ownership. The existing [calibration #61](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/61) and [benchmark comparability #62](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/62) remain distinct research work; a papers directory must not close or duplicate them merely by citing their inputs.

## Separate the questions

| Question | Evidence required |
| --- | --- |
| Is the citation correct? | Primary metadata and exact revision were inspected. |
| What do the authors report? | A claim and source locator in the exact cited revision, with its conditions. |
| Are artifacts available? | Observed code/data/model references and access state; availability is dated. |
| Is the protocol sufficiently described? | An assessed reproducibility tuple with remaining missing inputs. |
| Was a reproduction attempted? | An actual attempt receipt identifying actor, scope, inputs, environment and execution evidence. |
| Did it reproduce the target result? | A predefined comparison criterion, observed results, uncertainty and a scoped independent assessment. |
| Is the result scientifically valid or generalizable? | A separate substantive assessment; agreement in one reproduction is insufficient for a universal conclusion. |

Preserve author reproduction, third-party reproduction and Pick Your AI reproduction as different provenance. Independently measured means independent in the stated relationship, not independent of every possible conflict of interest.

## Minimum experimental identity

Before presenting a comparison as qualified, identify the exact claim, paper revision, code commit, model artifact/configuration, dataset version and split, preprocessing, prompts/templates, evaluation harness/version, metric definition and direction, aggregation, random seeds and repetitions, hardware/runtime/precision, hyperparameters, controls, measurement date and uncertainty. Include known data leakage, contamination, selection and reporting limitations.

A missing input remains missing. Do not infer it from a later repository default or an unrelated benchmark. If a protocol legitimately does not use a field, record why it is not applicable. A copied configuration is a proposed setup until execution evidence exists.

## Comparison and attempt design

Define the comparison before examining favorable results. State the exact target, eligible population, intended tolerance, statistical method, confidence interval or uncertainty approach, stopping criteria, excluded runs and allowable deviations. Do not invent thresholds to declare a completed attempt successful.

For a controlled single-factor comparison, isolate one independent experimental change. Evidence identity fields may differ without being experimental controls; multiple changes to precision, prompt/template and model configuration are multiple controls even if bundled under one artifact name. Where protocols differ materially, show qualified separate results rather than a winner.

Record intended deviations and unforeseen failures. Operational inability to install an artifact is an access/execution result, not evidence that the paper's conclusion is false. Inconclusive and partial attempts are useful if honestly scoped.

## Status and result handling

The initial records use `reproducibility_status: not_attempted` and `scientific_validity: not_assessed`. Future status vocabulary must preserve planned versus attempted, author versus independent, successful versus inconclusive/failed/partial, and reviewed versus unreviewed. New states require schema and consumer review rather than arbitrary strings.

Attach outcome claims only to their actual experiment/assessment. A paper can contain reproduced and unreproduced claims simultaneously. Preserve negative evidence and independent disagreement without flattening all assessments into a single endorsement badge.

## Evidence retention and authorization

Use small sanitized manifests for code pins, logs, output hashes and environment descriptions where permitted. Keep raw datasets, weights, credentials and restricted artifacts at authorized locations. A hash must be computed from actual bytes or explicitly identified as a source-reported value; never fabricate one to satisfy a schema.

An approved research plan does not authorize paid compute, third-party account access, dataset acceptance, external contact or unsafe workload execution. The execution owner must establish those permissions for the bounded experiment. The papers repository can continue identity and methodology work while those inputs are unresolved.

Reviewers assess claim fidelity, experimental scope, numerical integrity, rights and independence separately. The release manifest must disclose which observations were actually executed and which remain proposals.
