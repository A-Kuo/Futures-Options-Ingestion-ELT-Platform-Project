{{
    config(tags=["intermediate", "futures"])
}}

select
    contracts.futures_contract_sk,
    contracts.contract_symbol,
    contracts.underlying_code,
    underlyings.underlying_name,
    underlyings.asset_class,
    underlyings.exchange_code,
    underlyings.exchange_name,
    contracts.month_code,
    contracts.contract_year,
    contracts.contract_month_number,
    contracts.contract_month_name,
    contracts.expiry_date,
    contracts.first_notice_date,
    contracts.settlement_type,
    contracts.contract_multiplier,
    contracts.tick_size,
    contracts.is_active
from {{ ref('stg_futures_contracts') }} as contracts
inner join {{ ref('stg_underlyings') }} as underlyings
    on contracts.underlying_code = underlyings.underlying_code
