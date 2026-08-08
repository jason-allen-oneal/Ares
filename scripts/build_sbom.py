#!/usr/bin/env python3
"""Generate a CycloneDX SBOM from the active Python environment."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import importlib.metadata as metadata
import json
from pathlib import Path
import re
from typing import Any
from urllib.parse import quote
import uuid


_NAME_RE = re.compile(r"[-_.]+")
_REQUIREMENT_NAME_RE = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def normalize_name(value: str) -> str:
    return _NAME_RE.sub("-", value).lower()


def purl_for(name: str, version: str) -> str:
    return f"pkg:pypi/{quote(normalize_name(name))}@{quote(version)}"


def requirement_name(value: str) -> str | None:
    match = _REQUIREMENT_NAME_RE.match(value)
    return normalize_name(match.group(1)) if match else None


def component_for(distribution: metadata.Distribution, root_name: str) -> dict[str, Any]:
    name = distribution.metadata.get("Name") or distribution.name
    version = distribution.version
    normalized = normalize_name(name)
    component: dict[str, Any] = {
        "type": "application" if normalized == root_name else "library",
        "bom-ref": purl_for(name, version),
        "name": name,
        "version": version,
        "purl": purl_for(name, version),
    }

    description = distribution.metadata.get("Summary")
    if description:
        component["description"] = description

    homepage = distribution.metadata.get("Home-page")
    if homepage:
        component["externalReferences"] = [
            {"type": "website", "url": homepage}
        ]

    license_value = distribution.metadata.get("License")
    if license_value and license_value.upper() != "UNKNOWN":
        component["licenses"] = [{"license": {"name": license_value}}]

    return component


def generate_sbom(distribution_name: str) -> dict[str, Any]:
    root_name = normalize_name(distribution_name)
    installed: dict[str, metadata.Distribution] = {}
    for distribution in metadata.distributions():
        name = distribution.metadata.get("Name") or distribution.name
        installed[normalize_name(name)] = distribution

    root = installed.get(root_name)
    if root is None:
        raise SystemExit(
            f"distribution {distribution_name!r} is not installed in the active environment"
        )

    ordered = [installed[name] for name in sorted(installed)]
    components = [component_for(item, root_name) for item in ordered]

    dependencies: list[dict[str, Any]] = []
    for distribution in ordered:
        name = distribution.metadata.get("Name") or distribution.name
        refs: list[str] = []
        for requirement in distribution.requires or []:
            dependency_name = requirement_name(requirement)
            dependency = installed.get(dependency_name or "")
            if dependency is None:
                continue
            dependency_display_name = (
                dependency.metadata.get("Name") or dependency.name
            )
            refs.append(purl_for(dependency_display_name, dependency.version))
        dependencies.append(
            {
                "ref": purl_for(name, distribution.version),
                "dependsOn": sorted(set(refs)),
            }
        )

    root_component = component_for(root, root_name)
    return {
        "$schema": "https://cyclonedx.org/schema/bom-1.5.schema.json",
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": f"urn:uuid:{uuid.uuid4()}",
        "version": 1,
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
            "tools": {
                "components": [
                    {
                        "type": "application",
                        "name": "Ares stdlib SBOM generator",
                        "version": "1",
                    }
                ]
            },
            "component": root_component,
        },
        "components": components,
        "dependencies": dependencies,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--distribution", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    document = generate_sbom(args.distribution)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(document, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
