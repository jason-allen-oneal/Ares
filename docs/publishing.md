# Publishing Ares

Ares releases are built from signed version tags by `.github/workflows/release.yml`.

The workflow always publishes verifiable GitHub release assets. PyPI publishing is separately gated and uses Trusted Publishing through GitHub OIDC.

## Distribution identity

- Product: `Ares`
- Python distribution: `bluedot-ares`
- Python import: `ares`
- Console commands: `ares`, `ares-dashboard`, `ares-tui`

The PyPI project named `ares` is unrelated and must not be used for Ares releases.

## One-time PyPI configuration

1. Create or claim the `bluedot-ares` project under the BlueDot IT publishing account.
2. In the PyPI project publishing settings, add a GitHub Trusted Publisher with:

   - owner: `BlueDot-IT`
   - repository: `Ares`
   - workflow: `release.yml`
   - environment: `pypi`

3. In the GitHub repository, create an environment named `pypi`.
4. Add required reviewers or deployment restrictions appropriate for the release policy.
5. Do not create a PyPI API token secret.
6. Keep the repository variable `PYPI_PUBLISH_ENABLED` unset or `false` until a release is intended to publish.

## Repository variable gate

The PyPI job runs only when:

```text
PYPI_PUBLISH_ENABLED == true
```

This variable is not an authorization secret. It is an explicit operational switch. The protected GitHub environment and PyPI Trusted Publisher remain the authorization boundaries.

Set the variable to `true` only after:

- the PyPI project exists
- the Trusted Publisher matches the repository, workflow, and environment exactly
- the release version is final
- CI and security checks pass
- release notes and the support boundary are current

GitHub release creation does not depend on this variable.

## Release artifacts

The release build creates:

- one wheel
- one source distribution
- a CycloneDX SBOM generated from the clean installed-wheel environment
- `SHA256SUMS`
- GitHub build-provenance attestations

Only the wheel and source distribution are passed to the PyPI publishing action. Checksums and the SBOM remain GitHub release assets.

## Release procedure

Complete `docs/v1-release-checklist.md`, then create an annotated tag whose version exactly matches `pyproject.toml`:

```bash
VERSION="1.1.0"
git tag -a "v${VERSION}" -m "Ares v${VERSION}"
git push origin "v${VERSION}"
```

Never move an existing release tag. Publish a new patch version when a released artifact is defective.

## Verification

After the workflow completes:

```bash
sha256sum --check SHA256SUMS

gh attestation verify ./bluedot_ares-<version>-py3-none-any.whl \
  --repo BlueDot-IT/Ares

pipx install 'bluedot-ares==<version>'
ares --version
ares doctor
```

Confirm the PyPI files match the GitHub release wheel and source distribution hashes.

## Failure handling

If GitHub release publication succeeds but PyPI publication fails:

- do not move the tag
- diagnose Trusted Publisher, environment, project-name, or version conflicts
- rerun the failed job only when no file for that version was accepted by PyPI
- publish a new version when PyPI already contains an incorrect immutable file

If provenance, checksum, SBOM, or smoke validation fails, do not treat the release as complete.
