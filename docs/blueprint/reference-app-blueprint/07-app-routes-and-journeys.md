---
guide_id: REFAPP-ROUTES
title: App Routes and User Journeys
status: experimental
audience: human-and-ai
read_when:
  - Planning route groups, access, runtime boundaries, screen states, entrypoints, or end-to-end journeys.
skip_when:
  - Implementing a server-only module with an approved entrypoint contract.
depends_on:
  - README.md
  - ../10-runtime-accessibility-and-performance.md
owns:
  - FulfillOps logical route tree and access map
  - reference route-state and user-journey requirements
  - preset app-composition and route-to-surface compatibility
---

# App routes and user journeys

> Routes mount feature presentation and application contracts. They do not own business policy, persistence queries or trusted authorization.

The route tree is a `FULL_SHOWCASE` catalog. A tier plan includes only routes and protocols traced from selected `CAP-*`; `BASIC_WEB` may contain one list/form/detail journey plus health/operations entrypoints appropriate to its deployment.

## Rule `REF-ROUTE-MAP-01`: every route declares access, runtime and states

Each route entry records:

- stable `ROUTE-*` ID and logical path;
- public/authenticated/organization/role/resource access policy;
- server/browser/stream/worker runtime decision;
- owning module query/command and public DTO;
- search/filter/page/cache identity when present;
- loading, empty, stale, partial, degraded, denied, not-found and unexpected-error behavior;
- accessibility/focus/responsive contract;
- telemetry journey/route name and critical SLI;
- stack-specific file mapping only after the profile is selected.

## Logical route tree

Paths are examples; preserve roles when a framework uses another router. Absence of an unselected capability is preferable to an empty route.

### Public and identity

| Logical path | Access | Owner/purpose |
| --- | --- | --- |
| `/` | Public | Product explanation, demo limitations and sign-in entry |
| `/features` | Public | Capability showcase sourced from static product content, not fake live metrics |
| `/sign-in` | Anonymous-only where useful | Identity adapter entry |
| `/accept-invite/:token` | Token + identity checks | Workspaces invite acceptance |
| `/status` | Public sanitized status or hosted status link | Operations; no secret dependency detail |

### Account

| Logical path | Access | Owner/purpose |
| --- | --- | --- |
| `/settings/profile` | Authenticated subject | User profile/locale/timezone |
| `/settings/security` | Authenticated + reauth for sensitive action | Sessions, authenticators, recovery and revoke |

### Organization workspace

Use `/app/:organizationSlug` or an equivalent trusted active-organization context.

Access labels below name capability sets, not a single role enum. Workspaces resolves them from active `membership_roles`; business modules still authorize subject + action + resource + organization. Separate system roles apply only to system entrypoints and never imply organization access.

| Child path | Minimum access | Owner/purpose |
| --- | --- | --- |
| `/overview` | Member | Insights operational dashboard with freshness |
| `/customers` | Member; writes by capability | CRM list/search/create |
| `/customers/:customerId` | Resource-scoped | CRM detail, addresses, privacy state, related orders |
| `/catalog` | Member; writes by operator | Catalog list/search/media |
| `/catalog/:productId` | Resource-scoped | Product detail and inventory availability query |
| `/inventory` | Inventory viewer/operator | Availability, warehouse filter and stock ledger |
| `/inventory/reservations/:id` | Inventory operator | Reservation detail and authorized repair/release |
| `/orders` | Member; writes by sales/operator | Order list/search/create |
| `/orders/:orderId` | Resource-scoped | Timeline, lines, stock, payment, shipment and audit links |
| `/invoices` | Billing viewer/operator | Receivables list/aging |
| `/invoices/:invoiceId` | Resource-scoped | Invoice, payment intents, applied captures and reconciliation status |
| `/shipments` | Fulfillment viewer/operator | Ready/in-progress/exception shipments |
| `/shipments/:shipmentId` | Resource-scoped | Items, tracking timeline and carrier status |
| `/imports` | Data operator | Upload/preview/start/progress/history |
| `/imports/:jobId` | Job owner/operator | Row failures, pause/resume/retry/result |
| `/notifications` | Current subject | In-app notifications and read state |
| `/reports` | Report capability | Bounded operational/financial reports and export |
| `/settings/members` | Organization admin | Members, invitations and roles |
| `/settings/integrations` | Privileged + reauth | Payment connection metadata/health; carrier and external-email controls only when selected |
| `/settings/audit` | Auditor/admin | Security audit search/detail |

### System operations

| Logical path | Access | Owner/purpose |
| --- | --- | --- |
| `/system/operations` | System operator | Queue/job/provider health and deploy markers |
| `/system/failed-work` | System operator + reauth | Failure inspection and delegated replay preview |
| `/system/security` | Security admin | Identity/security events and policy state |

System routes never bypass tenant/module authorization merely because the subject is an operator. Cross-tenant support access is explicit, scoped, time-bounded where possible and audited.

### Protocol entrypoints

| Logical path/channel | Runtime/access | Contract |
| --- | --- | --- |
| `/api/auth/*` | Selected identity-provider protocol | Platform auth handler only |
| `/api/webhooks/payment/:provider` | `CAP-INTEGRATION` public edge with provider authenticity | Billing durable webhook acceptance |
| `/api/webhooks/carrier/:provider` | Conditional public edge with provider authenticity | Fulfillment durable webhook acceptance only with `CAP-CARRIER-PROVIDER` |
| `/api/files/upload-intent` | `CAP-FILES`, authenticated/resource-scoped | Catalog/Data Exchange file policy -> storage transfer |
| `/api/health/live` | Bounded platform check | Process liveness |
| `/api/health/ready` | Restricted/public-safe result | Required dependency readiness |
| worker consumers | Selected `CAP-ASYNC`/`CAP-BATCH`; durable identity | Application commands through worker composition root |
| scheduled reconciliation/reset | Selected reconciliation/demo capability; scheduler identity and lease | Bounded application job; not anonymous HTTP policy |

## Rule `REF-APP-COMPOSITION-01`: app mounts contracts; it does not become a feature layer

For every preset, the app/framework tree owns only routes, layouts, loading/error/not-found boundaries, metadata, provider/composition setup and protocol entrypoints. Feature views and public actions/queries are mounted from their owner modules; generic UI mechanics come from shared; database/auth/provider mechanisms come from `lib`/platform.

Each verified interactive route records this compatibility row in [route-map](templates/route-map.md):

| Route concern | Required mapping |
| --- | --- |
| Surface | Table/list/masonry/calendar/detail/form or custom selected presentation |
| Request/input | Canonical query parts or normalized form values emitted by the surface |
| Feature contract | Public query/command, trusted boundary and result/error shape |
| Runtime | Server read, browser lifecycle, action/handler and serialization boundary |
| Outcome | Loading/empty/error/stale/denied/success, focus/navigation and invalidation |

Server presentation may provide an initial read directly through the feature query. Add TanStack Query or another browser server-state layer only for a declared refetch, mutation, polling, optimistic or offline-like lifecycle, with one hydration/freshness contract. The route never reconstructs feature query aliases, columns, form schema or authorization policy.

For Next.js presets using the `src` option, route code lives under `src/app`; framework configuration, package/lock files and other framework-default root files remain outside `src` as declared by the preset materialization map.

## Server/browser runtime policy

- Default initial reads to server presentation when the framework supports it.
- Add browser query/cache only for refetch, mutation lifecycle, polling, optimistic interaction or offline-like behavior.
- Do not call an internal HTTP route from server presentation merely to reach the database.
- Keep client boundaries small and serializable.
- Route handlers parse protocol and call one application contract; they do not contain transactions.
- Large imports, notifications, projection rebuild and reconciliation run asynchronously.

## Screen-state contract

Every data surface handles:

- initial loading or streaming fallback without layout/focus chaos;
- empty state with the next allowed action;
- validation/domain/conflict/dependency errors distinctly;
- authorization denied versus intentionally hidden not-found policy;
- stale projection/cache indication when material;
- partial/degraded external state without plausible false success;
- retry only when policy says it is safe;
- mutation pending/duplicate completion and navigation/focus result;
- responsive keyboard-accessible interaction.

## `FULL_SHOWCASE` journey catalog and route evidence

1. `JRN-ONBOARD`: sign in -> create organization -> assign roles -> invite -> accept -> switch organization.
2. `JRN-CUSTOMER-CATALOG`: create customer/product -> upload media -> bounded search/detail.
3. `JRN-ORDER`: create/edit/submit order -> observe asynchronous reservation result.
4. `JRN-PAYMENT`: issue invoice -> simulate payment -> receive duplicate webhook -> one invoice balance effect -> reconcile ambiguity.
5. `JRN-FULFILLMENT`: create shipment -> request dispatch -> consume reservation -> dispatch/deliver -> complete order; add carrier events only when selected.
6. `JRN-NOTIFICATION`: generate in-app/local delivery -> inspect failure -> preview/replay.
7. `JRN-IMPORT`: import catalog -> partial row errors -> resume -> verify products.
8. `JRN-OPERATIONS`: view projection freshness -> bounded report/export -> follow correlated trace.
9. `JRN-RECOVERY`: inspect failed provider/job work -> follow runbook -> authorized repair/replay/restore evidence.
10. `JRN-TENANT-DENY`: attempt wrong-tenant IDs, stale roles and disabled membership through direct callable entrypoints.

Browser E2E covers critical observable wiring. Application/integration tests prove authorization, transaction, idempotency, import, webhook and event behavior below the UI.

## Route-map output

Fill one [templates/route-map.md](templates/route-map.md) `ROUTES-*` artifact, assign stable `ROUTE-*` IDs and select only `JRN-*` entries required by guide `02`; then let the accepted `STACK-*` source profile map logical paths into concrete files/layouts/providers. For HTMX, record full versus partial response and history/fallback behavior; for Next.js, record server/client and route/action boundaries.

## Stop conditions

Stop when a route queries ORM directly, rebuilds feature query/form policy, UI visibility replaces callable authorization, every page becomes a client component, server presentation calls internal HTTP, a webhook acknowledges before required durable acceptance, a system route grants implicit tenant bypass, or loading/error/empty behavior is left to library defaults.
