select
    market_date,
    underlying_code,
    contract_symbol,
    nearby_rank,
    volume,
    open_interest,
    volume_change,
    open_interest_change,
    volume_20d_avg,
    open_interest_20d_avg,
    is_unusual_volume,
    is_unusual_open_interest
from {{ ref('int_futures_activity_features') }}
where nearby_rank <= 3
