{{ config(materialized='view', tags=['staging', 'subscriptions']) }}

with source as (
    select * from {{ source('raw', 'subscriptions') }}
)

select
    subscription_id,
    customer_id,
    upper(plan_id)                            as plan_id,
    cast(snapshot_month as date)              as snapshot_month,
    cast(seat_count as integer)               as seat_count,
    {{ cents_to_dollars('mrr_cents') }}        as mrr_usd,
    cast(is_active as boolean)                as is_active,
    cast(is_new as boolean)                   as is_new_this_month,
    cast(is_churn as boolean)                 as is_churn_this_month
from source
