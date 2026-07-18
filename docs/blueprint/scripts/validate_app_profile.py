#!/usr/bin/env python3
"""Validate a stack-neutral application-profile authority manifest.

The validator deliberately uses only the Python standard library.  It checks
the cross-file contracts that JSON Schema cannot express: safe repository
paths, SHA-256 locks, Markdown artifact metadata and registry rows, skill
frontmatter, pattern and command registries, and revision-bound evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any


SHA256 = re.compile(r"^[0-9a-f]{64}$")
KEBAB_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ARTIFACT_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+){2,}$")
CONTENT_REVISION = re.compile(
    r"^(?:[0-9a-f]{40}|[0-9a-f]{64}|sha256:[0-9a-f]{64})$"
)
SOURCE_REVISION = CONTENT_REVISION
ENVIRONMENT_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
MARKDOWN_LINK = re.compile(r"^\[[^\]]*\]\((?P<target>[^)]+)\)$")
RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)

SCHEMA_VERSION = "1.0.0"
BLUEPRINT_VERSION = "0.12.0"
FUTURE_CLOCK_SKEW = timedelta(minutes=5)
REQUIRED_SKILLS = {
    "analyze-request",
    "lib",
    "shared",
    "feature",
    "app",
    "new-pattern",
    "ui",
}
BASELINE_COMMAND_LANES = {
    "install",
    "doctor",
    "test",
    "check",
    "build",
    "start-smoke",
}
FORBIDDEN_EXTERNAL_EFFECT_LANES = {"publish", "release", "deploy"}
AUDIT_NEGATIVE_EVAL_KINDS = {
    "audit-immutable-range",
    "audit-checkpoint",
}
PUBLISH_NEGATIVE_EVAL_KINDS = {
    "publish-topology",
    "publish-conflict",
    "publish-final-revision",
}
DUAL_VERDICTS = {"PASS", "FAIL", "BLOCKED", "NOT_EXECUTED"}
NEGATIVE_EVAL_KINDS = AUDIT_NEGATIVE_EVAL_KINDS | PUBLISH_NEGATIVE_EVAL_KINDS
NEGATIVE_DISPOSITIONS = {"BLOCKED", "REFUSED", "TASK_REROUTED"}
PROFILE_FIELDS = {
    "schema_version",
    "profile_id",
    "blueprint_version",
    "blueprint_revision",
    "source_revision",
    "artifact_registry",
    "artifact_closure",
    "system_profile",
    "stack_profile",
    "skills",
    "pattern_catalog",
    "verification_commands",
    "clean_room_evidence",
    "guidance_evidence",
    "freshness_policy",
}
OPTIONAL_PROFILE_FIELDS = {"$schema"}
REFERENCE_FIELDS = {"path", "sha256"}
ARTIFACT_REFERENCE_FIELDS = {"id", "status", "path", "sha256"}
SKILL_REFERENCE_FIELDS = {"name", "path", "sha256"}
GUIDANCE_REFERENCE_FIELDS = {
    "id",
    "current_revision",
    "path",
    "sha256",
    "skill_evals",
}
FRESHNESS_POLICY_FIELDS = {"stale_after_days"}
PATTERN_FIELDS = {
    "id",
    "intent",
    "primary_owner",
    "support_skills",
    "applicability",
    "public_contract",
    "allowed_dependencies",
    "forbidden_dependencies",
    "exemplar",
    "verifier",
    "verifier_argv",
    "fixtures",
    "verification_evidence",
}
WINDOWS_RESERVED = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}


@dataclass(frozen=True, order=True)
class Finding:
    path: str
    line: int
    message: str

    def render(self) -> str:
        return f"{self.path}:{self.line}: {self.message}"


class AppProfileValidator:
    """Fail-closed validator for one application-profile manifest."""

    def __init__(
        self,
        profile_path: Path,
        repo_root: Path,
        *,
        expected_revision: str | None = None,
        expected_blueprint_revision: str | None = None,
    ):
        self.repo_root_input = repo_root
        self.repo_root_lexical = Path(os.path.abspath(repo_root))
        self.repo_root = repo_root.resolve()
        self.profile_input = profile_path
        self.profile_path_lexical = Path(os.path.abspath(
            profile_path
            if profile_path.is_absolute()
            else self.repo_root_lexical / profile_path
        ))
        self.expected_revision = expected_revision
        self.expected_blueprint_revision = expected_blueprint_revision
        self.findings: list[Finding] = []

    def display(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.repo_root))
        except (OSError, ValueError):
            return str(path)

    def add(self, path: Path, message: str, line: int = 1) -> None:
        self.findings.append(Finding(self.display(path), line, message))

    @staticmethod
    def is_safe_relative(raw: Any, *, allow_dot: bool = False) -> bool:
        if raw == "." and allow_dot:
            return True
        if (
            not isinstance(raw, str)
            or not raw.strip()
            or len(raw) > 512
            or raw != raw.strip()
            or "\\" in raw
            or any(ord(character) < 32 or ord(character) == 127 for character in raw)
        ):
            return False
        if raw.startswith("/") or re.match(r"^[A-Za-z]:", raw) or ":" in raw:
            return False
        parts = raw.split("/")
        for part in parts:
            if part in {"", ".", ".."} or part.endswith((".", " ")):
                return False
            if part.split(".", 1)[0].casefold() in WINDOWS_RESERVED:
                return False
        return True

    @staticmethod
    def valid_kebab_id(raw: Any) -> bool:
        return isinstance(raw, str) and len(raw) <= 96 and bool(KEBAB_ID.fullmatch(raw))

    @staticmethod
    def valid_artifact_id(raw: Any) -> bool:
        return isinstance(raw, str) and len(raw) <= 96 and bool(ARTIFACT_ID.fullmatch(raw))

    def safe_path(
        self,
        raw: Any,
        owner: Path,
        label: str,
        *,
        kind: str | None = None,
        allow_dot: bool = False,
    ) -> Path | None:
        if not self.is_safe_relative(raw, allow_dot=allow_dot):
            self.add(owner, f"{label} must be a portable repository-relative path")
            return None
        assert isinstance(raw, str)
        relative = Path() if raw == "." else Path(raw)
        lexical = self.repo_root
        try:
            for part in relative.parts:
                lexical /= part
                if lexical.is_symlink():
                    self.add(owner, f"{label} must not traverse a symbolic link")
                    return None
            candidate = lexical.resolve()
            candidate.relative_to(self.repo_root)
        except (OSError, ValueError) as error:
            self.add(owner, f"{label} escapes the repository or cannot be resolved: {error}")
            return None
        try:
            exists = candidate.exists()
            is_file = candidate.is_file()
            is_dir = candidate.is_dir()
        except OSError as error:
            self.add(owner, f"{label} cannot be inspected: {error}")
            return None
        if not exists:
            self.add(owner, f"{label} does not exist: {raw}")
            return None
        if kind == "file" and not is_file:
            self.add(owner, f"{label} must reference a file: {raw}")
            return None
        if kind == "dir" and not is_dir:
            self.add(owner, f"{label} must reference a directory: {raw}")
            return None
        return candidate

    @staticmethod
    def digest_tree(target: Path) -> str:
        """Return a deterministic, domain-separated skill-package digest."""

        digest = hashlib.sha256()
        digest.update(b"app-profile-skill-tree-v1\0")
        entries = sorted(
            target.rglob("*"),
            key=lambda item: item.relative_to(target).as_posix().encode("utf-8"),
        )
        for path in entries:
            if path.is_symlink():
                raise ValueError(
                    "directory digest does not permit symbolic links: "
                    f"{path.relative_to(target).as_posix()}"
                )
            if not path.is_file():
                continue
            relative = path.relative_to(target).as_posix().encode("utf-8")
            content = path.read_bytes()
            digest.update(len(relative).to_bytes(8, "big"))
            digest.update(relative)
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
        return digest.hexdigest()

    @staticmethod
    def digest_path(target: Path) -> str:
        if target.is_file():
            return hashlib.sha256(target.read_bytes()).hexdigest()
        return AppProfileValidator.digest_tree(target)

    def check_digest(
        self,
        owner: Path,
        target: Path,
        raw_digest: Any,
        label: str,
    ) -> None:
        if not isinstance(raw_digest, str) or not SHA256.fullmatch(raw_digest):
            self.add(owner, f"{label} must be a lowercase full SHA-256 digest")
            return
        try:
            actual = self.digest_path(target)
        except (OSError, ValueError) as error:
            self.add(owner, f"cannot compute {label}: {error}")
            return
        if actual != raw_digest:
            self.add(owner, f"stale {label}: expected {actual}")

    def load_json(self, path: Path, label: str) -> Any | None:
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self.add(path, f"missing {label}")
        except UnicodeDecodeError as error:
            self.add(path, f"{label} is not UTF-8: {error}")
        except json.JSONDecodeError as error:
            self.add(path, f"invalid {label} JSON: {error.msg}", error.lineno)
        except OSError as error:
            self.add(path, f"cannot read {label}: {error}")
        return None

    def check_exact_fields(
        self,
        value: Any,
        expected: set[str],
        owner: Path,
        label: str,
    ) -> dict[str, Any] | None:
        if not isinstance(value, dict):
            self.add(owner, f"{label} must be a JSON object")
            return None
        for field in sorted(expected - set(value)):
            self.add(owner, f"{label} is missing required field: {field}")
        for field in sorted(set(value) - expected):
            self.add(owner, f"{label} has unknown field: {field}")
        return value

    @staticmethod
    def parse_frontmatter(text: str) -> dict[str, str] | None:
        lines = text.splitlines()
        if not lines or lines[0].strip() != "---":
            return None
        values: dict[str, str] = {}
        for line in lines[1:]:
            if line.strip() == "---":
                return values
            match = re.match(r"^([A-Za-z_][A-Za-z0-9_-]*):\s*(.*?)\s*$", line)
            if not match:
                continue
            value = match.group(2)
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            values[match.group(1)] = value
        return None

    def read_frontmatter(self, path: Path, label: str) -> dict[str, str] | None:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as error:
            self.add(path, f"cannot read {label}: {error}")
            return None
        metadata = self.parse_frontmatter(text)
        if metadata is None:
            self.add(path, f"{label} must start with closed YAML frontmatter")
        return metadata

    def validate_profile_location(self) -> Path | None:
        if not self.repo_root.exists() or not self.repo_root.is_dir():
            self.add(self.repo_root_input, "repo root must be an existing directory")
            return None
        try:
            relative = self.profile_path_lexical.relative_to(self.repo_root_lexical)
        except ValueError:
            self.add(
                self.profile_path_lexical,
                "app profile must be inside the explicit repo root",
            )
            return None
        lexical = self.repo_root
        try:
            for part in relative.parts:
                lexical /= part
                if lexical.is_symlink():
                    self.add(
                        self.profile_path_lexical,
                        "app profile must not traverse a symbolic link",
                    )
                    return None
        except OSError as error:
            self.add(
                self.profile_path_lexical,
                f"app profile cannot be inspected: {error}",
            )
            return None
        if not lexical.exists():
            self.add(self.profile_path_lexical, "app profile does not exist")
            return None
        if not lexical.is_file():
            self.add(self.profile_path_lexical, "app profile must be a regular file")
            return None
        return lexical

    def validate(self) -> list[Finding]:
        profile_path = self.validate_profile_location()
        if profile_path is None:
            return sorted(set(self.findings))
        profile = self.load_json(profile_path, "app profile")
        if not isinstance(profile, dict):
            if profile is not None:
                self.add(profile_path, "app profile must be a JSON object")
            return sorted(set(self.findings))

        preset_lock = self.repo_root / "docs/governance/preset-lock.json"
        if os.path.lexists(preset_lock):
            self.add(
                profile_path,
                "app-profile and canonical preset-lock authorities cannot coexist",
            )

        present = set(profile)
        for field in sorted(PROFILE_FIELDS - present):
            self.add(profile_path, f"app profile is missing required field: {field}")
        for field in sorted(present - PROFILE_FIELDS - OPTIONAL_PROFILE_FIELDS):
            self.add(profile_path, f"app profile has unknown field: {field}")

        if profile.get("schema_version") != SCHEMA_VERSION:
            self.add(profile_path, f"schema_version must be {SCHEMA_VERSION}")
        if not self.valid_kebab_id(profile.get("profile_id")):
            self.add(profile_path, "profile_id must be a kebab-case identifier")
        if profile.get("blueprint_version") != BLUEPRINT_VERSION:
            self.add(profile_path, f"blueprint_version must equal {BLUEPRINT_VERSION}")
        blueprint_revision = profile.get("blueprint_revision")
        if (
            not isinstance(blueprint_revision, str)
            or not CONTENT_REVISION.fullmatch(blueprint_revision)
        ):
            self.add(
                profile_path,
                "blueprint_revision must be a full immutable content revision",
            )
        source_revision = profile.get("source_revision")
        if (
            not isinstance(source_revision, str)
            or not SOURCE_REVISION.fullmatch(source_revision)
        ):
            self.add(
                profile_path,
                "source_revision must be an immutable source revision, not a movable selector",
            )
        if "$schema" in profile and (
            not isinstance(profile["$schema"], str) or not profile["$schema"].strip()
        ):
            self.add(profile_path, "$schema must be a nonempty string")

        if self.expected_revision is None:
            self.add(
                profile_path,
                "expected revision is required to qualify an effective app profile",
            )
        elif not SOURCE_REVISION.fullmatch(self.expected_revision):
            self.add(
                profile_path,
                "expected revision must be an immutable source revision, not a movable selector",
            )
        elif profile.get("source_revision") != self.expected_revision:
                self.add(
                    profile_path,
                    "source_revision does not match expected revision "
                    f"{self.expected_revision}",
                )

        if self.expected_blueprint_revision is None:
            self.add(
                profile_path,
                "expected blueprint revision is required to qualify an effective app profile",
            )
        elif not CONTENT_REVISION.fullmatch(self.expected_blueprint_revision):
            self.add(
                profile_path,
                "expected blueprint revision must be a full immutable content revision",
            )
        elif profile.get("blueprint_revision") != self.expected_blueprint_revision:
            self.add(
                profile_path,
                "blueprint_revision does not match expected blueprint revision "
                f"{self.expected_blueprint_revision}",
            )

        freshness_days = self.validate_freshness_policy(
            profile.get("freshness_policy"), profile_path
        )
        authority_input_digests = self.profile_input_digests(profile)

        artifact_paths: dict[str, Path] = {}
        artifact_records: dict[str, dict[str, Any]] = {}
        for field, artifact_type, status in (
            ("artifact_registry", "artifact-registry", "active"),
            ("system_profile", "system-profile", "active"),
            ("stack_profile", "stack-profile", "accepted"),
        ):
            record, path = self.validate_artifact_reference(
                profile.get(field), profile_path, field, artifact_type, status
            )
            if record is not None:
                artifact_records[field] = record
            if path is not None:
                artifact_paths[field] = path

        registry_path = artifact_paths.get("artifact_registry")
        if registry_path is not None:
            registry_rows = self.validate_registry(
                registry_path,
                artifact_records,
            )
            self.validate_artifact_closure(
                profile.get("artifact_closure"),
                profile_path,
                registry_path,
                registry_rows or [],
                artifact_records,
            )

        self.validate_skills(profile.get("skills"), profile_path)

        pattern_path = self.validate_file_reference(
            profile.get("pattern_catalog"), profile_path, "pattern_catalog"
        )
        if pattern_path is not None:
            self.validate_pattern_catalog(
                pattern_path,
                profile.get("skills"),
                profile.get("source_revision"),
                authority_input_digests,
                freshness_days,
            )

        command_reference = profile.get("verification_commands")
        command_path = self.validate_file_reference(
            command_reference,
            profile_path,
            "verification_commands",
        )
        command_registry: dict[str, dict[str, Any]] = {}
        if command_path is not None:
            command_registry = self.validate_command_registry(command_path)

        clean_room_path = self.validate_file_reference(
            profile.get("clean_room_evidence"),
            profile_path,
            "clean_room_evidence",
        )
        if clean_room_path is not None:
            command_digest = (
                command_reference.get("sha256")
                if isinstance(command_reference, dict)
                else None
            )
            self.validate_clean_room_evidence(
                clean_room_path,
                profile.get("source_revision"),
                command_digest,
                command_registry,
                self.evidence_authority_inputs(authority_input_digests),
                freshness_days,
            )

        self.validate_guidance_evidence(
            profile.get("guidance_evidence"),
            profile.get("source_revision"),
            profile.get("skills"),
            authority_input_digests,
            freshness_days,
            profile_path,
        )
        return sorted(set(self.findings))

    def validate_artifact_reference(
        self,
        raw: Any,
        owner: Path,
        label: str,
        artifact_type: str,
        required_status: str,
    ) -> tuple[dict[str, Any] | None, Path | None]:
        record = self.check_exact_fields(
            raw, ARTIFACT_REFERENCE_FIELDS, owner, label
        )
        if record is None:
            return None, None
        artifact_id = record.get("id")
        if not self.valid_artifact_id(artifact_id):
            self.add(owner, f"{label}.id must be a stable artifact ID")
        if record.get("status") != required_status:
            self.add(owner, f"{label}.status must be {required_status}")
        path = self.safe_path(record.get("path"), owner, f"{label}.path", kind="file")
        if path is None:
            return record, None
        self.check_digest(owner, path, record.get("sha256"), f"{label}.sha256")
        metadata = self.read_frontmatter(path, label)
        if metadata is not None:
            if metadata.get("artifact_id") != artifact_id:
                self.add(path, f"artifact_id does not match {label}.id")
            if metadata.get("artifact_type") != artifact_type:
                self.add(path, f"artifact_type must be {artifact_type}")
            if metadata.get("status") != required_status:
                self.add(path, f"status does not match {label}.status")
        return record, path

    @staticmethod
    def split_markdown_row(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    @staticmethod
    def normalize_heading(value: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()

    @staticmethod
    def is_separator_row(cells: list[str]) -> bool:
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)

    def parse_registry_rows(self, path: Path) -> list[dict[str, str]] | None:
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError) as error:
            self.add(path, f"cannot read artifact registry: {error}")
            return None
        aliases = {
            "artifact id": "id",
            "type": "type",
            "status": "status",
            "path evidence locator": "path",
        }
        for index, line in enumerate(lines[:-1]):
            if "|" not in line or "|" not in lines[index + 1]:
                continue
            headings = [self.normalize_heading(cell) for cell in self.split_markdown_row(line)]
            separator = self.split_markdown_row(lines[index + 1])
            if not self.is_separator_row(separator):
                continue
            if not set(aliases).issubset(set(headings)):
                continue
            positions = {aliases[name]: headings.index(name) for name in aliases}
            rows: list[dict[str, str]] = []
            for row_line in lines[index + 2 :]:
                if not row_line.strip() or "|" not in row_line:
                    break
                cells = self.split_markdown_row(row_line)
                if len(cells) != len(headings):
                    self.add(path, "artifact registry contains a malformed table row")
                    continue
                rows.append({key: cells[position] for key, position in positions.items()})
            return rows
        self.add(
            path,
            "artifact registry is missing the Artifact ID/Type/Status/Path evidence table",
        )
        return None

    @staticmethod
    def clean_locator(raw: str) -> str:
        value = raw.strip()
        while len(value) >= 2 and value.startswith("`") and value.endswith("`"):
            value = value[1:-1].strip()
        match = MARKDOWN_LINK.fullmatch(value)
        if match:
            value = match.group("target").strip()
        return value

    def locator_matches(self, registry: Path, raw: str, expected: str) -> bool:
        locator = self.clean_locator(raw)
        if not self.is_safe_relative(locator):
            return False
        direct = PurePosixPath(locator).as_posix()
        registry_relative = (
            PurePosixPath(registry.parent.relative_to(self.repo_root).as_posix())
            / PurePosixPath(locator)
        ).as_posix()
        return expected in {direct, registry_relative}

    def validate_registry(
        self,
        registry_path: Path,
        records: dict[str, dict[str, Any]],
    ) -> list[dict[str, str]] | None:
        rows = self.parse_registry_rows(registry_path)
        if rows is None:
            return None
        by_id: dict[str, list[dict[str, str]]] = {}
        for row in rows:
            artifact_id = row["id"].strip("`")
            by_id.setdefault(artifact_id, []).append(row)
        for field, artifact_type, status in (
            ("artifact_registry", "artifact-registry", "active"),
            ("system_profile", "system-profile", "active"),
            ("stack_profile", "stack-profile", "accepted"),
        ):
            record = records.get(field)
            if record is None or not isinstance(record.get("id"), str):
                continue
            artifact_id = record["id"]
            matching = by_id.get(artifact_id, [])
            if not matching:
                self.add(registry_path, f"artifact registry is missing row for {artifact_id}")
                continue
            if len(matching) != 1:
                self.add(registry_path, f"artifact registry has duplicate rows for {artifact_id}")
                continue
            row = matching[0]
            if row["type"].strip("`") != artifact_type:
                self.add(
                    registry_path,
                    f"artifact registry type contradicts {field}: {artifact_id}",
                )
            if row["status"].strip("`") != status:
                self.add(
                    registry_path,
                    f"artifact registry status contradicts {field}: {artifact_id}",
                )
            expected_path = record.get("path")
            if isinstance(expected_path, str) and not self.locator_matches(
                registry_path, row["path"], expected_path
            ):
                self.add(
                    registry_path,
                    f"artifact registry path contradicts {field}: {artifact_id}",
                )
        return rows

    def validate_artifact_closure(
        self,
        raw: Any,
        owner: Path,
        registry_path: Path,
        rows: list[dict[str, str]],
        authority_records: dict[str, dict[str, Any]],
    ) -> None:
        if not isinstance(raw, list) or not raw:
            self.add(owner, "artifact_closure must be a nonempty array")
            return
        accepted_by_id: dict[str, dict[str, Any]] = {}
        accepted_paths: dict[str, str] = {}
        for index, item in enumerate(raw):
            label = f"artifact_closure[{index}]"
            record = self.check_exact_fields(
                item,
                ARTIFACT_REFERENCE_FIELDS,
                owner,
                label,
            )
            if record is None:
                continue
            artifact_id = record.get("id")
            if not self.valid_artifact_id(artifact_id):
                self.add(owner, f"{label}.id must be a stable artifact ID")
            elif artifact_id in accepted_by_id:
                self.add(owner, f"artifact_closure has duplicate id: {artifact_id}")
            else:
                accepted_by_id[artifact_id] = record
            status = record.get("status")
            if status not in {"active", "accepted", "final", "approved", "in-progress"}:
                self.add(owner, f"{label}.status must be an effective artifact status")
            raw_path = record.get("path")
            if isinstance(raw_path, str):
                if raw_path in accepted_paths:
                    self.add(
                        owner,
                        f"artifact_closure has duplicate path: {raw_path}",
                    )
                else:
                    accepted_paths[raw_path] = str(artifact_id)
            target = self.safe_path(raw_path, owner, f"{label}.path", kind="file")
            if target is None:
                continue
            self.check_digest(owner, target, record.get("sha256"), f"{label}.sha256")
            metadata = self.read_frontmatter(target, label)
            if metadata is not None:
                if metadata.get("artifact_id") != artifact_id:
                    self.add(target, f"artifact_id does not match {label}.id")
                if metadata.get("status") != status:
                    self.add(target, f"status does not match {label}.status")

        effective_rows: dict[str, dict[str, str]] = {}
        for row in rows:
            artifact_id = row["id"].strip("`")
            artifact_type = row["type"].strip("`")
            status = row["status"].strip("`")
            if artifact_type == "artifact-registry" or status not in {
                "active",
                "accepted",
                "final",
                "approved",
                "in-progress",
            }:
                continue
            if artifact_id in effective_rows:
                self.add(
                    registry_path,
                    f"artifact registry has duplicate effective rows for {artifact_id}",
                )
                continue
            effective_rows[artifact_id] = row

        for artifact_id in sorted(set(effective_rows) - set(accepted_by_id)):
            self.add(
                owner,
                f"artifact_closure is missing effective registry artifact: {artifact_id}",
            )
        for artifact_id in sorted(set(accepted_by_id) - set(effective_rows)):
            self.add(
                owner,
                f"artifact_closure contains extra or ineffective artifact: {artifact_id}",
            )
        for artifact_id in sorted(set(effective_rows) & set(accepted_by_id)):
            row = effective_rows[artifact_id]
            record = accepted_by_id[artifact_id]
            row_status = row["status"].strip("`")
            if record.get("status") != row_status:
                self.add(
                    owner,
                    f"artifact_closure status contradicts registry: {artifact_id}",
                )
            raw_path = record.get("path")
            if isinstance(raw_path, str) and not self.locator_matches(
                registry_path,
                row["path"],
                raw_path,
            ):
                self.add(
                    owner,
                    f"artifact_closure path contradicts registry: {artifact_id}",
                )
            target = (
                self.repo_root / raw_path
                if isinstance(raw_path, str) and self.is_safe_relative(raw_path)
                else None
            )
            metadata = (
                self.read_frontmatter(target, f"accepted artifact {artifact_id}")
                if target is not None and target.is_file()
                else None
            )
            if metadata is not None and metadata.get("artifact_type") != row["type"].strip("`"):
                self.add(
                    target,
                    f"artifact_type contradicts registry for accepted artifact: {artifact_id}",
                )

        for authority_field in ("system_profile", "stack_profile"):
            authority = authority_records.get(authority_field)
            if not isinstance(authority, dict) or not isinstance(authority.get("id"), str):
                continue
            closure_record = accepted_by_id.get(authority["id"])
            if closure_record != authority:
                self.add(
                    owner,
                    f"{authority_field} must exactly match its artifact_closure entry",
                )

    def validate_skills(self, raw: Any, owner: Path) -> None:
        if not isinstance(raw, dict):
            self.add(owner, "skills must be a JSON object")
            return
        missing = REQUIRED_SKILLS - set(raw)
        for capability in sorted(missing):
            self.add(owner, f"skills is missing required capability: {capability}")
        names: dict[str, str] = {}
        paths: dict[str, str] = {}
        for capability in sorted(raw):
            if not self.valid_kebab_id(capability):
                self.add(owner, f"invalid skill capability key: {capability}")
                continue
            label = f"skills.{capability}"
            record = self.check_exact_fields(
                raw[capability], SKILL_REFERENCE_FIELDS, owner, label
            )
            if record is None:
                continue
            name = record.get("name")
            if not self.valid_kebab_id(name):
                self.add(owner, f"{label}.name must be a kebab-case skill name")
            elif name in names:
                self.add(
                    owner,
                    f"duplicate skill name for {names[name]} and {capability}: {name}",
                )
            else:
                names[name] = capability
            raw_path = record.get("path")
            if isinstance(raw_path, str):
                if raw_path in paths:
                    self.add(
                        owner,
                        f"duplicate skill path for {paths[raw_path]} and {capability}: {raw_path}",
                    )
                else:
                    paths[raw_path] = capability
            path = self.safe_path(record.get("path"), owner, f"{label}.path", kind="dir")
            if path is None:
                continue
            if isinstance(name, str) and path.name != name:
                self.add(owner, f"{label}.path basename must match its skill name")
            self.check_digest(owner, path, record.get("sha256"), f"{label}.sha256")
            skill_file = path / "SKILL.md"
            if skill_file.is_symlink():
                self.add(skill_file, f"{label} SKILL.md must not be a symbolic link")
                continue
            if not skill_file.is_file():
                self.add(path, f"{label} directory is missing SKILL.md")
                continue
            metadata = self.read_frontmatter(skill_file, f"{label} SKILL.md")
            if metadata is not None and metadata.get("name") != name:
                self.add(skill_file, f"frontmatter name does not match {label}.name")

    def validate_file_reference(
        self, raw: Any, owner: Path, label: str
    ) -> Path | None:
        record = self.check_exact_fields(raw, REFERENCE_FIELDS, owner, label)
        if record is None:
            return None
        path = self.safe_path(record.get("path"), owner, f"{label}.path", kind="file")
        if path is not None:
            self.check_digest(owner, path, record.get("sha256"), f"{label}.sha256")
        return path

    def validate_freshness_policy(self, raw: Any, owner: Path) -> int | None:
        policy = self.check_exact_fields(
            raw,
            FRESHNESS_POLICY_FIELDS,
            owner,
            "freshness_policy",
        )
        if policy is None:
            return None
        stale_after_days = policy.get("stale_after_days")
        if (
            not isinstance(stale_after_days, int)
            or isinstance(stale_after_days, bool)
            or not 1 <= stale_after_days <= 365
        ):
            self.add(
                owner,
                "freshness_policy.stale_after_days must be an integer from 1 to 365",
            )
            return None
        return stale_after_days

    @staticmethod
    def canonical_digest(domain: str, value: Any) -> str:
        serialized = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        digest = hashlib.sha256()
        digest.update(domain.encode("ascii"))
        digest.update(b"\0")
        digest.update(serialized)
        return digest.hexdigest()

    @classmethod
    def freshness_policy_digest(cls, profile: dict[str, Any]) -> str:
        return cls.canonical_digest(
            "app-profile-freshness-policy-v1",
            profile.get("freshness_policy"),
        )

    @classmethod
    def profile_inputs_digest(cls, profile: dict[str, Any]) -> str:
        """Digest effective authority inputs without circular evidence locks.

        The pattern catalog SHA transitively includes pattern execution evidence,
        so this envelope binds its path while each pattern binds its own semantic
        contract and resources. Clean-room and guidance evidence references are
        excluded because they consume this digest.
        """

        pattern_reference = profile.get("pattern_catalog")
        pattern_locator = (
            {"path": pattern_reference.get("path")}
            if isinstance(pattern_reference, dict)
            else pattern_reference
        )
        envelope = {
            "schema_version": profile.get("schema_version"),
            "profile_id": profile.get("profile_id"),
            "blueprint_version": profile.get("blueprint_version"),
            "blueprint_revision": profile.get("blueprint_revision"),
            "source_revision": profile.get("source_revision"),
            "artifact_registry": profile.get("artifact_registry"),
            "artifact_closure": profile.get("artifact_closure"),
            "system_profile": profile.get("system_profile"),
            "stack_profile": profile.get("stack_profile"),
            "skills": profile.get("skills"),
            "pattern_catalog": pattern_locator,
            "verification_commands": profile.get("verification_commands"),
            "freshness_policy": profile.get("freshness_policy"),
        }
        return cls.canonical_digest("app-profile-inputs-v1", envelope)

    @classmethod
    def profile_input_digests(cls, profile: dict[str, Any]) -> dict[str, Any]:
        locks: dict[str, Any] = {}
        for field in (
            "artifact_registry",
            "system_profile",
            "stack_profile",
            "pattern_catalog",
            "verification_commands",
        ):
            reference = profile.get(field)
            locks[field] = reference.get("sha256") if isinstance(reference, dict) else None
        skills = profile.get("skills")
        if isinstance(skills, dict):
            for capability in sorted(skills):
                record = skills[capability]
                locks[f"skill:{capability}"] = (
                    record.get("sha256") if isinstance(record, dict) else None
                )
        locks["freshness_policy"] = cls.freshness_policy_digest(profile)
        locks["profile_inputs"] = cls.profile_inputs_digest(profile)
        return locks

    @staticmethod
    def evidence_authority_inputs(
        authority_input_digests: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            name: authority_input_digests.get(name)
            for name in ("freshness_policy", "profile_inputs")
        }

    def validate_unique_string_list(
        self,
        path: Path,
        label: str,
        raw: Any,
        *,
        require_nonempty: bool = False,
    ) -> set[str]:
        if (
            not isinstance(raw, list)
            or (require_nonempty and not raw)
            or any(not isinstance(value, str) or not value.strip() for value in (raw or []))
        ):
            qualifier = "nonempty " if require_nonempty else ""
            self.add(path, f"{label} must be a {qualifier}string list")
            return set()
        normalized = set(raw)
        if len(normalized) != len(raw):
            self.add(path, f"{label} must contain unique values")
        return normalized

    def validate_pattern_fixture_reference(
        self,
        raw: Any,
        owner: Path,
        label: str,
    ) -> Path | None:
        record = self.check_exact_fields(raw, REFERENCE_FIELDS, owner, label)
        if record is None:
            return None
        path = self.safe_path(record.get("path"), owner, f"{label}.path", kind="file")
        if path is not None:
            self.check_digest(owner, path, record.get("sha256"), f"{label}.sha256")
            self.validate_substantive_pattern_resource(path, owner, label)
        return path

    def validate_substantive_pattern_resource(
        self,
        target: Path,
        owner: Path,
        label: str,
    ) -> None:
        """Reject bounded empty/comment-only pattern resources fail-closed."""

        try:
            with target.open("rb") as handle:
                content = handle.read(1_048_577)
        except OSError as error:
            self.add(owner, f"{label} cannot be inspected for substantive content: {error}")
            return
        if not content:
            self.add(owner, f"{label} must contain substantive content")
            return
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            self.add(owner, f"{label} must be UTF-8 substantive content")
            return
        stripped = text.strip()
        if not stripped:
            self.add(owner, f"{label} must contain substantive content")
            return
        if target.suffix.casefold() == ".json":
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError:
                parsed = object()
            if parsed in ({}, [], None, ""):
                self.add(owner, f"{label} must not be an empty JSON placeholder")
                return
        without_blocks = re.sub(r"/\*.*?\*/|<!--.*?-->", "", text, flags=re.DOTALL)
        comment_prefixes = ["//"]
        if target.suffix.casefold() in {
            ".py",
            ".pyi",
            ".rb",
            ".sh",
            ".bash",
            ".zsh",
            ".yaml",
            ".yml",
            ".toml",
        }:
            comment_prefixes.append("#")
        substantive_lines = [
            line
            for line in without_blocks.splitlines()
            if line.strip()
            and not any(line.lstrip().startswith(prefix) for prefix in comment_prefixes)
        ]
        if not substantive_lines:
            self.add(owner, f"{label} must not be empty or comment-only")

    def validate_pattern_catalog(
        self,
        path: Path,
        declared_skills: Any,
        source_revision: Any,
        authority_input_digests: dict[str, Any],
        stale_after_days: int | None,
    ) -> None:
        data = self.load_json(path, "pattern catalog")
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, "pattern catalog must be a JSON object")
            return
        allowed_catalog_fields = {"$schema", "schema_version", "patterns"}
        for field in sorted({"schema_version", "patterns"} - set(data)):
            self.add(path, f"pattern catalog missing required field: {field}")
        for field in sorted(set(data) - allowed_catalog_fields):
            self.add(path, f"pattern catalog has unknown field: {field}")
        if "$schema" in data and (
            not isinstance(data["$schema"], str) or not data["$schema"].strip()
        ):
            self.add(path, "pattern catalog $schema must be nonempty")
        if data.get("schema_version") != "1.0.0":
            self.add(path, "pattern catalog schema_version must equal 1.0.0")
        patterns = data.get("patterns")
        if not isinstance(patterns, list) or not patterns:
            self.add(path, "pattern catalog patterns must be a nonempty list")
            return
        skill_capability_by_ref: dict[str, str] = {}
        if isinstance(declared_skills, dict):
            skill_capability_by_ref.update(
                {capability: capability for capability in declared_skills}
            )
            for capability, record in declared_skills.items():
                if isinstance(record, dict) and isinstance(record.get("name"), str):
                    skill_capability_by_ref.setdefault(record["name"], capability)
        seen: set[str] = set()
        for index, pattern in enumerate(patterns):
            if not isinstance(pattern, dict):
                self.add(path, f"patterns[{index}] must be a JSON object")
                continue
            for field in sorted(PATTERN_FIELDS - set(pattern)):
                self.add(path, f"patterns[{index}] missing required field: {field}")
            for field in sorted(set(pattern) - PATTERN_FIELDS):
                self.add(path, f"patterns[{index}] has unknown field: {field}")
            for tier_field in ("tier", "evidence_tier"):
                if tier_field in pattern:
                    self.add(
                        path,
                        f"patterns[{index}].{tier_field} is task-time state and must not appear in the established catalog",
                    )
            pattern_id = pattern.get("id")
            if not self.valid_kebab_id(pattern_id):
                self.add(path, f"patterns[{index}].id must be a kebab-case identifier")
                continue
            if pattern_id in seen:
                self.add(path, f"duplicate pattern id: {pattern_id}")
            seen.add(pattern_id)
            label = f"patterns[{index}]"
            intent = pattern.get("intent")
            if not isinstance(intent, str) or not intent.strip():
                self.add(path, f"{label}.intent must be nonempty")
            primary_owner = pattern.get("primary_owner")
            primary_capability: str | None = None
            if (
                not isinstance(primary_owner, str)
                or primary_owner not in skill_capability_by_ref
            ):
                self.add(
                    path,
                    f"{label}.primary_owner must reference exactly one declared skill",
                )
            else:
                primary_capability = skill_capability_by_ref[primary_owner]
            support = pattern.get("support_skills")
            if not isinstance(support, list):
                self.add(path, f"{label}.support_skills must be a list")
            else:
                normalized_support: set[str] = set()
                raw_support: set[str] = set()
                for skill_ref in support:
                    if not isinstance(skill_ref, str) or skill_ref not in skill_capability_by_ref:
                        self.add(path, f"{label} references unknown support skill: {skill_ref}")
                        continue
                    capability = skill_capability_by_ref[skill_ref]
                    if skill_ref in raw_support or capability in normalized_support:
                        self.add(path, f"{label} has duplicate support skill: {skill_ref}")
                        continue
                    raw_support.add(skill_ref)
                    normalized_support.add(capability)
                    if capability == primary_capability:
                        self.add(
                            path,
                            f"{label}.support_skills must exclude primary_owner",
                        )
            applicability = pattern.get("applicability")
            if not isinstance(applicability, dict):
                self.add(path, f"{label}.applicability must be a JSON object")
            else:
                for field, require_nonempty in (("use_when", True), ("avoid_when", False)):
                    values = applicability.get(field)
                    if (
                        not isinstance(values, list)
                        or (require_nonempty and not values)
                        or any(
                            not isinstance(value, str) or not value.strip()
                            for value in (values if isinstance(values, list) else [])
                        )
                    ):
                        qualifier = "nonempty " if require_nonempty else ""
                        self.add(
                            path,
                            f"{label}.applicability.{field} must be a {qualifier}string list",
                        )
                for field in sorted(set(applicability) - {"use_when", "avoid_when"}):
                    self.add(path, f"{label}.applicability has unknown field: {field}")
            public_contract = pattern.get("public_contract")
            if not isinstance(public_contract, dict):
                self.add(path, f"{label}.public_contract must be a JSON object")
            else:
                required_contract_fields = {"inputs", "outputs", "states"}
                for field in sorted(required_contract_fields - set(public_contract)):
                    self.add(path, f"{label}.public_contract missing required field: {field}")
                for field in sorted(set(public_contract) - required_contract_fields):
                    self.add(path, f"{label}.public_contract has unknown field: {field}")
                for field in sorted(required_contract_fields):
                    self.validate_unique_string_list(
                        path,
                        f"{label}.public_contract.{field}",
                        public_contract.get(field),
                        require_nonempty=True,
                    )
            allowed_dependencies = self.validate_unique_string_list(
                path,
                f"{label}.allowed_dependencies",
                pattern.get("allowed_dependencies"),
            )
            forbidden_dependencies = self.validate_unique_string_list(
                path,
                f"{label}.forbidden_dependencies",
                pattern.get("forbidden_dependencies"),
            )
            for dependency in sorted(allowed_dependencies & forbidden_dependencies):
                self.add(
                    path,
                    f"{label} dependency appears in both allowed and forbidden lists: {dependency}",
                )
            exemplar_path = self.validate_file_reference(
                pattern.get("exemplar"),
                path,
                f"{label}.exemplar",
            )
            if exemplar_path is not None:
                self.validate_substantive_pattern_resource(
                    exemplar_path,
                    path,
                    f"{label}.exemplar",
                )
            verifier_path = self.validate_file_reference(
                pattern.get("verifier"),
                path,
                f"{label}.verifier",
            )
            if verifier_path is not None:
                self.validate_substantive_pattern_resource(
                    verifier_path,
                    path,
                    f"{label}.verifier",
                )
            verifier_argv = pattern.get("verifier_argv")
            verifier_path_value = (
                pattern.get("verifier", {}).get("path")
                if isinstance(pattern.get("verifier"), dict)
                else None
            )
            if (
                not isinstance(verifier_argv, list)
                or not verifier_argv
                or any(
                    not isinstance(argument, str) or not argument
                    for argument in (
                        verifier_argv if isinstance(verifier_argv, list) else []
                    )
                )
            ):
                self.add(path, f"{label}.verifier_argv must be a nonempty string list")
            elif verifier_path_value not in verifier_argv:
                self.add(path, f"{label}.verifier_argv must reference verifier.path")
            fixtures = pattern.get("fixtures")
            if not isinstance(fixtures, dict):
                self.add(path, f"{label}.fixtures must be a JSON object")
                continue
            for field in sorted({"positive", "negative", "expected_failures"} - set(fixtures)):
                self.add(path, f"{label}.fixtures missing required field: {field}")
            for field in sorted(set(fixtures) - {"positive", "negative", "expected_failures"}):
                self.add(path, f"{label}.fixtures has unknown field: {field}")
            for polarity in ("positive", "negative"):
                references = fixtures.get(polarity)
                if not isinstance(references, list) or not references:
                    self.add(
                        path,
                        f"{label}.fixtures.{polarity} must be a nonempty reference list",
                    )
                    continue
                for reference_index, reference in enumerate(references):
                    self.validate_pattern_fixture_reference(
                        reference,
                        path,
                        f"{label}.fixtures.{polarity}[{reference_index}]",
                    )
            self.validate_pattern_expected_failures(path, label, fixtures)
            evidence_path = self.validate_file_reference(
                pattern.get("verification_evidence"),
                path,
                f"{label}.verification_evidence",
            )
            if evidence_path is not None:
                self.validate_pattern_verification_evidence(
                    evidence_path,
                    source_revision,
                    pattern_id,
                    pattern,
                    label,
                    authority_input_digests,
                    stale_after_days,
                )

    def validate_pattern_expected_failures(
        self,
        path: Path,
        label: str,
        fixtures: dict[str, Any],
    ) -> None:
        negative = fixtures.get("negative")
        negative_paths = {
            reference.get("path")
            for reference in negative
            if isinstance(reference, dict) and isinstance(reference.get("path"), str)
        } if isinstance(negative, list) else set()
        raw = fixtures.get("expected_failures")
        if not isinstance(raw, dict) or not raw:
            self.add(path, f"{label}.fixtures.expected_failures must be a nonempty map")
            return
        for fixture_path in sorted(negative_paths - set(raw)):
            self.add(
                path,
                f"{label}.fixtures.expected_failures missing negative fixture: {fixture_path}",
            )
        for fixture_path in sorted(set(raw) - negative_paths):
            self.add(
                path,
                f"{label}.fixtures.expected_failures has undeclared fixture: {fixture_path}",
            )
        for fixture_path, failure in sorted(raw.items()):
            failure_label = f"{label}.fixtures.expected_failures[{fixture_path}]"
            record = self.check_exact_fields(
                failure,
                {"code", "reason"},
                path,
                failure_label,
            )
            if record is None:
                continue
            code = record.get("code")
            if not self.valid_kebab_id(code):
                self.add(path, f"{failure_label}.code must be kebab-case")
            reason = record.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                self.add(path, f"{failure_label}.reason must be nonempty")

    def validate_input_digests(
        self,
        path: Path,
        label: str,
        raw: Any,
        expected: dict[str, Any],
    ) -> None:
        if not isinstance(raw, dict):
            self.add(path, f"{label} must be a JSON object")
            return
        for name in sorted(set(expected) - set(raw)):
            self.add(path, f"{label} missing required input: {name}")
        for name in sorted(set(raw) - set(expected)):
            self.add(path, f"{label} has unknown input: {name}")
        for name in sorted(set(expected) & set(raw)):
            digest = raw[name]
            if not isinstance(digest, str) or not SHA256.fullmatch(digest):
                self.add(path, f"{label}.{name} must be a full SHA-256 digest")
            elif digest != expected[name]:
                self.add(path, f"{label}.{name} is stale or misbound")

    @staticmethod
    def parse_timestamp(raw: Any) -> datetime | None:
        if not isinstance(raw, str) or not RFC3339.fullmatch(raw):
            return None
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
        return parsed if parsed.tzinfo is not None else None

    @classmethod
    def valid_timestamp(cls, raw: Any) -> bool:
        return cls.parse_timestamp(raw) is not None

    @staticmethod
    def skill_eval_case_input_digest(case: dict[str, Any]) -> str:
        canonical = {
            field: case.get(field)
            for field in (
                "id",
                "kind",
                "skills",
                "prompt",
                "route_trace",
                "input_digests",
                "adversarial_fixture",
                "expected_disposition",
                "expected_failure",
            )
        }
        return AppProfileValidator.canonical_digest(
            "app-profile-skill-eval-case-v1",
            canonical,
        )

    def validate_provenance(
        self,
        path: Path,
        label: str,
        data: dict[str, Any],
        stale_after_days: int | None,
    ) -> None:
        for field in ("run_id", "actor", "toolchain", "environment"):
            value = data.get(field)
            if (
                not isinstance(value, str)
                or not value.strip()
                or value != value.strip()
                or len(value) > 256
                or any(ord(character) < 32 or ord(character) == 127 for character in value)
            ):
                self.add(path, f"{label} {field} must be a nonempty control-free string")
        observed_at = self.parse_timestamp(data.get("observed_at"))
        if observed_at is None:
            self.add(path, f"{label} observed_at must be timezone-aware RFC 3339")
            return
        if stale_after_days is None:
            return
        now = datetime.now(timezone.utc)
        observed_utc = observed_at.astimezone(timezone.utc)
        if observed_utc > now + FUTURE_CLOCK_SKEW:
            self.add(path, f"{label} observed_at must not be in the future")
        elif observed_utc < now - timedelta(days=stale_after_days):
            self.add(path, f"{label} evidence is expired by freshness_policy")

    @classmethod
    def pattern_contract_digest(cls, pattern: dict[str, Any]) -> str:
        envelope = {
            field: value
            for field, value in pattern.items()
            if field != "verification_evidence"
        }
        return cls.canonical_digest("app-profile-pattern-contract-v1", envelope)

    @classmethod
    def pattern_input_digests(
        cls,
        pattern: dict[str, Any],
        authority_input_digests: dict[str, Any],
    ) -> dict[str, Any]:
        locks: dict[str, Any] = {
            "profile_inputs": authority_input_digests.get("profile_inputs"),
            "freshness_policy": authority_input_digests.get("freshness_policy"),
            "pattern_contract": cls.pattern_contract_digest(pattern),
        }
        for field in ("exemplar", "verifier"):
            reference = pattern.get(field)
            locks[field] = reference.get("sha256") if isinstance(reference, dict) else None
        fixtures = pattern.get("fixtures")
        if isinstance(fixtures, dict):
            for polarity in ("positive", "negative"):
                references = fixtures.get(polarity)
                if isinstance(references, list):
                    for index, reference in enumerate(references):
                        locks[f"fixture:{polarity}:{index}"] = (
                            reference.get("sha256")
                            if isinstance(reference, dict)
                            else None
                        )
        return locks

    def validate_pattern_verification_evidence(
        self,
        path: Path,
        source_revision: Any,
        pattern_id: Any,
        pattern: dict[str, Any],
        pattern_label: str,
        authority_input_digests: dict[str, Any],
        stale_after_days: int | None,
    ) -> None:
        data = self.load_json(path, "pattern verification evidence")
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, "pattern verification evidence must be a JSON object")
            return
        required = {
            "schema_version",
            "source_revision",
            "pattern_id",
            "input_digests",
            "run_id",
            "actor",
            "toolchain",
            "environment",
            "observed_at",
            "result",
            "positive_result",
            "negative_result",
            "verifier_argv",
            "verifier_exit_code",
            "fixture_results",
        }
        for field in sorted(required - set(data)):
            self.add(path, f"pattern verification evidence missing required field: {field}")
        for field in sorted(set(data) - required):
            self.add(path, f"pattern verification evidence has unknown field: {field}")
        if data.get("schema_version") != "1.0.0":
            self.add(path, "pattern verification evidence schema_version must equal 1.0.0")
        if data.get("source_revision") != source_revision:
            self.add(path, "pattern verification evidence source_revision is stale")
        if data.get("pattern_id") != pattern_id:
            self.add(path, f"pattern verification evidence is misbound to {pattern_label}")
        if data.get("result") != "PASS":
            self.add(path, "pattern verification evidence result must be PASS")
        if data.get("positive_result") != "PASS":
            self.add(path, "pattern verification evidence positive_result must be PASS")
        if data.get("negative_result") != "PASS":
            self.add(path, "pattern verification evidence negative_result must be PASS")
        if data.get("verifier_argv") != pattern.get("verifier_argv"):
            self.add(path, "pattern verification evidence verifier_argv is misbound")
        verifier_exit = data.get("verifier_exit_code")
        if (
            not isinstance(verifier_exit, int)
            or isinstance(verifier_exit, bool)
            or verifier_exit != 0
        ):
            self.add(path, "pattern verification evidence verifier_exit_code must be 0")
        self.validate_pattern_fixture_results(path, data.get("fixture_results"), pattern)
        self.validate_provenance(
            path,
            "pattern verification evidence",
            data,
            stale_after_days,
        )
        self.validate_input_digests(
            path,
            "pattern verification evidence input_digests",
            data.get("input_digests"),
            self.pattern_input_digests(pattern, authority_input_digests),
        )

    def validate_pattern_fixture_results(
        self,
        path: Path,
        raw: Any,
        pattern: dict[str, Any],
    ) -> None:
        expected: dict[tuple[str, str], dict[str, Any]] = {}
        fixtures = pattern.get("fixtures")
        if isinstance(fixtures, dict):
            for polarity in ("positive", "negative"):
                references = fixtures.get(polarity)
                if not isinstance(references, list):
                    continue
                for reference in references:
                    if not isinstance(reference, dict) or not isinstance(
                        reference.get("path"), str
                    ):
                        continue
                    expected[(polarity, reference["path"])] = reference
        if not isinstance(raw, list) or not raw:
            self.add(path, "pattern verification evidence fixture_results must be nonempty")
            return
        seen: set[tuple[str, str]] = set()
        for index, result in enumerate(raw):
            label = f"fixture_results[{index}]"
            if not isinstance(result, dict):
                self.add(path, f"{label} must be a JSON object")
                continue
            required = {"polarity", "path", "sha256", "observed", "exit_code"}
            if result.get("polarity") == "negative":
                required.add("observed_failure")
            for field in sorted(required - set(result)):
                self.add(path, f"{label} missing required field: {field}")
            for field in sorted(set(result) - required):
                self.add(path, f"{label} has unknown field: {field}")
            key = (result.get("polarity"), result.get("path"))
            if not all(isinstance(value, str) for value in key):
                self.add(path, f"{label} requires string polarity and path")
                continue
            if key in seen:
                self.add(path, f"duplicate pattern fixture result: {key[0]}:{key[1]}")
                continue
            seen.add(key)
            reference = expected.get(key)
            if reference is None:
                self.add(path, f"{label} does not match a declared fixture")
                continue
            if result.get("sha256") != reference.get("sha256"):
                self.add(path, f"{label}.sha256 is stale or misbound")
            expected_observed = "accept" if key[0] == "positive" else "reject"
            if result.get("observed") != expected_observed:
                self.add(path, f"{label}.observed must equal {expected_observed}")
            expected_failures = fixtures.get("expected_failures", {}) if isinstance(
                fixtures, dict
            ) else {}
            if key[0] == "negative" and result.get("observed_failure") != expected_failures.get(
                key[1]
            ):
                self.add(
                    path,
                    f"{label}.observed_failure must match declared expected_failures entry",
                )
            exit_code = result.get("exit_code")
            if not isinstance(exit_code, int) or isinstance(exit_code, bool) or exit_code != 0:
                self.add(path, f"{label}.exit_code must be 0")
        for polarity, fixture_path in sorted(set(expected) - seen):
            self.add(
                path,
                f"pattern verification evidence missing fixture result: {polarity}:{fixture_path}",
            )

    def validate_command_registry(self, path: Path) -> dict[str, dict[str, Any]]:
        data = self.load_json(path, "verification command registry")
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, "verification command registry must be a JSON object")
            return {}
        allowed = {"$schema", "schema_version", "lanes"}
        for field in sorted({"schema_version", "lanes"} - set(data)):
            self.add(path, f"verification command registry missing required field: {field}")
        for field in sorted(set(data) - allowed):
            self.add(path, f"verification command registry has unknown field: {field}")
        if "$schema" in data and (
            not isinstance(data["$schema"], str) or not data["$schema"].strip()
        ):
            self.add(path, "verification command registry $schema must be nonempty")
        if data.get("schema_version") != "1.0.0":
            self.add(path, "command registry schema_version must equal 1.0.0")
        lanes = data.get("lanes")
        if not isinstance(lanes, dict):
            self.add(path, "command registry lanes must be a JSON object")
            return {}
        validated: dict[str, dict[str, Any]] = {}
        for lane_id in sorted(lanes):
            lane = lanes[lane_id]
            label = f"lanes.{lane_id}"
            if not self.valid_kebab_id(lane_id):
                self.add(path, f"invalid command lane id: {lane_id}")
                continue
            if lane_id in FORBIDDEN_EXTERNAL_EFFECT_LANES:
                self.add(
                    path,
                    f"command lane {lane_id} is forbidden because clean-room verification must not perform external publication or deployment",
                )
            if not isinstance(lane, dict):
                self.add(path, f"{label} must be a JSON object")
                continue
            allowed_fields = {
                "argv",
                "cwd",
                "required_environment",
                "timeout_seconds",
            }
            for field in sorted(set(lane) - allowed_fields):
                self.add(path, f"{label} has unknown field: {field}")
            argv = lane.get("argv")
            if (
                not isinstance(argv, list)
                or not argv
                or any(
                    not isinstance(argument, str)
                    or not argument
                    or any(ord(character) < 32 or ord(character) == 127 for character in argument)
                    for argument in argv
                )
            ):
                self.add(path, f"{label}.argv must be a nonempty array of nonempty arguments")
            self.safe_path(
                lane.get("cwd", "."),
                path,
                f"{label}.cwd",
                kind="dir",
                allow_dot=True,
            )
            environment = lane.get("required_environment", [])
            if (
                not isinstance(environment, list)
                or any(not isinstance(item, str) for item in environment)
                or len(environment) != len(set(environment))
            ):
                self.add(path, f"{label}.required_environment must be a unique string list")
            elif any(not ENVIRONMENT_NAME.fullmatch(item) for item in environment):
                self.add(path, f"{label}.required_environment contains an invalid name")
            timeout = lane.get("timeout_seconds")
            if timeout is not None and (
                not isinstance(timeout, int)
                or isinstance(timeout, bool)
                or timeout < 1
            ):
                self.add(path, f"{label}.timeout_seconds must be a positive integer")
            if lane_id == "start-smoke" and timeout is None:
                self.add(path, "lanes.start-smoke.timeout_seconds is required")
            if (
                isinstance(argv, list)
                and bool(argv)
                and all(
                    isinstance(argument, str)
                    and bool(argument)
                    and not any(
                        ord(character) < 32 or ord(character) == 127
                        for character in argument
                    )
                    for argument in argv
                )
                and self.valid_kebab_id(lane_id)
            ):
                validated[lane_id] = lane
        for lane_id in sorted(BASELINE_COMMAND_LANES):
            if lane_id not in lanes:
                self.add(path, f"missing baseline command lane: {lane_id}")
        return validated

    def validate_clean_room_evidence(
        self,
        path: Path,
        source_revision: Any,
        command_digest: Any,
        command_registry: dict[str, dict[str, Any]],
        expected_input_digests: dict[str, Any],
        stale_after_days: int | None,
    ) -> None:
        """Validate a record of execution; this function never runs commands."""

        data = self.load_json(path, "clean-room evidence")
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, "clean-room evidence must be a JSON object")
            return
        allowed = {
            "$schema",
            "schema_version",
            "source_revision",
            "verification_commands_sha256",
            "input_digests",
            "run_id",
            "actor",
            "toolchain",
            "environment",
            "observed_at",
            "status",
            "result",
            "commands",
        }
        required = allowed - {"$schema"}
        for field in sorted(required - set(data)):
            self.add(path, f"clean-room evidence missing required field: {field}")
        for field in sorted(set(data) - allowed):
            self.add(path, f"clean-room evidence has unknown field: {field}")
        if "$schema" in data and (
            not isinstance(data["$schema"], str) or not data["$schema"].strip()
        ):
            self.add(path, "clean-room evidence $schema must be nonempty")
        if data.get("schema_version") != "1.0.0":
            self.add(path, "clean-room evidence schema_version must equal 1.0.0")
        if data.get("source_revision") != source_revision:
            self.add(path, "clean-room evidence source_revision is stale")
        if data.get("verification_commands_sha256") != command_digest:
            self.add(
                path,
                "clean-room evidence verification_commands_sha256 does not match app profile",
            )
        self.validate_provenance(
            path,
            "clean-room evidence",
            data,
            stale_after_days,
        )
        self.validate_input_digests(
            path,
            "clean-room evidence input_digests",
            data.get("input_digests"),
            expected_input_digests,
        )
        if data.get("status") != "current":
            self.add(path, "clean-room evidence status must be current")
        if data.get("result") != "PASS":
            self.add(path, "clean-room evidence result must be PASS")
        commands = data.get("commands")
        if not isinstance(commands, list) or not commands:
            self.add(path, "clean-room evidence commands must be a nonempty list")
            return
        seen: set[str] = set()
        for index, command in enumerate(commands):
            label = f"commands[{index}]"
            if not isinstance(command, dict):
                self.add(path, f"{label} must be a JSON object")
                continue
            lane = command.get("lane")
            expected_fields = {"lane", "argv", "cwd", "exit_code"}
            if lane == "start-smoke":
                expected_fields.update(
                    {"readiness_observed", "termination_observed"}
                )
            for field in sorted(expected_fields - set(command)):
                self.add(path, f"{label} missing required field: {field}")
            for field in sorted(set(command) - expected_fields):
                self.add(path, f"{label} has unknown field: {field}")
            if not self.valid_kebab_id(lane):
                self.add(path, f"{label}.lane must be a kebab-case identifier")
                continue
            if lane in seen:
                self.add(path, f"duplicate clean-room command lane: {lane}")
                continue
            seen.add(lane)
            declared = command_registry.get(lane)
            if declared is None:
                self.add(path, f"clean-room evidence references undeclared lane: {lane}")
                continue
            if command.get("argv") != declared.get("argv"):
                self.add(path, f"{label}.argv does not match declared lane: {lane}")
            if command.get("cwd") != declared.get("cwd", "."):
                self.add(path, f"{label}.cwd does not match declared lane: {lane}")
            if lane == "start-smoke":
                if command.get("readiness_observed") is not True:
                    self.add(path, f"{label}.readiness_observed must equal true")
                if command.get("termination_observed") is not True:
                    self.add(path, f"{label}.termination_observed must equal true")
            exit_code = command.get("exit_code")
            if not isinstance(exit_code, int) or isinstance(exit_code, bool) or exit_code != 0:
                self.add(path, f"{label}.exit_code must be 0")
        for lane in sorted(BASELINE_COMMAND_LANES - seen):
            self.add(path, f"clean-room evidence missing baseline lane: {lane}")
        for lane in sorted(set(command_registry) - BASELINE_COMMAND_LANES - seen):
            self.add(path, f"clean-room evidence missing declared lane: {lane}")

    def validate_guidance_evidence(
        self,
        raw: Any,
        source_revision: Any,
        declared_skills: Any,
        expected_input_digests: dict[str, Any],
        stale_after_days: int | None,
        owner: Path,
    ) -> None:
        record = self.check_exact_fields(
            raw, GUIDANCE_REFERENCE_FIELDS, owner, "guidance_evidence"
        )
        if record is None:
            return
        evidence_id = record.get("id")
        if not self.valid_artifact_id(evidence_id):
            self.add(owner, "guidance_evidence.id must be a stable artifact ID")
        current_revision = record.get("current_revision")
        if not isinstance(current_revision, str) or not SOURCE_REVISION.fullmatch(current_revision):
            self.add(
                owner,
                "guidance_evidence.current_revision must be a safe immutable revision token",
            )
        elif current_revision != source_revision:
            self.add(owner, "guidance_evidence.current_revision must equal source_revision")
        path = self.safe_path(
            record.get("path"),
            owner,
            "guidance_evidence.path",
            kind="file",
        )
        if path is None:
            return
        self.check_digest(
            owner,
            path,
            record.get("sha256"),
            "guidance_evidence.sha256",
        )
        data = self.load_json(path, "guidance evidence")
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, "guidance evidence must be a JSON object")
            return
        required = {
            "schema_version",
            "evidence_id",
            "source_revision",
            "input_digests",
            "run_id",
            "actor",
            "toolchain",
            "environment",
            "observed_at",
            "result",
            "checks",
        }
        for field in sorted(required - set(data)):
            self.add(path, f"guidance evidence missing required field: {field}")
        for field in sorted(set(data) - required):
            self.add(path, f"guidance evidence has unknown field: {field}")
        if data.get("schema_version") != "1.0.0":
            self.add(path, "guidance evidence schema_version must equal 1.0.0")
        if data.get("evidence_id") != evidence_id:
            self.add(path, "guidance evidence_id does not match app profile")
        if data.get("source_revision") != current_revision:
            self.add(path, "guidance source_revision does not match current_revision")
        if data.get("result") != "PASS":
            self.add(path, "guidance evidence result must equal PASS")
        self.validate_unique_string_list(
            path,
            "guidance evidence checks",
            data.get("checks"),
            require_nonempty=True,
        )
        self.validate_provenance(
            path,
            "guidance evidence",
            data,
            stale_after_days,
        )
        self.validate_input_digests(
            path,
            "guidance evidence input_digests",
            data.get("input_digests"),
            self.evidence_authority_inputs(expected_input_digests),
        )
        eval_path = self.validate_file_reference(
            record.get("skill_evals"),
            owner,
            "guidance_evidence.skill_evals",
        )
        if eval_path is not None:
            self.validate_skill_evals(
                eval_path,
                declared_skills,
                current_revision,
                expected_input_digests,
                stale_after_days,
            )

    def validate_skill_evals(
        self,
        path: Path,
        declared_skills: Any,
        current_revision: Any,
        expected_input_digests: dict[str, Any],
        stale_after_days: int | None,
    ) -> None:
        data = self.load_json(path, "skill evaluation evidence")
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, "skill evaluation evidence must be a JSON object")
            return
        for field in sorted({"schema_version", "source_revision", "cases"} - set(data)):
            self.add(path, f"skill evaluation evidence missing required field: {field}")
        for field in sorted(set(data) - {"schema_version", "source_revision", "cases"}):
            self.add(path, f"skill evaluation evidence has unknown field: {field}")
        if data.get("schema_version") != "1.0.0":
            self.add(path, "skill evaluation schema_version must equal 1.0.0")
        if data.get("source_revision") != current_revision:
            self.add(path, "skill evaluation source_revision must equal current_revision")
        cases = data.get("cases")
        if not isinstance(cases, list) or not cases:
            self.add(path, "skill evaluation cases must be a nonempty list")
            return
        if not isinstance(declared_skills, dict):
            return
        skill_capability_by_ref: dict[str, str] = {
            capability: capability for capability in declared_skills
        }
        for capability, record in declared_skills.items():
            if isinstance(record, dict) and isinstance(record.get("name"), str):
                skill_capability_by_ref[record["name"]] = capability
        known_skills = set(skill_capability_by_ref)
        covered_skills: set[str] = set()
        skills_by_kind: dict[str, set[str]] = {}
        covered_kinds: set[str] = set()
        case_ids: set[str] = set()
        for index, case in enumerate(cases):
            label = f"cases[{index}]"
            if not isinstance(case, dict):
                self.add(path, f"{label} must be a JSON object")
                continue
            case_id = case.get("id")
            if not self.valid_kebab_id(case_id):
                self.add(path, f"{label}.id must be a kebab-case identifier")
            elif case_id in case_ids:
                self.add(path, f"duplicate skill evaluation case id: {case_id}")
            else:
                case_ids.add(case_id)
            kind = case.get("kind")
            normalized_kind: str | None = None
            if not self.valid_kebab_id(kind):
                self.add(path, f"{label}.kind must be a kebab-case identifier")
            else:
                normalized_kind = kind
                covered_kinds.add(normalized_kind)
            base_case_fields = {
                "id",
                "kind",
                "skills",
                "prompt",
                "route_trace",
                "input_digests",
                "conformance",
                "outcome",
            }
            expected_case_fields = set(base_case_fields)
            if normalized_kind in NEGATIVE_EVAL_KINDS:
                expected_case_fields.update(
                    {
                        "adversarial_fixture",
                        "expected_disposition",
                        "expected_failure",
                    }
                )
            for field in sorted(expected_case_fields - set(case)):
                self.add(path, f"{label} missing required field: {field}")
            for field in sorted(set(case) - expected_case_fields):
                self.add(path, f"{label} has unknown field: {field}")
            if normalized_kind in NEGATIVE_EVAL_KINDS:
                disposition = case.get("expected_disposition")
                if disposition not in NEGATIVE_DISPOSITIONS:
                    self.add(
                        path,
                        f"{label}.expected_disposition must be BLOCKED, REFUSED or TASK_REROUTED",
                    )
                failure = case.get("expected_failure")
                if not self.valid_kebab_id(failure):
                    self.add(
                        path,
                        f"{label}.expected_failure must be a stable kebab-case failure code",
                    )
                fixture_path = self.validate_file_reference(
                    case.get("adversarial_fixture"),
                    path,
                    f"{label}.adversarial_fixture",
                )
                if fixture_path is not None:
                    self.validate_adversarial_eval_fixture(
                        fixture_path,
                        disposition,
                        failure,
                    )
            prompt = case.get("prompt")
            if (
                not isinstance(prompt, str)
                or not prompt.strip()
                or any(ord(character) < 32 or ord(character) == 127 for character in prompt)
            ):
                self.add(path, f"{label}.prompt must be a nonempty control-free string")
            route_trace = case.get("route_trace")
            if (
                not isinstance(route_trace, list)
                or not route_trace
                or any(
                    not isinstance(item, str) or not item.strip()
                    for item in (route_trace if isinstance(route_trace, list) else [])
                )
            ):
                self.add(path, f"{label}.route_trace must be a nonempty string list")
            self.validate_input_digests(
                path,
                f"{label}.input_digests",
                case.get("input_digests"),
                expected_input_digests,
            )
            case_input_sha256 = self.skill_eval_case_input_digest(case)
            verdict_paths: dict[str, set[str]] = {}
            for axis in ("conformance", "outcome"):
                verdict_paths[axis] = self.validate_skill_eval_verdict(
                    path,
                    case.get(axis),
                    f"{label}.{axis}",
                    current_revision,
                    case_id,
                    axis,
                    expected_input_digests,
                    case_input_sha256,
                    stale_after_days,
                    case.get("expected_disposition")
                    if normalized_kind in NEGATIVE_EVAL_KINDS
                    else None,
                    case.get("expected_failure")
                    if normalized_kind in NEGATIVE_EVAL_KINDS
                    else None,
                )
            if verdict_paths["conformance"] & verdict_paths["outcome"]:
                self.add(
                    path,
                    f"{label} conformance and outcome evidence files must be distinct",
                )
            skill_refs = case.get("skills")
            case_capabilities: set[str] = set()
            if not isinstance(skill_refs, list) or not skill_refs:
                self.add(path, f"{label}.skills must be a nonempty list")
            else:
                for skill_ref in skill_refs:
                    if not isinstance(skill_ref, str) or skill_ref not in known_skills:
                        self.add(path, f"{label} references unknown skill: {skill_ref}")
                        continue
                    capability = skill_capability_by_ref[skill_ref]
                    covered_skills.add(capability)
                    case_capabilities.add(capability)
            if normalized_kind is not None:
                skills_by_kind.setdefault(normalized_kind, set()).update(
                    case_capabilities
                )
        for capability in sorted(set(declared_skills) - covered_skills):
            self.add(
                path,
                f"skill evaluations do not cover declared skill: {capability}",
            )
        optional_kinds = {
            "audit-changes": AUDIT_NEGATIVE_EVAL_KINDS,
            "publish": PUBLISH_NEGATIVE_EVAL_KINDS,
        }
        for capability, required_kinds in optional_kinds.items():
            if capability not in declared_skills:
                continue
            for kind in sorted(required_kinds - covered_kinds):
                self.add(
                    path,
                    f"skill evaluations missing required {capability} negative case: {kind}",
                )
            for kind in sorted(required_kinds & covered_kinds):
                if capability not in skills_by_kind.get(kind, set()):
                    self.add(
                        path,
                        f"required {capability} negative case {kind} must reference skill: {capability}",
                    )

    def validate_skill_eval_verdict(
        self,
        owner: Path,
        raw: Any,
        label: str,
        current_revision: Any,
        case_id: Any,
        axis: str,
        expected_input_digests: dict[str, Any],
        case_input_sha256: str,
        stale_after_days: int | None,
        expected_disposition: Any,
        expected_failure: Any,
    ) -> set[str]:
        if not isinstance(raw, dict):
            self.add(owner, f"{label} must be a JSON object")
            return set()
        for field in sorted({"result", "evidence"} - set(raw)):
            self.add(owner, f"{label} missing required field: {field}")
        for field in sorted(set(raw) - {"result", "evidence"}):
            self.add(owner, f"{label} has unknown field: {field}")
        result = raw.get("result")
        if result not in DUAL_VERDICTS:
            self.add(
                owner,
                f"{label}.result must use PASS, FAIL, BLOCKED or NOT_EXECUTED",
            )
        elif result != "PASS":
            self.add(owner, f"{label}.result must be PASS for an effective app profile")
        evidence = raw.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            self.add(owner, f"{label}.evidence must be a nonempty reference list")
            return set()
        paths: set[str] = set()
        for index, reference in enumerate(evidence):
            evidence_label = f"{label}.evidence[{index}]"
            if isinstance(reference, dict) and isinstance(reference.get("path"), str):
                paths.add(reference["path"])
            evidence_path = self.validate_file_reference(
                reference,
                owner,
                evidence_label,
            )
            if evidence_path is not None:
                self.validate_skill_eval_axis_evidence(
                    evidence_path,
                    current_revision,
                    case_id,
                    axis,
                    result,
                    expected_input_digests,
                    case_input_sha256,
                    stale_after_days,
                    expected_disposition,
                    expected_failure,
                )
        return paths

    def validate_adversarial_eval_fixture(
        self,
        path: Path,
        expected_disposition: Any,
        expected_failure: Any,
    ) -> None:
        data = self.load_json(path, "skill evaluation adversarial fixture")
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, "skill evaluation adversarial fixture must be a JSON object")
            return
        required = {
            "schema_version",
            "adversarial",
            "scenario",
            "expected_disposition",
            "expected_failure",
        }
        for field in sorted(required - set(data)):
            self.add(path, f"skill evaluation adversarial fixture missing required field: {field}")
        for field in sorted(set(data) - required):
            self.add(path, f"skill evaluation adversarial fixture has unknown field: {field}")
        if data.get("schema_version") != "1.0.0":
            self.add(path, "skill evaluation adversarial fixture schema_version must equal 1.0.0")
        if data.get("adversarial") is not True:
            self.add(path, "skill evaluation adversarial fixture adversarial must equal true")
        scenario = data.get("scenario")
        if not isinstance(scenario, str) or not scenario.strip():
            self.add(path, "skill evaluation adversarial fixture scenario must be nonempty")
        if data.get("expected_disposition") != expected_disposition:
            self.add(path, "skill evaluation adversarial fixture disposition is misbound")
        if data.get("expected_failure") != expected_failure:
            self.add(path, "skill evaluation adversarial fixture failure is misbound")

    def validate_skill_eval_axis_evidence(
        self,
        path: Path,
        current_revision: Any,
        case_id: Any,
        axis: str,
        expected_result: Any,
        expected_input_digests: dict[str, Any],
        case_input_sha256: str,
        stale_after_days: int | None,
        expected_disposition: Any,
        expected_failure: Any,
    ) -> None:
        data = self.load_json(path, "skill evaluation axis evidence")
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, "skill evaluation axis evidence must be a JSON object")
            return
        required = {
            "schema_version",
            "source_revision",
            "case_id",
            "axis",
            "result",
            "input_digests",
            "case_input_sha256",
            "run_id",
            "actor",
            "toolchain",
            "environment",
            "observed_at",
        }
        if expected_disposition is not None or expected_failure is not None:
            required.update({"observed_disposition", "observed_failure"})
        for field in sorted(required - set(data)):
            self.add(path, f"skill evaluation axis evidence missing required field: {field}")
        for field in sorted(set(data) - required):
            self.add(path, f"skill evaluation axis evidence has unknown field: {field}")
        if data.get("schema_version") != "1.0.0":
            self.add(path, "skill evaluation axis evidence schema_version must equal 1.0.0")
        if data.get("source_revision") != current_revision:
            self.add(path, "skill evaluation axis evidence source_revision is stale")
        if data.get("case_id") != case_id:
            self.add(path, "skill evaluation axis evidence case_id is misbound")
        if data.get("axis") != axis:
            self.add(path, "skill evaluation axis evidence axis is misbound")
        if data.get("result") != expected_result or data.get("result") != "PASS":
            self.add(path, "skill evaluation axis evidence result must equal PASS case verdict")
        if data.get("case_input_sha256") != case_input_sha256:
            self.add(path, "skill evaluation axis evidence case_input_sha256 is stale or misbound")
        if expected_disposition is not None or expected_failure is not None:
            if data.get("observed_disposition") != expected_disposition:
                self.add(
                    path,
                    "skill evaluation axis evidence observed_disposition is misbound",
                )
            if data.get("observed_failure") != expected_failure:
                self.add(
                    path,
                    "skill evaluation axis evidence observed_failure is misbound",
                )
        self.validate_input_digests(
            path,
            "skill evaluation axis evidence input_digests",
            data.get("input_digests"),
            expected_input_digests,
        )
        self.validate_provenance(
            path,
            "skill evaluation axis evidence",
            data,
            stale_after_days,
        )


def validate_app_profile(
    profile_path: Path,
    repo_root: Path,
    *,
    expected_revision: str | None = None,
    expected_blueprint_revision: str | None = None,
) -> list[Finding]:
    """Return deterministic findings for one repository-local app profile.

    Both expected revisions are required for a zero-finding, effective result;
    callers that omit either receive an explicit non-qualifying finding.
    """

    return AppProfileValidator(
        profile_path,
        repo_root,
        expected_revision=expected_revision,
        expected_blueprint_revision=expected_blueprint_revision,
    ).validate()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", type=Path, help="application-profile JSON path")
    parser.add_argument(
        "--repo-root",
        required=True,
        type=Path,
        help="explicit repository root used to resolve every manifest path",
    )
    parser.add_argument(
        "--expected-revision",
        required=True,
        help="exact immutable current source revision",
    )
    parser.add_argument(
        "--expected-blueprint-revision",
        required=True,
        help="exact immutable content revision of the selected blueprint package",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    findings = validate_app_profile(
        args.profile,
        args.repo_root,
        expected_revision=args.expected_revision,
        expected_blueprint_revision=args.expected_blueprint_revision,
    )
    for finding in findings:
        print(finding.render())
    print(f"app-profile-quality: findings={len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
