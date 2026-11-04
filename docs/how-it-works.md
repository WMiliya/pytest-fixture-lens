# How FixtureLens works

FixtureLens is an opt-in pytest plugin. It does not change test outcomes. It observes fixture setup and writes a report after the session.

## Hooks

| Hook | Purpose |
| --- | --- |
| `pytest_addoption` | Adds `--fixture-lens` and `--fixture-lens-dir`. |
| `pytest_configure` | Registers the collector only when enabled. Rejects xdist runs. |
| `pytest_runtest_protocol` | Creates a record for each test item. |
| `pytest_runtest_setup` | Records the test's fixture closure when available. |
| `pytest_fixture_setup` | Measures setup spans and aggregates fixture counts. |
| `pytest_runtest_logreport` | Records setup/call/teardown outcomes. |
| `pytest_sessionfinish` | Builds and writes `report.json` and `report.html`. |
| `pytest_terminal_summary` | Prints a short summary and report path. |

## Fixture closure

For each test, FixtureLens reads the fixture closure pytest computed for that item. This includes fixtures requested directly by the test and fixtures pulled in by other fixtures.

The graph is built from fixture arguments. If a fixture uses `request.getfixturevalue("x")` dynamically, that edge may be missing in this MVP.

## Setup timing

FixtureLens wraps `pytest_fixture_setup` and records wall-clock time.

- **Inclusive time**: total time inside the fixture setup hook, including nested fixture setup.
- **Exclusive time**: inclusive time minus nested fixture setup spans.

Exclusive time is used for hotspots so parent fixtures do not double-count child fixture cost.

## Requested, setups, reused

For each fixture function:

- `requested_count`: number of selected tests whose closure includes the fixture.
- `setup_count`: number of observed setup events.
- `reuse_count`: `max(0, requested_count - setup_count)`.

Parametrized fixtures are aggregated by fixture function. Parameter indices are recorded on setup events when they can be mapped back to `fixturedef.params`.

## Output

The plugin writes:

- `report.html`: self-contained HTML with embedded JSON and JavaScript.
- `report.json`: machine-readable report.

The HTML report does not load external fonts, scripts, styles, or images.

## Known limitations

- Teardown timing is not measured.
- Dynamic `getfixturevalue()` dependencies may be missing.
- pytest-xdist is not supported yet.
- Timings are from one run and are not a stable benchmark.
- Reports may contain sensitive test or fixture names. Review before sharing.
