"""Run the golden set and report accuracy, routing, latency, tokens and cost.

Usage: python evals/run_evals.py
Writes results/eval_<timestamp>.json. Extend golden_set.jsonl with more questions.
"""
import asyncio
import json
import statistics
import time
from pathlib import Path

from oracle.service import ask

GOLDEN = Path(__file__).parent / "golden_set.jsonl"


def load_cases() -> list[dict]:
    return [json.loads(line) for line in GOLDEN.read_text().splitlines() if line.strip()]


def percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, round(pct * (len(ordered) - 1)))]


async def main() -> None:
    rows = []
    for case in load_cases():
        try:
            result = await ask(case["question"])
        except Exception as exc:  # noqa: BLE001
            rows.append({"id": case["id"], "type": case["type"], "error": str(exc),
                         "route_ok": False, "content_ok": False, "latency_ms": 0,
                         "cost_usd": 0, "output_tokens": 0})
            continue
        answer = result["answer"].lower()
        called = set(result["metrics"]["tool_calls"])
        rows.append({
            "id": case["id"],
            "type": case["type"],
            "route_ok": set(case["expect_tools"]).issubset(called),
            "content_ok": all(k.lower() in answer for k in case["must_contain"]),
            "latency_ms": result["metrics"]["latency_ms"],
            "output_tokens": result["metrics"]["output_tokens"],
            "tokens_per_sec": result["metrics"]["tokens_per_sec"],
            "cost_usd": result["metrics"]["cost_usd"],
            "answer": result["answer"],
        })
        print(f"{case['id']:8} route={rows[-1]['route_ok']} content={rows[-1]['content_ok']} "
              f"{rows[-1]['latency_ms']:.0f} ms")

    n = len(rows)
    latencies = [r["latency_ms"] for r in rows if r["latency_ms"]]
    summary = {
        "cases": n,
        "routing_accuracy": sum(r["route_ok"] for r in rows) / n,
        "content_accuracy": sum(r["content_ok"] for r in rows) / n,
        "p50_latency_ms": statistics.median(latencies) if latencies else 0,
        "p95_latency_ms": percentile(latencies, 0.95) if latencies else 0,
        "avg_cost_usd": sum(r["cost_usd"] for r in rows) / n,
    }
    print("\n" + json.dumps(summary, indent=2))
    out_dir = Path("results")
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"eval_{time.strftime('%Y%m%d_%H%M%S')}.json"
    out.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2))
    print(f"Saved {out}")


if __name__ == "__main__":
    asyncio.run(main())
