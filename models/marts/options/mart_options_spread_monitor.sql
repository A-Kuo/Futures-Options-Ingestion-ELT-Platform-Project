select
    snapshot_date,
    underlying_code,
    option_contract_nk,
    expiry_date,
    strike,
    call_put_flag,
    bid_price,
    ask_price,
    bid_ask_spread,
    relative_spread,
    volume,
    moneyness_bucket
from {{ ref('fct_options_chain_snapshots') }}
where bid_ask_spread is not null
