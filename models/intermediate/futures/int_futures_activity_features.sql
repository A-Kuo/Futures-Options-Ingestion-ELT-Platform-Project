{{
    config(tags=["intermediate", "futures"])
}}

with ranked as (
    select * from {{ ref('int_futures_nearby_rank') }}
),

windowed as (
    select
        ranked.*,
        avg(volume) over (
            partition by contract_symbol
            order by market_date
            rows between 19 preceding and 1 preceding
        ) as volume_20d_avg,
        avg(open_interest) over (
            partition by contract_symbol
            order by market_date
            rows between 19 preceding and 1 preceding
        ) as open_interest_20d_avg,
        open_interest - lag(open_interest) over (
            partition by contract_symbol
            order by market_date
        ) as open_interest_change,
        volume - lag(volume) over (
            partition by contract_symbol
            order by market_date
        ) as volume_change
    from ranked
)

select
    *,
    case
        when volume_20d_avg is not null
            and volume_20d_avg > 0
            and volume >= volume_20d_avg * {{ var('unusual_volume_multiple') }}
            then true
        else false
    end as is_unusual_volume,
    case
        when open_interest_20d_avg is not null
            and open_interest_20d_avg > 0
            and abs(open_interest_change) >= open_interest_20d_avg * ({{ var('unusual_oi_multiple') }} - 1)
            then true
        else false
    end as is_unusual_open_interest
from windowed
