import yfinance as yf
import json
import pandas as pd
from pandas import Timestamp  

# ---------------------------------------------------------------------
# Task 3: Create Utility Functions to Fetch, Analyze, and Format Stock Market Data
# ---------------------------------------------------------------------

def history_to_dataframe(history_json):
    if not history_json:
        return None
    try:
        # Load the data if it’s a JSON string; otherwise, use it directly
        data = history_json if isinstance(history_json, list) else json.loads(history_json)
        
        # Convert the list/dict data into a DataFrame
        df = pd.DataFrame(data)
        
        # Explicitly set 'Date' as index and convert it to a datetime type
        if 'Date' in df.columns:
            df.set_index('Date', inplace=True)
            df.index = pd.to_datetime(df.index, errors="coerce")
        
        # Ensure the data is sorted chronologically
        df.sort_index(inplace=True)
        return df
    except Exception as e:
        # Log errors during DataFrame conversion
        print(f"[history_to_dataframe] Error: {e}")
        return None

def get_stock_data(ticker):
    try:
        # Create a Ticker object for the given symbol
        stock = yf.Ticker(ticker)

        # --- 1. Fetch 30 days of daily price history ---
        hist_df = stock.history(period="30d", interval="1d") 
        
        price = "N/A"
        change_pct = "N/A"

        # Compute the latest closing price and daily percentage change
        if not hist_df.empty:
            price_val = hist_df["Close"].iloc[-1]
            
            if len(hist_df) > 1:
                prev_close = hist_df["Close"].iloc[-2]
                
                if prev_close and prev_close != 0:
                    change_pct_val = ((price_val - prev_close) / prev_close * 100)
                    change_pct = round(change_pct_val, 2)
                
            price = round(price_val, 2)
        
        # --- 2. Retrieve additional metadata from stock.info ---
        info = stock.info
        
        # Helper function: safely extract numeric values and round them
        def safe_get_round(key, default="N/A"):
            val = info.get(key)
            return round(val, 2) if isinstance(val, (int, float)) else default

        # Return the compiled stock information as a dictionary
        return {
            "ticker": ticker.upper(),
            "company": info.get("longName", info.get("shortName", ticker.upper())),
            "price": price,
            "change_pct": change_pct,
            "pe_ratio": safe_get_round("trailingPE"),
            "beta": safe_get_round("beta"),
            "sector": info.get("sector", info.get("industry", "N/A")),
            # Include full 30-day price history for chart visualization
            "history_json": hist_df.reset_index().to_dict(orient="records") if not hist_df.empty else None
        }

    except Exception as e:
        # Log any critical error during stock data retrieval
        print(f"[get_stock_data] CRITICAL FAILURE for {ticker}: {e}")
        
        # Return fallback values to maintain application stability
        return {
            "ticker": ticker.upper(),
            "company": ticker.upper(),
            "price": "N/A",
            "change_pct": "N/A",
            "pe_ratio": "N/A",
            "beta": "N/A",
            "sector": "N/A",
            "history_json": None
        }