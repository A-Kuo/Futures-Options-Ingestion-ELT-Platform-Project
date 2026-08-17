{{
    config(tags=["intermediate", "options"])
}}

select distinct
    {{ dbt_utils.generate_surrogate_key(['option_contract_nk']) }} as options_contract_sk,
    option_contract_nk,
    underlying_code,
    expiry_date,
    strike,
    call_put_flag,
    option_root,
    exchange_code
from {{ ref('stg_options_chain') }}
