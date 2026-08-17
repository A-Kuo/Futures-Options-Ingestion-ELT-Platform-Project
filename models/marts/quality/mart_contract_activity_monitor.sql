with futures as (
    select
        market_date as as_of_date,
        underlying_code,
        sum(volume) as futures_volume,
        sum(open_interest) as futures_open_interest
    from {{ ref('fct_futures_activity') }}
    where nearby_rank <= 2
    group by 1, 2
),

options as (
    select
        snapshot_date as as_of_date,
        underlying_code,
        sum(volume) as options_volume,
        sum(open_interest) as options_open_interest
    from {{ ref('fct_options_activity') }}
    group by 1, 2
)

select
    coalesce(futures.as_of_date, options.as_of_date) as as_of_date,
    coalesce(futures.underlying_code, options.underlying_code) as underlying_code,
    futures.futures_volume,
    futures.futures_open_interest,
    options.options_volume,
    options.options_open_interest,
    options.options_volume / nullif(futures.futures_volume, 0) as options_to_futures_volume
from futures
full outer join options
    on futures.as_of_date = options.as_of_date
    and futures.underlying_code = options.underlying_code
