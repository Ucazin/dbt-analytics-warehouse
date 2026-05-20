{{ config(materialized='table', tags=['marts', 'core', 'date']) }}

with date_spine as (
    {{ dbt_utils.date_spine(
         datepart = 'day',
         start_date = "cast('2022-01-01' as date)",
         end_date   = "cast('2027-12-31' as date)"
    ) }}
)

select
    cast(date_day as date)                                                 as calendar_date,
    cast(strftime(date_day, '%Y%m%d') as integer)                          as date_key,
    extract(year    from date_day)                                         as year,
    extract(quarter from date_day)                                         as quarter,
    extract(month   from date_day)                                         as month,
    extract(day     from date_day)                                         as day,
    extract(dow     from date_day)                                         as day_of_week,
    strftime(date_day, '%A')                                               as day_name,
    strftime(date_day, '%B')                                               as month_name,
    date_trunc('month',   date_day)                                        as month_start,
    date_trunc('quarter', date_day)                                        as quarter_start,
    case when extract(dow from date_day) in (0, 6) then true else false end as is_weekend
from date_spine
