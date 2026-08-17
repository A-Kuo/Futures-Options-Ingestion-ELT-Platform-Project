select
    activity.futures_price_sk,
    activity.market_date,
    activity.contract_symbol,
    activity.underlying_code,
    activity.settlement_price,
    activity.open_price,
    activity.high_price,
    activity.low_price,
    activity.volume,
    activity.open_interest
from {{ ref('int_futures_activity_features') }} as activity
