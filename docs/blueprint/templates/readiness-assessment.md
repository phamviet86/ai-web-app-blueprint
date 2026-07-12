---
template_id: SKEL-TPL-READINESS-ASSESSMENT
template_version: 1.0.0
produces: readiness-assessment
owner_guide: ../08-scorecard-and-readiness-gates.md
use_when: Scoring blueprint maturity or deciding a greenfield, evolution, refactor, or release gate.
---

# Readiness assessment: [repo/system/scope]

> Instantiate with schema `1.0` from [README.md](README.md).

- Assessment owner / reviewers:
- System-profile artifact ID/version / operating mode (`GREENFIELD`, `EVOLUTION`, `REFACTOR`, `RELEASE`, or `AUDIT`):
- Control catalog version: `1.0.0`
- Assessment JSON `assessment_id` (must equal frontmatter `artifact_id`):
- Source revision, built artifact/deployment identity, and environment:
- Assessment `as_of` timestamp and timezone:
- Evidence freshness policy, default validity window, and next review trigger:
- Evidence manifest path/digest, exact trusted producer list, and accountable evidence acceptor:
- Machine-readable input/result locator and scoring command:

## Control evidence

- [ ] Every stable control ID in catalog `1.0.0` is mapped exactly once below.
- [ ] Every baseline control is applicable; every conditional exclusion is proved by the accepted system profile.
- [ ] Every selected repo-owned control has a distinct `CTL-*` ID, dimension, source rule, and expected outcome.
- [ ] Every conditional exclusion has owner, rationale, revisit trigger, decision date, and `artifact:`/`review:` applicability evidence; no dimension is empty.
- [ ] `unknown` applicability is scored as applicable with missing evidence, never excluded.
- [ ] Evidence locators identify exact revision/environment/time/result, not only a document claim.
- [ ] Strong, passed-gate, and N/A evidence resolves through the pinned manifest; producer trust is reviewed separately from hash integrity.

| Dimension | Control ID / source rule | Applicable: yes/no/unknown | Critical? and rationale | Expected outcome | Exact evidence locator/result | Observed at | Valid until or invalidation trigger | Owner | Score | N/A rationale and revisit |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

Use `0.00`, `0.25`, `0.50`, `0.75`, or `1.00`. Evidence locators use `command:`, `test:`, `artifact:`, `measurement:`, `drill:`, `runtime:`, `review:`, or `planning:`. Missing/contradictory evidence is `0.00`; stale or invalidated evidence cannot support more than `0.50` until refreshed. Scores `0.75` and `1.00` require observed command/test/measurement/drill/runtime evidence. Exclude only `baseline: false` controls and only with the full owned profile-decision record above.

Create the complete machine input with `python3 docs/blueprint/scripts/score_readiness.py --init path/to/assessment.json`. Map table applicability `yes/no/unknown` to JSON `true/false/null`; unresolved `null` is an error and scores `0.00` until decided.

## Dimension calculation

| Dimension | Applicable controls | Arithmetic mean | Critical minimum | Missing/stale critical evidence | Gate result |
| --- | ---: | ---: | ---: | --- | --- |
| 1. Drivers/topology/modules | | | | | |
| 2. Public contracts/sync flows | | | | | |
| 3. Security/identity/privacy | | | | | |
| 4. Data/migration/recovery | | | | | |
| 5. Reliability/integrations | | | | | |
| 6. Runtime/UX/performance | | | | | |
| 7. Testing/fitness | | | | | |
| 8. Developer experience/delivery | | | | | |
| 9. Observability/operations | | | | | |
| 10. Evolution/governance/AI | | | | | |

## Readiness declaration

- Calculation result and exact scorer version/command:
- Total `/10` (sum of unrounded ten-dimension means; round half-up to two decimals only for display):
- Applicable gate IDs, pass/fail, exact evidence, observed date, and validity/invalidation trigger:
- Critical/high-risk unknowns:
- Result: target / estimated / not-ready / ready / 9.5-ready
- Residual risk acceptance owner:
- Next evidence refresh or invalidation trigger:

## Reproduction record

```text
source revision:
profile artifact/version:
catalog version:
assessment input digest:
evidence manifest ID/digest and resolved-reference count:
accepted producer trust policy / reviewer:
scorer command/version:
output digest:
calculated at/timezone:
```

Do not declare `9.5-ready` unless total is at least `9.50`, every dimension and critical applicable control is at least `0.75`, no evidence is stale, and all applicable gates pass.
