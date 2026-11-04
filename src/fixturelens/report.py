"""Report assembly and self-contained HTML rendering."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any

from . import __version__

LIMITATIONS = [
    "Setup spans only; teardown time is not measured in this MVP.",
    "Exclusive setup time subtracts nested fixture setup spans to reduce double counting.",
    "The dependency graph is built from fixture arguments; dynamic getfixturevalue() calls "
    "may be missing.",
    "Parametrized instances are aggregated by fixture function; observed parameter indices "
    "are kept on events.",
    "pytest-xdist distributed runs are not supported yet.",
    "Timings are wall-clock measurements from this run, not a statistically stable benchmark.",
]


def build_report(
    *, tests: list[dict[str, Any]], fixtures: list[dict[str, Any]], exitstatus: int
) -> dict[str, Any]:
    hotspots = sorted(fixtures, key=lambda f: f["total_exclusive_ms"], reverse=True)
    summary = {
        "tests": len(tests),
        "fixtures": len(fixtures),
        "setup_exclusive_ms": round(sum(f["total_exclusive_ms"] for f in fixtures), 6),
        "reused_setups": sum(f["reuse_count"] for f in fixtures),
        "failed_tests": sum(1 for t in tests if t["outcome"] in {"failed", "error"}),
        "exitstatus": exitstatus,
    }
    return {
        "schema_version": 1,
        "generator": {"name": "fixturelens", "version": __version__},
        "summary": summary,
        "hotspots": [f["key"] for f in hotspots],
        "fixtures": fixtures,
        "tests": tests,
        "limitations": LIMITATIONS,
    }


def render_html(report: dict[str, Any]) -> str:
    template = (
        resources.files("fixturelens").joinpath("templates/report.html").read_text(encoding="utf-8")
    )
    payload = json.dumps(report, ensure_ascii=False, separators=(",", ":"))
    # Prevent closing the embedded JSON script tag from inside report content.
    payload = payload.replace("</", "<\\/")
    return template.replace("__FIXTURE_LENS_DATA__", payload)
