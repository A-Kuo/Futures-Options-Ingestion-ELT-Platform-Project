select
    activity.market_date,
    activity.underlying_code,
    contracts.underlying_name,
    activity.contract_symbol,
    activity.nearby_rank,
    activity.days_to_expiry,
    activity.is_roll_window,
    activity.settlement_price,
    activity.volume,
    activity.open_interest,
    activity.volume_20d_avg,
    activity.open_interest_change,
    case
        when lead_contract.volume is null or activity.volume + lead_contract.volume = 0 then null
        else activity.volume / (activity.volume + lead_contract.volume)
    end as front_volume_share,
    case
        when lead_contract.open_interest is null or activity.open_interest + lead_contract.open_interest = 0 then null
        else activity.open_interest / (activity.open_interest + lead_contract.open_interest)
    end as front_oi_share,
    lead_contract.contract_symbol as next_contract_symbol,
    lead_contract.volume as next_contract_volume,
    lead_contract.open_interest as next_contract_open_interest
from {{ ref('int_futures_activity_features') }} as activity
inner join {{ ref('dim_futures_contract') }} as contracts
    on activity.contract_symbol = contracts.contract_symbol
left join {{ ref('int_futures_activity_features') }} as lead_contract
    on activity.underlying_code = lead_contract.underlying_code
    and activity.market_date = lead_contract.market_date
    and lead_contract.nearby_rank = 2
where activity.nearby_rank = 1
