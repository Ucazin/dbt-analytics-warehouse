# Lineage summary

| Layer | Model | Materialization | Depends on |
|-------|-------|-----------------|------------|
| source | src.customers | — | — |
| source | src.order_items | — | — |
| source | src.orders | — | — |
| source | src.products | — | — |
| source | src.subscriptions | — | — |
| seed | country_regions | seed | — |
| seed | pricing_plans | seed | — |
| seed | product_categories | seed | — |
| staging | stg_customers | view | src.customers |
| staging | stg_order_items | view | src.order_items |
| staging | stg_orders | view | src.orders |
| staging | stg_products | view | src.products |
| staging | stg_subscriptions | view | src.subscriptions |
| intermediate | int_customer_lifecycle | ephemeral | stg_subscriptions |
| intermediate | int_mrr_movement | ephemeral | stg_subscriptions |
| intermediate | int_order_aggregations | ephemeral | stg_order_items |
| marts | dim_customer | table | int_customer_lifecycle, stg_customers, country_regions |
| marts | dim_date | table | — |
| marts | dim_product | table | stg_products, product_categories |
| marts | fct_mrr_movement | table | dim_customer, int_mrr_movement |
| marts | fct_orders | table | dim_customer, int_order_aggregations, stg_orders |
| marts | fct_subscription_snapshot | table | dim_customer, stg_subscriptions, pricing_plans |
| snapshot | snap_customers | snapshot | src.customers |