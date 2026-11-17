FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .
COPY data ./data
COPY scripts ./scripts
# Builds the local TF-IDF index. For the embeddings backend, build the index
# at deploy time instead (needs credentials).
RUN python scripts/ingest_docs.py
ENV PORT=8080
CMD exec uvicorn oracle.api:app --host 0.0.0.0 --port ${PORT}
