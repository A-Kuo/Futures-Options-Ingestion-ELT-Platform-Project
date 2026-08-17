select
    snapshot_date,
    option_contract_nk,
    underlying_code,
    expiry_date,
    days_to_expiry,
    strike,
    call_put_flag,
    volume,
    open_interest,
    bid_price,
    ask_price,
    bid_ask_spread,
    implied_volatility,
    underlying_futures_price,
    moneyness,
    moneyness_bucket
from {{ ref('fct_options_chain_snapshots') }}
