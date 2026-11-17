from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    model: str
    critic_model: str
    bq_project: str | None
    bq_dataset: str
    bq_max_bytes: int
    bq_max_rows: int
    retriever_backend: str
    embedding_model: str
    docs_dir: Path
    index_path: Path
    top_k: int
    price_per_1m_input: float
    price_per_1m_output: float


@lru_cache
def get_settings() -> Settings:
    return Settings(
        model=os.getenv("ORACLE_MODEL", "gemini-2.5-flash"),
        critic_model=os.getenv("ORACLE_CRITIC_MODEL", "gemini-2.5-flash"),
        bq_project=os.getenv("BQ_PROJECT") or None,
        bq_dataset=os.getenv("BQ_DATASET", "bigquery-public-data.thelook_ecommerce"),
        bq_max_bytes=int(os.getenv("BQ_MAX_BYTES", "1000000000")),
        bq_max_rows=int(os.getenv("BQ_MAX_ROWS", "50")),
        retriever_backend=os.getenv("RETRIEVER_BACKEND", "tfidf"),
        embedding_model=os.getenv("EMBEDDING_MODEL", "gemini-embedding-001"),
        docs_dir=Path(os.getenv("DOCS_DIR", "data/docs")),
        index_path=Path(os.getenv("INDEX_PATH", "data/index/index.json")),
        top_k=int(os.getenv("RETRIEVAL_TOP_K", "4")),
        price_per_1m_input=float(os.getenv("PRICE_PER_1M_INPUT", "0")),
        price_per_1m_output=float(os.getenv("PRICE_PER_1M_OUTPUT", "0")),
    )
