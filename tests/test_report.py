from __future__ import annotations

from fixturelens.report import build_report, render_html


def _fixture(key="k1", name="client"):
    return {
        "key": key,
        "name": name,
        "scope": "function",
        "source": "tests/conftest.py",
        "line": 3,
        "dependencies": [],
        "requested_count": 1,
        "setup_count": 1,
        "reuse_count": 0,
        "total_exclusive_ms": 1.5,
        "total_inclusive_ms": 2.0,
        "avg_exclusive_ms": 1.5,
        "param_indices": [],
    }


def test_build_report_summary_and_hotspot_order():
    fixtures = [_fixture("a", "fast"), _fixture("b", "slow")]
    fixtures[1]["total_exclusive_ms"] = 9.0
    report = build_report(tests=[], fixtures=fixtures, exitstatus=0)
    assert report["schema_version"] == 1
    assert report["summary"]["fixtures"] == 2
    assert report["hotspots"] == ["b", "a"]
    assert report["limitations"]


def test_render_html_is_self_contained_and_escapes_script_breakout():
    report = build_report(
        tests=[
            {
                "nodeid": "</script><script>alert(1)</script>",
                "location": ["x", 1, "x"],
                "outcome": "passed",
                "phases": {},
                "requested": [],
                "setup_events": [],
            }
        ],
        fixtures=[_fixture()],
        exitstatus=0,
    )
    html = render_html(report)
    assert "__FIXTURE_LENS_DATA__" not in html
    assert "<script>alert(1)</script>" not in html
    assert "<script src" not in html
