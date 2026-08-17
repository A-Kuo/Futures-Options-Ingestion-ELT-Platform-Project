{{
    config(tags=["staging", "futures"])
}}

with source as (
    select * from {{ source('raw', 'futures_contracts') }}
),

typed as (
    select
        trim(contract_pk) as source_contract_id,
        {{ normalize_symbol('globex') }} as source_globex_symbol,
        {{ normalize_symbol('product_code') }} as underlying_code,
        upper(trim(month_ltr)) as month_code,
        case
            when try_cast(trim(cast(yr as varchar)) as integer) between 0 and 99
                then 2000 + try_cast(trim(cast(yr as varchar)) as integer)
            else try_cast(trim(cast(yr as varchar)) as integer)
        end as contract_year,
        {{ parse_flexible_date('ltd') }} as expiry_date,
        {{ parse_flexible_date('fnd') }} as first_notice_date,
        lower(trim(settle_type)) as settlement_type,
        upper(trim(exch)) as exchange_code,
        {{ parse_flexible_number('multiplier') }} as contract_multiplier,
        {{ parse_flexible_number('tick') }} as tick_size,
        lower(trim(status)) in ('y', 'true', '1', 'active') as is_active,
        try_cast(last_updated as timestamp) as source_updated_at
    from source
),

joined as (
    select
        typed.*,
        month_codes.month_number as contract_month_number,
        month_codes.month_name as contract_month_name,
        typed.underlying_code
            || typed.month_code
            || right(cast(typed.contract_year as varchar), 2) as contract_symbol
    from typed
    left join {{ ref('stg_contract_month_codes') }} as month_codes
        on typed.month_code = month_codes.month_code
)

select
    {{ dbt_utils.generate_surrogate_key(['contract_symbol']) }} as futures_contract_sk,
    source_contract_id,
    contract_symbol,
    source_globex_symbol,
    underlying_code,
    month_code,
    contract_year,
    contract_month_number,
    contract_month_name,
    expiry_date,
    first_notice_date,
    settlement_type,
    exchange_code,
    contract_multiplier,
    tick_size,
    is_active,
    source_updated_at
from joined
where contract_symbol is not null
    and expiry_date is not null
    and underlying_code is not null
