{{ config(materialized='ephemeral') }}

with items as (
    select * from {{ ref('stg_order_items') }}
),

by_order as (
    select
        order_id,
        count(*)                              as item_count,
        sum(quantity)                         as units,
        sum(line_total_usd)                   as items_subtotal_usd
    from items
    group by order_id
)

select * from by_order
