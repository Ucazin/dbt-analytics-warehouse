{{ config(materialized='table', tags=['marts', 'core', 'product']) }}

with products as (
    select * from {{ ref('stg_products') }}
),

categories as (
    select * from {{ ref('product_categories') }}
)

select
    {{ dbt_utils.generate_surrogate_key(['p.product_id']) }} as product_key,
    p.product_id,
    p.product_name,
    p.category_id,
    c.category_name,
    c.department,
    c.is_returnable,
    p.list_price_usd,
    p.weight_grams,
    p.is_active
from products p
left join categories c on c.category_id = p.category_id
