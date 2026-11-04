from __future__ import annotations

import json
import re


def _read_report(outdir):
    data = json.loads((outdir / "report.json").read_text(encoding="utf-8"))
    html = (outdir / "report.html").read_text(encoding="utf-8")
    return data, html


def test_disabled_by_default(pytester, tmp_path):
    pytester.makepyfile(test_ok="def test_ok():\n    assert True\n")
    outdir = tmp_path / "lens"
    result = pytester.runpytest_subprocess(f"--fixture-lens-dir={outdir}")
    result.assert_outcomes(passed=1)
    assert not outdir.exists()


def test_report_graph_reuse_and_self_contained_html(pytester, tmp_path):
    pytester.makeconftest(
        """
        import time
        import pytest

        @pytest.fixture(scope="session")
        def settings():
            time.sleep(0.01)
            return {"debug": False}

        @pytest.fixture
        def client(settings):
            time.sleep(0.01)
            return object()
        """
    )
    pytester.makepyfile(
        test_app="""
        def test_one(client):
            assert client is not None

        def test_two(client):
            assert client is not None
        """
    )
    outdir = tmp_path / "lens"
    result = pytester.runpytest_subprocess("--fixture-lens", f"--fixture-lens-dir={outdir}")
    result.assert_outcomes(passed=2)

    data, html = _read_report(outdir)
    assert data["summary"]["tests"] == 2
    by_name = {f["name"]: f for f in data["fixtures"]}

    settings = by_name["settings"]
    client = by_name["client"]
    assert settings["scope"] == "session"
    assert settings["requested_count"] == 2
    assert settings["setup_count"] == 1
    assert settings["reuse_count"] == 1
    assert client["requested_count"] == 2
    assert client["setup_count"] == 2
    assert settings["key"] in client["dependencies"]
    assert settings["total_exclusive_ms"] >= 0
    assert client["total_inclusive_ms"] >= client["total_exclusive_ms"]

    assert "FixtureLens" in html
    assert "<script src" not in html
    assert "http://" not in html and "https://" not in html
    match = re.search(
        r'<script type="application/json" id="fixture-lens-data">(.*?)</script>', html, re.S
    )
    assert match
    embedded = json.loads(match.group(1))
    assert embedded["summary"]["tests"] == 2


def test_parametrized_fixture_instances_are_aggregated(pytester, tmp_path):
    pytester.makeconftest(
        """
        import pytest

        @pytest.fixture(params=[10, 20])
        def value(request):
            return request.param
        """
    )
    pytester.makepyfile(test_value="def test_value(value):\n    assert value in (10, 20)\n")
    outdir = tmp_path / "lens"
    result = pytester.runpytest_subprocess("--fixture-lens", f"--fixture-lens-dir={outdir}")
    result.assert_outcomes(passed=2)

    data, _ = _read_report(outdir)
    value = next(f for f in data["fixtures"] if f["name"] == "value")
    assert value["requested_count"] == 2
    assert value["setup_count"] == 2
    assert value["param_indices"] == [0, 1]


def test_failed_run_still_writes_report_and_preserves_exit_code(pytester, tmp_path):
    pytester.makepyfile(test_bad="def test_bad():\n    assert False\n")
    outdir = tmp_path / "lens"
    result = pytester.runpytest_subprocess("--fixture-lens", f"--fixture-lens-dir={outdir}")
    result.assert_outcomes(failed=1)
    assert result.ret != 0

    data, _ = _read_report(outdir)
    assert data["summary"]["failed_tests"] == 1
    assert data["summary"]["exitstatus"] == int(result.ret)
    assert data["tests"][0]["outcome"] == "failed"
