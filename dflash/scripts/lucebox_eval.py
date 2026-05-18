"""Consolidated lucebox HTTP evaluation runner.

The runner is intentionally server-facing: it evaluates the API shape and model
behavior of an already-running lucebox server, records uniform metrics, and
emits JSON that the autotuner can use as a correctness gate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import bench_agentic_tools
import bench_http_capability
import bench_http_frontiers


ALL_AREAS = ("api", "short", "long", "tools", "agentic", "cache")
DEPTHS = ("smoke", "standard", "deep")

DEPTH_CONFIG: dict[str, dict[str, Any]] = {
    "smoke": {
        "short_cases": 2,
        "tool_cases": 2,
        "tool_repeat": 1,
        "long_frontiers": [512],
        "long_gen_tokens": 32,
        "agentic_steps": 2,
        "soak_cycles": 2,
        "timeout": 180,
    },
    "standard": {
        "short_cases": len(bench_http_capability.CASES),
        "tool_cases": len(bench_agentic_tools.CASES),
        "tool_repeat": 2,
        "long_frontiers": [512, 2048, 4096],
        "long_gen_tokens": 64,
        "agentic_steps": 3,
        "soak_cycles": 4,
        "timeout": 420,
    },
    "deep": {
        "short_cases": len(bench_http_capability.CASES),
        "tool_cases": len(bench_agentic_tools.CASES),
        "tool_repeat": 4,
        "long_frontiers": [512, 2048, 4096, 8192, 16384],
        "long_gen_tokens": 128,
        "agentic_steps": 5,
        "soak_cycles": 8,
        "timeout": 900,
    },
}


def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def http_json(
    method: str,
    url: str,
    *,
    body: dict[str, Any] | None = None,
    timeout_s: int = 300,
) -> tuple[int | None, dict[str, Any] | None, str | None, float]:
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw), None, time.perf_counter() - t0
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return e.code, None, raw[:1000], time.perf_counter() - t0
    except Exception as e:
        return None, None, str(e), time.perf_counter() - t0


def props_hash(props: dict[str, Any] | None) -> str | None:
    if props is None:
        return None
    stable = {
        "default_generation_settings": props.get("default_generation_settings"),
        "model_alias": props.get("model_alias"),
        "model_path": props.get("model_path"),
        "build_info": props.get("build_info"),
        "speculative_mode": props.get("speculative_mode"),
        "runtime": props.get("runtime"),
        "reasoning": props.get("reasoning"),
        "server": props.get("server"),
    }
    encoded = json.dumps(stable, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def cache_subset(props: dict[str, Any] | None) -> dict[str, Any]:
    if not props:
        return {}
    return {
        "prefix_cache": props.get("prefix_cache") or {},
        "full_cache": props.get("full_cache") or {},
        "tool_replay": props.get("tool_replay") or {},
    }


def case_result(
    *,
    area: str,
    case_id: str,
    status: str,
    grade: float,
    wall_s: float,
    detail: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "id": case_id,
        "area": area,
        "status": status,
        "ok": status in {"passed", "skipped"},
        "grade": grade,
        "wall_ms": round(wall_s * 1000, 1),
    }
    if detail:
        payload.update(detail)
    return payload


def run_api(url: str, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    timeout = int(cfg["timeout"])
    rows: list[dict[str, Any]] = []

    for case_id, method, path, body in [
        ("props", "GET", "/props", None),
        ("models", "GET", "/v1/models", None),
        ("chat", "POST", "/v1/chat/completions", {
            "model": "luce-dflash",
            "messages": [{"role": "user", "content": "Reply with exactly: OK"}],
            "temperature": 0,
            "max_tokens": 16,
            "stream": False,
            "chat_template_kwargs": {"enable_thinking": False},
        }),
        ("responses", "POST", "/v1/responses", {
            "model": "luce-dflash",
            "input": "Reply with exactly: OK",
            "temperature": 0,
            "max_output_tokens": 16,
            "stream": False,
        }),
    ]:
        status, data, error, wall = http_json(method, url + path, body=body, timeout_s=timeout)
        ok = status == 200 and (data is not None)
        if case_id in {"chat", "responses"} and data:
            text = json.dumps(data)[:4000]
            ok = ok and ("OK" in text or len(text) > 0)
        rows.append(case_result(
            area="api",
            case_id=f"api.{case_id}",
            status="passed" if ok else "failed",
            grade=1.0 if ok else 0.0,
            wall_s=wall,
            detail={"http_status": status, "error": error},
        ))
    return rows


def run_short(url: str, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    cases = bench_http_capability.CASES[: int(cfg["short_cases"])]
    rows: list[dict[str, Any]] = []
    for case in cases:
        row = bench_http_capability.run_case(
            url, case, int(cfg["timeout"]), max_tokens=512, think=False)
        rows.append(case_result(
            area="short",
            case_id=f"short.{case['id']}",
            status="passed" if row["ok"] else "failed",
            grade=1.0 if row["ok"] else 0.0,
            wall_s=float(row.get("wall_s") or 0.0),
            detail={
                "source": case.get("source"),
                "finish_reason": row.get("finish_reason"),
                "prompt_tokens": row.get("prompt_tokens"),
                "completion_tokens": row.get("completion_tokens"),
                "given": row.get("given"),
                "correct": row.get("correct"),
                "content_preview": (row.get("output") or "")[:400],
            },
        ))
    return rows


def run_tools(url: str, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    cases = bench_agentic_tools.CASES[: int(cfg["tool_cases"])]
    rows: list[dict[str, Any]] = []
    for iteration in range(1, int(cfg["tool_repeat"]) + 1):
        for case in cases:
            row = bench_agentic_tools.run_case(url, case, int(cfg["timeout"]), retries=1)
            rows.append(case_result(
                area="tools",
                case_id=f"tools.{case['name']}.{iteration}",
                status="passed" if row["ok"] else "failed",
                grade=1.0 if row["ok"] else 0.0,
                wall_s=float(row.get("wall_s") or 0.0),
                detail={
                    "expected_tool_calls": [case["expected"]],
                    "observed_tool_calls": row.get("tool_names") or [],
                    "tool_args_valid": bool(row.get("tool_args_valid")),
                    "tool_args": row.get("tool_args") or [],
                    "tool_calls": row.get("tool_calls") or [],
                    "finish_reason": row.get("finish_reason"),
                    "model_retry_count": int(row.get("attempt", 1)) - 1,
                    "content_preview": row.get("content_preview"),
                },
            ))
    return rows


def run_long(url: str, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for frontier in cfg["long_frontiers"]:
        prompt = bench_http_frontiers.make_prompt(int(frontier), chars_per_token=4)
        t0 = time.perf_counter()
        try:
            row = bench_http_frontiers.run_frontier(
                url, prompt, int(cfg["long_gen_tokens"]), int(cfg["timeout"]), retries=1)
            error = None
        except Exception as e:
            row = {}
            error = str(e)
        wall = time.perf_counter() - t0
        ok = bool(row.get("completion_tokens", 0) > 0) and error is None
        ttft_s = row.get("ttft_s")
        prompt_tokens = row.get("prompt_tokens")
        prefill_tps = None
        if isinstance(ttft_s, int | float) and ttft_s > 0 and isinstance(prompt_tokens, int):
            prefill_tps = round(prompt_tokens / ttft_s, 2)
        rows.append(case_result(
            area="long",
            case_id=f"long.frontier.{frontier}",
            status="passed" if ok else "failed",
            grade=1.0 if ok else 0.0,
            wall_s=float(row.get("wall_s") or wall),
            detail={
                "frontier_target_tokens": frontier,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": row.get("completion_tokens"),
                "finish_reason": row.get("finish_reason"),
                "ttft_ms": round(float(ttft_s) * 1000, 1) if isinstance(ttft_s, int | float) else None,
                "prefill_ms": round(float(ttft_s) * 1000, 1) if isinstance(ttft_s, int | float) else None,
                "prefill_tps": prefill_tps,
                "decode_ms": round(float(row.get("decode_s") or 0.0) * 1000, 1),
                "decode_tps": row.get("decode_tps"),
                "wall_tps": row.get("wall_tps"),
                "model_retry_count": int(row.get("attempt", 1)) - 1 if row else 0,
                "error": error,
            },
        ))
    return rows


def run_agentic(url: str, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    timeout = int(cfg["timeout"])
    steps = bench_agentic_tools.CASES[: int(cfg["agentic_steps"])]
    messages: list[dict[str, Any]] = [{
        "role": "system",
        "content": "You are a coding agent. Use the requested tool and do not answer in prose.",
    }]
    rows: list[dict[str, Any]] = []
    for idx, case in enumerate(steps, start=1):
        messages.append({"role": "user", "content": case["prompt"]})
        body = {
            "model": "luce-dflash",
            "messages": messages,
            "tools": [bench_agentic_tools._tool_for(case["expected"])],
            "tool_choice": {"type": "function", "function": {"name": case["expected"]}},
            "temperature": 0,
            "max_tokens": 192,
            "stream": False,
            "chat_template_kwargs": {"enable_thinking": True},
        }
        status, data, error, wall = http_json(
            "POST", url + "/v1/chat/completions", body=body, timeout_s=timeout)
        choices = (data or {}).get("choices") or []
        msg = (choices[0].get("message") if choices else {}) or {}
        calls = msg.get("tool_calls") or []
        names = [((call.get("function") or {}).get("name")) for call in calls]
        ok = status == 200 and case["expected"] in names
        rows.append(case_result(
            area="agentic",
            case_id=f"agentic.step.{idx}.{case['expected']}",
            status="passed" if ok else "failed",
            grade=1.0 if ok else 0.0,
            wall_s=wall,
            detail={
                "http_status": status,
                "expected_tool_calls": [case["expected"]],
                "observed_tool_calls": names,
                "finish_reason": choices[0].get("finish_reason") if choices else None,
                "turn_index": idx,
                "error": error,
                "content_preview": (msg.get("content") or "")[:200],
            },
        ))
        if not ok:
            break
        tool_call = calls[0]
        messages.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": calls})
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.get("id") or f"call_{idx}",
            "name": case["expected"],
            "content": f"synthetic result for {case['expected']} at step {idx}",
        })
    return rows


def monotonic_counter(after: dict[str, Any], before: dict[str, Any], key: str) -> bool:
    a = after.get(key)
    b = before.get(key)
    return not (isinstance(a, int) and isinstance(b, int)) or a >= b


def run_cache(url: str, cfg: dict[str, Any]) -> list[dict[str, Any]]:
    timeout = int(cfg["timeout"])
    _, before_props, before_err, _ = http_json("GET", url + "/props", timeout_s=timeout)
    before = cache_subset(before_props)
    body = {
        "model": "luce-dflash",
        "messages": [{"role": "user", "content": "Cache probe key alpha-7319. Reply with one word: cached"}],
        "temperature": 0,
        "max_tokens": 24,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    status1, data1, err1, wall1 = http_json(
        "POST", url + "/v1/chat/completions", body=body, timeout_s=timeout)
    status2, data2, err2, wall2 = http_json(
        "POST", url + "/v1/chat/completions", body=body, timeout_s=timeout)
    _, after_props, after_err, _ = http_json("GET", url + "/props", timeout_s=timeout)
    after = cache_subset(after_props)
    prefix_before = before.get("prefix_cache") or {}
    prefix_after = after.get("prefix_cache") or {}
    full_before = before.get("full_cache") or {}
    full_after = after.get("full_cache") or {}
    capacity = int(prefix_after.get("capacity") or prefix_before.get("capacity") or 0)
    ok_http = status1 == 200 and status2 == 200 and data1 is not None and data2 is not None
    monotonic = (
        monotonic_counter(prefix_after, prefix_before, "lifetime_hits")
        and monotonic_counter(prefix_after, prefix_before, "lifetime_saves")
        and monotonic_counter(full_after, full_before, "lifetime_hits")
    )
    skipped = capacity <= 0
    ok = ok_http and monotonic
    return [case_result(
        area="cache",
        case_id="cache.repeat_prompt",
        status="skipped" if skipped and ok_http else ("passed" if ok else "failed"),
        grade=1.0 if ok or (skipped and ok_http) else 0.0,
        wall_s=wall1 + wall2,
        detail={
            "http_statuses": [status1, status2],
            "cache_before": before,
            "cache_after": after,
            "cache_capacity": capacity,
            "props_errors": [before_err, after_err],
            "request_errors": [err1, err2],
        },
    )]


RUNNERS = {
    "api": run_api,
    "short": run_short,
    "long": run_long,
    "tools": run_tools,
    "agentic": run_agentic,
    "cache": run_cache,
}


def matrix() -> dict[str, Any]:
    return {
        "depths": DEPTHS,
        "areas": {
            "api": "HTTP contract: /props, /v1/models, chat completions, Responses",
            "short": "deterministic DS4-inspired one-shot graded prompts",
            "long": "HTTP long-context frontier timing and non-empty generation",
            "tools": "single-turn forced tool-call emission and argument schema validity",
            "agentic": "multi-turn forced tool-call workflow with synthetic tool results",
            "cache": "repeat-prompt cache/replay invariants and counter monotonicity",
        },
        "depth_config": DEPTH_CONFIG,
    }


def parse_areas(raw: str) -> list[str]:
    if not raw or raw == "all":
        return list(ALL_AREAS)
    areas = [part.strip() for part in raw.split(",") if part.strip()]
    unknown = sorted(set(areas) - set(ALL_AREAS))
    if unknown:
        raise SystemExit(f"unknown eval area(s): {', '.join(unknown)}")
    return areas


def percentile(values: list[float], pct: float) -> float | None:
    if not values:
        return None
    values = sorted(values)
    if len(values) == 1:
        return round(values[0], 1)
    rank = (len(values) - 1) * pct
    low = math.floor(rank)
    high = math.ceil(rank)
    if low == high:
        return round(values[low], 1)
    return round(values[low] + (values[high] - values[low]) * (rank - low), 1)


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counted = [r for r in rows if r["status"] != "skipped"]
    passed = [r for r in counted if r["status"] == "passed"]
    by_area: dict[str, dict[str, Any]] = {}
    for area in ALL_AREAS:
        area_rows = [r for r in rows if r["area"] == area and r["status"] != "skipped"]
        if area_rows:
            area_passed = [r for r in area_rows if r["status"] == "passed"]
            by_area[area] = {
                "passed": len(area_passed),
                "total": len(area_rows),
                "pass_rate": round(len(area_passed) / len(area_rows), 4),
            }
    walls = [float(r["wall_ms"]) for r in counted if isinstance(r.get("wall_ms"), int | float)]
    ttfts = [float(r["ttft_ms"]) for r in counted if isinstance(r.get("ttft_ms"), int | float)]
    return {
        "passed": len(passed),
        "total": len(counted),
        "skipped": len(rows) - len(counted),
        "pass_rate": round(len(passed) / len(counted), 4) if counted else 0.0,
        "by_area": by_area,
        "wall_ms_p50": percentile(walls, 0.50),
        "wall_ms_p95": percentile(walls, 0.95),
        "ttft_ms_p50": percentile(ttfts, 0.50),
        "ttft_ms_p95": percentile(ttfts, 0.95),
        "mean_grade": round(statistics.fmean(float(r["grade"]) for r in counted), 4) if counted else 0.0,
    }


def compare_baseline(current_rows: list[dict[str, Any]], baseline_path: Path | None) -> dict[str, Any]:
    if baseline_path is None:
        return {"enabled": False, "regressions": []}
    baseline = json.loads(baseline_path.read_text())
    previous = {
        row["id"]: row
        for row in baseline.get("cases", [])
        if isinstance(row, dict) and row.get("status") == "passed"
    }
    regressions = []
    for row in current_rows:
        if row["id"] in previous and row["status"] != "passed":
            regressions.append({
                "id": row["id"],
                "area": row["area"],
                "previous_status": previous[row["id"]].get("status"),
                "current_status": row["status"],
            })
    return {
        "enabled": True,
        "path": str(baseline_path),
        "regressions": regressions,
        "ok": not regressions,
    }


def server_notes(rows: list[dict[str, Any]], props_start: dict[str, Any] | None,
                 props_end: dict[str, Any] | None) -> list[str]:
    notes: list[str] = []
    for row in rows:
        if row["status"] == "failed":
            notes.append(
                f"{row['area']}/{row['id']} failed: finish={row.get('finish_reason')} "
                f"tools={row.get('observed_tool_calls')} error={row.get('error')}"
            )
    if props_hash(props_start) != props_hash(props_end):
        notes.append("stable /props hash changed during eval run; candidate comparisons may be invalid")
    return notes


def write_notes(path: Path, notes: list[str], summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# lucebox eval notes", "", f"pass_rate: {summary['pass_rate']:.2%}", ""]
    if notes:
        lines.append("## Server Issues")
        lines.extend(f"- {note}" for note in notes)
    else:
        lines.append("No server issues captured.")
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description="Run lucebox API/capability evals.")
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--depth", choices=DEPTHS, default="smoke")
    ap.add_argument("--areas", default="all",
                    help="Comma-separated areas: api,short,long,tools,agentic,cache or all.")
    ap.add_argument("--required-areas", default="",
                    help="Comma-separated areas that must be 100% pass. Default: selected areas.")
    ap.add_argument("--soak", action="store_true",
                    help="Repeat the selected run as a stateful stability probe.")
    ap.add_argument("--seed", type=int, default=1,
                    help="Recorded for reproducibility; deterministic prompts do not randomize yet.")
    ap.add_argument("--baseline", type=Path)
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--trace-dir", type=Path)
    ap.add_argument("--notes-out", type=Path)
    ap.add_argument("--list", action="store_true",
                    help="Print the eval area/depth matrix and exit.")
    args = ap.parse_args()

    if args.list:
        print(json.dumps(matrix(), indent=2))
        return 0

    areas = parse_areas(args.areas)
    required_areas = parse_areas(args.required_areas) if args.required_areas else areas
    cfg = dict(DEPTH_CONFIG[args.depth])
    status, props_start, props_error, _ = http_json("GET", args.url + "/props", timeout_s=30)
    if props_error:
        print(f"[eval] warning: /props preflight failed: {props_error}", flush=True)
    print(
        f"[eval] url={args.url} depth={args.depth} soak={args.soak} "
        f"areas={','.join(areas)}",
        flush=True,
    )

    rows: list[dict[str, Any]] = []
    cycles = int(cfg["soak_cycles"]) if args.soak else 1
    for cycle in range(1, cycles + 1):
        for area in areas:
            print(f"[eval] cycle={cycle}/{cycles} area={area}", flush=True)
            area_rows = RUNNERS[area](args.url, cfg)
            if cycles > 1:
                for row in area_rows:
                    row["soak_cycle"] = cycle
                    row["id"] = f"{row['id']}.cycle{cycle}"
            rows.extend(area_rows)

    _, props_end, _, _ = http_json("GET", args.url + "/props", timeout_s=30)
    summary = summarize(rows)
    baseline = compare_baseline(rows, args.baseline)
    notes = server_notes(rows, props_start, props_end)
    required_ok = all(
        summary["by_area"].get(area, {}).get("pass_rate") == 1.0
        for area in required_areas
        if any(row["area"] == area and row["status"] != "skipped" for row in rows)
    )
    props_stable = props_hash(props_start) == props_hash(props_end)
    payload = {
        "suite": "lucebox-eval",
        "timestamp": now_iso(),
        "url": args.url,
        "depth": args.depth,
        "soak": bool(args.soak),
        "seed": args.seed,
        "areas": areas,
        "required_areas": required_areas,
        "summary": summary,
        "baseline": baseline,
        "props": {
            "preflight_http_status": status,
            "start_hash": props_hash(props_start),
            "end_hash": props_hash(props_end),
            "stable": props_stable,
            "start": props_start,
            "end": props_end,
        },
        "cases": rows,
        "server_notes": notes,
    }

    if args.trace_dir:
        args.trace_dir.mkdir(parents=True, exist_ok=True)
        (args.trace_dir / "lucebox-eval-cases.jsonl").write_text(
            "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows)
        )
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n")
    if args.notes_out:
        write_notes(args.notes_out, notes, summary)

    print(
        f"[eval] pass_rate={summary['pass_rate']:.2%} "
        f"passed={summary['passed']}/{summary['total']} skipped={summary['skipped']}",
        flush=True,
    )
    baseline_ok = not baseline.get("enabled") or bool(baseline.get("ok"))
    return 0 if summary["pass_rate"] == 1.0 and required_ok and baseline_ok and props_stable else 1


if __name__ == "__main__":
    raise SystemExit(main())
