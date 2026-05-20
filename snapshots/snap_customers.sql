{% snapshot snap_customers %}

{{
    config(
        target_schema = 'snapshots',
        unique_key    = 'customer_id',
        strategy      = 'check',
        check_cols    = ['country_code', 'status']
    )
}}

select
    customer_id,
    email,
    country_code,
    status,
    signed_up_at,
    synced_at
from {{ source('raw', 'customers') }}

{% endsnapshot %}
