select
    contracts.underlying_code,
    contracts.underlying_name,
    contracts.contract_symbol,
    contracts.expiry_date,
    contracts.contract_month_name,
    contracts.contract_year,
    datediff('day', date '{{ var("as_of_date") }}', contracts.expiry_date) as days_to_expiry_as_of,
    contracts.settlement_type,
    contracts.is_active,
    latest.volume as latest_volume,
    latest.open_interest as latest_open_interest,
    latest.nearby_rank as latest_nearby_rank
from {{ ref('dim_futures_contract') }} as contracts
left join {{ ref('int_futures_activity_features') }} as latest
    on contracts.contract_symbol = latest.contract_symbol
    and latest.market_date = date '{{ var("as_of_date") }}'
