select distinct
    {{ dbt_utils.generate_surrogate_key(['underlying_code', 'strike']) }} as strike_sk,
    underlying_code,
    strike
from {{ ref('int_options_contracts') }}
