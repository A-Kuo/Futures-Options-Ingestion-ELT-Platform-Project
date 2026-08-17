from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import query, scalar

st.set_page_config(
    page_title="Futures and Options ELT",
    page_icon="FO",
    layout="wide",
)

st.title("Futures and Options ELT Analytics Platform")
st.caption(
    "Warehouse-style reporting for contract activity, expiry monitoring, and options-chain structure. "
    "This app does not forecast prices or implied volatility."
)

try:
    last_futures = scalar("select max(market_date) from marts.fct_futures_prices")
    futures_rows = scalar("select count(*) from marts.fct_futures_prices")
    options_rows = scalar("select count(*) from marts.fct_options_chain_snapshots")
    unusual = scalar("select count(*) from marts.fct_futures_activity where is_unusual_volume")
except FileNotFoundError as exc:
    st.error(str(exc))
    st.stop()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Futures fact rows", f"{int(futures_rows):,}")
c2.metric("Options snapshot rows", f"{int(options_rows):,}")
c3.metric("Latest futures session", str(last_futures)[:10] if last_futures is not None else "n/a")
c4.metric("Unusual volume flags", f"{int(unusual):,}")

st.markdown(
    """
Use the pages in the sidebar:

1. **Pipeline quality** — row counts, coverage, and freshness
2. **Futures activity** — nearby roll, term structure, expiry calendar
3. **Options activity** — strike/expiry concentration, put/call, spreads
"""
)

coverage = query(
    """
    select metric_name, metric_value, extra_1 as min_date, extra_2 as max_date
    from marts.mart_pipeline_quality
    where metric_group = 'coverage'
    order by metric_name
    """
)
st.subheader("Data coverage by underlying")
st.dataframe(coverage, use_container_width=True, hide_index=True)

st.info(
    "Sample extracts are synthetic but schema-realistic. "
    "Implied volatility and delta are source-supplied demo fields, not model outputs."
)
