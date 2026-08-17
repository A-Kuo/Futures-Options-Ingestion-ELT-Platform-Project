{{
    config(tags=["staging", "reference"])
}}

with source as (
    select * from {{ ref('ref_contract_month_codes') }}
)

select
    upper(trim(month_code)) as month_code,
    cast(month_number as integer) as month_number,
    trim(month_name) as month_name
from source
