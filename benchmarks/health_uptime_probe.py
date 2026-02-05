"""
Probe health endpoints periodically and log availability/latency.
"""
from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path
from typing import List

import requests

DEFAULT_BASE_URL = "http://localhost:8000/api"
RESULT_DIR = Path(__file__).parent / "results"

ENDPOINTS = [
    "/health",
    "/health/detailed",
    "/health/ready",
    "/health/live",
]


def probe(base_url: str, endpoint: str) -> tuple[int, float]:
    url = base_url.rstrip("/") + endpoint
    start = time.perf_counter()
    try:
        resp = requests.get(url, timeout=10)
        latency_ms = (time.perf_counter() - start) * 1000
        return resp.status_code, latency_ms
    except Exception:
        latency_ms = (time.perf_counter() - start) * 1000
        return 0, latency_ms


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Backend base URL (default: %(default)s)")
    parser.add_argument("--duration-sec", type=int, default=300, help="Total probing duration in seconds")
    parser.add_argument("--interval-sec", type=float, default=3.0, help="Interval between probes")
    args = parser.parse_args()

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = RESULT_DIR / f"health_probe_{int(time.time())}.csv"

    end_time = time.time() + args.duration_sec
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "endpoint", "status_code", "latency_ms"])
        while time.time() < end_time:
            ts = int(time.time())
            for ep in ENDPOINTS:
                status, latency_ms = probe(args.base_url, ep)
                writer.writerow([ts, ep, status, round(latency_ms, 2)])
            f.flush()
            time.sleep(args.interval_sec)

    print(f"Wrote results to {out_csv}")


if __name__ == "__main__":
    main()
