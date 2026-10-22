# Rules register — complete workflow capability

This register covers the current `process` command, its helpers and writer.
Historical review outputs remain unchanged. A rule is different from evidence
that an individual case meets it. No case-specific answers are in the runtime.

## Pinned source registry

| Key | Source / version | Authority and origin |
|---|---|---|
| A | [Assignment](https://docs.google.com/document/d/1HhmU8Jay09XHDci38hl9ZOX_dMryaSv4aFLCPu1Nk-E/edit), Your task, Submission states, Deliverables, cross-file rules, Interview, Submit | Published requirements; no rubric weights |
| P | [Office procedure](../references/record-review/procedure.txt), LARK-MSO-2026.1, effective 2026-01-01 | Adopted IHS manual quotations with section numbers, alongside explicitly local rules; the office's procedure governs |
| ATT | [Accepted-source table](../references/record-review/accepted-sources.txt), LARK-ATT-2026.1, effective 2026-01-01 | Office closed source classes and impossibility routes |
| AUTH | [Roster](../references/record-review/authority.txt), LARK-AUTH-2026.1 | Office bodies, named people, terms, designation and continuing MSP |
| APP / REF / PRIV | [Application](../references/element-sources/APP.txt), [reference form](../references/element-sources/REF.txt), [privilege criteria](../references/element-sources/PRIV.txt), LARK-APP/REF/PRIV-2026.1 | Office forms/map; PRIV effective 2026-01-01; APP/REF have no separately stated effective date |
| E | [Export guide](../references/export-guide.txt), office note 2026-03-16 | Export meaning, closed batches, joins, blanks and address-check limitation |
| I | [Authentic final interview](../interviews/project-e-practitioner-credentialing-20261022-0427.md), Oct 21 18:05–18:06 and 23:50–23:54, Oct 22 00:21–00:27 | Original human turns; clocks/partial replies, attempts, signature method, qualitative CV meaning and unverified source-location claims |
| S | [Required schema](../snapshot.schema.json), credentialing-snapshot/1 | Original bytes unchanged; owns status/element meanings and required types |

`references/element-rules.json` pins the earlier continuation/record-review
contracts and all extracted texts. Its SHA-256 remains
`f4d0418c024166945826c2eb9f586f787350ab7efec3faa8fd0c7fc524613eb1`.
These are engineering transcriptions of office rules, not new office policy.
Hashes establish retained bytes, not native-provider revision authentication.

## Applied rule coverage

| Rule and exact source | Implementation / interpretation | Limit or human owner |
|---|---|---|
| Nine-condition completeness; no verification requests without signed release (P §1, APP §§A–J; manual §5 adopted, local nine conditions) | `workflow.intake`; evaluates each condition separately; unknown is not a pass or applicant failure. Request permission requires complete intake and release | Actual G1/G2 are unrepresented; typed MSP observations may establish them from cited sources, not a CLI bypass |
| Current CV means most recent professional history at intake (I lines 688/710); compare CV/application/completed verifications (P §2, adopted manual §6.2) | `human_review.observations`, separate file-level reconciliation result | No age threshold, no declared-history.csv equivalence; no invented comparison |
| Missing item written request +30 calendar days, inclusive; partial replies/revisions do not reset (P §1, manual §5 and local clock; I lines 624/634/644) | `workflow.intake` reads actual notices, retains original deadline and item receipts; no deadline from G1/G2 alone | No new notice or correspondence is sent by software |
| Unexplained ≥30-day gap returns file incomplete (P §§1/3 Check 2, adopted manual §6.4) | Computed element return requirement; actual returned status requires actual recorded return correspondence | A proposed action is not a performed return |
| Compare both values; applicant written amendment resolves; one disputed entry does not stop others (P §2, manual §6.4 and local entry scope) | `entry_checks` preserves reply/declaration/change fields; a matching amended date may use its original reply. Organization/role/contact/supervisor changes require a corresponding current verification | CV comparison is separate; no silent source-date adoption |
| First receipt anchors five-year experience floor; deeper verification for conflicts (P §3 Check 2, manual §6.4 and local anchor) | Current work/affiliation entries overlapping floor, plus identified earlier discrepancies, are checked | Current clinical competence remains with clinical leadership |
| Primary-source prohibition on applicant-carried evidence, closed accepted classes (P §3, manual §§1/6.1; ATT) | `source_class`, `entry_checks`, certification source checks; original rejected replies retained | Unknown source/route authority is unknown, not a proven refusal; explicit applicant-carried/unlisted types fail the source check |
| Affiliation-retained CVO names itself and the affiliation; secondary only when impossible, not nonresponsive (ATT) | Explicit CVO retaining/acting-for assertions; linked roster-validated MSP route observation plus most-recent affiliation and reason for secondary route | Mere offered secondary evidence is not proof MSP accepted it. APP-021 remains source-admission review |
| Permanent attempts; three 21 days apart; peer day 64 escalation (P §3, manual §§6.2/15; P Check 4/REF; I line 654) | `request_history`, owned next-attempt/overdue tasks; all attempts retained after reply | G7 does not authorize a fourth-reminder policy; tasks are not sent messages |
| WA four-field join; no match means no WA credential, not NPI; lookup exception (E joins/columns; P §3 Check 1) | `wa_observation`, source date filtering and exact board join; inclusive recorded expiry; no CE due-date use | Joined record is an observation, not identity authentication beyond supplied export |
| Active/current/full unrestricted WA bylaw; every other held licence verified including inactive (P Check 1, adopted manual §6.4 with local practice-state restriction) | Status/date/action and actual board reply considered together; restriction goes to CD. Other-state “None reported” is explicit no action; blank remains unknown | No restriction conclusion from actiontaken alone; expired/inactive other-state licences are still verified |
| Licensure finding persists after CD disposition ends wait (P Check 1/§8 local) | Original restriction source stays finding; source-recorded CD disposition clears its hold only | Disqualification is CD/MEC/GB judgment |
| All declared intervals inclusive; school completion +1; blank end = export; overlap covers; recompute ≥30 and ≥180 gaps (P Check 2; E blanks) | `gap_intervals`, `gap_explanations`; actual arithmetic independently checked with daily sets | Declared history is not silently replaced by source dates or missing CV contents |
| Explanation covers entire named period; presence marks explained; long gaps require recorded CD disposition (P Check 2 local) | Exact interval containment; CD actor/term and identified gap checked | Adequacy is never computed. G5 preserves the identified disposition while flagging its uncorroborated cited date |
| Degree and all post-graduate training verified, education does not confer licence (P Check 3, manual §6.4; ATT) | Per-entry source, date, credential/role and revision changes | Qualifying degree/accreditation for privilege support remains a distinct check |
| Two same-discipline, nonrelative, direct-work peers; recency at signature; currency second anniversary inclusive (P Check 4, manual §6.4; REF) | Distinct latest replies, returned box/prose, dates and signature; existing referee names carry through revisions because E restates only four other declaration tables | Unfamiliar/contradictory prose remains review; G3 boundary claim retained, actual May 18 stale result agrees under either wording |
| Extra unanswered peer request does not hold met element; close at presentation as no longer needed (P Check 4 local) | Separate count and permanent request history; closure requires established presentation/admission, not a readiness guess | Never counts an unanswered request; terminal closure has its own reason |
| All active/inactive certificates verified; board eligible exception; published map and training minima (P Check 5, manual §6.4/§9; PRIV rules 1–6) | Board/source/window/status, explicit candidate-good-standing note and future end; exact board/specialty; all/any training rows, calendar durations and degree/training accreditation | Actual accreditation lacks separate evidence; final support may remain unknown. No invented alias, threshold or accreditation pass |
| Unsupported subset versus no support, no automatic discontinuation (P Check 5; PRIV rules 2/3/5/6) | Names independently unsupported groups; eligibility question routed to CD; later supported request withdraws question; explicit inactive/forbidden eligibility and CARD clauses applied | G6 one-component “neither” tension remains scoped; current-experience column never automated |
| Yes or contradicted No is high risk; applicant confirmation and CD disposition (P §4/APP §I, manual §7; P §6) | Retains original disclosure, actual board contradiction, written confirmation and human disposition; queues CD/MEC/GB evidence | No third federal body; no automatic disqualification or recommendation |
| Complete/reconciled file, six nothing-owed results, no discrepancy, usable replies, named revision (P §8, manual §§8/12 with office rules) | Three-valued dependencies: any proven necessary failure makes readiness false; otherwise an unknown stays unknown. Last needed reply date excludes extra unnecessary peer returns | A missing proof is not by itself a proven historical failure. Historical readiness stays after refusal or terminal event |
| Reply on/after first receipt and strictly before decision; same-day lookup exception (P §8 local) | `visible` and `date_window`; each new decision uses its own batch/date view | Later batches never repair earlier results; prior evaluations remain immutable |
| Ordered authority, role/term, applicant/revision, prior packet, reason; second same-body GB names earlier admitted record (P §9/AUTH, adopted authority principle plus local protocol) | `conditional.decision`, full workflow independent condition observations and ordered result; original IDs/outcomes retained | Unknown prerequisite remains unevaluated, not refused. Plain approval/positive recommendation need no reason |
| Actual withdrawal or CD discontinuation ends file, never appointed (P §§6/11) | Applicant association, CD identity/term and actual directive; operational requests close but evidence/history stays | Wrong-recipient metadata stays visible; no automatic discontinuation from unsupported privileges |
| Admitted current-revision GB approval only, exact granted codes, effective date/decision date, one-year-minus-day cycle (P §10/Check 1, manual §§5/12/15) | `activation`; supports observed semicolon/comma grant delimiters; admission separate from activation | Undefined leap-cycle convention stays unresolved; no requested-but-ungranted group activated |
| Named approval conditions and licence expiry tracked; satisfaction names condition; overdue goes to CD; no activation hold (P §10/Check 1 local) | `recorded_conditions`, `conditions`, current/retained condition events; licence obligation due expiry itself; actual renewal joins its named credential | Unknown condition details block their schema projection, not unrelated work or otherwise established activation; no deadline invented |
| Five re-entry triggers, preserve prior source/revision/refusal/readiness/appointment/condition history (P §11, adopted manual §15 and local scope) | Workflow reports and immutable predecessor chain; entry changes affect own entry; export-clock monitoring continues | No later evidence silently rewrites an earlier decision evaluation |
| Schema and six cross-file invariants; unchanged rerun, new IDs/retained bytes/downstream regeneration (A Deliverables; S) | `processor`, `snapshots`, `writer`; current case fragments validated against original application definition; whole snapshot only for complete representable caseload/chain | Actual required snapshot paths stay absent; synthetic nested paths are explicitly fixtures |

## Engineering mechanisms and boundaries

`WorkflowStore` persists immutable content-hashed workflow reports with exact
predecessors, a writer lock and atomic HEAD. It is separate from the original
evidence store. Changed retained outputs require a separately identified
reconstruction; missing/corrupt predecessors never trigger a fresh start.
Snapshot writer transactions preserve planned/prior bytes and block verification
until rollback/retry. Workflow processing may succeed while schema generation
fails; that workflow result is not advertised as an assessed snapshot.

The typed MSP observation adapter requires a dated application/revision, roster
identity, existing source paths/hashes and permitted factual keys. It cannot grant
privileges or make a reserved clinical judgment. A conflicting correction must
name the prior review hash. No such record is invented for supplied applicants.
Hash/roster checks do not authenticate a signature; authorized input provenance
and independent human inspection remain material.

Formatting normalization only removes the observed Degree/Employment labels or
reorders the observed Residency label. It creates no medical credential alias.
Source documents are data, never tool instructions. Synthetic datasets have only
SYNTH-prefixed application IDs; mixed actual/synthetic application inputs are
rejected. The demo sources and assumptions are conspicuously labeled.

G1/G2 and G3–G8 remain in [the audit](../docs/readiness-audit.md). No facilitator
contact or inventory retry is required for current software work. Human judgments,
new source conventions and publication/submission remain with their actual owners.
