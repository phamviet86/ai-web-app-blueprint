---
guide_id: SKEL-PROFILE-NEXT-WEB
title: Next.js, Prisma/PostgreSQL, Ant Design Candidate Mapping
status: experimental
audience: human-and-ai
verified_on: 2026-07-12
builder_profile_id: BUILDER-NEXT-PRISMA-ANTD
profile_authority: candidate
provenance_status: incomplete
read_when:
  - Mapping the core blueprint to a Next.js App Router full-stack web application using this tool family.
skip_when:
  - The selected stack differs materially or only core architecture is being decided.
depends_on:
  - ../README.md
  - ../02-module-anatomy-and-public-contracts.md
  - ../10-runtime-accessibility-and-performance.md
owns:
  - concrete Next.js runtime and folder mapping
  - Ant Design and TanStack Query UI/runtime mapping
  - Prisma/PostgreSQL and Better Auth adapter mapping
  - same-stack verification source routing
  - reference-app builder selection guidance
---

# Next.js, Prisma/PostgreSQL, Ant Design candidate mapping

> This is a candidate implementation mapping, not a maintained compatibility profile or the architecture core. Its source snapshot has no repository revision or lockfile locator, so a project must re-resolve versions, primary documentation, and blocking compatibility paths before using it.

## Provenance gate

| Provenance field | Recorded value |
| --- | --- |
| Original source repository locator | Unavailable in this package |
| Source revision | Unavailable in this package |
| Lockfile path and digest | Unavailable in this package |
| Documentation/API mapping check | Dated `verified_on` above; this checks the written mapping, not the reported package set |
| Authority | Candidate input only; cannot directly produce an `accepted` `STACK-*` artifact |

The missing source identity makes the reported version set non-reproducible. Before selection, record the real project revision/lockfile, resolve primary version-aware documentation, and pass the stack template's compatibility spikes. Until that evidence exists, cite this file as `candidate mapping`, never as compatibility proof.

## Reference-app builder fit

The [reference-app builder](../reference-app-blueprint/README.md) may use this as the source mapping for a project-local `STACK-*` artifact. It fits all capability tiers when TypeScript/Node, App Router and Ant Design are deliberate product/team choices; the tier still decides which mechanisms exist.

| Tier/need | Mapping posture |
| --- | --- |
| `BASIC_WEB` | Prefer Server Components and direct server queries; omit TanStack Query, worker, cache, files and external providers unless a selected capability needs them |
| `MULTI_TENANT_SAAS` | Add Better Auth session mechanics plus application-owned membership/resource authorization; never treat provider organization data as the business authority |
| `ASYNC_INTEGRATION` | Add a separately operable worker/transport only after deployment compatibility is proven; Route Handlers remain protocol adapters |
| `REGULATED` | Strengthen assurance, audit, privacy, secret and recovery evidence through parent guides; Ant Design/Next.js do not supply those controls automatically |
| `FULL_SHOWCASE` | Map the complete selected FulfillOps catalog, still keeping optional providers/cache conditional |

Record `Candidate mapping: ../profiles/nextjs-prisma-antd.md`, the project-local provenance, and every deviation in the generated `STACK-*`. This file can seed investigation but is not acceptance evidence.

## Reported capability snapshot

The unavailable source snapshot was reported to contain:

| Capability | Verified implementation snapshot |
| --- | --- |
| Full-stack/runtime | Next.js `16.2.7` App Router, React `19.2.4` |
| Language | JavaScript modules in the source repo; strict TypeScript recommended for greenfield |
| Enterprise UI | Ant Design `6.5.0`, Pro Components, Ant Design SSR registry/style tooling |
| Client server-state | TanStack Query `5.101.0` when interactive lifecycle is needed |
| Validation | Zod `4.4.3` |
| Data | PostgreSQL via Prisma/Prisma Client `7.8.0`; serverless driver adapter in the source profile |
| Identity | Better Auth `1.6.20` for authentication/session primitives |
| Telemetry | Next.js instrumentation hooks plus a vendor-neutral OpenTelemetry path |

These versions are historical context, not reproducible compatibility evidence, a minimum, or a recommendation. Resolve a mutually compatible current set and record the project revision, lockfile locator/digest, primary sources, and spike results in the new repo's profile.

## Recommended greenfield mapping

```text
src/
├── app/                         Next entrypoints and top-level composition
│   ├── layout.tsx
│   ├── providers.tsx
│   ├── (routes)/.../page.tsx
│   └── api/.../route.ts
├── modules/<module>/
│   ├── public/
│   │   ├── shared.ts            serializable DTOs/schemas/types safe in either graph
│   │   ├── server.ts            server-only in-process commands and queries
│   │   └── client/              surfaces allowed to browser-side importers
│   │       ├── actions.ts       `use server`; async browser-callable actions only
│   │       └── browser.ts       client-safe keys/helpers with no server import
│   ├── application/             commands, queries, owned ports
│   ├── domain/                  optional pure invariants/state machine
│   ├── adapters/                Prisma/vendor/event implementations
│   ├── presentation/
│   │   ├── server/              Server Components/read composition
│   │   └── client/              focused interactive islands/hooks/config
│   └── compose.ts               module factory/wiring
├── platform/
│   ├── config/
│   ├── auth/
│   ├── database/
│   ├── telemetry/
│   ├── messaging/
│   └── runtime-clients/         protocol-neutral connection/client mechanics only
└── shared/
    ├── kernel/                  tiny pure stable primitives
    └── ui/                      reusable semantic UI contracts
```

An existing repo may keep `features`, `lib`, `views`, `hooks`, and `server` names. Refactor dependency direction and public contracts first; renaming folders is not architectural progress by itself.

For greenfield, enable strict TypeScript, no unchecked framework/ORM types at public boundaries, and runtime validation for untrusted input. Brownfield JavaScript may migrate module-by-module with checked JS/typed boundaries rather than a big-bang conversion.

Keep the three public entrypoints separate:

- `public/shared` exports serializable values and type/schema contracts with no server implementation import;
- `public/server` is marked server-only and is used by Server Components, Route Handlers, composition roots, and other in-process modules;
- `public/client/actions` exports only async Server Actions; `public/client/browser` contains client-safe keys/helpers and imports no server implementation.

`client` names the allowed importer, not one shared execution runtime: an action file still has the required server directive, while a browser helper stays client-safe. Do not combine them or re-export shared/server/client surfaces through one barrel. Package exports/import-boundary checks should prevent a Client Component from reaching `public/server` or module adapters.

Platform may initialize protocol-neutral database, queue, HTTP, telemetry, or credential clients. A vendor capability adapter and every business integration policy remain under the owning module's `adapters`; `platform` must not expose another business module as an integration service.

## Rule `PROFILE-NEXT-RUNTIME-01`: map App Router boundaries deliberately

- `page.tsx`/`layout.tsx` are thin composition/route entrypoints and Server Components by framework default.
- Server presentation calls an explicit query through the module's `public/server` entrypoint; do not call an internal Route Handler merely to read server data.
- Use small Client Components for state/effects/events/browser-only dependencies.
- Props crossing Server-to-Client must be serializable; internal Server Component data need not be forced into a transport envelope.
- Server Actions are browser-callable entrypoints exported through `public/client/actions`: parse input, derive trusted context, authorize, call one application contract, and map the result.
- Route Handlers own external HTTP/webhook protocol mapping, not business transactions.
- Mark database/auth/vendor implementation as server-only and enforce the separate shared/server/client public entrypoints; do not add a combined public barrel.
- Use native `loading`, `error`, and `not-found` boundaries only where segment-level behavior is useful.

Current Next.js 16 guidance confirms Server Components should fetch directly from the source rather than use internal Route Handlers, and only Client-bound props require serialization.

## TanStack Query mapping

Use TanStack Query only for browser server-state needing refetch, mutation, polling, optimistic, or cache lifecycle.

Choose one initial path:

1. server-only render with no equivalent client refetch; or
2. server `prefetchQuery` -> `dehydrate` -> `HydrationBoundary` -> client `useQuery` using the same query options/key/freshness contract.

For SSR hydration, use a per-request server QueryClient and a stable browser QueryClient; set a domain-appropriate nonzero `staleTime` when immediate mount refetch would duplicate work. Mutation success invalidates only affected keys. Pass the provided cancellation signal to supported fetch clients.

## Rule `PROFILE-ANTD-UI-01`: Ant Design implements shared UI, not business ownership

- Configure locale/theme/SSR registry at the narrowest app-wide provider boundary.
- Prefer native components, composition, semantic `classNames`/`styles`, and tokens before wrappers/custom CSS.
- Shared wrappers add stable semantics such as form layout, currency/date/nullability, request payload, or accessibility—not renamed props.
- Feature/module presentation owns columns, fields, options, labels, permissions, and action composition.
- Use semantic HTML/keyboard/focus behavior and verify WCAG targets from core guide `10`.
- For Ant Design `6.5.0`, `Table virtual` requires numeric `scroll.x` and `scroll.y`; custom body wrappers/rows preserve the ref contract.
- Virtualization is a measured choice after pagination/progressive rendering, not a default table mode.

Resolve exact APIs through the Ant Design CLI (`info`, `demo`, `doc`, `semantic`, `token`) for the selected version before writing code.

## Rule `PROFILE-PRISMA-DATA-01`: Prisma is an adapter, not the module API

- Application-owned repository/query ports expose domain/application types.
- Prisma adapters own `select`, `where`, mapping, transaction-client use, and database error translation.
- Public DTOs and domain models do not re-export generated Prisma types.
- Use narrow projections, relation batching/join strategies, stable pagination, measured indexes, and execution plans under guide `09`.
- Keep a bounded interactive transaction; never call a remote vendor while holding it unless the consistency design explicitly requires it.
- Use isolation/retry policy for known write conflicts and optimistic version checks for concurrent updates when appropriate.
- Development creates reviewed migrations; production uses deployment-safe pending-migration commands, never development reset/push workflows.
- Schema changes follow expand -> backfill -> switch -> contract and application/schema compatibility from guides `12` and `16`.
- Connection/client lifetime follows the deployment runtime and selected driver/pool guidance.

## Identity mapping

Better Auth (or replacement) belongs under platform identity infrastructure:

- provider configuration, session/cookie verification, auth endpoint, and current-subject lookup;
- no business-resource authorization inside the provider adapter;
- application commands/queries authorize action + resource + tenant using trusted context;
- server layouts may redirect/filter navigation but never replace callable authorization;
- session expiry, revocation, reauthentication, recovery, and privileged-action assurance follow guide `11`.

## Configuration and telemetry mapping

- One typed server configuration module reads environment, validates at startup, and exposes sanitized capability-specific config.
- Only explicitly public variables enter client bundles.
- `instrumentation.ts/js` registers server telemetry before application work; client instrumentation handles user navigation/web vitals when selected.
- Correlate entrypoint -> application -> adapter -> database/vendor spans and structured logs without recording secrets, tokens, raw request bodies, or unbounded IDs as metric labels.
- Flush/shutdown telemetry according to the deployment runtime; serverless/edge constraints may require platform-specific exporters.

For public web journeys, the current Core Web Vitals “good” thresholds are a useful initial profile: LCP at or below `2.5s`, INP at or below `200ms`, and CLS at or below `0.1`, assessed at the 75th percentile separately for mobile and desktop. Treat these as dated defaults from [web.dev](https://web.dev/articles/vitals), then add journey-specific server, bundle, query, capacity, and cost budgets from core guide `10`.

## Portable qualification mapping

| Core contract | Mapping required from an accepted project profile |
| --- | --- |
| Concrete authority | Use either the exact preset lock or a validated app profile that binds the accepted stack artifact, pattern/skill registries, command registry, dual-verdict evaluations and current digests; source folders alone grant no authority |
| Vertical task routing | The accepted skill/pattern registry maps one outcome to one primary feature/interaction owner and any platform, shared, UI or composition support tasks; the analyzer applies the core task-time evidence tiers, `TASK_REROUTED` disposition and two verdict axes without inventing layer-shaped patterns |
| Command lanes | Map `install`, `doctor`, `test`, `check`, `build` and a bounded production-artifact `start-smoke` to exact lockfile-compatible commands; run selected generation, database, auth and browser lanes in clean room rather than inferring them from package metadata or touching production |
| Data access modes | Map `NONE`, bounded `LIVE_READ`, guarded `TEST_MUTATION` and `PRODUCTION_HANDOFF` to explicit Prisma/PostgreSQL tools and authority; every test mutation wrapper rechecks the disposable target before opening a client |
| Boundary values | Prove meaningful `false`, `null`, zero and omission behavior, actual persisted identifier shapes, named timezone/default handling and import paths that do not eagerly require runtime-only secrets or clients |
| Public query/UI contract | Bind validated feature intent to allowed read operations and prove the exact server/client wire shape plus loading, empty, error, stale, denied, success, focus, responsive and pending/double-submit behavior |
| Schema history and external effects | Use the accepted stack migration mechanism for ordered integrity, clean replay, compatibility, postchecks and recovery; claim external intent before network I/O, finalize afterward and reconcile ambiguous outcomes without an unsafe ordinary retry |
| Fitness evidence | Add negative import/runtime/architecture fixtures, wire-shape contract checks, database concurrency cases and real interaction proof; lint/build or an unparsed/ignored file never supplies those claims |
| Operations and optional skills | Map alerts to an owned diagnostic/runbook, and give every live read, drill or production action an explicit data mode plus separate external-side-effect, interface, approval, postcheck and recovery boundaries. If the project declares audit or publish skills, bind exact revisions and topology through project policy; this candidate profile does not prescribe direct-main, worktree or remote behavior |

These rows demonstrate how the portable outcomes can map to this stack family. They do not upgrade this candidate mapping or transfer the Bingo LMS source profile's compatibility evidence.

## Same-stack verification routing

Before exact implementation:

1. read installed Next.js docs under `node_modules/next/dist/docs` or the matching official version;
2. resolve React, TanStack Query, Prisma, Better Auth, Zod, and telemetry docs through Context7/primary sources;
3. query Ant Design CLI for the selected version;
4. verify runtime/config/package versions from the actual lockfile;
5. run profile-appropriate format/lint/type/architecture/test/build checks;
6. escalate to browser/runtime/database/deploy evidence only for the changed risk.

## Profile stop conditions

Stop when a Next runtime boundary is guessed from a folder name, one barrel mixes server-only and client-importable modules, Prisma types escape as public contracts, Ant Design wrappers replace native semantics without value, client hydration duplicates initial reads, or exact API claims lack version-aware evidence.
