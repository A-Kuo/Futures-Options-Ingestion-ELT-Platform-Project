{% macro standardize_call_put(column) %}
case
    when lower(trim(cast({{ column }} as varchar))) in ('c', 'call', 'calls') then 'C'
    when lower(trim(cast({{ column }} as varchar))) in ('p', 'put', 'puts') then 'P'
    else null
end
{% endmacro %}
