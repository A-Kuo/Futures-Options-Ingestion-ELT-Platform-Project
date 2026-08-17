{% snapshot snap_futures_contracts %}

{{
    config(
      unique_key='contract_symbol',
      strategy='check',
      check_cols=['tick_size', 'contract_multiplier', 'is_active', 'expiry_date', 'settlement_type'],
      invalidate_hard_deletes=true
    )
}}

select
    contract_symbol,
    underlying_code,
    expiry_date,
    tick_size,
    contract_multiplier,
    is_active,
    settlement_type,
    exchange_code
from {{ ref('stg_futures_contracts') }}

{% endsnapshot %}
