{{ config(materialized='table', tags=['marts', 'finance', 'mrr']) }}

with movement as (
    select * from {{ ref('int_mrr_movement') }}
),

customers as (
    select customer_id, customer_key from {{ ref('dim_customer') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['m.customer_id', 'm.snapshot_month']) }} as movement_key,
    c.customer_key,
    m.snapshot_month,
    m.plan_id,
    m.mrr_usd,
    m.prev_mrr_usd,
    m.movement_type,
    m.movement_usd
from movement m
left join customers c on c.customer_id = m.customer_id
