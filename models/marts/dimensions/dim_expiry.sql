with expiries as (
    select distinct
        expiry_date,
        underlying_code,
        'futures' as instrument_family
    from {{ ref('stg_futures_contracts') }}
    union
    select distinct
        expiry_date,
        underlying_code,
        'options' as instrument_family
    from {{ ref('int_options_contracts') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['expiry_date', 'underlying_code', 'instrument_family']) }} as expiry_sk,
    expiry_date,
    extract(year from expiry_date) as expiry_year,
    extract(month from expiry_date) as expiry_month,
    strftime(expiry_date, '%A') as expiry_weekday,
    underlying_code,
    instrument_family
from expiries
