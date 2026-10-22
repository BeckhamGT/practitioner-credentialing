# Practitioner credentialing

Build a reusable Agent Skill that runs a medical staff office's initial-appointment credentialing file from application intake to recorded appointment and active privileges.

## Start

1. Read the [full task](https://docs.google.com/document/d/1HhmU8Jay09XHDci38hl9ZOX_dMryaSv4aFLCPu1Nk-E/edit): it owns the scope, deliverables and acceptance requirements.
2. Create your own repository from [this starter](https://github.com/GitRollTraining/practitioner-credentialing) using **Use this template → Create a new repository**, then clone your copy and work there.

## Supplied files

| File | Purpose |
|---|---|
| `README.md` | Starting instructions and the full-task link. |
| `snapshot.schema.json` | The required shape of the per-batch snapshot your Skill writes. Validate every snapshot against it. Your implementation language and validation library are yours. |

You create the Skill, its implementation, your own checks and every output the task requires. Nothing here implements any part of the office's work.

## Before you work

**Interview rule.** You conduct the stakeholder interview yourself, and the questions are yours. Do not connect a coding agent or any other AI to the interview to run, script, or automate it. The interview transcript is assessed together with the code; a project whose interview was run by an agent is not scored.

- Export your interview as the original Work Sim Markdown, save one final complete file per session under `interviews/`, and commit and push it with your code. Do not rewrite the export. If the export is unavailable, contact the facilitator.
- No runtime is supplied. Choose the dependencies your Skill needs and document how to install and run it.
- Complete the program's coding-session capture setup in the course before assessed work, and confirm your session is being captured after your first meaningful commit. Ask the facilitator to repair missing capture before you continue.
- Meet the stakeholder to obtain the relevant business source links and context; the facilitator supplies the interview link with the assignment. Read those online sources through the intended access route.

## Current implementation — evidence review and conditional components

The learner selected a Python CLI and explicit persisted JSON state. Loading,
structural validation, provenance, hashing, state storage, independent record
checks and chronological evidence review are implemented. Root [SKILL.md](SKILL.md)
documents invocation and boundaries; conditional business kernels have synthetic
tests only. **G1 (application-signature evidence) and G2 (CV currency and
reconciliation evidence) remain unresolved.** Completeness decisions, packet
readiness, decision admission and assessed snapshots remain unsupported. There is
no bypass flag. Independent human evidence tasks are reported with owners and
null due dates when no record fixes one. `run` retains its independent assessment
and exits 3 without writing an assessed snapshot.

Read [the source/readiness audit](docs/readiness-audit.md),
[the groundwork plan](docs/groundwork-plan.md), and
[the verification evidence](docs/groundwork-verification.md) for scope and limits.
The audit's narrower source conflicts remain open with owners and next actions;
the loader preserves their exact text without correcting or adjudicating it.

### Setup and checks

Use Python 3.11 or later (tested here on Python 3.15.0, macOS):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -v
.venv/bin/python -m credentialing --help
```

The single direct runtime dependency is jsonschema 4.26.0. The recorded environment's
transitive versions are in requirements.lock. Validation explicitly enables date
format checks; the validator's format keyword alone does not check dates ([validator documentation](https://python-jsonschema.readthedocs.io/en/stable/validate/)).

### One physical batch at a time

The CLI never reads `docs/audit/source-readings.json`, scans other batch folders,
or downloads sources. Prepare a separate input directory with the office's thirteen
CSV files, its README.md, and every indexed supporting document. The audit archive
contains all three batches and is unsuitable as runtime input. The local batch-1
demonstration uses only its 29 selected files, with hashes checked against the
audit's **extracted text** inventory; those are not claimed to be original provider
download bytes. Input preparation is not an assessed credentialing run.

Add `input.manifest.json` with this contract:

- `format`: `credentialing-input-manifest/1`; `batch`: positive integer; `as_of`:
  the export date, matching that batch's README.
- `files`: an exact allowlist, one entry per source with its relative POSIX `path`,
  lowercase hex `sha256` of exact bytes, `source_id`, HTTPS `source_url`,
  `source_batch` matching this batch, and `kind` (`records`, `batch-readme`, or
  `document`). This is an engineering manifest, not a new office record.
- All thirteen source CSV headers must match the observed export contract.
  Header-only files are valid; missing files are not. Correspondence document paths
  must resolve exactly to the listed `letters/`, `dispositions/`, `decisions/` files.
- The operator establishes the manifest's authority. A matching hash proves
  integrity relative to it, not source authenticity, clinical validity, or permission.

For the local batch-1 evidence demonstration:

```sh
.venv/bin/python -m credentialing check-input --input .local/inputs/batch-01 --batch 1
.venv/bin/python -m credentialing stage --input .local/inputs/batch-01 --batch 1 --store .local/evidence-store
.venv/bin/python -m credentialing inspect-state --store .local/evidence-store
```

`check-input` returns `structure-valid`; this makes no completeness finding.
`stage` returns `staged` or `unchanged`, an evidence-state hash, the batch export
clock, G1/G2 blockers, and `assessed_snapshot_written: false`. These operation
results are not the assignment's supported/partial/blocked/deferred submission states.
No records are silently cleaned, blank cells stay blank, and raw bytes are retained.
Observation dates after the export are rejected. Future expiry/end dates are not
later observations and are retained. Unlisted files are never opened. Symlink and
traversal paths are rejected.

For an authorized later evidence-stage operation, explicitly bind the prior state:

```sh
.venv/bin/python -m credentialing stage --input /absolute/path/to/batch-02 --batch 2 --store .local/evidence-store --previous-state PRIOR_STATE_SHA256
```

Replace the placeholder with the preceding receipt's exact hash. Batch 3 uses the
batch-2 hash, not batch 1. All retained predecessor bytes are verified on resume;
missing/corrupt state is never replaced with a fresh reconstruction. Actual
evidence batches 1–3 have been staged in the separate continuation store below;
the accepted original batch-1 store remains unchanged. Evidence staging and
assessment do not establish the assignment's consumed business-state snapshots.

### State integrity, failure and review

`objects/blobs/<sha256>` retains exact manifest/source bytes;
`objects/states/<sha256>` holds immutable JSON evidence-state occurrences.
`HEAD.json` points to the current occurrence. Neither object format is the required
assessment snapshot. Each state contains only that batch's manifest and a prior-state
hash, with no computed application status, readiness, decision or activation.

An unchanged latest-batch rerun keeps the same state bytes and identity. A changed
retained batch, stale predecessor, skipped batch, malformed source, or failed write
returns a nonzero exit and does not replace the last current state. This groundwork
does not implement the assignment's sealed-snapshot correction protocol; preserve
the original evidence store and investigate or create a separately identified
reconstruction after review. Never edit supplied records as a repair.

The store has an exclusive writer lock and atomic HEAD replacement. Abandoned
objects are not promoted automatically. If HEAD is missing while state objects
exist, preserve the store and investigate; do not treat it as a new run. For an
interrupted-writer lock, first establish that no writer is active before manually
removing only the lock. Power-loss/filesystem durability is not established.

Exit codes: 0 for a successful groundwork operation, 2 for validation/storage or
argument failure, 3 for the deliberately blocked business operation. Failure JSON
goes to stderr. No automatic remote publication occurs.

Before implementing the affected business logic, obtain the G1/G2 clarification and
return to the learner for review. After the first actual batch is processed, show
the real snapshot/action queue, source comparisons and an independent calculation
before continuing. Preserve authentic human choices and final inspection separately
from what the agent merely displayed. Do not push private sources/interview/capture
or submit to Classroom until the learner's publication/submission instructions permit it.

## Evidence continuation and handoff

The learner authorized confirmed-rule independent work and synthetic tests of
dependent logic. [The milestone plan](docs/confirmed-rule-plan.md) separates these
dependencies. The [rules](deliverables/rules.md), [verification](deliverables/verification.md)
and [run log](deliverables/run-log.md) describe actual capability and remaining work.
This is not yet the full intake-to-activation assignment implementation.

The already-read source archive contains extracted text from all three batches.
To reproduce the selected physical inputs, use the preparer **outside** business
runtime. It selects only the reviewed manifest, preserves exact retained text
bytes and provenance, and refuses to overwrite differing existing files. These
are connector-returned text bytes, not original provider file exports.

```sh
for credentialing_batch in 01 02 03; do
  .venv/bin/python tools/prepare_batch.py --archive docs/audit/source-readings.json --manifest "deliverables/evidence/input-manifests/batch-${credentialing_batch}.json" --output ".local/inputs/batch-${credentialing_batch}"
done
```

For a fresh replay, choose an unused store such as `.local/replay-store`. Preserve
any existing store; do not reinitialize a batch-3 store by staging batch 1 over it.
Run these in order, inspecting each receipt before continuing:

```sh
.venv/bin/python -m credentialing check-input --input .local/inputs/batch-01 --batch 1
.venv/bin/python -m credentialing stage --input .local/inputs/batch-01 --batch 1 --store .local/replay-store
.venv/bin/python -m credentialing stage --input .local/inputs/batch-02 --batch 2 --store .local/replay-store --previous-state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f
.venv/bin/python -m credentialing stage --input .local/inputs/batch-03 --batch 3 --store .local/replay-store --previous-state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a
```

Those hashes identify these exact retained manifests. For changed or new inputs,
use the hashes actually returned by the preceding verified receipts. The observed
separate `.local/continuation-store` now contains all three evidence stages:

| Batch | Export clock | State hash |
|---|---|---|
| 1 | 2026-03-16 | a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f |
| 2 | 2026-04-20 | 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a |
| 3 | 2026-05-18 | 0b9b640dc1d2552608b4c85628ef9beac3a53fedc661a3e2edf1c018e2a1651a |

Run/repeat the evidence timeline for a pinned state, even when HEAD is newer:

```sh
.venv/bin/python -m credentialing timeline --store .local/continuation-store --state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f --rules references/continuation.json --rules-sha256 d392ba706f13091ee72baab794fb106cd93696da7c09ceb26b8c5e6b75c5144c
.venv/bin/python -m credentialing timeline --store .local/continuation-store --state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a --rules references/continuation.json --rules-sha256 d392ba706f13091ee72baab794fb106cd93696da7c09ceb26b8c5e6b75c5144c
.venv/bin/python -m credentialing timeline --store .local/continuation-store --state 0b9b640dc1d2552608b4c85628ef9beac3a53fedc661a3e2edf1c018e2a1651a --rules references/continuation.json --rules-sha256 d392ba706f13091ee72baab794fb106cd93696da7c09ceb26b8c5e6b75c5144c
.venv/bin/python tools/independent_checks.py --inputs .local/inputs --reports deliverables/evidence --application APP-2026-014 --subject REF-1401
.venv/bin/python -m unittest discover -v
```

Timeline stdout is `credentialing-evidence-timeline/1`: revisions, source hashes,
attempts and replies, actual decision metadata and independently established
early refusals. An internal `admitted: null` means admission is unevaluated and
cannot be serialized into the assessment schema. `review_tasks` are MSP evidence
review tasks; the final per-file business action queue remains unfinished.

The read-only snapshot verifier accepts a root, repository-relative snapshot path
and schema: `verify-snapshot --root <workspace> --path <snapshot> --schema snapshot.schema.json`.
It checks schema and selected relationships listed in the rules register; it
does not establish source truth or business authority. No actual assessment
snapshot is available to verify yet. Synthetic tests exercise this interface.

### Assignment result meanings and current boundary

| Assignment state | Required actual evidence | Current implementation |
|---|---|---|
| Supported | All supplied batches consumed, three sealed snapshots and required files agreeing | Not demonstrated; evidence stages are not assessed consumption |
| Partial | A consumed batch with schema-valid owned unresolved cases and scope in run log | Not claimed; no encoding is invented for G1/G2 |
| Blocked | Batch cannot be consumed; failed attempt scoped; no replacement snapshot; prior sealed result retained | Required-field serialization blocked; independent reports retained; no actual sealed snapshot exists |
| Deferred | Authentic business hold with owner and awaited event, not a failed run | Conditional protocol tests; actual business-state integration pending |

To continue unfinished work, preserve the reports/store and consult the remaining
matrix in verification.md. Independent checks need no new blanket approval.
Signed application/CV evidence or an explicit authorized export convention is
still needed for dependent completeness/reconciliation. Return to the learner
before integrating newly supported dependent logic. Do not repeat the unchanged
Drive search without new source information. Actual first-batch business output
and final acceptance remain future learner review gates.

## Independent record review

The learner accepted the groundwork milestone and authorized confirmed-rule checks
independent of G1/G2. See [actual record-review results and limits](docs/record-review-milestone.md),
including the exact outstanding signature/CV prerequisites and source references.

The [current complete interview](interviews/project-e-practitioner-credentialing-20261022-0427.md)
retains the previous conversation and the latest follow-up without rewriting it.
See the [updated readiness audit](docs/readiness-audit.md) and
[byte-preservation/folder-inventory proof](docs/audit/interview-update-20261022-0427.json).
The supplied Drive trees contain no application revisions folder or completed
signed forms. CV currency now has a qualitative intake definition; actual CV
evidence and its exported reconciliation representation remain unresolved.
The latest follow-up confirms the two directory names refer to the same root,
but supplies no new document location. G1/G2 stay blocked; these source
clarifications change no runtime business logic. Independent authorized checks
continue without a new facilitator-approval requirement.

```sh
.venv/bin/python -m credentialing review --store .local/evidence-store --state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f --policy references/record-review --policy-sha256 673cce5abb0a6eab08f5a9bb2f569bbaa6af71a1b0dec01318a12d5e2c2e879b
```

This reads only the explicitly pinned evidence state and its predecessors; it never
opens a newer HEAD. Policy text hashes/versions are pinned separately, and future
policy is rejected. The command writes JSON to stdout and does not modify state or
source files. Preserve a saved report under its content hash if retaining it; do
not overwrite prior reports or call it an assessed snapshot.

The report checks delivery-source classes, recorded date windows, individual peer
fields and the first two decision-authority conditions. It retains original
outcomes and conflicting notes. A listed source class is not a verified credential;
an authority pass is not an admitted decision. Unknown links and unsupported
formats require source review. All dependent business conclusions stay not evaluated,
and `run` still exits 3. No notices, approvals, activation or business action queues
are generated by this command.

## Independent elements and local snapshot writer

[Current review](docs/element-review-milestone.md) shows actual results and
specific source comparisons. These are not accepted business outcomes.
`deliverables/assessments/current.json` selects the current report for each batch;
older hash-named reports remain preserved. The latest report uses the same pinned
state chain as the timeline. The element-rule hash is
`f4d0418c024166945826c2eb9f586f787350ab7efec3faa8fd0c7fc524613eb1`.

```sh
.venv/bin/python -m credentialing elements --store .local/continuation-store --state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f --rules references/element-rules.json --rules-sha256 f4d0418c024166945826c2eb9f586f787350ab7efec3faa8fd0c7fc524613eb1
.venv/bin/python -m credentialing elements --store .local/continuation-store --state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a --rules references/element-rules.json --rules-sha256 f4d0418c024166945826c2eb9f586f787350ab7efec3faa8fd0c7fc524613eb1
.venv/bin/python -m credentialing elements --store .local/continuation-store --state 0b9b640dc1d2552608b4c85628ef9beac3a53fedc661a3e2edf1c018e2a1651a --rules references/element-rules.json --rules-sha256 f4d0418c024166945826c2eb9f586f787350ab7efec3faa8fd0c7fc524613eb1
.venv/bin/python -m credentialing run --store .local/continuation-store --state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f --rules references/element-rules.json --rules-sha256 f4d0418c024166945826c2eb9f586f787350ab7efec3faa8fd0c7fc524613eb1 --report deliverables/assessments/batch-01-elements-1afae619a1e6.json
.venv/bin/python tools/independent_element_checks.py --inputs .local/inputs --reports deliverables/assessments
```

The fourth command is an expected **exit 3**: it verifies/retains the internal
report, then refuses unsupported snapshot serialization. For another batch use
that batch's exact state and a distinct report path; use its `current.json` name
to compare an unchanged report. Different existing report bytes are never
overwritten. `elements` writes stdout only. Neither command changes the store.

[Partial representation assessment](docs/partial-representation-assessment.md)
cites the assignment and exact schema fields. Its `in-verification` candidate
is labeled a rejected proposal: it would assert complete intake. A null-due MSP
evidence task is truthful, but cannot fix unknown mandatory booleans/statuses.
No actual `deliverables/snapshots/` paths are populated. The schema stays unchanged.

`credentialing/writer.py` is a tested local writer API; business-state projection
is unfinished. It validates the original schema, links and clock before writing;
preserves old bytes, regenerates affected downstream occurrences, retains a log
and requires new IDs for changed occurrences. A Git commit seals the output.
Internal journals/backups live under `.local/snapshot-writer/`. A failed
transaction blocks verification rather than exposing earlier success as current.
The recovery command validates retained bytes and refuses external changes:

```sh
.venv/bin/python -m credentialing recover-writer --root /absolute/path/to/interrupted/workspace --schema snapshot.schema.json
```

Inspect first, confirm the writer is inactive, preserve its journal, recover,
then retry the same authorized input. This is not evidence-store reconstruction.
Power-loss durability is unproved. The labeled demonstration is retained under
`deliverables/synthetic/writer-demo/`; its nested snapshot names are fixtures,
not the required submitted paths. To reproduce, choose a **new** synthetic root:

```sh
.venv/bin/python -m tools.writer_demo --output .local/synthetic/writer-replay --schema snapshot.schema.json
```
