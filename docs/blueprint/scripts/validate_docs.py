#!/usr/bin/env python3
"""Validate the production-repo blueprint as a self-consistent docs package.

The validator intentionally uses only the Python standard library so the same
command works locally and in an isolated CI job:

    python3 docs/blueprint/scripts/validate_docs.py docs/blueprint --repo-root .
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import unquote


ID_KEYS = ("guide_id", "template_id", "example_id", "artifact_id", "document_id")
ID_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
RULE_PATTERN = re.compile(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{2}(?!\d)")
RULE_DEFINITION = re.compile(
    r"^#{2,6}\s+Rule\s+`(?P<rule>[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{2})`"
)
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]*\]\((?P<target>[^)]+)\)")
HEADING_PATTERN = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*#*$")
FENCE_PATTERN = re.compile(r"^\s*(?P<marker>`{3,}|~{3,})")
FRONTMATTER_KEY = re.compile(r"^(?P<key>[A-Za-z_][A-Za-z0-9_-]*):(?:\s*(?P<value>.*))?$")
EXTERNAL_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
NUMERIC_GUIDE = re.compile(r"^\d{2}-.*\.md$")
CONTROL_TABLE_ROW = re.compile(
    r"^\|\s+`(?P<id>CTL-[A-Z0-9]+(?:-[A-Z0-9]+)+-\d+)`\s+\|\s+(?P<text>.+?)\s+\|$"
)

GUIDE_STATUSES = {"experimental", "candidate", "stable", "deprecated"}
ARTIFACT_TYPE_STATUSES = {
    "system-profile": {"draft", "active", "superseded", "retired"},
    "access-matrix": {"draft", "active", "superseded", "retired"},
    "threat-model": {"draft", "active", "superseded", "retired"},
    "test-strategy": {"draft", "active", "superseded", "retired"},
    "slo-runbook": {"draft", "active", "superseded", "retired"},
    "adr": {"proposed", "accepted", "rejected", "superseded"},
    "architecture-exception": {"proposed", "active", "resolved", "expired", "rejected", "superseded"},
    "readiness-assessment": {"draft", "final", "superseded"},
    "migration-plan": {"draft", "approved", "in-progress", "completed", "cancelled", "superseded"},
    "release-plan": {"draft", "approved", "in-progress", "completed", "cancelled", "superseded"},
    "refactor-plan": {"draft", "approved", "in-progress", "completed", "cancelled", "superseded"},
    "artifact-registry": {"draft", "active", "superseded", "retired"},
    "exception-ledger": {"draft", "active", "superseded", "retired"},
    "stack-profile": {"draft", "in-review", "accepted", "rejected", "superseded"},
    "capability-coverage": {"draft", "in-review", "accepted", "rejected", "superseded"},
    "data-model": {"draft", "in-review", "accepted", "rejected", "superseded"},
    "shared-plan": {"draft", "in-review", "accepted", "rejected", "superseded"},
    "platform-plan": {"draft", "in-review", "accepted", "rejected", "superseded"},
    "feature-plan": {"draft", "in-review", "accepted", "rejected", "superseded"},
    "route-map": {"draft", "in-review", "accepted", "rejected", "superseded"},
    "reference-app-plan": {"draft", "in-review", "accepted", "rejected", "superseded"},
    "preset-contract": {"draft", "in-review", "accepted", "rejected", "superseded"},
}
EFFECTIVE_ARTIFACT_STATUSES = {"active", "accepted", "final", "approved", "in-progress"}
EFFECTIVE_ARTIFACT_REQUIRED_HEADINGS = {
    "system-profile": (
        "Ownership",
        "Primary architecture profile",
        "Critical journeys",
        "Risk classification",
        "Selected controls",
        "Unknowns and adoption decision",
    ),
    "access-matrix": ("Lifecycle", "Enforcement points"),
    "threat-model": (
        "Data flow and trust boundaries",
        "Threats and controls",
        "Verification and residual risk",
    ),
    "test-strategy": ("Determinism", "Architecture fitness", "Completion evidence"),
    "slo-runbook": ("SLI/SLO", "Alerts", "Triage and mitigation", "Last exercised evidence"),
    "adr": ("Context and decision drivers", "Options considered", "Decision", "Consequences", "Fitness evidence"),
    "architecture-exception": (
        "Requested deviation",
        "Risk decision",
        "Compensating controls and ratchet",
        "Time bound and removal",
        "Verification and closure",
    ),
    "readiness-assessment": (
        "Control evidence",
        "Dimension calculation",
        "Readiness declaration",
        "Reproduction record",
    ),
    "migration-plan": ("Phases", "Backfill contract", "Production migration safety", "Recovery"),
    "release-plan": ("Gates", "Infrastructure evidence", "Rollout", "Recovery"),
    "refactor-plan": ("Characterization", "Transition", "Cutover and deletion"),
    "artifact-registry": ("Current and historical artifacts", "Registry invariants", "Registry review"),
    "exception-ledger": ("Ledger", "Ledger invariants", "Review record"),
    "stack-profile": (
        "Acceptance gate",
        "Stack card",
        "Executable topology",
        "Compatibility decisions",
        "Required spikes",
    ),
    "capability-coverage": ("Selection gate", "Coverage reconciliation"),
    "data-model": ("Relationships and invariants", "Lifecycle and isolation", "Migration sequence"),
    "shared-plan": ("Contract inventory", "UI and interaction contract", "Dependency and rollout check"),
    "platform-plan": (
        "Capability and adapter matrix",
        "Executable composition",
        "Configuration and trust",
        "Failure and operations evidence",
        "Acceptance",
    ),
    "feature-plan": ("Public contracts", "Evidence"),
    "route-map": ("Routes and entrypoints", "Critical journeys"),
    "reference-app-plan": (
        "Artifact registry",
        "End-to-end traceability",
        "Control and readiness bridge",
        "Completion evidence",
    ),
    "preset-contract": (
        "Filesystem and materialization map",
        "Capability matrix",
        "Inter-layer contract matrix",
        "AI guide routing",
        "Clean-room verification",
    ),
}
EFFECTIVE_ARTIFACT_REQUIRED_TOKENS = {
    "system-profile": ("CTL-",),
    "readiness-assessment": ("CTL-", "GATE-"),
    "capability-coverage": ("CAP-", "CTL-", "GATE-", "EVID-"),
    "feature-plan": ("CAP-", "EVID-"),
    "route-map": ("CAP-", "JRN-"),
    "reference-app-plan": ("CAP-", "CTL-", "GATE-", "EVID-"),
    "preset-contract": ("PRESET-", "EVID-"),
}
AUDIENCES = {"ai-agent", "human", "human-and-ai"}
EXAMPLE_STATUSES = {"experimental", "candidate", "stable", "deprecated", "example"}
CORE_FORBIDDEN_STACK_TERMS = (
    "next.js",
    "react",
    "prisma",
    "ant design",
    "tanstack query",
    "drizzle",
    "shadcn",
    "better auth",
    "django",
    "htmx",
    "laravel",
    "rails",
)


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


@dataclass
class Document:
    path: Path
    relative_path: Path
    text: str
    lines: list[str]
    metadata: dict[str, str | list[str]]
    metadata_lines: dict[str, int]


def _unquote(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_frontmatter(
    relative_path: Path, lines: list[str]
) -> tuple[dict[str, str | list[str]], dict[str, int], list[Finding]]:
    findings: list[Finding] = []
    if not lines or lines[0].strip() != "---":
        return {}, {}, [Finding(str(relative_path), 1, "missing YAML frontmatter")]

    try:
        end = next(index for index, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return {}, {}, [Finding(str(relative_path), 1, "frontmatter has no closing delimiter")]

    metadata: dict[str, str | list[str]] = {}
    metadata_lines: dict[str, int] = {}
    active_list: str | None = None

    for index in range(1, end):
        raw = lines[index]
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if active_list and re.match(r"^\s+-\s+", raw):
            item = re.sub(r"^\s+-\s+", "", raw).strip()
            current = metadata.setdefault(active_list, [])
            if isinstance(current, list):
                current.append(_unquote(item))
            continue

        match = FRONTMATTER_KEY.match(raw)
        if not match:
            findings.append(
                Finding(str(relative_path), index + 1, "unsupported or malformed frontmatter line")
            )
            active_list = None
            continue

        key = match.group("key")
        value = (match.group("value") or "").strip()
        metadata_lines[key] = index + 1
        if not value:
            metadata[key] = []
            active_list = key
        elif value == "[]":
            metadata[key] = []
            active_list = None
        else:
            metadata[key] = _unquote(value)
            active_list = None

    return metadata, metadata_lines, findings


def load_documents(root: Path) -> tuple[list[Document], list[Finding]]:
    documents: list[Document] = []
    findings: list[Finding] = []
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", ".venv", "node_modules"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        relative = path.relative_to(root)
        metadata, metadata_lines, metadata_findings = parse_frontmatter(relative, lines)
        findings.extend(metadata_findings)
        documents.append(Document(path, relative, text, lines, metadata, metadata_lines))
    return documents, findings


def metadata_value(document: Document, key: str) -> str | None:
    value = document.metadata.get(key)
    if not isinstance(value, str) or value.strip().lower() in {"null", "none", "~"}:
        return None
    return value


def metadata_line(document: Document, key: str) -> int:
    return document.metadata_lines.get(key, 1)


def require_fields(document: Document, fields: tuple[str, ...]) -> list[Finding]:
    findings: list[Finding] = []
    for field in fields:
        value = document.metadata.get(field)
        if value is None or value == "" or value == []:
            findings.append(
                Finding(str(document.relative_path), 1, f"missing required frontmatter field '{field}'")
            )
    return findings


def markdown_section(document: Document, title: str) -> tuple[int, list[str]] | None:
    heading = re.compile(r"^##\s+" + re.escape(title) + r"\s*#*$", re.IGNORECASE)
    start: int | None = None
    for index, line in enumerate(document.lines):
        if start is None:
            if heading.match(line):
                start = index
            continue
        if line.startswith("## "):
            return start + 1, document.lines[start + 1 : index]
    if start is not None:
        return start + 1, document.lines[start + 1 :]
    return None


def section_has_substance(lines: list[str]) -> bool:
    meaningful = [line.strip() for line in lines if line.strip()]
    if not meaningful:
        return False
    table_rows = [line for line in meaningful if line.startswith("|") and line.endswith("|")]
    non_table = [line for line in meaningful if line not in table_rows]
    if any(not re.fullmatch(r"<!--.*-->", line) for line in non_table):
        return True
    data_rows = [
        line
        for line in table_rows
        if not re.fullmatch(r"\|(?:\s*:?-+:?\s*\|)+", line)
    ]
    return len(data_rows) >= 2


def validate_effective_artifact_body(
    document: Document, artifact_type: str, status: str
) -> list[Finding]:
    if status not in EFFECTIVE_ARTIFACT_STATUSES:
        return []
    findings: list[Finding] = []
    for line_number, line in enumerate(document.lines, 1):
        stripped = line.strip()
        if re.fullmatch(r"-\s+[^:]+:\s*", stripped):
            findings.append(
                Finding(
                    str(document.relative_path),
                    line_number,
                    "effective artifact contains an empty named field; use an explicit value or N/A rationale",
                )
            )
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        is_separator = bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)
        if not is_separator and any(not cell for cell in cells):
            findings.append(
                Finding(
                    str(document.relative_path),
                    line_number,
                    "effective artifact table contains a blank cell; use an explicit value or N/A rationale",
                )
            )
    if re.search(r"^\s*-\s*\[\s\]\s+", document.text, re.MULTILINE):
        findings.append(
            Finding(
                str(document.relative_path),
                1,
                "effective artifact contains an unchecked completion gate",
            )
        )
    for heading in EFFECTIVE_ARTIFACT_REQUIRED_HEADINGS.get(artifact_type, ()):
        section = markdown_section(document, heading)
        if section is None:
            findings.append(
                Finding(
                    str(document.relative_path),
                    1,
                    f"effective {artifact_type} requires '## {heading}'",
                )
            )
        elif not section_has_substance(section[1]):
            findings.append(
                Finding(
                    str(document.relative_path),
                    section[0],
                    f"effective {artifact_type} has an empty '## {heading}' section",
                )
            )
    for token in EFFECTIVE_ARTIFACT_REQUIRED_TOKENS.get(artifact_type, ()):
        if token not in document.text:
            findings.append(
                Finding(
                    str(document.relative_path),
                    1,
                    f"effective {artifact_type} requires trace token '{token}'",
                )
            )
    return findings


def validate_metadata(documents: list[Document], root: Path, *, strict_package: bool) -> list[Finding]:
    findings: list[Finding] = []
    identifiers: dict[str, tuple[Path, int]] = {}
    templates_by_id = {
        template_id: document
        for document in documents
        if (template_id := metadata_value(document, "template_id")) is not None
    }
    template_versions = {
        template_id: metadata_value(document, "template_version")
        for template_id, document in templates_by_id.items()
    }
    templates_by_path = {
        document.path.resolve(): document for document in templates_by_id.values()
    }
    artifacts_by_id = {
        artifact_id: document
        for document in documents
        if (artifact_id := metadata_value(document, "artifact_id")) is not None
    }

    for document in documents:
        metadata = document.metadata
        identity_keys = [key for key in ID_KEYS if metadata_value(document, key)]
        if len(identity_keys) != 1:
            findings.append(
                Finding(
                    str(document.relative_path),
                    1,
                    "frontmatter must declare exactly one of " + ", ".join(ID_KEYS),
                )
            )
        else:
            identity_key = identity_keys[0]
            identity = metadata_value(document, identity_key) or ""
            if not ID_PATTERN.fullmatch(identity):
                findings.append(
                    Finding(
                        str(document.relative_path),
                        metadata_line(document, identity_key),
                        f"invalid {identity_key} '{identity}'",
                    )
                )
            if identity in identifiers:
                previous, previous_line = identifiers[identity]
                findings.append(
                    Finding(
                        str(document.relative_path),
                        metadata_line(document, identity_key),
                        f"duplicate ID '{identity}', first defined at {previous}:{previous_line}",
                    )
                )
            else:
                identifiers[identity] = (
                    document.relative_path,
                    metadata_line(document, identity_key),
                )

        if "guide_id" in metadata:
            findings.extend(require_fields(document, ("title", "status", "audience")))
            status = (metadata_value(document, "status") or "").lower()
            audience = (metadata_value(document, "audience") or "").lower()
            if status and status not in GUIDE_STATUSES:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "status"), f"unknown guide status '{status}'")
                )
            if audience and audience not in AUDIENCES:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "audience"), f"unknown audience '{audience}'")
                )
            if len(document.lines) > 300:
                findings.append(
                    Finding(str(document.relative_path), 301, f"guide exceeds 300-line budget ({len(document.lines)} lines)")
                )

        if "template_id" in metadata:
            findings.extend(require_fields(document, ("template_version", "produces", "owner_guide", "use_when")))
            template_version = metadata_value(document, "template_version") or ""
            if template_version and not re.fullmatch(r"\d+\.\d+\.\d+", template_version):
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "template_version"), "template_version must use semantic x.y.z")
                )
            produced_type = metadata_value(document, "produces") or ""
            if produced_type and produced_type not in ARTIFACT_TYPE_STATUSES:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "produces"), f"unknown produced artifact type '{produced_type}'")
                )

        if "example_id" in metadata:
            findings.extend(require_fields(document, ("title", "status", "audience")))
            example_status = (metadata_value(document, "status") or "").lower()
            if example_status and example_status not in EXAMPLE_STATUSES:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "status"), f"unknown example status '{example_status}'")
                )

        if "document_id" in metadata:
            findings.extend(require_fields(document, ("title", "status", "audience")))
            status = (metadata_value(document, "status") or "").lower()
            audience = (metadata_value(document, "audience") or "").lower()
            if status and status not in GUIDE_STATUSES:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "status"), f"unknown document status '{status}'")
                )
            if audience and audience not in AUDIENCES:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "audience"), f"unknown audience '{audience}'")
                )

        if "artifact_id" in metadata:
            required = (
                "artifact_type",
                "schema_version",
                "artifact_version",
                "title",
                "status",
                "owner",
                "created_at",
                "updated_at",
                "scope",
            )
            findings.extend(require_fields(document, required))
            status = (metadata_value(document, "status") or "").lower()
            artifact_type = metadata_value(document, "artifact_type") or ""
            allowed_statuses = ARTIFACT_TYPE_STATUSES.get(artifact_type)
            if not allowed_statuses:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "artifact_type"), f"unknown artifact_type '{artifact_type}'")
                )
            elif status and status not in allowed_statuses:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "status"), f"status '{status}' is invalid for {artifact_type}")
                )
            artifact_version = metadata_value(document, "artifact_version")
            if not artifact_version or not artifact_version.isdigit() or int(artifact_version) < 1:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "artifact_version"), "artifact_version must be a positive integer")
                )
            scope = metadata.get("scope")
            if not isinstance(scope, list) or not scope:
                findings.append(Finding(str(document.relative_path), metadata_line(document, "scope"), "scope must be a non-empty list"))
            elif any(not re.fullmatch(r"[a-z][a-z0-9-]*:[A-Za-z0-9._-]+", item) for item in scope):
                findings.append(Finding(str(document.relative_path), metadata_line(document, "scope"), "scope entries must use stable kind:value tokens"))
            for relation in ("source_template", "supersedes", "superseded_by", "review_by", "expires_at"):
                if relation not in metadata:
                    findings.append(Finding(str(document.relative_path), 1, f"artifact missing lifecycle field '{relation}'"))
            supersedes = metadata.get("supersedes")
            if not isinstance(supersedes, list) or any(
                not isinstance(identifier, str) or not ID_PATTERN.fullmatch(identifier)
                for identifier in supersedes
            ):
                findings.append(
                    Finding(
                        str(document.relative_path),
                        metadata_line(document, "supersedes"),
                        "supersedes must be a list of stable artifact IDs (or [])",
                    )
                )
            superseded_by_raw = metadata.get("superseded_by")
            superseded_by = metadata_value(document, "superseded_by")
            if isinstance(superseded_by_raw, list) or (
                superseded_by is not None and not ID_PATTERN.fullmatch(superseded_by)
            ):
                findings.append(
                    Finding(
                        str(document.relative_path),
                        metadata_line(document, "superseded_by"),
                        "superseded_by must be one stable artifact ID or null",
                    )
                )
            if status == "superseded" and metadata_value(document, "superseded_by") is None:
                findings.append(Finding(str(document.relative_path), metadata_line(document, "superseded_by"), "superseded artifact requires superseded_by"))
            if artifact_type == "architecture-exception" and status == "active" and metadata_value(document, "expires_at") is None:
                findings.append(Finding(str(document.relative_path), metadata_line(document, "expires_at"), "active architecture exception requires expires_at"))
            if artifact_type in {"system-profile", "access-matrix", "threat-model", "test-strategy", "slo-runbook"} and status == "active" and metadata_value(document, "review_by") is None:
                findings.append(Finding(str(document.relative_path), metadata_line(document, "review_by"), f"active {artifact_type} requires review_by"))
            if status in EFFECTIVE_ARTIFACT_STATUSES and re.search(r"\b(?:TBD|TODO|FIXME)\b", document.text):
                findings.append(
                    Finding(str(document.relative_path), 1, "effective artifact contains a blocking placeholder")
                )
            findings.extend(validate_effective_artifact_body(document, artifact_type, status))

        for date_key in ("verified_on", "created_at", "updated_at", "review_by", "expires_at"):
            value = metadata_value(document, date_key)
            if not value:
                continue
            try:
                parsed = date.fromisoformat(value)
            except ValueError:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, date_key), f"'{date_key}' must use YYYY-MM-DD")
                )
                continue
            if date_key in {"verified_on", "created_at", "updated_at"} and parsed > date.today():
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, date_key), f"'{date_key}' cannot be in the future")
                )

        created = metadata_value(document, "created_at")
        updated = metadata_value(document, "updated_at")
        if created and updated:
            try:
                if date.fromisoformat(updated) < date.fromisoformat(created):
                    findings.append(Finding(str(document.relative_path), metadata_line(document, "updated_at"), "updated_at cannot precede created_at"))
            except ValueError:
                pass
        if "artifact_id" in document.metadata:
            status = (metadata_value(document, "status") or "").lower()
            artifact_type = metadata_value(document, "artifact_type") or ""
            review_by = metadata_value(document, "review_by")
            if status in EFFECTIVE_ARTIFACT_STATUSES and review_by:
                try:
                    if date.fromisoformat(review_by) < date.today():
                        findings.append(
                            Finding(
                                str(document.relative_path),
                                metadata_line(document, "review_by"),
                                "effective artifact review_by is overdue",
                            )
                        )
                except ValueError:
                    pass
            expires_at = metadata_value(document, "expires_at")
            if artifact_type == "architecture-exception" and status == "active" and expires_at:
                try:
                    if date.fromisoformat(expires_at) < date.today():
                        findings.append(
                            Finding(
                                str(document.relative_path),
                                metadata_line(document, "expires_at"),
                                "active architecture exception is expired and must transition status",
                            )
                        )
                except ValueError:
                    pass

        for path_key in ("owner_guide",):
            target = metadata_value(document, path_key)
            if not target:
                continue
            resolved = (document.path.parent / target).resolve()
            if not resolved.exists():
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, path_key), f"{path_key} target does not exist: {target}")
                )

        source_template = metadata_value(document, "source_template")
        if source_template:
            if "/" in source_template or source_template.endswith(".md"):
                resolved = (document.path.parent / source_template).resolve()
                if not resolved.exists():
                    findings.append(
                        Finding(str(document.relative_path), metadata_line(document, "source_template"), f"source_template target does not exist: {source_template}")
                    )
                elif "artifact_id" in document.metadata:
                    template_document = templates_by_path.get(resolved)
                    produced = metadata_value(template_document, "produces") if template_document else None
                    artifact_type = metadata_value(document, "artifact_type")
                    if produced is None:
                        findings.append(
                            Finding(
                                str(document.relative_path),
                                metadata_line(document, "source_template"),
                                "source_template path must identify a versioned template",
                            )
                        )
                    elif artifact_type != produced:
                        findings.append(
                            Finding(
                                str(document.relative_path),
                                metadata_line(document, "source_template"),
                                f"source template produces {produced}, not {artifact_type}",
                            )
                        )
            else:
                template_id, separator, version = source_template.partition("@")
                if template_id not in template_versions or not separator or not re.fullmatch(r"\d+\.\d+\.\d+", version):
                    findings.append(
                        Finding(
                            str(document.relative_path),
                            metadata_line(document, "source_template"),
                            "source_template must be a relative template path or TEMPLATE-ID@semver",
                        )
                    )
                elif template_versions[template_id] != version:
                    findings.append(
                        Finding(
                            str(document.relative_path),
                            metadata_line(document, "source_template"),
                            f"source_template version {version} does not match {template_id}@{template_versions[template_id]}",
                        )
                    )
                elif "artifact_id" in document.metadata:
                    produced = metadata_value(templates_by_id[template_id], "produces")
                    artifact_type = metadata_value(document, "artifact_type")
                    if produced != artifact_type:
                        findings.append(
                            Finding(
                                str(document.relative_path),
                                metadata_line(document, "source_template"),
                                f"source template {template_id} produces {produced}, not {artifact_type}",
                            )
                        )
        elif "artifact_id" in document.metadata and "source_template" in document.metadata:
            if not re.search(r"^## Migration note\s*$", document.text, re.MULTILINE):
                findings.append(
                    Finding(
                        str(document.relative_path),
                        metadata_line(document, "source_template"),
                        "null source_template requires a '## Migration note' section",
                    )
                )

        dependencies = metadata.get("depends_on", [])
        if isinstance(dependencies, list):
            for dependency in dependencies:
                if not dependency or EXTERNAL_SCHEME.match(dependency):
                    continue
                resolved = (document.path.parent / dependency).resolve()
                if not resolved.exists():
                    findings.append(
                        Finding(str(document.relative_path), metadata_line(document, "depends_on"), f"depends_on target does not exist: {dependency}")
                    )

    for artifact_id, document in artifacts_by_id.items():
        status = (metadata_value(document, "status") or "").lower()
        supersedes = document.metadata.get("supersedes")
        if isinstance(supersedes, list):
            for replaced_id in supersedes:
                if not isinstance(replaced_id, str) or not ID_PATTERN.fullmatch(replaced_id):
                    continue
                if replaced_id == artifact_id:
                    findings.append(
                        Finding(
                            str(document.relative_path),
                            metadata_line(document, "supersedes"),
                            "artifact cannot supersede itself",
                        )
                    )
                    continue
                replaced = artifacts_by_id.get(replaced_id)
                if replaced is None:
                    findings.append(
                        Finding(
                            str(document.relative_path),
                            metadata_line(document, "supersedes"),
                            f"supersedes target does not exist: {replaced_id}",
                        )
                    )
                    continue
                if status in EFFECTIVE_ARTIFACT_STATUSES:
                    if (metadata_value(replaced, "status") or "").lower() != "superseded":
                        findings.append(
                            Finding(
                                str(document.relative_path),
                                metadata_line(document, "supersedes"),
                                f"effective replacement requires {replaced_id} status superseded",
                            )
                        )
                    if metadata_value(replaced, "superseded_by") != artifact_id:
                        findings.append(
                            Finding(
                                str(document.relative_path),
                                metadata_line(document, "supersedes"),
                                f"supersession is not reciprocal: {replaced_id}.superseded_by must be {artifact_id}",
                            )
                        )

        replacement_id = metadata_value(document, "superseded_by")
        if replacement_id is None or not ID_PATTERN.fullmatch(replacement_id):
            continue
        if replacement_id == artifact_id:
            findings.append(
                Finding(
                    str(document.relative_path),
                    metadata_line(document, "superseded_by"),
                    "artifact cannot be superseded by itself",
                )
            )
            continue
        replacement = artifacts_by_id.get(replacement_id)
        if replacement is None:
            findings.append(
                Finding(
                    str(document.relative_path),
                    metadata_line(document, "superseded_by"),
                    f"superseded_by target does not exist: {replacement_id}",
                )
            )
            continue
        if status != "superseded":
            findings.append(
                Finding(
                    str(document.relative_path),
                    metadata_line(document, "status"),
                    "artifact with superseded_by must have status superseded",
                )
            )
        if (metadata_value(replacement, "status") or "").lower() not in EFFECTIVE_ARTIFACT_STATUSES:
            findings.append(
                Finding(
                    str(document.relative_path),
                    metadata_line(document, "superseded_by"),
                    f"superseded_by target {replacement_id} must be effective",
                )
            )
        replacement_supersedes = replacement.metadata.get("supersedes")
        if not isinstance(replacement_supersedes, list) or artifact_id not in replacement_supersedes:
            findings.append(
                Finding(
                    str(document.relative_path),
                    metadata_line(document, "superseded_by"),
                    f"supersession is not reciprocal: {replacement_id}.supersedes must include {artifact_id}",
                )
            )

    if strict_package:
        document_by_relative = {str(document.relative_path): document for document in documents}
        package_files = ("README.md", "MATURITY.md", "CHANGELOG.md")
        package_versions: dict[str, str | None] = {
            name: metadata_value(document_by_relative[name], "package_version")
            for name in package_files
            if name in document_by_relative
        }
        if set(package_versions) != set(package_files) or any(value is None for value in package_versions.values()):
            findings.append(Finding("README.md", 1, "README, MATURITY, and CHANGELOG must declare package_version"))
        elif len(set(package_versions.values())) != 1:
            findings.append(Finding("README.md", 1, f"package_version mismatch: {package_versions}"))

        catalog_path = root / "controls" / "core-controls.json"
        try:
            catalog_version = str(json.loads(catalog_path.read_text(encoding="utf-8")).get("catalog_version"))
        except (OSError, json.JSONDecodeError):
            catalog_version = None
        catalog_declarations: dict[str, str | None] = {}
        for name in ("README.md", "MATURITY.md", "08-scorecard-and-readiness-gates.md"):
            if name in document_by_relative:
                catalog_declarations[name] = metadata_value(document_by_relative[name], "control_catalog_version")
        if catalog_version is None or any(value != catalog_version for value in catalog_declarations.values()):
            findings.append(Finding("README.md", 1, f"control catalog version mismatch: json={catalog_version!r} docs={catalog_declarations}"))

        schema_document = document_by_relative.get("templates/README.md")
        schema_version = metadata_value(schema_document, "schema_version") if schema_document else None
        schema_declarations: dict[str, str | None] = {}
        for name in ("README.md", "MATURITY.md"):
            if name in document_by_relative:
                schema_declarations[name] = metadata_value(document_by_relative[name], "artifact_schema_version")
        if schema_version is None or any(value != schema_version for value in schema_declarations.values()):
            findings.append(Finding("templates/README.md", 1, f"artifact schema version mismatch: owner={schema_version!r} docs={schema_declarations}"))
        for document in documents:
            if "artifact_id" in document.metadata and metadata_value(document, "schema_version") != schema_version:
                findings.append(
                    Finding(str(document.relative_path), metadata_line(document, "schema_version"), f"artifact schema_version must be {schema_version}")
                )

    if not documents:
        findings.append(Finding(".", 1, "no Markdown documents found"))
    return findings


def github_slug(title: str) -> str:
    title = re.sub(r"<[^>]+>", "", title.strip()).lower()
    title = re.sub(r"\s+", "-", title)
    return re.sub(r"[^\w-]", "", title, flags=re.UNICODE)


def document_anchors(document: Document) -> set[str]:
    anchors: set[str] = set()
    seen: dict[str, int] = {}
    for line in document.lines:
        match = HEADING_PATTERN.match(line)
        if not match:
            continue
        base = github_slug(match.group("title"))
        occurrence = seen.get(base, 0)
        seen[base] = occurrence + 1
        anchors.add(base if occurrence == 0 else f"{base}-{occurrence}")
    return anchors


def normalize_link_target(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and ">" in raw:
        return raw[1 : raw.index(">")]
    return raw.split(maxsplit=1)[0]


def validate_links(documents: list[Document], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    anchors = {document.path.resolve(): document_anchors(document) for document in documents}

    for document in documents:
        for match in LINK_PATTERN.finditer(document.text):
            target = normalize_link_target(match.group("target"))
            if not target or EXTERNAL_SCHEME.match(target):
                continue
            line = document.text.count("\n", 0, match.start()) + 1
            path_part, separator, fragment = target.partition("#")
            resolved = (document.path.parent / (unquote(path_part) or document.path.name)).resolve()
            if not resolved.exists():
                findings.append(
                    Finding(str(document.relative_path), line, f"broken relative link: {target}")
                )
                continue
            if separator and resolved.suffix.lower() == ".md":
                expected = unquote(fragment)
                if expected and expected not in anchors.get(resolved, set()):
                    findings.append(
                        Finding(str(document.relative_path), line, f"broken Markdown anchor: {target}")
                    )
    return findings


def validate_text_hygiene(documents: list[Document]) -> list[Finding]:
    findings: list[Finding] = []
    for document in documents:
        if document.text and not document.text.endswith("\n"):
            findings.append(Finding(str(document.relative_path), len(document.lines), "file must end with one newline"))
        open_fence: tuple[str, int, int] | None = None
        for line_number, line in enumerate(document.lines, 1):
            if line != line.rstrip():
                findings.append(Finding(str(document.relative_path), line_number, "trailing whitespace"))
            if "\t" in line:
                findings.append(Finding(str(document.relative_path), line_number, "tab character; use spaces in Markdown"))
            match = FENCE_PATTERN.match(line)
            if not match:
                continue
            marker = match.group("marker")
            marker_char = marker[0]
            marker_length = len(marker)
            if open_fence is None:
                open_fence = (marker_char, marker_length, line_number)
            elif marker_char == open_fence[0] and marker_length >= open_fence[1]:
                open_fence = None
        if open_fence is not None:
            findings.append(
                Finding(str(document.relative_path), open_fence[2], "unclosed fenced code block")
            )
    return findings


def validate_rules(documents: list[Document]) -> list[Finding]:
    findings: list[Finding] = []
    definitions: dict[str, tuple[Path, int]] = {}
    references: list[tuple[str, Path, int]] = []

    for document in documents:
        for line_number, line in enumerate(document.lines, 1):
            definition = RULE_DEFINITION.match(line)
            if definition:
                rule = definition.group("rule")
                if rule in definitions:
                    previous, previous_line = definitions[rule]
                    findings.append(
                        Finding(str(document.relative_path), line_number, f"duplicate rule '{rule}', first defined at {previous}:{previous_line}")
                    )
                else:
                    definitions[rule] = (document.relative_path, line_number)
            for rule in re.findall(r"`(" + RULE_PATTERN.pattern + r")`", line):
                if not rule.startswith(("CTL-", "GATE-")):
                    references.append((rule, document.relative_path, line_number))

    for rule, path, line in references:
        if rule not in definitions:
            findings.append(Finding(str(path), line, f"undefined rule reference '{rule}'"))
    return findings


def validate_control_catalog(root: Path, documents: list[Document]) -> tuple[list[Finding], int]:
    findings: list[Finding] = []
    path = root / "controls" / "core-controls.json"
    if not path.exists():
        return [Finding("controls/core-controls.json", 1, "missing canonical control catalog")], 0
    try:
        catalog = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [Finding("controls/core-controls.json", 1, f"invalid JSON: {error}")], 0
    if not isinstance(catalog, dict):
        return [Finding("controls/core-controls.json", 1, "catalog root must be an object")], 0
    if not isinstance(catalog.get("catalog_version"), str):
        findings.append(Finding("controls/core-controls.json", 1, "catalog_version must be a string"))

    rule_definitions: set[str] = set()
    for document in documents:
        for line in document.lines:
            match = RULE_DEFINITION.match(line)
            if match:
                rule_definitions.add(match.group("rule"))

    dimensions = catalog.get("dimensions")
    dimension_ids: set[int] = set()
    if not isinstance(dimensions, list):
        findings.append(Finding("controls/core-controls.json", 1, "dimensions must be an array"))
    else:
        for row in dimensions:
            if not isinstance(row, dict) or not isinstance(row.get("id"), int) or not isinstance(row.get("name"), str):
                findings.append(Finding("controls/core-controls.json", 1, "each dimension requires integer id and name"))
                continue
            dimension_ids.add(row["id"])
        if dimension_ids != set(range(1, 11)):
            findings.append(Finding("controls/core-controls.json", 1, "dimensions must contain IDs 1 through 10 exactly"))

    controls = catalog.get("controls")
    control_ids: set[str] = set()
    control_text: dict[str, str] = {}
    dimension_counts: dict[int, int] = {index: 0 for index in range(1, 11)}
    dimension_baseline_counts: dict[int, int] = {index: 0 for index in range(1, 11)}
    conditional_control_ids: set[str] = set()
    if not isinstance(controls, list):
        findings.append(Finding("controls/core-controls.json", 1, "controls must be an array"))
        controls = []
    for row in controls:
        if not isinstance(row, dict):
            findings.append(Finding("controls/core-controls.json", 1, "each control must be an object"))
            continue
        identifier = row.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"CTL-[A-Z0-9]+(?:-[A-Z0-9]+)+-\d+", identifier):
            findings.append(Finding("controls/core-controls.json", 1, f"invalid control id: {identifier!r}"))
        elif identifier in control_ids:
            findings.append(Finding("controls/core-controls.json", 1, f"duplicate control id: {identifier}"))
        else:
            control_ids.add(identifier)
            if isinstance(row.get("text"), str):
                control_text[identifier] = row["text"].strip()
        dimension = row.get("dimension")
        if not isinstance(dimension, int) or dimension not in range(1, 11):
            findings.append(Finding("controls/core-controls.json", 1, f"{identifier}: invalid dimension"))
        else:
            dimension_counts[dimension] += 1
        for field in ("text", "source_rule", "critical_when"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                findings.append(Finding("controls/core-controls.json", 1, f"{identifier}: missing {field}"))
        if not isinstance(row.get("baseline"), bool):
            findings.append(Finding("controls/core-controls.json", 1, f"{identifier}: baseline must be boolean"))
        elif isinstance(dimension, int) and dimension in range(1, 11):
            if row["baseline"]:
                dimension_baseline_counts[dimension] += 1
            elif isinstance(identifier, str):
                conditional_control_ids.add(identifier)
        source_rule = row.get("source_rule")
        if isinstance(source_rule, str) and source_rule not in rule_definitions:
            findings.append(Finding("controls/core-controls.json", 1, f"{identifier}: undefined source_rule '{source_rule}'"))
    for dimension, count in dimension_counts.items():
        if count != 4:
            findings.append(Finding("controls/core-controls.json", 1, f"dimension {dimension} must contain exactly 4 core controls, found {count}"))
        if dimension_baseline_counts[dimension] < 1:
            findings.append(Finding("controls/core-controls.json", 1, f"dimension {dimension} must retain at least one baseline control"))

    documented_controls: dict[str, str] = {}
    documented_conditionals: set[str] = set()
    for document in documents:
        if document.relative_path.name != "08-scorecard-and-readiness-gates.md":
            continue
        for line in document.lines:
            match = CONTROL_TABLE_ROW.match(line)
            if match:
                documented_controls[match.group("id")] = match.group("text").strip()
            if "The conditional IDs in catalog" in line:
                documented_conditionals.update(re.findall(r"`(CTL-[A-Z0-9]+(?:-[A-Z0-9]+)+-\d+)`", line))
    if set(documented_controls) != control_ids:
        missing = sorted(control_ids - set(documented_controls))
        extra = sorted(set(documented_controls) - control_ids)
        if missing:
            findings.append(Finding("08-scorecard-and-readiness-gates.md", 1, "control table missing IDs: " + ", ".join(missing)))
        if extra:
            findings.append(Finding("08-scorecard-and-readiness-gates.md", 1, "control table has unknown IDs: " + ", ".join(extra)))
    for identifier in sorted(control_ids & set(documented_controls)):
        if documented_controls[identifier] != control_text.get(identifier):
            findings.append(
                Finding(
                    "08-scorecard-and-readiness-gates.md",
                    1,
                    f"control outcome differs from catalog for {identifier}",
                )
            )
    if documented_conditionals != conditional_control_ids:
        findings.append(
            Finding(
                "08-scorecard-and-readiness-gates.md",
                1,
                "documented conditional control IDs differ from catalog: "
                f"docs={sorted(documented_conditionals)} catalog={sorted(conditional_control_ids)}",
            )
        )

    document_by_path = {document.path.resolve(): document for document in documents}
    gates = catalog.get("gates")
    gate_ids: set[str] = set()
    if not isinstance(gates, list):
        findings.append(Finding("controls/core-controls.json", 1, "gates must be an array"))
        gates = []
    for row in gates:
        if not isinstance(row, dict):
            findings.append(Finding("controls/core-controls.json", 1, "each gate must be an object"))
            continue
        identifier = row.get("id")
        if not isinstance(identifier, str) or not re.fullmatch(r"GATE-[A-Z0-9]+(?:-[A-Z0-9]+)*-\d+", identifier):
            findings.append(Finding("controls/core-controls.json", 1, f"invalid gate id: {identifier!r}"))
        elif identifier in gate_ids:
            findings.append(Finding("controls/core-controls.json", 1, f"duplicate gate id: {identifier}"))
        else:
            gate_ids.add(identifier)
        source = row.get("source")
        if not isinstance(row.get("name"), str) or not isinstance(source, str):
            findings.append(Finding("controls/core-controls.json", 1, f"{identifier}: gate requires name and source"))
            continue
        source_path, separator, source_anchor = source.partition("#")
        resolved = (root / source_path).resolve()
        document = document_by_path.get(resolved)
        if not document:
            findings.append(Finding("controls/core-controls.json", 1, f"{identifier}: missing gate source {source_path}"))
        elif not separator or source_anchor not in document_anchors(document):
            findings.append(Finding("controls/core-controls.json", 1, f"{identifier}: invalid gate source anchor {source}"))
    if gate_ids != {"GATE-GREENFIELD-01", "GATE-EVOLUTION-01", "GATE-REFACTOR-01", "GATE-RELEASE-01"}:
        findings.append(Finding("controls/core-controls.json", 1, "catalog must define the four canonical readiness gates"))
    return findings, len(controls)


def validate_evidence_manifest_schema(root: Path) -> list[Finding]:
    relative = Path("controls/evidence-manifest.schema.json")
    path = root / relative
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [Finding(str(relative), 1, f"invalid or missing evidence manifest schema: {error}")]
    findings: list[Finding] = []
    if not isinstance(schema, dict) or schema.get("type") != "object":
        findings.append(Finding(str(relative), 1, "evidence manifest schema root must be an object schema"))
        return findings
    required = schema.get("required")
    expected_required = {
        "manifest_id",
        "manifest_version",
        "assessment_id",
        "source_revision",
        "target",
        "environment",
        "records",
    }
    if not isinstance(required, list) or not expected_required.issubset(required):
        findings.append(Finding(str(relative), 1, "evidence manifest schema is missing required identity fields"))
    properties = schema.get("properties")
    manifest_version_schema = properties.get("manifest_version") if isinstance(properties, dict) else None
    if not isinstance(manifest_version_schema, dict) or manifest_version_schema.get("const") != "1.0.0":
        findings.append(Finding(str(relative), 1, "evidence manifest schema must pin manifest_version 1.0.0"))
    records_schema = properties.get("records") if isinstance(properties, dict) else None
    record_schema = records_schema.get("items") if isinstance(records_schema, dict) else None
    record_required = record_schema.get("required") if isinstance(record_schema, dict) else None
    expected_record = {"reference", "artifact", "sha256", "result", "producer", "observed_at"}
    if not isinstance(record_required, list) or not expected_record.issubset(record_required):
        findings.append(Finding(str(relative), 1, "evidence manifest record schema is incomplete"))
    return findings


def validate_core_neutrality(documents: list[Document]) -> list[Finding]:
    findings: list[Finding] = []
    for document in documents:
        if document.relative_path.parent != Path(".") or not NUMERIC_GUIDE.fullmatch(document.relative_path.name):
            continue
        lowered = document.text.lower()
        for term in CORE_FORBIDDEN_STACK_TERMS:
            match = re.search(r"(?<![\w])" + re.escape(term) + r"(?![\w])", lowered)
            if match:
                line = lowered[: match.start()].count("\n") + 1
                findings.append(
                    Finding(str(document.relative_path), line, f"stack-specific term '{term}' leaked into the neutral core")
                )
    return findings


def validate_router_budgets(documents: list[Document]) -> list[Finding]:
    findings: list[Finding] = []
    for document in documents:
        in_router = False
        header_seen = False
        required_column: int | None = None
        for line_number, line in enumerate(document.lines, 1):
            if line.startswith("## "):
                in_router = line.strip().lower() == "## task router"
                header_seen = False
                required_column = None
                continue
            if not in_router or not line.startswith("|"):
                continue
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if not header_seen:
                header_seen = True
                for index, cell in enumerate(cells):
                    if cell.lower() == "required reads":
                        required_column = index
                continue
            if set("".join(cells)) <= {"-", ":"} or required_column is None or required_column >= len(cells):
                continue
            required = cells[required_column]
            numeric = re.findall(r"(?<![A-Za-z0-9])(?:0[1-9]|1[0-9]|2[0-9])(?![A-Za-z0-9])", required)
            alternatives = re.findall(r"\b(?:0[1-9]|1[0-9]|2[0-9])\s+or\s+(?:0[1-9]|1[0-9]|2[0-9])\b", required)
            named = sum(
                1
                for token in ("README", "MATURITY", "Companion")
                if token in required
            )
            count = len(numeric) - len(alternatives) + named
            if count > 4:
                findings.append(
                    Finding(str(document.relative_path), line_number, f"task-router required bundle names {count} guides; maximum is 4")
                )
    return findings


def validate_ci_contract(root: Path) -> list[Finding]:
    relative = Path(".github/workflows/docs-quality.yml")
    path = root / relative
    if not path.exists():
        return [Finding(str(relative), 1, "missing docs-quality CI workflow")]
    text = path.read_text(encoding="utf-8")
    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^\s*-\s+uses:\s+([^\s#]+)", line)
        if not match:
            continue
        reference = match.group(1)
        if reference.startswith("./"):
            continue
        _action, separator, revision = reference.rpartition("@")
        if not separator or not re.fullmatch(r"[0-9a-f]{40}", revision):
            findings.append(
                Finding(str(relative), line_number, f"external action must be pinned to a 40-character commit SHA: {reference}")
            )
    required_fragments = {
        "contents: read": "workflow must use read-only contents permission",
        "persist-credentials: false": "checkout must not persist credentials",
        '"docs/blueprint/controls/**"': "workflow path filters must include blueprint controls",
        '"docs/blueprint/reference-app-blueprint/**/*.json"': "workflow path filters must include reference assessment JSON",
        '"docs/presets/**"': "workflow path filters must include preset contracts and packages",
        "PYTHONPATH=docs/blueprint python3 -m unittest discover -s docs/blueprint/scripts -p 'test_*.py'": "workflow must run all script unit tests",
        "python3 docs/blueprint/scripts/validate_docs.py docs/blueprint --repo-root .": "workflow must run the canonical docs validator",
        "python3 docs/blueprint/scripts/score_readiness.py docs/blueprint/reference-app-blueprint/examples/basic-web-artifacts/readiness.json --json --expect not-ready": "workflow must pin the fail-closed reference assessment result",
    }
    for fragment, message in required_fragments.items():
        if fragment not in text:
            findings.append(Finding(str(relative), 1, message))
    return findings


def validate_repository(
    root: Path,
    *,
    require_catalog: bool = True,
    repo_root: Path | None = None,
) -> tuple[list[Finding], dict[str, int]]:
    root = root.resolve()
    repo_root = (repo_root or root).resolve()
    documents, findings = load_documents(root)
    findings.extend(validate_metadata(documents, root, strict_package=require_catalog))
    findings.extend(validate_links(documents, root))
    findings.extend(validate_text_hygiene(documents))
    findings.extend(validate_rules(documents))
    control_count = 0
    if require_catalog:
        catalog_findings, control_count = validate_control_catalog(root, documents)
        findings.extend(catalog_findings)
        findings.extend(validate_evidence_manifest_schema(root))
    findings.extend(validate_core_neutrality(documents))
    findings.extend(validate_router_budgets(documents))
    if require_catalog:
        findings.extend(validate_ci_contract(repo_root))
    summary = {
        "documents": len(documents),
        "guides": sum(1 for document in documents if "guide_id" in document.metadata),
        "templates": sum(1 for document in documents if "template_id" in document.metadata),
        "artifacts": sum(1 for document in documents if "artifact_id" in document.metadata),
        "controls": control_count,
        "findings": len(findings),
    }
    return sorted(set(findings)), summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", type=Path)
    parser.add_argument(
        "--repo-root",
        type=Path,
        help="Repository root containing .github; defaults to the documentation package root.",
    )
    args = parser.parse_args(argv)
    findings, summary = validate_repository(args.root, repo_root=args.repo_root)

    for finding in findings:
        print(finding.render())
    print(
        "docs-quality: "
        + " ".join(f"{key}={value}" for key, value in summary.items())
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
