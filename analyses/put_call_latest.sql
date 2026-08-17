select
    snapshot_date,
    underlying_code,
    put_call_volume_ratio,
    put_call_oi_ratio,
    put_volume,
    call_volume
from {{ ref('mart_put_call_summary') }}
order by snapshot_date desc, underlying_code
limit 50
