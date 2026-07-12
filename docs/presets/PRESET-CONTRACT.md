# Preset package contract

A preset is a coherent, executable reference implementation for one exact stack combination. It is not a bag of snippets and not a claim that every supported library combination composes safely.

## Required outputs

Every `docs/presets/<preset-id>` contains:

- a human README with purpose, fit/non-fit, quick start, exact versions, and lifecycle;
- `preset.yaml`, the machine-readable manifest;
- a complete `template/` containing framework-default root files and application source;
- the six canonical AI guides defined in [`AI-GUIDE-CONTRACT.md`](AI-GUIDE-CONTRACT.md);
- deterministic verification commands, fixtures, and evidence descriptions;
- at least one removable vertical walking slice that proves the declared layer contracts.

## Manifest minimum

`preset.yaml` must declare, at minimum:

```yaml
preset_id: next-ts-example
preset_version: 0.1.0
blueprint_version: 0.10.0
blueprint_revision: <immutable revision>
status: experimental
archetype: full-stack-web
stack: []                 # exact package/runtime versions and provenance
capabilities: []          # provided/verified/conditional/unsupported + evidence
verified_flows: []        # read/write/auth and optional capability slices
root_files: []            # source, target, operation, conflict policy
source_paths: []
guides: []
verification_commands: []
compatibility: []
upgrade_policy: {}
```

The illustrative ID above is not an available preset. Schema validation should be introduced with the first actual preset so it is tested against a real package rather than a speculative manifest.

## Capability and inter-layer matrix

Each capability is one of `provided`, `verified`, `conditional`, or `unsupported`. Only `verified` means an exact-version closed flow passed. Every row records provider, consumer, public payload/result, failures/states, constraints, and evidence.

The baseline closed flows are:

```text
read surface -> validated query request -> feature query policy -> repository -> ORM/database
             <- page/range result       <- mapped safe result    <-

form/input -> normalized values -> action -> service/transaction -> repository
           <- form adapter      <- typed action result            <-

session adapter -> trusted subject -> route/action guard -> feature resource policy
                                                   -> mandatory repository scope
```

Browser inputs never become raw ORM filters. `lib/db` may supply parsing, pagination, operator mechanics, transactions, and adapter primitives; each feature owns public aliases, allowed fields/operators/sorts/joins/projections, tenant/resource scope, and cost/index constraints.

## Shared UI baseline

A full-stack web preset must declare support or non-support for:

- tokens/primitives and app/page layout;
- async feedback and standard action states;
- normalized form fields and input adapters;
- table and list surfaces;
- search/filter/sort/pagination/range toolbars;
- detail, form, and confirm overlays;
- actions and menus;
- remote list/detail/options/form/mutation adapters.

Calendar, masonry, transfer, upload, editor, and similar surfaces are capability-selected. Every supported surface declares the request it emits, result it consumes, loading/empty/error/stale/denied states, accessibility, responsive behavior, and feature-owned configuration boundary.

Normalization covers absent/null/empty semantics, dates/time/timezone, numbers/currency, single/multi options, files, field errors, and action results. Feature fields, columns, labels, permissions, filters, and actions remain feature-owned.

## Feature compatibility contract

The preset maps semantic roles to concrete paths. A typical feature needs public contracts, schemas, client orchestration, server actions/queries, application services, repositories, policies, and views; empty folders are not required. The mapping must prove:

- presentation consumes only public/feature contracts;
- actions validate untrusted data and establish trusted context;
- services own use-case sequencing and transaction intent;
- repositories own persistence mapping and mandatory data scope;
- UI adapters translate typed results into focus, feedback, close/reset, invalidation, and refetch behavior;
- `app` remains composition, not a second feature layer.

## Materialization

Each template entry declares `create`, `merge`, or `replace` and a conflict policy. Instantiation must:

1. confirm preset fit and exact toolchain prerequisites;
2. inventory target conflicts before writes;
3. create framework root files and `src/` at their prescribed paths;
4. install the locked dependencies;
5. write the preset lock and local decisions;
6. run clean-room build, architecture, and walking-slice verification;
7. leave a failed install diagnosable and resumable without falsely recording success.

Preset examples may demonstrate behavior, but sample business entities must be removable without dismantling shared/platform foundations.
