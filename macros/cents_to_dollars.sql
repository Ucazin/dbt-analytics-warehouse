{#
    cents_to_dollars(column_name, precision)

    Convert a cents-denominated integer into a dollars-denominated DECIMAL.

    Usage:
        select {{ cents_to_dollars('price_cents') }} as price_usd
#}

{% macro cents_to_dollars(column_name, precision=2) %}
    cast(({{ column_name }} / 100.0) as numeric(18, {{ precision }}))
{% endmacro %}
