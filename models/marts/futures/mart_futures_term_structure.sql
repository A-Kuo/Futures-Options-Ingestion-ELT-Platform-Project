select
    market_date,
    underlying_code,
    nearby_rank,
    contract_symbol,
    expiry_date,
    days_to_expiry,
    settlement_price,
    volume,
    open_interest,
    settlement_price - first_value(settlement_price) over (
        partition by underlying_code, market_date
        order by nearby_rank
    ) as spread_vs_front
from {{ ref('int_futures_nearby_rank') }}
where nearby_rank <= 6
