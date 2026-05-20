{{
    config(
        materialized = 'view',
        tags = ['staging', 'customers']
    )
}}

with source as (
    select * from {{ source('raw', 'customers') }}
),

renamed as (
    select
        customer_id,
        lower(trim(email))                 as email,
        upper(country_code)                as country_code,
        cast(signed_up_at as timestamp)    as signed_up_at,
        cast(status as varchar)            as status,
        synced_at
    from source
)

select * from renamed
