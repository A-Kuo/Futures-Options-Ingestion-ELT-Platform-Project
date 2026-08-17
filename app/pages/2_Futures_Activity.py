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

st.set_page_config(page_title="Futures activity", layout="wide")
st.title("Futures activity")
st.caption("Nearby-contract reporting, term structure, and expiry monitoring — not a trading book.")

underlyings = query("select distinct underlying_code from marts.mart_futures_nearby_roll order by 1")
underlying = st.selectbox("Underlying", underlyings["underlying_code"].tolist(), index=0)

roll = query(
    f"""
    select *
    from marts.mart_futures_nearby_roll
    where underlying_code = '{underlying}'
    order by market_date
    """
)
term = query(
    f"""
    select *
    from marts.mart_futures_term_structure
    where underlying_code = '{underlying}'
      and market_date = (select max(market_date) from marts.mart_futures_term_structure where underlying_code = '{underlying}')
    order by nearby_rank
    """
)
overview = query(
    f"""
    select contract_symbol, expiry_date, nearby_rank, days_to_expiry, settlement_price, volume, open_interest,
           is_roll_window, is_unusual_volume
    from marts.mart_futures_contract_overview
    where underlying_code = '{underlying}'
    order by expiry_date
    """
)
unusual = query(
    f"""
    select market_date, contract_symbol, nearby_rank, volume, volume_20d_avg, open_interest, is_unusual_volume, is_unusual_open_interest
    from marts.mart_futures_volume_oi_trends
    where underlying_code = '{underlying}'
      and (is_unusual_volume or is_unusual_open_interest)
    order by market_date desc
    limit 25
    """
)
calendar = query(
    f"""
    select contract_symbol, expiry_date, days_to_expiry_as_of, latest_nearby_rank, latest_volume, latest_open_interest
    from marts.mart_futures_expiry_calendar
    where underlying_code = '{underlying}'
    order by expiry_date
    """
)

c1, c2, c3 = st.columns(3)
latest = roll.iloc[-1] if not roll.empty else None
if latest is not None:
    c1.metric("Front month", latest["contract_symbol"])
    c2.metric("Days to expiry", int(latest["days_to_expiry"]))
    share = latest["front_volume_share"]
    c3.metric("Front volume share", f"{share:.1%}" if share is not None and share == share else "n/a")

fig = px.line(
    roll,
    x="market_date",
    y="front_volume_share",
    title=f"{underlying} front-month volume share vs next contract",
)
fig.update_layout(**PLOT_LAYOUT, xaxis_title="Market date", yaxis_title="Front volume share")
st.plotly_chart(fig, use_container_width=True)

left, right = st.columns(2)
with left:
    fig_vol = px.line(
        roll,
        x="market_date",
        y=["volume", "next_contract_volume"],
        title="Front vs next-month volume",
    )
    fig_vol.update_layout(**PLOT_LAYOUT, xaxis_title="Market date", yaxis_title="Volume")
    st.plotly_chart(fig_vol, use_container_width=True)
with right:
    fig_term = px.line(
        term,
        x="nearby_rank",
        y="settlement_price",
        markers=True,
        title=f"{underlying} term structure on latest session",
    )
    fig_term.update_layout(**PLOT_LAYOUT, xaxis_title="Nearby rank", yaxis_title="Settlement")
    st.plotly_chart(fig_term, use_container_width=True)

st.subheader("Contract overview")
st.dataframe(overview, use_container_width=True, hide_index=True)

st.subheader("Expiry calendar")
st.dataframe(calendar, use_container_width=True, hide_index=True)

st.subheader("Unusual activity flags")
st.caption("Flags compare a session to the prior 20 sessions for that contract. They are operations monitors, not signals.")
st.dataframe(unusual, use_container_width=True, hide_index=True)
