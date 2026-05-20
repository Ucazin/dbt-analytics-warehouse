-- Singular test: gross_revenue_usd should never be negative on a non-refunded order.

select *
from   {{ ref('fct_orders') }}
where  gross_revenue_usd < 0
  and  order_status not in ('refunded', 'canceled')
