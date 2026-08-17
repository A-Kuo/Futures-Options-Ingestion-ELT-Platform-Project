with source_counts as (
    select 'raw.underlyings' as object_name, count(*) as row_count from {{ source('raw', 'underlyings') }}
    union all
    select 'raw.futures_contracts', count(*) from {{ source('raw', 'futures_contracts') }}
    union all
    select 'raw.futures_prices', count(*) from {{ source('raw', 'futures_prices') }}
    union all
    select 'raw.options_chain', count(*) from {{ source('raw', 'options_chain') }}
),

model_counts as (
    select 'stg_underlyings' as object_name, count(*) as row_count from {{ ref('stg_underlyings') }}
    union all
    select 'stg_futures_contracts', count(*) from {{ ref('stg_futures_contracts') }}
    union all
    select 'stg_futures_prices', count(*) from {{ ref('stg_futures_prices') }}
    union all
    select 'stg_options_chain', count(*) from {{ ref('stg_options_chain') }}
    union all
    select 'fct_futures_prices', count(*) from {{ ref('fct_futures_prices') }}
    union all
    select 'fct_options_chain_snapshots', count(*) from {{ ref('fct_options_chain_snapshots') }}
),

coverage as (
    select
        'futures' as domain,
        underlying_code,
        min(market_date) as min_date,
        max(market_date) as max_date,
        count(*) as row_count
    from {{ ref('fct_futures_prices') }}
    group by 1, 2
    union all
    select
        'options' as domain,
        underlying_code,
        min(snapshot_date) as min_date,
        max(snapshot_date) as max_date,
        count(*) as row_count
    from {{ ref('fct_options_chain_snapshots') }}
    group by 1, 2
)

select
    'source_row_count' as metric_group,
    object_name as metric_name,
    cast(row_count as varchar) as metric_value,
    cast(null as varchar) as extra_1,
    cast(null as varchar) as extra_2
from source_counts
union all
select
    'model_row_count',
    object_name,
    cast(row_count as varchar),
    null,
    null
from model_counts
union all
select
    'coverage',
    domain || ':' || underlying_code,
    cast(row_count as varchar),
    cast(min_date as varchar),
    cast(max_date as varchar)
from coverage
