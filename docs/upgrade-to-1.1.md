# Upgrade to Ares 1.1

Ares 1.1 changes the Python distribution name from `ares` to `bluedot-ares` because the PyPI name `ares` belongs to an unrelated project.

The following remain unchanged:

- Python import: `ares`
- CLI: `ares`
- dashboard launcher: `ares-dashboard`
- TUI launcher: `ares-tui`
- state directory: `~/.ares`

## 1. Back up operator state

Stop Ares gateway, dashboard, TUI, and mission processes, then back up the local state directory:

```bash
cp -a ~/.ares ~/.ares.pre-1.1-backup
```

Treat the backup as sensitive. It may contain credentials, target details, session metadata, evidence references, reports, and authorization provenance.

## 2. Remove the old distribution

A clean replacement avoids leaving two distributions that both provide the `ares` Python package.

For an old `pipx` installation:

```bash
pipx uninstall ares
```

For an old `uv tool` installation:

```bash
uv tool uninstall ares
```

For an ordinary virtual environment:

```bash
python -m pip uninstall ares
```

For an editable source checkout, deactivate and remove the old virtual environment rather than layering the new distribution over it.

Do not install the unrelated public package with `pip install ares`.

## 3. Install the new distribution

Using `pipx`:

```bash
pipx install bluedot-ares
```

Using `uv`:

```bash
uv tool install bluedot-ares
```

Using a dedicated virtual environment:

```bash
python -m venv .venv-ares
. .venv-ares/bin/activate
python -m pip install --upgrade pip
python -m pip install bluedot-ares
```

Install required optional integrations in the same command when applicable:

```bash
pipx install 'bluedot-ares[anthropic,gemini,ghostmcp]'
```

## 4. Verify package identity

```bash
ares --version
ares doctor
python - <<'PY'
import importlib.metadata
import ares

print("distribution:", importlib.metadata.version("bluedot-ares"))
print("runtime:", ares.__version__)
assert importlib.metadata.version("bluedot-ares") == ares.__version__
PY
```

The distribution and runtime versions must match.

## 5. Verify state migration

List existing sessions and run a read-only report or memory command before starting new assessment work:

```bash
ares sessions
ares memory
ares report <existing-session-id>
```

Ares upgrades supported StateDB schemas in place when the database opens. Do not delete the pre-upgrade backup until existing sessions, reports, mission state, and gateway configuration have been checked.

## 6. Verify operator surfaces

```bash
ares dashboard --help
ares tui --help
ares mission --help
```

For gateway deployments, review the configured mode, authentication requirement, and CIDR allowlist before starting the service.

## Rollback

If the upgrade fails:

1. stop Ares processes
2. uninstall `bluedot-ares`
3. restore `~/.ares` from the pre-1.1 backup
4. reinstall the exact prior GitHub release wheel in an isolated environment
5. file a redacted support issue with the failing command and `ares doctor` output

Do not move or replace a published release tag to repair an upgrade defect. The project must publish a new patch release.
