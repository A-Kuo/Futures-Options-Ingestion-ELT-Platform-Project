# Futures and Options ELT Analytics Platform

A warehouse-style ELT system for ingesting, standardizing, and publishing futures and options market data into validated analytics marts for reporting, monitoring, and derivatives analytics.

This project is intentionally focused on data engineering and analytics rather than market prediction. Its goal is to operationalize complex derivatives datasets into trustworthy reporting tables, documented transformations, and reusable warehouse models.

**Version 1 runs entirely locally** (Python + DuckDB + dbt Core + Streamlit). Nothing here writes to Snowflake, dbt Cloud, or a remote warehouse.

## Why this exists

Futures and options data are easy to download and hard to operationalize. They contain multiple entity levels — underlying, contract month, expiry, strike, side, and session — that create messy joins and inconsistent schemas. This repo builds a clean warehouse model for contract activity, expiry monitoring, and options-chain reporting.

It is **not** a trading strategy, price predictor, or implied-volatility forecasting engine.

## Stack

| Layer | Choice | Why |
| --- | --- | --- |
| Generate / land | Python | Repeatable synthetic extracts with realistic source dirtiness |
| Warehouse | DuckDB file `data/warehouse.duckdb` | Local, no cloud account |
| Transform | dbt Core + `dbt-duckdb` | Staging → intermediate → marts, tests, docs |
| Presentation | Streamlit | Pipeline quality, futures activity, options activity |

Python **3.12** is required (`py -3.12`). System Python 3.14 is not used.

## Project layout

```text
├── src/                    # generate + ingest into DuckDB raw schema
├── data/raw_samples/       # vendor-style CSVs (synthetic)
├── data/seeds/             # CME month-letter map
├── models/staging/
├── models/intermediate/
├── models/marts/           # dimensions, facts, futures/options/quality marts
├── snapshots/              # contract-master change tracking
├── tests/                  # singular data tests
├── analyses/
├── docs/                   # grain, source mapping, architecture
└── app/                    # Streamlit
```

## Grain (short version)

| Dataset | One row means | Key |
| --- | --- | --- |
| Futures prices | One contract on one session | `contract_symbol` + `market_date` |
| Options chain | One option series on one snapshot date | `option_contract_nk` + `snapshot_date` |
| Nearby roll mart | Front-month contract for one underlying on one session | `underlying_code` + `market_date` |

Full grain list: [docs/grain.md](docs/grain.md).

## Local setup

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.generate_raw
.\.venv\Scripts\python.exe -m src.ingest
.\.venv\Scripts\dbt.exe deps --profiles-dir .
.\.venv\Scripts\dbt.exe build --profiles-dir .
.\.venv\Scripts\streamlit.exe run app/streamlit_app.py
```

`profiles.yml` lives in the repo and points at `data/warehouse.duckdb`. dbt must be invoked with `--profiles-dir .`.

Generate lineage docs (still local):

```powershell
.\.venv\Scripts\dbt.exe docs generate --profiles-dir .
.\.venv\Scripts\dbt.exe docs serve --profiles-dir .
```

After the Streamlit app is running, save a few PNGs into `screenshots/` (pipeline quality, nearby roll, options heatmap) for the portfolio README.

## Analytics questions the marts answer

**Futures**

- Which contracts have the highest volume and open interest?
- How does activity shift toward the next expiry as the front month approaches last trade?
- What does the term structure look like across nearby contracts?
- Which contracts printed unusual volume or open-interest changes vs their recent baseline?

**Options**

- Where is volume and open interest clustered by strike and expiry?
- How do calls and puts compare on volume and open interest?
- Where are bid/ask spreads unusually wide (quote-quality monitor)?

**Cross-domain**

- How do options and futures activity line up on the same session?
- Which underlyings dominate listed activity in this warehouse?

## Data

Extracts are **synthetic but schema-realistic**: CME-style Globex symbols, month letters, third-Friday equity expiries, mixed vendor date formats, duplicate snapshot retries, and inconsistent call/put flags. Staging is where that dirtiness is removed.

Implied volatility and delta are copied from the extract as vendor-supplied demo fields. This project does not price options.

A visible operations example is built in: crude oil front-month volume on 2026-06-12 is spiked so `is_unusual_volume` has something to show.

## Tests

- Unique / not-null keys on staged contracts and facts
- Accepted month codes and call/put flags
- Non-negative prices, strikes, volume, and open interest
- Referential integrity to underlyings and contract dimensions
- Singular test: one front-month row per underlying per date
- Unit tests for nearby rank and put/call ratio math

## Resume framing

Built an end-to-end ELT platform for futures and options market data, standardizing raw contract and option-chain datasets into tested warehouse models and analytics marts for expiry, open-interest, and contract-activity reporting.

## Publishing this repo (you do the cloud/git remote steps)

This environment only writes local files. A safe publish sequence:

1. Review `git status` and `git diff`. Confirm no secrets (there should be none; warehouse files are gitignored).
2. `git add` the project files (not `.venv/` or `data/*.duckdb`).
3. Commit with a message such as: `Add local DuckDB ELT platform for futures and options marts`.
4. `git push` to your GitHub remote when you are ready.

I will not push from this workspace unless you explicitly ask.
