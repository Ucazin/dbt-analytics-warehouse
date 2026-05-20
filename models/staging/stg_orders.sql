{{ config(materialized='view', tags=['staging', 'orders']) }}

with source as (
    select * from {{ source('raw', 'orders') }}
)

select
    order_id,
    customer_id,
    cast(ordered_at  as timestamp)   as ordered_at,
    cast(paid_at     as timestamp)   as paid_at,
    cast(shipped_at  as timestamp)   as shipped_at,
    cast(delivered_at as timestamp)  as delivered_at,
    lower(order_status)              as order_status,
    {{ cents_to_dollars('gross_revenue_cents') }} as gross_revenue_usd,
    {{ cents_to_dollars('shipping_cents') }}      as shipping_usd,
    {{ cents_to_dollars('tax_cents') }}           as tax_usd,
    upper(currency)                  as currency
from source
