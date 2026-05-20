"""
seed_sources.py — generate the raw.* tables that dbt expects.

Run once before `dbt build`:
    python scripts/seed_sources.py

Writes a DuckDB file at ./warehouse.duckdb with a `raw` schema containing
customers, subscriptions, orders, order_items, products.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

SEED = 42
N_CUSTOMERS = 5_000
N_PRODUCTS  = 200
N_ORDERS    = 20_000
N_MONTHS    = 24
# Start 28 months ago so every generated event lands in the past (the dbt
# test `assert_no_future_dated_events` enforces this invariant).
START_MONTH = (pd.Timestamp.now().normalize().replace(day=1)
               - pd.DateOffset(months=N_MONTHS + 4))
NOW         = pd.Timestamp.now().normalize()
DB_PATH     = "warehouse.duckdb"

rng = np.random.default_rng(SEED)


def make_customers() -> pd.DataFrame:
    countries = ["US", "CA", "UK", "AU", "DE", "FR", "BR", "JP"]
    probs     = [0.45, 0.10, 0.12, 0.06, 0.08, 0.05, 0.10, 0.04]
    return pd.DataFrame({
        "customer_id":  [f"C{1+i:06d}" for i in range(N_CUSTOMERS)],
        "email":        [f"user{i}@example.com" for i in range(N_CUSTOMERS)],
        "country_code": rng.choice(countries, size=N_CUSTOMERS, p=probs),
        "signed_up_at": pd.to_datetime(
            START_MONTH + pd.to_timedelta(
                rng.integers(0, N_MONTHS * 30, size=N_CUSTOMERS), unit="D"
            )
        ),
        "status":       rng.choice(["active", "active", "active", "churned"],
                                   size=N_CUSTOMERS),
        "synced_at":    datetime.now(timezone.utc).replace(tzinfo=None),
    })


def make_products() -> pd.DataFrame:
    categories = ["ELEC", "COMP", "ACC", "SOFT", "SUB", "SVC", "TRAIN", "SUPP"]
    return pd.DataFrame({
        "product_id":      [f"P{1+i:04d}" for i in range(N_PRODUCTS)],
        "product_name":    [f"Product {i:04d}" for i in range(N_PRODUCTS)],
        "category_id":     rng.choice(categories, size=N_PRODUCTS),
        "list_price_cents": rng.integers(500, 80_000, size=N_PRODUCTS),
        "weight_grams":     rng.integers(50, 5_000, size=N_PRODUCTS),
        "is_active":        rng.choice([True, True, True, False], size=N_PRODUCTS),
    })


def make_subscriptions(customers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    plan_prices = {"STARTER": 1_500, "GROWTH": 4_000, "PRO": 8_500}
    months = pd.date_range(START_MONTH, periods=N_MONTHS, freq="MS")
    for _, c in customers.iterrows():
        plan = rng.choice(list(plan_prices.keys()), p=[0.55, 0.30, 0.15])
        first_month_idx = rng.integers(0, N_MONTHS - 1)
        active = True
        seats = int(rng.integers(1, 25))
        for m_idx in range(first_month_idx, N_MONTHS):
            if not active:
                break
            is_new   = m_idx == first_month_idx
            is_churn = (not is_new) and rng.random() < 0.04
            if is_churn:
                active = False
            mrr_cents = seats * plan_prices[plan]
            rows.append({
                "subscription_id": f"S{len(rows)+1:08d}",
                "customer_id":     c["customer_id"],
                "plan_id":         plan,
                "snapshot_month":  months[m_idx],
                "seat_count":      seats,
                "mrr_cents":       int(mrr_cents),
                "is_active":       active,
                "is_new":          is_new,
                "is_churn":        is_churn,
            })
    return pd.DataFrame(rows)


def make_orders(customers: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    orders   = []
    items    = []
    statuses = ["delivered", "delivered", "delivered", "shipped", "paid", "refunded"]
    for i in range(N_ORDERS):
        cust = customers.sample(1, random_state=int(rng.integers(0, 1 << 31))).iloc[0]
        signup = pd.Timestamp(cust["signed_up_at"])
        # Cap the upper bound so no order lands in the future.
        max_days = max(1, min(540, (NOW - signup).days - 8))
        ordered_at = signup + pd.Timedelta(days=int(rng.integers(1, max_days + 1)))
        status     = rng.choice(statuses)
        paid_at    = ordered_at + pd.Timedelta(minutes=int(rng.integers(1, 60)))
        shipped_at = paid_at    + pd.Timedelta(days=int(rng.integers(1, 4))) if status in ("shipped", "delivered") else pd.NaT
        delivered_at = shipped_at + pd.Timedelta(days=int(rng.integers(1, 6))) if status == "delivered" else pd.NaT
        n_items    = int(rng.integers(1, 5))
        item_lines = []
        gross_cents = 0
        for _ in range(n_items):
            qty   = int(rng.integers(1, 4))
            unit  = int(rng.integers(500, 12_000))
            line  = qty * unit
            gross_cents += line
            item_lines.append((qty, unit, line))
        shipping_cents = int(rng.integers(0, 1_500))
        tax_cents      = int(gross_cents * 0.08)
        orders.append({
            "order_id":            f"O{i+1:07d}",
            "customer_id":         cust["customer_id"],
            "ordered_at":          ordered_at,
            "paid_at":             paid_at,
            "shipped_at":          shipped_at,
            "delivered_at":        delivered_at,
            "order_status":        status,
            "gross_revenue_cents": gross_cents + shipping_cents + tax_cents,
            "shipping_cents":      shipping_cents,
            "tax_cents":           tax_cents,
            "currency":            "USD",
        })
        for qty, unit, line in item_lines:
            items.append({
                "order_item_id":   f"OI{len(items)+1:08d}",
                "order_id":        f"O{i+1:07d}",
                "product_id":      f"P{int(rng.integers(1, N_PRODUCTS+1)):04d}",
                "quantity":        qty,
                "unit_price_cents": unit,
                "line_total_cents": line,
            })
    return pd.DataFrame(orders), pd.DataFrame(items)


def main() -> None:
    print(f"Generating synthetic raw data → {DB_PATH}")
    customers = make_customers()
    products  = make_products()
    subs      = make_subscriptions(customers)
    orders, items = make_orders(customers)

    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")

    for name, df in [
        ("customers",     customers),
        ("products",      products),
        ("subscriptions", subs),
        ("orders",        orders),
        ("order_items",   items),
    ]:
        con.execute(f"DROP TABLE IF EXISTS raw.{name}")
        con.register("_tmp", df)
        con.execute(f"CREATE TABLE raw.{name} AS SELECT * FROM _tmp")
        con.unregister("_tmp")
        print(f"  raw.{name:<14} {len(df):>8,} rows")

    con.close()
    print(f"\nDone. Now run:   dbt deps && dbt build")


if __name__ == "__main__":
    main()
