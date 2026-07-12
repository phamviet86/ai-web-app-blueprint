#!/usr/bin/env python3
"""Validate authored preset packages using only the Python standard library.

The catalog may intentionally contain no presets. A preset is discovered only
when a direct child of the supplied root contains ``preset.json``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit


SEMVER = re.compile(
    r"^(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)"
    r"(?:-[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
KEBAB_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]*\]\((?P<target>[^)]+)\)")
HEADING = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*#*\s*$")
EXTERNAL_SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)
RFC3339 = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$"
)

STATUSES = {"experimental", "candidate", "verified", "deprecated", "retired"}
REQUIRED_SKILLS = {
    "analyze-request",
    "lib",
    "shared",
    "feature",
    "app",
    "new-pattern",
    "ui",
}
REQUIRED_HEADINGS = {
    "inputs",
    "workflow",
    "completion criteria",
    "verification",
    "stop conditions",
}
REQUIRED_EVAL_KINDS = {
    "single-layer",
    "cross-layer",
    "new-pattern",
    "unsafe-boundary",
    "ui-research",
}
PROHIBITED_SKILL_FILES = {
    "readme.md",
    "changelog.md",
    "quick_reference.md",
    "installation_guide.md",
}
CORE_FIELDS = {
    "schema_version",
    "preset_id",
    "preset_version",
    "blueprint_version",
    "blueprint_revision",
    "status",
    "archetype",
    "stack",
    "capabilities",
    "verified_flows",
    "materialization",
    "skills",
    "patterns",
    "sources",
    "design",
    "verification",
}
OPTIONAL_FIELDS = {"$schema", "prerequisites", "compatibility", "upgrade_policy"}
SKILL_FIELDS = {"name", "path", "sha256", "invocation", "targets"}
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


@dataclass(frozen=True)
class Counts:
    presets: int = 0
    skills: int = 0
    patterns: int = 0


class PresetValidator:
    def __init__(self, presets_root: Path):
        self.root = presets_root.resolve()
        self.findings: list[Finding] = []
        self.skill_count = 0
        self.pattern_count = 0

    def display(self, path: Path) -> str:
        try:
            return str(path.resolve().relative_to(self.root))
        except (OSError, ValueError):
            return str(path)

    def add(self, path: Path, message: str, line: int = 1) -> None:
        self.findings.append(Finding(self.display(path), line, message))

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

    @staticmethod
    def is_safe_relative(raw: Any) -> bool:
        if (
            not isinstance(raw, str)
            or not raw.strip()
            or "\\" in raw
            or any(ord(character) < 32 or ord(character) == 127 for character in raw)
        ):
            return False
        if raw.startswith("/") or re.match(r"^[A-Za-z]:", raw):
            return False
        if ":" in raw:
            return False
        for part in raw.split("/"):
            if part in {"", ".", ".."} or part.endswith((".", " ")):
                return False
            if part.split(".", 1)[0].casefold() in WINDOWS_RESERVED:
                return False
        return True

    def safe_path(
        self,
        preset: Path,
        raw: Any,
        owner: Path,
        label: str,
        *,
        kind: str | None = None,
    ) -> Path | None:
        if not isinstance(raw, str) or not raw.strip():
            self.add(owner, f"{label} must be a nonempty relative path")
            return None
        if not self.is_safe_relative(raw):
            self.add(owner, f"{label} must be a portable POSIX-relative path")
            return None
        candidate_raw = Path(raw)
        try:
            lexical = preset
            for part in candidate_raw.parts:
                lexical /= part
                if lexical.is_symlink():
                    self.add(owner, f"{label} must not traverse a symbolic link")
                    return None
            candidate = (preset / candidate_raw).resolve()
        except (OSError, ValueError) as error:
            if "embedded null" in str(error).lower():
                self.add(owner, f"{label} contains an invalid path character")
            else:
                self.add(owner, f"{label} cannot be resolved safely: {error}")
            return None
        try:
            candidate.relative_to(preset.resolve())
        except ValueError:
            self.add(owner, f"{label} escapes the preset")
            return None
        try:
            exists = candidate.exists()
            is_file = candidate.is_file()
            is_dir = candidate.is_dir()
        except OSError as error:
            self.add(owner, f"{label} cannot be inspected safely: {error}")
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
    def digest_path(target: Path) -> str:
        """Return a raw file digest or a deterministic directory-tree digest."""
        if target.is_file():
            return hashlib.sha256(target.read_bytes()).hexdigest()
        return PresetValidator.digest_tree(target, b"preset-skill-tree-v1")

    @staticmethod
    def digest_tree(target: Path, domain: bytes) -> str:
        """Return a domain-separated deterministic digest for a directory tree."""
        digest = hashlib.sha256()
        digest.update(domain + b"\0")
        entries = sorted(
            target.rglob("*"),
            key=lambda item: item.relative_to(target).as_posix().encode("utf-8"),
        )
        for path in entries:
            if path.is_symlink():
                raise ValueError(
                    f"directory digest does not permit symbolic links: "
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

    def check_digest(self, owner: Path, target: Path, raw: Any, label: str) -> None:
        if not isinstance(raw, str) or not SHA256.fullmatch(raw):
            self.add(owner, f"{label} must be a full SHA-256 digest")
            return
        try:
            actual = self.digest_path(target)
        except (OSError, ValueError) as error:
            self.add(owner, f"cannot compute {label}: {error}")
            return
        if actual.lower() != raw.lower():
            self.add(owner, f"stale {label}: expected {actual}")

    def validate(self) -> tuple[list[Finding], Counts]:
        if not self.root.exists():
            self.add(self.root, "presets root does not exist")
            return sorted(self.findings), Counts()
        if not self.root.is_dir():
            self.add(self.root, "presets root is not a directory")
            return sorted(self.findings), Counts()

        children = sorted(self.root.iterdir())
        presets: list[Path] = []
        for child in children:
            if child.is_symlink() and child.is_dir() and (child / "preset.json").is_file():
                self.add(child, "preset directory must not be a symbolic link")
                continue
            manifest = child / "preset.json"
            if child.is_dir() and manifest.is_symlink():
                self.add(manifest, "preset manifest must not be a symbolic link")
                continue
            if child.is_dir() and manifest.is_file():
                presets.append(child)
        for preset in presets:
            self.validate_preset(preset)
        return (
            sorted(set(self.findings)),
            Counts(len(presets), self.skill_count, self.pattern_count),
        )

    def validate_preset(self, preset: Path) -> None:
        manifest_path = preset / "preset.json"
        required = {
            "README.md": "file",
            "template": "dir",
            "guides": "dir",
            "patterns/catalog.json": "file",
            "design": "dir",
            "verification": "dir",
        }
        for relative, kind in required.items():
            path = preset / relative
            lexical = preset
            has_symlink = False
            for part in Path(relative).parts:
                lexical /= part
                if lexical.is_symlink():
                    self.add(path, "required preset path must not traverse a symbolic link")
                    has_symlink = True
                    break
            if has_symlink:
                continue
            if not path.exists():
                self.add(path, f"missing required preset {kind}")
            elif kind == "file" and not path.is_file():
                self.add(path, "required preset path must be a file")
            elif kind == "dir" and not path.is_dir():
                self.add(path, "required preset path must be a directory")

        manifest = self.load_json(manifest_path, "preset manifest")
        if not isinstance(manifest, dict):
            if manifest is not None:
                self.add(manifest_path, "preset manifest must be a JSON object")
            return

        for field in sorted(CORE_FIELDS - manifest.keys()):
            self.add(manifest_path, f"missing required manifest field: {field}")
        for field in sorted(manifest.keys() - CORE_FIELDS - OPTIONAL_FIELDS):
            self.add(manifest_path, f"unknown manifest field: {field}")
        self.validate_optional_sections(preset, manifest_path, manifest)

        preset_id = manifest.get("preset_id")
        if preset_id != preset.name:
            self.add(manifest_path, "preset_id must equal its directory name")
        if (
            not isinstance(preset_id, str)
            or len(preset_id) > 47
            or not KEBAB_NAME.fullmatch(preset_id)
        ):
            self.add(manifest_path, "preset_id must be a <=47 character lowercase kebab name")

        schema_version = manifest.get("schema_version")
        if not isinstance(schema_version, str) or not SEMVER.fullmatch(schema_version):
            self.add(manifest_path, "schema_version must be an exact semantic version")
        for field in ("preset_version", "blueprint_version"):
            value = manifest.get(field)
            if not isinstance(value, str) or not SEMVER.fullmatch(value):
                self.add(manifest_path, f"{field} must be an exact semantic version")
        revision = manifest.get("blueprint_revision")
        if not isinstance(revision, str) or not SHA40.fullmatch(revision):
            self.add(manifest_path, "blueprint_revision must be a full immutable 40-character SHA")
        status = manifest.get("status")
        if status not in STATUSES:
            self.add(manifest_path, f"status must be one of: {', '.join(sorted(STATUSES))}")
        elif status in {"candidate", "verified"} and "upgrade_policy" not in manifest:
            self.add(manifest_path, f"{status} preset requires upgrade_policy")
        archetype = manifest.get("archetype")
        if not isinstance(archetype, str) or not KEBAB_NAME.fullmatch(archetype):
            self.add(manifest_path, "archetype must be lowercase kebab-case")

        self.validate_capabilities(
            preset,
            manifest_path,
            manifest.get("capabilities"),
            status if isinstance(status, str) else "",
        )
        self.validate_flows(
            preset,
            manifest_path,
            manifest.get("verified_flows"),
            status if isinstance(status, str) else "",
        )
        self.validate_materialization(preset, manifest_path, manifest.get("materialization"))

        stack_source_ids = self.validate_stack(manifest_path, manifest.get("stack"))
        skills, known_skill_refs = self.validate_skills(
            preset, manifest_path, preset_id, manifest.get("skills")
        )
        self.skill_count += len(skills)
        self.validate_patterns(
            preset,
            manifest_path,
            manifest.get("patterns"),
            known_skill_refs,
            status if isinstance(status, str) else "",
        )
        source_records = self.validate_sources(
            preset, manifest_path, manifest.get("sources")
        )
        source_ids = set(source_records)
        for source_id in sorted(stack_source_ids - source_ids):
            self.add(manifest_path, f"stack references unknown source_id: {source_id}")
        for source_id in sorted(stack_source_ids & source_ids):
            if source_records[source_id].get("kind") not in {"official-docs", "context7"}:
                self.add(
                    manifest_path,
                    f"stack source_id {source_id} must resolve to official-docs or context7",
                )
        self.validate_design(
            preset,
            manifest_path,
            manifest.get("design"),
            status if isinstance(status, str) else "",
            {
                source_id: str(record.get("kind", ""))
                for source_id, record in source_records.items()
            },
        )
        self.validate_cross_contracts(
            preset,
            manifest_path,
            manifest,
            status if isinstance(status, str) else "",
            source_records,
        )
        self.validate_verification(
            preset,
            manifest_path,
            manifest.get("verification"),
            known_skill_refs,
            status if isinstance(status, str) else "",
        )

    def validate_stack(self, owner: Path, raw: Any) -> set[str]:
        source_ids: set[str] = set()
        if not isinstance(raw, list) or not raw:
            self.add(owner, "stack must be a nonempty list")
            return source_ids
        seen: set[str] = set()
        for index, entry in enumerate(raw):
            label = f"stack[{index}]"
            if not isinstance(entry, dict):
                self.add(owner, f"{label} must be an object")
                continue
            for field in sorted({"package", "version", "source_id"} - entry.keys()):
                self.add(owner, f"{label} missing required field: {field}")
            for field in sorted(entry.keys() - {"package", "version", "source_id"}):
                self.add(owner, f"{label} has unknown field: {field}")
            identity = entry.get("package")
            if not isinstance(identity, str) or not identity.strip():
                self.add(owner, f"{label}.package must be nonempty")
            elif identity in seen:
                self.add(owner, f"duplicate stack identity: {identity}")
            else:
                seen.add(identity)
            version = entry.get("version")
            if not isinstance(version, str) or not SEMVER.fullmatch(version):
                self.add(owner, f"{label}.version must be an exact semantic version")
            source_id = entry.get("source_id")
            if not isinstance(source_id, str) or not KEBAB_NAME.fullmatch(source_id):
                self.add(owner, f"{label}.source_id must be lowercase kebab-case")
            else:
                source_ids.add(source_id)
        return source_ids

    def validate_optional_sections(
        self, preset: Path, owner: Path, manifest: dict[str, Any]
    ) -> None:
        if "$schema" in manifest and (
            not isinstance(manifest["$schema"], str) or not manifest["$schema"].strip()
        ):
            self.add(owner, "$schema must be a nonempty string")

        prerequisites = manifest.get("prerequisites")
        if prerequisites is not None:
            if not isinstance(prerequisites, dict):
                self.add(owner, "prerequisites must be an object")
            else:
                expected = {"hard", "quality"}
                for field in sorted(expected - prerequisites.keys()):
                    self.add(owner, f"prerequisites missing required field: {field}")
                for field in sorted(prerequisites.keys() - expected):
                    self.add(owner, f"prerequisites has unknown field: {field}")
                for kind in ("hard", "quality"):
                    entries = prerequisites.get(kind)
                    if not isinstance(entries, list):
                        self.add(owner, f"prerequisites.{kind} must be a list")
                        continue
                    for index, entry in enumerate(entries):
                        self.validate_prerequisite(owner, kind, index, entry)

        compatibility = manifest.get("compatibility")
        if compatibility is not None:
            if not isinstance(compatibility, list):
                self.add(owner, "compatibility must be a list")
            else:
                expected = {"subject", "range", "status", "evidence"}
                for index, entry in enumerate(compatibility):
                    label = f"compatibility[{index}]"
                    if not isinstance(entry, dict):
                        self.add(owner, f"{label} must be an object")
                        continue
                    for field in sorted(expected - entry.keys()):
                        self.add(owner, f"{label} missing required field: {field}")
                    for field in sorted(entry.keys() - expected):
                        self.add(owner, f"{label} has unknown field: {field}")
                    for field in ("subject", "range"):
                        if not isinstance(entry.get(field), str) or not entry[field].strip():
                            self.add(owner, f"{label}.{field} must be nonempty")
                    if entry.get("status") not in {
                        "supported",
                        "conditional",
                        "unsupported",
                    }:
                        self.add(owner, f"{label}.status is invalid")
                    evidence = entry.get("evidence")
                    if not isinstance(evidence, list):
                        self.add(owner, f"{label}.evidence must be a list")
                    else:
                        for evidence_index, reference in enumerate(evidence):
                            self.ref_path(
                                preset,
                                owner,
                                reference,
                                f"{label}.evidence[{evidence_index}]",
                            )

        upgrade = manifest.get("upgrade_policy")
        if upgrade is not None:
            expected = {"strategy", "breaking_change_policy", "stale_after_days"}
            if not isinstance(upgrade, dict):
                self.add(owner, "upgrade_policy must be an object")
            else:
                for field in sorted(expected - upgrade.keys()):
                    self.add(owner, f"upgrade_policy missing required field: {field}")
                for field in sorted(upgrade.keys() - expected):
                    self.add(owner, f"upgrade_policy has unknown field: {field}")
                if upgrade.get("strategy") != "explicit-merge":
                    self.add(owner, "upgrade_policy.strategy must be explicit-merge")
                if upgrade.get("breaking_change_policy") != "require-decision":
                    self.add(
                        owner,
                        "upgrade_policy.breaking_change_policy must be require-decision",
                    )
                stale_days = upgrade.get("stale_after_days")
                if not isinstance(stale_days, int) or isinstance(stale_days, bool) or stale_days < 1:
                    self.add(owner, "upgrade_policy.stale_after_days must be a positive integer")

    def validate_prerequisite(
        self, owner: Path, kind: str, index: int, entry: Any
    ) -> None:
        label = f"prerequisites.{kind}[{index}]"
        required = {"id", "check", "recovery"}
        allowed = required | {"fallback"}
        if not isinstance(entry, dict):
            self.add(owner, f"{label} must be an object")
            return
        for field in sorted(required - entry.keys()):
            self.add(owner, f"{label} missing required field: {field}")
        if kind == "quality" and "fallback" not in entry:
            self.add(owner, f"{label} missing required field: fallback")
        for field in sorted(entry.keys() - allowed):
            self.add(owner, f"{label} has unknown field: {field}")
        prerequisite_id = entry.get("id")
        if not isinstance(prerequisite_id, str) or not KEBAB_NAME.fullmatch(prerequisite_id):
            self.add(owner, f"{label}.id must be lowercase kebab-case")
        for field in ("check", "recovery"):
            if not isinstance(entry.get(field), str) or not entry[field].strip():
                self.add(owner, f"{label}.{field} must be nonempty")
        if "fallback" in entry and (
            not isinstance(entry["fallback"], str) or not entry["fallback"].strip()
        ):
            self.add(owner, f"{label}.fallback must be nonempty")

    def validate_capabilities(
        self, preset: Path, owner: Path, raw: Any, status: str
    ) -> None:
        if not isinstance(raw, list) or not raw:
            self.add(owner, "capabilities must be a nonempty list")
            return
        required = {
            "id",
            "status",
            "providers",
            "consumers",
            "payloads",
            "states",
            "constraints",
            "patterns",
            "evidence",
        }
        seen: set[str] = set()
        verified_count = 0
        for index, entry in enumerate(raw):
            label = f"capabilities[{index}]"
            if isinstance(entry, str):
                capability_id = entry
                if not KEBAB_NAME.fullmatch(entry):
                    self.add(owner, f"{label} must be lowercase kebab-case")
                if status in {"candidate", "verified"}:
                    self.add(owner, f"{label} must be a capability object for {status}")
            elif isinstance(entry, dict):
                for field in sorted(required - entry.keys()):
                    self.add(owner, f"{label} missing required field: {field}")
                for field in sorted(entry.keys() - required):
                    self.add(owner, f"{label} has unknown field: {field}")
                capability_id = entry.get("id")
                if not isinstance(capability_id, str) or not KEBAB_NAME.fullmatch(capability_id):
                    self.add(owner, f"{label}.id must be lowercase kebab-case")
                if entry.get("status") not in {
                    "provided",
                    "verified",
                    "conditional",
                    "unsupported",
                }:
                    self.add(owner, f"{label}.status is invalid")
                elif entry.get("status") == "verified":
                    verified_count += 1
                for field in (
                    "providers",
                    "consumers",
                    "payloads",
                    "states",
                    "constraints",
                    "patterns",
                ):
                    value = entry.get(field)
                    if not isinstance(value, list) or not all(
                        isinstance(item, str) for item in value
                    ):
                        self.add(owner, f"{label}.{field} must be a string list")
                if (
                    status in {"candidate", "verified"}
                    and isinstance(entry.get("patterns"), list)
                    and not entry["patterns"]
                ):
                    self.add(owner, f"{label}.patterns must be nonempty")
                if (
                    status in {"candidate", "verified"}
                    and entry.get("status") == "verified"
                ):
                    for field in (
                        "providers",
                        "consumers",
                        "payloads",
                        "states",
                        "constraints",
                        "patterns",
                    ):
                        if isinstance(entry.get(field), list) and not entry[field]:
                            self.add(owner, f"{label}.{field} must be nonempty when verified")
                evidence = entry.get("evidence")
                if not isinstance(evidence, list):
                    self.add(owner, f"{label}.evidence must be a list")
                else:
                    require_evidence = (
                        status in {"candidate", "verified"}
                        and entry.get("status") == "verified"
                    )
                    if require_evidence and not evidence:
                        self.add(owner, f"{label}.evidence must prove the verified capability")
                    for evidence_index, reference in enumerate(evidence):
                        evidence_label = f"{label}.evidence[{evidence_index}]"
                        if require_evidence and not isinstance(reference, dict):
                            self.add(owner, f"{evidence_label} must include path and sha256")
                        path = self.ref_path(
                            preset,
                            owner,
                            reference,
                            evidence_label,
                        )
                        if path is not None and require_evidence:
                            self.validate_dual_verdict_evidence(
                                preset,
                                path,
                                "capability evidence",
                                status,
                                "capability",
                                str(capability_id),
                            )
            else:
                self.add(owner, f"{label} must be a kebab ID or capability object")
                continue
            if isinstance(capability_id, str):
                if capability_id in seen:
                    self.add(owner, f"duplicate capability id: {capability_id}")
                seen.add(capability_id)
        if status in {"candidate", "verified"} and verified_count == 0:
            self.add(owner, f"{status} preset requires at least one verified capability")

    def validate_flows(self, preset: Path, owner: Path, raw: Any, status: str) -> None:
        if not isinstance(raw, list):
            self.add(owner, "verified_flows must be a list")
            return
        if status in {"candidate", "verified"} and not raw:
            self.add(owner, f"{status} preset must declare verified_flows")
        required = {"id", "capability_id", "steps", "evidence"}
        seen: set[str] = set()
        for index, entry in enumerate(raw):
            label = f"verified_flows[{index}]"
            if isinstance(entry, str):
                flow_id = entry
                if not KEBAB_NAME.fullmatch(entry):
                    self.add(owner, f"{label} must be lowercase kebab-case")
                if status in {"candidate", "verified"}:
                    self.add(owner, f"{label} must be a verified-flow object for {status}")
            elif isinstance(entry, dict):
                for field in sorted(required - entry.keys()):
                    self.add(owner, f"{label} missing required field: {field}")
                for field in sorted(entry.keys() - required):
                    self.add(owner, f"{label} has unknown field: {field}")
                flow_id = entry.get("id")
                if not isinstance(flow_id, str) or not KEBAB_NAME.fullmatch(flow_id):
                    self.add(owner, f"{label}.id must be lowercase kebab-case")
                capability_id = entry.get("capability_id")
                if not isinstance(capability_id, str) or not KEBAB_NAME.fullmatch(
                    capability_id
                ):
                    self.add(owner, f"{label}.capability_id must be lowercase kebab-case")
                steps = entry.get("steps")
                if not isinstance(steps, list) or not steps or not all(
                    isinstance(item, str) and item.strip() for item in steps
                ):
                    self.add(owner, f"{label}.steps must be a nonempty string list")
                evidence = entry.get("evidence")
                if not isinstance(evidence, list) or not evidence:
                    self.add(owner, f"{label}.evidence must be a nonempty list")
                else:
                    for evidence_index, reference in enumerate(evidence):
                        evidence_label = f"{label}.evidence[{evidence_index}]"
                        if status in {"candidate", "verified"} and not isinstance(
                            reference, dict
                        ):
                            self.add(owner, f"{evidence_label} must include path and sha256")
                        path = self.ref_path(
                            preset,
                            owner,
                            reference,
                            evidence_label,
                        )
                        if path is not None and status in {"candidate", "verified"}:
                            self.validate_dual_verdict_evidence(
                                preset,
                                path,
                                "verified-flow evidence",
                                status,
                                "flow",
                                str(flow_id),
                            )
            else:
                self.add(owner, f"{label} must be a kebab ID or verified-flow object")
                continue
            if isinstance(flow_id, str):
                if flow_id in seen:
                    self.add(owner, f"duplicate verified flow id: {flow_id}")
                seen.add(flow_id)

    def validate_materialization(self, preset: Path, owner: Path, raw: Any) -> None:
        if not isinstance(raw, (dict, list)) or not raw:
            self.add(owner, "materialization must be a nonempty object or list")
            return
        entries = list(raw.values()) if isinstance(raw, dict) else raw
        targets: list[tuple[str, ...]] = []
        for index, entry in enumerate(entries):
            label = f"materialization[{index}]"
            if isinstance(entry, str):
                self.safe_path(preset, entry, owner, label)
                continue
            if not isinstance(entry, dict):
                self.add(owner, f"{label} must be a path or materialization object")
                continue
            required = {"source", "target", "operation", "conflict_policy", "sha256"}
            for field in sorted(required - entry.keys()):
                self.add(owner, f"{label} missing required field: {field}")
            for field in sorted(entry.keys() - required):
                self.add(owner, f"{label} has unknown field: {field}")
            source = self.safe_path(preset, entry.get("source"), owner, f"{label}.source")
            target = entry.get("target")
            if not self.is_safe_relative(target):
                self.add(owner, f"{label}.target must be a portable POSIX-relative path")
            else:
                parts = tuple(part.casefold() for part in target.split("/"))
                for prior in targets:
                    common = min(len(parts), len(prior))
                    if parts[:common] == prior[:common]:
                        self.add(
                            owner,
                            f"{label}.target overlaps another materialization target: {target}",
                        )
                        break
                targets.append(parts)
            if entry.get("operation") not in {"create", "merge", "replace"}:
                self.add(owner, f"{label}.operation is invalid")
            if entry.get("conflict_policy") not in {
                "fail",
                "require-decision",
                "verified-merge",
            }:
                self.add(owner, f"{label}.conflict_policy is invalid")
            if source is not None:
                self.check_digest(owner, source, entry.get("sha256"), f"{label}.sha256")

    def validate_skills(
        self, preset: Path, owner: Path, preset_id: Any, raw: Any
    ) -> tuple[dict[str, dict[str, Any]], set[str]]:
        if not isinstance(raw, dict):
            self.add(owner, "skills must be an object keyed by capability")
            return {}, set()
        skills = {key: value for key, value in raw.items() if isinstance(value, dict)}
        for key, value in raw.items():
            if not isinstance(value, dict):
                self.add(owner, f"skill {key} must be an object")
        for capability in sorted(REQUIRED_SKILLS - raw.keys()):
            self.add(owner, f"missing required skill capability: {capability}")

        known: set[str] = set(raw)
        seen_names: set[str] = set()
        seen_paths: set[str] = set()
        for capability, record in sorted(skills.items()):
            for field in sorted(SKILL_FIELDS - record.keys()):
                self.add(owner, f"skill {capability} missing required field: {field}")
            for field in sorted(record.keys() - SKILL_FIELDS):
                self.add(owner, f"skill {capability} has unknown field: {field}")
            name = record.get("name")
            if isinstance(name, str):
                known.add(name)
                if name in seen_names:
                    self.add(owner, f"duplicate skill name: {name}")
                seen_names.add(name)
            expected_name = (
                f"{preset_id}-{capability}" if isinstance(preset_id, str) else None
            )
            if (
                not isinstance(name, str)
                or len(name) >= 64
                or not KEBAB_NAME.fullmatch(name)
                or name != expected_name
            ):
                self.add(
                    owner,
                    f"skill {capability} name must equal the <64 character canonical name: {expected_name}",
                )

            invocation = record.get("invocation")
            if not self.valid_invocation(invocation):
                self.add(owner, f"skill {capability} invocation must be nonempty")
            targets = record.get("targets")
            if (
                not isinstance(targets, list)
                or not targets
                or not all(
                    isinstance(item, str)
                    and item == item.strip().lower()
                    and KEBAB_NAME.fullmatch(item)
                    for item in targets
                )
                or len(targets) != len(set(targets))
            ):
                self.add(owner, f"skill {capability} targets must be a unique nonempty string list")
                targets = []

            raw_path = record.get("path")
            if isinstance(raw_path, str):
                if raw_path in seen_paths:
                    self.add(owner, f"duplicate skill path: {raw_path}")
                seen_paths.add(raw_path)
            skill_dir = self.safe_path(
                preset, raw_path, owner, f"skill {capability} path", kind="dir"
            )
            if skill_dir is None:
                continue
            expected_path = f"guides/{name}" if isinstance(name, str) else None
            if record.get("path") != expected_path:
                self.add(
                    owner,
                    f"skill {capability} path must equal guides/<manifest-name>: {expected_path}",
                )
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                self.add(skill_file, f"skill {capability} path must contain SKILL.md")
                continue
            self.check_digest(owner, skill_dir, record.get("sha256"), f"skill {capability} sha256")
            self.validate_skill_file(preset, skill_dir, skill_file, capability, name)
            if any(target.lower() == "codex" for target in targets):
                openai_yaml = skill_dir / "agents/openai.yaml"
                if not openai_yaml.is_file():
                    self.add(openai_yaml, f"Codex skill {capability} requires agents/openai.yaml")
                else:
                    self.validate_openai_metadata(openai_yaml, name)
        return skills, known

    def validate_openai_metadata(self, path: Path, skill_name: Any) -> None:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            self.add(path, f"agents/openai.yaml is not UTF-8: {error}")
            return
        except OSError as error:
            self.add(path, f"cannot read agents/openai.yaml: {error}")
            return
        if not re.search(r"(?m)^interface:\s*$", text):
            self.add(path, "agents/openai.yaml requires an interface mapping")
        values: dict[str, str] = {}
        for key in ("display_name", "short_description", "default_prompt"):
            match = re.search(rf"(?m)^\s{{2}}{key}:\s*(.+?)\s*$", text)
            if not match:
                self.add(path, f"agents/openai.yaml missing interface.{key}")
                continue
            value = match.group(1).strip().strip("'\"")
            if not value:
                self.add(path, f"agents/openai.yaml interface.{key} must be nonempty")
            values[key] = value
        short = values.get("short_description", "")
        if len(short) > 80:
            self.add(path, "agents/openai.yaml short_description must be <=80 characters")
        prompt = values.get("default_prompt", "")
        if isinstance(skill_name, str) and f"${skill_name}" not in prompt:
            self.add(path, f"agents/openai.yaml default_prompt must mention ${skill_name}")

    @staticmethod
    def nonempty(value: Any) -> bool:
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, dict)):
            return bool(value)
        return False

    @staticmethod
    def valid_invocation(value: Any) -> bool:
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, list):
            if not value or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                return False
            return len(value) == len(set(value))
        if isinstance(value, dict):
            return bool(value) and all(
                isinstance(key, str)
                and key.strip()
                and isinstance(item, str)
                and item.strip()
                for key, item in value.items()
            )
        return False

    def parse_skill_frontmatter(
        self, skill_file: Path, lines: list[str]
    ) -> tuple[dict[str, str], int]:
        if not lines or lines[0].strip() != "---":
            self.add(skill_file, "SKILL.md must start with YAML frontmatter")
            return {}, 0
        try:
            end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
        except StopIteration:
            self.add(skill_file, "SKILL.md frontmatter has no closing delimiter")
            return {}, 0
        metadata: dict[str, str] = {}
        malformed = False
        for index in range(1, end):
            raw = lines[index]
            if not raw.strip():
                continue
            match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):\s*(.+)", raw)
            if not match or match.group(1) in metadata:
                self.add(skill_file, "malformed or duplicate SKILL.md frontmatter field", index + 1)
                malformed = True
                continue
            key, value = match.groups()
            value = value.strip()
            quoted = (
                len(value) >= 2
                and value[0] == value[-1]
                and value[0] in {"'", '"'}
            )
            if not quoted and (
                value.startswith(("{", "[", "&", "*", "!", "|", ">", "- "))
                or value in {"null", "Null", "NULL", "~"}
            ):
                self.add(
                    skill_file,
                    "SKILL.md frontmatter values must be plain or quoted scalar strings",
                    index + 1,
                )
                malformed = True
            if quoted:
                value = value[1:-1]
            metadata[key] = value
        if set(metadata) != {"name", "description"} or malformed:
            self.add(skill_file, "SKILL.md frontmatter must contain exactly name and description")
        return metadata, end

    def validate_skill_file(
        self,
        preset: Path,
        skill_dir: Path,
        skill_file: Path,
        capability: str,
        manifest_name: Any,
    ) -> None:
        try:
            text = skill_file.read_text(encoding="utf-8")
        except UnicodeDecodeError as error:
            self.add(skill_file, f"SKILL.md is not UTF-8: {error}")
            return
        except OSError as error:
            self.add(skill_file, f"cannot read SKILL.md: {error}")
            return
        lines = text.splitlines()
        if len(lines) > 500:
            self.add(skill_file, f"SKILL.md exceeds 500 lines ({len(lines)})")
        metadata, frontmatter_end = self.parse_skill_frontmatter(skill_file, lines)
        if metadata.get("name") != manifest_name:
            self.add(skill_file, f"SKILL.md name does not match manifest skill {capability}")
        description = metadata.get("description", "")
        if "Use when" not in description:
            self.add(skill_file, "SKILL.md description must contain a 'Use when' trigger clause")

        headings: set[str] = set()
        for line in lines[frontmatter_end + 1 :]:
            match = HEADING.match(line)
            if match:
                title = re.sub(r"[`*_]", "", match.group("title")).strip().lower()
                headings.add(title)
        for heading in sorted(REQUIRED_HEADINGS - headings):
            self.add(skill_file, f"SKILL.md missing required heading: {heading.title()}")

        for path in sorted(skill_dir.rglob("*")):
            if path.is_file() and path.name.lower() in PROHIBITED_SKILL_FILES:
                self.add(path, f"prohibited file inside skill: {path.name}")

        direct_links: set[Path] = set()
        for match in MARKDOWN_LINK.finditer("\n".join(lines[frontmatter_end + 1 :])):
            target = self.link_path(match.group("target"))
            if not target or target.startswith("#") or EXTERNAL_SCHEME.match(target):
                continue
            split = urlsplit(target)
            if not split.path.lower().endswith(".md"):
                continue
            try:
                resolved = (skill_file.parent / unquote(split.path)).resolve()
            except (OSError, ValueError) as error:
                self.add(skill_file, f"invalid Markdown reference path: {target} ({error})")
                continue
            try:
                resolved.relative_to(preset.resolve())
            except ValueError:
                self.add(skill_file, f"Markdown reference escapes the preset: {target}")
                continue
            direct_links.add(resolved)
            if not resolved.is_file():
                self.add(skill_file, f"unresolved Markdown reference: {target}")

        references = skill_dir / "references"
        if references.is_dir():
            for reference in sorted(references.rglob("*.md")):
                if reference.resolve() not in direct_links:
                    self.add(reference, "reference Markdown must be directly linked from SKILL.md")

    @staticmethod
    def link_path(raw: str) -> str:
        raw = raw.strip()
        if raw.startswith("<") and ">" in raw:
            return raw[1 : raw.index(">")]
        try:
            parts = shlex.split(raw)
        except ValueError:
            parts = raw.split()
        return parts[0] if parts else ""

    def validate_patterns(
        self,
        preset: Path,
        owner: Path,
        raw: Any,
        known_skills: set[str],
        status: str,
    ) -> None:
        if not isinstance(raw, dict):
            self.add(owner, "patterns must be an object with catalog and sha256")
            return
        catalog_path = self.safe_path(
            preset, raw.get("catalog"), owner, "patterns.catalog", kind="file"
        )
        if raw.get("catalog") != "patterns/catalog.json":
            self.add(owner, "patterns.catalog must be patterns/catalog.json")
        if catalog_path is None:
            return
        try:
            actual = self.digest_tree(preset / "patterns", b"preset-pattern-tree-v1")
        except (OSError, ValueError) as error:
            self.add(owner, f"cannot compute patterns.sha256: {error}")
        else:
            digest = raw.get("sha256")
            if not isinstance(digest, str) or not SHA256.fullmatch(digest):
                self.add(owner, "patterns.sha256 must be a full SHA-256 digest")
            elif digest != actual:
                self.add(owner, f"stale patterns.sha256: expected {actual}")
        data = self.load_json(catalog_path, "pattern catalog")
        entries = self.records(data, "patterns", catalog_path, "pattern catalog")
        if entries is None:
            return
        self.pattern_count += len(entries)
        seen: set[str] = set()
        for index, entry in enumerate(entries):
            label = f"pattern[{index}]"
            if not isinstance(entry, dict):
                self.add(catalog_path, f"{label} must be an object")
                continue
            pattern_id = entry.get("id")
            if not isinstance(pattern_id, str) or not pattern_id.strip():
                self.add(catalog_path, f"{label}.id must be nonempty")
            elif pattern_id in seen:
                self.add(catalog_path, f"duplicate pattern id: {pattern_id}")
            else:
                seen.add(pattern_id)
            if not isinstance(entry.get("layer"), str) or not entry["layer"].strip():
                self.add(catalog_path, f"{label}.layer must be nonempty")
            skill_refs = entry.get("skills")
            if not isinstance(skill_refs, list) or not skill_refs:
                self.add(catalog_path, f"{label}.skills must be a nonempty list")
            else:
                for skill_ref in skill_refs:
                    if not isinstance(skill_ref, str) or skill_ref not in known_skills:
                        self.add(catalog_path, f"{label} references unknown skill: {skill_ref}")
            dependency_validity: dict[str, bool] = {}
            for field in ("allowed_dependencies", "forbidden_dependencies"):
                value = entry.get(field)
                valid = isinstance(value, list) and all(
                    isinstance(item, str) for item in value
                )
                dependency_validity[field] = valid
                if not valid:
                    self.add(catalog_path, f"{label}.{field} must be a string list")
            allowed = entry.get("allowed_dependencies", [])
            forbidden = entry.get("forbidden_dependencies", [])
            if all(dependency_validity.values()):
                overlap = sorted(set(allowed) & set(forbidden))
                if overlap:
                    self.add(catalog_path, f"{label} allows and forbids: {', '.join(overlap)}")
            self.validate_path_list(
                preset, catalog_path, entry.get("examples"), f"{label}.examples", nonempty=True
            )
            self.safe_path(
                preset, entry.get("verifier"), catalog_path, f"{label}.verifier", kind="file"
            )
            fixtures = entry.get("fixtures")
            if not isinstance(fixtures, dict):
                self.add(catalog_path, f"{label}.fixtures must be an object")
            else:
                for polarity in ("positive", "negative"):
                    self.validate_path_list(
                        preset,
                        catalog_path,
                        fixtures.get(polarity),
                        f"{label}.fixtures.{polarity}",
                        nonempty=True,
                    )
            if status in {"candidate", "verified"}:
                intent = entry.get("intent")
                if not isinstance(intent, str) or not intent.strip():
                    self.add(catalog_path, f"{label}.intent must be nonempty")
                applicability = entry.get("applicability")
                if not isinstance(applicability, dict):
                    self.add(catalog_path, f"{label}.applicability must be an object")
                else:
                    for field, nonempty in (("use_when", True), ("avoid_when", False)):
                        value = applicability.get(field)
                        if (
                            not isinstance(value, list)
                            or (nonempty and not value)
                            or not all(isinstance(item, str) and item.strip() for item in value)
                        ):
                            self.add(
                                catalog_path,
                                f"{label}.applicability.{field} must be a "
                                f"{'nonempty ' if nonempty else ''}string list",
                            )
                public_contract = entry.get("public_contract")
                if not isinstance(public_contract, dict):
                    self.add(catalog_path, f"{label}.public_contract must be an object")
                else:
                    for field in ("inputs", "outputs", "states"):
                        value = public_contract.get(field)
                        if not isinstance(value, list) or not value or not all(
                            isinstance(item, str) and item.strip() for item in value
                        ):
                            self.add(
                                catalog_path,
                                f"{label}.public_contract.{field} must be a nonempty string list",
                            )
                evidence = entry.get("evidence")
                if not isinstance(evidence, list) or not evidence:
                    self.add(catalog_path, f"{label}.evidence must be a nonempty list")
                else:
                    for evidence_index, reference in enumerate(evidence):
                        evidence_label = f"{label}.evidence[{evidence_index}]"
                        if not isinstance(reference, dict):
                            self.add(
                                catalog_path,
                                f"{evidence_label} must include path and sha256",
                            )
                        path = self.ref_path(
                            preset, catalog_path, reference, evidence_label
                        )
                        if path is not None:
                            self.validate_dual_verdict_evidence(
                                preset,
                                path,
                                "pattern evidence",
                                status,
                                "pattern",
                                str(pattern_id),
                            )

    def validate_path_list(
        self,
        preset: Path,
        owner: Path,
        raw: Any,
        label: str,
        *,
        nonempty: bool,
    ) -> None:
        if (
            not isinstance(raw, list)
            or (nonempty and not raw)
            or not all(isinstance(item, str) and item.strip() for item in raw)
        ):
            qualifier = "nonempty " if nonempty else ""
            self.add(owner, f"{label} must be a {qualifier}path list")
            return
        for item in raw:
            self.safe_path(preset, item, owner, label)

    def validate_sources(
        self, preset: Path, owner: Path, raw: Any
    ) -> dict[str, dict[str, Any]]:
        if not isinstance(raw, dict):
            self.add(owner, "sources must be an object with ledger and sha256")
            return {}
        expected = {"ledger", "sha256"}
        for field in sorted(expected - raw.keys()):
            self.add(owner, f"sources missing required field: {field}")
        for field in sorted(raw.keys() - expected):
            self.add(owner, f"sources has unknown field: {field}")
        ledger_path = self.safe_path(
            preset, raw.get("ledger"), owner, "sources.ledger", kind="file"
        )
        if ledger_path is None:
            return {}
        self.check_digest(owner, ledger_path, raw.get("sha256"), "sources.sha256")
        data = self.load_json(ledger_path, "source ledger")
        entries = self.records(data, "sources", ledger_path, "source ledger")
        if entries is None:
            return {}
        required = {
            "id",
            "kind",
            "url",
            "requested_ref",
            "resolved_revision",
            "retrieved_at",
            "license",
            "claims",
            "invalidation_triggers",
        }
        source_ids: set[str] = set()
        source_records: dict[str, dict[str, Any]] = {}
        for index, entry in enumerate(entries):
            label = f"source[{index}]"
            if not isinstance(entry, dict):
                self.add(ledger_path, f"{label} must be an object")
                continue
            for field in sorted(required - entry.keys()):
                self.add(ledger_path, f"{label} missing required field: {field}")
            for field in required - {"claims", "invalidation_triggers"}:
                if field in entry and (
                    not isinstance(entry[field], str) or not entry[field].strip()
                ):
                    self.add(ledger_path, f"{label}.{field} must be a nonempty string")
            for field in ("claims", "invalidation_triggers"):
                value = entry.get(field)
                if (
                    not isinstance(value, list)
                    or not value
                    or not all(isinstance(item, str) and item.strip() for item in value)
                ):
                    self.add(ledger_path, f"{label}.{field} must be a nonempty string list")
            source_id = entry.get("id")
            if isinstance(source_id, str) and KEBAB_NAME.fullmatch(source_id):
                if source_id in source_ids:
                    self.add(ledger_path, f"duplicate source id: {source_id}")
                source_ids.add(source_id)
                source_records[source_id] = entry
            elif source_id is not None:
                self.add(ledger_path, f"{label}.id must be lowercase kebab-case")
            retrieved_at = entry.get("retrieved_at")
            if retrieved_at is not None and not self.valid_timestamp(retrieved_at):
                self.add(
                    ledger_path,
                    f"{label}.retrieved_at must be timezone-aware RFC 3339",
                )
            resolved_revision = entry.get("resolved_revision")
            if resolved_revision is not None and not self.immutable_revision(
                resolved_revision
            ):
                self.add(
                    ledger_path,
                    f"{label}.resolved_revision must be an exact SemVer or immutable SHA",
                )
            kind = entry.get("kind")
            if kind == "context7":
                for field in ("library_id", "queries", "official_urls"):
                    value = entry.get(field)
                    if field == "library_id":
                        valid = isinstance(value, str) and bool(value.strip())
                    else:
                        valid = (
                            isinstance(value, list)
                            and bool(value)
                            and all(isinstance(item, str) and item.strip() for item in value)
                        )
                    if not valid:
                        self.add(ledger_path, f"{label} Context7 source requires {field}")
            if kind == "ux-heuristic" and entry.get("acquisition_mode") != "read-only":
                self.add(ledger_path, f"{label} ux-heuristic acquisition_mode must be read-only")
        return source_records

    def validate_design(
        self,
        preset: Path,
        owner: Path,
        raw: Any,
        status: str,
        source_kinds: dict[str, str],
    ) -> None:
        if not isinstance(raw, dict):
            self.add(owner, "design must be an object with contract, sha256, and evidence")
            return
        expected = {"contract", "sha256", "evidence"}
        for field in sorted(expected - raw.keys()):
            self.add(owner, f"design missing required field: {field}")
        for field in sorted(raw.keys() - expected):
            self.add(owner, f"design has unknown field: {field}")
        contract_path = self.safe_path(
            preset, raw.get("contract"), owner, "design.contract", kind="file"
        )
        if contract_path is not None:
            self.check_digest(owner, contract_path, raw.get("sha256"), "design.sha256")
            if status in {"candidate", "verified"}:
                self.validate_design_contract(contract_path, source_kinds)

        evidence = raw.get("evidence")
        if not isinstance(evidence, list):
            self.add(owner, "design.evidence must be a list")
            return
        if status in {"candidate", "verified"} and not evidence:
            self.add(owner, f"{status} preset requires nonempty design.evidence")
        for index, reference in enumerate(evidence):
            label = f"design.evidence[{index}]"
            if status in {"candidate", "verified"} and not isinstance(reference, dict):
                self.add(owner, f"{label} must include path and sha256")
            path = self.ref_path(preset, owner, reference, label)
            if path is not None and status in {"candidate", "verified"}:
                self.validate_pass_evidence(
                    preset,
                    path,
                    "design evidence",
                    status=status,
                    required_context="ui-review",
                )

    def validate_design_contract(
        self, path: Path, source_kinds: dict[str, str]
    ) -> None:
        data = self.load_json(path, "UI design contract")
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, "UI design contract must be a JSON object")
            return
        required = {
            "version",
            "brief",
            "tokens",
            "surfaces",
            "states",
            "responsive",
            "accessibility",
            "framework_bindings",
            "source_ids",
        }
        for field in sorted(required - data.keys()):
            self.add(path, f"UI design contract missing required field: {field}")
        version = data.get("version")
        if not isinstance(version, str) or not SEMVER.fullmatch(version):
            self.add(path, "UI design contract version must be exact SemVer")
        for field in ("brief", "responsive", "accessibility"):
            if not isinstance(data.get(field), dict) or not data[field]:
                self.add(path, f"UI design contract {field} must be a nonempty object")
        tokens = data.get("tokens")
        if not isinstance(tokens, dict):
            self.add(path, "UI design contract tokens must be an object")
        else:
            for field in ("primitive", "semantic", "component_state"):
                if not isinstance(tokens.get(field), dict) or not tokens[field]:
                    self.add(path, f"UI design contract tokens.{field} must be nonempty")
        for field in ("surfaces", "framework_bindings", "source_ids"):
            value = data.get(field)
            if not isinstance(value, list) or not value or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                self.add(path, f"UI design contract {field} must be a nonempty string list")
        states = data.get("states")
        required_states = {"loading", "empty", "error", "stale", "denied", "success"}
        if not isinstance(states, list) or not all(isinstance(item, str) for item in states):
            self.add(path, "UI design contract states must be a string list")
        else:
            for state in sorted(required_states - set(states)):
                self.add(path, f"UI design contract missing state: {state}")
        source_ids = data.get("source_ids")
        if isinstance(source_ids, list):
            for source_id in source_ids:
                if isinstance(source_id, str) and source_id not in source_kinds:
                    self.add(path, f"UI design contract references unknown source: {source_id}")
            if not any(
                source_kinds.get(source_id) in {"official-docs", "context7"}
                for source_id in source_ids
                if isinstance(source_id, str)
            ):
                self.add(path, "UI design contract requires an official-docs or context7 source")

    def validate_cross_contracts(
        self,
        preset: Path,
        owner: Path,
        manifest: dict[str, Any],
        status: str,
        source_records: dict[str, dict[str, Any]],
    ) -> None:
        if status not in {"candidate", "verified"}:
            return
        stack_pairs: set[tuple[str, str]] = set()
        raw_stack = manifest.get("stack")
        for entry in (raw_stack if isinstance(raw_stack, list) else []):
            if not isinstance(entry, dict):
                continue
            package = entry.get("package")
            version = entry.get("version")
            source_id = entry.get("source_id")
            if isinstance(package, str) and isinstance(version, str):
                stack_pairs.add((package, version))
            source = source_records.get(source_id) if isinstance(source_id, str) else None
            requested = source.get("requested_ref") if isinstance(source, dict) else None
            if (
                isinstance(version, str)
                and isinstance(requested, str)
                and requested.removeprefix("v") != version
            ):
                self.add(
                    owner,
                    f"stack {package}@{version} source {source_id} requested_ref "
                    f"must equal the exact stack version",
                )
        catalog = self.load_json(preset / "patterns/catalog.json", "pattern catalog")
        pattern_entries = self.records(
            catalog,
            "patterns",
            preset / "patterns/catalog.json",
            "pattern catalog",
        )
        pattern_ids = {
            entry.get("id")
            for entry in (pattern_entries or [])
            if isinstance(entry, dict) and isinstance(entry.get("id"), str)
        }
        raw_capabilities = manifest.get("capabilities")
        capability_entries = [
            entry
            for entry in (raw_capabilities if isinstance(raw_capabilities, list) else [])
            if isinstance(entry, dict) and isinstance(entry.get("id"), str)
        ]
        capability_ids = {entry["id"] for entry in capability_entries}
        verified_capabilities = {
            entry["id"]
            for entry in capability_entries
            if entry.get("status") == "verified"
        }
        for entry in capability_entries:
            raw_patterns = entry.get("patterns")
            for pattern_id in (raw_patterns if isinstance(raw_patterns, list) else []):
                if isinstance(pattern_id, str) and pattern_id not in pattern_ids:
                    self.add(
                        owner,
                        f"capability {entry['id']} references unknown pattern: {pattern_id}",
                    )

        mapped_capabilities: set[str] = set()
        raw_flows = manifest.get("verified_flows")
        for flow in (raw_flows if isinstance(raw_flows, list) else []):
            if not isinstance(flow, dict):
                continue
            capability_id = flow.get("capability_id")
            if isinstance(capability_id, str):
                if capability_id not in capability_ids:
                    self.add(
                        owner,
                        f"verified flow {flow.get('id')} references unknown capability: "
                        f"{capability_id}",
                    )
                mapped_capabilities.add(capability_id)
        for capability_id in sorted(verified_capabilities - mapped_capabilities):
            self.add(owner, f"verified capability has no verified flow: {capability_id}")

        design = manifest.get("design")
        if isinstance(design, dict):
            contract = self.safe_path(
                preset, design.get("contract"), owner, "design.contract", kind="file"
            )
            if contract is not None:
                data = self.load_json(contract, "UI design contract")
                surfaces = data.get("surfaces") if isinstance(data, dict) else None
                if isinstance(surfaces, list) and pattern_ids and not (
                    set(item for item in surfaces if isinstance(item, str)) & pattern_ids
                ):
                    self.add(
                        contract,
                        "UI design contract surfaces must map at least one declared pattern",
                    )
                bindings = (
                    data.get("framework_bindings") if isinstance(data, dict) else None
                )
                for binding in (bindings if isinstance(bindings, list) else []):
                    if not isinstance(binding, str) or "@" not in binding:
                        continue
                    package, _, version = binding.rpartition("@")
                    if (package, version) not in stack_pairs:
                        self.add(
                            contract,
                            f"UI framework binding is not an exact stack item: {binding}",
                        )

    def validate_verification(
        self,
        preset: Path,
        owner: Path,
        raw: Any,
        known_skills: set[str],
        status: str,
    ) -> None:
        if not isinstance(raw, dict):
            self.add(owner, "verification must be an object")
            return
        expected = {
            "skill_evals",
            "integrity",
            "clean_room_evidence",
            "independent_use_evidence",
        }
        for field in sorted(raw.keys() - expected):
            self.add(owner, f"verification has unknown field: {field}")
        if status in {"candidate", "verified"} and not isinstance(
            raw.get("skill_evals"), dict
        ):
            self.add(owner, "verification.skill_evals must include path and sha256")
        eval_path = self.ref_path(preset, owner, raw.get("skill_evals"), "verification.skill_evals")
        if eval_path is not None:
            data = self.load_json(eval_path, "skill evals")
            cases = self.records(data, "cases", eval_path, "skill evals")
            if cases is not None:
                covered: set[str] = set()
                covered_skills: set[str] = set()
                case_ids: set[str] = set()
                for index, case in enumerate(cases):
                    label = f"case[{index}]"
                    if not isinstance(case, dict):
                        self.add(eval_path, f"{label} must be an object")
                        continue
                    kind = next(
                        (
                            case.get(key)
                            for key in ("kind", "case_type", "category", "type")
                            if key in case
                        ),
                        None,
                    )
                    if not isinstance(kind, str) or not kind.strip():
                        self.add(eval_path, f"{label} requires a case kind")
                    else:
                        covered.add(kind.replace("_", "-").lower())
                    skill_refs = case.get("skills")
                    if not isinstance(skill_refs, list) or not skill_refs:
                        self.add(eval_path, f"{label}.skills must be a nonempty list")
                    else:
                        for skill_ref in skill_refs:
                            if not isinstance(skill_ref, str) or skill_ref not in known_skills:
                                self.add(eval_path, f"{label} references unknown skill: {skill_ref}")
                            elif skill_ref in REQUIRED_SKILLS:
                                covered_skills.add(skill_ref)
                    if status in {"candidate", "verified"}:
                        self.validate_eval_case(
                            preset, eval_path, case, label, case_ids, status
                        )
                for kind in sorted(REQUIRED_EVAL_KINDS - covered):
                    self.add(eval_path, f"skill evals missing required case: {kind}")
                if status in {"candidate", "verified"}:
                    for capability in sorted(REQUIRED_SKILLS - covered_skills):
                        self.add(
                            eval_path,
                            f"skill evals do not forward-test required skill: {capability}",
                        )

        evidence = raw.get("clean_room_evidence")
        if status in {"candidate", "verified"}:
            if not isinstance(raw.get("integrity"), dict):
                self.add(owner, "verification.integrity must include path and sha256")
            integrity = self.ref_path(
                preset, owner, raw.get("integrity"), "verification.integrity"
            )
            if integrity is not None:
                self.validate_integrity(preset, integrity)
            if not isinstance(evidence, list) or not evidence:
                self.add(owner, f"{status} preset requires nonempty clean_room_evidence")
                clean_run_ids: set[str] = set()
            else:
                clean_run_ids = set()
                for index, reference in enumerate(evidence):
                    label = f"verification.clean_room_evidence[{index}]"
                    if not isinstance(reference, dict):
                        self.add(owner, f"{label} must include path and sha256")
                    path = self.ref_path(
                        preset,
                        owner,
                        reference,
                        label,
                    )
                    if path is not None:
                        validated = self.validate_pass_evidence(
                            preset,
                            path,
                            "clean-room evidence",
                            status=status,
                            required_context="clean-room",
                            require_commands=True,
                        )
                        if isinstance(validated, dict) and isinstance(
                            validated.get("run_id"), str
                        ):
                            clean_run_ids.add(validated["run_id"])
            if status == "verified":
                independent = raw.get("independent_use_evidence")
                if not isinstance(independent, list) or not independent:
                    self.add(owner, "verified preset requires independent_use_evidence")
                else:
                    clean_references = evidence if isinstance(evidence, list) else []
                    clean_paths = {
                        value
                        for reference in clean_references
                        for value in [
                            reference.get("path")
                            if isinstance(reference, dict)
                            else reference
                        ]
                        if isinstance(value, str)
                    }
                    for index, reference in enumerate(independent):
                        label = f"verification.independent_use_evidence[{index}]"
                        if not isinstance(reference, dict):
                            self.add(owner, f"{label} must include path and sha256")
                        raw_path = (
                            reference.get("path")
                            if isinstance(reference, dict)
                            else reference
                        )
                        if isinstance(raw_path, str) and raw_path in clean_paths:
                            self.add(owner, f"{label} must be distinct from clean-room evidence")
                        path = self.ref_path(preset, owner, reference, label)
                        if path is not None:
                            validated = self.validate_pass_evidence(
                                preset,
                                path,
                                "independent-use evidence",
                                status=status,
                                required_context="independent-use",
                                require_commands=True,
                            )
                            if isinstance(validated, dict):
                                run_id = validated.get("run_id")
                                independent_from = validated.get(
                                    "independent_from_run_id"
                                )
                                if isinstance(run_id, str) and run_id in clean_run_ids:
                                    self.add(
                                        path,
                                        "independent-use run_id must differ from clean-room runs",
                                    )
                                if independent_from not in clean_run_ids:
                                    self.add(
                                        path,
                                        "independent-use evidence must name a clean-room run",
                                    )
            elif raw.get("independent_use_evidence") is not None:
                independent = raw.get("independent_use_evidence")
                if not isinstance(independent, list):
                    self.add(owner, "independent_use_evidence must be a list")
                else:
                    for index, reference in enumerate(independent):
                        label = f"verification.independent_use_evidence[{index}]"
                        if not isinstance(reference, dict):
                            self.add(owner, f"{label} must include path and sha256")
                        path = self.ref_path(preset, owner, reference, label)
                        if path is not None:
                            self.validate_pass_evidence(
                                preset,
                                path,
                                "independent-use evidence",
                                status=status,
                                required_context="independent-use",
                                require_commands=True,
                            )
        elif evidence is not None:
            if not isinstance(evidence, list):
                self.add(owner, "verification.clean_room_evidence must be a list")
            else:
                for index, reference in enumerate(evidence):
                    self.ref_path(
                        preset,
                        owner,
                        reference,
                        f"verification.clean_room_evidence[{index}]",
                    )
        if status not in {"candidate", "verified"} and raw.get("integrity") is not None:
            integrity_ref = raw.get("integrity")
            if not isinstance(integrity_ref, dict):
                self.add(owner, "verification.integrity must include path and sha256")
            integrity = self.ref_path(
                preset, owner, integrity_ref, "verification.integrity"
            )
            if integrity is not None:
                self.validate_integrity(preset, integrity)
        if status not in {"candidate", "verified"} and raw.get(
            "independent_use_evidence"
        ) is not None:
            independent = raw.get("independent_use_evidence")
            if not isinstance(independent, list):
                self.add(owner, "independent_use_evidence must be a list")
            else:
                for index, reference in enumerate(independent):
                    label = f"verification.independent_use_evidence[{index}]"
                    if not isinstance(reference, dict):
                        self.add(owner, f"{label} must include path and sha256")
                    self.ref_path(preset, owner, reference, label)

    def validate_eval_case(
        self,
        preset: Path,
        owner: Path,
        case: dict[str, Any],
        label: str,
        case_ids: set[str],
        status: str,
    ) -> dict[str, Any] | None:
        required = {
            "id",
            "kind",
            "skills",
            "prompt",
            "input_digests",
            "route_trace",
            "conformance",
            "outcome",
        }
        for field in sorted(required - case.keys()):
            self.add(owner, f"{label} missing required forward-eval field: {field}")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not KEBAB_NAME.fullmatch(case_id):
            self.add(owner, f"{label}.id must be lowercase kebab-case")
        elif case_id in case_ids:
            self.add(owner, f"duplicate skill eval id: {case_id}")
        else:
            case_ids.add(case_id)
        prompt = case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            self.add(owner, f"{label}.prompt must be nonempty")
        route_trace = case.get("route_trace")
        if not isinstance(route_trace, list) or not route_trace or not all(
            isinstance(item, str) and item.strip() for item in route_trace
        ):
            self.add(owner, f"{label}.route_trace must be a nonempty string list")

        input_digests = case.get("input_digests")
        expected = self.evaluation_input_locks(preset)
        if not isinstance(input_digests, dict):
            self.add(owner, f"{label}.input_digests must be an object")
        else:
            for name in sorted(expected.keys() - input_digests.keys()):
                self.add(owner, f"{label}.input_digests missing required input: {name}")
            for name in sorted(input_digests.keys() - expected.keys()):
                self.add(owner, f"{label}.input_digests has unknown input: {name}")
            for name in sorted(expected.keys() & input_digests.keys()):
                if input_digests[name] != expected[name]:
                    self.add(owner, f"{label}.input_digests.{name} is stale or misbound")
        verdict_paths: dict[str, set[str]] = {}
        for verdict in ("conformance", "outcome"):
            raw_verdict = case.get(verdict)
            references = raw_verdict.get("evidence") if isinstance(raw_verdict, dict) else None
            verdict_paths[verdict] = {
                path_value
                for reference in (references if isinstance(references, list) else [])
                for path_value in [
                    reference.get("path") if isinstance(reference, dict) else reference
                ]
                if isinstance(path_value, str)
            }
        if verdict_paths["conformance"] & verdict_paths["outcome"]:
            self.add(owner, f"{label} conformance and outcome evidence must be distinct")
        for verdict in ("conformance", "outcome"):
            self.validate_eval_verdict(
                preset,
                owner,
                case.get(verdict),
                f"{label}.{verdict}",
                status,
                str(case_id),
                verdict,
            )

    def validate_eval_verdict(
        self,
        preset: Path,
        owner: Path,
        raw: Any,
        label: str,
        status: str,
        case_id: str,
        verdict: str,
    ) -> None:
        if not isinstance(raw, dict):
            self.add(owner, f"{label} must be an object")
            return
        if raw.get("result") != "pass":
            self.add(owner, f"{label}.result must be pass")
        evidence = raw.get("evidence")
        if not isinstance(evidence, list) or not evidence:
            self.add(owner, f"{label}.evidence must be a nonempty list")
            return
        for index, reference in enumerate(evidence):
            evidence_label = f"{label}.evidence[{index}]"
            if not isinstance(reference, dict):
                self.add(owner, f"{evidence_label} must include path and sha256")
            path = self.ref_path(preset, owner, reference, evidence_label)
            if path is not None:
                self.validate_dual_verdict_evidence(
                    preset,
                    path,
                    "skill-eval evidence",
                    status,
                    f"skill-eval-{verdict}",
                    case_id,
                )

    @staticmethod
    def valid_timestamp(raw: Any) -> bool:
        if not isinstance(raw, str) or not RFC3339.fullmatch(raw):
            return False
        try:
            parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return False
        return parsed.tzinfo is not None

    @staticmethod
    def immutable_revision(raw: Any) -> bool:
        if not isinstance(raw, str):
            return False
        return bool(
            SHA40.fullmatch(raw)
            or SHA256.fullmatch(raw)
            or SEMVER.fullmatch(raw)
            or (raw.startswith("v") and SEMVER.fullmatch(raw[1:]))
        )

    def validate_pass_evidence(
        self,
        preset: Path,
        path: Path,
        label: str,
        *,
        status: str,
        required_context: str,
        require_commands: bool = False,
    ) -> None:
        data = self.load_json(path, label)
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, f"{label} must be a JSON object")
            return None
        if data.get("result") != "pass":
            self.add(path, f"{label}.result must be pass")
        if data.get("qualification") != status:
            self.add(path, f"{label}.qualification must equal {status}")
        if data.get("context") != required_context:
            self.add(path, f"{label}.context must equal {required_context}")
        for field in ("run_id", "actor", "toolchain", "environment"):
            value = data.get(field)
            if not isinstance(value, str) or not value.strip():
                self.add(path, f"{label}.{field} must be nonempty")
        run_id = data.get("run_id")
        if isinstance(run_id, str) and not KEBAB_NAME.fullmatch(run_id):
            self.add(path, f"{label}.run_id must be lowercase kebab-case")
        if required_context == "independent-use" and (
            not isinstance(data.get("independent_from_run_id"), str)
            or not data["independent_from_run_id"].strip()
        ):
            self.add(path, f"{label}.independent_from_run_id must be nonempty")
        if not self.valid_timestamp(data.get("observed_at")):
            self.add(path, f"{label}.observed_at must be timezone-aware RFC 3339")
        input_digests = data.get("input_digests")
        if (
            not isinstance(input_digests, dict)
            or not input_digests
            or not all(
                isinstance(key, str)
                and key.strip()
                and isinstance(value, str)
                and SHA256.fullmatch(value)
                for key, value in input_digests.items()
            )
        ):
            self.add(path, f"{label}.input_digests must map inputs to SHA-256 values")
        else:
            expected = self.evidence_input_locks(preset)
            for name in sorted(expected.keys() - input_digests.keys()):
                self.add(path, f"{label}.input_digests missing required input: {name}")
            for name in sorted(input_digests.keys() - expected.keys()):
                self.add(path, f"{label}.input_digests has unknown input: {name}")
            for name in sorted(expected.keys() & input_digests.keys()):
                if input_digests[name] != expected[name]:
                    self.add(path, f"{label}.input_digests.{name} is stale or misbound")
        self.validate_evidence_freshness(preset, path, label, data.get("observed_at"))
        if require_commands:
            commands = data.get("commands")
            if not isinstance(commands, list) or not commands:
                self.add(path, f"{label}.commands must be a nonempty list")
            else:
                for index, command in enumerate(commands):
                    if (
                        not isinstance(command, dict)
                        or not isinstance(command.get("command"), str)
                        or not command["command"].strip()
                        or command.get("exit_code") != 0
                    ):
                        self.add(
                            path,
                            f"{label}.commands[{index}] requires command and exit_code 0",
                        )
        return data

    def validate_dual_verdict_evidence(
        self,
        preset: Path,
        path: Path,
        label: str,
        status: str,
        claim_type: str,
        claim_id: str,
    ) -> None:
        data = self.load_json(path, label)
        if not isinstance(data, dict):
            if data is not None:
                self.add(path, f"{label} must be a JSON object")
            return
        if data.get("conformance") != "pass":
            self.add(path, f"{label}.conformance must be pass")
        if data.get("outcome") != "pass":
            self.add(path, f"{label}.outcome must be pass")
        if data.get("qualification") != status:
            self.add(path, f"{label}.qualification must equal {status}")
        if data.get("claim_type") != claim_type:
            self.add(path, f"{label}.claim_type must equal {claim_type}")
        if data.get("claim_id") != claim_id:
            self.add(path, f"{label}.claim_id must equal {claim_id}")
        if not self.valid_timestamp(data.get("observed_at")):
            self.add(path, f"{label}.observed_at must be timezone-aware RFC 3339")
        self.validate_evidence_freshness(
            preset, path, label, data.get("observed_at")
        )
        input_digests = data.get("input_digests")
        expected = self.evaluation_input_locks(preset)
        if claim_type == "pattern":
            expected.pop("patterns", None)
        if not isinstance(input_digests, dict):
            self.add(path, f"{label}.input_digests must be an object")
        else:
            for name in sorted(expected.keys() - input_digests.keys()):
                self.add(path, f"{label}.input_digests missing required input: {name}")
            for name in sorted(input_digests.keys() - expected.keys()):
                self.add(path, f"{label}.input_digests has unknown input: {name}")
            for name in sorted(expected.keys() & input_digests.keys()):
                if input_digests[name] != expected[name]:
                    self.add(path, f"{label}.input_digests.{name} is stale or misbound")

    def evidence_input_locks(self, preset: Path) -> dict[str, str]:
        try:
            manifest = json.loads((preset / "preset.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}

        canonical = json.loads(json.dumps(manifest))
        design = canonical.get("design")
        if isinstance(design, dict):
            design.pop("evidence", None)
        verification = canonical.get("verification")
        if isinstance(verification, dict):
            canonical["verification"] = {
                "skill_evals": verification.get("skill_evals")
            }
        serialized = json.dumps(
            canonical,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
        locks = {"manifest_inputs": hashlib.sha256(serialized).hexdigest()}

        template = preset / "template"
        if template.is_dir():
            try:
                locks["template"] = self.digest_tree(
                    template, b"preset-template-tree-v1"
                )
            except (OSError, ValueError):
                pass
        for field in ("patterns", "sources", "design"):
            section = manifest.get(field)
            if isinstance(section, dict):
                digest = section.get("sha256")
                if isinstance(digest, str) and SHA256.fullmatch(digest):
                    locks[field] = digest
        skills = manifest.get("skills")
        if isinstance(skills, dict):
            for capability in sorted(REQUIRED_SKILLS):
                record = skills.get(capability)
                if isinstance(record, dict):
                    digest = record.get("sha256")
                    if isinstance(digest, str) and SHA256.fullmatch(digest):
                        locks[f"skill:{capability}"] = digest
        if isinstance(verification, dict):
            eval_ref = verification.get("skill_evals")
            if isinstance(eval_ref, dict):
                digest = eval_ref.get("sha256")
                if isinstance(digest, str) and SHA256.fullmatch(digest):
                    locks["skill_evals"] = digest
        return locks

    def evaluation_input_locks(self, preset: Path) -> dict[str, str]:
        locks = self.evidence_input_locks(preset)
        locks.pop("manifest_inputs", None)
        locks.pop("skill_evals", None)
        return locks

    def validate_evidence_freshness(
        self, preset: Path, path: Path, label: str, observed_at: Any
    ) -> None:
        if not self.valid_timestamp(observed_at):
            return
        try:
            manifest = json.loads((preset / "preset.json").read_text(encoding="utf-8"))
            stale_days = manifest["upgrade_policy"]["stale_after_days"]
        except (OSError, KeyError, TypeError, json.JSONDecodeError):
            return
        if not isinstance(stale_days, int) or isinstance(stale_days, bool) or stale_days < 1:
            return
        observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - observed.astimezone(timezone.utc)
        if age.total_seconds() < -300:
            self.add(path, f"{label}.observed_at must not be in the future")
        elif age.days >= stale_days:
            self.add(path, f"{label} is stale after {stale_days} days")

    def validate_integrity(self, preset: Path, integrity_path: Path) -> None:
        data = self.load_json(integrity_path, "integrity evidence")
        if not isinstance(data, dict):
            if data is not None:
                self.add(integrity_path, "integrity evidence must be a JSON object")
            return
        if data.get("algorithm") != "sha256":
            self.add(integrity_path, "integrity algorithm must be sha256")
        if data.get("result") != "pass":
            self.add(integrity_path, "integrity result must be pass")
        if not self.valid_timestamp(data.get("generated_at")):
            self.add(
                integrity_path,
                "integrity generated_at must be timezone-aware RFC 3339",
            )
        records = data.get("files")
        if not isinstance(records, list) or not records:
            self.add(integrity_path, "integrity files must be a nonempty list")
            return

        declared: set[str] = set()
        declared_order: list[str] = []
        for index, record in enumerate(records):
            label = f"integrity.files[{index}]"
            if not isinstance(record, dict) or set(record) != {"path", "sha256"}:
                self.add(integrity_path, f"{label} must contain exactly path and sha256")
                continue
            raw_path = record.get("path")
            if isinstance(raw_path, str):
                declared_order.append(raw_path)
                if raw_path in declared:
                    self.add(integrity_path, f"duplicate integrity path: {raw_path}")
                declared.add(raw_path)
            target = self.safe_path(
                preset, raw_path, integrity_path, f"{label}.path", kind="file"
            )
            if target is not None:
                self.check_digest(
                    integrity_path,
                    target,
                    record.get("sha256"),
                    f"{label}.sha256",
                )
        if declared_order != sorted(declared_order, key=lambda item: item.encode("utf-8")):
            self.add(integrity_path, "integrity files must use POSIX byte-sorted path order")

        excluded = {
            "preset.json",
            integrity_path.relative_to(preset).as_posix(),
        }
        expected: set[str] = set()
        for path in preset.rglob("*"):
            relative = path.relative_to(preset).as_posix()
            if path.is_symlink():
                self.add(integrity_path, f"integrity scope contains symbolic link: {relative}")
            elif path.is_file() and relative not in excluded:
                expected.add(relative)
        for missing in sorted(expected - declared):
            self.add(integrity_path, f"integrity graph missing file: {missing}")
        for extra in sorted(declared - expected):
            self.add(integrity_path, f"integrity graph has unexpected file: {extra}")

    def ref_path(self, preset: Path, owner: Path, raw: Any, label: str) -> Path | None:
        digest: Any = None
        path_value = raw
        if isinstance(raw, dict):
            path_value = raw.get("path")
            digest = raw.get("sha256")
        path = self.safe_path(preset, path_value, owner, label, kind="file")
        if path is not None and isinstance(raw, dict):
            self.check_digest(owner, path, digest, f"{label}.sha256")
        return path

    def records(
        self, data: Any, key: str, owner: Path, label: str
    ) -> list[Any] | None:
        if isinstance(data, list):
            return data
        if isinstance(data, dict) and isinstance(data.get(key), list):
            return data[key]
        self.add(owner, f"{label} must be a list or an object containing {key}")
        return None


def validate_presets(presets_root: Path) -> tuple[list[Finding], Counts]:
    """Return deterministic findings and aggregate counts for a preset catalog."""

    return PresetValidator(presets_root).validate()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "presets_root",
        nargs="?",
        type=Path,
        default=Path("docs/presets"),
        help="preset catalog root (default: docs/presets)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    findings, counts = validate_presets(args.presets_root)
    for finding in findings:
        print(finding.render())
    print(
        "presets-quality: "
        f"presets={counts.presets} skills={counts.skills} "
        f"patterns={counts.patterns} findings={len(findings)}"
    )
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
