from __future__ import annotations

import sys
from pathlib import Path

import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db import as_sql_date, query
from app.chart_style import PLOT_LAYOUT

st.set_page_config(page_title="Options activity", layout="wide")
st.title("Options activity")
st.caption("Chain structure, open-interest concentration, and put/call reporting. Not a volatility forecast.")

underlyings = query("select distinct underlying_code from marts.mart_options_chain_activity order by 1")
underlying = st.selectbox("Underlying", underlyings["underlying_code"].tolist(), index=0)

latest_date = as_sql_date(
    query(
        f"""
        select max(snapshot_date) as snapshot_date
        from marts.mart_options_chain_activity
        where underlying_code = '{underlying}'
        """
    ).iloc[0]["snapshot_date"]
)

expiries = query(
    f"""
    select distinct expiry_date
    from marts.mart_options_chain_activity
    where underlying_code = '{underlying}'
      and snapshot_date = '{latest_date}'
    order by 1
    """
)
expiry = as_sql_date(st.selectbox("Expiry", expiries["expiry_date"].tolist()))

pc = query(
    f"""
    select *
    from marts.mart_put_call_summary
    where underlying_code = '{underlying}'
    order by snapshot_date
    """
)
strike = query(
    f"""
    select *
    from marts.mart_options_open_interest_by_strike
    where underlying_code = '{underlying}'
      and snapshot_date = '{latest_date}'
      and expiry_date = '{expiry}'
    order by strike
    """
)
heatmap = query(
    f"""
    select expiry_date, strike, sum(total_open_interest) as total_open_interest
    from marts.mart_options_open_interest_by_strike
    where underlying_code = '{underlying}'
      and snapshot_date = '{latest_date}'
    group by 1, 2
    """
)
spreads = query(
    f"""
    select option_contract_nk, strike, call_put_flag, bid_ask_spread, relative_spread, volume, moneyness_bucket
    from marts.mart_options_spread_monitor
    where underlying_code = '{underlying}'
      and snapshot_date = '{latest_date}'
      and expiry_date = '{expiry}'
    order by relative_spread desc nulls last
    limit 20
    """
)
expiry_summary = query(
    f"""
    select expiry_date, days_to_expiry, strike_count, total_volume, total_open_interest, call_volume, put_volume
    from marts.mart_options_expiry_summary
    where underlying_code = '{underlying}'
      and snapshot_date = '{latest_date}'
    order by expiry_date
    """
)

c1, c2, c3 = st.columns(3)
if not pc.empty:
    last = pc.iloc[-1]
    c1.metric("Snapshot", str(latest_date)[:10])
    c2.metric("Put/call volume", f"{last['put_call_volume_ratio']:.2f}")
    c3.metric("Put/call open interest", f"{last['put_call_oi_ratio']:.2f}")

heat_pivot = heatmap.pivot(index="strike", columns="expiry_date", values="total_open_interest")
fig_hm = px.imshow(
    heat_pivot,
    aspect="auto",
    origin="lower",
    color_continuous_scale=["#1B2026", "#C4A35A"],
    title=f"{underlying} open interest by strike and expiry",
)
fig_hm.update_layout(**PLOT_LAYOUT, xaxis_title="Expiry", yaxis_title="Strike")
st.plotly_chart(fig_hm, use_container_width=True)

left, right = st.columns(2)
with left:
    fig_oi = px.bar(
        strike,
        x="strike",
        y=["call_open_interest", "put_open_interest"],
        barmode="group",
        title="Open interest by strike",
    )
    fig_oi.update_layout(**PLOT_LAYOUT, xaxis_title="Strike", yaxis_title="Open interest")
    st.plotly_chart(fig_oi, use_container_width=True)
with right:
    fig_pc = px.line(
        pc,
        x="snapshot_date",
        y=["put_call_volume_ratio", "put_call_oi_ratio"],
        title="Put/call ratios over snapshots",
    )
    fig_pc.update_layout(**PLOT_LAYOUT, xaxis_title="Snapshot date", yaxis_title="Ratio")
    st.plotly_chart(fig_pc, use_container_width=True)

st.subheader("Activity by expiry")
st.dataframe(expiry_summary, use_container_width=True, hide_index=True)

st.subheader("Widest relative spreads")
st.caption("Quote-width monitoring for data quality and chain completeness, not execution.")
st.dataframe(spreads, use_container_width=True, hide_index=True)
