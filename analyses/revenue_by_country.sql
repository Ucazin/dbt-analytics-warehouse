-- analyses/ files don't get materialized — they're for ad-hoc SQL that you
-- still want versioned and reviewable.

select
    c.country_name,
    c.region,
    count(distinct o.order_id) as orders,
    sum(o.gross_revenue_usd)   as revenue_usd
from {{ ref('fct_orders') }} o
join {{ ref('dim_customer') }} c on c.customer_key = o.customer_key
group by 1, 2
order by revenue_usd desc
