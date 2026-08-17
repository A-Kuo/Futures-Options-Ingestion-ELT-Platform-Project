{{
    config(tags=["staging", "shared"])
}}

with source as (
    select * from {{ source('raw', 'underlyings') }}
),

cleaned as (
    select
        {{ normalize_symbol('product_code') }} as underlying_code,
        trim(product_desc) as underlying_name,
        trim(asset_class) as asset_class,
        upper(trim(exch)) as exchange_code,
        trim(exch_full) as exchange_name,
        {{ parse_flexible_number('min_tick') }} as tick_size,
        {{ parse_flexible_number('tick_val') }} as tick_value,
        {{ parse_flexible_number('multiplier') }} as contract_multiplier,
        upper(trim(ccy)) as currency_code,
        trim(uom) as quote_units,
        trim(session) as trading_session,
        trim(group_name) as product_group,
        lower(trim(listed_status)) in ('y', 'true', '1', 'active') as is_listed,
        lower(trim(src_system)) as source_system
    from source
)

select
    {{ dbt_utils.generate_surrogate_key(['underlying_code']) }} as underlying_sk,
    *
from cleaned
where underlying_code is not null
