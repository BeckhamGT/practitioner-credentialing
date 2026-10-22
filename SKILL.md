---
name: practitioner-credentialing
description: Review Larkhollow initial-appointment export evidence across batches, retain provenance and decision records, and expose unresolved human-owned work.
---

# Practitioner credentialing

Use this repository from its root with the Python CLI in [README.md](README.md).
This version performs evidence review and continuation. It is **not yet the full
intake-to-activation implementation**. Its outputs cannot replace the assignment's
three assessed snapshots.

## Inputs and scope

Take one authorized physical export folder with `input.manifest.json`, the exact
predecessor state SHA-256 when continuing, and the pinned rule/source bundle.
The manifest names exactly the thirteen CSVs, README and indexed supporting
documents. Read actual document bytes, not merely correspondence subjects.

Read [the rules register](deliverables/rules.md) for rule origin, source sections,
and implemented versus conditional behavior. Before assessing completeness or
using a new clarification, read [the unresolved source register](docs/readiness-audit.md#unresolved-gaps-and-contradictions).
G1/G2 currently lack actual signed-application/CV evidence or an authorized export
representation. Keep these unknown. A receipt date or blank template supplies
neither a case pass nor an applicant failure.

## One batch and continuation

1. Follow README setup. Verify the supplied batch manifest with `check-input`.
   Its export date is the business clock, not the host date.
2. Stage exactly the next batch using the explicit predecessor shown in README.
   Keep the accepted store and historical source bytes. Stage receipts mean
   evidence retained, not complete intake or an assessed snapshot.
3. Run `review` for independent source-class, date and authority-prefix checks;
   run `timeline` for revisions, recorded attempts/replies and the decision register.
   Run `elements` for declared-history gaps, licence observations, source replies,
   privilege components, peer fields and all independently checkable decision
   conditions. README supplies the exact pinned rule/hash and state commands.
   Pin the requested state even when HEAD is newer. Keep every received occurrence,
   original outcome, refusal and provenance reference.
4. Inspect actual output against the linked original source rows/documents and
   independently check a meaningful quantity. Show the learner a real milestone
   with what to inspect; display is not acceptance. Record only their actual reply.

The exact commands and observed state hashes are in README. For a new authorized
batch, use the new manifest and the verified current state; do not reuse the
example's dates or hashes as if they described a different input.

## Authority and conditional behavior

The five reserved judgments and their owners are in the rules register. Preserve
both sides of discrepancies and authentic returned dispositions. A recommendation
does not become an approval; a record asserting a role does not establish it.

An independently proved early admission failure may be refused now. Otherwise
leave admission unevaluated until the required prior revision-bound packet is
supported. `admitted: null` occurs only in the internal evidence-review format;
it is never a new value for the published snapshot schema.

`credentialing/conditional.py` contains kernels exercised on labeled synthetic
fixtures. There is no CLI route applying them to supplied applicants. In particular,
synthetic completeness/CV facts and readiness results never authorize a real
decision or activation. Return to the learner before integrating newly supported
dependent business logic. Continue independent work while a scoped gap remains.

## Outputs, failure and rerun

Evidence review JSON lives under `deliverables/evidence/`; the independent
element reports live under `deliverables/assessments/`, with `current.json`
selecting the latest retained report occurrence per batch. Separate synthetic
results live under `deliverables/synthetic/`. None is an actual assessed snapshot.
The original schema is [snapshot.schema.json](snapshot.schema.json); `verify-snapshot`
checks its structure and selected cross-file relationships, not business truth.

Use [verification](deliverables/verification.md) and [run log](deliverables/run-log.md)
to distinguish observed results from unfinished work. A failed operation returns
nonzero, records its scope and leaves the last verified state intact. It must not
present old output as the current successful result. An unchanged stage/rerun keeps
the same evidence state and report bytes. Preserve damaged state for diagnosis;
recover only from verified retained evidence in a separate reconstruction when needed.

`run` with pinned state/rules and a separate `--report` preserves the independent
assessment, then exits 3 `snapshot_unrepresentable` while required schema facts
are unknown. This is neither Partial nor an admitted business deferral. Read
[the schema conflict and rejected status proposal](docs/partial-representation-assessment.md).
Never populate `deliverables/snapshots/` to bypass missing evidence.

`credentialing/writer.py` implements local schema/chain-gated generation,
unchanged reruns, byte-preserved supersession and downstream regeneration. It has
synthetic demonstrations only; a complete business-state projector is unfinished.
Only a Git commit seals a generated occurrence. The writer never commits or
publishes remotely. Its transaction journal is internal control state, not a
business outcome. An interrupted transaction blocks current-output verification.
After preserving and inspecting it, use `recover-writer --root <workspace>
--schema snapshot.schema.json` to validate journal/backups and restore prior
working outputs. If the current files differ from both prior and planned bytes,
recovery refuses to overwrite them; preserve the evidence and investigate. After
recovery rerun the same authorized input. Never remove a lock until its writer
has been shown inactive. Power-loss durability is not established.

## Handoff boundary

Keep one authentic final cumulative export per interview session, retain superseded
bytes in Git, and leave originals unchanged. The learner conducts interviews; this
Skill identifies missing evidence but does not draft or automate that interview.
Keep genuine capture associated with meaningful commits. Publication, capture
syncing and Classroom submission remain separate pending actions requiring the
learner's publication/submission authorization and the approved access arrangement.
