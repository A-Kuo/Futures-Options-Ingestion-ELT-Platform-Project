select distinct
    {{ dbt_utils.generate_surrogate_key(['exchange_code']) }} as exchange_sk,
    exchange_code,
    exchange_name
from {{ ref('stg_underlyings') }}
