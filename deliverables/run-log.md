# Run log — actual and conditional workflow operations

This log records actual commands. No actual-case command below produced a full assessed snapshot or a Supported/Partial assignment result. The separate synthetic CLI demonstration generates labeled fixture snapshots. Deliberate probes are labeled; source/accepted stores were preserved. See [machine log](evidence/execution-log.json) for exact arguments, return codes and stdout hashes. Times are UTC; business clocks are the batch export dates.

## Consumed and produced

For a batch operation, the consumed allowlist is its byte-preserved [input manifest](evidence/input-manifests/). It contains the thirteen record filenames, README, document paths and source hashes/IDs/URLs. The initial archive materialization is a preparation operation outside business runtime. stage/review/timeline receive only the physical batch or its verified predecessor chain.

Stages write immutable source/state objects and HEAD under the named local store; the main evaluation driver also retained stage receipts under .local/confirmed-milestone/. Timeline writes stdout; the first three evaluations were preserved under the report paths in the verification report. Repeated read-only timelines write no state or report file. The probe/replay stages write only their separate stores. Logs are recording wrappers, not substitutes for genuine Entire capture.

## Actual operations

| # | Time UTC | Batch | Command | Exit | Scope/result |
|---|---|---|---|---|---|
| 1 | 2026-10-22T05:01:16.752967+00:00 | 1 | `.venv/bin/python -m credentialing check-input --input .local/inputs/batch-01 --batch 1` | 0 | evidence evaluation only; no assessed snapshot |
| 2 | 2026-10-22T05:01:16.835813+00:00 | 1 | `.venv/bin/python -m credentialing stage --input .local/inputs/batch-01 --batch 1 --store .local/continuation-store` | 0 | evidence evaluation only; no assessed snapshot |
| 3 | 2026-10-22T05:01:16.930134+00:00 | 1 | `.venv/bin/python -m credentialing timeline --store .local/continuation-store --state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f --rules references/continuation.json --rules-sha256 d392ba706f13091ee72baab794fb106cd93696da7c09ceb26b8c5e6b75c5144c` | 0 | evidence evaluation only; no assessed snapshot |
| 4 | 2026-10-22T05:01:37.906213+00:00 | 2 | `.venv/bin/python -m credentialing check-input --input .local/inputs/batch-02 --batch 2` | 0 | evidence evaluation only; no assessed snapshot |
| 5 | 2026-10-22T05:01:37.981829+00:00 | 2 | `.venv/bin/python -m credentialing stage --input .local/inputs/batch-02 --batch 2 --store .local/continuation-store --previous-state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f` | 0 | evidence evaluation only; no assessed snapshot |
| 6 | 2026-10-22T05:01:38.080131+00:00 | 2 | `.venv/bin/python -m credentialing timeline --store .local/continuation-store --state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a --rules references/continuation.json --rules-sha256 d392ba706f13091ee72baab794fb106cd93696da7c09ceb26b8c5e6b75c5144c` | 0 | evidence evaluation only; no assessed snapshot |
| 7 | 2026-10-22T05:01:38.215764+00:00 | 3 | `.venv/bin/python -m credentialing check-input --input .local/inputs/batch-03 --batch 3` | 0 | evidence evaluation only; no assessed snapshot |
| 8 | 2026-10-22T05:01:38.286015+00:00 | 3 | `.venv/bin/python -m credentialing stage --input .local/inputs/batch-03 --batch 3 --store .local/continuation-store --previous-state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a` | 0 | evidence evaluation only; no assessed snapshot |
| 9 | 2026-10-22T05:01:38.381760+00:00 | 3 | `.venv/bin/python -m credentialing timeline --store .local/continuation-store --state 0b9b640dc1d2552608b4c85628ef9beac3a53fedc661a3e2edf1c018e2a1651a --rules references/continuation.json --rules-sha256 d392ba706f13091ee72baab794fb106cd93696da7c09ceb26b8c5e6b75c5144c` | 0 | evidence evaluation only; no assessed snapshot |
| 10 | 2026-10-22T05:03:07.036105+00:00 | 1 | `.venv/bin/python -m credentialing timeline --store .local/continuation-store --state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f --rules references/continuation.json --rules-sha256 d392ba706f13091ee72baab794fb106cd93696da7c09ceb26b8c5e6b75c5144c` | 0 | read-only repeat or isolated deliberate failure/recovery probe; no assessed snapshot |
| 11 | 2026-10-22T05:03:07.150957+00:00 | 2 | `.venv/bin/python -m credentialing timeline --store .local/continuation-store --state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a --rules references/continuation.json --rules-sha256 d392ba706f13091ee72baab794fb106cd93696da7c09ceb26b8c5e6b75c5144c` | 0 | read-only repeat or isolated deliberate failure/recovery probe; no assessed snapshot |
| 12 | 2026-10-22T05:03:07.260955+00:00 | 3 | `.venv/bin/python -m credentialing timeline --store .local/continuation-store --state 0b9b640dc1d2552608b4c85628ef9beac3a53fedc661a3e2edf1c018e2a1651a --rules references/continuation.json --rules-sha256 d392ba706f13091ee72baab794fb106cd93696da7c09ceb26b8c5e6b75c5144c` | 0 | read-only repeat or isolated deliberate failure/recovery probe; no assessed snapshot |
| 13 | 2026-10-22T05:03:07.354052+00:00 | 1 | `.venv/bin/python -m credentialing stage --input .local/inputs/batch-01 --batch 1 --store .local/confirmed-milestone/probe-store` | 0 | read-only repeat or isolated deliberate failure/recovery probe; no assessed snapshot |
| 14 | 2026-10-22T05:03:07.449338+00:00 | 2 | `.venv/bin/python -m credentialing stage --input .local/inputs/batch-02 --batch 2 --store .local/confirmed-milestone/probe-store --previous-state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f` | 0 | read-only repeat or isolated deliberate failure/recovery probe; no assessed snapshot |
| 15 | 2026-10-22T05:03:07.536883+00:00 | 3 | `.venv/bin/python -m credentialing stage --input .local/inputs/batch-03 --batch 3 --store .local/confirmed-milestone/probe-store --previous-state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f` | 2 | read-only repeat or isolated deliberate failure/recovery probe; no assessed snapshot; predecessor_mismatch |
| 16 | 2026-10-22T05:03:07.632481+00:00 | 3 | `.venv/bin/python -m credentialing stage --input .local/inputs/batch-03 --batch 3 --store .local/confirmed-milestone/probe-store --previous-state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a` | 0 | read-only repeat or isolated deliberate failure/recovery probe; no assessed snapshot |
| 17 | 2026-10-22T05:03:07.726353+00:00 | 3 | `.venv/bin/python -m credentialing stage --input .local/inputs/batch-03 --batch 3 --store .local/confirmed-milestone/probe-store --previous-state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a` | 0 | read-only repeat or isolated deliberate failure/recovery probe; no assessed snapshot |
| 18 | 2026-10-22T05:03:07.792931+00:00 | — | `.venv/bin/python -m credentialing run` | 3 | read-only repeat or isolated deliberate failure/recovery probe; no assessed snapshot; business_blocked |
| 19 | 2026-10-22T05:11:43.534613+00:00 | 1 | `.venv/bin/python tools/prepare_batch.py --archive docs/audit/source-readings.json --manifest deliverables/evidence/input-manifests/batch-01.json --output .local/confirmed-milestone/replay/inputs/batch-01` | 0 | Clean handoff reconstruction using only manifest-selected input; not assessed processing |
| 20 | 2026-10-22T05:11:43.613091+00:00 | 1 | `.venv/bin/python -m credentialing check-input --input .local/confirmed-milestone/replay/inputs/batch-01 --batch 1` | 0 | Clean handoff reconstruction using only manifest-selected input; not assessed processing |
| 21 | 2026-10-22T05:11:43.707472+00:00 | 1 | `.venv/bin/python -m credentialing stage --input .local/confirmed-milestone/replay/inputs/batch-01 --batch 1 --store .local/confirmed-milestone/replay/store` | 0 | Clean handoff reconstruction using only manifest-selected input; not assessed processing |
| 22 | 2026-10-22T05:11:43.744831+00:00 | 2 | `.venv/bin/python tools/prepare_batch.py --archive docs/audit/source-readings.json --manifest deliverables/evidence/input-manifests/batch-02.json --output .local/confirmed-milestone/replay/inputs/batch-02` | 0 | Clean handoff reconstruction using only manifest-selected input; not assessed processing |
| 23 | 2026-10-22T05:11:43.817882+00:00 | 2 | `.venv/bin/python -m credentialing check-input --input .local/confirmed-milestone/replay/inputs/batch-02 --batch 2` | 0 | Clean handoff reconstruction using only manifest-selected input; not assessed processing |
| 24 | 2026-10-22T05:11:43.912933+00:00 | 2 | `.venv/bin/python -m credentialing stage --input .local/confirmed-milestone/replay/inputs/batch-02 --batch 2 --store .local/confirmed-milestone/replay/store --previous-state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f` | 0 | Clean handoff reconstruction using only manifest-selected input; not assessed processing |
| 25 | 2026-10-22T05:11:43.948952+00:00 | 3 | `.venv/bin/python tools/prepare_batch.py --archive docs/audit/source-readings.json --manifest deliverables/evidence/input-manifests/batch-03.json --output .local/confirmed-milestone/replay/inputs/batch-03` | 0 | Clean handoff reconstruction using only manifest-selected input; not assessed processing |
| 26 | 2026-10-22T05:11:44.020028+00:00 | 3 | `.venv/bin/python -m credentialing check-input --input .local/confirmed-milestone/replay/inputs/batch-03 --batch 3` | 0 | Clean handoff reconstruction using only manifest-selected input; not assessed processing |
| 27 | 2026-10-22T05:11:44.117661+00:00 | 3 | `.venv/bin/python -m credentialing stage --input .local/confirmed-milestone/replay/inputs/batch-03 --batch 3 --store .local/confirmed-milestone/replay/store --previous-state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a` | 0 | Clean handoff reconstruction using only manifest-selected input; not assessed processing |

## Development and verification commands

- First continuation suite: 32 tests, three join errors. Tuple-key diagnosis and targeted correction, then 87 tests passed.
- Added explicit type/returned-extra-reference coverage: 88 tests passed.
- Added four input-preparation tests: initial two fixture errors traced to the macOS /var symlink alias. Resolved the test root without weakening the production guard; 92 tests passed. Added an unknown-receipt-context guard: 93 tests passed; actual report bytes unchanged.
- `.venv/bin/python -m compileall -q credentialing tools` passed.
- Initial Skill validator under system python3 lacked yaml. Reused the installed scanner Python environment; `quick_validate.py .` passed; no dependency installation.
- `tools/independent_checks.py` independently reproduced actual counts and request intervals.
- Local-only Skill scan and manual bundle inspection are recorded in verification.md.

No stakeholder interview was conducted, scripted or automated. No notices were sent, source facts corrected, human decisions authored, Drive search retried, or material published/submitted.

## Local implementation checkpoint

Meaningful commit `486d0eb6f580081ee3cbf812e4c11872034ee9a5` has real checkpoint `01M5H0MYEEFCSDDP9TKX6E3GP4`; stored transcript bytes and learner authorization were inspected. Capture proof is recorded in a later documentation commit. Remote syncing/access remain pending; no publication or submission. Three final post-guard timeline reads were also compared byte-for-byte with retained reports; their tool record is in genuine capture, rather than a separately timestamped per-command entry here.

## Element assessment and writer milestone

[Machine log](assessments/execution-log.json) is the exact argument/time/exit/hash
record for the following operations. Inputs for each elements/run operation are
the pinned state and its predecessor chain's immutable manifests/blobs, plus the
pinned element/continuation/record-review source bundle. `run` creates/verifies
only its named independent report, then stops at assessed serialization; it
writes no assessed snapshot. `elements` stdout is retained under a content hash.
The first report set remains preserved; a later report occurrence corrects an
obsolete metadata label, not source content or business outcomes. `current.json`
selects the current occurrences. Logging wrappers write this ledger, not business
source records. Original source and accepted-store bytes remain unchanged.

| Log entry | UTC start | Batch | Operation | Exit | Produced / result |
|---|---|---|---|---|---|
| 1 | 2026-10-22T06:06:32.032710+00:00 | 1 | elements | 0 | deliverables/assessments/batch-01-elements-4b7fef28a1d9.json  |
| 2 | 2026-10-22T06:06:32.151276+00:00 | 1 | elements | 0 | deliverables/assessments/batch-01-elements-4b7fef28a1d9.json unchanged repeat |
| 3 | 2026-10-22T06:06:32.251173+00:00 | 1 | run | 3 | deliverables/assessments/batch-01-elements-4b7fef28a1d9.json  |
| 4 | 2026-10-22T06:06:32.344493+00:00 | 2 | elements | 0 | deliverables/assessments/batch-02-elements-f59ac7adae7b.json  |
| 5 | 2026-10-22T06:06:32.475564+00:00 | 2 | elements | 0 | deliverables/assessments/batch-02-elements-f59ac7adae7b.json unchanged repeat |
| 6 | 2026-10-22T06:06:32.597547+00:00 | 2 | run | 3 | deliverables/assessments/batch-02-elements-f59ac7adae7b.json  |
| 7 | 2026-10-22T06:06:32.710942+00:00 | 3 | elements | 0 | deliverables/assessments/batch-03-elements-4f8bb26795ad.json  |
| 8 | 2026-10-22T06:06:32.847039+00:00 | 3 | elements | 0 | deliverables/assessments/batch-03-elements-4f8bb26795ad.json unchanged repeat |
| 9 | 2026-10-22T06:06:32.988900+00:00 | 3 | run | 3 | deliverables/assessments/batch-03-elements-4f8bb26795ad.json  |
| 10 | 2026-10-22T06:10:41.217504+00:00 | 1 | elements | 0 | deliverables/assessments/batch-01-elements-1afae619a1e6.json  |
| 11 | 2026-10-22T06:10:41.360158+00:00 | 1 | elements | 0 | deliverables/assessments/batch-01-elements-1afae619a1e6.json unchanged repeat |
| 12 | 2026-10-22T06:10:41.454797+00:00 | 1 | run | 3 | deliverables/assessments/batch-01-elements-1afae619a1e6.json  |
| 13 | 2026-10-22T06:10:41.551969+00:00 | 2 | elements | 0 | deliverables/assessments/batch-02-elements-cf7c99c0984a.json  |
| 14 | 2026-10-22T06:10:41.677197+00:00 | 2 | elements | 0 | deliverables/assessments/batch-02-elements-cf7c99c0984a.json unchanged repeat |
| 15 | 2026-10-22T06:10:41.798416+00:00 | 2 | run | 3 | deliverables/assessments/batch-02-elements-cf7c99c0984a.json  |
| 16 | 2026-10-22T06:10:41.925740+00:00 | 3 | elements | 0 | deliverables/assessments/batch-03-elements-c6a4eef414e0.json  |
| 17 | 2026-10-22T06:10:42.068943+00:00 | 3 | elements | 0 | deliverables/assessments/batch-03-elements-c6a4eef414e0.json unchanged repeat |
| 18 | 2026-10-22T06:10:42.214408+00:00 | 3 | run | 3 | deliverables/assessments/batch-03-elements-c6a4eef414e0.json  |
| 19 | 2026-10-22T06:10:42.345419+00:00 | — | tools/independent_element_checks.py --inputs | 0 | deliverables/assessments/independent-verification.json  |
| 20 | 2026-10-22T06:10:42.436602+00:00 | — | -m tools.writer_demo | 0 | .local/elements-milestone/writer-demo-stdout.json  |

The first development wrapper stopped at `changed_report` on batch 1 because
stdout and persisted report differed only in Unicode escaping. Its two preceding
read-only evaluations and failed attempt are visible in the genuine session;
the wrapper aborted before saving a timestamped operation ledger. No exact
operation timestamp is reconstructed. The original hash-named report remains.
The Unicode regression test reproduced exit 2 instead of intended exit 3; the
serialization correction restored byte equality without overwriting the report.
See verification.md for the precise cause and final 114-test result.

The writer demo command creates only its explicitly synthetic root, with
synthetic source/rules files, generated nested snapshots, archives/index, run-log,
proof and internal transaction journals. Its proof records each generation,
unchanged rerun, rejected correction, injected write failure, blocked verification,
rollback and successful retry. It never reads supplied applicants. Fixture Git
sealing is the subsequent meaningful local commit, not the generation call.
[Independent checker](assessments/independent-verification.json) consumes original
three-batch CSVs/README/manifests and selected current reports; it writes stdout
only. The later clock-source refinement reproduced those exact output bytes.
Regression stdout/stderr summary is in assessments/test-summary.json and raw
output in assessments/tests.txt. Development checks are not assessed batch runs.

## Complete workflow processing

`process` now runs all confirmed-rule branches and persists a complete internal
workflow report even when the original schema cannot encode the actual batch.
The exact command/time/exit/receipt records are in [workflow execution log](workflow/execution-log.json).
The first three are actual batches in order; subsequent entries are unchanged
batch-3 repeats, a clean three-batch reconstruction and the independent check.
Each consumes its pinned source manifest/previous workflow plus original pinned
rules. Each writes or verifies its hash-named workflow report and the separate
immutable workflow store; no actual assessment snapshot is generated. Exit 3 is
scoped to assessed projection, not a software or business deferral.

The synthetic demonstration's [own log](synthetic/workflow-demo/execution-log.json)
records seven real CLI calls: three evidence stages, three full workflow runs,
and an unchanged final rerun. Inputs are only its invented batch folders. Outputs
are its separate stores, nested reports/snapshots/run log and proof. Its snapshot
produced lists include the workflow report and writer artifacts. Internal journal/
state-control objects are distinct from business output files.

Development evaluations before verification had false role-format/action/referee
classifications and overly strong treatment of unrecorded route/narrative review.
They were rejected, preserved byte-for-byte with logs in
.local/workflow-completion/rejected-development-reports and separately identified
stores, and reconstructed without changing any source or previously accepted
result. Original command/receipt paths remain in those development logs with
retained locations/dispositions. They are not asserted as current business results.
The final raw 145-test output is workflow/tests.txt. Integrated failure/recovery
and malformed-condition probes are explicitly synthetic; no production failure,
notification, clinical approval or learner acceptance was manufactured.

| Entry | UTC start | Operation / batch | Exit | Result |
|---|---|---|---|---|
| 1 | 2026-10-22T07:48:31.871839+00:00 | process / 1 | 3 | stored blocked-at-schema-projection |
| 2 | 2026-10-22T07:48:32.286072+00:00 | process / 2 | 3 | stored blocked-at-schema-projection |
| 3 | 2026-10-22T07:48:32.898796+00:00 | process / 3 | 3 | stored blocked-at-schema-projection |
| 4 | 2026-10-22T07:48:33.606057+00:00 | process / 3 | 3 | unchanged blocked-at-schema-projection |
| 5 | 2026-10-22T07:48:34.391216+00:00 | process / 3 | 3 | unchanged blocked-at-schema-projection |
| 6 | 2026-10-22T07:52:52.016331+00:00 | process / 1 | 3 | stored blocked-at-schema-projection |
| 7 | 2026-10-22T07:52:52.451186+00:00 | process / 2 | 3 | stored blocked-at-schema-projection |
| 8 | 2026-10-22T07:52:53.057549+00:00 | process / 3 | 3 | stored blocked-at-schema-projection |
| 9 | 2026-10-22T07:52:53.744852+00:00 | independent check / all | 0 | independent original-source repeat  |
