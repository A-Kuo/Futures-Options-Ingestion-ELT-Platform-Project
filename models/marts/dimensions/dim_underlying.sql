select
    underlying_sk,
    underlying_code,
    underlying_name,
    asset_class,
    exchange_code,
    exchange_name,
    tick_size,
    tick_value,
    contract_multiplier,
    currency_code,
    quote_units,
    trading_session,
    product_group,
    is_listed
from {{ ref('stg_underlyings') }}
