"""Read-only SQL validation. Defence in depth: the service account should ALSO be read-only."""
from __future__ import annotations

import re

FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|create|alter|merge|truncate|grant|revoke|call|execute|export|load)\b",
    re.IGNORECASE,
)


class UnsafeSQLError(ValueError):
    pass


def validate_sql(sql: str) -> str:
    """Return cleaned SQL if it is a single read-only SELECT/WITH statement, else raise."""
    cleaned = (sql or "").strip().rstrip(";").strip()
    if not cleaned:
        raise UnsafeSQLError("Empty query.")
    if ";" in cleaned:
        raise UnsafeSQLError("Only a single statement is allowed.")
    no_comments = re.sub(r"--.*?$|/\*.*?\*/", "", cleaned, flags=re.DOTALL | re.MULTILINE).strip()
    if not no_comments:
        raise UnsafeSQLError("Query contains only comments.")
    first_word = no_comments.split(None, 1)[0].lower()
    if first_word not in {"select", "with"}:
        raise UnsafeSQLError("Only SELECT queries are allowed.")
    match = FORBIDDEN.search(no_comments)
    if match:
        raise UnsafeSQLError(f"Forbidden keyword: {match.group(0)}")
    return cleaned
