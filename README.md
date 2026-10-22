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

## Current workflow

The reusable [Skill](SKILL.md) runs a Python CLI with explicit immutable JSON
state. `process` evaluates all six elements, intake, owned queues, decisions,
activation/conditions and history, and invokes the original-schema writer when
every required meaning is established. [Current review](docs/workflow-review.md)
separates actual, unknown and synthetic conditional results. No facilitator
contact or new inventory search is needed to use the software.

Actual signatures/CVs are still unavailable; no pass is assumed. Actual reports
carry G1/G2 as MSP-owned review work. Known facts and proven negative prerequisites
are evaluated independently. The current actual full caseload cannot be projected
into three truthful assessment snapshots; reports name each unmet field. This
serialization limitation does not stop workflow continuation.

### Setup

Python 3.11+ (tested on macOS Python 3.15.0), jsonschema 4.26.0:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -v
.venv/bin/python -m credentialing --help
```

Transitive versions are recorded in requirements.lock. No network is used by
business processing; sources must be authorized local inputs. No mail or notice
is sent by the CLI. Business clocks always come from the export, never host time.

### Materialize and retain one physical batch

If `.local/inputs` is absent, the preparation tool can reconstruct one batch
from the retained extracted archive and reviewed manifest. This utility is
outside business runtime; it selects only the named batch. Original native
provider revision/signature authentication is not implied by extracted hashes.

```sh
.venv/bin/python tools/prepare_batch.py --archive docs/audit/source-readings.json --manifest deliverables/evidence/input-manifests/batch-01.json --output .local/inputs/batch-01
.venv/bin/python tools/prepare_batch.py --archive docs/audit/source-readings.json --manifest deliverables/evidence/input-manifests/batch-02.json --output .local/inputs/batch-02
.venv/bin/python tools/prepare_batch.py --archive docs/audit/source-readings.json --manifest deliverables/evidence/input-manifests/batch-03.json --output .local/inputs/batch-03
.venv/bin/python -m credentialing stage --input .local/inputs/batch-01 --batch 1 --store .local/replay-evidence
.venv/bin/python -m credentialing stage --input .local/inputs/batch-02 --batch 2 --store .local/replay-evidence --previous-state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f
.venv/bin/python -m credentialing stage --input .local/inputs/batch-03 --batch 3 --store .local/replay-evidence --previous-state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a
```

Use a new replay store, or its current exact predecessor; do not initialize over
retained work. Input contents/manifest hashes, required thirteen CSVs, README,
actual document index and observation cutoffs are checked before state moves.
Stage is evidence retention, not completeness or assessed batch consumption.
The accepted batch-1 store and the earlier continuation store remain unchanged.

### Exact workflow commands and continuation

Use a fresh work store for a clean 1→2→3 replay. The following source/previous
hashes reproduce the current retained actual results. For another authorized
batch use that batch's actual receipt hashes, not these examples.

```sh
.venv/bin/python -m credentialing process --store .local/replay-evidence --state a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f --work-store .local/your-workflow-replay --rules references/element-rules.json --rules-sha256 f4d0418c024166945826c2eb9f586f787350ab7efec3faa8fd0c7fc524613eb1
.venv/bin/python -m credentialing process --store .local/replay-evidence --state 58b5a3bc181da5ac48746d3e45803f5a1b52d5e179f8e3937bfe4a8bfe69659a --work-store .local/your-workflow-replay --rules references/element-rules.json --rules-sha256 f4d0418c024166945826c2eb9f586f787350ab7efec3faa8fd0c7fc524613eb1 --previous-workflow 5ac56baa3165b13892d55b987d05b93533018f1961612533ef8e7d76e80e1679
.venv/bin/python -m credentialing process --store .local/replay-evidence --state 0b9b640dc1d2552608b4c85628ef9beac3a53fedc661a3e2edf1c018e2a1651a --work-store .local/your-workflow-replay --rules references/element-rules.json --rules-sha256 f4d0418c024166945826c2eb9f586f787350ab7efec3faa8fd0c7fc524613eb1 --previous-workflow a4359c44c6537fbe0f5d1ad7c47d258a86d7b63478a91798985ad90c303b898e
```

These actual-case commands intentionally exit **3**, while stdout supplies a
stored workflow hash/report and `blocked-at-schema-projection`. Domain processing
completed; a schema snapshot was not asserted. Continue from the workflow receipt
as shown. Exit **2** is an actual validation/storage/argument failure: investigate
before continuing. Exit **0** means schema generation or unchanged validated
snapshot succeeded; it is not human acceptance or submission readiness.

After batch 3, repeat its exact command to verify unchanged bytes. To rerun an
earlier batch, preserve the existing store and replay in a new work store from
batch 1; do not roll HEAD backwards or change a closed source. Changed software
results are a new reconstruction, not a silent rewrite of earlier reports.
`deliverables/workflow/current.json` selects the reviewed current reports. The
internal immutable store has `objects/<hash>.json` and `HEAD.json`. It is separate
from both source state and the required assessment snapshots.

### Results and human evidence

| Result | Meaning in this implementation |
|---|---|
| Established actual result | Supported by current exported rows/documents and the named rule. A known necessary failure can establish false readiness despite unrelated unknowns |
| Missing-evidence result | Null only in the internal report, with its dependency/owner/action; never silently converted into an assessment enum or boolean |
| Conditional demonstration | SYNTH-only fixtures state their invented facts and sources. They demonstrate software behavior, not supplied-applicant outcomes |
| Partial assignment result | Requires a truthful schema snapshot for the full consumed caseload, with owned unresolved work. Not claimed for the current actual runs |
| Blocked assessed projection | Independent workflow persisted; required snapshot cannot truthfully encode named fields or lacks its assessed predecessor. No fake snapshot replaces a prior result |
| Deferred business result | Only an admitted GB deferral; its exact awaited information and MSP chase are retained. A failed run is never called deferred |

The [MSP observation protocol](docs/human-observation-protocol.md) supports
source-linked factual reviews of signature, CV/reconciliation, declarations,
accreditation and secondary-route authorization. It requires dated retained
document hashes and the roster's actual MSP. It cannot grant privileges, accept
an explanation clinically or discontinue a file. No observation is invented for
actual applicants. Newly supplied evidence/conventions still receive learner
review before being treated as established actual facts.

### Verify and demonstrate

```sh
.venv/bin/python tools/independent_workflow_checks.py --inputs .local/inputs --reports deliverables/workflow
.venv/bin/python -m tools.workflow_demo --output .local/synthetic/workflow-replay
```

Choose a new demo directory. The retained demonstration is
`deliverables/synthetic/workflow-demo/`, with invented source batches, review
records, decisions, receipts, three nested snapshots and proof. Its stages are
packet-presentable → approved-not-yet-effective → active-with-conditions. The
approval grants only PRIV-FM, from 2026-04-25 through 2027-04-24, despite two
requested groups. Other conditional exception paths are in tests/test_workflow.py.

Read-only structural/relationship verification:

```sh
.venv/bin/python -m credentialing verify-snapshot --root deliverables/synthetic/workflow-demo --path deliverables/snapshots/batch-03.json --schema snapshot.schema.json
```

The legacy `review`, `timeline`, `elements` and `run --report` interfaces remain
available for prior evidence-report reproduction. `run` is the earlier guarded
report boundary; **`process` is the full workflow command**. Original historical
outputs are retained, not relabeled as current full-workflow results.

### Failure, recovery and sealing

Source and workflow stores reject skipped/corrupt/missing predecessors, orphaned
state without HEAD, symlinked destinations and changed retained batches/results.
Preserve damaged work, establish that a writer is inactive before removing a
stale lock, and reconstruct separately from verified retained inputs. Never edit
source records as repair. Power-loss durability is not claimed.

Workflow persistence and snapshot generation are separate phases. An interrupted
snapshot write blocks current-output verification and retains a journal/backups.
The workflow report may already be stored; this is not an assessed success.
Recover the writer, then retry the **same batch and original predecessor**:

```sh
.venv/bin/python -m credentialing recover-writer --root /absolute/path/to/interrupted/workspace --schema snapshot.schema.json
```

Recovery refuses files changed outside the transaction. Preserve and investigate
rather than overwrite those changes. Synthetic tests prove failed write → blocked
verification → exact rollback → unchanged workflow retry → valid snapshot.

Only Git commit seals a snapshot. The writer retains unchanged reruns; a changed
sealed occurrence needs a new ID, exact archived bytes, a reason and regeneration
of every later occurrence. Read the archive path/hash index to locate old chain
bytes; their original predecessor paths are never rewritten.

### Handoff and publication

Required Skill/docs/rules/run log/verification and the one authentic interview
are present locally. Full actual schema snapshots remain absent with precise
per-field reasons. G1/G2 and scoped source issues are human work, not a reason to
leave the remaining software unfinished. [Verification](deliverables/verification.md)
links actual and conditional evidence; [run log](deliverables/run-log.md) names
commands, consumed/produced artifacts and failures. Inspect the real outputs;
display and passing tests are not acceptance.

The original public fork is preserved, while the starter says to use its
template. On October 22 the learner authorized a separate private publication at
`BeckhamGT/practitioner-credentialing-submission`, including the authentic
interview, history and genuine Entire records. Entire explicitly targets that
private repository; its supported git-refs backend is retained. The assignment's
capture-branch wording is disclosed; no capture branch is fabricated. See the
[submission handoff](docs/submission-handoff.md) and
[preflight evidence](docs/audit/private-publication-preflight.json).

Private publication, demonstrated remote synchronization, facilitator access
and Classroom submission are separate checks. The final publication receipt
pins the exact published commit and advertised checkpoint objects. Facilitator
identity/access remains unavailable; the learner asked to skip that step for
now, so Classroom submission remains pending. The learner owns actual choices
and final review; put any choice/reason early in a turn (first 600 characters).
