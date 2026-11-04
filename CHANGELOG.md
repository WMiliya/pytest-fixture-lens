# Changelog

## 0.1.1

Docs and packaging fix. No behaviour changes.

- Use absolute image and link URLs in both READMEs so the PyPI project page renders
  the banner, demo GIF, and report preview instead of broken images.
- Remove "not published yet" wording now that the package is on PyPI.
- Add `tests/test_readme_assets.py` to prevent relative URLs from creeping back in.
- Document the release process in `docs/pypi.md`, including why a README fix needs a new
  version to appear on PyPI.

## 0.1.0

Initial alpha MVP.

- Opt-in pytest plugin: `--fixture-lens`.
- Self-contained HTML report and JSON output.
- Fixture dependency graph from fixture arguments.
- Observed setup spans with inclusive and exclusive time.
- Requested / setup / reuse counts.
- Parametrized fixture indices aggregated by fixture function.
- Clear rejection of pytest-xdist distributed runs.
- Demo project and pytester-based integration tests.
- GitHub-ready repository polish: README, assets, CI, issue/PR templates, docs, security/support files.
