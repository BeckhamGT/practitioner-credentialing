# Verification — element and writer milestone

This is a bounded local milestone, not full implementation or submission
readiness. [Current review](../docs/element-review-milestone.md) contains actual
results, precise source comparisons, proposed status treatment and remaining
implementation versus external gaps. [Current reports](assessments/current.json)
select immutable hash-named assessment occurrences. The first set is retained;
a later metadata clarification removes an obsolete not-evaluated label for
reason observations without changing any supplied source or case outcome.

| Actual check | Observed evidence and limit |
|---|---|
| Three chronological element assessments | 40 files each, four declared gaps ≥30 days and one ≥180; decision refusal/blocked counts 0/6, 2/33, 2/54. No completeness/readiness/positive admission inferred |
| Independent original-source arithmetic | `tools/independent_element_checks.py`: daily sets versus interval union, all 120 application/batch gap and WA joins match; [evidence](assessments/independent-verification.json). Not CV reconciliation |
| Actual correspondence/dispositions | [Selected original records](assessments/source-comparisons.json); full bodies are retained in the reports. G5 remains and new G8 scopes APP-018 wording to that record |
| All supported decision conditions | Body, registry role/term, recorded revision, reason and literal prior-ID observations shown. Blank Supersedes is observed, but its admission consequence remains conditional on earlier admission |
| Actual assessed-run attempt | Three `run` commands retain independent reports, exit 3 `snapshot_unrepresentable`, and produce no actual snapshots; [exact log](assessments/execution-log.json) |
| Rerun and batch isolation | Reports reproduce byte-for-byte with later HEAD present; pinned state chain only; original store/source evidence unchanged |
| Synthetic writer lifecycle | [Proof](synthetic/writer-demo/proof.json): three schema-valid fixture occurrences, exact predecessor chain, unchanged rerun, preserved superseded bytes, full downstream regeneration, injected failure, blocked current verification, journal rollback and retry. No supplied applicant result |
| Regression | [114 tests](assessments/test-summary.json), [raw output](assessments/tests.txt), including Unicode report preservation, unknown inputs, illegal status/activation and protected refusal history. Tests alone do not establish requirement coverage |

A real development defect was found during the first actual `run`: stdout escaped
Unicode while report persistence did not, so the preservation guard returned
`changed_report`. The parsed objects were equal (1,391,306 versus 1,389,453
bytes). A Unicode source fixture reproduced the failure; persistence now matches
stdout exactly, and the guard still refuses genuinely different bytes. The
original report is preserved. Separate actual-source inspection found semicolons
in multi-grant decision records; synthetic activation parsing now handles that
separator and tests exact grant codes. Neither change admits a real decision.

The writer API is implemented; a complete business-state projector is not. Final
per-element states, reuse/reconciliation, actual queue/terminal effects and
packet/admission/activation integration remain implementation work. G1/G2 remain
external evidence blockers for dependent facts. [Partial representation analysis](../docs/partial-representation-assessment.md)
explains why an owned task cannot repair the mandatory status/boolean conflict.
The schema is unchanged; no unsupported status, deferral or snapshot is created.

Skill validation/security scan and genuine commit-linked capture are recorded
for this candidate below after inspection. Remote syncing, access, publication,
learner acceptance, Classroom submission and grading remain pending.

## Current genuine capture

Meaningful implementation commit `012f589738abaa5803a3f10901011691369137da`
carries genuine Entire checkpoint `01M5H4CZAGHEBN7X1QX6W1H993` at
`refs/entire/checkpoints/93/01M5H4CZAGHEBN7X1QX6W1H993`.
The Git-stored full payload equals the CLI export byte-for-byte: 10,380,272 bytes,
SHA-256 `7b7f25e4c47900f5655952ea0d54f95929070a942e871d0b99ce5750e1227a85`.
It contains this learner request and subsequent actual implementation/test,
independent-check and writer operations. [Capture proof](assessments/capture-proof.json)
records commit association, ref/object and actual message/tool record matches.
It is written after the implementation commit; it is not a reconstructed session.
Synthetic demo occurrences are locally sealed by that implementation commit.
Remote checkpoint synchronization, facilitator access, publication and submission
remain pending. No push was attempted.

## Current Skill inspection

Metadata validation passed. The pinned local-only scanner exited 0 and reported
one MEDIUM `DATA_EXFIL_NETWORK_REQUESTS` at elements.py:368 and one INFO
`MANIFEST_MISSING_LICENSE` at SKILL.md. The medium is an inspected false positive:
`requests` is a local dictionary from `indexed`, and `.get` reads privilege rows;
no HTTP client is imported. The INFO is accepted for the local candidate without
inventing license terms. [Raw report](assessments/skill-scan.md) and [bundle hashes/dispositions](assessments/skill-validation.json)
are retained. Manual code/instruction/output inspection supplements the scan;
the scanner's SAFE label is not a safety certification. Raw scanner output keeps
its extra final blank line and runtime telemetry warning unchanged.

## Prior milestone account (historical)

The following describes the earlier confirmed-rule milestone and its 93-test
state. Its original evidence files remain unchanged. Where it says an element
check or writer is unfinished, the current scope above supersedes that account;
full business integration remains unfinished.


This is a bounded implementation and source verification milestone, **not full
implementation or submission readiness**. No assessed snapshots exist. The
authentic final interview, original schema, source archive, prior reports and
accepted evidence-store HEAD remain unchanged.

## Actual evidence evaluations

| Export | Clock | Applications / revisions | Attempts | Decisions | Report |
|---|---|---|---|---|---|
| 1 | 2026-03-16 | 40 / 41 | 236 | 6 | [Batch 1](evidence/batch-01-timeline-43ea990d33a5.json) |
| 2 | 2026-04-20 | 40 / 45 | 245 | 35 | [Batch 2](evidence/batch-02-timeline-4c0b738ad865.json) |
| 3 | 2026-05-18 | 40 / 46 | 250 | 56 | [Batch 3](evidence/batch-03-timeline-2339f13a56fa.json) |

These are chronological evidence-review outputs, not the three assignment batch
snapshots. Batch 3 resumes batch 2's exact state hash in a separate evaluation
store. The accepted original store is unchanged. Re-running all three pinned
reviews with the batch-3 HEAD present reproduces the exact report bytes.

## Source comparisons and independent calculations

Checks were recomputed with standard-library CSV, datetime, regex, JSON and
hashlib, outside implementation functions. [Independent evidence](evidence/independent-verification.json)
records observed state/report hashes, counts, source comparisons, preservation
and recovery. The generic rerunnable checker is `tools/independent_checks.py`.

- APP-2026-014 / REF-1401: actual attempts on **2026-02-09, 2026-03-02,
  2026-03-23** in verification-attempts.csv yield **21 and 21 calendar days**.
  First request plus 64 days is **2026-04-14**. All three attempts remain after
  the reply. An observed returned row is not treated as a qualifying reference.
- MEC-2026-036, batch 2 decisions/2026-04-14_MEC-2026-036.md: actual body MEC,
  outcome approved. AUTH and P §9 forbid this body approving. The first failed
  condition is body-authority; original outcome/wording remains intact. The
  refusal persists in batch 3; its MSP review task has no invented deadline.
- GBD-2026-034, batch 2 decision for APP-2026-036: record names revision 1 on
  2026-04-14, while applications.csv has revision 2 already received. After the
  authority prefix passes, applicant/revision is the first independently failed
  condition. This does not establish packet readiness for either revision.
- The remaining **54 of 56** received decisions have no positive admission or
  activation computed. Their prior presentable packet is unproved. In particular,
  the later duplicate-looking GB record is not refused at a later condition while
  earlier packet/admission dependencies remain unknown.
- APP-2026-025's two batch-1 revisions remain distinct. Later revision comparisons
  preserve APP-2026-030's changed history date and added entry, APP-2026-036's
  changed entry fields, and APP-2026-027's changed privilege group. No comparison
  chooses a disputed value, certifies CV agreement or declares evidence reusable.

Reproduce independent counts/arithmetic:

```sh
.venv/bin/python tools/independent_checks.py --inputs .local/inputs --reports deliverables/evidence --application APP-2026-014 --subject REF-1401
```

## Conditional results — synthetic only

[Conditional outputs](synthetic/conditional-results.json) contain invented
SYNTH-ONLY inputs with explicit completeness, CV, reconciliation and disposition
assumptions. They are separate from the supplied-applicant reports.

- Unknown completeness or CV reconciliation yields no presentability boolean.
- An explicitly disposed finding remains `finding` while the synthetic packet
  can be presentable; an unresolved hold prevents it.
- Ordered admission, prior-packet timing, reason exceptions and GB supersession
  are tested. Unknown prior admission cannot be assumed away.
- The synthetic approval grants only PRIV-FM from 2026-04-01 through 2027-03-31;
  the March 16 evaluation is inactive, the April 1 evaluation active. Conditions
  remain separately monitored. A record naming a different condition does not
  satisfy the synthetic condition.
- An extra unanswered request never counts as a reference, does not hold an
  explicitly met element, and closes at presentation as no longer needed.

These kernels do not implement complete intake, clinical judgment or source
acquisition, and they are not wired to a supplied-case processing command.

## Tests, failures and recovery

**93 tests pass**: the previous 55 plus 38 continuation, conditional, schema and input-preparation tests.
They cover contact-only changes, retained attempts/refusals, blank dates,
backdated later-batch isolation, explicit unknowns, persistent findings, ordered
admission, exact grants, reason/supersession rules, named condition evidence,
original-schema validation and predecessor/retained-decision integrity.

The first new test run found three correspondence-join errors. Diagnosis showed
the shared index uses tuple keys even for one column; the new code used scalar
keys. The two affected lookups were corrected, then the full suite passed.
A later preparation test initially used macOS’s /var alias, which the explicit symlink guard rejected. The test fixture now uses its resolved /private/var path; no production guard was weakened. These development failures are distinct from the deliberate recovery probe.

An isolated probe staged batches 1/2, deliberately supplied batch 1 as batch 3's
predecessor, and observed exit 2 `predecessor_mismatch`. The prior HEAD remained
byte-identical. Resuming with batch 2's exact predecessor recovered the expected
batch-3 state; unchanged rerun returned unchanged. This is a labeled intentional
test, not a fabricated production incident. Source/accepted stores were untouched.

A clean handoff replay through the documented input preparer and CLI stages reproduced all three exact state hashes; see [handoff evidence](evidence/handoff-check.json). The preparer reads the combined archive outside runtime and materializes only the reviewed manifest’s batch. It preserves differing existing files.

The generic `run` command still exits 3 with G1/G2 and writes no assessed snapshot.
Schema validation and passing tests alone cannot supply missing business facts.

## Remaining evidence and implementation

The smallest source prerequisite remains a **direct working application-revisions
folder/document-set link**, with applicant/revision association, completed signed
forms and CVs. If intentionally omitted, obtain an explicit authorized export
representation/limitation instead. The root directory alias and qualitative CV
definition are already answered. No repeated unchanged folder search is needed.

Full per-element calculations, evidence reuse/reconciliation, the complete
business queue, dependent admission/activation integration, terminal paths and
the assessed writer/sealed-snapshot supersession still need implementation and
actual lifecycle verification. Independent portions remain authorized now;
integration of newly supported G1/G2-dependent logic returns to the learner first.
G3–G7 remain scoped; see the audit. Publication/access, remote capture syncing,
final learner acceptance and Classroom submission are separately pending.

## Learner inspection

1. Compare REF-1401's three original attempt dates with the report; check 21/21
   yourself and confirm the earlier attempts remain after the reply.
2. Inspect the two original refused decisions and their exact recorded revisions,
   outcomes and sources. Confirm the other 54 are not represented as admitted.
3. Compare one revision's changed contact/date fields and check that old values
   and source hashes remain available.
4. Inspect the synthetic output's assumptions before its positive results; none
   should appear as a fact about a supplied applicant.

This report is shown for review. It does not record learner inspection or
acceptance. Put any actual choice and reason early in the next turn, because
the assignment reads its first 600 characters.

## Skill validation and manual inspection

Skill metadata validation passed with the existing scanner Python environment. The default interpreter lacked YAML; no dependencies were installed. The pinned local-only Cisco 2.0.13 scan exited 0 with zero high/medium/low findings and one INFO finding, MANIFEST_MISSING_LICENSE at SKILL.md. This is accepted for the current local candidate; no license terms are invented. [Raw scan](evidence/skill-scan.md) and [scanned bundle hashes/disposition](evidence/skill-validation.json) are preserved. Manual inspection covered instructions, runtime, preparer, checker, hidden-file scope and local destinations. The Skill is not certified safe by this scan, and full-repository historical evidence/dependency trees were not scanned as operative code.

## Local commit and genuine capture

Meaningful implementation commit `486d0eb6f580081ee3cbf812e4c11872034ee9a5` carries checkpoint `01M5H0MYEEFCSDDP9TKX6E3GP4` at `refs/entire/checkpoints/P4/01M5H0MYEEFCSDDP9TKX6E3GP4`. The actual Git-stored full transcript equals the CLI export byte-for-byte and contains the learner’s real authorization/continuation plus implementation, synthetic tests and independent-check operations. [Capture proof](evidence/capture-proof.json) records object, hash and observed timestamps. This proof is recorded afterward in a documentation commit; it does not claim to predate the implementation commit. Remote synchronization and facilitator access remain pending. No push or submission occurred.

Whitespace note: the raw scanner report retains the scanner’s extra final blank line byte-for-byte; git diff --check reports that artifact’s blank-at-EOF warning. Code/documentation checks excluding that raw evidence file pass. The scan output was not silently normalized.
