# Start here

This repository supports five distinct modes. Declare one before changing files.

| Mode | Choose it when | First read | Allowed primary output |
| --- | --- | --- | --- |
| `BLUEPRINT_MAINTENANCE` | Improving portable rules or governance | [`docs/blueprint/README.md`](docs/blueprint/README.md) | owning guides, shared contracts/schemas/validators, entry docs, tests and changelog; no app source or preset instance |
| `AUTHOR_PRESET` | Creating or upgrading a reusable stack combo | [`docs/blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md`](docs/blueprint/reference-app-blueprint/10-preset-authoring-and-instantiation.md) | `docs/presets/<preset-id>/**` |
| `APP_BOOTSTRAP` | Instantiating a verified preset or adopting governance for an existing/custom app | Preset: [`docs/presets/README.md`](docs/presets/README.md); adoption: [`docs/blueprint/06-greenfield-bootstrap-and-portability.md`](docs/blueprint/06-greenfield-bootstrap-and-portability.md) | preset materialization paths, or repo-local governance/skill/pattern/verification artifacts for one app profile |
| `APP_DEVELOPMENT` | Changing an app governed by a preset lock or accepted app profile | [`AGENTS.md`](AGENTS.md) plus the selected authority's skills | paths owned by the selected task skill |
| `NEW_PATTERN` | No selected-authority pattern can satisfy a required capability | [`AGENTS.md`](AGENTS.md), selected `new-pattern` skill, then the exact blueprint owner | smallest local pattern, fitness evidence, and approved catalog/ADR delta |

The preset catalog is intentionally empty today. Do not pretend a preset is verified or generate an app from a nonexistent preset. A new app should author and verify a preset before instantiation. An existing/custom app may instead adopt an `app-profile`, but only after its current artifact registry, stack profile, pattern/skill registries, command lanes, revision-bound clean-room execution record, dual-verdict skill evaluations, revisions, and digests validate together.

## Suggested prompts

Maintain the blueprint:

> Read AGENTS.md and evaluate this architecture requirement against the source-of-truth blueprint. Update only the owning rule and its required contracts/tests.

Author a preset later:

> Read AGENTS.md. In AUTHOR_PRESET mode, create an exact-version preset for my selected stack. Prove its read, write, and auth walking slices before marking any capability verified.

Instantiate an app later:

> Read AGENTS.md. Analyze my requirements, select a compatible verified preset, show fit and gaps, then instantiate it without changing the preset's architectural patterns.

Adopt an existing/custom app:

> Read AGENTS.md. In APP_BOOTSTRAP / ADOPT_APP_PROFILE, preserve current behavior, validate the repo-local artifact, pattern, skill, command, clean-room and evaluation records, then create exactly one app-profile authority without claiming preset provenance.

Develop a governed app:

> Read AGENTS.md and resolve exactly one preset lock or app profile. Turn this requirement into a vertical task graph, select locked pattern IDs and matching skills, then satisfy each skill's completion and verification criteria.

## Human decisions AI must not invent

- product scope, risk acceptance, owners, and release approval;
- whether a preset fit gap is acceptable;
- whether an ungoverned existing app should adopt an app profile or first author a reusable preset;
- destructive replacement of conflicting app files;
- promotion of a local exception into a reusable repository pattern.

All other safe, in-scope discovery and verification should proceed without turning the setup into an open-ended technology interview.
