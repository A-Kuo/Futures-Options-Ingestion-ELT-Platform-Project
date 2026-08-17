select
    options_chain_sk as options_activity_sk,
    snapshot_date,
    option_contract_nk,
    underlying_code,
    expiry_date,
    strike,
    call_put_flag,
    volume,
    open_interest,
    bid_ask_spread,
    relative_spread,
    moneyness_bucket
from {{ ref('int_options_chain_enriched') }}
