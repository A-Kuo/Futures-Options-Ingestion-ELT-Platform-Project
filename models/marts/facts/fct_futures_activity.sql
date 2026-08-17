select
    futures_nearby_sk as futures_activity_sk,
    market_date,
    contract_symbol,
    underlying_code,
    nearby_rank,
    days_to_expiry,
    is_roll_window,
    volume,
    open_interest,
    volume_change,
    open_interest_change,
    volume_20d_avg,
    open_interest_20d_avg,
    is_unusual_volume,
    is_unusual_open_interest
from {{ ref('int_futures_activity_features') }}
