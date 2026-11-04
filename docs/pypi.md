# Publishing to PyPI

This project publishes with **PyPI Trusted Publishing (OIDC)**. No API token, password, or
secret is stored in the repository or in GitHub. GitHub proves its identity to PyPI for a
single workflow run, and PyPI accepts the upload.

You can do every step below from a phone browser.

## How it works

```text
You publish a GitHub Release
        ↓
.github/workflows/publish.yml runs
        ↓
lint + tests + build + twine check + wheel smoke test
        ↓
PyPI accepts the upload via OIDC (no token)
        ↓
pip install pytest-fixture-lens
```

## One-time setup

### 1. Create a PyPI account

Register at <https://pypi.org/account/register/> and verify your email.

**Enable 2FA.** PyPI requires two-factor authentication on accounts that upload packages.

### 2. Register a pending trusted publisher

Because the project does not exist on PyPI yet, register a *pending* publisher. This also
reserves the project name.

Go to <https://pypi.org/manage/account/publishing/> and choose
**Add a new pending publisher → GitHub Actions**, then enter exactly:

| Field | Value |
| --- | --- |
| PyPI Project Name | `pytest-fixture-lens` |
| Owner | `WMiliya` |
| Repository name | `pytest-fixture-lens` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

Save. These five values must match the workflow exactly, or the upload is rejected.

### 3. Create the GitHub environment

In the repository: **Settings → Environments → New environment**, name it `pypi`.

The workflow declares `environment: pypi`, and PyPI checks that name. Optionally add
yourself as a required reviewer so every publish needs your approval.

## Publishing a release

### 1. Bump the version

Edit `version` in `pyproject.toml` and add a section to `CHANGELOG.md`.

A version can never be reused on PyPI. If a release is broken, bump the number
(for example `0.1.1`) and release again — do not try to re-upload `0.1.0`.

### 2. Publish a GitHub Release

Go to <https://github.com/WMiliya/pytest-fixture-lens/releases/new> and set:

- **Tag:** `v0.1.0` (create the tag from `main`)
- **Title:** `v0.1.0`
- **Description:** the matching `CHANGELOG.md` section

Press **Publish release**.

### 3. Watch the workflow

<https://github.com/WMiliya/pytest-fixture-lens/actions/workflows/publish.yml>

The `build` job runs lint, tests, `twine check`, and installs the built wheel to confirm the
plugin loads. The `publish` job then uploads to PyPI.

### 4. Verify

- Project page: <https://pypi.org/project/pytest-fixture-lens/>
- Install test:

```bash
pip install pytest-fixture-lens
pytest --fixture-lens
```

## Manual publish without a release

The workflow also supports `workflow_dispatch`: open the **Actions** tab, pick
**Publish to PyPI**, and press **Run workflow**. Useful for re-running a failed upload
attempt with the same version, as long as that version never reached PyPI.

## Local build (optional, needs a computer)

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
```

Inspect the wheel:

```bash
python -c "import zipfile; print('\n'.join(zipfile.ZipFile('dist/pytest_fixture_lens-0.1.0-py3-none-any.whl').namelist()))"
```

The wheel must contain `fixturelens/templates/report.html`, `fixturelens/py.typed`, and an
`entry_points.txt` with a `[pytest11]` section — that entry point is what makes pytest
discover the plugin automatically.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| `invalid-publisher` | One of the five trusted-publisher fields does not match. Check the workflow filename and environment name. |
| `403 Forbidden` on upload | 2FA not enabled, or the pending publisher was not saved. |
| `File already exists` | That version is already on PyPI. Bump the version. |
| Publish job skipped | The `pypi` environment has a required reviewer who has not approved the run. |
| Plugin not found after install | The `[pytest11]` entry point is missing from the built wheel. |

## Why not an API token?

A token is a long-lived secret that must be stored somewhere and rotated. Trusted
Publishing issues a short-lived credential for one workflow run, scoped to one project.
Nothing to leak, nothing to rotate.
