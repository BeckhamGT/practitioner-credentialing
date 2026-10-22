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

## Authorized groundwork — not a completed credentialing Skill

The learner selected a Python CLI and explicit persisted JSON state. Only loading,
structural validation, provenance, hashing, state storage and the command interface
are implemented. **G1 (application-signature evidence) and G2 (CV currency and
reconciliation evidence) remain unresolved.** Completeness decisions, packet
readiness, business action queues and assessed snapshots are disabled. There is
no bypass flag. `run` exits 3 without writing an assessed snapshot.

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
missing/corrupt state is never replaced with a fresh reconstruction. Only synthetic
fixtures have been staged through three batches so far. The actual caseload has
not been processed, and actual batch-2/3 evidence has not entered the local store.

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
