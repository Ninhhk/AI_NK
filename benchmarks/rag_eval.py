"""
Benchmark RAG QA F1 and latency against a running API.
Dataset format (JSONL):
{"doc_path": "path/to/file.txt", "query": "What is ...?", "answers": ["gold1", "gold2"]}
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from pathlib import Path
from typing import Iterable, List, Tuple

import requests

# Document analysis API is under /api/documents
DEFAULT_BASE_URL = "http://localhost:8000/api/documents"
RESULT_DIR = Path(__file__).parent / "results"


def tokenize(text: str) -> List[str]:
    return text.lower().split()


def f1_score(pred: str, gold_list: Iterable[str]) -> float:
    pred_tokens = tokenize(pred)
    best = 0.0
    for gold in gold_list:
        gold_tokens = tokenize(gold)
        if not gold_tokens or not pred_tokens:
            continue
        common = len(set(pred_tokens) & set(gold_tokens))
        if common == 0:
            continue
        precision = common / len(pred_tokens)
        recall = common / len(gold_tokens)
        f1 = 2 * precision * recall / (precision + recall)
        best = max(best, f1)
    return best


def load_dataset(path: Path) -> List[dict]:
    items = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def post_qa(base_url: str, doc_path: Path, question: str) -> Tuple[str, float, str]:
    url = base_url.rstrip("/") + "/analyze"
    with doc_path.open("rb") as fh:
        files = {"file": (doc_path.name, fh, "application/octet-stream")}
        data = {"query_type": "qa", "user_query": question}
        start = time.perf_counter()
        resp = requests.post(url, data=data, files=files, timeout=120)
        elapsed_ms = (time.perf_counter() - start) * 1000
    if resp.status_code != 200:
        return "", elapsed_ms, f"http {resp.status_code}: {resp.text[:200]}"
    payload = resp.json()
    answer = payload.get("result") or payload.get("answer") or ""
    return str(answer), elapsed_ms, "ok"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Path to JSONL with doc_path/query/answers")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Backend base URL (default: %(default)s)")
    parser.add_argument("--repeats", type=int, default=1, help="Repeat each sample N times")
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    if not dataset_path.exists():
        print(f"Dataset not found: {dataset_path}", file=sys.stderr)
        sys.exit(1)

    samples = load_dataset(dataset_path)
    if not samples:
        print("Dataset empty", file=sys.stderr)
        sys.exit(1)

    RESULT_DIR.mkdir(parents=True, exist_ok=True)
    out_csv = RESULT_DIR / f"rag_eval_{int(time.time())}.csv"

    hw_info = {
        "platform": sys.platform,
        "cpu_count": os.cpu_count(),
    }

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "sample_id",
            "doc_path",
            "question",
            "gold_answers",
            "prediction",
            "f1",
            "latency_ms",
            "status",
            "hardware",
        ])

        for idx, item in enumerate(samples):
            doc_path = Path(item["doc_path"])
            question = item.get("query") or item.get("question") or ""
            gold_answers = item.get("answers") or []
            if not doc_path.exists():
                writer.writerow([idx, doc_path, question, gold_answers, "", 0.0, 0.0, "missing_file", hw_info])
                continue
            for _ in range(args.repeats):
                pred, latency_ms, status = post_qa(args.base_url, doc_path, question)
                f1 = f1_score(pred, gold_answers) if status == "ok" else 0.0
                writer.writerow([idx, doc_path, question, gold_answers, pred, f1, round(latency_ms, 2), status, hw_info])
                f.flush()

    print(f"Wrote results to {out_csv}")


if __name__ == "__main__":
    main()
