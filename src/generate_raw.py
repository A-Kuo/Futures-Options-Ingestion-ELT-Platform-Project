"""Synthetic but schema-realistic futures and options extracts.

The files this module writes are intentionally messy: mixed date formats,
inconsistent call/put flags, padded symbols, and a small number of duplicate
rows. Staging models are responsible for cleaning that source weirdness.

This is not live market data and is not suitable for trading.
"""

from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw_samples"

AS_OF = date(2026, 8, 14)
START = date(2026, 4, 1)
RNG = random.Random(42)

MONTH_CODES = {
    1: "F",
    2: "G",
    3: "H",
    4: "J",
    5: "K",
    6: "M",
    7: "N",
    8: "Q",
    9: "U",
    10: "V",
    11: "X",
    12: "Z",
}

# CME equity index futures typically expire the 3rd Friday.
# Energy/metal expiries here are simplified exchange-style dates, not official calendars.
US_HOLIDAYS_2026 = {
    date(2026, 4, 3),
    date(2026, 5, 25),
    date(2026, 6, 19),
    date(2026, 7, 3),
}


def third_friday(year: int, month: int) -> date:
    d = date(year, month, 1)
    fridays = 0
    while True:
        if d.weekday() == 4:
            fridays += 1
            if fridays == 3:
                return d
        d += timedelta(days=1)


def trading_days(start: date, end: date) -> list[date]:
    days: list[date] = []
    current = start
    while current <= end:
        if current.weekday() < 5 and current not in US_HOLIDAYS_2026:
            days.append(current)
        current += timedelta(days=1)
    return days


def globex_symbol(root: str, expiry: date) -> str:
    return f"{root}{MONTH_CODES[expiry.month]}{expiry.year % 100:02d}"


def dirty_date(d: date) -> str:
    choice = RNG.random()
    if choice < 0.55:
        return d.isoformat()
    if choice < 0.75:
        return d.strftime("%m/%d/%Y")
    if choice < 0.90:
        return d.strftime("%Y%m%d")
    return d.strftime("%m/%d/%y")


def dirty_symbol(symbol: str) -> str:
    choice = RNG.random()
    if choice < 0.80:
        return symbol
    if choice < 0.90:
        return symbol.lower()
    return f"{symbol[:2]} {symbol[2:]}"


def dirty_bool(value: bool) -> str:
    if value:
        return RNG.choice(["Y", "true", "True", "1", "active"])
    return RNG.choice(["N", "false", "0", "inactive"])


def dirty_number(value: float | int | None, as_int: bool = False) -> str:
    if value is None:
        return RNG.choice(["", "NA", "null"])
    if as_int:
        formatted = f"{int(value)}"
    else:
        formatted = f"{value:.4f}".rstrip("0").rstrip(".")
    if RNG.random() < 0.08:
        return f"{int(value):,}" if as_int else f"{value:,.2f}"
    return formatted


UNDERLYINGS = [
    {
        "product_code": "ES",
        "product_desc": "E-mini S&P 500",
        "asset_class": "Equity Index",
        "exch": "CME",
        "exch_full": "Chicago Mercantile Exchange",
        "min_tick": 0.25,
        "tick_val": 12.50,
        "multiplier": 50,
        "ccy": "USD",
        "uom": "index points",
        "session": "Sun-Fri 17:00-16:00 CT",
        "group_name": "Equity",
        "spot": 5825.0,
        "vol": 0.13,
        "tick": 0.25,
        "style": "quarterly",
    },
    {
        "product_code": "NQ",
        "product_desc": "E-mini Nasdaq-100",
        "asset_class": "Equity Index",
        "exch": "cme",
        "exch_full": "Chicago Mercantile Exchange",
        "min_tick": 0.25,
        "tick_val": 5.00,
        "multiplier": 20,
        "ccy": "USD",
        "uom": "index points",
        "session": "Sun-Fri 17:00-16:00 CT",
        "group_name": "Equity",
        "spot": 21140.0,
        "vol": 0.18,
        "tick": 0.25,
        "style": "quarterly",
    },
    {
        "product_code": "CL",
        "product_desc": "Crude Oil Futures",
        "asset_class": "Energy",
        "exch": "NYMEX",
        "exch_full": "New York Mercantile Exchange",
        "min_tick": 0.01,
        "tick_val": 10.00,
        "multiplier": 1000,
        "ccy": "USD",
        "uom": "USD/barrel",
        "session": "Sun-Fri 17:00-16:00 CT",
        "group_name": "Energy",
        "spot": 78.40,
        "vol": 0.32,
        "tick": 0.01,
        "style": "monthly",
    },
    {
        "product_code": "GC",
        "product_desc": "Gold Futures",
        "asset_class": "Metals",
        "exch": "COMEX",
        "exch_full": "Commodity Exchange",
        "min_tick": 0.10,
        "tick_val": 10.00,
        "multiplier": 100,
        "ccy": "USD",
        "uom": "USD/troy oz",
        "session": "Sun-Fri 17:00-16:00 CT",
        "group_name": "Metals",
        "spot": 2648.0,
        "vol": 0.16,
        "tick": 0.10,
        "style": "gold",
    },
    {
        "product_code": "ZB",
        "product_desc": "30-Year U.S. Treasury Bond",
        "asset_class": "Interest Rate",
        "exch": "CBOT",
        "exch_full": "Chicago Board of Trade",
        "min_tick": 0.03125,
        "tick_val": 31.25,
        "multiplier": 1000,
        "ccy": "USD",
        "uom": "points",
        "session": "Sun-Fri 17:00-16:00 CT",
        "group_name": "Rates",
        "spot": 116.25,
        "vol": 0.08,
        "tick": 0.03125,
        "style": "quarterly",
    },
]


def contract_schedule(style: str) -> list[date]:
    if style == "quarterly":
        months = [3, 6, 9, 12]
        years = [2026, 2027]
    elif style == "monthly":
        months = list(range(1, 13))
        years = [2026, 2027]
    else:  # gold-style even months plus some actives
        months = [2, 4, 6, 8, 12]
        years = [2026, 2027]

    expiries: list[date] = []
    for year in years:
        for month in months:
            expiries.append(third_friday(year, month))
    return [e for e in expiries if date(2026, 3, 1) <= e <= date(2027, 6, 30)]


def round_tick(price: float, tick: float) -> float:
    if tick <= 0:
        return round(price, 4)
    return round(round(price / tick) * tick, 6)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_underlyings() -> list[dict]:
    rows = []
    for item in UNDERLYINGS:
        rows.append(
            {
                "product_code": item["product_code"] if RNG.random() > 0.1 else f" {item['product_code']} ",
                "product_desc": item["product_desc"],
                "asset_class": item["asset_class"],
                "exch": item["exch"],
                "exch_full": item["exch_full"],
                "min_tick": item["min_tick"],
                "tick_val": item["tick_val"],
                "multiplier": item["multiplier"],
                "ccy": item["ccy"],
                "uom": item["uom"],
                "session": item["session"],
                "group_name": item["group_name"],
                "listed_status": dirty_bool(True),
                "src_system": RNG.choice(["cme_ref", "CME_REF", "exchange_master"]),
            }
        )
    return rows


def build_contracts() -> tuple[list[dict], list[dict]]:
    rows: list[dict] = []
    specs: list[dict] = []
    for item in UNDERLYINGS:
        for expiry in contract_schedule(item["style"]):
            symbol = globex_symbol(item["product_code"], expiry)
            contract = {
                "root": item["product_code"],
                "symbol": symbol,
                "expiry": expiry,
                "tick": item["tick"],
                "spot": item["spot"],
                "vol": item["vol"],
                "style": item["style"],
                "asset_class": item["asset_class"],
            }
            specs.append(contract)
            ltd = expiry
            fnd = "" if item["asset_class"] == "Equity Index" else (expiry - timedelta(days=7)).isoformat()
            rows.append(
                {
                    "contract_pk": f"{item['exch'].lower()}-{item['product_code'].lower()}-{MONTH_CODES[expiry.month].lower()}-{expiry.year}",
                    "globex": dirty_symbol(symbol) if RNG.random() < 0.2 else symbol,
                    "product_code": item["product_code"] if RNG.random() > 0.15 else item["product_code"].lower(),
                    "month_ltr": MONTH_CODES[expiry.month],
                    "yr": expiry.year if RNG.random() > 0.1 else str(expiry.year)[-2:],
                    "ltd": dirty_date(ltd),
                    "fnd": fnd,
                    "settle_type": "financial" if item["asset_class"] in {"Equity Index", "Interest Rate"} else "physical",
                    "exch": item["exch"],
                    "multiplier": item["multiplier"],
                    "tick": item["min_tick"],
                    "status": dirty_bool(expiry >= AS_OF - timedelta(days=40)),
                    "last_updated": datetime(2026, 8, 14, 21, 15, 0).isoformat(),
                }
            )
    return rows, specs


def path_for(root: str, days: list[date], start_price: float, annual_vol: float, tick: float) -> dict[date, float]:
    prices: dict[date, float] = {}
    price = start_price
    dt = 1 / 252
    for d in days:
        shock = RNG.gauss(0, 1)
        drift = 0.04 if root != "CL" else -0.02
        price = max(tick * 4, price * (1 + drift * dt + annual_vol * (dt**0.5) * shock))
        # Inventory-style crude spike for the quality/unusual-activity demo.
        if root == "CL" and d == date(2026, 7, 15):
            price *= 1.045
        prices[d] = round_tick(price, tick)
    return prices


def term_premium(root: str, nearby_rank: int) -> float:
    if root == "CL":
        return -0.0045 * nearby_rank  # backwardation
    if root == "ZB":
        return 0.0008 * nearby_rank
    return 0.0018 * nearby_rank  # mild contango


def live_contracts_on(specs: list[dict], root: str, market_date: date) -> list[dict]:
    live = [c for c in specs if c["root"] == root and c["expiry"] >= market_date]
    return sorted(live, key=lambda c: (c["expiry"], c["symbol"]))


def build_prices(specs: list[dict], days: list[date], spots: dict[str, dict[date, float]]) -> list[dict]:
    by_root: dict[str, list[dict]] = {}
    for spec in specs:
        by_root.setdefault(spec["root"], []).append(spec)

    rows: list[dict] = []

    for d in days:
        for root, contracts in by_root.items():
            live = live_contracts_on(contracts, root, d)
            if not live:
                continue
            front = live[0]
            front_px = spots[root][d]
            for rank, contract in enumerate(live, start=1):
                dte = (contract["expiry"] - d).days
                px = round_tick(front_px * (1 + term_premium(root, rank - 1)), contract["tick"])
                # Roll: front-month activity fades inside 10 DTE, next month absorbs it.
                roll = 1.0
                if rank == 1 and dte <= 10:
                    roll = max(0.25, dte / 10)
                elif rank == 2 and (front["expiry"] - d).days <= 10:
                    roll = 1.0 + (10 - (front["expiry"] - d).days) / 10
                base_vol = {"ES": 1_450_000, "NQ": 620_000, "CL": 410_000, "GC": 180_000, "ZB": 95_000}[root]
                volume = int(base_vol * (0.62** (rank - 1)) * roll * RNG.uniform(0.82, 1.18))
                oi = int(volume * RNG.uniform(1.15, 1.85) * (0.70 ** (rank - 1)))
                if root == "CL" and d == date(2026, 6, 12) and rank == 1:
                    volume = int(volume * 3.4)
                high = round_tick(px * RNG.uniform(1.001, 1.012), contract["tick"])
                low = round_tick(px * RNG.uniform(0.988, 0.999), contract["tick"])
                open_px = round_tick(px * RNG.uniform(0.995, 1.005), contract["tick"])
                row = {
                    "trade_dt": dirty_date(d),
                    "globex_sym": dirty_symbol(contract["symbol"]),
                    "px_open": dirty_number(open_px),
                    "px_high": dirty_number(max(high, open_px, px)),
                    "px_low": dirty_number(min(low, open_px, px)),
                    "px_settle": dirty_number(px),
                    "vol": dirty_number(volume, as_int=True),
                    "oi": dirty_number(oi, as_int=True),
                    "settle_flag": RNG.choice(["FINAL", "final", "Final"]),
                    "file_name": f"cme_settle_{d.strftime('%Y%m%d')}.csv",
                    "load_ts": datetime(2026, 8, 17, 6, 40, 0).isoformat(timespec="seconds"),
                }
                rows.append(row)
                if RNG.random() < 0.015:
                    dup = dict(row)
                    dup["load_ts"] = datetime(2026, 8, 17, 6, 41, 12).isoformat(timespec="seconds")
                    rows.append(dup)
    return rows


def option_expiries(root: str) -> list[date]:
    if root == "ES":
        return [
            date(2026, 8, 21),
            date(2026, 8, 28),
            date(2026, 9, 18),
            date(2026, 10, 16),
            date(2026, 12, 18),
        ]
    return [
        date(2026, 8, 19),
        date(2026, 9, 16),
        date(2026, 10, 14),
        date(2026, 11, 18),
    ]


def strike_grid(root: str, spot: float) -> list[float]:
    if root == "ES":
        center = round(spot / 50) * 50
        return [center + 50 * i for i in range(-10, 11)]
    center = round(spot)
    return [float(center + i) for i in range(-10, 11)]


def build_options(days: list[date], spots: dict[str, dict[date, float]]) -> list[dict]:
    option_days = [d for d in days if d >= date(2026, 7, 20)]
    rows: list[dict] = []
    for root in ("ES", "CL"):
        meta = next(item for item in UNDERLYINGS if item["product_code"] == root)
        for d in option_days:
            spot = spots[root][d]
            for expiry in option_expiries(root):
                if expiry <= d:
                    continue
                dte = max((expiry - d).days, 1)
                t = dte / 365
                for strike in strike_grid(root, spot):
                    moneyness = (strike - spot) / spot
                    for cp in ("C", "P"):
                        # Vendor-supplied IV/delta: sourced fields, not a pricing engine.
                        skew = 0.55 * max(0.0, -moneyness) if cp == "P" else 0.18 * max(0.0, moneyness)
                        iv = max(0.08, meta["vol"] * (0.85 + 0.9 * abs(moneyness) + skew))
                        intrinsic = max(0.0, (spot - strike) if cp == "C" else (strike - spot))
                        time_value = spot * iv * (t**0.5) * 0.35
                        mid = max(meta["tick"], intrinsic + time_value)
                        spread = max(meta["tick"], mid * (0.008 + 0.04 * abs(moneyness) + 0.01 * (dte / 120)))
                        bid = round_tick(max(meta["tick"], mid - spread / 2), meta["tick"])
                        ask = round_tick(mid + spread / 2, meta["tick"])
                        last = round_tick((bid + ask) / 2, meta["tick"])
                        atm_weight = max(0.05, 1.2 - abs(moneyness) * 14)
                        expiry_weight = max(0.15, 1.1 - dte / 180)
                        round_strike = 1.35 if (root == "ES" and strike % 100 == 0) or (root == "CL" and strike % 5 == 0) else 1.0
                        volume = int(18000 * atm_weight * expiry_weight * round_strike * RNG.uniform(0.4, 1.3))
                        if cp == "P":
                            volume = int(volume * 1.12)
                        oi = int(volume * RNG.uniform(2.2, 4.8) * (1.15 if cp == "P" else 1.0))
                        delta = 0.5 + (0.5 if cp == "C" else -0.5) * (1 / (1 + abs(moneyness) * 18))
                        delta = round(delta if cp == "C" else -abs(delta), 3)
                        cp_raw = cp if RNG.random() > 0.12 else ("Call" if cp == "C" else RNG.choice(["Put", "put", "P "]))
                        rows.append(
                            {
                                "as_of": dirty_date(d),
                                "und": root if RNG.random() > 0.08 else root.lower(),
                                "exp_dt": dirty_date(expiry),
                                "strike_px": dirty_number(strike),
                                "put_call": cp_raw,
                                "bid_px": dirty_number(bid),
                                "ask_px": dirty_number(ask),
                                "last_px": dirty_number(last),
                                "trd_vol": dirty_number(volume, as_int=True),
                                "oi": dirty_number(oi, as_int=True),
                                "imp_vol": dirty_number(round(iv, 4)),
                                "delta": dirty_number(delta),
                                "opt_root": root,
                                "exch": meta["exch"],
                                "snap_id": f"snap-{d.strftime('%Y%m%d')}-{root.lower()}",
                                "rec_hash": f"{root}-{expiry:%Y%m%d}-{int(strike)}-{cp}-{d:%Y%m%d}",
                            }
                        )
                        if RNG.random() < 0.008:
                            dup = dict(rows[-1])
                            dup["snap_id"] = dup["snap_id"] + "-retry"
                            rows.append(dup)
    return rows


def generate() -> dict[str, Path]:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    days = trading_days(START, AS_OF)
    underlying_rows = build_underlyings()
    contract_rows, specs = build_contracts()
    spots = {
        item["product_code"]: path_for(item["product_code"], days, item["spot"], item["vol"], item["tick"])
        for item in UNDERLYINGS
    }
    price_rows = build_prices(specs, days, spots)
    option_rows = build_options(days, spots)

    paths = {
        "underlyings": RAW_DIR / "raw_underlyings.csv",
        "futures_contracts": RAW_DIR / "raw_futures_contracts.csv",
        "futures_prices": RAW_DIR / "raw_futures_prices.csv",
        "options_chain": RAW_DIR / "raw_options_chain.csv",
    }
    write_csv(
        paths["underlyings"],
        underlying_rows,
        [
            "product_code",
            "product_desc",
            "asset_class",
            "exch",
            "exch_full",
            "min_tick",
            "tick_val",
            "multiplier",
            "ccy",
            "uom",
            "session",
            "group_name",
            "listed_status",
            "src_system",
        ],
    )
    write_csv(
        paths["futures_contracts"],
        contract_rows,
        [
            "contract_pk",
            "globex",
            "product_code",
            "month_ltr",
            "yr",
            "ltd",
            "fnd",
            "settle_type",
            "exch",
            "multiplier",
            "tick",
            "status",
            "last_updated",
        ],
    )
    write_csv(
        paths["futures_prices"],
        price_rows,
        [
            "trade_dt",
            "globex_sym",
            "px_open",
            "px_high",
            "px_low",
            "px_settle",
            "vol",
            "oi",
            "settle_flag",
            "file_name",
            "load_ts",
        ],
    )
    write_csv(
        paths["options_chain"],
        option_rows,
        [
            "as_of",
            "und",
            "exp_dt",
            "strike_px",
            "put_call",
            "bid_px",
            "ask_px",
            "last_px",
            "trd_vol",
            "oi",
            "imp_vol",
            "delta",
            "opt_root",
            "exch",
            "snap_id",
            "rec_hash",
        ],
    )
    return paths


if __name__ == "__main__":
    written = generate()
    for name, path in written.items():
        print(f"{name}: {path} ({path.stat().st_size} bytes)")
