{% macro parse_flexible_number(column) %}
try_cast(
    nullif(
        replace(replace(replace(trim(cast({{ column }} as varchar)), ',', ''), '$', ''), ' ', ''),
        ''
    ) as double
)
{% endmacro %}
