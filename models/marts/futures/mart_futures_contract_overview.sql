with latest as (
    select *
    from {{ ref('int_futures_activity_features') }}
    where market_date = date '{{ var("as_of_date") }}'
)

select
    contracts.underlying_code,
    contracts.underlying_name,
    contracts.asset_class,
    contracts.exchange_code,
    contracts.contract_symbol,
    contracts.expiry_date,
    latest.nearby_rank,
    latest.days_to_expiry,
    latest.settlement_price,
    latest.volume,
    latest.open_interest,
    latest.is_unusual_volume,
    latest.is_unusual_open_interest,
    latest.is_roll_window
from {{ ref('dim_futures_contract') }} as contracts
left join latest
    on contracts.contract_symbol = latest.contract_symbol
