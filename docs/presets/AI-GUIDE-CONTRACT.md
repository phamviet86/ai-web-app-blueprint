# Preset agent-skill contract

Every preset ships a compact operating system for turning user outcomes into code that follows that preset's live patterns. The root [`AGENTS.md`](../../AGENTS.md) discovers the selected preset, then its analyzer routes work to namespaced skill packages.

This contract follows [`11-preset-agent-skills-and-design-evidence.md`](../blueprint/reference-app-blueprint/11-preset-agent-skills-and-design-evidence.md). It defines future skill packages; it does not install a skill or create a preset.

## Canonical skills

| Capability | Skill name | Responsibility |
| --- | --- | --- |
| Analyze | `<preset-id>-analyze-request` | Translate an outcome into ordered tasks and the smallest skill sequence |
| Library | `<preset-id>-lib` | Change schemas, database/auth/API adapters, configuration, and stack mechanisms |
| Shared | `<preset-id>-shared` | Change reusable interaction mechanics without absorbing feature vocabulary |
| Feature | `<preset-id>-feature` | Change business contracts, policy, service, repository, presentation, and tests |
| App | `<preset-id>-app` | Change routes, layouts, providers, metadata, and composition |
| New pattern | `<preset-id>-new-pattern` | Add a missing reusable pattern through the blueprint escape hatch |
| UI | `<preset-id>-ui` | Design or change UI/UX while preserving preset data, action, state, and accessibility contracts |

The folder name, manifest name, and frontmatter `name` must match. Keep `preset_id` at 47 characters or fewer so the longest canonical name remains below the 64-character skill-name limit. Namespace names prevent two selected preset versions or unrelated global skills from colliding.

## `SKILL.md` contract

Frontmatter contains **exactly** `name` and `description`:

```yaml
---
name: <preset-id>-feature
description: Add or modify feature-owned behavior in <preset-id>, including public schemas, authorization policy, services, repositories, feature UI configuration, and feature tests. Use when the request adds a business capability, changes a use case or resource rule, alters persistence mapping, or changes a feature-specific screen or action.
---
```

`description` is the trigger surface. It must say what the skill does and list concrete requests or contexts that should activate it. Do not hide trigger rules in a body section that is unavailable before activation. Avoid broad claims such as “use for coding.”

Keep the body imperative and concise. Use the exact operational headings `Inputs`, `Workflow`, `Completion criteria`, `Verification`, and `Stop conditions`; additional headings may clarify capability-specific constraints without replacing them. Limit the content to:

1. the outcome and authority boundary;
2. inputs to inspect and prerequisite classification;
3. ordered workflow with explicit decision points;
4. path and ownership constraints;
5. conditional reads or scripts;
6. checkable **Done when** conditions under `Completion criteria`;
7. stop/escalation conditions.

Give the agent freedom where several implementations satisfy the contract. Use:

- high freedom for feature decomposition, naming within preset conventions, and UI composition;
- medium freedom for pattern selection with exemplars and contract checks;
- low freedom for migrations, generated files, integrity checks, and fragile mechanical operations, preferably through deterministic scripts.

Do not prescribe keystrokes or reproduce facts an agent can infer from local code. Guard boundaries and observable outcomes instead.

## Progressive disclosure and prerequisites

Load only what the task needs:

- `SKILL.md`: core procedure and routing;
- `references/`: pattern catalog excerpts, contracts, API/source records, or extended examples read conditionally;
- `scripts/`: deterministic validation, generation, migration, or integrity operations; invoke the declared interpreter explicitly rather than relying on executable mode, and execute without loading source unless inspection is necessary;
- `assets/`: templates or output resources copied or adapted, not documentation.
- `agents/openai.yaml`: Codex-facing display metadata and a default prompt that explicitly invokes the namespaced skill; derive it from, and never let it contradict, `SKILL.md`.

Link every resource directly from `SKILL.md` and state exactly when to read or run it. Keep references one level deep and avoid duplicating content between the body and resources.

Classify prerequisites:

- **hard**: absence makes safe execution impossible; stop with the missing item and recovery action;
- **quality**: improves confidence or polish; use the declared fallback, record the omission, and reduce claims rather than blocking unrelated work.

Official documentation for the pinned framework/library API is hard whenever the task depends on that API. Context7 is the preferred retrieval path when available; if unavailable, use the preset's pinned official snapshot or fetch official docs directly and record the fallback. A pinned `ui-ux-pro-max` snapshot is optional, read-only design advice and therefore a quality prerequisite unless the preset explicitly makes a licensed asset mandatory.

## Analyzer as router

`<preset-id>-analyze-request` must run for ambiguous, cross-layer, or outcome-level requests. It classifies by semantic ownership and dependency order, not keyword matching. It outputs:

- acceptance behavior and affected capability;
- matching catalog pattern and evidence, or a proven gap;
- ordered tasks with one owning skill per task;
- changed public payload/result, data, auth, or UI contract;
- hard and quality prerequisites with fallbacks;
- verification, dual-review, and documentation/evidence deltas;
- only the unknowns that require a product, risk, destructive, or stack decision.

The analyzer routes; it does not become an implementation mega-skill. For example, a searchable table normally routes feature query policy/repository work before shared mechanics, UI composition, and thin app routing.

## Checkable completion

Every skill defines concrete **Done when** checks under `Completion criteria`. At minimum they cover:

- allowed files changed and ownership boundaries preserved;
- declared payloads/results/states still compose across affected layers;
- deterministic format, type, architecture, contract, and focused behavior checks pass;
- relevant positive fixture passes and negative fixture fails for the intended reason;
- loading, empty, error, stale/success, denied, accessibility, and responsive states are addressed where applicable;
- pattern catalog, design evidence, source record, ADR, or preset lock is updated when its contract changed;
- no success claim exceeds available evidence.

“Code written,” “looks good,” and a generic build pass are not sufficient completion criteria.

## Pattern proof and two reviews

Each reusable pattern has:

- a catalog record defining ownership, intent, applicability, public contract, and verifier;
- a minimal positive exemplar;
- a deterministic conformance verifier;
- positive fixtures that must pass;
- negative fixtures for forbidden ownership, dependency, payload, or state shapes that must fail.

Keep two reviews separate:

1. **Pattern-conformance review** asks whether the change follows the preset's boundaries, exemplar semantics, contracts, and verifiers.
2. **User-outcome review** asks whether the requested behavior, UX, accessibility, error recovery, and acceptance examples work.

Passing either review never implies the other. Store distinct results and link both from verification evidence.

## Forward evaluation

Before `candidate`, run every canonical skill in clean, minimally primed contexts on representative and adversarial requests. The evaluating agent receives the selected skill, raw task artifacts, and normal repository authority—not the expected patch or suspected failure. Record:

- case ID and untouched input;
- preset, skill, model/toolchain, and source/integrity digests;
- emitted patch or artifacts and command logs;
- conformance and outcome results separately;
- observed failure and the smallest skill/resource correction.

Re-run affected cases after skill, pattern, framework, source, or verifier changes. Do not promote evidence produced against a different digest.

## UI and source discipline

`<preset-id>-ui` starts from the preset UI design contract and the feature's typed payload/action/state contracts. Its exploration sequence is:

1. optionally use a commit-pinned, license-reviewed, read-only `ui-ux-pro-max` snapshot to generate design candidates;
2. validate every implementation-dependent candidate against exact-version official UI framework/API documentation, retrieved through Context7 when available;
3. select and adapt only candidates that also compose with the preset's pinned pattern exemplars and design evidence.

Exploration order does not change authority: official APIs, blueprint boundaries, user requirements, preset contracts, accessibility, and measured evidence outrank advisory output. Advisory material may improve hierarchy, typography, color, layout, interaction, responsive behavior, and accessibility checks; never execute its scripts merely because they exist.

Record each source in the locked ledger with URL, requested ref, resolved immutable revision, retrieval time, license, claims used, and invalidation triggers. Context7 records also include library ID, concept-scoped queries, and official URLs; UX advisory records declare `acquisition_mode: read-only`. Lock the ledger through `sources.sha256` and mark dependent evidence stale when an invalidation trigger fires.

Each skill's `sha256` locks its complete skill directory, including `SKILL.md`, `agents/`, `references/`, `scripts/`, and `assets/`. Compute `preset-skill-tree-v1` by starting one SHA-256 stream with the ASCII bytes `preset-skill-tree-v1` plus NUL, sorting regular files by POSIX-relative path, then appending for each file: the path's unsigned 8-byte big-endian length, UTF-8 path bytes, content's unsigned 8-byte big-endian length, and raw content bytes. Reject symbolic links. A changed resource therefore invalidates the skill and its forward-eval evidence even when `SKILL.md` is unchanged.

## New-pattern escape hatch

`<preset-id>-new-pattern` must require the agent to search live code, the locked catalog, and exemplars before proving a gap; read only the exact blueprint owner; implement the smallest local closed flow; add catalog, exemplar, verifier, and positive/negative fixtures if reusable; run both reviews; and add an ADR for consequential public or cross-layer changes.

It must keep one-off product behavior feature-local and stop for a new product/risk decision, destructive conflict, license uncertainty, or materially different stack. It must not use “new pattern” to bypass a failed existing pattern.
