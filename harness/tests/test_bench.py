"""Coverage for harness.bench.main() --area / --areas resolution.

main() resolves the (area, areas) pair before delegating to run_bench. We
stub run_bench so no luce-bench subprocess runs, and capture the kwargs it
would have received. Bad combinations exit 2 without calling run_bench.
"""

from __future__ import annotations

import pytest

from harness import bench


@pytest.fixture
def capture_run_bench(monkeypatch):
    """Stub run_bench; capture its kwargs. Returns the capture dict."""
    captured: dict = {}

    def fake_run_bench(**kwargs):
        captured.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(bench, "run_bench", fake_run_bench)
    return captured


def _run_main(monkeypatch, argv: list[str]) -> int:
    monkeypatch.setattr("sys.argv", ["harness-run-bench", *argv])
    return bench.main()


def test_single_area_via_areas_routes_to_area(capture_run_bench, monkeypatch) -> None:
    rc = _run_main(monkeypatch, ["--base-url", "http://x", "--areas", "code"])
    assert rc == 0
    assert capture_run_bench["area"] == "code"
    assert capture_run_bench["areas"] is None


def test_multi_areas_triggers_sweep(capture_run_bench, monkeypatch) -> None:
    rc = _run_main(
        monkeypatch, ["--base-url", "http://x", "--areas", "code,gsm8k"]
    )
    assert rc == 0
    # Sweep mode: area=None, the literal selector forwarded as areas.
    assert capture_run_bench["area"] is None
    assert capture_run_bench["areas"] == "code,gsm8k"


def test_areas_all_triggers_sweep(capture_run_bench, monkeypatch) -> None:
    rc = _run_main(monkeypatch, ["--base-url", "http://x", "--areas", "all"])
    assert rc == 0
    assert capture_run_bench["area"] is None
    assert capture_run_bench["areas"] == "all"


def test_area_flag_routes_to_area(capture_run_bench, monkeypatch) -> None:
    rc = _run_main(monkeypatch, ["--base-url", "http://x", "--area", "code"])
    assert rc == 0
    assert capture_run_bench["area"] == "code"
    assert capture_run_bench["areas"] is None


def test_area_and_areas_both_exits_2(capture_run_bench, monkeypatch) -> None:
    rc = _run_main(
        monkeypatch,
        ["--base-url", "http://x", "--area", "code", "--areas", "gsm8k"],
    )
    assert rc == 2
    assert capture_run_bench == {}  # run_bench never called


def test_bogus_single_areas_exits_2(capture_run_bench, monkeypatch) -> None:
    rc = _run_main(
        monkeypatch, ["--base-url", "http://x", "--areas", "not-an-area"]
    )
    assert rc == 2
    assert capture_run_bench == {}


def test_known_areas_constant_matches_resolver() -> None:
    """KNOWN_AREAS is the single source for the --areas single-name check."""
    assert "smoke" in bench.KNOWN_AREAS
    assert "code" in bench.KNOWN_AREAS
    assert "not-an-area" not in bench.KNOWN_AREAS
