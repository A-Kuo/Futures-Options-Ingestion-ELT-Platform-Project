{{
    config(tags=["staging", "options"])
}}

with source as (
    select * from {{ source('raw', 'options_chain') }}
),

typed as (
    select
        {{ parse_flexible_date('as_of') }} as snapshot_date,
        {{ normalize_symbol('und') }} as underlying_code,
        {{ parse_flexible_date('exp_dt') }} as expiry_date,
        {{ parse_flexible_number('strike_px') }} as strike,
        {{ standardize_call_put('put_call') }} as call_put_flag,
        {{ parse_flexible_number('bid_px') }} as bid_price,
        {{ parse_flexible_number('ask_px') }} as ask_price,
        {{ parse_flexible_number('last_px') }} as last_price,
        {{ parse_flexible_number('trd_vol') }} as volume,
        {{ parse_flexible_number('oi') }} as open_interest,
        {{ parse_flexible_number('imp_vol') }} as implied_volatility,
        {{ parse_flexible_number('delta') }} as delta,
        {{ normalize_symbol('opt_root') }} as option_root,
        upper(trim(exch)) as exchange_code,
        trim(snap_id) as snapshot_id,
        trim(rec_hash) as source_record_hash
    from source
),

keyed as (
    select
        *,
        underlying_code
            || '_'
            || strftime(expiry_date, '%Y%m%d')
            || '_'
            || replace(cast(strike as varchar), '.', 'p')
            || '_'
            || call_put_flag as option_contract_nk
    from typed
    where snapshot_date is not null
        and underlying_code is not null
        and expiry_date is not null
        and strike is not null
        and call_put_flag is not null
),

deduped as (
    select
        *,
        row_number() over (
            partition by option_contract_nk, snapshot_date
            order by snapshot_id desc
        ) as _dedupe_rank,
        count(*) over (
            partition by option_contract_nk, snapshot_date
        ) as source_duplicate_count
    from keyed
)

select
    {{ dbt_utils.generate_surrogate_key(['option_contract_nk', 'snapshot_date']) }} as options_chain_sk,
    snapshot_date,
    option_contract_nk,
    underlying_code,
    expiry_date,
    strike,
    call_put_flag,
    bid_price,
    ask_price,
    last_price,
    volume,
    open_interest,
    implied_volatility,
    delta,
    option_root,
    exchange_code,
    snapshot_id,
    source_record_hash,
    source_duplicate_count
from deduped
where _dedupe_rank = 1
