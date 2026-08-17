{{
    config(tags=["intermediate", "futures"])
}}

with live_contracts as (
    select
        prices.futures_price_sk,
        prices.market_date,
        prices.contract_symbol,
        contracts.underlying_code,
        contracts.underlying_name,
        contracts.asset_class,
        contracts.exchange_code,
        contracts.expiry_date,
        contracts.month_code,
        contracts.contract_year,
        datediff('day', prices.market_date, contracts.expiry_date) as days_to_expiry,
        prices.open_price,
        prices.high_price,
        prices.low_price,
        prices.settlement_price,
        prices.volume,
        prices.open_interest,
        prices.source_duplicate_count
    from {{ ref('stg_futures_prices') }} as prices
    inner join {{ ref('int_futures_contracts_enriched') }} as contracts
        on prices.contract_symbol = contracts.contract_symbol
    where contracts.expiry_date >= prices.market_date
)

select
    {{ dbt_utils.generate_surrogate_key(['contract_symbol', 'market_date']) }} as futures_nearby_sk,
    *,
    row_number() over (
        partition by underlying_code, market_date
        order by expiry_date, contract_symbol
    ) as nearby_rank,
    days_to_expiry <= {{ var('roll_watch_dte') }} as is_roll_window
from live_contracts
