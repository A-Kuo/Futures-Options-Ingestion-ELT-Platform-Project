-- Parsed market dates must land in the synthetic extract window, not year 0008/0026 artifacts.
select
    market_date,
    count(*) as row_count
from {{ ref('stg_futures_prices') }}
where market_date < date '2026-01-01'
    or market_date > date '2027-12-31'
group by 1
