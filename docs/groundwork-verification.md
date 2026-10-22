# Groundwork verification — limited authorization

Only the Python loading, validation, provenance, hashes, JSON state and CLI groundwork is implemented. No application completeness, packet-readiness conclusion, human decision, action queue or assessed snapshot was computed. G1/G2 remain unresolved. G3–G7 in [the audit](readiness-audit.md) retain their affected sources, consequences, owners and next actions; no source text was repaired.

## Observed checks

` .venv/bin/python -m unittest discover -v ` passed **32 tests** on Python 3.15.0, macOS. `compileall` and `git diff --check` passed. Tests exercise behavior and failure boundaries rather than credentialing answers: unknown cells and quoted CSV, missing versus header-only files, malformed UTF-8/CSV/JSON, date-format checking, future observations versus known expiry dates, hash mismatch, wrong/mixed batch provenance, unlisted future files remaining unread, traversal/symlinks, document index coverage, immutable bytes, unchanged reruns, explicit three-batch synthetic resume, skipped/stale predecessor rejection, corrupted/missing state, locking, failed atomic HEAD replacement, and observed retry after the isolated failure.

Synthetic continuation/failure fixtures are temporary test inputs and are not case records or historical production failures. Only actual batch-1 sources have been staged in `.local/evidence-store`; actual batches 2/3 have not been staged. Runtime has no network calls and never imports the combined audit archive. The published snapshot schema is byte-unchanged from the starter.

The physical batch-1 input was prepared from the already-reviewed audit readings, selecting only its 29 files and independently comparing their SHA-256 values to the extracted-text inventory. That preparation is not a business run. The source bytes available here are connector-returned extracted text; provider-original byte identity is not claimed. All observed office CSV headers are represented explicitly in the loader contract; no case answers, IDs or outcome thresholds appear in the implementation.

[Actual command receipts and independent checks](groundwork-checks.json) record:

| Actual command | Observed result | Limit |
|---|---|---|
| `check-input --input .local/inputs/batch-01 --batch 1` | Structure valid; 13 CSVs, 15 supporting documents; 41 application-revision rows | No completeness or credentialing judgment |
| `stage --input .local/inputs/batch-01 --batch 1 --store .local/evidence-store` | First observed operation staged; later receipt says unchanged with identical HEAD | Evidence retention only |
| `inspect-state --store .local/evidence-store` | One batch, export clock 2026-03-16, phase evidence-only, G1/G2 attached | No business state |
| `run` | Exit 3, error business_blocked | No assessed snapshot written; no bypass flag |

The current evidence-state object has SHA-256 `a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f`. Outside the implementation's writer, a standard-library hashlib check recomputed its exact-byte hash, compared every retained source blob to the selected input bytes, and confirmed unchanged HEAD after rerun and blocked run. This is infrastructure evidence, not fulfillment of the assignment's future output-based independent verification requirement.

The final interview remains exactly 37,803 bytes with SHA-256 `841137c5c271aa52ff4305ccccfaae818eedc63edacdfaf852259e9df4ee41d9`, equal to the Downloads original. Only one combined export is under interviews/.

## Commit and capture gate

The first meaningful groundwork commit is `13acbae26f407632674b6488791204506c18de5a`. Its actual commit message carries `Entire-Checkpoint: 01M5GRMYMAQCXFP2MK68DKP90K`, resolving locally to `refs/entire/checkpoints/0K/01M5GRMYMAQCXFP2MK68DKP90K`, Git object `1b63c8ae0adcc91a486f928532952f7ccb000429`.

`entire checkpoint explain --commit HEAD --json` identifies the actual session `01a15fd1-860f-7210-a8ec-b2a637129c5e`. The checkpoint transcript was exported with the read-only `--transcript` mode and compared byte-for-byte with the Git-stored payload. It contains the learner's authorization at `2026-10-22T02:46:42.859Z` and the actual implementation tool records. Its 4,661,589 bytes / 614 JSONL records have SHA-256 `33e6b7e9cdd511d6e6bb4e63e33cf5211319e17c18b65dcc0032f761b83a091f`. The raw export stays under ignored `.local/capture/`; the actual durable checkpoint is the Git ref, not this report. [Machine-readable capture proof](groundwork-capture.json) records the observed references and checks.

Local commit association and genuine stored capture are demonstrated. Remote synchronization is **pending**, not passed: no push was authorized or attempted. Facilitator access is not demonstrated. Fork/publication and checkpoint-ref-format questions remain with the learner/facilitator. This evidence report is recorded in a later local documentation commit and does not pretend its own text was present in the earlier checkpoint.

## Review guide and remaining gates

- Inspect the actual `check-input` and `inspect-state` receipts: export clock must be 2026-03-16 and no application states should appear. The 41 rows are revisions, not an asserted count of distinct applicants.
- Read the stored manifest/state using the hash above and independently compare one source's SHA-256 to its original selected input. Presence of a matching hash does not establish clinical admissibility.
- Verify `run` exits 3 and writes no deliverables/snapshots file. Structural acceptance of a blank release/CV field must never be mistaken for passing completeness.
- The original audit map still contains the full published requirements. Groundwork tests do not establish business-rule coverage, Skill completeness, schema relationships between assessed snapshots, submission readiness or learner acceptance.
- Learner obtains G1/G2 clarifications and the fork/publication/capture-format answers. Return to the learner before affected business logic. Later show the actual first assessed snapshot and queue with source comparisons and an independent calculation before continuing.
- All interview, source material and capture remain local. Publication, Classroom submission and grading are unperformed.
