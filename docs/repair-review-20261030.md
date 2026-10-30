# Local repaired candidate — 30 October 2026

Ready for learner inspection of the bounded repairs. Publication, access changes and resubmission are pending. This is not acceptance of applicant outcomes or a claim that every assignment deliverable is complete.

## Version and preserved comparison

The graded baseline is `cbc1d70a40724f48d82aaf074c8bb2dc131fb7f7`. The pause save is `b105db66ff4746d499652e31e17d3839d225c921`. Both remain in unmodified history. Their original reports, interview, source archive and schema remain available and unchanged. The separate candidate reports are indexed by [deliverables/repair-20261030/workflow/current.json](../deliverables/repair-20261030/workflow/current.json). The paused reports under `repair-20261029` remain historical evidence.

The exact candidate commit is obtained with `git rev-parse HEAD` after the local candidate commit; the review response supplies its full ID. A document cannot contain its own commit hash. No code or checkpoint upload has occurred in this repair phase.

## Repairs and evidence

| Repair | Before | After / governing rule | Evidence |
|---|---|---|---|
| Contradictory source verification | An earlier matching reply could conceal a later contradiction and leave a packet presentable. A later matching reply could also implicitly select between conflicting source values. | Keep the affected entry in discrepancy until applicant amendment/reconciliation supports current-entry verification; preserve all replies. Other entries continue. P §§2,11. | Synthetic contradiction and subsequent matching-reply regressions; existing contact/date amendment recovery checks still pass. |
| Criteria-version binding | An approval naming an unavailable criteria version could be admitted under the loaded version. | Preserve independently proven ordered refusals; otherwise block positive admission when the cited policy is unavailable. Unsupported requested policy versions remain source review work. No guessed refusal or activation. PRIV introduction, I Oct 21 5:29 PM. | Synthetic decision-version and requested-version regressions. All 56 supplied decisions and 51 privilege-request rows cite LARK-PRIV-2026.1, so no actual admission changed for this fix. |
| Request resolution and follow-up | Raw receipt suppressed source chasing; qualification and satisfaction remained “not-evaluated.” | Separate receipt, qualifying current source response and satisfied current request. Applicant-carried material, partial replies and old replies to amended contacts do not satisfy the request; retain the first-three 21-day schedule and permanent attempts. A genuine discrepancy goes to applicant resolution, not an automatic source re-request. P §3 common verification rules, §2, I 6:06 PM. | Synthetic inadmissible, partial and amended-entry cases; independently checked actual APP-020/022. No new fourth-attempt deadline or sent notice. |
| Temporary eligibility referral | Pending degree/training verification could leave no Clinical Director question; a later reply could drop a prior question without establishing support. | Raise and retain the owned question while source-supported mapping is still unavailable. Withdraw it without a disposition only when verified evidence supports a requested group. Missing accreditation remains unknown; the office never discontinues a file. PRIV application rule 6. | Synthetic missing-training, later-supported recovery and still-unknown-accreditation cases; original-source comparisons for six actual files. |
| Existing outstanding state | An unknown source-review element could remain null and prevent otherwise supported individual application projection. | Use schema `outstanding` for owed review, with existing owner tasks; retain unknown `nothing_owed`, completeness, readiness and admission facts. S `/$defs/element_state`. | Synthetic missing-observation case; actual individually representable counts 3/3/2, previously 1/2/2. No full snapshots manufactured. |
| Durable attempts/current selection | Workflow processing and validation failures bypassed writer logging; current selection depended on an external wrapper. | Every process attempt with writable safe output gets a JSON receipt and latest-attempt pointer; consumed results update current.json. Failure preserves the last consumed selection and explicitly marks the latest attempt failed. Receipts retain arguments, batch/clock when known, consumed manifest, retained workflow and report, exit and error scope. An interrupted writer owns run-log.md until recovery; receipts persist immediately and pending log links flush on the next run. | Synthetic failure, retry, interrupted-writer rollback, prior selection and current-pointer checks. Actual fresh run receipts and rerun are saved separately. |

The original failing probes remain in [the October 22 audit](audit/resubmission-20261022/). Additional repair evidence is in [audit/repair-20261029](audit/repair-20261029/):

- `complete-regressions-graded-baseline.txt`: all 12 focused tests fail against a disposable checkout of graded code (9 assertions, 3 unavailable output/field errors).
- `complete-regressions-candidate.txt`: those 12 tests pass against the candidate.
- `tests-complete-20261030.txt`: full suite **157 tests passed**. Baseline coverage is retained; one former null-element assertion now checks `outstanding`, unknown `nothing_owed` and unknown packet readiness.
- `candidate-execution-log.json`, `candidate-baseline-results.json`, `candidate-reproduce.py`: real chronological prepare/stage/process commands, exact predecessor state/workflow hashes, export clocks, exits and rerun. Each actual process exits 3 because full assessed projection remains unsupported; workflow consumption succeeds.
- `candidate-independent-checks.json`: original CSVs and actual notice, 120 comparisons of revisions, referee counts/qualification and daily-set gaps; independently recomputed March 20 deadline. No product business imports.
- `candidate-source-verification.json`: separate CSV/graded-output checker confirms all 40 files in each batch, unchanged actual business outcomes, source-backed referrals, and APP-020/022 request satisfaction. Implemented in `tools/verify_repair_candidate.py`, outside the Skill's runtime.

The checks are complementary: output comparison detects regressions but does not establish source truth alone; the original-row checks establish the affected facts. Synthetic fixtures demonstrate unavailable actual branches without declaring actual applicants approved.

## Actual results to inspect

| Batch / export clock | Packet false / unknown | Refused / admission unresolved | Individually projectable applications |
|---|---:|---:|---:|
| 1 / March 16 | 24 / 16 | 1 / 5 | 3 |
| 2 / April 20 | 13 / 27 | 4 / 31 | 3 |
| 3 / May 18 | 6 / 34 | 4 / 52 | 2 |

There are 40 files per batch. All statuses, readiness booleans, admission results, approval IDs and activation/monitored-condition outcomes match the graded baseline. No actual approval or activation is established. New review work is the material actual change:

- Batch 1: APP-010 ENT-1001, APP-018 ENT-1801, APP-021 ENT-2100 and APP-032 ENT-3201 lack a returned degree/residency verification; APP-020 ENT-2000 has an applicant-carried diploma; APP-022 ENT-2201 has a state-medical-society reply outside ATT's accepted education sources. These independently establish the temporary referral's premises. This is not a signature/CV failure or an invented adverse clinical conclusion.
- Batches 2/3: the same six previously raised questions remain visible wherever verified support is still unproved. New verification alone does not erase the prior question while accreditation or source-route admission is unknown. The existing source review/accreditation tasks remain alongside it. Actual packet booleans remain unchanged; the pending question is not used to manufacture a new adverse outcome.
- APP-020: batch-1 `verification-replies.csv` row 53 is applicant-carried; batch-3 row 2, VR-2003 dated May 4, is the registrar reply. The degree request is satisfied only in batch 3.
- APP-022: VR-2201, State medical society — Cascade Valley Physicians Society, remains outside ATT's closed list through batch 3. Raw receipt remains visible; request satisfaction remains false. Three recorded attempts are retained; no invented fourth due date.
- APP-036: the revised contact/organization requires a current-entry response. Old source receipt does not satisfy that amended request; the later source response can recover that entry. Other resolved entries continue.
- APP-014/018 gain individually valid batch-1 application objects through outstanding review states; APP-014 gains that representation in batch 2. Their original refusals/returns remain. This does not reduce the required full-caseload snapshot scope.

Correct source identifiers: **GBD-2026-034 belongs to APP-036** (wrong revision), **MEC-2026-036 belongs to APP-038** (committee asserts approval), and APP-034 concerns deferral/referee correspondence with the recorded name-metadata conflict. APP-022 did not later obtain an admissible reply in the supplied batches. Historical documents are retained; these corrections govern current review.

## Remaining requirement gaps

All three required actual paths `deliverables/snapshots/batch-01.json` through `batch-03.json` remain absent. The reusable Skill, documentation, rules, reports, independent checks, logs and original interview are present. Actual snapshot/lifecycle evidence remains incomplete.

- **G1:** actual signed/dated application attestation and its application/revision association. The release date is not that attestation. MSP/source owner supplies usable documents or an explicit authorized export mapping.
- **G2:** actual CV contents/version at intake and reconciliation with the application and completed verifications. Receipt date is not contents; declared-history.csv is not an authorized equivalent. Current means most recent professional history at intake, without an age threshold.
- **Accreditation:** source evidence or authorized interpretation of degree/training completion rows as accreditation evidence. No accreditation pass is inferred.
- G3–G8 remain scoped as in the readiness audit: reference anniversary boundary, APP-034/029 name metadata, APP-017's missing cited explanation, one-component privilege wording, unspecified further attempts, APP-018 narrative reconciliation. Independent work continues; no source record is silently corrected.

The unchanged schema requires an established status and non-null readiness/admission booleans. Partial still requires a truthful snapshot for the consumed caseload. These reports cannot be labeled Supported or conforming Partial, and their internal `blocked-at-schema-projection` label is not the assignment's Blocked state (batch could not be consumed). Deferred requires its real business record. Preserve actual reports and owned work until evidence/conventions support projection.

## Capture findings and prepared synchronization

The [62-record investigation](audit/repair-20261029/checkpoint-investigation.json) establishes that local object `dbb34c3ca90d8fb20f575708b9c2f28c4c1df789` is the direct child of remote object `a034371d10d65d5f509de65533f0855de920205f`. The remote points to the initial 05:07:19 EDT checkpoint; local finalized at 05:12:54. Every remote record is retained locally and the 62 additions run through 09:12:53 UTC. This is a later finalized checkpoint left unsynchronized; no evidence proves a network upload failure.

After publication authorization and destination/access review, refresh local/remote objects first, then the prepared fast-forward ref push is:

```sh
git push origin refs/entire/checkpoints/QC/01M5HDTRSACHMXCJWE604FV6QC:refs/entire/checkpoints/QC/01M5HDTRSACHMXCJWE604FV6QC
```

Do not force-push or reconstruct payloads. Read back the remote object and transcript hash, and similarly verify every genuine checkpoint associated with the candidate after session finalization. A successful code push alone is insufficient. This command has **not** been run during repairs.

The pause commit lacked a capture trailer. New local commit `0fb3fe183f52d7a2ad7c0459ebb9113ceb0c37f4` carries genuine checkpoint `01M65VXYD68RC0B137B0EBBW8Y`, whose actual stored payload contains the learner's repair authorization and resume request. This supplies a new traceable association without rewriting the pause commit. The final candidate must likewise have its real trailer and inspected payload; do not infer capture from configuration.

## Publication/access recommendation and learner review

Keep the candidate local until the learner reviews it. Both repositories were last observed public; no visibility operation was performed. The assignment's private-conversation restriction remains relevant despite earlier public publication authorization.

Recommended next arrangement: use an approved private non-fork destination containing full commit/interview/capture history, identify the actual authorized grading GitHub account or integration, and verify authenticated read access before changing the Classroom URL. The existing non-fork submission repository could serve after a reviewed visibility/access change if still suitable. Obtain course guidance on the template-origin discrepancy. A private copy does not retract public fork-network data; public exposure needs a separately approved remediation plan, potentially involving GitHub Support. Do not delete or rewrite public history without that approval. Unknown grader identity remains a concrete access prerequisite, not a reason to stop local repairs.

Inspect independently before deciding:

1. Compare APP-020 and APP-022 original CSV rows with the request satisfaction and action queues in all three candidate reports.
2. Inspect the six new eligibility-review queues against the supplied degree/training replies and PRIV rule 6. Confirm that no discontinuation, approval, notice or deadline was invented.
3. Check APP-014 refusals, APP-019's March 20 clock, APP-015's retained finding, APP-030/036 revision recovery and APP-031's later WA evidence against their original sources. Verify that batch 3 did not repair earlier reports.
4. Inspect the synthetic failing/passing examples and failure receipts; they establish software behavior only. Confirm original assessed snapshot paths are still absent and that limitations are disclosed.
5. Review the privacy/access proposal and state your actual choice and reason directly at the start of a chat turn. Showing these outputs does not record approval. Publication and resubmission require a later explicit instruction.

No grade estimate or allocation to private evaluator checkpoints is made.
