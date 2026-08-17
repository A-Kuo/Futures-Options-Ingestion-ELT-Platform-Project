{% docs dim_underlying %}
One row per listed product root (ES, NQ, CL, GC, ZB). This is the shared parent entity for futures contracts and option series.
{% enddocs %}

{% docs dim_futures_contract %}
One row per listed futures contract. The business key is the canonical Globex symbol (for example ESZ26), built from product root, month letter, and two-digit year.
{% enddocs %}

{% docs dim_options_contract %}
One row per option series. The natural key is underlying + expiry + strike + call/put. This dimension does not change with each chain snapshot; quotes live in the snapshot fact.
{% enddocs %}

{% docs fct_futures_prices %}
One row per futures contract per market date. Contains the daily OHLC/settlement tape plus that session's volume and open interest.
{% enddocs %}

{% docs fct_futures_activity %}
Same grain as futures prices, with nearby rank, days-to-expiry, trailing 20-session context, and unusual activity flags for operations monitoring.
{% enddocs %}

{% docs fct_options_chain_snapshots %}
One row per option contract per snapshot date. Implied volatility and delta are vendor-supplied fields from the extract, not calculated by this project.
{% enddocs %}

{% docs mart_futures_nearby_roll %}
One row per underlying per market date for the front-month contract, with the next contract's volume/open interest attached so roll participation can be monitored as expiry approaches.
{% enddocs %}

{% docs mart_options_chain_activity %}
Reporting-ready option chain at snapshot grain. Use this for strike/expiry heatmaps, spread monitors, and moneyness distribution — not for pricing or forecast work.
{% enddocs %}
