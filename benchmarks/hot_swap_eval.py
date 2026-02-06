"""
Measure model set/get latency for slide generation service.
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from typing import List, Tuple

import requests

DEFAULT_BASE_URL = "http://localhost:8000/api"
RESULT_DIR = Path(__file__).parent / "results"


def set_model(base_url: str, model: str) -> Tuple[float, str]:
    url = base_url.rstrip("/") + "/slides/set-model"
    start = time.perf_counter()
    resp = requests.post(url, data={"model_name": model}, timeout=30)
    elapsed_ms = (time.perf_counter() - start) * 1000
    if resp.status_code != 200:
        return elapsed_ms, f"http {resp.status_code}: {resp.text[:200]}"
    return elapsed_ms, "ok"


def get_model(base_url: str) -> Tuple[str, float, str]:
    url = base_url.rstrip("/") + "/slides/current-model"
    start = time.perf_counter()
    resp = requests.get(url, timeout=10)
    elapsed_ms = (time.perf_counter() - start) * 1000
    if resp.status_code != 200:
        return "", elapsed_ms, f"http {resp.status_code}: {resp.text[:200]}"
    payload = resp.json()
    return str(payload.get("model_name", "")), elapsed_ms, "ok"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Backend base URL (default: %(default)s)")
    parser.add_argument("--models", nargs="+", required=True, help="Models to toggle between (e.g., qwen3:4b-instruct-2507-q4_K_M llama3.1:8b)")
    parser.add_argument("--runs", type=int, default=10, help="Number of set/get cycles")
    args = parser.parse_args()

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = RESULT_DIR / f"hot_swap_eval_{int(time.time())}.csv"

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "model", "set_latency_ms", "get_latency_ms", "model_after_get", "status_set", "status_get"])
        for i in range(args.runs):
            model = args.models[i % len(args.models)]
            set_ms, status_set = set_model(args.base_url, model)
            current, get_ms, status_get = get_model(args.base_url)
            writer.writerow([i, model, round(set_ms, 2), round(get_ms, 2), current, status_set, status_get])
            f.flush()

    print(f"Wrote results to {out_csv}")


if __name__ == "__main__":
    main()
