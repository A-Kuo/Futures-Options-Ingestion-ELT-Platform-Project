select
    options_contract_sk,
    option_contract_nk,
    underlying_code,
    expiry_date,
    strike,
    call_put_flag,
    option_root,
    exchange_code,
    case call_put_flag
        when 'C' then 'Call'
        when 'P' then 'Put'
    end as call_put_label
from {{ ref('int_options_contracts') }}
