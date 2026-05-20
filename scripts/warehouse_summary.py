"""Print headline numbers from the built warehouse."""
import duckdb
con = duckdb.connect("warehouse.duckdb", read_only=True)

def q(sql): return con.execute(sql).df()

print("\n--- Mart row counts ---")
print(q("""
    SELECT 'main_core.dim_customer'         AS mart, COUNT(*) AS rows FROM main_core.dim_customer
    UNION ALL SELECT 'main_core.dim_product',                   COUNT(*) FROM main_core.dim_product
    UNION ALL SELECT 'main_core.dim_date',                      COUNT(*) FROM main_core.dim_date
    UNION ALL SELECT 'main_core.fct_orders',                    COUNT(*) FROM main_core.fct_orders
    UNION ALL SELECT 'main_finance.fct_mrr_movement',           COUNT(*) FROM main_finance.fct_mrr_movement
    UNION ALL SELECT 'main_finance.fct_subscription_snapshot',  COUNT(*) FROM main_finance.fct_subscription_snapshot
""").to_string(index=False))

print("\n--- fct_orders snapshot ---")
print(q("""
    SELECT
        COUNT(*)                                            AS orders,
        COUNT(DISTINCT customer_key)                        AS customers,
        ROUND(SUM(gross_revenue_usd), 0)                    AS revenue_usd,
        ROUND(AVG(gross_revenue_usd), 2)                    AS avg_order_value,
        SUM(CASE WHEN order_status = 'delivered' THEN 1 ELSE 0 END) AS delivered_orders
    FROM main_core.fct_orders
""").to_string(index=False))

print("\n--- fct_mrr_movement breakdown ---")
print(q("""
    SELECT movement_type, COUNT(*) AS rows, ROUND(SUM(movement_usd), 0) AS total_usd
    FROM main_finance.fct_mrr_movement
    GROUP BY movement_type ORDER BY total_usd DESC
""").to_string(index=False))

print("\n--- Latest 3 months ending MRR ---")
print(q("""
    SELECT snapshot_month, ROUND(SUM(mrr_usd), 0) AS ending_mrr_usd
    FROM main_finance.fct_subscription_snapshot
    WHERE is_active GROUP BY snapshot_month
    ORDER BY snapshot_month DESC LIMIT 3
""").to_string(index=False))
