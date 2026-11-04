"""Replace GitHub owner placeholders before publishing.

Usage:

    python scripts/configure_repo.py YOUR_GITHUB_USERNAME
"""

from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
    ROOT / "README.md",
    ROOT / "pyproject.toml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
    ROOT / "docs" / "publishing.md",
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("owner", help="GitHub username or organization that will own the repo")
    args = parser.parse_args()
    owner = args.owner.strip()
    if not owner or "/" in owner or " " in owner:
        raise SystemExit("owner must be a GitHub username or organization, not a URL")

    changed = []
    for path in TARGETS:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "YOUR_NAME" not in text:
            continue
        path.write_text(text.replace("YOUR_NAME", owner), encoding="utf-8")
        changed.append(str(path.relative_to(ROOT)))

    if changed:
        print("Updated:")
        for item in changed:
            print(f"  - {item}")
    else:
        print("No placeholders found.")


if __name__ == "__main__":
    main()
