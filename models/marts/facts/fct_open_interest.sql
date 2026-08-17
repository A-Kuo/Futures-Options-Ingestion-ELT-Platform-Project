with futures_oi as (
    select
        market_date as as_of_date,
        underlying_code,
        'futures' as instrument_type,
        contract_symbol as instrument_code,
        open_interest,
        volume
    from {{ ref('fct_futures_prices') }}
),

options_oi as (
    select
        snapshot_date as as_of_date,
        underlying_code,
        'options' as instrument_type,
        option_contract_nk as instrument_code,
        open_interest,
        volume
    from {{ ref('fct_options_chain_snapshots') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['as_of_date', 'instrument_type', 'instrument_code']) }} as open_interest_sk,
    *
from (
    select * from futures_oi
    union all
    select * from options_oi
) as combined
