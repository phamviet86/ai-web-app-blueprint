---
guide_id: SKEL-RUNTIME-PERF
title: Runtime, Native UI, Accessibility, and Performance Budgets
status: experimental
audience: human-and-ai
read_when:
  - Choosing render/data runtime, client boundaries, caching, streaming, UI primitives, accessibility, or performance/capacity work.
skip_when:
  - The task changes no runtime, interaction, accessibility, bundle, network, compute, database, or cost behavior.
depends_on:
  - README.md
  - 01-foundations.md
  - 04-dependency-contracts-and-sync-flows.md
owns:
  - native-platform-first UI/runtime policy
  - server/client/rendering path selection
  - accessibility baseline
  - performance and capacity budgets
  - cache/waterfall and measurement gates
---

# Runtime, native UI, accessibility, and performance budgets

> Performance is an explicit quality contract. Optimize a measured critical journey without weakening correctness, accessibility, security, or operability.

## Rule `NATIVE-FIRST-01`: use platform capability before wrapping it

Prefer current documented framework, browser, language, UI-system, and data capabilities for routing, rendering, forms, tables, tokens, semantics, caching, and transport.

Create an abstraction only when it protects a durable application contract such as:

- accessibility/locale/currency/date/nullability semantics;
- server/client or trust isolation;
- stable request/error/interaction behavior;
- repeated application layout or domain-neutral workflow;
- replaceable port around a volatile external capability.

A wrapper that only renames props, hides useful native APIs, or prevents upgrades is debt. Verify exact APIs in the selected stack profile and primary docs.

## Rule `RUNTIME-PATH-01`: run work where its constraints are cheapest and safest

| Need | Default direction |
| --- | --- |
| Secrets, authorization, initial/read-heavy content | Server/loader/query boundary close to data |
| Browser interaction, device APIs, transient local state | Small client island/component |
| User mutation | Client/entrypoint -> guarded command -> application use case |
| Slow independent sections | Start work in parallel; stream progressively when supported and useful |
| Live state | Explicit subscription/polling lifecycle with load and disconnect limits |
| Large/long work | Bounded asynchronous job with progress/result contract |

Do not force every read through a client cache, every operation through HTTP inside the same process, or every component into one runtime graph. Values crossing a process/runtime boundary use explicit safe DTOs.

## Rule `RUNTIME-WATERFALL-01`: dependency order must be real

- Start independent reads before awaiting them serially.
- Preserve true dependencies; concurrency is not automatically correctness.
- Stream only sections whose independent completion improves the user journey.
- Prefetch likely work with the same query/cache contract that consumes it.
- Do not merge unrelated endpoints or overfetch simply to remove every waterfall.
- Inspect network/server/query timelines; component nesting does not prove execution order.

## Cache ownership

Every cache declares:

```text
data owner and source of truth
identity including authorization/tenant scope
freshness/staleness contract
invalidation/update trigger
failure and stale-read behavior
storage/lifetime/eviction/cost
privacy deletion propagation
```

Choose one initial client-data handoff: client-only fetch, or server prefetch/hydration using the same key/options/freshness contract. Do not independently fetch equivalent server and client contracts on mount.

## Rule `ACCESSIBILITY-BASELINE-01`: accessible behavior is a release contract

For user-facing web applications, use WCAG 2.2 AA as the default target unless the system profile sets a stricter or justified different requirement.

Require:

- semantic elements/names/relationships before ARIA patches;
- full keyboard operation, visible/non-obscured focus, logical order, and escape behavior;
- label, error, help, status, loading, empty, and success announcements;
- sufficient contrast, zoom/reflow, target size, reduced-motion support where relevant;
- text alternatives and non-color-only meaning;
- accessible authentication and no unnecessary cognitive/motor barrier;
- preservation of semantics when virtualizing, portal-rendering, dragging, or wrapping native UI.

Automated a11y checks catch a subset. Critical workflows require keyboard/screen-reader-oriented interaction evidence proportional to risk.

## Rule `PERF-BUDGET-01`: budgets belong to critical journeys

For each important journey, record:

- representative device/runtime, network/region, dataset, and authenticated state;
- field/user-centric responsiveness and visual stability targets;
- server/API p50/p95/p99 or task-duration targets;
- client bundle/chunk, request count/bytes, and hydration/interaction budget;
- database query count/time/rows and external dependency budget;
- memory/CPU/cold-start and per-request/job cost ceiling;
- measurement method, environment, owner, and regression threshold.

A global “fast” requirement is not actionable. Exact defaults belong in the stack/system profile and may evolve.

## Rule `PERF-CAPACITY-01`: latency without load shape is incomplete

Define expected and tested:

- steady and peak throughput/concurrency;
- dataset/cardinality and growth horizon;
- queue depth/lag, connection/thread/pool limits;
- saturation signal and safe headroom;
- autoscaling/cold-start behavior where applicable;
- rate-limit/backpressure/degraded-mode response;
- dependency quotas and cost at the capacity target.

Load tests use safe environments/data and test the bottleneck actually owned by the system. Do not generate unapproved load against production or third parties.

## UI performance decision

- Paginate or progressively reveal before rendering unbounded collections.
- Virtualize only measured large collections and preserve focus, semantics, stable keys, size assumptions, and imperative-ref requirements.
- Lazy-load heavy optional interactions when it improves measured initial behavior; verify the selected framework actually creates a separate chunk/runtime boundary.
- Keep render/config identities stable only where profiling shows meaningful churn; avoid blanket memoization.
- Separate draft/local interaction state from cached server state.
- Preserve loading/empty/error/retry feedback during optimization.

## Server and data performance

- Project only required application fields and relations.
- Eliminate per-row/N+1 work through bounded batch/join/query design.
- Align common filter/sort/join paths with measured indexes/query plans.
- Keep network calls outside database transactions unless consistency requires them.
- Bound fan-out and propagate deadlines/cancellation.
- Treat exact counts, deep offsets, substring search, aggregates, and duplicated read models as explicit costs under guide `09`.
- Optimize cost and resource saturation together with latency.

## Evidence matrix

| Claim | Minimum useful evidence |
| --- | --- |
| Smaller client payload | Production artifact/chunk/request comparison |
| Faster user journey | Same-condition field or representative lab timing and UX metrics |
| Removed waterfall | Before/after network/server trace |
| Faster rendering | Profiler trace at representative component/data size |
| Faster query | Query count, timing, rows/cardinality, and execution plan when relevant |
| Higher capacity | Load shape, saturation point, error/latency curve, and recovery |
| Better cache | Hit/refetch/staleness/invalidation evidence with correct security scope |
| Better accessibility | Automated scan plus relevant keyboard/assistive interaction evidence |

Record baseline, change, same-condition result, functional regression checks, and trade-off. A passing build is not performance evidence.

## Stop conditions

Stop when optimization expands trusted/client boundaries, duplicates cache ownership, hides authorization, drops accessibility semantics, relies on speculative memoization/materialization, lacks representative baseline, or improves latency by violating cost/reliability limits.
