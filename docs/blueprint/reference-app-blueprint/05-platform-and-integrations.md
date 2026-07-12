---
guide_id: REFAPP-PLATFORM
title: Platform, Lib, and Integration Mapping
status: experimental
audience: human-and-ai
read_when:
  - Planning configuration, identity, database, storage, email, messaging, cache, telemetry, external clients, or composition roots.
skip_when:
  - The current slice is pure domain/application/presentation work with established ports.
depends_on:
  - README.md
  - ../03-shared-kernel-and-platform.md
  - ../11-security-identity-and-privacy.md
  - ../15-delivery-observability-and-operations.md
owns:
  - reference-app platform capability inventory
  - local/test/production adapter requirements
  - web/worker/migration composition mapping
  - preset lib/query/auth seams and compatibility evidence
---

# Platform, lib, and integration mapping

> `platform` is the portable role. A selected stack may call it `lib`, `infrastructure`, `adapters`, packages, or services; the name never moves business policy into it.

Create only mechanisms selected by `COVERAGE-*`. `BASIC_WEB` normally starts with config, database, telemetry and deployment primitives; auth is added for a private boundary, while HTTP/storage/email/messaging/cache/flags require an owning capability.

## Rule `REF-PLATFORM-MAP-01`: every mechanism implements an owned need

Recommended logical map:

```text
platform/
├── config/         typed environment and capability configuration
├── auth/           identity/session mechanism and current-subject adapter
├── database/       connection, migration runner and transaction capability
├── http/           bounded base client, deadlines and safe protocol metadata
├── storage/        object bytes, signed transfer and lifecycle mechanism
├── email/          transport and provider diagnostics
├── messaging/      queue/event transport and worker mechanics
├── cache/          cache/rate-limit mechanism when selected
├── telemetry/      logs, metrics, traces, errors and deploy markers
├── security/       crypto/secret/signature mechanisms
└── flags/          optional rollout/config mechanism
```

Module adapters translate these mechanisms into customer, order, payment, shipment, notification and import vocabulary.

## Capability contracts

| Platform role | Minimum contract | Required failure/recovery evidence |
| --- | --- | --- |
| Config | Parse once, fail fast, expose server-safe capability config and explicit public config | Missing/invalid/secret-leak tests |
| Auth | Verify session/credential, resolve trusted subject, revoke/expire and expose assurance facts | Expired/revoked/stale membership and privileged reauth |
| Database | Bounded client/pool, transaction capability, health and graceful close | Connection exhaustion, transaction rollback, migration job |
| HTTP | Deadline/cancellation, bounded body, retry classification and safe error metadata | Timeout, ambiguous mutation, quota and dependency outage |
| Storage | Put/get/delete or signed transfer, checksum/metadata and lifecycle | Failed upload, scan/quarantine, orphan cleanup and denied access |
| Email | Send normalized message, provider reference and safe failure | Sandbox/local capture, retry exhaustion and deduplication |
| Messaging/jobs | Durable identity, publish/claim/ack, retry/backoff, scheduling and dead-letter inspection | Duplicate, crash before/after effect, stale lease and replay |
| Cache/rate limit | Namespaced get/set/invalidate or decision contract | Miss/outage/eviction and no authorization widening |
| Telemetry | Structured log/metric/span/error, correlation and deploy/config markers | Redaction, cardinality/drop/exporter outage and shutdown flush |
| Secrets/crypto | Secret reference, encryption/signature/random capability | Rotation, revoked key, invalid signature and no raw value logging |
| Flags | Evaluated value with subject/tenant context and audit metadata | Kill switch, stale config, owner and expiry |

Do not add cache, flags or a dedicated broker merely to fill a folder. The capability coverage says whether the app needs them; reliability behavior remains mandatory for every selected async/integration capability even when a database-backed mechanism implements it.

## Local, test and deployed adapters

Every external capability records this matrix:

| Environment | Adapter expectation |
| --- | --- |
| Local | One-command dependency or deterministic local sink; no real external side effects |
| Automated test | Controllable fake for application tests plus real protocol/database adapter tests where risk requires |
| Preview/public demo | Isolated namespace, sandbox credentials, quota, TTL/cleanup and safe recipients |
| Production starter | Managed/operated adapter with rotation, monitoring, retry/recovery and data-lifecycle agreement |

Do not let test fakes become the only evidence for database constraints, webhook signatures, migrations or provider payload normalization.

## Composition roots

The reference app has explicit selected executable roots:

```text
web root        config -> telemetry -> selected auth/database/platform -> modules -> routes
worker root     only with CAP-ASYNC/BATCH -> telemetry -> database/messaging -> consumers/jobs
migration root  config -> database -> pending reviewed migrations -> exit
CLI/lab root    isolated config -> selected modules/adapters -> bounded operation -> exit
test root       deterministic selected adapters -> module/application contracts
```

Workers call application contracts directly through composition; they do not call the app's internal HTTP endpoints. Migration does not run implicitly inside a user request or every application instance startup.

## Rule `REF-INTEGRATION-ADAPTER-01`: provider protocol and business policy stay separate

Examples:

- Billing owns `PaymentGateway` and payment policy; its adapter uses a platform HTTP/secret/signature mechanism.
- Fulfillment owns `CarrierGateway` and shipment policy; its adapter normalizes carrier events.
- Notifications owns `NotificationSender`; an email adapter maps normalized intent to the selected transport.
- Catalog/Data Exchange own file purpose and authorization; storage handles object transfer only.

Each integration declares:

- capability/version and official source;
- request/response/event normalization;
- trusted authentication/signature boundary;
- deadline, retry, idempotency and ambiguous-outcome policy;
- quota/rate/degraded behavior;
- persistence and reconciliation owner;
- safe telemetry and redaction;
- sandbox/local adapter and replacement seam.

## Identity boundary

Identity platform owns provider configuration, account/session mechanics, auth endpoints and current-subject lookup. Workspaces owns organization/member/invitation policy. Every business module authorizes trusted subject + action + resource + organization; navigation visibility is presentation only.

Provider-generated auth schema joins the same reviewed migration/recovery lifecycle but remains provider mechanism data. Do not expose provider models as application DTOs.

## Database and migration boundary

- One connection module selects driver/pool by runtime.
- ORM/query clients remain inside adapters.
- Application ports expose domain/application types.
- Development generates reviewed migration files; release applies pending migrations through a dedicated job.
- Seed/reset commands target isolated local/test/demo data only and require explicit environment guards.
- Production/public-demo restore and migration follow parent guide `12`.

## Rule `REF-PLATFORM-QUERY-AUTH-01`: lib provides mechanics; features provide policy

For preset authoring, record these seams in [platform-plan](templates/platform-plan.md):

| `lib`/platform mechanism | May provide | Remains feature/application-owned |
| --- | --- | --- |
| Query request | Structural schema, bounds, canonicalization and operator primitives | Public aliases, allowed operators, relation/join mapping, projection and query budget |
| Database/ORM | Client lifecycle, transaction capability, safe translator helpers and error containment | Repository contract, mandatory subject/tenant predicate and business read/write ownership |
| Auth | Provider setup, session verification, trusted-subject facts and auth endpoints | Resource/tenant authorization, roles/capabilities and business denial policy |
| Result/error | Stable technical categories and safe correlation metadata | Business error codes, field mapping, localized message and UI invalidation policy |

The identity path is identity/session adapter -> trusted subject -> route/action guard -> feature authorization -> mandatory repository scope -> safe public result. Navigation visibility is never a security boundary, and a generic query helper cannot add or remove authorization predicates.

Each `verified` preset flow proves the chosen auth adapter and database driver/ORM together in the actual web runtime. Include expired/revoked session, denied resource/tenant, malformed query, transaction rollback and connection/adapter failure as selected negative evidence. Provider or ORM types stay inside their adapters even when the preset exposes convenience factories.

## Telemetry and operations

Initialize telemetry before application modules. Propagate correlation through web, outbox, worker, webhook and provider calls. Record safe module/use-case/error/dependency dimensions; never use unbounded customer/order IDs as metric labels.

Define health semantics per executable: liveness is process health, readiness is ability to accept required work, and dependency detail is access-controlled. Every critical job/integration has dashboard, alert, owner and recovery runbook.

## Required output

Fill [templates/platform-plan.md](templates/platform-plan.md). Every selected mechanism must name its owning need, port, local/test/demo/production adapter, configuration and secret classes, composition roots, failure evidence, health semantics and replacement seam.

## Stop conditions

Stop when `lib/platform` contains business workflows, a generic query helper accepts raw client field/relation paths, modules import raw provider SDKs without adapters, workers call internal HTTP, auth decides arbitrary business-resource policy, migration runs in request paths, local/public demo can contact real recipients or capture real money, or telemetry failure can fail the business operation.
