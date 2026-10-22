# Independent element and writer review

This milestone is implemented and locally checked within its stated scope. It
is shown for learner review, not accepted, published, submitted or graded.

## Actual results

All three reports use their export date and exact predecessor evidence chain.
They preserve original correspondence/dispositions and reported decision outcomes.
They are internal evidence assessments, not schema snapshots.

| Batch / clock | Current report | Applications | Declared gaps ≥30 / ≥180 days | Decisions: proven refusal / evaluation blocked |
|---|---|---|---|---|
| 1 / 2026-03-16 | [Batch 1](../deliverables/assessments/batch-01-elements-1afae619a1e6.json) | 40 | 4 / 1 | 0 / 6 |
| 2 / 2026-04-20 | [Batch 2](../deliverables/assessments/batch-02-elements-cf7c99c0984a.json) | 40 | 4 / 1 | 2 / 33 |
| 3 / 2026-05-18 | [Batch 3](../deliverables/assessments/batch-03-elements-c6a4eef414e0.json) | 40 | 4 / 1 | 2 / 54 |

Reports cover Washington joins/status/expiry observations, other declared licence
observations, revision-context source replies, education/training/experience
comparisons, certification and privilege components, peer fields/prose, PPQ
answers and actual human documents. A returned field is not a final element pass.
The final schema projection remains unknown; evidence tasks have MSP ownership
and no invented deadline. Original outcome assertions do not create admissions.

Inspect [original selected rows and documents](../deliverables/assessments/source-comparisons.json)
beside the reports. Exact source IDs, file hashes and row numbers are retained.

1. **APP-2026-017:** ENT-1702/1703 end 2019-03-31; ENT-1704 begins
   2019-11-06. Inclusive missing dates are April 1–November 5, **219 days**.
   The February 13 explanation covers that interval. The April 2 Clinical
   Director disposition cites February 24 instead. G5 remains a provenance
   anomaly; no missing letter is invented and the finding/history is retained.
2. **APP-2026-018:** ENT-1802 ends May 1, 2024; ENT-1803 starts June 2.
   May 2–June 1 is **31 days**. No explanation exists at batch 1. Batch 2's
   March 30 letter covers the interval, but says Harrowgate and end of April,
   whereas the declared row says Silverbeck and May 1. G8 now flags that precise
   conflict. Coverage does not decide adequacy or silently change declared dates.
3. **APP-2026-030:** revision 2 changes ENT-3002's end from 2022-08-31 to
   2021-11-30 and adds ENT-3090 (2021-12-06–2022-09-05). The report recomputes
   all intervals; these changes create no ≥30-day gap. Older replies retain
   their revision context; this is not a reuse or CV-reconciliation approval.
4. **APP-2026-031:** the original four identity fields have no Washington
   board match in batch 1. Batch 2 has MD60251004, issued April 2 and looked
   up April 16. Batch 1 never borrows that later evidence. This specific
   missing-row meaning comes from E; it does not make unavailable forms/CVs fail.
5. **MEC-2026-036 and GBD-2026-034:** compare the original body/outcome and
   application revision. Body-authority and applicant/revision are the two
   proven first failures. All independently supported conditions are displayed,
   including reason requirements. GBD-2026-037 has blank Supersedes and an
   earlier received GBD-2026-036, but earlier admission is unknown: no later
   supersession refusal is claimed ahead of missing packet prerequisites.

## Independent verification and resilience

[Independent evidence](../deliverables/assessments/independent-verification.json)
uses only stdlib and original CSVs, with daily set subtraction rather than the
runtime interval-union algorithm. All **120** application/batch gap and WA-join
comparisons match. Export clocks match retained manifests and original READMEs.
The check does not establish reconciliation, completeness or clinical adequacy.

Each pinned element evaluation was repeated with the batch-3 HEAD already
present; current report bytes matched exactly. Batch 3's previous state is batch
2's retained hash. Protected original schema/interview/source/report bytes and
accepted-store HEAD are checked separately. There are **114 passing tests**;
that count is supplemental to actual-source verification.

[Synthetic writer proof](../deliverables/synthetic/writer-demo/proof.json)
demonstrates 1→2→3 generation, exact predecessor hashes, unchanged rerun,
rejected incomplete downstream regeneration, three retained superseded byte
copies and new IDs, then regenerated current chains. An explicitly injected
batch-2 filesystem failure blocks verification, restores exact prior outputs
through journal recovery and succeeds on retry. Refusals survive. These fixtures
assume complete synthetic intake; they establish no supplied-applicant outcome.
Archived predecessor paths remain byte-unchanged; history/index.json maps each
original path plus hash to its retained occurrence. Only current chains use the
new predecessor hashes. The demo is sealed only by the subsequent local commit.

The actual `run` command retains the independent report then exits 3
`snapshot_unrepresentable`. All three attempts are logged. This is a blocked
assessed projection after successful independent checks, not a Partial result,
an applicant failure, or an admitted business deferral. No actual sealed
snapshot exists; none is presented as current after failure.

## Proposed unresolved-check treatment

[The detailed assessment](partial-representation-assessment.md) cites assignment
Submission states/Deliverables and schema status, packet_presentable, admitted
and action_queue definitions. Its concrete **proposal only** uses
`status: in-verification` plus an MSP task to obtain revision-linked signed/dated
application and CV or explicit authorized export representation, `due: null`.
The task is truthful; **the status is rejected** because complete intake is
unproved. Required packet/admission booleans also cannot mean unknown. Existing
schema fields therefore do not truthfully represent this particular partial
case. The schema remains unchanged; no paths are filled merely to satisfy a list.

## Deliverables and remaining work

| Required deliverable | Current state |
|---|---|
| Authentic final interview | Complete local byte preservation/history; remote access pending |
| Skill and supporting code | Partial: evidence workflow, conditional kernels and writer exist; full business-state projector unfinished |
| README | Current setup/commands/results/recovery/handoff documented; final full-run demonstration pending |
| Rules register | Complete for applied behavior; future implementation must extend it |
| Verification report and run log | Current bounded milestone documented; full lifecycle coverage incomplete |
| Three required assessed snapshots | Blocked; absent for the precise schema/evidence conflict above |
| Genuine capture | Verified against commit 012f589738abaa5803a3f10901011691369137da and checkpoint 01M5H4CZAGHEBN7X1QX6W1H993; remote syncing/access pending |

**External evidence gaps:** G1 actual signature/date-to-revision evidence; G2
actual current CV/version and reconciliation representation, or an explicit
authorized export convention. MSP owns the direct working revisions-folder or
document-set link. G3–G8 stay scoped to the records/rule branches in the audit.
Publication/access and installed checkpoint-ref versus capture-branch acceptance
remain separate learner/facilitator prerequisites.

**Implementation gaps:** nine-condition completeness/revision reconciliation
adapter; final per-element states and evidence reuse at presentation; final
owned business queues including actual notices/escalation/terminal effects;
packet history and decision/condition/activation integration into a complete
state projector. These are distinct from external missing facts. Independent
branches and synthetic dependent verification remain authorized; G1/G2 are not
a blanket stop. The writer API exists but cannot substitute for that projector.

Shortest path: obtain the precise document set/export convention; review any
newly supported dependent approach with the learner; finish the remaining
projector and actual lifecycle checks; show real batch 1 and independent source
comparisons for learner inspection before continuing assessed batches; then
complete final review and approved publication/capture access. Classroom needs
separate explicit authorization.

For this review, inspect the five comparisons above and the rejected status
proposal. No learner approval is recorded. Any actual choice and its reason
belongs early in the learner's own turn (first 600 characters); a learner choice
cannot waive the office rule or supply missing source evidence.

[Current capture proof](../deliverables/assessments/capture-proof.json) compares
Git-stored full session bytes with the genuine CLI export and checks actual user
and tool records. It is recorded after the associated implementation commit.
All publication and facilitator-access claims remain pending.
