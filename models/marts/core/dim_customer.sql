{{
    config(
        materialized = 'table',
        tags = ['marts', 'core', 'customer']
    )
}}

with customers as (
    select * from {{ ref('stg_customers') }}
),

regions as (
    select * from {{ ref('country_regions') }}
),

lifecycle as (
    select * from {{ ref('int_customer_lifecycle') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['c.customer_id']) }} as customer_key,
    c.customer_id,
    c.email,
    c.country_code,
    r.country_name,
    r.region,
    c.signed_up_at,
    coalesce(l.lifecycle_stage, 'never_active') as lifecycle_stage,
    l.first_active_month,
    l.last_active_month,
    l.churned_month,
    l.latest_plan_id,
    l.lifetime_mrr_usd,
    l.months_with_activity
from customers c
left join regions  r on r.country_code = c.country_code
left join lifecycle l on l.customer_id = c.customer_id
