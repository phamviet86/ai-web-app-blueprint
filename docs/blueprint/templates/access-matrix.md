---
template_id: SKEL-TPL-ACCESS-MATRIX
template_version: 1.0.0
produces: access-matrix
owner_guide: ../11-security-identity-and-privacy.md
use_when: Defining resource/action/tenant authorization or privileged operations.
---

# Access matrix: [scope]

> Instantiate with schema `1.0` from [README.md](README.md).

- Policy owner:
- Identity source and assurance:
- Default decision: deny
- Tenant/resource ownership rule:

| Actor/role | Resource + scope | Action | Conditions/attributes | Reauth/audit | Negative tests |
| --- | --- | --- | --- | --- | --- |

## Lifecycle

- Grant/provisioning:
- Role/attribute change propagation:
- Revocation/session invalidation:
- Emergency/break-glass path:
- Review cadence and stale-access removal:

## Enforcement points

| Entrypoint/use case/query | Trusted subject/scope source | Policy function | Repository/data filter | Audit event |
| --- | --- | --- | --- | --- |
