# Evidence manifests

`research-evidence.json` contains four bibliographic checks performed during setup. Reviews, experiments and publication receipts are empty. `research-events.json` is empty because correction/retraction status has not been assessed; it does not assert that no notices exist. `upstream-inspection.json` records exact upstream snapshots, blob hashes, selected-file scope and count qualifications.

Manifests refer to permitted public evidence. Do not store private correspondence, credentials, full article text, copyrighted figures, datasets or model binaries. Automation checks consistency and explicit evidence links; reviewers must inspect source meaning and the scope of any permission.

## Content-bound checks and reviews

Each matched source check records `observed_fields_sha256`, the SHA256 of canonical JSON mapping its observation pointers to the actual stored values. This prevents a changed title, author list, identifier or integrity status from retaining an unchanged check. Canonical JSON uses sorted object keys, compact separators and UTF-8 with non-ASCII characters preserved. The digest binds the recorded observation; it does not authenticate an external source or prove the checker was correct.

Each accepted review records `target_sha256`, computed by `review_scope_sha256(kind, target_id, documents)`. A record review binds the full record and related source observations, rights decisions, citation/integrity checks, experiments, integrity events and owned graph nodes/edges. A rights review binds its decision, terms-source observations and every affected record snapshot. An integrity review binds its event, authoritative source, scoped checks and affected record snapshot. A reviewed scientific edge binds that exact edge, endpoints and their evidence and record snapshots. Claim content is included in its record snapshot. Review objects are excluded to avoid digest cycles; their IDs remain in target content. Changing a substantive value, term observation, right, status or projection requires a newly scoped independent review. A published record additionally needs an exact-byte publication receipt.

These are consistency controls, not cryptographic signatures or proof of a human review. Actual reviewer identity, independence, source meaning and execution evidence require the contribution and governance process. No actual approvals or experiments are present in this scaffold.
