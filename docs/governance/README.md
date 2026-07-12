# App governance artifacts

This directory is reserved for repository-local state created when a preset is instantiated. It is documentation today; no app or preset is currently selected.

An app bootstrap should create, at minimum:

- `preset-lock.json`: preset ID/version, immutable source revision, blueprint version/revision, manifest/template/skill/pattern/source/design/evaluation/integrity digests, qualification evidence references, materialization timestamp, and verification result;
- a local decision/override record for deliberate deviations;
- links to the current system profile, artifact registry, architecture exceptions, and verification evidence when those artifacts apply.

These files describe the generated app, not the reusable preset. They must not be written during `AUTHOR_PRESET`, and an upgrade must reconcile them instead of silently replacing local decisions.
