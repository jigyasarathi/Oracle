import pytest

from oracle.tools.sql_guard import UnsafeSQLError, validate_sql


def test_allows_select():
    assert validate_sql("SELECT 1;") == "SELECT 1"


def test_allows_with_cte():
    assert validate_sql("WITH a AS (SELECT 1 x) SELECT x FROM a").startswith("WITH")


def test_allows_columns_that_contain_keywords():
    assert validate_sql("SELECT created_at, updated_at FROM t")


@pytest.mark.parametrize(
    "bad",
    [
        "DROP TABLE x",
        "DELETE FROM x WHERE 1=1",
        "SELECT 1; DROP TABLE x",
        "INSERT INTO x VALUES (1)",
        "SELECT * FROM x WHERE a = 1 -- ok\n; DELETE FROM x",
        "",
        "-- just a comment",
    ],
)
def test_rejects_unsafe(bad):
    with pytest.raises(UnsafeSQLError):
        validate_sql(bad)
