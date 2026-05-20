{{ config(materialized='view', tags=['staging', 'orders']) }}

with source as (
    select * from {{ source('raw', 'order_items') }}
)

select
    order_item_id,
    order_id,
    product_id,
    cast(quantity as integer)                    as quantity,
    {{ cents_to_dollars('unit_price_cents') }}   as unit_price_usd,
    {{ cents_to_dollars('line_total_cents') }}   as line_total_usd
from source
