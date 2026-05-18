"""Small graded HTTP capability benchmark for lucebox.

This follows the useful mechanics of antirez/ds4's `ds4-eval`: fixed cases,
strict final-answer prompts, answer extraction after any hidden-thinking close
tag, pass/fail grading, and an optional trace file with the exact prompt and
model output. It intentionally uses lucebox's OpenAI-compatible HTTP API and a
small Qwen-appropriate case set rather than DS4's embedded DeepSeek V4 eval.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.request
from pathlib import Path
from typing import Any


SYSTEM_PROMPT = (
    "You are solving a benchmark question. Reason carefully if useful. "
    "The final answer must follow the requested format exactly."
)

CASES = [
    {
        "source": "smoke-mc",
        "id": "arithmetic-choice",
        "kind": "choice",
        "question": "What is 19 + 23?",
        "choices": ["41", "42", "43", "44"],
        "answer": "B",
    },
    {
        "source": "smoke-integer",
        "id": "modular-arithmetic",
        "kind": "integer",
        "question": "Find the least non-negative residue of 12345 modulo 97.",
        "answer": "26",
    },
    {
        "source": "smoke-code",
        "id": "line-localization",
        "kind": "line",
        "question": (
            "Identify the single source line where the bounds bug is introduced. "
            "Return 0 if the function is safe.\n\n"
            "1  int copy_name(char *dst, size_t dst_len, const char *src) {\n"
            "2      size_t n = strlen(src);\n"
            "3      if (n > dst_len) return -1;\n"
            "4      memcpy(dst, src, n + 1);\n"
            "5      return 0;\n"
            "6  }\n"
        ),
        "answer": "3",
    },
    {
        "source": "smoke-context",
        "id": "needle-recall",
        "kind": "integer",
        "question": (
            "Remember this value for the final answer: project_code = 7319.\n"
            "Background: Lucebox benchmark traces should preserve prompt text, "
            "server usage, model output, and grading decisions so regressions "
            "can be inspected after optimizer sweeps. " * 30
            + "\nWhat is project_code?"
        ),
        "answer": "7319",
    },
]


def visible_text(generated: str) -> str:
    close = generated.rfind("</think>")
    if close >= 0:
        return generated[close + len("</think>"):]
    return generated


def build_prompt(case: dict[str, Any]) -> str:
    parts = [case["question"]]
    choices = case.get("choices") or []
    if choices:
        parts.append("\nChoices:")
        for idx, choice in enumerate(choices):
            parts.append(f"{chr(ord('A') + idx)}. {choice}")
        parts.append(
            "\nSolve the question. At the end, write exactly one final line in "
            "this format and do not write anything after it:\nAnswer: <letter>"
        )
    elif case["kind"] == "line":
        parts.append(
            "\nAt the end, write exactly one final line in this format and do "
            "not write anything after it:\nAnswer: <line number>"
        )
    else:
        parts.append(
            "\nSolve the problem. At the end, write exactly one final line in "
            "this format and do not write anything after it:\nAnswer: <integer>"
        )
    return "\n".join(parts)


def find_choice_answer(generated: str, nchoices: int) -> str:
    text = visible_text(generated)
    max_answer = chr(ord("A") + nchoices - 1)
    answer = re.search(r"answer\s*[:\-]?\s*([A-Z])\b", text, flags=re.IGNORECASE)
    if answer:
        got = answer.group(1).upper()
        return got if "A" <= got <= max_answer else "?"
    letters = re.findall(r"\b([A-Z])\b", text.upper())
    for got in reversed(letters):
        if "A" <= got <= max_answer:
            return got
    return "?"


def find_integer_answer(generated: str) -> str:
    text = visible_text(generated)
    answer = re.search(r"answer\s*[:\-]?\s*(-?\d+)\b", text, flags=re.IGNORECASE)
    if answer:
        return str(int(answer.group(1)))
    ints = re.findall(r"-?\d+", text)
    return str(int(ints[-1])) if ints else "?"


def find_answer(case: dict[str, Any], generated: str) -> str:
    if case["kind"] == "choice":
        return find_choice_answer(generated, len(case.get("choices") or []))
    return find_integer_answer(generated)


def run_case(
    url: str,
    case: dict[str, Any],
    timeout_s: int,
    max_tokens: int,
    think: bool,
) -> dict[str, Any]:
    prompt = build_prompt(case)
    body = json.dumps({
        "model": "luce-dflash",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": think},
    }).encode()
    req = urllib.request.Request(
        url + "/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )

    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            data = json.loads(resp.read())
            http_status = resp.status
    except Exception as e:
        return {
            "source": case["source"],
            "id": case["id"],
            "status": "error",
            "ok": False,
            "error": str(e),
            "wall_s": round(time.perf_counter() - t0, 3),
            "prompt": prompt,
            "output": "",
        }

    wall = time.perf_counter() - t0
    choices = data.get("choices") or []
    msg = (choices[0].get("message") if choices else {}) or {}
    output = msg.get("content") or ""
    got = find_answer(case, output)
    ok = got == case["answer"]
    usage = data.get("usage") or {}
    return {
        "source": case["source"],
        "id": case["id"],
        "kind": case["kind"],
        "status": "passed" if ok else "failed",
        "ok": ok,
        "http_status": http_status,
        "finish_reason": choices[0].get("finish_reason") if choices else None,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "given": got,
        "correct": case["answer"],
        "wall_s": round(wall, 3),
        "prompt": prompt,
        "output": output,
    }


def write_trace(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        f.write("# lucebox HTTP capability trace\n")
        for idx, row in enumerate(rows, start=1):
            f.write(
                f"\n===== CASE {idx} {row['source']}/{row['id']} =====\n"
                f"status: {row['status']}\n"
                f"given: {row.get('given', '?')}\n"
                f"correct: {row.get('correct', '?')}\n"
                f"prompt_tokens: {row.get('prompt_tokens')}\n"
                f"completion_tokens: {row.get('completion_tokens')}\n"
                "PROMPT_BEGIN\n"
                f"{row.get('prompt', '')}\n"
                "PROMPT_END\n"
                "MODEL_OUTPUT_BEGIN\n"
                f"{row.get('output', '')}\n"
                "MODEL_OUTPUT_END\n"
            )


def main() -> int:
    ap = argparse.ArgumentParser(description="Run graded HTTP capability prompts.")
    ap.add_argument("--url", default="http://127.0.0.1:8000", help="Server base URL.")
    ap.add_argument("--questions", type=int, default=len(CASES),
                    help="Run only the first N embedded questions.")
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--timeout", type=int, default=300)
    ap.add_argument("--min-pass-rate", type=float, default=1.0)
    ap.add_argument("--think", action="store_true",
                    help="Enable Qwen thinking mode. Default is off for stable visible-answer grading.")
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--trace", type=Path)
    args = ap.parse_args()

    selected = CASES[:max(0, min(args.questions, len(CASES)))]
    rows: list[dict[str, Any]] = []
    print(f"[capability] url={args.url} questions={len(selected)}", flush=True)
    for idx, case in enumerate(selected, start=1):
        row = run_case(args.url, case, args.timeout, args.max_tokens, args.think)
        rows.append(row)
        status = "PASS" if row["ok"] else "FAIL"
        print(
            f"  {idx:2d} {status:4s} {case['source']:14s} {case['id']:20s} "
            f"given={row.get('given', '?')} correct={case['answer']} "
            f"wall={row['wall_s']:.2f}s",
            flush=True,
        )

    passed = sum(1 for row in rows if row["ok"])
    pass_rate = passed / len(rows) if rows else 0.0
    payload = {
        "suite": "capability",
        "source": "ds4-eval-inspired-http-grading",
        "passed": passed,
        "total": len(rows),
        "pass_rate": round(pass_rate, 4),
        "thinking_enabled": bool(args.think),
        "rows": rows,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    print(f"[capability] pass_rate={pass_rate:.2%}", flush=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n")
    if args.trace:
        write_trace(args.trace, rows)
    return 0 if pass_rate >= args.min_pass_rate else 1


if __name__ == "__main__":
    raise SystemExit(main())
