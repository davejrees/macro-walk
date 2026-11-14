import json
import yfinance as yf
from datetime import datetime, timezone

TICKERS = {
    # Tab 1: Physical & Supply Chain
    "brent": "BZ=F",          # Brent Crude ($/bbl)
    "natgas": "NG=F",         # Natural Gas ($/MMBtu)
    "zim": "ZIM",             # ZIM Container Shipping (Spot freight proxy)
    "bdry": "BDRY",           # Breakwave Dry Bulk Shipping ETF
    "copper": "HG=F",         # COMEX Copper ($/lb)
    "wheat": "ZW=F",          # CBOT Wheat (cents/bushel)

    # Tab 2: Rates, FX & Inflation
    "gbpusd": "GBPUSD=X",     # GBP / USD
    "uk10y": "^TMBMKGB-10Y",  # UK 10-Year Gilt Yield
    "us10y": "^TNX",          # US 10-Year Treasury Yield
    "gold": "GC=F",           # Gold Futures ($/oz)

    # Tab 3: Liquidity & Risk
    "ndx": "^NDX",            # NASDAQ-100 (Mag 7 & tech liquidity)
    "hyg": "HYG",             # High Yield Corporate Bond ETF
    "vix": "^VIX"             # CBOE Volatility Index
}

def fetch_macro_series():
    output = {
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "series": {}
    }

    for key, sym in TICKERS.items():
        try:
            ticker = yf.Ticker(sym)
            hist = ticker.history(period="1mo")
            if hist.empty:
                continue

            prices = []
            for date, row in hist.iterrows():
                val = float(row["Close"])
                # Safeguard: only divide ^TNX if Yahoo ever reverts to x10 quoting
                if sym == "^TNX" and val > 20:
                    val = val / 10.0
                prices.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "price": round(val, 3)
                })

            if prices:
                current = prices[-1]["price"]
                prev = prices[-2]["price"] if len(prices) > 1 else current
                delta_pct = round(((current - prev) / prev) * 100, 2)

                output["series"][key] = {
                    "current": current,
                    "delta_pct": delta_pct,
                    "history": prices
                }
        except Exception as e:
            print(f"Error fetching {key} ({sym}): {e}")

    # Calculate Copper-to-Gold Ratio (Growth vs. Fear)
    if "copper" in output["series"] and "gold" in output["series"]:
        c_hist = {p["date"]: p["price"] for p in output["series"]["copper"]["history"]}
        g_hist = {p["date"]: p["price"] for p in output["series"]["gold"]["history"]}
        common_dates = sorted(set(c_hist.keys()) & set(g_hist.keys()))

        ratio_prices = []
        for d in common_dates:
            if g_hist[d] > 0:
                # Scaled x1000 for clean readability (e.g. ~2.35)
                ratio_val = (c_hist[d] / g_hist[d]) * 1000
                ratio_prices.append({
                    "date": d,
                    "price": round(ratio_val, 3)
                })

        if ratio_prices:
            curr_r = ratio_prices[-1]["price"]
            prev_r = ratio_prices[-2]["price"] if len(ratio_prices) > 1 else curr_r
            delta_r = round(((curr_r - prev_r) / prev_r) * 100, 2)
            output["series"]["cu_au"] = {
                "current": curr_r,
                "delta_pct": delta_r,
                "history": ratio_prices
            }

    return output

if __name__ == "__main__":
    data = fetch_macro_series()
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Successfully generated v1.1 data.json")
