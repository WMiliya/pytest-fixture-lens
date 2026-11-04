from __future__ import annotations

import json


def test_skipped_and_setup_error_are_reported(pytester, tmp_path):
    pytester.makeconftest(
        """
        import pytest

        @pytest.fixture
        def broken():
            raise RuntimeError("boom")
        """
    )
    pytester.makepyfile(
        test_outcomes="""
        import pytest

        def test_skip():
            pytest.skip("not today")

        def test_error(broken):
            assert True
        """
    )
    outdir = tmp_path / "lens"
    result = pytester.runpytest_subprocess("--fixture-lens", f"--fixture-lens-dir={outdir}")
    result.assert_outcomes(skipped=1, errors=1)

    data = json.loads((outdir / "report.json").read_text(encoding="utf-8"))
    outcomes = {t["nodeid"].split("::")[-1]: t["outcome"] for t in data["tests"]}
    assert outcomes["test_skip"] == "skipped"
    assert outcomes["test_error"] == "error"
    assert data["summary"]["failed_tests"] == 1
