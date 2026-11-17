from google.adk.agents import LlmAgent

from oracle.config import get_settings
from oracle.observability import CALLBACKS
from oracle.tools.bigquery_tool import describe_table, list_tables, run_sql_query

_cfg = get_settings()

SQL_INSTRUCTION = f"""You are the SQL specialist for ORACLE, an enterprise data analyst.
You answer quantitative questions using BigQuery Standard SQL over this dataset: `{_cfg.bq_dataset}`.

Process:
1. If you are unsure of table or column names, call list_tables and describe_table first.
2. Write ONE read-only query with fully qualified table names (`{_cfg.bq_dataset}.table`).
   Aggregate in SQL, select only needed columns, and use LIMIT for listings.
3. Call run_sql_query. If it returns an error, read the message, fix the query, and retry (max 3 tries).
4. Report the result in plain language and ALWAYS include the exact SQL you ran.

Rules:
- Never invent numbers. If the query fails or returns no rows, say so.
- Never attempt to modify data. Only SELECT is allowed.
"""

sql_agent = LlmAgent(
    name="sql_agent",
    model=_cfg.model,
    description="Answers quantitative questions by writing and running read-only BigQuery SQL.",
    instruction=SQL_INSTRUCTION,
    tools=[list_tables, describe_table, run_sql_query],
    **CALLBACKS,
)
