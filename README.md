# ORACLE: multi-agent enterprise data analyst on Google Cloud

Ask a business question in plain language. ORACLE routes it to a **SQL agent** (BigQuery) and/or a **document RAG agent**,
then a **critic agent** checks the draft for unsupported claims and assigns a confidence level.

**Status: baseline scaffold.** Everything here is a starting point you extend. See "Roadmap".

## Stack
Python 3.10+ | Google ADK (multi-agent) | Gemini (Vertex AI or Gemini API) | BigQuery | FastAPI | Cloud Run | Terraform

## Project layout
```
src/oracle/
  agents/        sql_agent, doc_agent, pipeline (analyst -> critic)
  tools/         BigQuery tools + SQL safety guard + document retrieval tool
  rag/           chunking + small vector store (TF-IDF or Gemini embeddings)
  observability  tokens, tool calls, tokens/sec, cost per request
  service.py     runs a question through the pipeline
  api.py         FastAPI app (POST /ask)
adk_agents/      entrypoint for the ADK dev UI (adk web)
data/docs/       sample (synthetic) policy documents
evals/           golden question set + eval runner
infra/terraform  Cloud Run, service account, IAM, Artifact Registry
docs/            architecture, discovery template
FEEDBACK.md      product feedback log
```

## Quick start (local)
1. Create a virtual environment and install:
   ```bash
   python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
   make install            # or: pip install -e ".[dev]"
   ```
2. Configure:
   ```bash
   cp .env.example .env    # Windows: copy .env.example .env
   ```
   - **Models:** set `GOOGLE_API_KEY` (from Google AI Studio), or use Vertex AI by setting
     `GOOGLE_GENAI_USE_VERTEXAI=TRUE`, `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`.
   - **BigQuery:** run `gcloud auth application-default login` and set `BQ_PROJECT` to a project you can bill queries to.
     The default dataset is the public `bigquery-public-data.thelook_ecommerce`.
3. Build the document index (offline, no cloud calls): `make ingest`
4. Run the tests (no cloud needed): `make test`
5. Ask a question:
   ```bash
   python scripts/ask.py "What is the return window, and how many items have status Returned?"
   ```
6. Run the API: `make run`, then
   ```bash
   curl -X POST localhost:8080/ask -H "Content-Type: application/json" \
     -d '{"question": "Which 3 countries have the most users?"}'
   ```
7. Optional ADK dev UI with traces: `make adk`

## Evals
`make eval` runs `evals/golden_set.jsonl` and reports routing accuracy, content accuracy, p50/p95 latency and cost.
Set `PRICE_PER_1M_INPUT` and `PRICE_PER_1M_OUTPUT` in `.env` from the current Google Cloud pricing page to get real cost numbers.
Grow the set to 50 to 100 questions and keep a results table in this README.

## Deploy to Cloud Run
```bash
cd infra/terraform
terraform init && terraform apply -var="project_id=YOUR_PROJECT"
cd ../..
gcloud builds submit --tag REGION-docker.pkg.dev/YOUR_PROJECT/oracle/oracle:latest
terraform -chdir=infra/terraform apply -var="project_id=YOUR_PROJECT" \
  -var="image=REGION-docker.pkg.dev/YOUR_PROJECT/oracle/oracle:latest"
```
The service is private by default. Grant `roles/run.invoker` to the callers you want. The Terraform has not been
validated against your project, so run `terraform plan` and read it before applying.

## Safety defaults
- SQL: single SELECT/WITH only, dry-run before every query, `maximum_bytes_billed` cap, row limit.
- Runtime service account is read-only. Never give it write roles.
- Docs agent answers only from retrieved text and must cite sources.

## Roadmap (suggested build order)
1. Baseline works end to end on the sample data. Record eval numbers. **Do this first.**
2. Replace sample docs with a real corpus (PDFs via Document AI or Gemini extraction) and add a data-quality check before indexing.
3. Swap the JSON store for Vertex AI Vector Search or pgvector; add reranking and hybrid search.
4. Give the critic a retrieval tool so it can re-verify claims; add a retry loop.
5. Ablations: Gemini Flash vs Pro, with vs without critic, with vs without reranking. Put the table here.
6. Tracing with OpenTelemetry / Cloud Trace; persistent sessions.
7. Fill in `docs/discovery.md` and `FEEDBACK.md`.

## Notes
- Built against `google-adk>=1.0.0`. ADK evolves quickly; if an import or signature fails after an upgrade, check the ADK release notes.
- Sample documents are synthetic.
