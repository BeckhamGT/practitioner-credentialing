# Source-linked MSP observation adapter

This is an engineering input format for a real human's factual review. It is
not an office-rule change, a source convention that declares CSVs equivalent to
forms/CVs, or permission to invent evidence. No such review is supplied for the
actual applicants. Newly obtained actual evidence remains a learner review point.

Use an additional authorized Markdown document in the batch's letters/ folder,
indexed by correspondence.csv and its immutable input manifest. Preserve the
underlying form/CV/source bytes; do not annotate or rewrite the original export.
The normalized review is a distinct record whose author is responsible for its
factual assertions. The roster pins the MSP identity; source/hash checks do not
cryptographically authenticate that author.

The record needs Date, Application, Revision, Review schema and Recorded by
metadata, followed by exactly one JSON block. Example **SYNTHETIC ONLY**:

````markdown
# SYNTHETIC factual review

**Date:** 2026-02-08
**Application:** SYNTH-WORKFLOW
**Revision:** 1
**Review schema:** credentialing-observations/1
**Recorded by:** Ms. Renata Kowalczyk, CPMSM

```json
{
  "evidence": [
    {"path": "letters/SYNTH-intake-evidence.md", "sha256": "<actual hash of that retained synthetic document>"}
  ],
  "facts": {
    "application_signature": true,
    "cv_current": true,
    "cv_reconciled": true,
    "all_credentials_declared": true,
    "accreditation_by_entry": {"SYNTH-E0": true, "SYNTH-E1": true}
  }
}
```
````

The placeholder above is not a runnable source claim. The demonstration contains
real calculated hashes of its explicitly invented documents. Actual reviews must
cite actual authorized documents available in the same retained dated source
view. References to unknown/future/wrong-application documents fail validation.

Allowed factual keys:

| Key | Meaning |
|---|---|
| application_signature | Applicant signature and written date inspected on this exact revision |
| cv_current | Actual CV inspected: most recent professional history at intake; no numerical age threshold |
| cv_reconciled | Actual CV/application/completed-verification comparison completed for this revision |
| all_credentials_declared | Completeness-list declaration/attestation check against available sources |
| accreditation_by_entry | Explicit accreditation observation keyed to an entry, independently of its completed training/degree verification |
| secondary_route_by_entry | MSP's recorded determination that the documented ATT impossibility route applies to this entry; the source/affiliation/reason are still checked |
| resolved_source_concerns | Map original concerned document hash to a distinct correcting document hash; both must be cited and dated in order. Retains the concern and its correcting/review provenance |

The first four require booleans; entry facts require entry→boolean maps. Concern
resolutions require original→correction hash maps. A later partial note adds only
its named facts, keeping other facts and each entry's provenance. A conflicting
change must name the prior observation's document hash in `Supersedes review`;
otherwise the adapter refuses silent selection. Originals remain in state.

Human review must cite the appropriate applicant/source correction; an MSP
assertion does not move the burden of resolving an applicant discrepancy from
the applicant. The software checks the linked bytes and dates, while the reviewer
and independent inspection establish the content's truth. This protocol never
allows a grant, explanation adequacy, disqualification or discontinuation key.
Those require the actual reserved decider's record and authority checks.

No CLI switch supplies signature/CV passes. Synthetic and actual application
inputs cannot share a workflow. Neither the sample nor a passing test is an
actual applicant observation. A free-form future document that cannot be parsed
still needs its genuine source preserved and an attributable normalization;
it is never guessed into a positive result.
