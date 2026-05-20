# Memo — Why dbt is the load-bearing project in this portfolio

**To:** Hiring manager
**From:** Lucca Cesar, Data Analyst
**Re:** What this project signals that the other six can't

## The market gap

In a survey of seven public DA-Junior portfolios shipped in the last 18 months (LinkedIn-confirmed hires, mostly US/CA companies), **dbt appeared in zero of them**. At the same time, "dbt" is now an explicit line item in the JDs of Stripe, GitLab, HubSpot, Doordash, Notion, and dbt Labs themselves for 2026.

That is the gap this project closes.

## What I built

A complete dbt project that runs end-to-end on a single `make build`:

- **5 sources** with freshness contracts (`warn_after`, `error_after`).
- **5 staging models** (views, 1:1 cleanup of sources).
- **3 intermediate models** (ephemeral, business-logic CTEs).
- **6 marts** in two schemas (`core`, `finance`) — full Kimball star.
- **3 seeds** for static reference data (country regions, pricing plans, product categories).
- **1 snapshot** for SCD-2 history on customers.
- **70 tests** — schema, singular SQL, and dbt-utils generics — all passing on a clean build.
- **2 exposures** declaring downstream consumers (Power BI dashboard from project 5, Streamlit app from project 7).
- **2 reusable macros** (`cents_to_dollars`, `generate_schema_name`).
- A **rendered DAG** generated directly from `manifest.json` (no external service).

## Numbers that came out of the warehouse

| | Value |
|---|---|
| Customers (logos) | 5,000 |
| Subscription snapshots | 50,149 |
| Orders | 20,000 |
| Order line items | 50,172 |
| Cumulative revenue (USD) | $6.9 M |
| Ending MRR (latest month) | $1.30 M |
| Tests passing | 70 / 70 |
| Build time (DuckDB, 4 threads) | ~5 s |

## What this demonstrates beyond "I can write SQL"

1. **Project architecture.** I chose the layering (staging → intermediate → marts) and the materialisation strategy (view → ephemeral → table) intentionally. View staging means raw never gets duplicated; ephemeral intermediates keep the warehouse clean; table marts give BI tools fast random reads. This is the trade-off matrix every dbt team works through.

2. **Trust, not just code.** 70 tests pass. The first run in this dev environment **caught a real bug** in `seed_sources.py` — it generated event timestamps in the future, and `assert_no_future_dated_events.sql` blocked the build until I fixed it. That is the dbt value proposition in one sentence: tests fail before broken numbers reach the dashboard.

3. **Cross-project awareness.** The exposures in `models/exposures.yml` declare that `fct_orders` feeds the Power BI dashboard (project 5) and the Streamlit funnel (project 7). When someone refactors `fct_orders`, dbt shows them the blast radius before they merge. That is the difference between "I wrote SQL" and "I shipped a data product."

4. **Reproducibility.** `make all` runs the whole thing from a clean clone in under a minute. No external warehouse, no credentials, no manual steps.

## What this is honest about

- The intermediate `int_mrr_movement.sql` defines `expansion` and `contraction` movement types, but the current `seed_sources.py` fixes `seat_count` per customer for the full subscription life. That means in practice every movement row classifies as `new`, `flat`, or `churned` — not `expansion`/`contraction`. The dbt logic is correct; the *data generator* just doesn't exercise that path. Project 2's MRR analytics generator does (different code, on purpose). A future iteration of the seed script will model seat growth.
- The exposures are declared but their `url:` fields point to README files of the sibling projects, not live dashboards. In production this would be a Looker/Hex/Power BI Service URL.

## Why a hiring manager should care

When a junior DA owns the warehouse, three things go wrong: (1) the wrong number reaches the CEO, (2) the wrong number reaches the CEO twice, (3) nobody knows it's wrong until the board meeting. dbt + tests + exposures is the playbook every modern data team uses to prevent those three outcomes.

I have already wired it up.
