import duckdb

con = duckdb.connect("data/warehouse.duckdb", read_only=True)
print("--- nearby roll latest ---")
print(
    con.execute(
        """
        select market_date, underlying_code, contract_symbol, days_to_expiry, volume, round(front_volume_share, 3) as front_volume_share
        from marts.mart_futures_nearby_roll
        where market_date = (select max(market_date) from marts.mart_futures_nearby_roll)
        order by underlying_code
        """
    )
    .df()
    .to_string(index=False)
)
print("--- unusual CL ---")
print(
    con.execute(
        """
        select market_date, contract_symbol, volume, round(volume_20d_avg, 0) as volume_20d_avg
        from marts.mart_futures_volume_oi_trends
        where is_unusual_volume and underlying_code = 'CL'
        order by market_date
        limit 5
        """
    )
    .df()
    .to_string(index=False)
)
print("--- put call latest ---")
print(
    con.execute(
        """
        select snapshot_date, underlying_code, put_volume, call_volume, round(put_call_volume_ratio, 3) as pc_vol
        from marts.mart_put_call_summary
        where snapshot_date = (select max(snapshot_date) from marts.mart_put_call_summary)
        """
    )
    .df()
    .to_string(index=False)
)
print("--- quality ---")
print(
    con.execute(
        """
        select metric_name, metric_value
        from marts.mart_pipeline_quality
        where metric_group = 'model_row_count'
        order by metric_name
        """
    )
    .df()
    .to_string(index=False)
)
