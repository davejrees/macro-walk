import json
import yfinance as yf
from datetime import datetime

# Map of assets to their Yahoo Finance tickers
TICKERS = {
    "brent": "BZ=F",        # Brent Crude ($/bbl)
    "copper": "HG=F",       # COMEX Copper ($/lb)
    "wheat": "ZW=F",        # CBOT Wheat (cents/bushel)
    "gbpusd": "GBPUSD=X",   # GBP / USD
    "us10y": "^TNX",        # US 10-Year Treasury Yield (quoted x10)
    "uk10y": "^TMBMKGB-10Y",# UK 10-Year Gilt Yield
    "hyg": "HYG"            # High Yield ETF (proxy for credit stress)
}

def fetch_macro_series():
    output = {
        "last_updated": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC"),
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
                # Adjust US 10Y CBOE formatting (e.g. 44.5 -> 4.45%)
                if sym == "^TNX":
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

    return output

if __name__ == "__main__":
    data = fetch_macro_series()
    with open("data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("Successfully generated data.json")
