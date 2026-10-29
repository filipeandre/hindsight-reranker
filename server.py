"""TEI-compatible reranker service (GET /info, POST /rerank, GET /health).

Serves cross-encoder/ms-marco-MiniLM-L-6-v2 on CPU. Scores are sigmoid(logit), same
as TEI, which the Hindsight server then uses as-is (identical to its local provider).
"""
import math, os, threading, time
import torch
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import CrossEncoder

MODEL = os.environ.get("RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
BATCH = int(os.environ.get("RERANKER_BATCH", "32"))
torch.set_num_threads(int(os.environ.get("RERANKER_THREADS", "6")))
model = CrossEncoder(MODEL, device="cpu", max_length=512)
model.predict([("warm", "up")] * 4)
lock = threading.Lock()  # one scoring job at a time so threads are not oversubscribed
app = FastAPI()


class Req(BaseModel):
    query: str
    texts: list[str]
    return_text: bool = False


@app.get("/info")
def info():
    return {"model_id": MODEL, "model_type": {"reranker": {}}}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/rerank")
def rerank(r: Req):
    if not r.texts:
        return []
    with lock:
        logits = model.predict([(r.query, t) for t in r.texts], batch_size=BATCH, show_progress_bar=False)
    out = [{"index": i, "score": 1.0 / (1.0 + math.exp(-float(v)))} for i, v in enumerate(logits)]
    out.sort(key=lambda x: x["score"], reverse=True)
    return out
