{{ config(materialized='ephemeral') }}

with subs as (
    select * from {{ ref('stg_subscriptions') }}
),

aggregated as (
    select
        customer_id,
        min(snapshot_month)                                        as first_active_month,
        max(case when is_active then snapshot_month end)           as last_active_month,
        max(case when is_churn_this_month then snapshot_month end) as churned_month,
        max(plan_id)                                               as latest_plan_id,
        sum(case when is_active then mrr_usd else 0 end)           as lifetime_mrr_usd,
        count(distinct snapshot_month)                             as months_with_activity
    from subs
    group by customer_id
)

select
    *,
    case
        when churned_month is not null            then 'churned'
        when last_active_month is null            then 'never_active'
        when months_with_activity >= 12           then 'mature'
        when months_with_activity >= 3            then 'engaged'
        else                                          'new'
    end as lifecycle_stage
from aggregated
