# hindsight-reranker

A small TEI-compatible reranker service for a Hindsight API server. It serves a cross-encoder
(`cross-encoder/ms-marco-MiniLM-L-6-v2` by default) on CPU over HTTP, so reranking can run on a
machine with more cores than the server hosting Hindsight.

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Liveness check, returns `{"status":"ok"}` |
| GET | `/info` | Returns `{"model_id": ...}`, used by the Hindsight TEI client at startup |
| POST | `/rerank` | Body `{"query": str, "texts": [str], "return_text": false}`. Returns `[{"index": int, "score": float}]` sorted by score descending |

Scores are `sigmoid(logit)`, the same scale the TEI server returns and the same ordering Hindsight's
local provider produces after its own normalisation, so a `min_scores` reranker floor behaves identically.

## Setup (Windows)

```powershell
uv venv --python 3.12 .venv
uv pip install --python .venv\Scripts\python.exe -r requirements.txt
.\run.cmd                  # foreground test; first run downloads the model
.\install-task.ps1         # elevated: start at boot, restart on failure
```

Environment variables (all optional): `RERANKER_PORT` (8787), `RERANKER_MODEL`, `RERANKER_THREADS` (6), `RERANKER_BATCH` (32).

## Hindsight server settings

```
HINDSIGHT_API_RERANKER_PROVIDER=tei
HINDSIGHT_API_RERANKER_TEI_URL=http://<host>:<port>
HINDSIGHT_API_RERANKER_TEI_BATCH_SIZE=300
HINDSIGHT_API_RERANKER_TEI_HTTP_TIMEOUT=10
# local failover if this service is unreachable
HINDSIGHT_API_RERANKER_1_PROVIDER=local
```

When running Hindsight in Docker Compose, each variable must be passed through as a bare list entry
(`- HINDSIGHT_API_RERANKER_...`), not `VAR=${VAR:-}`, or an empty value can break startup.

## Security

There is no authentication. Bind it to a trusted network and restrict the inbound firewall rule to the
Hindsight server's address only.

## Operations

- Health: `curl http://127.0.0.1:8787/health`
- Log: `service.log` in this folder
- Stop: stop the scheduled task and end the python process listening on the port
