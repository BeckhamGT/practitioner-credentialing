# Project E independent recovery audit — 22 October 2026

Review artifact, not acceptance, a new assessed result, or authorization to resubmit. The implementation and sealed history are unchanged. This audit challenges earlier completion claims; historical receipts remain evidence of what was checked then, not guarantees of current state.

## 1. Baseline and what the score can tell us

Local `main`, fresh public remote `main`, and Tacitt's “View on GitHub” graded revision all identify **cbc1d70a40724f48d82aaf074c8bb2dc131fb7f7**. The working tree was clean at audit start. Google Classroom currently says **Turned in**, with the original repository attached. Tacitt records one attempt, submitted October 22: **109/130 met, 2 not met, 19 no evidence; 83.8/100, Passed**. Earlier “submission pending” documentation is stale. No submission/unsubmission action was taken in this audit.

Tacitt explicitly describes the score as the share of 130 checkpoints met. Thus 124/130 is 95.4 and 129/130 is 99.2 after rounding: 15 or 20 additional met checkpoints respectively, **provided existing credit is retained**. The individual checks and category achieved counts are private. The 19/99/12 Automation/Workflow/Artifact totals do not identify which checks were missed. Roadmap skill assessments and session maturity are separate displays, not evidence of the challenge's missed points. No finding below is asserted to be one of the two privately failed checks.

Reproduction, in a new isolated directory, produced:

| Check | Fresh result |
|---|---|
| `.venv/bin/python -m unittest discover -v` | 145 tests; 2.246 seconds; OK, exit 0 |
| Source preparation, stage, workflow process for batches 1→2→3 | All source states and all three workflow report hashes match the published baseline; full report bytes identical |
| Batch 3 rerun | Unchanged state/report |
| Independent original-source checker | 120 application/batch comparisons pass: revisions, incremental referee names, qualifying returned fields, inclusive gaps; APP-019 calendar deadline independently matches |
| Retained synthetic snapshots | All three pass the original schema and cross-file verifier |
| Fresh synthetic workflow | Packet-presentable → approved-not-yet-effective → active-with-conditions, with continuation and rerun |
| Failure/recovery and sealed supersession tests | Re-executed in the test suite; synthetic, not claims of real applicant failure or approval |
| Required actual snapshot paths | All three absent, as disclosed in the passed submission |

Detailed commands, UTC execution times, exits, hashes and observations are retained in [the audit evidence directory](audit/resubmission-20261022/). Full disposable replay inputs/stores/stdout remain under `.local/resubmission-audit-20261022/`; they do not replace retained stores or selected outputs. Tests verify many correct branches but did not detect the defects below.

| Actual batch / export clock | Packet false / unknown | Proven refusals / unresolved admissions | Existing individually projectable files |
|---|---:|---:|---:|
| 1 / 2026-03-16 | 24 / 16 | 1 / 5 | 1 |
| 2 / 2026-04-20 | 13 / 27 | 4 / 31 | 2 |
| 3 / 2026-05-18 | 6 / 34 | 4 / 52 | 2 |

Every report carries 40 files. No actual approval or activation is established. The synthetic demonstration remains distinct from this table.

**Most plausible explanation of the uncredited work:** three required assessed artifacts are demonstrably absent; actual-case evidence for much of the downstream lifecycle is consequently unavailable; several reusable workflow branches have defects or incomplete operational evidence; publication/capture and handoff have specific compliance gaps. These are stronger explanations than “we need more tests,” but their allocation to the 21 private checkpoints is unknowable. A successful synthetic path cannot establish the supplied applicants' appointment outcomes.

## 2. Confirmed software and evidence gaps

Four isolated diagnostic probes expose behavior beyond the previous test suite. They use expressly synthetic facts and temporary stores. [Probe code and observations](audit/resubmission-20261022/diagnostic-probes.json) are audit evidence, not supplied-case results; no product fix has yet been applied.

| Finding | Root cause and reproduction | Source and consequence | Scope / proposed correction |
|---|---|---|---|
| D1: Later contradictory verification can remain resolved | `credentialing/workflow.py:123–134` treats any matching reply as sufficient and tests discrepancy only when no matching reply exists. A later admissible correction to an employment start date leaves the old match, `experience=resolved`, and packet true despite the retained contradictory reply. | P §2 requires both values retained and applicant resolution; P §11 reopens affected work. | High correctness risk. Reopen the affected entry when usable evidence conflicts; retain both records and do not pick the corrected date automatically. Original CSV review finds multiple replies only for APP-020/036/021, with no instance of this exact later-date-correction pattern. Confirmed reusable defect, not a newly proven actual-case misdecision. |
| D2: Cited criteria version is ignored | A synthetic GB record citing `SYNTH-UNAVAILABLE-VERSION` is admitted and creates an approval/activation schedule using the available LARK-PRIV-2026.1 rules. | PRIV introduction requires decisions to remain bound to their cited version; I 5:29 PM addresses applicable versions. | High correctness risk. Validate request/decision policy binding; missing cited policy is unresolved evaluation with an owner, not automatic refusal. Independent parsing found **all 56 actual decisions and all 51 privilege-request rows cite LARK-PRIV-2026.1**. Current actual case version mismatch is not established. |
| D3: Inadmissible material suppresses scheduled source chasing | `timeline.request_history` leaves `reply_qualifies` and `request_satisfied` as “not-evaluated.” `workflow.finish_case` schedules attempts only when no raw reply exists. In the probe an applicant-carried diploma after one registrar request suppresses the required next source attempt; generic source-review tasks remain, but their due dates are null. | P §3 common admissibility/attempt rules, ATT education row; I 6:06 PM distinguishes verification attempts and the applicant clock. | High operational gap. Evaluate whether the intended source request is answered, separately from whether material arrived; maintain the first three required attempts and appropriate unresolved tasks. Do not invent a fourth-request deadline. APP-020 and APP-022 exhibit the raw-receipt/status distinction; each already has three attempts in batch 1, so the missing second-attempt consequence is demonstrated synthetically, not attributed to them. |
| D4: Pending verified-training support misses a CD question | `workflow.py:344` raises eligibility only if every group is classified unsupported. Removing a training reply from an otherwise supported synthetic file produces unknown support and no Clinical Director action. | PRIV “How the office applies the table,” rule 6 explicitly places the question with the CD while nothing yet verified supports any requested group, and withdraws it when later verification supports the request. | Add the temporary owned referral for this supported situation; never compute discontinuation. Missing export accreditation facts and the one-component wording conflict must not be collapsed into a proven adverse finding. APP-027 already has a referral in batches 1/2; it is not evidence of this specific missing-referral defect. |

Two additional artifact/operational improvements are supported:

- **D5 — Element representation is too conservative.** The schema defines `outstanding` as something still owed. Pending source/admissibility/accreditation review can use it with an explicit human task, without declaring applicant failure. A diagnostic copy mapping only unknown element states to `outstanding` validates 3, 3 and 2 individual applications in batches 1–3, versus 1, 2 and 2 now. It does not settle unknown intake status, readiness or decision admission, and is not a full snapshot. See §3.
- **D6 — Routine attempts need durable run receipts and current-result selection.** `processor.process_run` returns exit 3 before invoking the snapshot writer; early validation errors also bypass that writer's log. Existing wrapper logs honestly record historical runs, but the documented process command alone does not append every failure/projection outcome to `deliverables/run-log.md` or maintain `deliverables/workflow/current.json`. Add a durable attempt ledger and explicit result-index updates, preserving failures and distinguishing the last sealed snapshot from the latest attempted run. Test disk/validation failure and recovery; do not relabel exit 3 as the assignment's Blocked state.

The full [requirements-to-evidence matrix](resubmission-requirements-20261022.md) distinguishes verified actual work, conditional demonstrations, implementation defects and external dependencies. It is a published-requirement coverage map, not a reconstructed private rubric.

## 3. Can we legitimately recover the actual snapshots now?

**Not all three complete 40-file snapshots, with the present evidence and unchanged schema.** There is a narrower representation improvement, but no valid global substitution.

Sources: [assignment](https://docs.google.com/document/d/1HhmU8Jay09XHDci38hl9ZOX_dMryaSv4aFLCPu1Nk-E/edit), “Submission states,” “Deliverables,” and cross-file rules; [schema](../snapshot.schema.json), `/$defs/application/properties/status`, `packet_presentable`, `decisions/items/properties/admitted`, and `/$defs/element_state`; P §§1–2 and 8–9; E “What I do not export.”

| Required meaning | Why it remains unavailable | Smallest authoritative resolution |
|---|---|---|
| Intake complete, required by `status=in-verification` | G1: application signature/date and revision association are absent from the accessible supplied inventory. `release_signed_date` is a different authorization. The blank form only establishes layout. | MSP supplies direct usable signed-form/revision links, or an explicit authorized export convention identifying what proves the application attestation for each revision. |
| CV current / reconciled | G2: `cv_received_date` proves receipt only. I 11:51/11:54 PM defines current history and comparison; I 12:22 AM claims CVs accompany revisions, but the folder is not in the supplied inventory. `declared-history.csv` has not been declared equivalent to reviewed CV contents. | CV/version linked to each relevant application revision and supported comparison findings; or an explicit source-owner convention covering equivalence, currency, reconciliation, exceptions and temporal applicability. No invented age threshold. |
| Positive privilege support | PRIV requires accredited qualifying degree and training. Ordinary completed-degree/training rows do not expressly attest accreditation; the export guide provides no exemption. Current observation adapter can retain authentic supporting review evidence, but actual accreditation observations are absent. | Source evidence or an explicit authorized meaning for these exported education/training records. Preserve current-experience judgment for clinical leadership. This is an additional prerequisite, not another name for G1/G2. |
| `packet_presentable` boolean | Known unmet prerequisites establish false for some cases. Others have all known checks satisfied but missing completeness/reconciliation prerequisites: unknown is neither false business readiness nor true. Batch 3 has 34 such cases. | Resolve the factual checks, or obtain an authoritative assignment/export treatment. An engineering preference cannot make these booleans truthful. |
| Every `decisions[].admitted` boolean | 52 batch-3 received decisions lack established prerequisites. Four proven refusals are retained; uncertainty cannot be turned into refusal or admission. | Resolve the prerequisites as knowable at the decision time, while preserving ordered conditions and prior refusals. New information must establish historical facts or a valid historical convention, not retrospectively borrow later-batch evidence. |

G1/G2 are not applicant failures. No written missing-items notice or running clock can be invented. A withdrawn/discontinued/independently refused file can have a supported status while other fields still prevent its complete serialization. A subset of projectable files is not the required caseload.

**Proposal only — APP-2026-014, batch 1:** retain `status: "decision-inadmissible"` and `packet_presentable: false`, supported by MEC-2026-024's insufficient qualifying references at its decision date. Use `elements.certification: "outstanding"` for its unresolved support review. Keep the actual refusal reason, known element states and all real G1/G2 tasks. One proposed queue entry is:

```json
{
  "item": "Obtain the signed and dated application for APP-2026-014 revision 1 and its associated current CV; confirm revision binding and record comparison with the application and available verifications. Export receipt dates do not establish these checks.",
  "owner": "Medical Services Professional",
  "due": null
}
```

This owner and next action are supported; no deadline is supplied. A separate support-review task must retain the missing accreditation evidence. [The full proposed application copy](audit/resubmission-20261022/proposed-APP014-batch1.json) passes the application fragment's unchanged schema. This is neither a sealed assessed snapshot nor a learner-approved business result. The proposed element mapping yields APP-014/018/019 in batch 1, APP-014/019/029 in batch 2, and APP-019/029 in batch 3. Later APP-014 reference evidence does not repair its earlier refusals; by batch 3 its remaining readiness uncertainty prevents projection.

**Correct run classification:** actual workflow consumption and state continuation succeeded, but the required artifact could not be emitted. This is not Supported; it is not a conforming Partial submission because Partial still requires a full-caseload snapshot; it is not the assignment's Blocked state, defined as inability to consume the batch at all. `blocked-at-schema-projection` is an internal diagnostic label. Deferred denotes a supported business hold and the schema's `deferred` requires an admitted GB deferral. None is a generic fallback for missing export evidence. This is a genuine gap between Partial's general description and these non-nullable required meanings for these supplied records; preserve the separate actual reports and document the unmet requirement until source evidence/convention resolves it.

### Access investigation boundary

The earlier complete inventory checked the 13 supplied accessible locations, pagination, subfolders, shortcuts and supplied links: 124 batch file paths/IDs, no application-revisions folder, completed applications or CVs. Those locations listed successfully; this is an inventory/location mismatch, not a demonstrated permission denial. The final interview calls “Case records export” and “Batch export” the same directory, adding no alternate location. This audit reviewed the final interview and freshly read the assignment plus the procedure, accepted-source table, privilege criteria and export guide. The four refreshed policy readings differ from retained text only in extraction formatting/list numbering; no new signature/CV convention appeared. No identical folder search was repeated. Do not claim documents are absent everywhere in Drive.

The export guide's statement that clean files are clean is a teaching-set description, not a per-revision signature, CV or accreditation attestation. Its explicit outside-export exemption for referee addresses does not extend to other checks without source authority.

## 4. Actual sources and scoped issues

Original CSV calculations independent of product imports reconfirm **219 days** for APP-017 (2019-04-01–2019-11-05), **31 days** for APP-018 (2024-05-02–2024-06-01), and **2026-03-20** for APP-019's February 18 + 30-day inclusive deadline. The checker covers all 120 application/batch combinations, not just these examples. Additional source/document facts and actual report comparisons are in [additional independent checks](audit/resubmission-20261022/additional-independent-checks.json).

| Supplied scenario | Source comparison and bounded conclusion |
|---|---|
| APP-014 | MEC-2026-024 (Mar 10) and GBD-2026-024 (Apr 14) precede the second qualifying reference REF-1401, received May 8 in batch 3. Both refusals persist; the later reference cannot repair them. |
| APP-015 | Mar 4 board reply establishes a monitoring agreement. Apr 20 applicant confirmation belongs to batch 3; do not import it into batch 2. May 6 CD disposition allows presentation with evidence. Retain the licence finding even when its human hold ends; this does not itself prove whole-packet readiness. |
| APP-017 | Feb 13 explanation covers the independently recomputed 219-day interval. Apr 2 CD disposition cites an unavailable Feb 24 explanation. Retain the disposition and G5 provenance issue; do not invent the cited document or automatically erase the disposition. |
| APP-018 | Mar 6 return for unexplained gap; Mar 30 explanation in batch 2 covers the 31 days. Narrative employer/date details conflict with revision-2 ENT-1802/1803. Explained interval is established; full reconciliation is not. |
| APP-019 | Actual Feb 18 missing-release/CV notice explicitly states Mar 20. Intake-incomplete at Mar 16; clock-expired by Apr 20 and May 18. This is an actual documented missing-item clock, not a G1/G2-invented notice. |
| APP-020 / APP-022 | APP-020 applicant-carried diploma, batch-1 CSV row 53, is replaced as usable evidence only by registrar reply VR-2003 on May 4 (batch-3 row 2). APP-022's medical-society training reply remains inadmissible through batch 3. The request's suggestion that both later receive admissible replies is not supported. All attempts remain recorded. |
| APP-021 | Apr 8 most-recent-employer letter reports the school closed in 2019 and direct verification in 2005; Mar 24 FCVS record says no record. Retain this exact secondary-route evidence and the remaining MSP admission review; do not call nonresponse impossibility. |
| APP-025 | May 5, 2024 reference is stale at May 18, 2026 under either G3 boundary interpretation. The other reference approaches May 20. Preserve prior named referees across revision and flag the exact-anniversary conflict only where it matters. |
| APP-028 / APP-029 | Actual withdrawal and CD discontinuation establish terminal outcomes without invented appointments. APP-029 notice's recipient surname conflict remains G4 metadata work. |
| APP-030 | Source/declaration date discrepancy is retained; revision 2 changes declaration and adds locum work. Batch-3 verification supports that new entry. CV reconciliation is separately unresolved. |
| APP-031 | No initial WA row is a meaningful absence under E's explicit join contract; NPI/another-state licence is not a substitute. Later WA lookup supports the later batch only. |
| APP-034 / APP-036 / APP-038 | Correct the scenario IDs: **GBD-2026-034 belongs to APP-036**, citing revision 1 after revision 2 arrived Mar 30; **MEC-2026-036 belongs to APP-038**, whose committee cannot approve. APP-034 instead has deferral/referee correspondence and G4 name metadata conflicts. APP-036's changed employer/contact work reopens and its batch-3 reply supports the revised entry. |

| Gap | Current scope / next owner action | Work that continues and required regression |
|---|---|---|
| G3 | APP-025 exact two-year anniversary wording; MSP identifies controlling boundary or corrects letter. | Staleness at May 18 is established under both readings; test before/on/after anniversary, keep conflict explicit. |
| G4 | APP-034 To/From surnames and APP-029 notice recipient; MSP supplies linked identity clarification. | Matching application IDs remain visible; no guessed recipient, automatic adverse finding or global stop. Test provenance flag without rewriting text. |
| G5 | APP-017 disposition's cited Feb 24 explanation; MSP/CD identifies reviewed document or supplies it. | Gap length, supplied explanation and disposition remain recorded. Test narrow source discrepancy without pretending missing text was read. |
| G6 | Only one of certification/training holds, and missing accreditation support; MSP/clinical rule owner clarifies ambiguous unsupported classification. | Rule 1's positive conjunction, explicit CARD/board-eligibility clauses and rule 6's temporary CD routing can be implemented where their premises are known. Test partial support and later withdrawal of question separately; never compute clinical discontinuation. |
| G7 | General at-least-three attempts versus peer up-to-three then day-64 escalation; MSP clarification only for genuinely unspecified further-attempt behavior. | First three at 21-day spacing, permanent log, no silence-as-pass and peer substitution are confirmed. Test inadmissible/partial replies and extra requests separately; no invented fourth deadline. |
| G8 | APP-018 specific narrative/date/organization discrepancy; MSP reconciles with applicant/source, CD owns explanation adequacy where routed. | Explanation coverage and unrelated elements continue. Test written coverage independently of reconciliation and clinical judgment. |

## 5. Publication, capture and learner involvement

Fresh GitHub metadata reports **both** `BeckhamGT/practitioner-credentialing` (a public fork) and `BeckhamGT/practitioner-credentialing-submission` (a public non-fork) as public. Historical private-repository receipts are not current visibility proof. The assignment forbids making private conversations public; previous user authorization to publish does not establish assignment conformity. Both repositories need to be included in the remedy assessment.

GitHub states that a fork's visibility cannot be changed independently and that public fork-network Git data may remain accessible even after deleting a fork ([official fork documentation](https://docs.github.com/en/pull-requests/reference/forks)). Therefore “make the original fork private” is not a complete available fix. Recommended approach for learner review: establish a private, full-history destination with an identified authorized grader account/integration; verify authenticated access; then agree on public-material remediation and any necessary GitHub Support/fork-network action. A private copy alone does not retract already-public conversations. Do not delete the passed revision, rewrite history, change visibility, migrate, or alter the submission URL without approval. Prior private-repository access identity remains unknown. Tacitt's current graded public commit shows current integration reachability; it does not identify a private-repository grading principal.

The starter said **Use this template**, and GitHub confirms a fork was used. This is a procedural discrepancy, not missing code. Safest initial correction is a documented exception or approved destination procedure from the course; no retroactive assertion that the fork was a template. A new repository alone cannot erase the historical origin or confidentiality issue. Any migration must retain original commit/capture identities and be reviewed.

Capture verification is stronger than configuration alone:

- Entire 0.11.3 reports enabled Codex capture for actual session `01a15fd1-860f-7210-a8ec-b2a637129c5e`, correct worktree and main branch. Both project/local checkpoint settings and Git push defaults point to the original repository (`origin`), not `submission`.
- Fresh unauthenticated remote fetch reaches all **16** genuine local checkpoint refs. **15 match exact Git objects and full transcript hashes; one differs.** Latest checkpoint `01M5HDTRSACHMXCJWE604FV6QC`, associated with cbc1d70, has local object `dbb34c3ca90d8fb20f575708b9c2f28c4c1df789` versus remote `a034371d10d65d5f509de65533f0855de920205f`. Parsing confirms all remote JSON records are retained locally, plus 62 local records; byte differences also include JSON serialization. This is incomplete current payload synchronization, not absence of all capture. See [remote comparison](audit/resubmission-20261022/capture-remote-comparison.json) and [record comparison](audit/resubmission-20261022/capture-record-comparison.json).
- Implementation commit `3c03608ab0010f4873318492e158a36b38127005` carries genuine checkpoint `01M5HAKJS8PH3W4AQYQNJ71TBH`; local/remote full payload SHA-256 `ebc0a0107afd3c007122468bc6448da832cb17d3037a8d0ce9cc35970d1dbab4` matches. Earlier size/hash receipts are preserved as historical observations.
- The live genuine Codex transcript contains this new audit request at line 3428, timestamp `2026-10-22T19:20:29.931Z`. No new implementation commit was made in this audit; its new work is not yet represented by a new sealed commit checkpoint. Publication is deliberately not repeated while the confidentiality choice is under review. Verify the actual new commit/checkpoint and its remote payload after the approved route is established; do not infer syncing from a successful code push.
- The actual learner message stored in this turn contains an attachment reference, not the full “My decision and reasoning” paragraph inside its first 600 characters. The attached request is valid authorization, but future material choices should be typed directly at the start of the chat message so that assessment window sees them. Do not rewrite prior turns or invent learner rationale.

The required “capture branch” wording versus installed genuine `refs/entire/checkpoints/*` remains a format question; Tacitt has recognized one real session, which is positive evidence, not an explicit waiver of all handoff wording. Preserve genuine refs and document them; never manufacture a branch as substitute evidence.

## 6. Ranked implementation plan

These are estimated engineering effort/coverage relevance, not point promises. No product rewrite is needed. All fixes must preserve the passed baseline and produce separately identified corrected reports.

| Order | Work | Evidence / expected impact | Effort, regression risk and decision |
|---|---|---|---|
| Parallel prerequisite | Resolve signature/CV/reconciliation and accreditation representation with exact source owner; decide privacy/access remedy | Highest actual snapshot/lifecycle opportunity; no responsible estimate of checkpoint count | External timing unknown. Needs authentic evidence/convention and learner review; not a stop on safe code fixes. |
| 1 | Regressions and minimal fixes for D1 contradictory replies and D2 criteria-version binding | Explicit source rules; high correctness value across future cases | Medium, about 2–4 focused engineering hours including independent replay; moderate regression risk. Safe local implementation; unknown versions stay unresolved. |
| 2 | Complete request-resolution/follow-up semantics (D3), then explicit temporary eligibility routing (D4) | Real operational distinctions plus independently reproduced conditional failures; likely Workflow relevance | Medium, about 2–4 hours; moderate risk. Follow confirmed first-three and rule-6 behavior. Pause only any new fourth-attempt rule or expansion of missing-export facts into adverse findings. |
| 3 | Truthful `outstanding` element projection (D5) and complete owned queues | Supported schema improvement; makes additional individual files representable but not full caseload snapshots | Small–medium, about 1–2 hours; low/moderate risk. Show proposed/actual diff; never coerce unknown packet/status/admission. |
| 4 | Durable process/failure receipts, current-result index and accurate run-state documentation (D6) | Required Automation/Artifact evidence; prevents older success masquerading as latest result | Medium, about 2–4 hours; moderate transactional risk. Failure injection, rerun, recovery and produced-file checks required. |
| 5 | Full original-source replay and independent check expansion; fix current handoff claims without altering historical receipts | Demonstrates actual changes rather than code existence; corrects source IDs, submission state and coverage claims | Medium, about 2–4 hours. No whole-suite repetition without substantive changes; independently compare source-based expected deltas. |
| 6 | If authentic prerequisites arrive, process them chronologically and recover three full assessed snapshots; review before adopting new source conventions | Highest deliverable and downstream actual-case coverage opportunity | Cannot responsibly time before source scope is known. Preserve source availability dates, prior decisions and required sealed-occurrence archive chain. No silent repair of closed exports. |
| 7 | Approved privacy/access remedy, final capture sync/readback, learner review, then separately authorized resubmission | Submission compliance and verifiable code/capture pairing | Depends on platform/account identity and learner choice. No speculative grading gain claimed. |

Steps 1–5 can start locally without resolving G1/G2, subject to the narrow boundaries stated. This first response stops at the audit as requested. No fix is hidden inside a documentation change, and no new business interpretation is treated as approved.

## 7. Candidate acceptance and next learner decision

Insist on these before another attempt:

1. Each published requirement has a linked actual artifact/test/source check or an explicit residual limitation; all new defect regressions pass and existing credited behavior is preserved.
2. Required snapshots exist only if truthful: all 40 files, batch clocks, latest revisions, complete received decision history, first failed reasons, exact approved privileges/dates, owned work, correct predecessor SHA-256 links and rules/produced references. If still absent, disclose precisely that the candidate remains incomplete and decide whether the demonstrated improvement warrants resubmission.
3. Actual and synthetic results are separate. Independent calculations and original-document checks cover affected cases and the complete caseload, including temporal cutoffs, revisions, refusing authority, conditions, failure/recovery and reruns. Passing tests is not acceptance.
4. Original interview bytes, source hashes and historical outcomes are preserved. Closed source evidence is never rewritten. Corrected sealed snapshots, if any, use new IDs, unchanged archived occurrences and regenerated downstream chains.
5. A reviewed privacy remedy and authenticated facilitator/grader access are demonstrated; history/template deviation and genuine capture-ref format are accurately disclosed. No exposed material is assumed retracted merely because a new repository is private.
6. Exact candidate commit, all genuine associated checkpoint payloads and remote revision are freshly verified. Run log and handoff describe that revision, not older pending states. Classroom/Tacitt resubmission occurs only after learner review and authorization.

No numerical improvement is promised: 15 additional met checks is the arithmetic target for 95+, not an estimate that these fixes earn 15. Workflow is the largest published category, and actual snapshot/lifecycle evidence is the strongest coverage opportunity; private checkpoint credit remains uncertain.

**Material choice needed:** how to pursue the private-material/access remedy while preserving the passed public submission and its history. Recommended next step is to obtain an identified grader access route and course guidance on private delivery/template correction, while safe fixes proceed locally. The learner should state their own choice and reason directly at the start of a chat turn. This audit records no approval of that proposal, no final business acceptance, and no resubmission.
