select
    underlying_code,
    market_date,
    contract_symbol,
    nearby_rank,
    days_to_expiry,
    volume,
    front_volume_share
from {{ ref('mart_futures_nearby_roll') }}
order by market_date desc, underlying_code
limit 50
