{% macro normalize_symbol(column) %}
upper(replace(trim(cast({{ column }} as varchar)), ' ', ''))
{% endmacro %}
