# Independent record-review milestone

The learner explicitly accepted the groundwork milestone. That acceptance does not resolve G1/G2, approve business outcomes, or accept this subsequent milestone. This bounded extension was selected within the learner's authorization to continue confirmed-rule work independent of those gaps.

## Scope and independence

The new read-only `review` command checks recorded delivery-source classes, date-window facts, individual peer-reference fields, and the first two decision-authority conditions. Its inputs are an explicit evidence-state hash and separately pinned, versioned office rule/source text. It does not inspect a later HEAD, load the combined audit archive, fetch sources, modify retained state, or read later batch objects. A regression test demonstrates reviewing state 1 after a synthetic state 2 exists without opening the newer HEAD or state/blob objects.

These checks do not require a conclusion about whether an application is signed or its CV current/reconciled. They examine a particular reply's delivery route, recorded dates, returned reference fields and a decision's named body/signatory against independent office records. No positive check is promoted to file completeness, resolved element, packet readiness, admitted decision, active privilege or approved clinical judgment.

Source-class recognition is deliberately limited to explicit exported labels and named designated equivalents. Unrecognized formats, missing/ambiguous links and secondary/impossibility routes require source review; the code does not infer employer authorization, source closure or aliases from free text. Reuse of a reply after a revision is not evaluated. Individual peer-field checks are not a count of qualifying references and do not evaluate clinical recommendations. Both raw recommendations and comments remain available in the report. A date-window check at export is not a presentation-date conclusion. No rule is invented for a February-29 anniversary; such a calculation remains unknown if encountered.

## Applied rules and provenance

| Check | Governing source | Implementation limit |
|---|---|---|
| Applicant-carried material and closed source lists | [Accepted-source table](https://docs.google.com/document/d/1ze0RTP4H8J68FSqbFmkG7Qd_5cZiB6Lh2BfyU6v2Sj8/edit), cross-cutting rules and per-element rows; procedure §3 | Reports source-class facts, not complete verification validity |
| First-receipt anchor and source date window | [Procedure](https://docs.google.com/document/d/1v442U759TGLwnElS24xF1MmvovZjBSHy4KKe2Nl-GDk/edit) §8; export guide's export-date clock | First-receipt dates must agree across revisions and with revision 1. Unknown/conflicting anchor does not pass. Export-day inclusion is distinguished from strict pre-decision inclusion |
| Peer discipline, relationship, recent direct work and signature currency | Procedure §3 Check 4 | Individual fields at export only; no element/readiness or competency judgment; actual presentation currency remains unevaluated |
| Body/outcome and signatory/role/date | [Authority roster](https://docs.google.com/document/d/1Dvc3eJei4K7RyE8HZtZkMtRQNqE6VPQU8gUXVbps2xQ/edit), body table, role terms and 2026-01-05 designation; procedure §9 | Only the first two admission conditions; applicant/revision/packet/reason/supersession remain unevaluated |

The [pinned rules and source extracts](../references/record-review/README.md) are an explicit engineering transcription of LARK-MSO-2026.1, LARK-ATT-2026.1 and LARK-AUTH-2026.1. Their extracted-text hashes and semantic versions travel with every review. There are no case IDs or case answers in the implementation or rule configuration. All original sources and the final authentic interview remain unchanged.

## Actual results for review

[Full immutable batch-1 review](reviews/batch-01-record-review-63af121d5181.json): state `a2927aa3e86233b01b040efb68b5c3258db2aaec18b85708a63648a47b0ced8f`, clock **2026-03-16**, report SHA-256 `63af121d518196af97fcbd555728f1e99b0970ded015e879c9cc3ed960fda8f1`.

| Observed result | Exact source comparison | What it does not establish |
|---|---|---|
| 150 reply records reviewed: 148 match listed primary-source classes, one applicant-carried, one outside accepted list | 112 verification replies plus 38 certification replies in batch 1; each report item cites original file hash, batch and CSV row | Not 148 verified credentials or complete applications |
| VR-2000: applicant-carried | verification-replies.csv row 53 says Applicant — hand-delivered at intake, despite apparent registrar signature/seal; ATT cross-cutting prohibition | Does not delete the reply or compute an application status |
| VR-2201: not on accepted education-source list | verification-replies.csv row 58 is Cascade Valley Physicians Society; ATT Education and training lists neither that source nor state societies generally | Does not invent a substitute source or initiate a request |
| VR-3002: listed primary-source class with original discrepancy retained | verification-replies.csv row 82 retains confirmed-with-discrepancy and 2021-11-30 versus declared 2022-08-31 in its notes | Does not choose either date, reconcile CV, recompute gaps or resolve the discrepancy |
| 57 peer replies checked; earliest signature 2024-05-05 has second anniversary 2026-05-05 | RR-2500 signature, compared to export 2026-03-16 using procedure Check 4 | Not 57 qualifying references, a met element, or proof of presentation |
| Six MEC records pass the two authority-prefix checks | Actual six decision documents name Peter Vandermolen, Chair of MEC, recommended, with dates inside the roster term | Not six admitted decisions or approvals; all dependent checks remain not evaluated |

The earlier unreviewed diagnostic occurrence remains preserved at reviews/batch-01-record-review-1638d5576c72.json; the current occurrence explicitly labels the relationship box separately from unevaluated relationship prose. No source evidence changed.

There are no actual batch-2/3 results in this milestone. Their source conflicts remain scoped in the original audit and were not imported to alter the batch-1 review. The existing source records were neither corrected nor interpreted beyond the stated checks. No business action queue, missing-item notice, packet-readiness conclusion or assessed snapshot was written. `run` remains disabled by G1/G2 with exit code 3.

## Verification and independent checks

**55 tests pass**: the accepted 32 groundwork tests plus 23 record-review tests. New tests cover policy hash/version boundaries, delivery versus letterhead, subject/issuer matching, unknown links, source nonresponse versus impossibility, date endpoints, peer disqualifiers/unknowns, leap-day limitations, actual designation date/role terms, a body claiming an unauthorized approval without outcome rewriting, duplicate document metadata, review of earlier state in the presence of later state, unchanged state bytes, preserved discrepancy text, conflicting first-receipt anchors and CLI review with the business block retained.

[Independent checks](reviews/independent-checks.json) were computed separately with standard-library CSV, datetime, regex and hashlib, without importing implementation functions. Raw delivery-route counts are 36 registrar, 33 GME, 41 medical staff office, 38 certifying board, one applicant, one state society: 150 total. The three example source records were compared directly, and the six actual MEC documents were independently checked against the roster. The oldest signature's second anniversary is **50 days after the export date**. Rerunning the actual CLI produces identical report bytes and leaves evidence HEAD unchanged. The interview hash is unchanged and assessed snapshots are absent.

These checks support this bounded component only. They do not establish the full assignment's rule coverage or submission readiness. Secondary routes, final verification conclusions, reference counts, revision-based evidence reuse, complete decision admission, supersession, packet readiness, activation and business outcomes remain unimplemented or blocked as stated.

## Exact G1/G2 prerequisites — updated after the 11:54 PM follow-up

The later [complete interview](../interviews/project-e-practitioner-credentialing-20261022-0355.md) retains all prior turns. Its source-only update changes no reviewed result, policy configuration, runtime code or stored batch state. [Fresh folder-listing evidence](audit/interview-update-20261022.json) compares all supplied batch paths/IDs to the original inventory. These clarifications are shown for review, not accepted as business outcomes.

| Gap | Evidence or authoritative clarification needed | Source and consequence |
|---|---|---|
| G1 | Correct folder URL/access and authentic signed/dated application attestation associated with each relevant application revision, **or** an explicit authorized export contract identifying which supplied fact certifies that check and its revision scope. An authorized limitation is needed if intentionally unassessable. | Procedure §1 condition 1; [application form](https://docs.google.com/document/d/1nFdoz-AeCUTBzZUXrG27AKsNXCiJ_TJLLDI3WleiiB0/edit) §J. I 11:50 PM line 674 clarifies the signature/date check method. I 11:54 PM line 702 claims an application revisions folder per batch and says check results are internal. All 13 supplied folders list successfully, but no such folder/forms appear; all 124 batch file IDs/paths match prior inventory. This is a location mismatch, not an observed permission denial or proof of signature compliance. Completeness/readiness stay blocked. Owners: MSP/facilitator. |
| G2 — currency evidence | Actual CV contents/version showing the most recent professional history at intake, associated with the application/revision being assessed, **or** an explicit authorized export convention establishing that evidence and its limits. No numeric age threshold is sought or invented. | Procedure §1 condition 4; I 11:51 PM line 688 now supplies the qualitative meaning at intake. The definition gap is narrowed; cv_received_date alone still does not prove the criterion. No CV documents were found in the supplied trees. Owner: MSP; facilitator for export limitations. |
| G2 — reconciliation | Authentic CV contents/version sufficient for comparison with application and returned verifications, **or** an authoritative mapping identifying which exported fields preserve CV observations, differences and revision scope, with an authorized limitation if unassessable. | Procedure §2; export guide The files / What I do not export; I 11:54 PM line 710. The stakeholder identifies CV as declared professional history and describes comparing it. This does not expressly equate declared-history.csv with the CV or prove reconciliation for an application/revision. No such equivalence or case pass is inferred. Owners: MSP/facilitator. |

The published schema has no unknown-intake status, and intake-incomplete asserts a real written notice/running clock. The learner's milestone acceptance cannot supply missing facts or authorize invented notices, clocks, statuses or office rules. A source-backed permitted representation is needed before those branches proceed.

G3–G7 remain in [the scoped conflict register](readiness-audit.md#unresolved-gaps-and-contradictions), with affected records, consequences, owners and next actions. No additional global hold or silent source repair was introduced. The signature-anniversary conflict belongs to APP-2026-025's later letter; the current batch-1 report uses the explicit procedure rule and does not read that future letter.

## Local commit/capture and review gate

Meaningful local implementation commit `eff26c4e07fcf2b69a6acce0f82220cd4504fe3b` carries Entire checkpoint `01M5GT4Y6C225ZK9HT3RBE68F4` at `refs/entire/checkpoints/F4/01M5GT4Y6C225ZK9HT3RBE68F4`. The actual stored Git transcript payload was compared byte-for-byte with the CLI transcript export. It contains this session, the learner's actual groundwork acceptance and continuation, and the review implementation tool records. [Capture proof](reviews/capture-proof.json) records the exact ref/object, transcript hash and observed message timestamps. The raw transcript remains local under ignored .local/capture/.

Remote synchronization and facilitator access remain **pending**; no push or publication was authorized or attempted. This proof is preserved by a subsequent local documentation commit. Full implementation, final business verification, submission readiness, Classroom submission and grading are not claimed.

For learner inspection: compare VR-2000 and VR-2201 with the two source-table prohibitions; confirm VR-3002's conflicting dates are still visible and not selected; independently check RR-2500's 2026-05-05 anniversary and 50-day distance from export; confirm all six decisions say final_admission not-evaluated and no activation appears. Showing this report does not record its acceptance.

The next meaningful choice is whether to proceed with another independent bounded scope (proposed: request/response chronology from recorded attempts and correspondence, without issuing notices or deciding completeness) or prioritize resolving G1/G2 first. This is a sequencing choice, not an authorization to invent missing business facts. Put the learner's actual choice and reason early in their next turn; the assessment reads the first 600 characters.
