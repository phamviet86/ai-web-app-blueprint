---
document_id: REFAPP-PRESET-SOURCE-PROVENANCE
title: Preset Skill and UI Source Provenance
status: experimental
audience: human-and-ai
read_when:
  - Reviewing the external evidence behind preset skill authoring or UI design-intelligence guidance.
  - Refreshing, replacing, or licensing either audited external source.
---

# Preset skill and UI source provenance

This is load-on-demand research evidence, not runtime authority and not an installation instruction. Findings were independently summarized on 2026-07-12; no third-party code, data, prompt text or assets are vendored into the blueprint.

## Authority and trust boundary

- User/product/risk decisions, the blueprint, the selected preset and observed evidence remain authoritative for architecture and behavior.
- Exact-version official framework/library documentation owns API facts; Context7 helps retrieve it.
- The repositories below are untrusted advisory inputs. Pinning makes review reproducible but does not make content safe or correct.
- Do not auto-install, globally install, source shell setup, or run repository scripts with credentials or ambient write access. Inspect a pinned tree read-only and use a disposable sandbox only when an explicitly approved test needs execution.
- Copying any code, data or asset requires a separate file-level license and attribution review. The blueprint adopts independently written process ideas only.

## `mattpocock/skills`

| Field | Recorded value |
| --- | --- |
| Repository | [`mattpocock/skills`](https://github.com/mattpocock/skills) |
| Audited commit | [`391a2701dd948f94f56a39f7533f8eea9a859c87`](https://github.com/mattpocock/skills/commit/391a2701dd948f94f56a39f7533f8eea9a859c87) |
| Commit time | `2026-07-10T13:14:59Z` |
| License | [MIT](https://github.com/mattpocock/skills/blob/391a2701dd948f94f56a39f7533f8eea9a859c87/LICENSE) |
| Primary files reviewed | [`writing-great-skills/SKILL.md`](https://github.com/mattpocock/skills/blob/391a2701dd948f94f56a39f7533f8eea9a859c87/skills/productivity/writing-great-skills/SKILL.md), its [glossary](https://github.com/mattpocock/skills/blob/391a2701dd948f94f56a39f7533f8eea9a859c87/skills/productivity/writing-great-skills/GLOSSARY.md), [`research/SKILL.md`](https://github.com/mattpocock/skills/blob/391a2701dd948f94f56a39f7533f8eea9a859c87/skills/engineering/research/SKILL.md), [`codebase-design/SKILL.md`](https://github.com/mattpocock/skills/blob/391a2701dd948f94f56a39f7533f8eea9a859c87/skills/engineering/codebase-design/SKILL.md) |

Independent findings adopted:

- Treat a skill as a process-predictability device: invocation and execution need explicit contracts even when outputs vary.
- Put distinct triggers in the model-visible description; use one router when users or agents should not memorize many separate entry points.
- Keep ordered work and must-have invariants in `SKILL.md`; place branch-specific reference behind a condition-bearing pointer.
- End work units with checkable, sufficiently exhaustive completion criteria so later steps do not encourage premature completion.
- Prefer primary sources and preserve one source of truth; prune duplicated, stale and behavior-neutral instruction text.
- Use a compact shared vocabulary for patterns and interfaces so the same terms connect prompts, catalog entries, skills and code.

Not adopted as authority:

- Repository-specific command conventions, invocation metadata, issue workflow and commit behavior are not portable preset rules.
- A third-party skill's confidence, preferred terminology or examples do not prove this blueprint's architecture or a preset's compatibility.

## `nextlevelbuilder/ui-ux-pro-max-skill`

| Field | Recorded value |
| --- | --- |
| Repository | [`nextlevelbuilder/ui-ux-pro-max-skill`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) |
| Audited commit | [`3da52ff1cab1be91848072ec1be5f493d730fd5f`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/commit/3da52ff1cab1be91848072ec1be5f493d730fd5f) |
| Commit time | `2026-07-10T14:30:06Z` |
| License | [MIT](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/3da52ff1cab1be91848072ec1be5f493d730fd5f/LICENSE) |
| Primary files reviewed | [`ui-ux-pro-max/SKILL.md`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/3da52ff1cab1be91848072ec1be5f493d730fd5f/.claude/skills/ui-ux-pro-max/SKILL.md), [token architecture](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/3da52ff1cab1be91848072ec1be5f493d730fd5f/.claude/skills/design-system/references/token-architecture.md), [states and variants](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/3da52ff1cab1be91848072ec1be5f493d730fd5f/.claude/skills/design-system/references/states-and-variants.md), [Next.js stack dataset](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/3da52ff1cab1be91848072ec1be5f493d730fd5f/.claude/skills/ui-ux-pro-max/data/stacks/nextjs.csv) |

Independent findings adopted:

- Start UI work with a product/user brief, generate design candidates across style, color, typography, layout, density and motion, then record rationale rather than selecting by taste alone.
- Separate primitive, semantic and component/state tokens and connect them through the selected framework's native theming mechanism.
- Treat responsive behavior, accessibility, state visibility, forms/feedback and data visualization as design-system concerns with objective checks.
- Combine broad design recommendations with stack-specific API guidance; do not mistake a generic visual rule for framework-compatible implementation.

Security and distribution finding:

- The npm registry reported `ui-ux-pro-max-cli@2.10.2` on 2026-07-12. Tag `v2.10.2` resolves to [`12b486b22e67f5d887962ef8351c1ac863bfaeb9`](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/commit/12b486b22e67f5d887962ef8351c1ac863bfaeb9), which predates the audited hardening commit `3da52ff1`.
- The later [hardening commit](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/commit/3da52ff1cab1be91848072ec1be5f493d730fd5f) removed unused prompt-shaped datasets, constrained persisted path names, replaced agent-directed system package installation with a user decision, and reported repository verification. That commit was not an npm release at audit time.
- Therefore the blueprint must not install the current npm package or assume its distributed assets contain the audited fixes. If source-assisted research is approved, use the exact reviewed commit read-only, verify its digest and license, and sandbox only the minimum inspected operation.

Not adopted as authority:

- Generated palettes, style rankings, numerical design defaults and stack snippets are candidates, not requirements.
- UI recommendations cannot override WCAG, product constraints, user safety, official API documentation, the preset's interaction contracts or observed outcome evidence.

## Context7 lookup record

| Field | Recorded value |
| --- | --- |
| Resolved library | `/upstash/context7` |
| Repository revision | [`a9d7c77f5e4c93c1c875b109d6d057487f2dc437`](https://github.com/upstash/context7/commit/a9d7c77f5e4c93c1c875b109d6d057487f2dc437) |
| Queried on | `2026-07-12` |
| Query scope | Required resolve-then-query workflow and reproducible version/source metadata for agent API decisions |
| Returned primary sources | [Context7 agent workflow](https://github.com/upstash/context7/blob/a9d7c77f5e4c93c1c875b109d6d057487f2dc437/docs/agentic-tools/ai-sdk/agents/context7-agent.mdx), [`find-docs` skill](https://github.com/upstash/context7/blob/a9d7c77f5e4c93c1c875b109d6d057487f2dc437/skills/find-docs/SKILL.md), [CLI rule](https://github.com/upstash/context7/blob/a9d7c77f5e4c93c1c875b109d6d057487f2dc437/rules/context7-cli.md) |

The result supports resolving a library name first, selecting the best official/version match, and querying documentation with a specific task. Context7 results remain retrieval evidence: record the selected ID, scope and returned source, then reconcile API claims with the exact dependency lock and official documentation. Re-query when the dependency, library ID, returned source or preset review deadline changes.

## Refresh triggers

Refresh this record when either pinned repository is intentionally upgraded, its license changes, a cited file disappears, a security review changes the allowed execution boundary, Context7 resolution behavior changes, or a preset wants to copy rather than independently reinterpret source material.
