with daily as (
    select
        snapshot_date,
        underlying_code,
        sum(case when call_put_flag = 'C' then volume else 0 end) as call_volume,
        sum(case when call_put_flag = 'P' then volume else 0 end) as put_volume,
        sum(case when call_put_flag = 'C' then open_interest else 0 end) as call_open_interest,
        sum(case when call_put_flag = 'P' then open_interest else 0 end) as put_open_interest
    from {{ ref('fct_options_chain_snapshots') }}
    group by 1, 2
)

select
    snapshot_date,
    underlying_code,
    call_volume,
    put_volume,
    call_open_interest,
    put_open_interest,
    put_volume / nullif(call_volume, 0) as put_call_volume_ratio,
    put_open_interest / nullif(call_open_interest, 0) as put_call_oi_ratio
from daily
