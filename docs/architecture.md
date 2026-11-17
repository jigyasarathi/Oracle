# ORACLE architecture

```mermaid
flowchart TD
    U[User / API client] --> API[FastAPI on Cloud Run]
    API --> P[SequentialAgent: oracle]
    P --> A[analyst agent - router]
    A -->|AgentTool| S[sql_agent]
    A -->|AgentTool| D[doc_agent]
    S --> BQ[(BigQuery - read-only, dry-run cost cap)]
    D --> V[(Vector index - TF-IDF or embeddings)]
    A --> C[critic agent - self-reflection]
    C --> API
    API --> M[Metrics: tokens, latency, tokens/sec, cost]
```

## Design decisions
- **Hierarchical delegation:** the analyst treats specialists as tools, so each has a narrow prompt and toolset.
- **Safety:** SQL is validated (single SELECT only), dry-run for cost, `maximum_bytes_billed` enforced, and the runtime service account is read-only.
- **Grounding:** the doc agent may only answer from retrieved passages and must cite chunk IDs; the critic rejects unsupported claims.
- **Observability:** ADK callbacks record tokens and tool calls per request.

## Known limitations (be honest about these in interviews)
- The critic checks the draft's internal consistency; it does not re-run retrieval yet (next step: give it search_documents).
- Retrieval is TF-IDF by default; the embeddings backend is a simple in-memory index.
- Sessions are in memory only; use a database-backed session service for production.
