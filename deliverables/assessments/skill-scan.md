2026-10-22 02:19:59.742 Python[44800:13261224] 2026-10-22 02:19:59.742258 [W:onnxruntime:Default, telemetry_1ds.cc:600 operator()] Failed to persist telemetry device ID; using an in-memory identifier
# Agent Skill Security Scan Report

**Skill:** practitioner-credentialing
**Directory:** /Users/user/fellowship/practitioner-credentialing/.local/elements-milestone/skill-bundle
**Status:** [OK] SAFE
**Max Severity:** MEDIUM
**Scan Duration:** 0.54s
**Timestamp:** 2026-10-22T06:20:00.019240+00:00

## Summary

- **Total Findings:** 2
- **Critical:** 0
- **High:** 0
- **Medium:** 1
- **Low:** 0
- **Info:** 1

## Findings

### MEDIUM Severity

#### [MEDIUM] Outbound network request primitives that can transmit data externally

**Severity:** MEDIUM
**Category:** data_exfiltration
**Rule ID:** DATA_EXFIL_NETWORK_REQUESTS
**Location:** credentialing/elements.py:368

**Description:** Pattern detected: requests.get(

**Code Snippet:**
```
"privilege_components": privilege_components(requests.get(key, []), certs, checks, rules, as_of),
```

**Remediation:** Ensure network operations are necessary and document allowed destinations

### INFO Severity

#### [INFO] Skill does not specify a license

**Severity:** INFO
**Category:** policy_violation
**Rule ID:** MANIFEST_MISSING_LICENSE
**Location:** SKILL.md

**Description:** Skill manifest does not include a 'license' field. Specifying a license helps users understand usage terms.

**Remediation:** Add 'license' field to SKILL.md frontmatter (e.g., MIT, Apache-2.0)

## Analyzers

The following analyzers were used:

- static_analyzer
- bytecode
- pipeline

