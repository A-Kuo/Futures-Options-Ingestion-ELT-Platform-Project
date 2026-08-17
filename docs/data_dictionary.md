# Data dictionary

Column-level descriptions live in dbt YAML and are the source of truth after `dbt docs generate`. This page lists reporting metrics that are easy to misuse.

| Metric | Definition | Do not read as |
| --- | --- | --- |
| `nearby_rank` | Rank of still-live contracts by expiry for an underlying on a market date. 1 = front month. | A roll *instruction* or trading signal |
| `days_to_expiry` | Calendar days from session date to contract `expiry_date` | Business-day DTE |
| `front_volume_share` | Front-month volume / (front + second nearby volume) | Probability the market will roll |
| `is_unusual_volume` | Session volume >= 2.5x trailing 20-session average | News detection or alpha |
| `put_call_volume_ratio` | Put volume / call volume for an underlying on a snapshot date | Sentiment forecast |
| `moneyness` | `(strike - front futures price) / front futures price` | Option value or implied-vol surface fit |
| `implied_volatility` | Copied from the source extract | A volatility we computed |
| `delta` | Copied from the source extract | A Greek we computed |

Synthetic data notes:

- Equity index futures expiries use a third-Friday convention.
- Crude oil is generated in backwardation; equity index futures in mild contango.
- 2026-06-12 CL front-month volume is intentionally spiked so the unusual-activity monitor has a visible example.
