# Grain definitions

This warehouse is useful because futures and options data sit at **different grains**. Every model states its grain in YAML; this page is the canonical list.

This project does **not** predict prices, implied volatility, or trading signals. It operationalizes messy derivatives extracts into tested reporting tables.

## Entity levels

| Entity | What one row means | Business key |
| --- | --- | --- |
| Underlying | One listed product root | `underlying_code` (ES, NQ, CL, GC, ZB) |
| Futures contract | One expiry of a futures product | `contract_symbol` (ESZ26) |
| Options contract | One strike / expiry / side | `option_contract_nk` (`ES_20260918_5800_C`) |
| Market date | One trading session | `market_date` |
| Option snapshot | One chain capture for a session | `snapshot_date` + option contract |

## Source extracts

| Raw table | Intended grain | Known source issues |
| --- | --- | --- |
| `raw.underlyings` | One product | Padded codes, mixed-case exchange labels |
| `raw.futures_contracts` | One listed contract | Two-digit years, mixed expiry formats, messy Globex symbols |
| `raw.futures_prices` | Contract + trade date | Duplicate settlement-file retries, commas in numbers |
| `raw.options_chain` | Option + snapshot date | `Call`/`P `/`put` flags, retry snapshot IDs |

## Staging

| Model | Grain | Primary key |
| --- | --- | --- |
| `stg_underlyings` | Product | `underlying_code` |
| `stg_futures_contracts` | Listed futures contract | `contract_symbol` |
| `stg_futures_prices` | Contract + session | `futures_price_sk` |
| `stg_options_chain` | Option + snapshot date | `options_chain_sk` |

## Intermediate

| Model | Grain | Why it exists |
| --- | --- | --- |
| `int_futures_nearby_rank` | Live contract + session | Nearby rank and days-to-expiry |
| `int_futures_activity_features` | Same | Trailing volume/OI and unusual-activity flags |
| `int_options_contracts` | Option series | Contract dimension without quote history |
| `int_options_chain_enriched` | Option + snapshot | Moneyness vs front-month futures, bid/ask width |

## Facts and marts

| Model | Grain |
| --- | --- |
| `fct_futures_prices` | Contract + market date |
| `fct_futures_activity` | Contract + market date, live contracts only |
| `fct_options_chain_snapshots` | Option + snapshot date |
| `fct_open_interest` | Instrument + date across futures and options |
| `mart_futures_nearby_roll` | Underlying + market date (front month) |
| `mart_futures_term_structure` | Underlying + date + nearby rank (ranks 1-6) |
| `mart_put_call_summary` | Underlying + snapshot date |
| `mart_options_open_interest_by_strike` | Underlying + snapshot + expiry + strike |
