"""
Benchmark JSON parse success rate for slide generation.
Dataset format (JSONL): {"topic": "...", "num_slides": 8}
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path
from typing import List, Tuple

import requests

DEFAULT_BASE_URL = "http://localhost:8000/api"
RESULT_DIR = Path(__file__).parent / "results"


def load_dataset(path: Path) -> List[dict]:
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def validate_slides(payload: dict) -> Tuple[bool, str]:
    if not isinstance(payload, dict):
        return False, "payload_not_dict"
    slides = payload.get("slides")
    if not isinstance(slides, list) or not slides:
        return False, "missing_slides"
    for i, slide in enumerate(slides):
        if not isinstance(slide, dict):
            return False, f"slide_{i}_not_dict"
        if "title_text" not in slide:
            return False, f"slide_{i}_missing_title"
        content = slide.get("content") or slide.get("text")
        if content is None:
            return False, f"slide_{i}_missing_content"
    return True, "ok"


def call_generate(base_url: str, topic: str, num_slides: int) -> Tuple[dict, float, str]:
    url = base_url.rstrip("/") + "/slides/generate"
    data = {"topic": topic, "num_slides": num_slides}
    start = time.perf_counter()
    resp = requests.post(url, data=data, timeout=180)
    elapsed_ms = (time.perf_counter() - start) * 1000
    if resp.status_code != 200:
        return {}, elapsed_ms, f"http {resp.status_code}: {resp.text[:200]}"
    try:
        payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        return {}, elapsed_ms, f"json_error: {exc}"
    return payload, elapsed_ms, "ok"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to JSONL with topic/num_slides")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Backend base URL (default: %(default)s)")
    parser.add_argument("--runs", type=int, default=30, help="Total runs (if larger than dataset, cycles over)")
    args = parser.parse_args()

    samples = load_dataset(Path(args.dataset))
    if not samples:
        raise SystemExit("Dataset empty")

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = RESULT_DIR / f"json_parse_eval_{int(time.time())}.csv"

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["run_id", "topic", "num_slides", "latency_ms", "valid", "status"])
        for i in range(args.runs):
            sample = samples[i % len(samples)]
            topic = sample.get("topic") or ""
            num_slides = int(sample.get("num_slides", 10))
            payload, latency_ms, status = call_generate(args.base_url, topic, num_slides)
            is_valid, reason = validate_slides(payload)
            writer.writerow([i, topic, num_slides, round(latency_ms, 2), int(is_valid), reason if status == "ok" else status])
            f.flush()

    print(f"Wrote results to {out_csv}")


if __name__ == "__main__":
    main()
