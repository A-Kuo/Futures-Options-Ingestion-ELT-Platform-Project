{{
    config(tags=["intermediate", "options"])
}}

with chain as (
    select * from {{ ref('stg_options_chain') }}
),

front_month as (
    select
        market_date,
        underlying_code,
        settlement_price as underlying_futures_price,
        contract_symbol as underlying_futures_symbol
    from {{ ref('int_futures_nearby_rank') }}
    where nearby_rank = 1
),

enriched as (
    select
        chain.*,
        front_month.underlying_futures_price,
        front_month.underlying_futures_symbol,
        datediff('day', chain.snapshot_date, chain.expiry_date) as days_to_expiry,
        chain.ask_price - chain.bid_price as bid_ask_spread,
        case
            when chain.bid_price is not null and chain.ask_price is not null
                then (chain.bid_price + chain.ask_price) / 2.0
            else chain.last_price
        end as mid_price,
        case
            when front_month.underlying_futures_price is null or front_month.underlying_futures_price = 0
                then null
            else (chain.strike - front_month.underlying_futures_price)
                / front_month.underlying_futures_price
        end as moneyness
    from chain
    left join front_month
        on chain.underlying_code = front_month.underlying_code
        and chain.snapshot_date = front_month.market_date
)

select
    *,
    case
        when moneyness is null then 'unknown'
        when abs(moneyness) <= 0.01 then 'atm'
        when abs(moneyness) <= 0.05 then 'near_atm'
        when moneyness < 0 then 'below_spot'
        else 'above_spot'
    end as moneyness_bucket,
    case
        when mid_price is null or mid_price = 0 or bid_ask_spread is null then null
        else bid_ask_spread / mid_price
    end as relative_spread
from enriched
