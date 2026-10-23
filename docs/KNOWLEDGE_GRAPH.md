# Scholarly knowledge graph

The graph is a proposed research model and validated record format. This package does not deploy a graph database, query API, embedding service or search index. [graph-edge.schema.json](../schemas/graph-edge.schema.json) defines the presently implemented edge intake; broader relationships below are planned extension points requiring schema and consumer review.

## Entity boundaries

Use distinct identities for work, revision, manifestation, author, organization, venue, method, claim, experiment, artifact reference, reproduction assessment, correction event and open question. Reference external model/dataset/application entities by their owning repository and immutable contract/version when available. Do not create duplicate technical records merely to make graph endpoints local.

Each entity has a stable identity, source observations, revision history and an explicit editorial/publication state. Preserve unknown and provisional identity matches. The graph must be able to express incomplete knowledge without inventing an edge.

## Relationship semantics

| Relationship family | Assertion and boundary |
| --- | --- |
| Revision / manifestation of | A supported identity relation; it does not establish equivalent text or conclusions. |
| Authored by / affiliated with | A source-backed contribution or dated affiliation; not current employment or organizational endorsement. |
| Cites | A source includes a reference to the target; not evidence that it agrees with the target. |
| Describes / introduces / uses method | A source-scoped method relation; precedence and novelty claims require separate evidence. |
| Reports claim / evaluated in | A claim and experiment are tied to their exact revision and protocol; author reporting remains explicit. |
| Uses dataset / benchmark / model / code | An exact referenced artifact and role; availability, license and reproducibility remain separate. |
| Supports / contradicts | A reviewed claim-level interpretation under compatible scope; neither follows automatically from text similarity. |
| Reproduction of | A declared target and actual assessment scope; attempts and outcomes are explicit. |
| Corrects / withdraws / retracts / supersedes | A sourced event or revision relationship; retain the original and the notice. |
| Open question / proposed follow-up | An attributed unresolved question, distinct from a verified finding. |

## Edge evidence

An asserted edge needs an ID, predicate, subject and object identities, source reference, exact locator, applicable revision/time scope, observation date, rationale or quoted-field description, evidence status and review/publication state. Use an original paraphrase when describing supporting text. A source URL without a relevant locator is insufficient for a precise scientific relation.

Some endpoints can remain external unresolved references, but that uncertainty must be typed and cannot pass a publication rule that requires resolved identity. Do not add a dummy entity or use an empty identifier to satisfy validation. An absence of edges means no admitted relation was recorded, not that no relationship exists.

Separate asserted edges from computed navigation links. A shared keyword may produce an editorial “related topic” suggestion; it cannot silently create `supports`, `reproduces`, `authored_by` or `same_as`. Any algorithmic suggestions must preserve method/version and be reviewed before factual admission.

The implemented intake requires `corrects`, `withdraws` and `retracts` to connect an admitted integrity-notice node to an affected revision, with a matching event, scoped authoritative source check and handling review. Ordinary bibliographic metadata cannot support those predicates. A `reproduces` edge requires a scoped independent experimental record; a citation or proposed future replication is insufficient. The current pilot contains neither type of scientific assertion.

## Integrity and versioning

Validate endpoint kinds, known predicates, source references, duplicate identity, revision consistency and required evidence. Reject self-relations where their semantics disallow them. Revision ancestry and taxonomy hierarchies must be acyclic; citation graphs can legitimately contain cycles, including later manifestations, and are not delivery-blocker graphs.

Do not require every graph relation to be symmetric or transitive. A paper reproducing a particular experiment does not establish all claims in its target paper. A `supports` relation is not inherited by every citation ancestor. Collaboration edges derived from coauthorship need explicit derivation and date scope.

Retain prior assertions and correction events when evidence changes. Withdraw affected publishable projections without erasing permitted historical provenance. Record merge/split redirects and the release in which they changed. Rights restrictions may limit retained material even when identity history remains useful.

## Cross-repository handoff

Every external reference must identify the producer, artifact ID, exact version/commit, relationship role, reviewed fields and acceptance status. Published edges may reference only eligible material under an agreed consumer contract. The website should display evidence provenance and uncertainty adjacent to significant claims; no client may upgrade a proposal through visual styling.

The initial pilot is deliberately modest: checked bibliographic metadata and traced upstream references. It does not include invented experimental claims, citation counts, resolved author profiles or a reproduced-results graph.
