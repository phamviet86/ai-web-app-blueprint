---
template_id: SKEL-TPL-THREAT-MODEL
template_version: 1.0.0
produces: threat-model
owner_guide: ../11-security-identity-and-privacy.md
use_when: Adding/changing an external, identity, privileged, sensitive-data, file, webhook, or admin boundary.
---

# Threat model: [scope]

> Instantiate with schema `1.0` from [README.md](README.md).

- Owner / reviewers:
- Date / revisit trigger:
- System-profile classifications:
- Assets and unacceptable outcomes:

## Data flow and trust boundaries

```text
[actor] -> [entrypoint] -> [application/module] -> [data/vendor/queue]
```

| Boundary/component | Trust/identity | Data | Privilege | Existing controls |
| --- | --- | --- | --- | --- |

## Threats and controls

| Threat/abuse case | Likelihood/impact | Prevention | Detection | Recovery | Owner |
| --- | --- | --- | --- | --- | --- |

Cover applicable identity/session abuse, authorization/tenant escape, injection/encoding, CSRF/CORS, SSRF, file/upload, replay/idempotency, rate/resource exhaustion, secret leakage, dependency compromise, privacy leakage, audit tampering, and admin/recovery abuse.

## Verification and residual risk

| Control | Positive/negative evidence | Environment | Residual risk/acceptor |
| --- | --- | --- | --- |
