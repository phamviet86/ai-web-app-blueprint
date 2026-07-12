---
guide_id: REFAPP-SHARED
title: Shared Foundation Inventory
status: experimental
audience: human-and-ai
read_when:
  - Planning reusable kernel, UI, hooks, formatting, testing, or accessibility foundations for the reference app.
skip_when:
  - Implementing feature policy or platform I/O.
depends_on:
  - README.md
  - ../03-shared-kernel-and-platform.md
owns:
  - reference-app shared inventory and acceptance examples
  - mapping from shared roles to showcase consumers
  - preset shared-surface, input-normalization, and interaction contracts
---

# Shared foundation inventory

> Build only stable semantics used by real slices. Shared code renders or transforms resolved contracts; it never selects business policy or performs module I/O.

The inventory is a menu, not a tier requirement. A small `BASIC_WEB` slice may need only error/result semantics, one accessible form/list shell and deterministic test helpers; omit money, organization, file, chart, query hydration or async helpers until selected capabilities create real consumers.

## Rule `REF-SHARED-INVENTORY-01`: every shared item has consumers and a boundary

For each item record purpose, owner, first two real consumers, variability, accessibility/test contract and removal/merge trigger. Do not build the full inventory before the first walking slice.

## Suggested logical structure

```text
shared/
├── kernel/       pure cross-module primitives
├── ui/           accessible presentation primitives and semantic compositions
├── hooks/        browser-only generic interaction helpers
├── formatting/   locale-aware pure presentation functions
└── testing/      deterministic factories, clocks, IDs and render/test harnesses
```

A stack profile may map these roles to `components`, `lib`, packages or another tree. Preserve dependency direction.

## Shared kernel

Start small:

| Contract | Purpose | Must not contain |
| --- | --- | --- |
| `Result<T, AppError>` | Stable expected success/failure discrimination | HTTP statuses, localized copy, raw causes |
| `AppError` categories | Validation, auth, absence, conflict, domain, rate and dependency semantics | Vendor/database messages |
| `RequestContext` | Selected trusted subject, optional tenant, correlation and locale references | Client-asserted authority or a mandatory organization field when tenancy is not selected |
| `Page<T>` and page metadata | Stable bounded pagination result | ORM cursors/rows |
| `Money` representation | Minor amount + currency with pure arithmetic guards | Formatting or exchange-rate I/O |
| `Clock`/`IdGenerator` ports | Deterministic application inputs | Global mutable clock/ID state |

Keep organization, order, inventory, payment and shipment vocabulary inside their modules.

## Shared UI capability set

Build these only as they gain consumers:

| UI contract | Shared responsibility | Feature responsibility |
| --- | --- | --- |
| Application shell/navigation | Responsive landmarks, skip link, focus, mobile/desktop shell | Visible destinations and allowed actions |
| Page header/toolbar | Layout, breadcrumbs slot, action slots | Titles, labels and commands |
| Form field/shell | Labels, description/error association, layout, submit state | Schema, fields, business validation and mutation |
| Data table/list | Accessible table/list, sorting/filter/paging controls and state plumbing | Columns, allowed fields/operators, query key and row actions |
| Async state | Loading, empty, error, retry and stale/degraded presentation | Error message, retry policy and business empty meaning |
| Dialog/drawer/confirm | Focus trap, dismissal and destructive confirmation semantics | Authorization and command selection |
| Status badge | Tokenized visual variants with text/icon support | Mapping business states to resolved variants |
| File picker/progress | Accessible selection, progress/cancel shell | Content rules, ownership and upload command |
| Toast/notice | Announcement region and severity presentation | Safe localized message and deduplication key |
| Chart/card primitives | Responsive/accessibility and formatting slots | Metric definition, query, freshness and thresholds |

Wrappers must add semantics, accessibility, consistency or a stable product contract—not rename the underlying design-system props.

## Rule `REF-SHARED-SURFACE-CONTRACT-01`: preset UI capabilities declare both ends

An `AUTHOR_PRESET` classifies each shared capability as `provided`, `verified`, `conditional`, or `unsupported` in [preset-contract](templates/preset-contract.md). Its baseline covers only real archetype needs, but must address these categories explicitly:

| Category | Minimum preset decision |
| --- | --- |
| Tokens/primitives | Theme, typography, button/action, icon and status semantics |
| App/page layout | Application shell, page header, section/grid and responsive/focus landmarks |
| Feedback | Loading/skeleton, empty, validation/error, stale/degraded and notice behavior |
| Form/input | Field association, normalized values, submit lifecycle and server field errors |
| Data surfaces | At least one verified table or list; classify masonry, calendar and transfer/picker separately |
| Toolbar | Search, filter, sort, pagination/range, refresh and visible active-state/reset behavior |
| Overlay/action | Detail/form dialog or drawer, confirmation and action/menu pending/disabled behavior |
| Remote lifecycle | List, detail, options, form and mutation adapters selected by the stack |

Every provided data surface declares the canonical request parts it emits, result shape it consumes, controlled/uncontrolled state boundary, reset/canonicalization behavior, loading/empty/error/stale/degraded states, keyboard/focus/responsive behavior and feature-owned configuration. Shared code owns mechanics; features own columns/cards/events, field aliases/operators, labels, permissions, query keys, invalidation policy and business actions.

Implement each preset natively for its UI system. Do not create a lowest-common-denominator wrapper merely to make shadcn, Ant Design or another system look identical.

## Design contract and evidence before shared UI code

Before a preset labels a UI capability `provided`, record a design brief with product type, users/top tasks, information hierarchy, content/data density, brand and locale constraints, supported input/device modes, accessibility target, responsive breakpoints and performance budget. An optional pinned design-intelligence source may suggest candidates; the selected result still needs product rationale and framework/API proof under guide [11](11-preset-agent-skills-and-design-evidence.md).

Use three token roles and map each through the selected framework's native theme contract:

| Token role | Owns | Evidence |
| --- | --- | --- |
| Primitive | Raw color, type, spacing, radius, elevation, opacity and motion scales | Value inventory, contrast/motion checks and theme inputs |
| Semantic | Surface, text, border, focus, action, status, density and responsive meaning | Light/dark/high-contrast mappings and usage rules |
| Component/state | Framework-native component slots, sizes, variants and state overrides | Rendered representative states and API compatibility |

Every interactive component maps default, hover, focus-visible, active, disabled, loading and invalid states where applicable. Every remote surface additionally maps empty, error, stale/degraded, denied and success. Forms preserve normalized values and field errors on failure, announce a safe action result, restore/focus the correct target, close or navigate only on success and let the feature own invalidation. Tables, lists and calendars show how their request controls, result metadata and row/event actions behave at narrow and wide widths.

Acceptance evidence includes objective accessibility/component checks, representative viewport/state captures and at least one real feature walking slice. A component gallery can document tokens and variants but cannot prove payload, action-result, auth or remote-state integration.

## Standard input and form normalization

Each preset records one value contract reused deliberately across forms, toolbar filters and inline controls:

| Value family | Decisions that must be explicit |
| --- | --- |
| Text/IDs/options | Trim/normalization, option `{label,value}` equivalent, single/multi and clear semantics |
| Number/currency | Display parsing versus canonical numeric/minor-unit value and invalid/empty behavior |
| Boolean/choice | Missing versus false, checkbox/radio semantics and disabled/read-only behavior |
| Date/time/range | Canonical instant/business date, timezone, inclusive/exclusive range and serialization |
| File/rich input | Client preview value versus validated server/storage contract |

Distinguish `undefined`, `null`, empty text and explicit deletion. The client normalizes ergonomics; the feature boundary revalidates authority and business rules. A field descriptor may serve form and filter modes only when those modes have intentionally compatible semantics.

The standard mutation path is resolved input -> normalized values -> feature schema/action -> service/repository -> stable result -> form adapter. The result distinguishes field validation, authorization, conflict, domain, dependency and unexpected failure so shared presentation can focus the first invalid field, keep values, announce safe feedback, close only on success and invalidate/refetch only by feature policy.

## Browser hooks

Allowed generic hooks include:

- debounced input and stable previous value;
- media query and reduced-motion preference;
- focus restoration and disclosure state;
- local column/view preference under an explicit namespace;
- cancellable upload UI state;
- query-client creation/hydration utilities selected by the stack profile.

Module query keys, server calls, permissions, option loading, optimistic policy and mutation invalidation remain module-owned.

## Formatting and localization

Provide pure formatters for date/time, number, percent, money, file size and safe fallback text. The app profile records locale/timezone/currency policy. Formatting never changes stored values or performs business calculations.

User-facing copy stays in presentation/module localization resources. Error codes remain stable and language-neutral.

## Shared testing foundation

Provide:

- fixed/fake clock and deterministic ID factory;
- render harness with theme, locale, router and query providers;
- accessibility assertions and keyboard/focus helpers;
- synthetic data builders that are valid by default;
- controlled file, email, queue and telemetry fakes through ports;
- database fixture helpers owned by integration-test infrastructure, not UI components.

Do not create one mutable global test fixture shared across parallel tests.

## Promotion sequence

1. Build the first use inside a module.
2. Observe a second consumer with the same semantics.
3. Define the smaller shared contract.
4. Move only generic rendering/transformation.
5. Add independent accessibility/unit evidence.
6. Enforce that shared cannot import modules or platform I/O.

App-wide foundations such as theme tokens, application shell and error boundary may be shared from the start because their scope is inherently global.

## Acceptance evidence

- Shared import rules are mechanically enforced.
- Every exported item has at least one real consumer; promoted items have the required semantic justification.
- Shared UI works with resolved callbacks/data and no hidden module fetch.
- Keyboard, focus, labels, errors, responsive behavior and reduced motion are checked where applicable.
- Primitive/semantic/component tokens, design-brief decisions and representative states are linked to exact framework APIs and evidence.
- UI standards evidence and the real user-outcome result are recorded separately; neither substitutes for the other.
- Business states/permissions/messages remain in feature presentation.
- Unused generated design-system components are not treated as shared product APIs.

## Required output

Fill [templates/shared-plan.md](templates/shared-plan.md) as consumers emerge. A shared item is accepted only when its semantics, first two real consumers, allowed dependencies, accessibility/test evidence and removal/merge trigger are explicit.

## Stop conditions

Stop when a surface has no request/result counterpart, input empty/date semantics differ silently across form and filter use, shared code imports a module, fetches business data, owns query keys or authorization, converts all design-system primitives into wrappers, contains feature status maps, exposes platform clients, or is generated speculatively before real consumers exist.
