# Publishing to GitHub

This guide turns the local project into a polished GitHub repository.

## 1. Owner placeholders

This checkout is already configured for the GitHub owner `WMiliya`.

To point it at a different owner later, run:

```bash
python scripts/configure_repo.py OTHER_GITHUB_USERNAME
```

## 1b. Pushing from an Android phone (no computer)

Install Termux, then:

```bash
pkg update -y && pkg upgrade -y
pkg install -y git python unzip openssh
termux-setup-storage
cd ~
cp ~/storage/downloads/fixturelens-github-ready.zip .
unzip -o fixturelens-github-ready.zip
cd pytest-fixture-lens
bash scripts/termux_push.sh
```

The script creates an SSH key, prints the public key for you to add on GitHub,
and then pushes. It never asks for your GitHub password.

## 2. Create the repository

Create an empty GitHub repository named `pytest-fixture-lens` (or choose another name and update `pyproject.toml`).

Do not initialize it with a README if you plan to push this project as-is.

## 3. Push

```bash
git init
git add .
git commit -m "Initial FixtureLens MVP"
git branch -M main
git remote add origin https://github.com/WMiliya/pytest-fixture-lens.git
git push -u origin main
```

## 4. Make the GitHub page look good

In repository settings:

- Description: `See which pytest fixtures your tests build, reuse, and pay for — offline HTML + JSON reports.`
- Website: link to the demo report if you publish it with GitHub Pages.
- Topics: `pytest`, `pytest-plugin`, `fixtures`, `testing`, `performance`, `developer-tools`, `python`, `html-report`, `ci`.
- Social preview: upload `assets/social-preview.png`.
- Enable Discussions if you want a place for questions.
- Enable private vulnerability reporting if available.

## 5. Protect main

Recommended branch protection:

- Require pull request reviews.
- Require status checks: CI.
- Require branches to be up to date before merging.

## 6. Optional: publish the demo report with GitHub Pages

You can publish `examples/demo_project/report.html` as a static demo. One simple way is to copy it into a `gh-pages` branch or use a Pages workflow. The report is self-contained, so it works as a static file.

## 7. Optional: publish to PyPI later

Before publishing:

- Verify the distribution name is available.
- Update version and changelog.
- Build and check the package.
- Publish with a trusted publisher or API token.

Example build commands:

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
```
