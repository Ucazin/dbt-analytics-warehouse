{#
    Custom schema-name resolver:
      - dev:  every model lives in dbt_<user>_<schema>
      - prod: bare schema name (as declared in dbt_project.yml or the model config)
#}

{% macro generate_schema_name(custom_schema_name, node) -%}
    {%- set default_schema = target.schema -%}
    {%- if target.name == 'prod' -%}
        {{ custom_schema_name | default(default_schema) | trim }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name | trim }}
    {%- endif -%}
{%- endmacro %}
