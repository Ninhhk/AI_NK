# Benchmarks

This folder contains reproducible benchmark scripts for AI NVCB. Numbers are not hard-coded; they are measured at runtime.

## Scripts

- `rag_eval.py`: Measure RAG QA quality (token-level F1) and latency against a running backend (prefix `/api/documents`).
- `json_parse_eval.py`: Measure JSON parse success rate for slide generation (structured output) and latency.
- `hot_swap_eval.py`: Measure model set/get latency for slide generation service.
- `health_uptime_probe.py`: Probe health endpoints over time and record availability/latency.
- `image_size_eval.bat`: Build Docker image(s) and record image size and build time (Windows batch).

## Test data expectations

- RAG: JSONL file; each line: `{ "doc_path": "path/to/file.txt", "query": "...", "answers": ["gold1", "gold2"] }`. Files can be any format accepted by the API (txt/pdf/docx). The dataset can remain private; the script only needs paths.
- JSON parse: JSONL file; each line: `{ "topic": "...", "num_slides": 8 }`.

## How to run

All scripts assume the FastAPI backend is running (default `http://localhost:8000/api`). Adjust `--base-url` as needed.

```bash
# RAG QA F1 + latency (document API lives under /api/documents)
python benchmarks/rag_eval.py --dataset data/rag_eval.jsonl --base-url http://localhost:8000/api/documents --repeats 1

# Structured JSON parse rate for slides
a python benchmarks/json_parse_eval.py --dataset data/topics.jsonl --base-url http://localhost:8000/api --runs 30

# Hot-swap latency for slide model
a python benchmarks/hot_swap_eval.py --base-url http://localhost:8000/api --models qwen3:8b llama3.1:8b --runs 10

# Health probe for 5 minutes (3s interval)
a python benchmarks/health_uptime_probe.py --base-url http://localhost:8000/api --duration-sec 300 --interval-sec 3

# Build image and record size/time (Windows)
benchmarks/image_size_eval.bat
```

Outputs are written to `benchmarks/results/*.csv` and `benchmarks/results/*.log` with timestamps and hardware metadata (CPU, RAM, platform).
