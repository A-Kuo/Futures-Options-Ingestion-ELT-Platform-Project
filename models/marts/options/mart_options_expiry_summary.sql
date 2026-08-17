select
    snapshot_date,
    underlying_code,
    expiry_date,
    days_to_expiry,
    count(distinct strike) as strike_count,
    sum(volume) as total_volume,
    sum(open_interest) as total_open_interest,
    sum(case when call_put_flag = 'C' then volume else 0 end) as call_volume,
    sum(case when call_put_flag = 'P' then volume else 0 end) as put_volume,
    avg(relative_spread) as avg_relative_spread
from {{ ref('fct_options_chain_snapshots') }}
group by 1, 2, 3, 4
