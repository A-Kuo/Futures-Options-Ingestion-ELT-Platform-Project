# Source-to-warehouse mapping

Sample extracts are generated locally by `python -m src.generate_raw` and landed with `python -m src.ingest`. They follow CME-style conventions (Globex symbols, month letters, third-Friday equity expiries) but **are synthetic**. Do not use them for trading.

Refresh cadence in this repo is on-demand / batch. `loaded_at` on the price extract is `2026-08-17 06:40:00` to represent an overnight settlement load.

| Source file | DuckDB raw table | Dirty fields | Staging model | Target grain |
| --- | --- | --- | --- | --- |
| `data/raw_samples/raw_underlyings.csv` | `raw.underlyings` | padded product codes, mixed-case `exch` | `stg_underlyings` | one product |
| `data/raw_samples/raw_futures_contracts.csv` | `raw.futures_contracts` | `yr` as 26 vs 2026, `ltd` date formats, Globex spacing | `stg_futures_contracts` | one listed contract |
| `data/raw_samples/raw_futures_prices.csv` | `raw.futures_prices` | date formats, comma-formatted volume, duplicate retries | `stg_futures_prices` | contract + session |
| `data/raw_samples/raw_options_chain.csv` | `raw.options_chain` | `put_call` flags, mixed expiries, retry `snap_id` | `stg_options_chain` | option + snapshot |
| `data/seeds/ref_contract_month_codes.csv` | seed | clean reference | `stg_contract_month_codes` | month letter |

Implied volatility and delta on the options extract are **source-supplied demo fields**, not outputs of a pricing model.

Staging date parsing is explicit rather than `cast(... as date)`. Two-digit values such as `09/18/26` must use `%m/%d/%y`; DuckDB's `%Y` will otherwise accept them as year 0026 and drop still-listed contracts from nearby rank.
