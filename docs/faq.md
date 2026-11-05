# FAQ

## What is a fixture?

In pytest, a fixture is reusable setup code: a database connection, an API client, a temporary directory, seeded data, or a configured object. Tests request fixtures by argument name.

## Why not just use `pytest --durations`?

`--durations` shows slow tests and phases. FixtureLens focuses on fixture setup: which fixtures were built, how often, how they depend on each other, and where setup time is concentrated.

## Does it slow my tests down?

It adds small hook overhead and writes a report at the end. It is opt-in, so normal `pytest` runs are unaffected.

## Does it send data anywhere?

No. The HTML report is self-contained and the plugin does not make network calls.

## Can I share the report publicly?

Review it first. Reports can contain test node IDs, fixture names, and source paths. Do not share reports with private or proprietary names.

## Does it work on Windows?

Yes. The plugin is pure Python and the report is a plain HTML file.

## Does it support pytest-xdist?

Not yet. Distributed runs are rejected with a clear error.

## Does it measure teardown?

Not in this MVP. It measures setup spans only.

## Does it detect unused fixtures?

No. It reports fixtures observed in the selected test run. Unused-fixture detection is a different problem because dynamic fixture requests and plugins can make static analysis unreliable.

## Is it published on PyPI?

Yes: <https://pypi.org/project/pytest-fixture-lens/>

```bash
pip install pytest-fixture-lens
```

Releases are published from GitHub Actions using PyPI Trusted Publishing, so no API token is
stored anywhere. See [pypi.md](pypi.md).
