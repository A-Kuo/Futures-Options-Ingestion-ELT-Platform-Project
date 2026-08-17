{% macro parse_flexible_date(column) %}
case
    when regexp_full_match(trim(cast({{ column }} as varchar)), '^[0-9]{4}-[0-9]{2}-[0-9]{2}$')
        then try_strptime(trim(cast({{ column }} as varchar)), '%Y-%m-%d')
    when regexp_full_match(trim(cast({{ column }} as varchar)), '^[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$')
        then try_strptime(trim(cast({{ column }} as varchar)), '%Y-%m-%d %H:%M:%S')
    when regexp_full_match(trim(cast({{ column }} as varchar)), '^[0-9]{8}$')
        then try_strptime(trim(cast({{ column }} as varchar)), '%Y%m%d')
    when regexp_full_match(trim(cast({{ column }} as varchar)), '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{4}$')
        then try_strptime(trim(cast({{ column }} as varchar)), '%m/%d/%Y')
    when regexp_full_match(trim(cast({{ column }} as varchar)), '^[0-9]{1,2}/[0-9]{1,2}/[0-9]{2}$')
        then try_strptime(trim(cast({{ column }} as varchar)), '%m/%d/%y')
    else null
end
{% endmacro %}
