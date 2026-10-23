# Pick Your AI — AI Papers & Research Index

A proposed, source-linked scholarly directory connecting AI literature, authors, laboratories, methods, experimental claims, research artifacts, and corrections to the wider Pick Your AI ecosystem.

**Current state: the planning foundation is published on the [contribution branch](https://github.com/Pick-Your-AI/pick-your-ai-papers/tree/contrib/papers-bootstrap/foundation) and submitted in [PR #166](https://github.com/Pick-Your-AI/pick-your-ai-papers/pull/166).** Its [recorded CI run](https://github.com/Pick-Your-AI/pick-your-ai-papers/actions/runs/39905405514) passed at head `20435598`; the PR's latest head and checks establish later publication results.

[Project #9](https://github.com/orgs/Pick-Your-AI/projects/9) contains **165 issues**—one program, 20 epics and 144 work packages—with **164 internal native parents, 270 blockers, 17 controlled fields and 2,805 verified values**. All eleven saved views and Project access roles have dated readbacks; native Assignees are empty. [Program #1](https://github.com/Pick-Your-AI/pick-your-ai-papers/issues/1) has native parent [research #509](https://github.com/Pick-Your-AI/pick-your-ai-research/issues/509).

Repository team access and rule saves remain blocked by GitHub's **Confirm access** gate. Independent latest-push approval, merge, default-branch verification and Foundation acceptance remain open.

Four metadata proposals remain withheld from production release. This repository does not operate a research search engine or claim an admitted scholarly catalog or independent reproductions. See [setup](docs/PROJECT_SETUP.md), [validation](docs/VALIDATION.md) and the [execution receipts](planning/github-receipt.json) for evidence and remaining work.

## What this repository owns

This repository plans and researches scholarly identities and relationships: works and preprints; exact revisions and publication manifestations; authors and dated affiliations; research organizations; methods and architectures; claim-level evidence; references to datasets, benchmarks, models, and code; independent reproduction assessments; correction and retraction histories; and open research questions.

Original summaries and permitted metadata and links are the default. A paper's presence means it has an explicitly recorded research status, not that its conclusions are correct. A checked citation, peer-review event, available code repository, and reproduced experiment are different observations.

The four bibliographic seed proposals use arXiv's observed CC0 metadata basis and original project summaries, as recorded in [publication rights](docs/PUBLICATION_RIGHTS.md). **Withheld** means withheld from production catalog release; it does not make a committed public-repository file private.

| Existing owner | Boundary preserved here |
| --- | --- |
| [pick-your-ai-research](https://github.com/Pick-Your-AI/pick-your-ai-research) | Canonical technical research, the accepted source/evidence policy, evaluation methodology, and frozen builder contracts remain upstream. |
| `pick-your-ai-datasets` | Dataset directory entities and their rights/version lifecycle are a separate proposed consumer/producer boundary; verify its live existence and contract before handoff. |
| `pick-your-ai-applications` | Application and service product facts remain outside scholarly work identity. Verify its live existence and contract before handoff. |
| `pick-your-ai-catalog-pipeline` | Shared acquisition, admission, and publishing machinery is a separate proposed implementation owner; no integration is implied by a name. |
| [pick-your-ai-website](https://github.com/Pick-Your-AI/pick-your-ai-website) | Public interface, search experience, accessibility, SEO, and receiving integration remain in the website repository. |
| [pick-your-ai-leaderboard](https://github.com/Pick-Your-AI/pick-your-ai-leaderboard) | Contributor recognition remains independent of scientific merit, citation counts, and evidence acceptance. |

## Start here

1. Read the [charter](docs/charter.md), [research method](docs/RESEARCH_METHOD.md), and [publication-rights policy](docs/PUBLICATION_RIGHTS.md).
2. Find the independently reviewable outcome in the [delivery plan](docs/DELIVERY_PLAN.md) and [rendered backlog](docs/BACKLOG.md). The canonical scope is [planning/project-backlog.json](planning/project-backlog.json).
3. Check the [coverage matrix](planning/coverage-matrix.json), [decision register](planning/decision-register.json), and [dependencies](docs/DEPENDENCIES.md). Coverage is measured against declared samples and strata, never an invented universe of all AI papers.
4. Prepare a note with [templates/research-note.md](templates/research-note.md). Keep incomplete facts and unresolved identities explicit. Submit structured proposals only when their fields are supported.
5. Run the checks below and follow [CONTRIBUTING.md](CONTRIBUTING.md). Passing checks is structural evidence; scientific review, permissions, and receiving acceptance remain separate.

## Repository map

| Location | Contents and limits |
| --- | --- |
| `planning/` | Stable program, epic, work-package, task and subtask identifiers; coverage, decisions and release gates. |
| `docs/` | Scholarly identity, taxonomy, knowledge-graph semantics, evidence, editorial, rights, integration and maintenance policies. |
| `schemas/` | Proposed independent scholarly intake schemas. These do not change the upstream frozen builder contract. |
| `catalog/proposals/` | Research proposals; publication eligibility is explicit and may remain withheld. |
| `sources/` | Source observations and material/use rights decisions, with dates and limitations. |
| `research/` | Original notes and upstream-reference inventory; incomplete findings are valid research. |
| `evidence/` | Sanitized receipts and small metadata manifests. External artifacts remain at their authorized source. |
| `templates/` | Research, identity, rights, reproduction, correction and handoff records. |
| `examples/`, `tests/` | Clearly marked examples and regression fixtures; never real scientific evidence. |
| `scripts/` | Offline validation, deterministic documentation generation and setup tooling. |

## Local validation

Use Python 3.12. Validation uses the standard library and needs no package installation:

```bash
python3 scripts/validate_plan.py
python3 scripts/validate_research.py
python3 scripts/render_docs.py --check
python3 scripts/build_project_spec.py --check
python3 -m unittest discover -s tests -v
```

The validators inspect the submitted files. They do not remotely verify citations, access permissions, experimental results, GitHub settings, or the absence of every possible secret. The explicit publication mode is a gate, not the ordinary scaffold test:

```bash
python3 scripts/validate_research.py --publication
```

It must reject withheld proposals. Do not weaken a gate or promote a record solely to obtain a passing command. No pilot is approved for public data delivery by this establishment package.

## Delivery and research status

The plan follows **Program → Epic → Work Package → Task → Subtask**. Independently reviewable program/epic/work-package outcomes become native GitHub issues and sub-issues; small tasks and subtasks are nested checklists. Stable IDs such as `PAPER-01.01.T1.S1` do not encode GitHub issue numbers. Native Assignees determine actual ownership.

The user's supplied enumeration ended during item `02.05`. The rest of the backlog is an explicit proposed decomposition of the mission, recorded in the decision register. It is not a recovered or verbatim continuation of missing instructions.

Publication, scientific validity, reproducibility, citation verification, rights, editorial acceptance, and delivery Status are independent. A Done setup issue would not make a paper verified, a source licensed, or the directory complete.

## Governance and license

The [organization contribution rules](https://github.com/Pick-Your-AI/.github/blob/main/CONTRIBUTING.md) and [Code of Conduct](https://github.com/Pick-Your-AI/.github/blob/main/CODE_OF_CONDUCT.md) apply. Repository access is team-based. No team or individual permission is created by these files. Changes to `main` require the organization's independent GitHub review process.

The prepared [bootstrap](scripts/bootstrap_github.py) defaults to a read-only plan. Its explicit apply mode can stage authorized setup when an authenticated administrative path is available, and must preserve independent approval. A scaffold PR may remain awaiting that approval. The [GitHub receipt](planning/github-receipt.json) records actual creation and readback; it must not be filled from intended configuration alone.

Original software and documentation use the [MIT License](LICENSE), consistent with the research repository. That license does not relicense cited articles, third-party metadata, figures, code, or datasets. See [SECURITY.md](SECURITY.md) for private reporting guidance and [publication rights](docs/PUBLICATION_RIGHTS.md) for source-specific boundaries.
