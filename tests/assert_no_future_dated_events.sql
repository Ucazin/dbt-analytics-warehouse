-- Singular test: no fact row can have an event timestamp in the future.
-- Returns rows that violate the assertion — empty result = pass.

with violations as (
    select 'fct_orders' as model, order_id as id, ordered_at as event_ts
    from   {{ ref('fct_orders') }}
    where  ordered_at > current_timestamp

    union all

    select 'fct_subscription_snapshot', cast(snapshot_key as varchar), snapshot_month
    from   {{ ref('fct_subscription_snapshot') }}
    where  snapshot_month > current_date
)

select * from violations
