from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_docs import (
    load_documents,
    validate_ci_contract,
    validate_evidence_manifest_schema,
    validate_metadata,
    validate_repository,
)


GUIDE = """---
guide_id: TEST-GUIDE
title: Test guide
status: candidate
audience: human-and-ai
depends_on: []
---

# Test guide

## Rule `TEST-RULE-01`: one owner

Use `TEST-RULE-01`.
"""

REFACTOR_TEMPLATE = """---
template_id: TEST-REFACTOR-TEMPLATE
template_version: 1.1.0
produces: refactor-plan
owner_guide: 01-test.md
use_when: Testing refactor-plan contracts.
---

# Refactor template
"""


def refactor_plan(
    *,
    omit: str | None = None,
    empty: str | None = None,
    header_only: str | None = None,
    without_separator: str | None = None,
    fenced_only: str | None = None,
) -> str:
    sections = {
        "Frozen boundary and authorized delta": """| Boundary group | Baseline | Authorized delta | Final proof | Owner |
| --- | --- | --- | --- | --- |
| Public contract | revision-a | None | immutable diff passed | architecture-team |""",
        "Candidate disposition": """| Finding | Disposition | Rationale | Evidence | Owner |
| --- | --- | --- | --- | --- |
| No candidate in scope | N/A | Focused seam only | `check-a \\| check-b` reviewed | architecture-team |""",
        "Characterization": "Observable success, failure, authorization, and effect behavior is recorded.",
        "Behavior-equivalence matrix": """| Axis | Baseline | Target | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Callable contract | preserved-shape | compatible-shape | contract suite passed | architecture-team |""",
        "Checker coverage": "Analyzed roots, supported forms, exclusions, and positive/negative fixtures are recorded.",
        "Transition": "The selected seam, migration batches, ratchet, and abort threshold are explicit.",
        "Cutover and deletion": "Consumer, recovery, and candidate-closure proof gate deletion.",
    }
    body = []
    for heading, content in sections.items():
        if heading == omit:
            continue
        if heading == header_only:
            content = "Instructions remain copied from the template.\n\n" + "\n".join(
                content.splitlines()[:2]
            )
        if heading == without_separator:
            rows = content.splitlines()
            content = "\n".join((rows[0], rows[2]))
        if heading == fenced_only:
            content = (
                "Instructions remain copied from the template.\n\n```text\n"
                + content
                + "\n```"
            )
        body.append(f"## {heading}\n\n{'' if heading == empty else content}")
    return """---
artifact_id: REF-EXAMPLE-01
artifact_type: refactor-plan
schema_version: 1.0
artifact_version: 1
title: Approved refactor slice
status: approved
owner: architecture-team
created_at: 2026-07-19
updated_at: 2026-07-19
scope:
  - system:test
source_template: template.md
supersedes: []
superseded_by: null
review_by: null
expires_at: null
---

# Approved refactor slice

""" + "\n\n".join(body) + "\n"


class ValidatorTests(unittest.TestCase):
    def validate(self, files: dict[str, str]):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            return validate_repository(root, require_catalog=False)[0]

    def test_accepts_minimal_valid_guide(self):
        self.assertEqual(self.validate({"01-test.md": GUIDE}), [])

    def test_accepts_complete_effective_refactor_plan(self):
        self.assertEqual(
            self.validate(
                {
                    "01-test.md": GUIDE,
                    "template.md": REFACTOR_TEMPLATE,
                    "refactor.md": refactor_plan(),
                }
            ),
            [],
        )

    def test_draft_refactor_plan_may_defer_contract_sections(self):
        draft = refactor_plan(omit="Frozen boundary and authorized delta").replace(
            "status: approved", "status: draft"
        )
        self.assertEqual(
            self.validate(
                {
                    "01-test.md": GUIDE,
                    "template.md": REFACTOR_TEMPLATE,
                    "refactor.md": draft,
                }
            ),
            [],
        )

    def test_rejects_missing_or_empty_refactor_contract_sections(self):
        headings = (
            "Frozen boundary and authorized delta",
            "Candidate disposition",
            "Behavior-equivalence matrix",
            "Checker coverage",
        )
        for heading in headings:
            with self.subTest(heading=heading, state="missing"):
                findings = self.validate(
                    {
                        "01-test.md": GUIDE,
                        "template.md": REFACTOR_TEMPLATE,
                        "refactor.md": refactor_plan(omit=heading),
                    }
                )
                self.assertTrue(
                    any(
                        f"requires '## {heading}'" in finding.message
                        for finding in findings
                    )
                )
            with self.subTest(heading=heading, state="empty"):
                findings = self.validate(
                    {
                        "01-test.md": GUIDE,
                        "template.md": REFACTOR_TEMPLATE,
                        "refactor.md": refactor_plan(empty=heading),
                    }
                )
                self.assertTrue(
                    any(
                        f"has an empty '## {heading}' section" in finding.message
                        for finding in findings
                    )
                )

    def test_rejects_copied_but_unfilled_refactor_data_tables(self):
        for heading in (
            "Frozen boundary and authorized delta",
            "Candidate disposition",
            "Behavior-equivalence matrix",
        ):
            with self.subTest(heading=heading):
                findings = self.validate(
                    {
                        "01-test.md": GUIDE,
                        "template.md": REFACTOR_TEMPLATE,
                        "refactor.md": refactor_plan(header_only=heading),
                    }
                )
                self.assertTrue(
                    any(
                        f"requires a populated data row in '## {heading}'"
                        in finding.message
                        for finding in findings
                    )
                )

    def test_rejects_refactor_data_table_without_separator(self):
        heading = "Candidate disposition"
        findings = self.validate(
            {
                "01-test.md": GUIDE,
                "template.md": REFACTOR_TEMPLATE,
                "refactor.md": refactor_plan(without_separator=heading),
            }
        )
        self.assertTrue(
            any(
                f"requires a populated data row in '## {heading}'" in finding.message
                for finding in findings
            )
        )

    def test_rejects_refactor_data_table_inside_fenced_example(self):
        heading = "Candidate disposition"
        findings = self.validate(
            {
                "01-test.md": GUIDE,
                "template.md": REFACTOR_TEMPLATE,
                "refactor.md": refactor_plan(fenced_only=heading),
            }
        )
        self.assertTrue(
            any(
                f"requires a populated data row in '## {heading}'" in finding.message
                for finding in findings
            )
        )

    def test_rejects_required_refactor_section_inside_fenced_example(self):
        heading = "Candidate disposition"
        artifact = refactor_plan(omit=heading).replace(
            "## Characterization",
            """```markdown
## Candidate disposition

| Finding | Disposition | Rationale | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Candidate | REFACTOR_CONFIRMED | Same behavior | Tests pass | architecture-team |
```

## Characterization""",
        )
        findings = self.validate(
            {
                "01-test.md": GUIDE,
                "template.md": REFACTOR_TEMPLATE,
                "refactor.md": artifact,
            }
        )
        self.assertTrue(
            any(f"requires '## {heading}'" in finding.message for finding in findings)
        )

    def test_fence_with_trailing_text_cannot_expose_fake_refactor_section(self):
        heading = "Candidate disposition"
        artifact = refactor_plan(omit=heading).replace(
            "## Characterization",
            """````markdown
````not-a-close
## Candidate disposition

| Finding | Disposition | Rationale | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Candidate | REFACTOR_CONFIRMED | Same behavior | Tests pass | architecture-team |
````still-not-a-close
````

## Characterization""",
        )
        findings = self.validate(
            {
                "01-test.md": GUIDE,
                "template.md": REFACTOR_TEMPLATE,
                "refactor.md": artifact,
            }
        )
        self.assertTrue(
            any(f"requires '## {heading}'" in finding.message for finding in findings)
        )

    def test_html_comment_cannot_expose_fake_refactor_section(self):
        heading = "Candidate disposition"
        artifact = refactor_plan(omit=heading).replace(
            "## Characterization",
            """<!--
## Candidate disposition

| Finding | Disposition | Rationale | Evidence | Owner |
| --- | --- | --- | --- | --- |
| Candidate | REFACTOR_CONFIRMED | Same behavior | Tests pass | architecture-team |
-->

## Characterization""",
        )
        findings = self.validate(
            {
                "01-test.md": GUIDE,
                "template.md": REFACTOR_TEMPLATE,
                "refactor.md": artifact,
            }
        )
        self.assertTrue(
            any(f"requires '## {heading}'" in finding.message for finding in findings)
        )

    def test_rejects_fenced_only_refactor_section_substance(self):
        heading = "Checker coverage"
        artifact = refactor_plan().replace(
            "## Checker coverage\n\nAnalyzed roots, supported forms, exclusions, and positive/negative fixtures are recorded.",
            "## Checker coverage\n\n```text\nExample coverage only.\n```",
        )
        findings = self.validate(
            {
                "01-test.md": GUIDE,
                "template.md": REFACTOR_TEMPLATE,
                "refactor.md": artifact,
            }
        )
        self.assertTrue(
            any(
                f"has an empty '## {heading}' section" in finding.message
                for finding in findings
            )
        )

    def test_requires_evidence_manifest_schema(self):
        with tempfile.TemporaryDirectory() as temporary:
            findings = validate_evidence_manifest_schema(Path(temporary))
        self.assertTrue(any("invalid or missing evidence manifest schema" in finding.message for finding in findings))

    def test_rejects_broken_relative_link(self):
        findings = self.validate({"01-test.md": GUIDE + "\n[missing](missing.md)\n"})
        self.assertTrue(any("broken relative link" in finding.message for finding in findings))

    def test_rejects_duplicate_identity(self):
        findings = self.validate({"01-test.md": GUIDE, "02-test.md": GUIDE})
        self.assertTrue(any("duplicate ID" in finding.message for finding in findings))

    def test_rejects_undefined_rule_reference(self):
        findings = self.validate({"01-test.md": GUIDE + "\nUse `MISSING-RULE-01`.\n"})
        self.assertTrue(any("undefined rule" in finding.message for finding in findings))

    def test_rejects_unclosed_fence_and_trailing_whitespace(self):
        findings = self.validate({"01-test.md": GUIDE + "\n```text\nvalue  \n"})
        self.assertTrue(any("unclosed fenced" in finding.message for finding in findings))
        self.assertTrue(any("trailing whitespace" in finding.message for finding in findings))

    def test_rejects_task_router_over_context_budget(self):
        router = """
## Task router

| Task | Required reads | Add only when needed |
| --- | --- | --- |
| Too broad | README, 01, 02, 03, 04 | None |
"""
        findings = self.validate({"01-test.md": GUIDE + router})
        self.assertTrue(any("maximum is 4" in finding.message for finding in findings))

    def test_rejects_blocking_placeholder_in_accepted_artifact(self):
        artifact = """---
artifact_id: ART-EXAMPLE-01
artifact_type: adr
schema_version: 1.0
artifact_version: 1
title: Accepted example
status: accepted
owner: platform-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:test
source_template: template.md
supersedes: []
superseded_by: null
---

# Accepted example

TBD
"""
        template = """---
template_id: TEST-TEMPLATE
template_version: 1.0.0
produces: adr
owner_guide: 01-test.md
use_when: Testing.
---

# Template
"""
        findings = self.validate(
            {"01-test.md": GUIDE, "template.md": template, "artifact.md": artifact}
        )
        self.assertTrue(any("blocking placeholder" in finding.message for finding in findings))

    def test_rejects_template_instance_version_drift(self):
        artifact = """---
artifact_id: ART-EXAMPLE-02
artifact_type: adr
schema_version: 1.0
artifact_version: 1
title: Version drift
status: proposed
owner: platform-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:test
source_template: TEST-TEMPLATE@2.0.0
supersedes: []
superseded_by: null
review_by: null
expires_at: null
---

# Version drift
"""
        template = """---
template_id: TEST-TEMPLATE
template_version: 1.0.0
produces: adr
owner_guide: 01-test.md
use_when: Testing.
---

# Template
"""
        findings = self.validate(
            {"01-test.md": GUIDE, "template.md": template, "artifact.md": artifact}
        )
        self.assertTrue(any("source_template version" in finding.message for finding in findings))

    def test_rejects_artifact_type_status_mismatch(self):
        artifact = """---
artifact_id: ART-EXAMPLE-03
artifact_type: system-profile
schema_version: 1.0
artifact_version: 1
title: Invalid lifecycle
status: accepted
owner: platform-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:test
source_template: TEST-TEMPLATE@1.0.0
supersedes: []
superseded_by: null
review_by: null
expires_at: null
---

# Invalid lifecycle
"""
        template = """---
template_id: TEST-TEMPLATE
template_version: 1.0.0
produces: system-profile
owner_guide: 01-test.md
use_when: Testing.
---

# Template
"""
        findings = self.validate(
            {"01-test.md": GUIDE, "template.md": template, "artifact.md": artifact}
        )
        self.assertTrue(any("invalid for system-profile" in finding.message for finding in findings))

    def test_rejects_source_template_produced_type_mismatch(self):
        artifact = """---
artifact_id: ART-EXAMPLE-04
artifact_type: system-profile
schema_version: 1.0
artifact_version: 1
title: Wrong source template
status: draft
owner: platform-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:test
source_template: TEST-TEMPLATE@1.0.0
supersedes: []
superseded_by: null
review_by: null
expires_at: null
---

# Wrong source template
"""
        template = """---
template_id: TEST-TEMPLATE
template_version: 1.0.0
produces: adr
owner_guide: 01-test.md
use_when: Testing.
---

# Template
"""
        findings = self.validate(
            {"01-test.md": GUIDE, "template.md": template, "artifact.md": artifact}
        )
        self.assertTrue(any("produces adr, not system-profile" in finding.message for finding in findings))

    def test_rejects_empty_accepted_capability_artifact(self):
        artifact = """---
artifact_id: ART-CAPABILITY-01
artifact_type: capability-coverage
schema_version: 1.0
artifact_version: 1
title: Empty accepted coverage
status: accepted
owner: platform-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:test
source_template: TEST-CAPABILITY-TEMPLATE@1.0.0
supersedes: []
superseded_by: null
review_by: null
expires_at: null
---

# Empty accepted coverage

## Selection gate

## Coverage reconciliation

"""
        template = """---
template_id: TEST-CAPABILITY-TEMPLATE
template_version: 1.0.0
produces: capability-coverage
owner_guide: 01-test.md
use_when: Testing.
---

# Template
"""
        findings = self.validate(
            {"01-test.md": GUIDE, "template.md": template, "artifact.md": artifact}
        )
        self.assertTrue(any("empty '## Selection gate'" in finding.message for finding in findings))
        self.assertTrue(any("requires trace token 'CTL-'" in finding.message for finding in findings))

    def test_rejects_unchecked_gate_in_effective_artifact(self):
        artifact = """---
artifact_id: ART-CAPABILITY-02
artifact_type: capability-coverage
schema_version: 1.0
artifact_version: 1
title: Incomplete accepted coverage
status: accepted
owner: platform-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:test
source_template: TEST-CAPABILITY-TEMPLATE@1.0.0
supersedes: []
superseded_by: null
review_by: null
expires_at: null
---

# Incomplete accepted coverage

## Selection gate

- [ ] Confirm `CAP-TEST`, `CTL-TEST-01`, `GATE-TEST-01`, and `EVID-TEST`.

## Coverage reconciliation

Coverage is linked to the accepted profile.
"""
        template = """---
template_id: TEST-CAPABILITY-TEMPLATE
template_version: 1.0.0
produces: capability-coverage
owner_guide: 01-test.md
use_when: Testing.
---

# Template
"""
        findings = self.validate(
            {"01-test.md": GUIDE, "template.md": template, "artifact.md": artifact}
        )
        self.assertTrue(any("unchecked completion gate" in finding.message for finding in findings))

    def test_rejects_empty_active_system_profile(self):
        artifact = """---
artifact_id: SYS-EXAMPLE-01
artifact_type: system-profile
schema_version: 1.0
artifact_version: 1
title: Empty active profile
status: active
owner: platform-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:test
source_template: TEST-SYSTEM-TEMPLATE@1.0.0
supersedes: []
superseded_by: null
review_by: 2020-10-01
expires_at: null
---

# Empty active profile
"""
        template = """---
template_id: TEST-SYSTEM-TEMPLATE
template_version: 1.0.0
produces: system-profile
owner_guide: 01-test.md
use_when: Testing.
---

# Template
"""
        findings = self.validate(
            {"01-test.md": GUIDE, "template.md": template, "artifact.md": artifact}
        )
        self.assertTrue(any("effective system-profile requires '## Ownership'" in finding.message for finding in findings))
        self.assertTrue(any("requires trace token 'CTL-'" in finding.message for finding in findings))
        self.assertTrue(any("review_by is overdue" in finding.message for finding in findings))

    def test_rejects_blank_named_field_in_effective_artifact(self):
        artifact = """---
artifact_id: ADR-EXAMPLE-05
artifact_type: adr
schema_version: 1.0
artifact_version: 1
title: Incomplete accepted ADR
status: accepted
owner: platform-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:test
source_template: TEST-ADR-TEMPLATE@1.0.0
supersedes: []
superseded_by: null
review_by: null
expires_at: null
---

# Incomplete accepted ADR

## Context and decision drivers

One durable driver exists.

## Options considered

Option A and option B were compared.

## Decision

- Decision owner:

## Consequences

The trade-off is explicit.

## Fitness evidence

The selected check is recorded.
"""
        template = """---
template_id: TEST-ADR-TEMPLATE
template_version: 1.0.0
produces: adr
owner_guide: 01-test.md
use_when: Testing.
---

# Template
"""
        findings = self.validate(
            {"01-test.md": GUIDE, "template.md": template, "artifact.md": artifact}
        )
        self.assertTrue(any("empty named field" in finding.message for finding in findings))

    def test_rejects_missing_supersession_target(self):
        artifact = """---
artifact_id: ADR-EXAMPLE-06
artifact_type: adr
schema_version: 1.0
artifact_version: 1
title: Missing supersession target
status: proposed
owner: platform-team
created_at: 2026-07-12
updated_at: 2026-07-12
scope:
  - system:test
source_template: TEST-ADR-TEMPLATE@1.0.0
supersedes:
  - ADR-MISSING-000
superseded_by: null
review_by: null
expires_at: null
---

# Missing supersession target
"""
        template = """---
template_id: TEST-ADR-TEMPLATE
template_version: 1.0.0
produces: adr
owner_guide: 01-test.md
use_when: Testing.
---

# Template
"""
        findings = self.validate(
            {"01-test.md": GUIDE, "template.md": template, "artifact.md": artifact}
        )
        self.assertTrue(any("supersedes target does not exist" in finding.message for finding in findings))

    def test_rejects_package_version_drift(self):
        def guide(identifier: str, extra: str) -> str:
            return f"""---
guide_id: {identifier}
title: Test
status: candidate
audience: human-and-ai
{extra}---

# Test
"""

        files = {
            "README.md": guide(
                "TEST-ROOT",
                "package_version: 1.0.0\ncontrol_catalog_version: 1.0.0\nartifact_schema_version: 1.0\n",
            ),
            "MATURITY.md": guide(
                "TEST-MATURITY",
                "package_version: 2.0.0\ncontrol_catalog_version: 1.0.0\nartifact_schema_version: 1.0\n",
            ),
            "CHANGELOG.md": """---
document_id: TEST-CHANGELOG
title: Test changelog
status: candidate
audience: human-and-ai
package_version: 1.0.0
---

# Changelog
""",
            "08-scorecard-and-readiness-gates.md": guide(
                "TEST-SCORE", "control_catalog_version: 1.0.0\n"
            ),
            "templates/README.md": guide("TEST-SCHEMA", "schema_version: 1.0\n"),
            "controls/core-controls.json": '{"catalog_version":"1.0.0"}\n',
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            documents, parse_findings = load_documents(root)
            self.assertEqual(parse_findings, [])
            findings = validate_metadata(documents, root, strict_package=True)
        self.assertTrue(any("package_version mismatch" in finding.message for finding in findings))

    def test_rejects_mutable_external_action_tag(self):
        workflow = """permissions:
  contents: read
steps:
  - uses: actions/checkout@v6
    with:
      persist-credentials: false
# "docs/blueprint/controls/**"
# "docs/blueprint/reference-app-blueprint/**/*.json"
# "docs/presets/**"
# PYTHONPATH=docs/blueprint python3 -m unittest discover -s docs/blueprint/scripts -p 'test_*.py'
# python3 docs/blueprint/scripts/validate_docs.py docs/blueprint --repo-root .
# python3 docs/blueprint/scripts/validate_presets.py docs/presets
# python3 docs/blueprint/scripts/score_readiness.py docs/blueprint/reference-app-blueprint/examples/basic-web-artifacts/readiness.json --json --expect not-ready
"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / ".github/workflows/docs-quality.yml"
            path.parent.mkdir(parents=True)
            path.write_text(workflow, encoding="utf-8")
            findings = validate_ci_contract(root)
        self.assertTrue(any("40-character commit SHA" in finding.message for finding in findings))


if __name__ == "__main__":
    unittest.main()
