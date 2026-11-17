"""BigQuery tools for the SQL agent: schema discovery + guarded read-only queries."""
from __future__ import annotations

import json
import re
from functools import lru_cache

from oracle.config import get_settings
from oracle.tools.sql_guard import UnsafeSQLError, validate_sql


@lru_cache
def _client():
    from google.cloud import bigquery

    return bigquery.Client(project=get_settings().bq_project)


def list_tables() -> dict:
    """List the tables available in the analytics dataset.

    Returns:
        A dict with status and a list of table names.
    """
    try:
        tables = [t.table_id for t in _client().list_tables(get_settings().bq_dataset)]
        return {"status": "ok", "dataset": get_settings().bq_dataset, "tables": tables}
    except Exception as exc:  # noqa: BLE001 - surface the error to the agent so it can recover
        return {"status": "error", "error": str(exc)}


def describe_table(table_name: str) -> dict:
    """Describe the columns of one table in the analytics dataset.

    Args:
        table_name: Table name only, without project or dataset (for example "orders").

    Returns:
        A dict with status and a list of columns (name, type, description).
    """
    if not re.fullmatch(r"[A-Za-z0-9_]+", table_name or ""):
        return {"status": "error", "error": "Invalid table name."}
    try:
        table = _client().get_table(f"{get_settings().bq_dataset}.{table_name}")
        columns = [
            {"name": f.name, "type": f.field_type, "description": f.description or ""}
            for f in table.schema
        ]
        return {"status": "ok", "table": table_name, "num_rows": table.num_rows, "columns": columns}
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}


def run_sql_query(query: str) -> dict:
    """Run a read-only BigQuery Standard SQL query and return up to a limited number of rows.

    Args:
        query: A single SELECT (or WITH ... SELECT) statement. Use fully qualified table names.

    Returns:
        A dict with status, rows, row_count, bytes_processed and the executed query,
        or status "error" with a message you can use to fix the query.
    """
    from google.cloud import bigquery

    cfg = get_settings()
    try:
        sql = validate_sql(query)
    except UnsafeSQLError as exc:
        return {"status": "error", "error": f"Query rejected: {exc}"}

    try:
        client = _client()
        dry = client.query(
            sql, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
        )
        if dry.total_bytes_processed > cfg.bq_max_bytes:
            gb = dry.total_bytes_processed / 1e9
            return {
                "status": "error",
                "error": f"Query would scan {gb:.2f} GB, above the {cfg.bq_max_bytes / 1e9:.2f} GB "
                "limit. Add filters, select fewer columns, or aggregate.",
            }
        job = client.query(
            sql, job_config=bigquery.QueryJobConfig(maximum_bytes_billed=cfg.bq_max_bytes)
        )
        rows = [dict(row) for row in job.result(max_results=cfg.bq_max_rows)]
        rows = json.loads(json.dumps(rows, default=str))
        return {
            "status": "ok",
            "query": sql,
            "row_count": len(rows),
            "rows": rows,
            "bytes_processed": job.total_bytes_processed,
        }
    except Exception as exc:  # noqa: BLE001
        return {"status": "error", "error": str(exc)}
