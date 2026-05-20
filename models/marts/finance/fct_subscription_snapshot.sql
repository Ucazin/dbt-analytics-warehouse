{{ config(materialized='table', tags=['marts', 'finance', 'subscription']) }}

with subs as (
    select * from {{ ref('stg_subscriptions') }}
),

plans as (
    select * from {{ ref('pricing_plans') }}
),

customers as (
    select customer_id, customer_key from {{ ref('dim_customer') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['s.customer_id', 's.snapshot_month']) }} as snapshot_key,
    c.customer_key,
    s.snapshot_month,
    s.plan_id,
    p.plan_name,
    p.tier_rank,
    s.seat_count,
    s.mrr_usd,
    s.is_active,
    s.is_new_this_month,
    s.is_churn_this_month
from subs s
left join plans     p on p.plan_id     = s.plan_id
left join customers c on c.customer_id = s.customer_id
