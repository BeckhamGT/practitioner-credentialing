# Rules register — current implementation scope

This register distinguishes executable checks from conditional test kernels and
remaining work. It is not a declaration that every application is complete. No
case-specific answers are encoded in the runtime. Case examples belong in the
verification evidence, not rule configuration.

## Sources and versions

| Key | Source and locator | Version / origin |
|---|---|---|
| A | [Assignment](https://docs.google.com/document/d/1HhmU8Jay09XHDci38hl9ZOX_dMryaSv4aFLCPu1Nk-E/edit), Your task, Deliverables, cross-file rules, Interview, Submit | Published assignment; no rubric weights published |
| P | [Office procedure](https://docs.google.com/document/d/1v442U759TGLwnElS24xF1MmvovZjBSHy4KKe2Nl-GDk/edit) | LARK-MSO-2026.1, effective 2026-01-01; distinguishes quoted manual rules from local Larkhollow rules |
| ATT | [Accepted-source table](https://docs.google.com/document/d/1ze0RTP4H8J68FSqbFmkG7Qd_5cZiB6Lh2BfyU6v2Sj8/edit) | LARK-ATT-2026.1, effective 2026-01-01; office closed lists |
| AUTH | [Authority roster](https://docs.google.com/document/d/1Dvc3eJei4K7RyE8HZtZkMtRQNqE6VPQU8gUXVbps2xQ/edit) | LARK-AUTH-2026.1; office roles, terms and 2026-01-05 designation |
| E | [Export guide](https://docs.google.com/document/d/1UtQMnsCW78nPClsgEJV1DgBKlaiIkzNS-fT93-kTLgA/edit), The files, Dates/blanks, The three joins, What I do not export | Office note 2026-03-16 |
| I | [Original final interview](../interviews/project-e-practitioner-credentialing-20261022-0427.md) | Participant-visible turns; timestamps/lines below; original bytes unchanged |
| APP / REF / PRIV | [Application](../references/element-sources/APP.txt), [reference form](../references/element-sources/REF.txt), [privilege criteria](../references/element-sources/PRIV.txt) | LARK-APP/REF/PRIV-2026.1; PRIV effective 2026-01-01. APP/REF effective dates not separately stated; no date inferred |
| S | [Published schema](../snapshot.schema.json) | credentialing-snapshot/1, Draft 2020-12; byte-unchanged |

The executable source/hash pins are [record-review/rules.json](../references/record-review/rules.json)
[continuation.json](../references/continuation.json) and [element-rules.json](../references/element-rules.json). These are engineering
transcriptions of confirmed rules, not newly authored office policy. Hashes cover
retained extracted text, not authenticated native-provider revisions.

## Applied to supplied evidence now

| Rule | Exact source / adopted versus local | Implementation and limit |
|---|---|---|
| Export date is clock; UTF-8, inclusive dates and explicitly meaningful blanks | E The export date is the clock; Dates, blanks and columns — office convention | `validation.py`, `review.py`, `timeline.py`; empty evidence stays unknown; no host date in business arithmetic |
| Exact thirteen record files, one README, actual indexed documents | E The files; A actual supporting evidence — office/export contract | `validation.py`; structural integrity only, including valid header-only files |
| Source hashes, allowlist, immutable state objects, explicit predecessor, atomic HEAD | A sequential continuation; engineering integrity choices | `storage.py`; these are internal evidence objects, not schema snapshots; no orphan-state promotion |
| Applicant-carried evidence is unacceptable regardless of letterhead | P §3, manual §6.1 — adopted rule | `review.source_class`; retain original reply, classify route; not a final credential conclusion |
| Closed accepted sources and matching declared subject | P §3 office closed-list rule; ATT per-element table — local criteria within adopted primary-source framework | `review.py`; source-class classification only. Secondary-source impossibility route is not automatically inferred from silence |
| Verification on/after first receipt and before decision; board lookup exception | P §8 — office arithmetic consistent with the manual's removal of the old fixed limit | `review.date_window` tests strict decision boundary; actual reports check export-date window only, not final packet usability |
| Referee same discipline, nonrelative box, direct-work dates; two-year signature anniversary | P §3 Check 4: manual §6.4 element 11; office measurement/currency rules | `review.peer_checks`; individual returned fields only; `elements` also checks explicit direct-work prose conservatively; final qualification/counts remain unevaluated |
| Retain every attempt and original request/reply occurrence | P §3, manual §6.2 and office permanent-history rule — adopted plus local | `timeline.request_history`; a returned row is observed evidence, never automatic satisfaction or acceptable verification |
| Three peer requests 21 days apart; day 64 arithmetic | P §3 Check 4 — office schedule; I October 21 18:06 line 654 confirms at-least-three/21-day attempts | `timeline.py`; computes schedule only when recorded anchor is unambiguous; no notice sent or invented fourth-reminder policy |
| Restated revision-side facts; compare all entry fields | E The three joins; P §§2,11 — office convention | `timeline.revision_history`; retains additions/removals/changed values, including organization, role and contact fields. Does not claim CV reconciliation or unchanged evidence usable |
| Registry-validated body, outcome, signatory and role term | P §9 manual §§1,7,12 plus local roster protocol; AUTH — adopted authority principle, local identities/terms | `review.authority_checks`, `timeline.decision_history`; preserve asserted outcome and stop on proved early failures |
| Decision must name current applicant/revision | P §9 — office admission/re-entry rule | `timeline.py`; compare recorded revision available at decision date, excluding later-batch revisions. This can prove a negative mismatch; it cannot establish positive packet identity/admission |
| Received decisions and refusal reasons persist | A cross-file rule 4; P §§9,11 — assignment/local history rule | Timeline preserves original records in receipt order. Later reports retain earlier early refusals. Actual snapshots not yet produced |
| Human owner of rejected-record review is MSP | P §9 — local protocol | Timeline `review_tasks`; internal evidence-review tasks with no invented due date, not the final business queue |

## Conditional kernels — synthetic fixtures only

| Rule | Exact source / adopted versus local | Tested behavior and dependency |
|---|---|---|
| Presentability requires complete intake, reconciliation, usable evidence, six resolved elements and revision binding | P §§1,2,8 — office completeness/readiness criteria | `conditional.packet` requires explicit established facts. Unknown completeness/CV inputs yield no presentability boolean. It does not implement the nine-condition intake screen |
| A disposed licensure finding/partial certification finding may remain while presentable | P §8 explanation of resolved; §3 Check 1 — office interpretation | Finding enum retained; independently supplied nothing-owed facts control. No Clinical Director judgment is synthesized |
| Ordered admission; prior packet strictly before decision; reason exceptions | P §9 five conditions and later reason clarification — office protocol implementing adopted authority | `conditional.decision`; first failed or unknown check stops evaluation. Plain approval and positive recommendation need no reason |
| Second GB decision names prior admitted decision it supersedes; recommendations not duplicates | P §9 two-decisions clarification — local | Conditional tests cover exact prior ID, wrong/missing reference and unknown earlier admission. Actual duplicate admission is not inferred while the earlier packet/admission is unknown |
| Only admitted current-revision GB approval activates exact grants; effective date or decision date | P §10, manual §§5/15 plus local activation rule | `conditional.activation`; no positive supplied-case route. Unknown admission blocks; no requested-but-ungranted privilege is added |
| Initial cycle one year minus one day | P §3 Check 1 manual §12 and local cycle; §10 | Conditional date arithmetic. Leap-day cycle convention remains explicitly unsupported, not silently shifted |
| Named conditions have own due dates; only a naming record satisfies; unmet on due date routes to CD; conditions do not block activation | P §10 — office monitoring rule | `conditional.conditions`; explicit synthetic records only. Actual condition extraction/admission and licence-expiry monitoring are still pending |
| Extra unanswered reference stays visible after two qualify, closes at presentation as no longer needed, never counts as a reference | P §3 Check 4 — local clarification | `conditional.peer_extra_request`; two qualified/current references and presentation are explicit synthetic inputs. A returned extra reply still needs qualification |

## Schema and cross-file checks

`snapshots.verify_snapshot` applies S plus A cross-file rules: calendar-valid dates,
current snapshot in produced, existing produced/rules paths, exact predecessor
bytes, sequential batch clocks, distinct occurrence IDs, retained applications and
decision histories/refusal reasons, same-file admitted approval reference, and
activation range/clock consistency. These are read-only checks demonstrated on
synthetic snapshots. They do not establish source truth, body authority, exact
grants, condition satisfaction, queue ownership or consumed-file completeness.
The local writer now validates these checks before generation; synthetic proof covers unchanged reruns, byte-preserved archives, new IDs, downstream regeneration, interrupted-write rejection and journal rollback/retry. A Git commit seals generated working files. The complete actual business-state projector remains unfinished.

## Missing evidence, scoped conflicts and reserved judgments

G1: no actual signed/dated forms associated with revisions. G2: no CV contents/version
or explicit export mapping of CV reconciliation. I October 21 lines 688/710 clarifies
qualitative currency and comparison; October 22 lines 722/744/752/766/774 claims a
shared revisions location but supplies no available document set. No age threshold,
CSV substitution, applicant failure, notice or schema status is invented.

G3–G8 remain in the [scoped source register](../docs/readiness-audit.md#unresolved-gaps-and-contradictions).
They retain their exact records, consequences and owners; they are not global
stops. No source correction or unsupported privilege-support interpretation is adopted.

Five judgments remain reserved (A Your task; P §6): gap explanation adequacy —
Clinical Director; disqualifying findings — Clinical Director, MEC and GB;
eligibility discontinuation — Clinical Director; recommendation/privileges — MEC;
grant/modify/defer/deny — GB. Runtime reviews preserve evidence and authentic
decisions. No engineering choice or synthetic fixture supplies their judgment.

Remaining confirmed-rule implementation includes the full intake/reconciliation
screen, final licensure/expiry state, reconciled history and final support evaluation,
qualification of references including prose, evidence reuse, final packet/decision
state, terminal paths, activation/conditions and the business action queue. Some
independent portions can continue now; G1/G2 block only dependent conclusions.

## Additional applied independent checks

| Rule | Source / origin | Implementation and limit |
|---|---|---|
| Medical-school completion +1; all interval types inclusive; blank end runs to export; gaps ≥30, ≥180 routes to CD | P §3 Check 2; E dates — adopted manual history check with office thresholds/arithmetic | `elements.gap_intervals`, `gap_explanations`. Declared intervals only; exact full-period explanation coverage is observed; adequacy and G5/G8 remain with humans |
| Five-year experience floor anchored to first receipt, deeper for conflicts | P §3 Check 2; P §11 — office measurement of adopted verification rule | `entry_observations`: source reply context and every changed entry field retained; no automatic reuse after G2/revision changes |
| WA exact four-field join; no row means no WA credential; own lookup exempt from reply window; NPI/CE not licence | E joins/WA columns; P §3 Check 1 — office export convention and adopted manual licence verification | `wa_observation`; actiontaken prompts reading actual board reply, does not prove restricted/unrestricted. Status and inclusive expiry facts separately recorded |
| Verify every declared other-state licence, active/inactive | P §3 Check 1; ATT — adopted manual rule and office source list | `other_licence_observations`; number/jurisdiction observations preserved. Missing reply is not no licence |
| Current supporting certification AND verified minimum accredited training; published codes, CARD conjunction, limited board eligibility | PRIV table and application rules 1–8 — local eligibility criteria | `privilege_components` records exact board/specialty, current certificate observations and returned training/duration. No new aliases; undefined specialty/accreditation stay explicit. G6 one-component classification not settled; current experience/competence remain human |
| Current CV reflects most recent professional history at intake; compare actual CV/application/verifications | P §§1–2, I Oct 21 11:51/11:54 PM lines 688/710 — local clarification | Intake facts retain receipt/release fields, PPQ answers and yes-comments independently; signature, CV content/reconciliation unknown. No age threshold/CSV equivalence inferred |
| Reason required except plain approval/positive recommendation; same-body GB supersession names earlier admitted record | P §9 and AUTH — local admission protocol | `decision_conditions` inspects every independently supported field, retaining the ordered stopping point. Received prior record ≠ admitted prior record; no later refusal leapfrogs unknown packet prerequisites |
| Actual human records are data, actor/term must be checked | A Your task, P §6; AUTH — adopted authority with local roster | `elements.actual_documents_read` retains full bodies and checks CD identity/term prefix. Binding/effect and scoped provenance conflicts are not silently adopted |
| No schema enum or required boolean may mean an unsupported unknown | A submission states/Deliverables/cross-file rules, S status/packet/admitted definitions — published contract | `run` preserves independent facts then blocks serialization. Rejected proposal and exact conflict in docs/partial-representation-assessment.md; truthful evidence task owner MSP, due null, never an invented applicant notice |
| Exact listed grant codes; multi-code separators are lexical, not additional grants | Actual decision record format; P §10 — engineering parsing of supplied records | Conditional activation handles observed semicolons and commas, rejects unknown/duplicate codes, still synthetic only |

Training durations use calendar month boundaries (e.g. July 1–June 30 for 36
months). Undefined month-end/leap conventions remain unknown; CARD's separate
IM-residency minimum is not invented from a different row. Source text hashes
are checked; they do not authenticate provider revision history.

Writer output files and its run-log notes are distinct from internal transaction
journals/backups. Current chains are validated; unchanged archived snapshots keep
their original predecessor paths/bytes, resolved historically through the
path/hash archive index. This is an engineering integrity mechanism, not an
authorization to alter a human record or waive an office rule.
