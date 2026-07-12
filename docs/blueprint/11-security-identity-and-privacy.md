---
guide_id: SKEL-SECURITY
title: Security, Identity, and Privacy Contracts
status: experimental
audience: human-and-ai
read_when:
  - Designing or changing authentication, authorization, tenancy, sessions, external boundaries, secrets, sensitive data, or security audit behavior.
  - Establishing the security and privacy baseline for a new repository.
skip_when:
  - The change is purely presentational and does not alter trust, identity, data exposure, callable behavior, or configuration.
depends_on:
  - README.md
owns:
  - threat and risk modeling
  - identity and session lifecycle
  - authorization and tenant isolation
  - input, output, and edge abuse controls
  - browser hardening baseline
  - secret lifecycle
  - privacy and security audit contracts
  - security detection and response requirements
---

# Security, identity, and privacy contracts

> Core rule: security controls follow the system's actual exposure, data sensitivity, tenancy, criticality, and identity assurance needs. A control may be conditional, but a trust boundary may never remain implicit.

## Security profile

Before selecting controls, record a compact system profile:

- public, partner, internal, or machine-only exposure;
- protected assets and sensitive operations;
- data classification and tenant model;
- human, service, support, and administrative identities;
- availability and fraud impact;
- applicable legal, contractual, or regulatory constraints;
- accepted residual risks and accountable owners.

Use profile labels such as `baseline`, `internet-facing`, `multi-tenant`, `regulated`, and `high-assurance`. Do not apply every advanced control to every repository, but require evidence for every applicable control and a reason for every material `not-applicable` decision.

For web applications, use [OWASP ASVS 5.0](https://owasp.org/www-project-application-security-verification-standard/) as a versioned verification catalog; select controls from the system profile rather than treating the entire catalog as identical ceremony for every repo.
When identity proofing, authenticator assurance, or federation is material, map the system profile to IAL/AAL/FAL or an equivalent assurance model, including phishing resistance, reauthentication, and recovery requirements. Use [NIST SP 800-63-4](https://csrc.nist.gov/pubs/sp/800/63/4/final) as a current primary reference and tailor it to the system's jurisdiction and risk.

Use [templates/threat-model.md](templates/threat-model.md) and [templates/access-matrix.md](templates/access-matrix.md) only when the routed boundary needs those artifacts.

## Rule `SEC-RISK-01`: model threats at trust boundaries

For each external or privileged boundary, identify:

1. assets and security properties to protect;
2. callers, operators, dependencies, and potential attackers;
3. entry points, data flows, and privilege transitions;
4. abuse cases, failure impact, and current mitigations;
5. control owner, verification evidence, and residual risk.

Refresh the model when adding a new identity type, public endpoint, tenant boundary, sensitive data flow, vendor, upload, webhook, background worker, or administrative capability. A lightweight data-flow diagram plus an abuse-case table is sufficient for a small service.

Threat modeling is not a compliance inventory. Prioritize credible misuse paths and controls that materially reduce risk.

## Rule `IDENTITY-LIFECYCLE-01`: identities have explicit states and owners

Define lifecycle states and allowed transitions for every identity type:

```text
invited/provisioned -> active -> locked or suspended -> recovered -> deprovisioned
```

The exact states may differ, but the contract must cover:

- enrollment/provisioning and identity proofing appropriate to risk;
- credential or authenticator enrollment, replacement, and recovery;
- account linking and prevention of accidental identity takeover;
- lock, suspend, disable, and deprovision behavior;
- role, tenant-membership, and ownership changes;
- service-account owner, purpose, scope, and expiry;
- support impersonation or break-glass access when applicable.

Use an immutable internal subject identifier. Email, username, phone number, or vendor handle may change and must not silently become the authorization identity.

High-impact recovery, authenticator reset, privilege elevation, and sensitive account changes require risk-appropriate reauthentication and audit evidence.

## Rule `SESSION-LIFECYCLE-01`: sessions are bounded and revocable

Document:

- issuance and rotation rules;
- idle and absolute lifetime;
- revocation after password/authenticator reset, suspension, compromise, or material privilege change;
- reauthentication triggers for sensitive actions;
- concurrent-session/device policy when risk requires it;
- secure transport and storage appropriate to the client type;
- refresh-token or long-lived credential rotation and replay handling;
- logout semantics across the current session, all sessions, and federated providers.

Do not authorize from stale client claims when current server state can revoke or narrow access. Do not expose bearer credentials to logs, URLs, analytics, or browser storage that is inappropriate for their threat model.

## Rule `AUTHZ-DEFAULT-DENY-01`: authorization is server-enforced policy

Model authorization as:

```text
subject + action + resource + trusted context -> allow or deny
```

- Default to deny when no policy explicitly permits the action.
- Enforce at every callable server boundary and data access path; navigation and hidden controls are presentation only.
- Treat roles as coarse grants, not a substitute for tenant, ownership, record-state, relationship, or purpose checks.
- Derive subject, tenant, support mode, and trusted route context server-side.
- Apply field-level read/write rules where records contain mixed sensitivity.
- Keep privileged administration, impersonation, export, and bulk operations explicit and auditable.
- Re-evaluate authorization when the resource changes between read and write.

Maintain an access matrix for important `subject x action x resource` combinations. Test allowed paths and denied paths, including stale role, wrong owner, wrong tenant, disabled account, and direct callable access.

## Rule `TENANT-ISOLATION-01`: trusted tenant context scopes every authorized action

For a multi-tenant system:

- resolve tenant membership from trusted identity/context;
- authorize `subject x action x resource x tenant` at every callable and query boundary;
- prevent a client filter or identifier from widening tenant scope;
- include tenant identity in idempotency, rate-limit, and cache namespaces where it affects behavior;
- make cross-tenant support access explicit, time-bounded when possible, and audited;
- re-evaluate access when membership, resource ownership, or tenant state changes between read and write.

Physical row/schema/database/account isolation, tenant-scoped storage, restore, deletion, and migration are owned by `DATA-ISOLATION-01` in [12-data-lifecycle-migrations-and-recovery.md](12-data-lifecycle-migrations-and-recovery.md#rule-data-isolation-01-environments-tenants-and-workloads-do-not-share-trust-accidentally). Prove the combined security/data path with automated negative tests and review every bypass or privileged path.

## Rule `SEC-INPUT-OUTPUT-01`: validate meaning before use and encode for the sink

- Parse untrusted input into a strict application shape; reject unknown or ambiguous intent where it could broaden behavior.
- Bound size, count, depth, range, content type, filename, and processing cost.
- Canonicalize identifiers and paths before authorization or comparison.
- Use parameterized database/query APIs and safe process invocation.
- Encode output for its actual HTML, URL, JSON, header, log, SQL, shell, or template context.
- Validate uploaded content independently of the claimed extension/type; isolate storage and scanning according to risk.
- Return safe errors without stack traces, secrets, internal topology, or unnecessarily sensitive identifiers.

Validation does not replace authorization, and output encoding does not make an unsafe interpreter or query boundary acceptable.

## Rule `SEC-EDGE-ABUSE-01`: public edges have explicit abuse controls

Inventory public pages, APIs, webhooks, callbacks, uploads, redirects, and authentication endpoints. For each applicable edge, decide:

- rate, concurrency, payload, and resource quotas;
- automated-abuse, credential-stuffing, enumeration, and expensive-query protection;
- request-origin, CSRF, CORS, cookie, and redirect policy;
- SSRF-safe destination allowlists and network egress restrictions;
- provider-supported webhook authenticity/integrity and replay policy under `VENDOR-WEBHOOK-01` in [13-reliability-async-and-integrations.md](13-reliability-async-and-integrations.md#rule-vendor-webhook-01-integrations-separate-protocol-policy-and-delivery-state);
- safe file handling, decompression, parsing, and asynchronous scanning;
- failure behavior that does not reveal whether a protected identity/resource exists.

Rate limiting is defense in depth, not authorization. Fail closed for security decisions; use graceful degradation only where it cannot widen access.

## Rule `BROWSER-HARDENING-01`: browser defenses are explicit and verified at the delivered edge

For a browser-facing application, select and record an environment-appropriate baseline at the final response/CDN layer:

- serve authenticated and sensitive traffic only over approved TLS; redirect insecure production traffic and enable HSTS only after the covered hosts and subdomains are proven HTTPS-ready;
- set session cookies with `Secure`, `HttpOnly`, an intentional `SameSite` mode, narrow path/domain, and bounded lifetime; pair cross-site requirements with explicit CSRF defenses;
- allowlist exact CORS origins, methods, and headers; never combine credentialed requests with a wildcard origin or treat CORS as authorization;
- deploy a Content Security Policy from report-only measurement to enforcement, using nonces/hashes or another reviewed strategy; restrict framing with `frame-ancestors` and sandbox untrusted/embedded content;
- set MIME-sniffing, referrer, and browser-capability policies appropriate to the routes (`X-Content-Type-Options`, `Referrer-Policy`, and `Permissions-Policy` or platform equivalents);
- keep untrusted values out of executable DOM/URL/style sinks, and constrain third-party scripts with minimal origin access plus integrity pinning when the delivery model supports it;
- apply `HTTP-CACHE-01` from [09-query-cache-and-read-models.md](09-query-cache-and-read-models.md#rule-http-cache-01-browsers-and-cdns-cache-only-an-explicit-representation-contract) so edge caching cannot bypass session or tenant isolation.

Exact directives belong to the stack/system profile because routes and integrations differ. Evidence must inspect delivered headers and cookies through the real proxy/CDN, exercise CSRF/CORS/frame/XSS abuse cases, and prove production policy does not silently disappear on errors or redirects.

## Rule `SECRET-LIFECYCLE-01`: every secret is inventoried, scoped, and rotatable

For credentials, signing keys, certificates, tokens, and encryption keys, record:

- owner, purpose, consumers, environment, scope, and blast radius;
- source of truth and delivery mechanism;
- creation, expiry, rotation, revocation, and emergency replacement procedure;
- access/audit policy and dependent systems;
- whether a short-lived workload identity or dynamic credential can replace it.

Use a designated secret-management mechanism when available. Prefer least-privilege, environment-specific, short-lived credentials. Never commit secrets or put them in client bundles, fixtures, documentation, telemetry, build output, or AI context.

Validate required configuration without printing values. Secret scanning is a detection layer, not permission to store secrets in source. A suspected leak requires revocation/rotation first; deleting the visible string alone is insufficient.

## Rule `PRIVACY-LIFECYCLE-01`: personal data has a declared purpose and end state

- Assess foreseeable privacy harm to individuals as well as organizational, contractual, and legal exposure; use the [NIST Privacy Framework](https://www.nist.gov/privacy-framework/getting-started-0) as a voluntary risk vocabulary when useful.
- Collect the minimum data needed for a recorded purpose.
- Identify the applicable permission, notice, consent, or other processing basis with domain/legal owners.
- Define access, correction, export, retention, deletion, and legal-hold behavior.
- Propagate lifecycle actions to caches, indexes, analytics, logs, vendors, derived data, and backups according to the documented policy.
- Mask or synthesize sensitive production data before non-production use.
- Minimize personal data in URLs, telemetry, support tools, fixtures, and audit records.
- Record vendor/subprocessor transfers, locations, purposes, retention, and deletion commitments when relevant.

Detailed storage inventory, retention execution, and recovery behavior belong to [12-data-lifecycle-migrations-and-recovery.md](12-data-lifecycle-migrations-and-recovery.md).

## Rule `SEC-AUDIT-01`: security audit records answer who did what and why

Audit at least applicable authentication events, failed authorization, privilege/membership changes, support impersonation, sensitive reads/exports/deletions, secret administration, and security-policy changes.

An audit event contains a trusted timestamp, actor/subject, action, target, tenant/scope, outcome, reason/code, source, and correlation identifier. It must not contain credentials or unnecessary sensitive payloads.

Protect audit records from unauthorized modification/deletion, restrict access, define retention, and make them searchable enough for investigation. Application logs, product history, and security audit are distinct contracts even when they share transport.

## Rule `SEC-DETECTION-RESPONSE-01`: material abuse paths have an exercised detection and containment path

Derive detection cases from the threat model and data classification. At minimum where applicable, cover authentication/recovery abuse, repeated authorization or tenant-isolation denial, privilege/support-mode changes, sensitive export/deletion, secret/key administration, integrity/configuration change, malware/upload findings, and unusual rate or origin behavior.

Each case declares signal source and safe fields, threshold/correlation logic, expected false-positive handling, severity, route/on-call owner, acknowledge/contain targets, and a short playbook. The playbook covers triage, evidence preservation and access, containment, session/credential/key revocation, affected-scope assessment, recovery validation, communication/notification decision, and handoff to `INCIDENT-RECOVERY-01` in [15-delivery-observability-and-operations.md](15-delivery-observability-and-operations.md#rule-incident-recovery-01-recovery-is-practiced-evidence).

Exercise representative detections with safe simulations on a declared cadence and after material trust-boundary changes. Record delivery, acknowledgement, decision, containment, recovery, gaps, and owners. A dashboard or stored audit event without a tested route and response action is not detection evidence; collecting raw secrets or sensitive payloads to make detection possible is unacceptable.

## Acceptance evidence

- [ ] System security profile and current threat/abuse model exist for material boundaries.
- [ ] Human, service, support, and admin identity/session lifecycles are defined where applicable.
- [ ] Access matrix and automated allow/deny tests cover ownership, privilege, disabled identity, and tenant isolation.
- [ ] Public-edge inventory records validation, abuse limits, origin/request, upload, callback, and webhook controls as applicable.
- [ ] Browser-facing delivery has verified TLS, cookie, CSRF/CORS, CSP/framing, MIME, referrer, capability, and cache policy as applicable.
- [ ] Secret inventory has owners, scopes, rotation/revocation procedures, and evidence of leak detection.
- [ ] Personal-data inventory links purpose, harms, access, retention, deletion, vendors, and non-production handling.
- [ ] Where personal-data rights/lifecycle actions apply, tests or operational records prove identity verification, authorization, access/correction/export scope, permission withdrawal, legal-hold conflicts, deletion propagation, vendor completion, and re-deletion after restore.
- [ ] Representative security audit events are complete, correlated, access-controlled, and free of secrets/raw sensitive payloads.
- [ ] Material security detections route to an owner and a recent safe exercise proves triage, containment, recovery, and notification decision paths.
- [ ] Every high-impact exception has an owner, reason, expiry/review date, and residual-risk statement.

## Stop conditions

Stop and redesign when identity or tenant context comes from an authoritative client claim, a missing rule becomes allow, session/credential compromise has no revocation path, cross-tenant access is an implicit query convention, browser policy is absent at the delivered edge, a public edge has unbounded costly input, a secret has no owner/rotation path, production personal data is copied to non-production unmasked, detection has no routed containment action, or auditability requires logging the sensitive payload itself.
