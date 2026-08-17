-- Option facts must not invent call/put values outside the C/P convention.
select
    call_put_flag,
    count(*) as row_count
from {{ ref('fct_options_chain_snapshots') }}
where call_put_flag not in ('C', 'P')
    or call_put_flag is null
group by 1
