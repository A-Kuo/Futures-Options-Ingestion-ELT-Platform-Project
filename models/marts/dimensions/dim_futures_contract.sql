select
    futures_contract_sk,
    contract_symbol,
    underlying_code,
    underlying_name,
    asset_class,
    exchange_code,
    month_code,
    contract_year,
    contract_month_number,
    contract_month_name,
    expiry_date,
    first_notice_date,
    settlement_type,
    contract_multiplier,
    tick_size,
    is_active
from {{ ref('int_futures_contracts_enriched') }}
