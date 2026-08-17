select
    snapshot_date,
    underlying_code,
    expiry_date,
    strike,
    moneyness_bucket,
    sum(case when call_put_flag = 'C' then volume else 0 end) as call_volume,
    sum(case when call_put_flag = 'P' then volume else 0 end) as put_volume,
    sum(volume) as total_volume,
    sum(case when call_put_flag = 'C' then open_interest else 0 end) as call_open_interest,
    sum(case when call_put_flag = 'P' then open_interest else 0 end) as put_open_interest,
    sum(open_interest) as total_open_interest
from {{ ref('fct_options_chain_snapshots') }}
group by 1, 2, 3, 4, 5
