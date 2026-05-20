{{ config(materialized='view', tags=['staging', 'products']) }}

with source as (
    select * from {{ source('raw', 'products') }}
)

select
    product_id,
    product_name,
    upper(category_id)                          as category_id,
    {{ cents_to_dollars('list_price_cents') }}  as list_price_usd,
    cast(weight_grams as integer)               as weight_grams,
    cast(is_active as boolean)                  as is_active
from source
