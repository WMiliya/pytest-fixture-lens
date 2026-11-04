"""Pytest plugin entry point and runtime collector.

The plugin is opt-in. It records fixture *setup* spans and the fixture closure
requested by each collected test, then writes a self-contained HTML report and
a JSON document. It deliberately does not claim to detect unused fixtures or
measure teardown time in this MVP.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

import pytest

from .report import build_report, render_html


def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("fixturelens")
    group.addoption(
        "--fixture-lens",
        action="store_true",
        default=False,
        help="Write an offline FixtureLens HTML/JSON report after the test run.",
    )
    group.addoption(
        "--fixture-lens-dir",
        action="store",
        default=".fixturelens",
        metavar="DIR",
        help="Output directory for report.html and report.json (default: .fixturelens).",
    )


def pytest_configure(config: pytest.Config) -> None:
    if not config.getoption("fixture_lens", default=False):
        return

    numprocesses = getattr(config.option, "numprocesses", None)
    dist = getattr(config.option, "dist", "no")
    if numprocesses not in (None, 0) or dist not in ("no", None):
        raise pytest.UsageError(
            "FixtureLens does not support pytest-xdist yet. Run without -n/--dist, "
            "or disable --fixture-lens for distributed runs."
        )

    lens = FixtureLens(config)
    config._fixturelens = lens  # type: ignore[attr-defined]
    config.pluginmanager.register(lens, "fixturelens-runtime")


def _relative_source(path: str, rootpath: Path) -> str:
    try:
        return os.path.relpath(path, rootpath)
    except ValueError:
        return path


def fixture_key(fixturedef: pytest.FixtureDef, rootpath: Path) -> str:
    """Stable function-level key.

    Parametrized instances are aggregated under the same fixture function; the
    observed parameter indices are kept on setup events instead.
    """
    func = fixturedef.func
    code = getattr(func, "__code__", None)
    path = _relative_source(code.co_filename, rootpath) if code else "<unknown>"
    line = code.co_firstlineno if code else 0
    qualname = getattr(func, "__qualname__", getattr(func, "__name__", fixturedef.argname))
    payload = json.dumps(
        [path, line, qualname, fixturedef.argname, fixturedef.scope],
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _param_index(fixturedef: pytest.FixtureDef, cache_key: Any) -> int | None:
    """Map pytest's fixture cache key back to a parameter index when possible."""
    params = getattr(fixturedef, "params", None)
    if params is None or cache_key is None:
        return None
    try:
        return list(params).index(cache_key)
    except ValueError:
        return None


class FixtureLens:
    """Collects fixture setup events for one non-distributed pytest session."""

    def __init__(self, config: pytest.Config) -> None:
        self.config = config
        self.rootpath = Path(config.rootpath)
        outdir = Path(config.getoption("fixture_lens_dir"))
        self.outdir = outdir if outdir.is_absolute() else self.rootpath / outdir
        self.tests: dict[str, dict[str, Any]] = {}
        self.fixtures: dict[str, dict[str, Any]] = {}
        self.current_nodeid: str | None = None
        self.setup_stack: list[dict[str, Any]] = []
        self.report: dict[str, Any] | None = None
        self.write_error: str | None = None

    # -- collection / test lifecycle -------------------------------------------------

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item: pytest.Item, nextitem: pytest.Item | None):
        nodeid = item.nodeid
        self.current_nodeid = nodeid
        self.tests[nodeid] = {
            "nodeid": nodeid,
            "location": list(item.location),
            "outcome": "unknown",
            "phases": {},
            "requested": [],
            "setup_events": [],
            "requests_recorded": False,
        }
        self._record_requests(item)
        try:
            yield
        finally:
            self.current_nodeid = None

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_setup(self, item: pytest.Item):
        # Some item types expose fixtureinfo only once setup begins.
        self._record_requests(item)
        yield

    def _record_requests(self, item: pytest.Item) -> None:
        rec = self.tests.get(item.nodeid)
        if rec is None or rec["requests_recorded"]:
            return
        info = getattr(item, "_fixtureinfo", None)
        if info is None:
            return
        rec["requests_recorded"] = True
        seen: set[str] = set()
        for name in getattr(info, "names_closure", []):
            defs = info.name2fixturedefs.get(name)
            if not defs:
                continue
            fixturedef = defs[-1]
            key = self._ensure_fixture(fixturedef)
            if key in seen:
                continue
            seen.add(key)
            rec["requested"].append(key)
            self.fixtures[key]["requested_count"] += 1

        # Resolve dependencies with the same visibility map pytest used for this
        # test. This handles conftest overrides more reliably than asking the
        # fixture manager from inside a fixture definition.
        for name in getattr(info, "names_closure", []):
            defs = info.name2fixturedefs.get(name)
            if not defs:
                continue
            fixturedef = defs[-1]
            node = self.fixtures[fixture_key(fixturedef, self.rootpath)]
            for dep in fixturedef.argnames:
                if dep == "request":
                    continue
                dep_defs = info.name2fixturedefs.get(dep)
                if not dep_defs:
                    continue
                dep_key = self._ensure_fixture(dep_defs[-1])
                if dep_key not in node["dependencies"]:
                    node["dependencies"].append(dep_key)

    def _ensure_fixture(self, fixturedef: pytest.FixtureDef) -> str:
        key = fixture_key(fixturedef, self.rootpath)
        if key in self.fixtures:
            return key

        func = fixturedef.func
        code = getattr(func, "__code__", None)
        source = _relative_source(code.co_filename, self.rootpath) if code else "<unknown>"
        line = code.co_firstlineno if code else 0
        node: dict[str, Any] = {
            "key": key,
            "name": fixturedef.argname,
            "scope": fixturedef.scope,
            "source": source,
            "line": line,
            "dependencies": [],
            "requested_count": 0,
            "setup_count": 0,
            "reuse_count": 0,
            "total_exclusive_ms": 0.0,
            "total_inclusive_ms": 0.0,
            "param_indices": set(),
        }
        self.fixtures[key] = node
        return key

    # -- fixture timing ---------------------------------------------------------------

    @pytest.hookimpl(hookwrapper=True)
    def pytest_fixture_setup(self, fixturedef: pytest.FixtureDef, request: pytest.FixtureRequest):
        key = self._ensure_fixture(fixturedef)
        span = {"key": key, "start": time.perf_counter(), "children_ms": 0.0}
        self.setup_stack.append(span)
        try:
            yield
        finally:
            inclusive_ms = (time.perf_counter() - span["start"]) * 1000.0
            self.setup_stack.pop()
            if self.setup_stack:
                self.setup_stack[-1]["children_ms"] += inclusive_ms
            exclusive_ms = max(0.0, inclusive_ms - span["children_ms"])

            cached = getattr(fixturedef, "cached_result", None)
            cache_key = cached[1] if cached else None
            param_index = _param_index(fixturedef, cache_key)
            failed = bool(cached and cached[2] is not None)

            node = self.fixtures[key]
            node["setup_count"] += 1
            node["total_exclusive_ms"] += exclusive_ms
            node["total_inclusive_ms"] += inclusive_ms
            if param_index is not None:
                node["param_indices"].add(param_index)

            if self.current_nodeid and self.current_nodeid in self.tests:
                self.tests[self.current_nodeid]["setup_events"].append(
                    {
                        "key": key,
                        "name": fixturedef.argname,
                        "scope": fixturedef.scope,
                        "param_index": param_index,
                        "inclusive_ms": round(inclusive_ms, 6),
                        "exclusive_ms": round(exclusive_ms, 6),
                        "failed": failed,
                    }
                )

    @pytest.hookimpl
    def pytest_runtest_logreport(self, report: pytest.TestReport) -> None:
        rec = self.tests.get(report.nodeid)
        if rec is None:
            return
        rec["phases"][report.when] = {
            "outcome": report.outcome,
            "duration_ms": round(report.duration * 1000.0, 6),
        }

    # -- output -----------------------------------------------------------------------

    @pytest.hookimpl
    def pytest_sessionfinish(self, session: pytest.Session, exitstatus: int) -> None:
        for rec in self.tests.values():
            rec["outcome"] = _final_outcome(rec["phases"])
            rec.pop("requests_recorded", None)
        for node in self.fixtures.values():
            node["reuse_count"] = max(0, node["requested_count"] - node["setup_count"])
            node["param_indices"] = sorted(node["param_indices"])
            setups = node["setup_count"]
            node["avg_exclusive_ms"] = (
                round(node["total_exclusive_ms"] / setups, 6) if setups else 0.0
            )
            node["total_exclusive_ms"] = round(node["total_exclusive_ms"], 6)
            node["total_inclusive_ms"] = round(node["total_inclusive_ms"], 6)

        self.report = build_report(
            tests=list(self.tests.values()),
            fixtures=list(self.fixtures.values()),
            exitstatus=int(exitstatus),
        )
        try:
            self.outdir.mkdir(parents=True, exist_ok=True)
            (self.outdir / "report.json").write_text(
                json.dumps(self.report, indent=2, ensure_ascii=False), encoding="utf-8"
            )
            (self.outdir / "report.html").write_text(render_html(self.report), encoding="utf-8")
        except OSError as exc:
            self.write_error = str(exc)

    @pytest.hookimpl
    def pytest_terminal_summary(
        self, terminalreporter: Any, exitstatus: int, config: pytest.Config
    ):
        if self.write_error:
            terminalreporter.write_sep("-", "FixtureLens")
            terminalreporter.write_line(f"could not write report: {self.write_error}")
            return
        if self.report is None:
            return
        summary = self.report["summary"]
        terminalreporter.write_sep("-", "FixtureLens")
        terminalreporter.write_line(
            f"{summary['tests']} tests · {summary['fixtures']} fixtures · "
            f"{summary['setup_exclusive_ms']:.1f} ms exclusive setup · "
            f"{summary['reused_setups']} reused setups"
        )
        terminalreporter.write_line(f"report: {self.outdir / 'report.html'}")


def _final_outcome(phases: dict[str, dict[str, Any]]) -> str:
    setup = phases.get("setup", {})
    call = phases.get("call", {})
    teardown = phases.get("teardown", {})
    if setup.get("outcome") == "failed":
        return "error"
    if setup.get("outcome") == "skipped":
        return "skipped"
    if call.get("outcome") == "failed":
        return "failed"
    if call.get("outcome") == "skipped":
        return "skipped"
    if teardown.get("outcome") == "failed":
        return "error"
    if call.get("outcome") == "passed":
        return "passed"
    return "unknown"
