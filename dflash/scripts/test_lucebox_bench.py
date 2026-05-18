import bench_agentic_tools
import bench_http_capability
import bench_http_frontiers
import lucebox_eval
import lucebox_bench


def _cell(max_ctx, budget, mean, status="ok", min_tps=None):
    return {
        "max_ctx": max_ctx,
        "budget": budget,
        "status": status,
        "mean_decode_tps": mean,
        "min_decode_tps": mean if min_tps is None else min_tps,
    }


def _cfg(**kwargs):
    fields = {
        "max_ctx": 32768,
        "budget": 22,
        "lazy": True,
        "prefix_cache_slots": 1,
        "prefill_cache_slots": 0,
        "tool_memory_max_entries": 50000,
        "kv": "auto",
        "prefill_mode": "off",
        "prefill_keep_ratio": 0.05,
        "prefill_threshold": 32000,
        "prefill_drafter": "",
    }
    fields.update(kwargs)
    return lucebox_bench.SweepConfig(**fields)


def test_pick_winner_quick_prefers_speed():
    winner = lucebox_bench.pick_winner([
        _cell(131072, 22, 18.0),
        _cell(32768, 16, 25.0),
    ], profile="quick")

    assert winner["max_ctx"] == 32768
    assert winner["budget"] == 16


def test_pick_winner_context_prefers_highest_context_within_speed_floor():
    winner = lucebox_bench.pick_winner([
        _cell(32768, 16, 25.0),
        _cell(65536, 22, 23.0),
        _cell(131072, 22, 18.0),
    ], profile="context", min_context_speed_ratio=0.85)

    assert winner["max_ctx"] == 65536
    assert winner["budget"] == 22


def test_rank_candidates_context_keeps_fallback_order():
    ranked = lucebox_bench.rank_candidates([
        _cell(32768, 16, 30.0),
        _cell(98304, 16, 20.0),
        _cell(98304, 22, 26.0),
        _cell(114688, 22, 23.0),
    ], profile="context", min_context_speed_ratio=0.75)

    assert [(c["max_ctx"], c["budget"]) for c in ranked[:3]] == [
        (114688, 22),
        (98304, 22),
        (32768, 16),
    ]


def test_rank_candidates_stress_uses_context_policy():
    ranked = lucebox_bench.rank_candidates([
        _cell(65536, 16, 26.0),
        _cell(98304, 16, 24.0),
        _cell(114688, 22, 18.0),
    ], profile="stress", min_context_speed_ratio=0.85)

    assert [(c["max_ctx"], c["budget"]) for c in ranked] == [
        (98304, 16),
        (65536, 16),
    ]


def test_pick_winner_context_uses_fastest_budget_inside_highest_viable_context():
    winner = lucebox_bench.pick_winner([
        _cell(32768, 16, 25.0),
        _cell(65536, 16, 22.0),
        _cell(65536, 22, 23.0),
    ], profile="context", min_context_speed_ratio=0.85)

    assert winner["max_ctx"] == 65536
    assert winner["budget"] == 22


def test_context_values_for_profile_quick_uses_configured_env(monkeypatch):
    monkeypatch.setenv("DFLASH_MAX_CTX", "114688")

    assert lucebox_bench.context_values_for_profile("quick", "") == [114688]


def test_context_values_for_profile_context_caps_to_configured_env(monkeypatch):
    monkeypatch.setenv("DFLASH_MAX_CTX", "98304")

    assert lucebox_bench.context_values_for_profile("context", "") == [
        32768, 65536, 98304,
    ]


def test_sweep_configs_expands_requested_tunables(monkeypatch):
    monkeypatch.setenv("DFLASH_MAX_CTX", "65536")
    args = type("Args", (), {
        "profile": "context",
        "ctx_values": "32768",
        "budgets": "16,22",
        "lazy_values": "0,1",
        "prefix_cache_slots_values": "0,1",
        "prefill_cache_slots_values": "",
        "tool_memory_max_entries_values": "",
        "kv_values": "auto,q4_0",
        "prefill_modes": "off",
        "prefill_keep_ratios": "",
        "prefill_thresholds": "",
        "prefill_drafter": "",
    })()

    configs = lucebox_bench.sweep_configs(args)

    assert len(configs) == 16
    assert any(c.budget == 16 and c.lazy is False and c.kv == "q4_0" for c in configs)


def test_sweep_configs_defaults_to_current_kv(monkeypatch):
    monkeypatch.setenv("DFLASH_MAX_CTX", "65536")
    monkeypatch.setenv("DFLASH_CACHE_TYPE_K", "q4_0")
    monkeypatch.setenv("DFLASH_CACHE_TYPE_V", "q4_0")
    args = type("Args", (), {
        "profile": "quick",
        "ctx_values": "32768",
        "budgets": "22",
        "lazy_values": "",
        "prefix_cache_slots_values": "",
        "prefill_cache_slots_values": "",
        "tool_memory_max_entries_values": "",
        "kv_values": "",
        "prefill_modes": "off",
        "prefill_keep_ratios": "",
        "prefill_thresholds": "",
        "prefill_drafter": "",
    })()

    configs = lucebox_bench.sweep_configs(args)

    assert [c.kv for c in configs] == ["q4_0"]


def test_build_server_argv_includes_tuned_flags(tmp_path):
    target = tmp_path / "target.gguf"
    target.write_text("")
    drafter = tmp_path / "Qwen3-0.6B-BF16.gguf"
    drafter.write_text("")
    cfg = _cfg(
        kv="q4_0",
        prefix_cache_slots=0,
        prefill_cache_slots=1,
        prefill_mode="auto",
        prefill_threshold=512,
        prefill_keep_ratio=0.1,
        prefill_drafter=str(drafter),
    )

    argv = lucebox_bench.build_server_argv(cfg, target)

    assert "--cache-type-k" in argv
    assert "--cache-type-v" in argv
    assert "--prefix-cache-slots" in argv
    assert argv[argv.index("--prefix-cache-slots") + 1] == "0"
    assert "--prefill-cache-slots" in argv
    assert argv[argv.index("--prefill-cache-slots") + 1] == "1"
    assert "--prefill-compression" in argv
    assert argv[argv.index("--prefill-compression") + 1] == "auto"


def test_build_server_env_includes_tool_memory_override():
    env = lucebox_bench.build_server_env(_cfg(tool_memory_max_entries=0))

    assert env["DFLASH_TOOL_MEMORY_MAX_ENTRIES"] == "0"


def test_build_server_argv_persists_f16_as_cache_type(tmp_path):
    target = tmp_path / "target.gguf"
    target.write_text("")

    argv = lucebox_bench.build_server_argv(_cfg(kv="f16"), target)

    assert "--kv-f16" not in argv
    assert argv[argv.index("--cache-type-k") + 1] == "f16"
    assert argv[argv.index("--cache-type-v") + 1] == "f16"


def test_http_frontier_retries_empty_completion(monkeypatch):
    rows = [
        {"completion_tokens": 0},
        {"completion_tokens": 12},
    ]

    def fake_run_one(*_args):
        return rows.pop(0)

    monkeypatch.setattr(bench_http_frontiers, "run_one", fake_run_one)

    row = bench_http_frontiers.run_frontier("http://test", "prompt", 16, 1, retries=2)

    assert row["completion_tokens"] == 12
    assert row["attempt"] == 2


def test_capability_answer_extractors_ignore_hidden_thinking():
    assert bench_http_capability.find_answer(
        {"kind": "choice", "choices": ["x", "y"], "answer": "B"},
        "<think>Answer: A</think>\nAnswer: B",
    ) == "B"
    assert bench_http_capability.find_answer(
        {"kind": "integer", "answer": "42"},
        "scratch 7\nAnswer: 0042",
    ) == "42"


def test_agentic_tool_case_retries_until_expected_call(monkeypatch):
    rows = [
        {"ok": False, "attempt": 1},
        {"ok": True, "attempt": 2},
    ]

    def fake_run_case_once(*_args):
        return rows.pop(0)

    monkeypatch.setattr(bench_agentic_tools, "run_case_once", fake_run_case_once)

    row = bench_agentic_tools.run_case(
        "http://test", {"name": "x", "expected": "read_file"}, timeout_s=1, retries=2)

    assert row["ok"] is True
    assert row["attempt"] == 2


def test_agentic_tool_call_requires_schema_valid_args(monkeypatch):
    payload = {
        "choices": [{
            "message": {
                "tool_calls": [{
                    "id": "call_1",
                    "function": {
                        "name": "read_file",
                        "arguments": "{}",
                    },
                }],
                "content": "",
            },
            "finish_reason": "tool_calls",
        }],
    }

    class FakeResp:
        status = 200

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            import json
            return json.dumps(payload).encode()

    monkeypatch.setattr(bench_agentic_tools.urllib.request, "urlopen", lambda *_a, **_k: FakeResp())

    row = bench_agentic_tools.run_case_once(
        "http://test", {"name": "x", "expected": "read_file", "prompt": "x"}, 1, 1)

    assert row["tool_names"] == ["read_file"]
    assert row["tool_args_valid"] is False
    assert row["ok"] is False


def test_lucebox_eval_area_parser_and_summary():
    assert lucebox_eval.parse_areas("all") == list(lucebox_eval.ALL_AREAS)
    assert lucebox_eval.parse_areas("api,tools") == ["api", "tools"]

    summary = lucebox_eval.summarize([
        {"id": "a", "area": "api", "status": "passed", "grade": 1.0, "wall_ms": 10},
        {"id": "b", "area": "api", "status": "failed", "grade": 0.0, "wall_ms": 20},
        {"id": "c", "area": "cache", "status": "skipped", "grade": 1.0, "wall_ms": 1},
    ])

    assert summary["passed"] == 1
    assert summary["total"] == 2
    assert summary["skipped"] == 1
    assert summary["by_area"]["api"]["pass_rate"] == 0.5


def test_lucebox_eval_props_hash_ignores_cache_counters():
    props = {
        "default_generation_settings": {"n_ctx": 8192},
        "model_alias": "luce-dflash",
        "model_path": "/m.gguf",
        "build_info": "x",
        "speculative_mode": "dflash",
        "runtime": {"backend": "cuda"},
        "reasoning": {"supported": True},
        "server": {"name": "luce-dflash"},
        "prefix_cache": {"lifetime_hits": 1},
    }
    changed = dict(props)
    changed["prefix_cache"] = {"lifetime_hits": 99}

    assert lucebox_eval.props_hash(props) == lucebox_eval.props_hash(changed)


def test_lucebox_eval_matrix_documents_depths_and_areas():
    matrix = lucebox_eval.matrix()

    assert matrix["depths"] == lucebox_eval.DEPTHS
    assert set(matrix["areas"]) == set(lucebox_eval.ALL_AREAS)
    assert matrix["depth_config"]["smoke"]["long_frontiers"] == [512]


def test_run_extra_suites_marks_failed_suite_and_cleans_process(monkeypatch, tmp_path):
    class FakeProc:
        pid = 123

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(lucebox_bench, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(lucebox_bench, "wait_ready", lambda _timeout: True)
    monkeypatch.setattr(lucebox_bench.subprocess, "Popen", lambda *_args, **_kwargs: FakeProc())
    monkeypatch.setattr(lucebox_bench.subprocess, "call", lambda _cmd: 1)
    monkeypatch.setattr(lucebox_bench.os, "killpg", lambda *_args: None)
    monkeypatch.setattr(lucebox_bench, "build_server_argv", lambda *_args: ["server"])

    results = lucebox_bench.run_extra_suites(
        _cfg(), tmp_path / "target.gguf", ["capability"], 1, "512", 1,
        "smoke", "all", False, "")

    assert len(results) == 1
    assert results[0]["suite"] == "capability"
    assert results[0]["status"] == "failed"
    assert results[0]["returncode"] == 1
    assert results[0]["report"] == str(tmp_path / "bench-capability.json")


def test_run_extra_suites_invokes_consolidated_eval(monkeypatch, tmp_path):
    class FakeProc:
        pid = 123

        def wait(self, timeout=None):
            return 0

    called = {}

    def fake_call(cmd):
        called["cmd"] = cmd
        return 0

    monkeypatch.setattr(lucebox_bench, "REPORT_DIR", tmp_path)
    monkeypatch.setattr(lucebox_bench, "wait_ready", lambda _timeout: True)
    monkeypatch.setattr(lucebox_bench.subprocess, "Popen", lambda *_args, **_kwargs: FakeProc())
    monkeypatch.setattr(lucebox_bench.subprocess, "call", fake_call)
    monkeypatch.setattr(lucebox_bench.os, "killpg", lambda *_args: None)
    monkeypatch.setattr(lucebox_bench, "build_server_argv", lambda *_args: ["server"])

    results = lucebox_bench.run_extra_suites(
        _cfg(), tmp_path / "target.gguf", ["lucebox-eval"], 1, "512", 1,
        "standard", "api,tools", True, "api")

    assert results[0]["suite"] == "lucebox-eval"
    assert results[0]["status"] == "ok"
    assert "--depth" in called["cmd"]
    assert called["cmd"][called["cmd"].index("--depth") + 1] == "standard"
    assert "--areas" in called["cmd"]
    assert called["cmd"][called["cmd"].index("--areas") + 1] == "api,tools"
    assert "--soak" in called["cmd"]
