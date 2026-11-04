# Contributing to FixtureLens

Thanks for helping make pytest fixture costs visible.

## Setup

```bash
python -m pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest
```

## Ground rules

- Keep the plugin opt-in.
- Do not add network calls or external assets to the HTML report.
- Do not print fixture values or secrets.
- Prefer small, tested changes over broad rewrites.
- If a behavior depends on private pytest API, add a test and document the supported pytest range.

## Good first issues

- Add CSV export for the hotspots table.
- Add a `--fixture-lens-min-ms` filter for the terminal summary.
- Improve graph layout for wide dependency graphs.
- Add a test for fixture setup errors with parametrized fixtures.
- Document how exclusive setup time is calculated with a diagram.

## Regenerating assets

README assets are generated from the demo report:

```bash
pytest examples/demo_project/tests --fixture-lens --fixture-lens-dir examples/demo_project
python scripts/make_assets.py
```

## Pull request checklist

- [ ] Tests added or updated.
- [ ] `ruff check .` passes.
- [ ] `ruff format --check .` passes.
- [ ] `pytest` passes.
- [ ] README/docs updated if user-facing behavior changed.
- [ ] No real secrets or private data in fixtures, reports, or screenshots.
