{{ config(materialized='ephemeral') }}

with subs as (
    select * from {{ ref('stg_subscriptions') }}
),

with_lag as (
    select
        customer_id,
        snapshot_month,
        plan_id,
        mrr_usd,
        is_new_this_month,
        is_churn_this_month,
        lag(mrr_usd) over (
            partition by customer_id
            order by     snapshot_month
        )                                                  as prev_mrr_usd,
        lag(is_active::int) over (
            partition by customer_id
            order by     snapshot_month
        )                                                  as prev_is_active
    from subs
),

classified as (
    select
        *,
        case
            when is_new_this_month            then 'new'
            when is_churn_this_month          then 'churned'
            when prev_is_active is null and mrr_usd > 0
                                              then 'new'
            when mrr_usd > coalesce(prev_mrr_usd, 0)
                                              then 'expansion'
            when mrr_usd < coalesce(prev_mrr_usd, 0)
                  and not is_churn_this_month then 'contraction'
            else                                   'flat'
        end as movement_type,

        case
            when is_new_this_month             then mrr_usd
            when is_churn_this_month           then -coalesce(prev_mrr_usd, 0)
            when mrr_usd > coalesce(prev_mrr_usd, 0)
                                               then mrr_usd - prev_mrr_usd
            when mrr_usd < coalesce(prev_mrr_usd, 0)
                  and not is_churn_this_month  then mrr_usd - prev_mrr_usd
            else                                    0
        end as movement_usd

    from with_lag
)

select * from classified
