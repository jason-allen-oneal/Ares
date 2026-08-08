# Ares v1 Release Checklist

This is the release gate for Ares 1.1.0 and later stable v1 releases. Complete it from a clean checkout. Do not release from a working tree that contains uncommitted or ignored build output.

## 1. Release identity

- [ ] The intended version appears in `pyproject.toml`, `ares.__version__`, `CHANGELOG.md`, and the release notes.
- [ ] The release is correctly classified as patch, minor, or major according to `docs/v1-support-boundary.md`.
- [ ] The Python distribution remains `bluedot-ares` and the import/commands remain `ares`, `ares-dashboard`, and `ares-tui`.
- [ ] The `bluedot-ares` project is controlled by BlueDot IT on PyPI.
- [ ] PyPI Trusted Publishing is configured for `BlueDot-IT/Ares`, the release workflow, and the protected `pypi` environment.
- [ ] No long-lived PyPI API token is stored in repository or organization secrets.
- [ ] `PYPI_PUBLISH_ENABLED` is `true` only when the release should be published to PyPI.

## 2. Product and compatibility review

- [ ] `CHANGELOG.md` lists every operator-visible change since the previous release.
- [ ] Release notes clearly separate supported and experimental behavior.
- [ ] `docs/v1-support-boundary.md` matches current behavior.
- [ ] `README.md`, `INSTALL.md`, `SUPPORT.md`, and command help agree on installation and first-run behavior.
- [ ] Database changes include upgrade and reopen tests from every supported prior schema version.
- [ ] Gateway, dashboard, TUI, CLI, mission, report, and training-export compatibility impacts are documented.
- [ ] Security-sensitive changes have an independent review focused on scope, risk, approvals, evidence, receipts, routing, and policy enforcement.

## 3. Clean local validation

Run from a disposable checkout or reset a dedicated release checkout:

```bash
git checkout main
git fetch origin --prune
git reset --hard origin/main
git clean -fdx -e vendor/ghostmcp

git submodule update --init --recursive

python -m venv .venv-release
. .venv-release/bin/activate
python -m pip install --upgrade pip build
python -m pip install -e '.[dev,anthropic,gemini,ghostmcp]' -e vendor/ghostmcp

python -m pytest tests -q
python -m compileall src/ares
```

Record the results:

- [ ] Full test suite passed.
- [ ] Expected skips were reviewed.
- [ ] Python compilation passed.
- [ ] No credential or client evidence material was present.

## 4. Build and clean-wheel smoke test

```bash
rm -rf dist build src/*.egg-info
python -m build

test "$(find dist -maxdepth 1 -name '*.whl' -print | wc -l)" -eq 1
test "$(find dist -maxdepth 1 -name '*.tar.gz' -print | wc -l)" -eq 1

python -m venv /tmp/ares-release-smoke
. /tmp/ares-release-smoke/bin/activate
python -m pip install --upgrade pip
WHEEL="$(find dist -maxdepth 1 -name '*.whl' -print -quit)"
python -m pip install "$WHEEL"
python -m pip check

python - <<'PY'
import importlib.metadata
import ares

assert importlib.metadata.version("bluedot-ares") == ares.__version__
PY

ares --version
ares doctor
ares tools
ares dashboard --help
ares-dashboard --help
ares tui --help
ares-tui --help
ares route --target 127.0.0.1 --prompt "safe local smoke test"
ares training --out /tmp/ares-sft-smoke.jsonl --min-status final_response
```

- [ ] Wheel and source distribution built.
- [ ] Clean wheel installed without source-tree imports.
- [ ] `pip check` passed.
- [ ] Distribution metadata matched `ares.__version__`.
- [ ] CLI, dashboard, TUI, route, and training smoke checks passed.

## 5. SBOM and checksums

While the clean release environment is active:

```bash
PACKAGE_VERSION="$(python -c 'import ares; print(ares.__version__)')"
python scripts/build_sbom.py \
  --distribution bluedot-ares \
  --output "dist/bluedot-ares-${PACKAGE_VERSION}.cdx.json"
python -m json.tool "dist/bluedot-ares-${PACKAGE_VERSION}.cdx.json" >/dev/null

(
  cd dist
  sha256sum ./*.whl ./*.tar.gz ./*.cdx.json > SHA256SUMS
  sha256sum --check SHA256SUMS
)
```

- [ ] CycloneDX SBOM generated and parsed.
- [ ] SBOM identifies `bluedot-ares` as the root application.
- [ ] SHA-256 checksums verify locally.

## 6. CI and workflow gate

- [ ] Linux tests passed on Python 3.11, 3.12, and 3.13.
- [ ] Linux package smoke passed.
- [ ] Windows package smoke passed.
- [ ] Security workflows passed or every failure was resolved before release.
- [ ] Release workflow action versions were reviewed for current supported majors.
- [ ] The PyPI publishing job remains guarded by the repository variable and protected environment.

## 7. Create the release

Never move or replace an existing release tag.

```bash
VERSION="1.1.0"
git tag -a "v${VERSION}" -m "Ares v${VERSION}"
git push origin "v${VERSION}"
```

The tag must trigger `.github/workflows/release.yml`, which:

1. verifies the tag against package metadata
2. builds wheel and source distribution
3. installs and smoke-tests the wheel
4. generates the CycloneDX SBOM
5. generates `SHA256SUMS`
6. creates GitHub build-provenance attestations
7. publishes the GitHub release assets
8. optionally publishes the wheel and source distribution through PyPI Trusted Publishing

## 8. Post-release verification

- [ ] GitHub release contains exactly one wheel and one source distribution.
- [ ] GitHub release contains `SHA256SUMS` and the CycloneDX SBOM.
- [ ] `sha256sum --check SHA256SUMS` succeeds after downloading the release assets.
- [ ] GitHub artifact attestations verify for every release asset.
- [ ] PyPI shows the expected `bluedot-ares` version when publishing was enabled.
- [ ] `pipx install 'bluedot-ares==<version>'` succeeds in a clean environment.
- [ ] `uv tool install 'bluedot-ares==<version>'` succeeds in a clean environment.
- [ ] `ares onboard`, `ares doctor`, dashboard help, and TUI help work from the public installation.
- [ ] Release links in the repository and documentation resolve correctly.

Example attestation verification:

```bash
gh attestation verify ./bluedot_ares-<version>-py3-none-any.whl \
  --repo BlueDot-IT/Ares
```

If any identity, checksum, provenance, installation, or smoke check fails, do not move the tag. Fix the defect and publish a new version.
