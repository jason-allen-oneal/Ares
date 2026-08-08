from __future__ import annotations

import importlib.util
from pathlib import Path
import tomllib

import ares


ROOT = Path(__file__).resolve().parents[1]


def _load_sbom_module():
    path = ROOT / "scripts" / "build_sbom.py"
    spec = importlib.util.spec_from_file_location("ares_build_sbom", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_distribution_identity_matches_runtime_version() -> None:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]

    assert project["name"] == "bluedot-ares"
    assert project["version"] == ares.__version__
    assert project["scripts"] == {
        "ares": "ares.cli:app",
        "ares-dashboard": "ares.dashboard:dashboard_app",
        "ares-tui": "ares.tui:main",
    }


def test_installation_docs_reject_unrelated_pypi_name() -> None:
    install_doc = (ROOT / "INSTALL.md").read_text(encoding="utf-8")

    assert "pipx install bluedot-ares" in install_doc
    assert "Do not run `pip install ares`" in install_doc


def test_sbom_generator_identifies_installed_distribution() -> None:
    sbom = _load_sbom_module()
    document = sbom.generate_sbom("bluedot-ares")

    assert document["bomFormat"] == "CycloneDX"
    assert document["specVersion"] == "1.5"
    root = document["metadata"]["component"]
    assert root["name"] == "bluedot-ares"
    assert root["version"] == ares.__version__
    assert root["purl"].startswith("pkg:pypi/bluedot-ares@")
    assert any(item["ref"] == root["bom-ref"] for item in document["dependencies"])
