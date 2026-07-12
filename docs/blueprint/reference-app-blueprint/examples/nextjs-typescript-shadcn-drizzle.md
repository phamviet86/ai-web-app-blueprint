---
example_id: REFAPP-EXAMPLE-NEXT-SHADCN-DRIZZLE
title: Next.js, TypeScript, shadcn, TanStack Query, Better Auth, PostgreSQL, and Drizzle
status: experimental
audience: human-and-ai
verified_on: 2026-07-12
non_authoritative: true
read_when:
  - The user accepts the worked web stack or needs an example stack decision to adapt.
depends_on:
  - ../README.md
---

# Worked stack example: Next.js, TypeScript, shadcn, and Drizzle

> This is a non-authoritative example, not a version pin. Resolve current official docs, peer compatibility, runtime support and deployment constraints before generating an accepted project-local stack artifact.

The topology below is intentionally broad enough for `FULL_SHOWCASE` async/integration work. It is not the default for `BASIC_WEB`: the accepted `COVERAGE-*` must remove the worker, queue, object storage, email, cache, providers and related local services when their capabilities are not selected.

## Intended topology

Use one modular-monolith repository with separate executable roots:

```text
Node web application
  + dedicated Node worker
  + release migration job
  + test/lab CLI

PostgreSQL authority
dedicated no-eviction Redis/Valkey durable queue service
S3-compatible object storage
email sandbox/provider
OTLP telemetry backend
```

This topology demonstrates web, worker, graceful shutdown, queue replay and telemetry without pretending short-lived request functions can run a persistent worker. A serverless-first deployment must replace BullMQ/long-lived worker assumptions with a verified managed durable-job adapter and re-evaluate database pooling plus telemetry flush.

## Stack card

| Role | Worked selection | Ownership boundary |
| --- | --- | --- |
| Web/runtime | Next.js App Router + React on Node runtime | `app` contains thin route/layout/composition entrypoints |
| Language/tooling | Strict TypeScript, one package manager/lockfile | Public boundaries avoid unchecked types |
| UI/styling | Tailwind CSS + shadcn/ui + Lucide | Installed component source is repo-owned shared UI; module presentation owns business composition |
| Browser server-state | TanStack Query | Only interactive refetch/mutation/polling/optimistic/cache lifecycle; module owns keys/options |
| Identity | Better Auth with database-backed sessions | `platform/auth` owns account/session mechanics; Workspaces/business modules own authorization |
| SQL/ORM | PostgreSQL + Drizzle ORM/Kit + `postgres.js` | Platform owns connection/migration root; module adapters own queries/mapping |
| Validation | Zod | Config, transport/action, form, event and vendor boundaries |
| Storage | S3-compatible API; MinIO local | Platform transfers bytes; Catalog/Data Exchange own purpose, metadata and authorization |
| Email | Mailpit local; Resend adapter for deployed sandbox/production | Notifications owns intent/retry policy; adapter owns protocol |
| Jobs/queue | BullMQ + dedicated `noeviction` Redis/Valkey service + dedicated worker | Application owns job/event identity and recovery; platform owns transport |
| Cache/rate limit | Separate Redis/Valkey service/instance only when measured | Never source of truth or authorization; eviction policy cannot affect the queue |
| Telemetry | OpenTelemetry/OTLP + structured logs; hosted error backend optional | Initialize at executable roots; redact and bound cardinality |
| Tests | Vitest, Testing Library, Playwright, real isolated PostgreSQL and queue adapter tests | Risk-routed evidence, not E2E for everything |
| Local environment | Container composition for Postgres, queue Redis/Valkey, MinIO, Mailpit and telemetry collector; optional separate cache | One documented start/check/reset path |
| Deployment | Containerized web + worker, managed PostgreSQL/object store/Redis/email/OTLP | Same-region where practical; migration runs once as release job |

Resolve exact versions when implementation starts. Context7 evidence used for this example included Next.js `v16.2.9`, TanStack Query `v5.90.3`, Better Auth `v1.6.23`, current shadcn/ui source docs and current Drizzle ORM docs; these are evidence dates, not automatic pins.

The durable queue store must not share an eviction-capable cache instance. Sharing is allowed only when the entire Redis/Valkey instance uses `noeviction`, has a dedicated memory budget, and cache writes are explicitly allowed to fail when memory is full; a separate service/instance is the safer default.

## Recommended source mapping

```text
src/
├── app/
│   ├── (public)/
│   ├── (auth)/
│   ├── (workspace)/
│   ├── api/auth/[...all]/route.ts
│   ├── api/webhooks/<capability>/<provider>/route.ts
│   ├── layout.tsx
│   └── providers.tsx
├── modules/<capability>/
│   ├── public/
│   │   ├── shared.ts
│   │   ├── server.ts
│   │   └── client/{actions.ts,browser.ts}
│   ├── application/
│   ├── domain/
│   ├── adapters/
│   ├── presentation/{server,client}/
│   └── compose.ts
├── shared/{kernel,ui,hooks,formatting,testing}/
├── platform/{config,auth,database,http,storage,email,messaging,cache,telemetry,security}/
├── workers/
└── instrumentation.ts
```

Keep public entrypoints runtime-homogeneous. `public/server` and adapters are server-only; `public/client/actions` contains browser-callable server actions; `public/client/browser` contains no server import.

## Next.js runtime policy

- Server Components call module server queries directly; they do not call internal Route Handlers for database reads.
- Client Components are small islands for events, effects and browser-only libraries.
- Server-to-client props are serializable and intentionally projected.
- Server Actions and Route Handlers parse input, derive trusted context, authorize, call application contracts and map typed errors.
- External webhooks use Route Handlers; business transactions remain in modules.
- Worker consumers call application contracts through the worker composition root, not through HTTP.

## shadcn/ui policy

shadcn/ui installs open component source that the repository owns. Record `components.json`, aliases, Tailwind/theme tokens, icon choice and RSC/TSX configuration. Treat installed primitives as design-system source, not third-party black boxes.

- Keep primitives in shared UI and review their accessibility/upgrades.
- Compose feature-specific tables/forms/status/actions inside module presentation.
- Do not wrap every primitive or generate unused components.
- Verify keyboard, focus, labels, errors, responsive behavior and dark/theme contrast.

## TanStack Query policy

Default to server reads. Use TanStack Query only for browser state needing refetch, mutation lifecycle, polling, optimistic updates or cache coordination.

- Use stable module-owned query keys/options.
- For prefetch/hydration, create a request-local server QueryClient and stable browser QueryClient.
- Use a domain-appropriate nonzero `staleTime` when immediate hydration refetch would duplicate work.
- Invalidate only affected keys and pass cancellation signals where supported.
- Do not maintain a server-rendered and client-fetched authority without one freshness contract.

## Better Auth policy

- Better Auth owns user/session/account/verification mechanism and auth protocol endpoint.
- The default example keeps organizations, memberships and invitations in the Workspaces module so business authorization is provider-independent.
- Generate/review auth schema and include it in the same Drizzle migration/recovery history.
- Store secrets in managed configuration, use database sessions, define expiry/refresh/revocation and encrypt sensitive provider tokens where used.
- Session/layout checks improve UX; every callable business command/query authorizes subject + action + resource + organization.
- Add social login, 2FA, passkeys or SSO only when the selected assurance profile requires them.

## PostgreSQL and Drizzle policy

- Drizzle schema is adapter/schema source; generated ORM types do not become public DTOs.
- Split schema/query adapters by module ownership while keeping one reviewed migration history.
- Declare tenant-scoped foreign keys/uniques, money checks, version fields and required indexes explicitly.
- Keep remote calls outside transactions; use bounded transactions and explicit concurrency handling.
- Development uses `generate` to create reviewable SQL migrations; release uses `migrate` to apply pending history.
- Direct push/reset is limited to guarded disposable local environments.
- Use a deployment-appropriate pooled connection endpoint and test real connection limits.

## Compatibility spikes before acceptance

The generated accepted profile must prove:

- install, strict typecheck, architecture check and production build;
- typed config fail-fast and server-only import guard;
- Better Auth handler, session lookup, revoke path and application membership authorization;
- Drizzle connection, reviewed migration, rollback/roll-forward decision and transaction;
- one Server Component query and one hydrated interactive query without unintended duplicate fetch;
- one signed upload flow with ownership and a local/sandbox object store;
- one durable worker job through BullMQ with duplicate/crash/retry evidence;
- one email delivery through Mailpit/sandbox and safe retry state;
- one correlated trace/log across entrypoint -> application -> adapter -> worker/provider;
- unit, PostgreSQL integration, component accessibility and critical Playwright journey.

Any failed blocking spike changes the accepted stack profile; it is not deferred to feature implementation.

## Replacement seams

Keep `PaymentGateway`, `FileStore`, `NotificationSender`, `EventTransport`, `JobScheduler`, `Cache`, `RateLimiter`, `Telemetry` and `IdentityProvider` behind owned ports/adapters. Add `CarrierGateway` only when `CAP-CARRIER-PROVIDER` is selected. Replacing one provider must not change domain policy or public DTOs.

## Stop conditions

Stop when the chosen host cannot run the worker/connection model, shadcn source becomes feature-agnostic dumping ground, TanStack duplicates server reads, Better Auth becomes business authorization, Drizzle types escape module adapters, migration runs on every request/startup, Redis eviction can lose jobs, or exact APIs are copied without current primary verification.
