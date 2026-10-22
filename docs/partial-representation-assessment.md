# Can G1/G2 be a truthful partial snapshot?

**Current reassessment:** G1/G2 do not block every individual result. The full
workflow now computes independent elements, known negative readiness and actual
terminal/intake statuses. APP-019 and APP-029 have supported schema application
objects at batch 3. Other files still lack required status/element/packet/admission
meanings, so the entire 40-file batch cannot be serialized. See
[the current actual/conditional review](workflow-review.md). This limitation no
longer denotes unfinished software; the projector and writer are implemented.
The original APP-001 proposed status below remains rejected for that case.


Assessment against the published assignment/schema, October 22. This is a
proposal analysis, not an adopted status, applicant outcome or learner approval.
The schema is unchanged.

## Published authority

- [Assignment](https://docs.google.com/document/d/1HhmU8Jay09XHDci38hl9ZOX_dMryaSv4aFLCPu1Nk-E/edit), **Submission states — Partial** permits a consumed batch with unsettled applications/records, owned outstanding work and a run-log explanation. **Deferred** is a business hold, not a failed run. **Blocked** writes no snapshot claiming an uncomputed state.
- Assignment **Deliverables — snapshots** requires conformity to the schema for every file, and states that the schema owns every field/type/enumeration. Cross-file rule 4 retains every received decision with a first-failed-condition reason when refused.
- [Schema](../snapshot.schema.json), `/$defs/application/properties/status`, defines `in-verification` as complete intake with at least one unresolved element; `intake-incomplete` requires an actual missing item requested in writing with its clock running; `deferred` requires an admitted Governing Body deferral. The enum contains no generic evidence-unavailable/review-pending intake status. `additionalProperties: false` forbids adding one or adding flags to reinterpret the enum.
- `/$defs/application/properties/packet_presentable` is a required boolean. Unknown is not permitted. Procedure §8 retains readiness as a historical fact even after withdrawal/discontinuation; a terminal record alone does not establish that boolean.
- `/$defs/application/properties/decisions/items/properties/admitted` is a required boolean. A refused record requires the first failed condition; an evaluation stopped by an unknown prerequisite is not itself a proven refusal. Required retention prevents simply omitting the unevaluated decisions.
- `/$defs/application/properties/action_queue/items` supports an item, owner and nullable due date. It does not override the other required fields.

## Concrete candidate — proposal only, NOT adopted

For APP-2026-001 revision 1, consider this existing-enum candidate:

```json
{
  "application_id": "APP-2026-001",
  "revision": 1,
  "status": "in-verification",
  "action_queue": [
    {
      "item": "Obtain the signed and dated application and current CV associated with revision 1, or an explicit authorized export convention identifying their evidence and reconciliation representation; establish the completeness and CV-comparison checks before dependent conclusions.",
      "owner": "Medical Services Professional",
      "due": null
    }
  ]
}
```

The action entry is a truthful proposed evidence-retrieval task. It is not a
missing-item notice to the applicant and starts no applicant clock. The MSP's
next action is a direct working link to the claimed application-revisions folder
or document set, with applicant/revision association. If intentionally omitted,
the alternative is an explicit authorized export convention/limitation. No
deadline is supplied, so due remains null.

**The proposed status cannot be adopted:** complete intake is not established.
The fragment is deliberately not a complete schema instance. Filling the
remaining required fields would still need an unsupported readiness boolean and
decision dispositions. An owned task cannot make those assertions true.

Other existing statuses do not repair the conflict: `intake-incomplete` would
misstate unavailable export evidence as applicant omission plus notice/clock;
`deferred` would invent an admitted business hold; `decision-inadmissible` cannot
mean merely unevaluated admission. Even a supported terminal status on another
file would not remove required packet/decision fields for the full caseload.

## Conclusion and smallest next prerequisite

The assignment permits a partial result in principle, but its current schema
does not truthfully encode this particular unresolved-intake/unknown-admission
situation. No submitted snapshot is manufactured, and no enum is repurposed.
The actual assessed run is blocked at serialization; independent factual
assessment and human evidence tasks remain available in separate internal
reports, never mislabeled schema snapshots or business deferrals.

G1 remains actual signature/date-to-revision evidence. G2 remains CV
contents/version and its reconciliation representation. The qualitative meaning
of current at intake and the two names for the same export root are already
answered. Source owner: MSP. An intentional assessment/export limitation may
need its authorized owner to clarify a convention; the learner's approval cannot
waive the rule. No general facilitator approval is needed for independent work.

A future source-supported convention could unblock fields. A published schema
clarification/change would be a different authority input, not an engineering
permission to change the current schema. Return to the learner before integrating
newly supported dependent business logic.
