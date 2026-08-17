"""Land vendor-style CSVs into a local DuckDB raw schema.

Raw tables keep source column names and types as varchar so staging can
demonstrate parsing, deduplication, and contract-symbol normalization.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw_samples"
DB_PATH = ROOT / "data" / "warehouse.duckdb"

TABLES = {
    "underlyings": "raw_underlyings.csv",
    "futures_contracts": "raw_futures_contracts.csv",
    "futures_prices": "raw_futures_prices.csv",
    "options_chain": "raw_options_chain.csv",
}


def _csv_path(name: str) -> Path:
    return RAW_DIR / TABLES[name]


def ingest(generate_if_missing: bool = True) -> Path:
    missing = [name for name, filename in TABLES.items() if not (RAW_DIR / filename).exists()]
    if missing:
        if not generate_if_missing:
            raise FileNotFoundError(f"Missing raw extracts: {missing}")
        from src.generate_raw import generate

        generate()

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    try:
        con.execute("create schema if not exists raw")
        for table_name, filename in TABLES.items():
            csv_path = (RAW_DIR / filename).as_posix()
            con.execute(
                f"""
                create or replace table raw.{table_name} as
                select *
                from read_csv(
                    '{csv_path}',
                    header = true,
                    all_varchar = true,
                    quote = '"',
                    escape = '"'
                )
                """
            )
            count = con.execute(f"select count(*) from raw.{table_name}").fetchone()[0]
            print(f"raw.{table_name}: {count:,} rows from {filename}")
    finally:
        con.close()
    return DB_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description="Load raw futures/options CSVs into local DuckDB")
    parser.add_argument("--no-generate", action="store_true", help="Fail if sample CSVs are missing")
    args = parser.parse_args()
    ingest(generate_if_missing=not args.no_generate)
    print(f"Wrote {DB_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
