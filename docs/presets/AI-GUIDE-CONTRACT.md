# Preset AI guide contract

Every preset ships a small operating system that turns a user's outcome into code changes consistent with that preset. The root [`AGENTS.md`](../../AGENTS.md) routes into it after the app is instantiated.

## Required guide set

| File | Owns |
| --- | --- |
| `guides/analyze-request.md` | Convert the request into ordered tasks and select the smallest relevant guide set |
| `guides/lib.md` | Add/modify schemas, data/auth adapters, configuration, and other stack mechanisms |
| `guides/shared.md` | Add/modify reusable UI, hooks, input/form, feedback, and remote interaction mechanics |
| `guides/feature.md` | Add/modify business capability contracts, service, repository, policy, presentation, and tests |
| `guides/app.md` | Add/modify routes, layouts, providers, metadata, and composition |
| `guides/new-pattern.md` | Resolve a capability not covered by an existing preset pattern without bypassing the blueprint |

Each guide declares preset/version applicability, `read_when`, required reads, allowed paths, owned decisions, prohibited ownership, ordered steps, verification, documentation/evidence delta, and stop/escalation conditions.

## Request analysis

`analyze-request.md` must classify outcomes by semantic ownership, not keywords alone. One request may create ordered tasks across layers; for example, a new searchable table can require feature query policy/repository work, shared mechanics only if a reusable capability is missing, then thin app composition.

The output must state:

- user outcome and acceptance behavior;
- affected capability and existing pattern found;
- task order and guide for each task;
- public payload/result or data/auth contract changed;
- verification and likely docs/evidence delta;
- unknowns that genuinely require a human decision.

## New-pattern protocol

`new-pattern.md` must require the agent to:

1. search preset docs and live code for an existing compatible pattern;
2. prove the capability gap rather than treating preference as novelty;
3. read the exact source-of-truth owner under `docs/blueprint`;
4. design the smallest preset-compatible contract and one closed walking slice;
5. add boundary/fitness verification;
6. update the preset catalog and affected guides when the pattern is reusable;
7. add an ADR for a consequential public or cross-layer contract;
8. keep one-off product behavior local to its feature.

An AI agent may propose a new pattern, but it may not silently change risk acceptance, stack identity, or destructive migration policy.
