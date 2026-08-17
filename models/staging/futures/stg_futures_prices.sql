{{
    config(tags=["staging", "futures"])
}}

with source as (
    select * from {{ source('raw', 'futures_prices') }}
),

typed as (
    select
        {{ parse_flexible_date('trade_dt') }} as market_date,
        {{ normalize_symbol('globex_sym') }} as contract_symbol,
        {{ parse_flexible_number('px_open') }} as open_price,
        {{ parse_flexible_number('px_high') }} as high_price,
        {{ parse_flexible_number('px_low') }} as low_price,
        {{ parse_flexible_number('px_settle') }} as settlement_price,
        {{ parse_flexible_number('vol') }} as volume,
        {{ parse_flexible_number('oi') }} as open_interest,
        upper(trim(settle_flag)) as settle_status,
        trim(file_name) as source_file_name,
        try_cast(load_ts as timestamp) as loaded_at
    from source
),

deduped as (
    select
        *,
        row_number() over (
            partition by contract_symbol, market_date
            order by loaded_at desc nulls last
        ) as _dedupe_rank,
        count(*) over (
            partition by contract_symbol, market_date
        ) as source_duplicate_count
    from typed
    where market_date is not null
        and contract_symbol is not null
)

select
    {{ dbt_utils.generate_surrogate_key(['contract_symbol', 'market_date']) }} as futures_price_sk,
    market_date,
    contract_symbol,
    open_price,
    high_price,
    low_price,
    settlement_price,
    volume,
    open_interest,
    settle_status,
    source_file_name,
    loaded_at,
    source_duplicate_count
from deduped
where _dedupe_rank = 1
