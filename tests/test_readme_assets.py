"""The READMEs are uploaded to PyPI as the long description.

PyPI renders that HTML on pypi.org, where relative paths such as ``assets/banner.png``
cannot resolve. Every image and repo-file link must therefore be an absolute URL.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
READMES = ["README.md", "README.fa.md"]


@pytest.mark.parametrize("name", READMES)
def test_readme_images_use_absolute_urls(name: str) -> None:
    text = (ROOT / name).read_text(encoding="utf-8")
    srcs = re.findall(r'src="([^"]+)"', text)
    assert srcs, f"{name} has no images to check"
    relative = [s for s in srcs if not s.startswith(("https://", "http://"))]
    assert not relative, f"{name} has relative image paths that break on PyPI: {relative}"


@pytest.mark.parametrize("name", READMES)
def test_readme_local_links_use_absolute_urls(name: str) -> None:
    text = (ROOT / name).read_text(encoding="utf-8")
    hrefs = re.findall(r'href="([^"]+)"', text)
    md_links = re.findall(r"\]\(([^)]+)\)", text)
    relative = [
        u for u in hrefs + md_links if not u.startswith(("https://", "http://", "#", "mailto:"))
    ]
    assert not relative, f"{name} has relative links that break on PyPI: {relative}"


@pytest.mark.parametrize("name", READMES)
def test_readme_does_not_claim_unpublished(name: str) -> None:
    text = (ROOT / name).read_text(encoding="utf-8")
    stale = ["not published to PyPI", "منتشر نشده", "available after the first release"]
    found = [s for s in stale if s in text]
    assert not found, f"{name} still claims the package is unpublished: {found}"
