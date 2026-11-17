"""Tiny vector store persisted as JSON.

Backends:
  tfidf       - offline, no cloud calls (default; good for dev and CI)
  embeddings  - Gemini embeddings + cosine similarity (needs model access)

Swap this module for Vertex AI Vector Search or pgvector when the corpus grows.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from oracle.config import get_settings
from oracle.rag.chunking import Chunk

_cache: dict[str, dict] = {}


def _embed(texts: list[str]) -> list[list[float]]:
    from google import genai

    client = genai.Client()
    model = get_settings().embedding_model
    vectors: list[list[float]] = []
    for i in range(0, len(texts), 50):
        resp = client.models.embed_content(model=model, contents=texts[i : i + 50])
        vectors.extend(list(e.values) for e in resp.embeddings)
    return vectors


def build_index(
    chunks: list[Chunk], index_path: Path | None = None, backend: str | None = None
) -> Path:
    cfg = get_settings()
    index_path = index_path or cfg.index_path
    backend = backend or cfg.retriever_backend
    payload = {
        "backend": backend,
        "chunks": [{"id": c.id, "source": c.source, "text": c.text} for c in chunks],
        "vectors": _embed([c.text for c in chunks]) if backend == "embeddings" else None,
    }
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(payload), encoding="utf-8")
    _cache.pop(str(index_path), None)
    return index_path


def _load(index_path: Path) -> dict:
    key = str(index_path)
    mtime = index_path.stat().st_mtime  # raises FileNotFoundError if missing
    cached = _cache.get(key)
    if cached and cached["mtime"] == mtime:
        return cached
    data = json.loads(index_path.read_text(encoding="utf-8"))
    texts = [c["text"] for c in data["chunks"]]
    if data["backend"] == "tfidf":
        from sklearn.feature_extraction.text import TfidfVectorizer

        vectorizer = TfidfVectorizer(stop_words="english")
        data["vectorizer"] = vectorizer
        data["matrix"] = vectorizer.fit_transform(texts)
    else:
        data["matrix"] = np.array(data["vectors"], dtype=float)
    data["mtime"] = mtime
    _cache[key] = data
    return data


def search(query: str, k: int = 4, index_path: Path | None = None) -> list[dict]:
    index_path = index_path or get_settings().index_path
    data = _load(index_path)
    if data["backend"] == "tfidf":
        from sklearn.metrics.pairwise import cosine_similarity

        scores = cosine_similarity(data["vectorizer"].transform([query]), data["matrix"])[0]
    else:
        q = np.array(_embed([query])[0], dtype=float)
        m = data["matrix"]
        scores = (m @ q) / (np.linalg.norm(m, axis=1) * np.linalg.norm(q) + 1e-9)
    top = np.argsort(scores)[::-1][:k]
    return [
        {
            "chunk_id": data["chunks"][i]["id"],
            "source": data["chunks"][i]["source"],
            "score": round(float(scores[i]), 4),
            "text": data["chunks"][i]["text"],
        }
        for i in top
        if scores[i] > 0
    ]
