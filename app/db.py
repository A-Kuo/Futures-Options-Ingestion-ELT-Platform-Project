from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.duckdb"


def connect() -> duckdb.DuckDBPyConnection:
    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Warehouse not found at {DB_PATH}. Run python -m src.ingest and dbt build --profiles-dir ."
        )
    return duckdb.connect(str(DB_PATH), read_only=True)


@lru_cache(maxsize=32)
def query(sql: str) -> pd.DataFrame:
    con = connect()
    try:
        return con.execute(sql).df()
    finally:
        con.close()


def table(name: str, schema: str = "marts") -> pd.DataFrame:
    return query(f"select * from {schema}.{name}")


def as_sql_date(value) -> str:
    return pd.Timestamp(value).date().isoformat()


def scalar(sql: str):
    df = query(sql)
    if df.empty:
        return None
    return df.iloc[0, 0]
