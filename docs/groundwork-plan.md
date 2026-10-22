# Authorized groundwork

The learner selected Python CLI with explicit persisted JSON state and authorized file loading, structural validation, source provenance, hashes, storage, CLI and component tests. Their actual authorization is in this Codex session; no additional reasoning is attributed to them.

Completeness, packet readiness, business decisions, action queues and assessed snapshots remain disabled pending G1/G2 clarification and another learner review. The runtime does not import the combined audit archive or fetch network resources. A reviewed manifest and its single physical batch folder are the only stage inputs.

Implementation choices within the authorization: use standard-library CSV/date/hash/JSON handling plus jsonschema 4.26.0 with explicit date-format checking; preserve raw UTF-8 bytes and blank cells; retain provenance per occurrence even when identical content shares a blob; use immutable SHA-256 objects, a linked state chain and an atomic local HEAD replacement. Hashes establish byte integrity relative to the manifest, not authenticity or business authority. No credentialing status is added to evade missing facts.

Work sequence: implement and test the manifest boundary and byte-level loader; implement immutable JSON state and explicit-predecessor continuation; demonstrate structure/staging on batch-1 evidence only, plus isolated synthetic continuation/failure probes; update requirement coverage and show real receipts; make a local meaningful commit and inspect the genuine Entire checkpoint and associated transcript. Do not push. Stop assessed implementation if that capture check fails.

The store serializes writers with an exclusive lock. Ordinary exceptions before atomic HEAD replacement preserve the last state; orphan objects never become current automatically. Interrupted-writer lock recovery is manual after checking for a live writer. Power-loss/filesystem durability and protection against a malicious user replacing the entire trusted manifest/store are not claimed.

The audit archive intentionally contains later batches for source review. It is not a runtime input. Input preparation must select only the intended batch and preserve the archive's extracted-text provenance limitations; batch-1 staging cannot use future-batch records. Future expiry dates are facts already known at an earlier export and are not confused with later observation dates.

Published snapshot schema and business rules remain unchanged. A future approved implementation must separately add chronological business processing, the actual Skill, required run/verification reports, snapshots, semantic validation and learner review after batch 1.
