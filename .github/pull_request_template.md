## What changed

Describe the operator-visible and implementation changes.

## Why

Describe the concrete problem this pull request solves.

## Operator impact

- Commands or configuration changed:
- Installation or upgrade impact:
- Persistence or migration impact:
- Documentation impact:

## Security-boundary impact

Address each applicable boundary:

- target or filesystem scope
- rules of engagement
- risk ceiling
- dangerous-action approval
- approval receipts
- GhostMCP policy
- model-visible schemas
- route policy
- evidence trust and redaction
- database or report contents

State `none` only after checking the change against the list.

## Validation

- [ ] Focused tests added or updated
- [ ] `python -m pytest tests -q`
- [ ] `python -m compileall src/ares`
- [ ] Wheel and source distribution build
- [ ] Clean wheel installation smoke test, when packaging or entrypoints changed
- [ ] Windows behavior considered
- [ ] `git diff --check`
- [ ] No credentials, policies, approval receipts, client evidence, real target data, databases, or generated engagement reports committed

Provide exact test results and commands:

```text

```

## Documentation and release notes

- [ ] User-facing documentation updated
- [ ] `CHANGELOG.md` updated for operator-visible changes
- [ ] Supported versus experimental status stated
- [ ] Compatibility decision documented for supported-surface changes

## Screenshots or output

Include redacted output when it materially helps review. Do not attach real engagement data.
