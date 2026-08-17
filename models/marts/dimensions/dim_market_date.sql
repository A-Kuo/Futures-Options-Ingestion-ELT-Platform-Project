with dates as (
    select distinct market_date as calendar_date from {{ ref('stg_futures_prices') }}
    union
    select distinct snapshot_date as calendar_date from {{ ref('stg_options_chain') }}
)

select
    calendar_date as market_date,
    extract(year from calendar_date) as market_year,
    extract(month from calendar_date) as market_month,
    extract(quarter from calendar_date) as market_quarter,
    strftime(calendar_date, '%A') as weekday_name,
    extract(dow from calendar_date) in (0, 6) as is_weekend,
    calendar_date = (select max(calendar_date) from dates) as is_latest_session
from dates
