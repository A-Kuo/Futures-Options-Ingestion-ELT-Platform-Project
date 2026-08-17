from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import query
from app.chart_style import PLOT_LAYOUT

st.set_page_config(page_title="Pipeline quality", layout="wide")
st.title("Pipeline and quality overview")
st.caption("Source landing, model row counts, and date coverage. Tests are run with dbt, not in this page.")

counts = query(
    """
    select metric_group, metric_name, metric_value
    from marts.mart_pipeline_quality
    where metric_group in ('source_row_count', 'model_row_count')
    order by metric_group, metric_name
    """
)

left, right = st.columns(2)
with left:
    st.subheader("Raw landing")
    raw = counts[counts["metric_group"] == "source_row_count"].copy()
    raw["metric_value"] = raw["metric_value"].astype(int)
    st.dataframe(raw[["metric_name", "metric_value"]], use_container_width=True, hide_index=True)
with right:
    st.subheader("Staged and fact tables")
    models = counts[counts["metric_group"] == "model_row_count"].copy()
    models["metric_value"] = models["metric_value"].astype(int)
    st.dataframe(models[["metric_name", "metric_value"]], use_container_width=True, hide_index=True)

coverage = query(
    """
    select metric_name as series, extra_1 as min_date, extra_2 as max_date, metric_value as row_count
    from marts.mart_pipeline_quality
    where metric_group = 'coverage'
    order by metric_name
    """
)
st.subheader("Coverage windows")
st.dataframe(coverage, use_container_width=True, hide_index=True)

dupes = query(
    """
    select 'futures_prices' as extract, count(*) as rows_with_source_duplicates
    from staging.stg_futures_prices
    where source_duplicate_count > 1
    union all
    select 'options_chain', count(*)
    from staging.stg_options_chain
    where source_duplicate_count > 1
    """
)
st.subheader("Duplicates collapsed in staging")
st.dataframe(dupes, use_container_width=True, hide_index=True)

fresh = query(
    """
    select
        max(market_date) as last_futures_session,
        date '2026-08-14' as expected_as_of,
        date_diff('day', max(market_date), date '2026-08-17') as days_since_last_session
    from marts.fct_futures_prices
    """
)
st.subheader("Session recency")
st.dataframe(fresh, use_container_width=True, hide_index=True)

layer = models.copy()
fig = px.bar(layer, x="metric_name", y="metric_value", title="Row counts by modeled table")
fig.update_layout(**PLOT_LAYOUT, xaxis_title="Model", yaxis_title="Rows")
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
Run tests locally with:

```bash
dbt test --profiles-dir . --select marts
```

Singular tests include one front-month row per underlying/date and valid call/put flags.
"""
)
