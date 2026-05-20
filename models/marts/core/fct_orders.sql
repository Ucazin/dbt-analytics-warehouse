{{ config(materialized='table', tags=['marts', 'core', 'orders']) }}

with orders as (
    select * from {{ ref('stg_orders') }}
),

items as (
    select * from {{ ref('int_order_aggregations') }}
),

customers as (
    select customer_id, customer_key from {{ ref('dim_customer') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['o.order_id']) }} as order_key,
    o.order_id,
    c.customer_key,
    o.ordered_at,
    cast(strftime(o.ordered_at, '%Y%m%d') as integer) as ordered_date_key,
    o.delivered_at,
    o.order_status,
    o.currency,
    i.item_count,
    i.units,
    i.items_subtotal_usd,
    o.shipping_usd,
    o.tax_usd,
    o.gross_revenue_usd,
    case
        when o.delivered_at is not null
        then date_diff('day', o.ordered_at, o.delivered_at)
    end as fulfillment_days
from orders o
left join items     i on i.order_id    = o.order_id
left join customers c on c.customer_id = o.customer_id
