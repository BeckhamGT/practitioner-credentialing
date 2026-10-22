---
name: practitioner-credentialing
description: Process Larkhollow initial-appointment export batches with persisted evidence, scoped human review, owned queues, chronological decisions and guarded credentialing snapshots.
---

# Practitioner credentialing

Run from this repository root using [README](README.md). This Skill implements
the dated workflow and writer. A usable implementation does not imply that its
supplied applicants have enough evidence for complete assessment snapshots.

## One batch and exact predecessor

1. Read the [rules register](deliverables/rules.md), original schema and current
   [source audit](docs/readiness-audit.md). Use one authorized physical batch
   manifest, its export date, pinned rules and the exact preceding state hashes.
2. If needed, materialize only the reviewed manifest's batch using the README
   preparer outside business runtime. `stage` retains original bytes; it is not
   a completeness pass. Never load the combined archive into a batch runner.
3. Invoke `process` with evidence store/state, separate work store, pinned
   element rules/hash and `--previous-workflow` for later batches. README supplies
   exact three-batch commands. Batch 3 must resume batch 2. Do not replace missing
   or corrupt predecessors with an empty run.
4. Read stdout's workflow hash/report and assessment result. Exit 3 can mean the
   workflow report was retained while its schema projection is blocked; it is
   not an approved business deferral. Continue independent work from that exact
   workflow receipt. Exit 2 requires failure investigation. Exit 0 means a
   generated/unchanged schema result, not acceptance or submission readiness.

## Evidence and authority

Preserve raw sources, original outcomes, refused records, revision bindings,
request attempts and prior workflow objects. Re-evaluate changed entry fields,
current licence/peer dates and affected elements; unrelated checks continue.
Retain readiness and disposition history when an element reopens or a file ends.

Separate established results, missing evidence and synthetic assumptions. A known
false necessary condition may disprove readiness independently of another
unknown. Missing signature/CV evidence is neither an applicant omission nor a
pass. G1/G2 remain MSP-owned human review tasks with due null absent a record.
Do not invent a written notice, clock, source class, age threshold or approval.

Five judgments remain human: gap explanation adequacy; disqualifying finding;
eligibility discontinuation; appointment/privilege recommendation; and GB
approval/modification/deferral/denial. Check actual people, bodies, terms and
protocol against the roster. A role asserted in a record is not its authority.
Record the actual disposition; never write the learner's choice or reasoning.

For evidence absent from CSVs, use only genuine source-linked human records
conforming to [the MSP observation protocol](docs/human-observation-protocol.md).
The adapter permits factual checks and MSP source-route determination, not
reserved clinical judgments. It validates dated source references and roster
identity, not cryptographic authorship. No actual review record is fabricated.
Return to the learner before newly supplied evidence/conventions are adopted.

## Outputs and schema boundary

`deliverables/workflow/current.json` selects full actual-case workflow reports;
immutable object hashes link their predecessors. Reports contain six element
results, exact dependencies, source observations, owned queues, decisions,
activation/condition records and history. Null means unknown only in this
internal format. Use the unchanged schema's application definition where its
meanings are established. Never substitute a new enum or nullable boolean in a
required snapshot.

Only a fully representable caseload and assessed predecessor chain can generate
`deliverables/snapshots/batch-0N.json`. Otherwise retain the full report and exact
unmet fields. No application is omitted to force a batch through. Partial needs
an actual schema-valid snapshot; deferred needs an admitted GB business hold.

`deliverables/synthetic/workflow-demo/` contains the separate invented SYNTH-only
end-to-end package. Its source assumptions/positive results do not establish
facts for supplied applicants. Mixed synthetic/actual application inputs are
rejected. Lower-level historical reports remain under evidence/assessments.

## Rerun, failure and recovery

Unchanged latest-batch `process` retains workflow identity and snapshot bytes.
Replay an earlier chain in a new store, preserving the old one. Changed closed
inputs/retained results never overwrite original state. If HEAD is lost while
objects remain, or a file/hash conflicts, preserve and investigate; reconstruct
separately from verified retained evidence. A stale lock requires proof its
writer is inactive before manual removal.

Snapshot writer transactions keep exact prior/planned bytes and block
verification after interruption. Workflow state may already have advanced;
that is not an assessed success. Inspect, use `recover-writer --root <workspace>
--schema snapshot.schema.json`, then retry the same batch and original workflow
predecessor. External file changes are never overwritten by rollback. A failed
later run must not advertise an earlier snapshot as its current success.

Git commit seals a snapshot. Unchanged reruns keep it. A changed sealed occurrence
gets a new ID, archived original bytes, a recorded reason and regenerated later
chain. Use the history path/hash index; never rewrite old predecessor bytes.
Power-loss durability is not established by these local tests.

## Verification and review

Inspect [current verification](deliverables/verification.md),
[run log](deliverables/run-log.md) and [review guide](docs/workflow-review.md).
Compare actual source rows/documents and recompute a meaningful quantity with
`tools/independent_workflow_checks.py`, outside the workflow implementation.
Use the synthetic CLI demo and exception/failure tests for conditional branches.
Tests, schema checks and output display do not replace actual-case evidence or
learner review. Record only real feedback; put learner choices/reasons early in
their own turns because the first 600 characters are assessed.

Keep the authentic final interview byte-unchanged and preserve superseded Git
history. The learner conducts interviews; this Skill neither drafts nor automates
them. Verify genuine Entire payloads for meaningful local commits. Keep material
local until publication/access is authorized; remote syncing, facilitator access,
Classroom submission and grading are separate pending states. No facilitator
contact or repeated unchanged inventory search is required for current software.
