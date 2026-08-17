-- One front-month row per underlying per session is the roll-monitor grain.
select
    underlying_code,
    market_date,
    count(*) as row_count
from {{ ref('mart_futures_nearby_roll') }}
group by 1, 2
having count(*) > 1
