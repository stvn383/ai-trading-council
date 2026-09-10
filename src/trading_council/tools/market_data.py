import json
import os
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
from agents import function_tool

load_dotenv()

CACHE_FILE = Path("stock_data_cache.json")
CACHE_DURATION = timedelta(hours=24)
API_CALL_INTERVAL = 1.1
TICKER_ALIASES = {
    "BRK.B": "BRK-B",
}

_market_data_lock = threading.Lock()
_last_api_call = 0.0


def load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}

    with open(CACHE_FILE, "r") as file:
        return json.load(file)


def save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w") as file:
        json.dump(cache, file, indent=2)


def fetch_stock_data(ticker: str) -> dict:
    global _last_api_call

    ticker = ticker.upper()
    ticker = TICKER_ALIASES.get(ticker, ticker)
    
    # First cache check — fast path
    cache = load_cache()

    if ticker in cache:
        cached_time = datetime.fromisoformat(cache[ticker]["timestamp"])

        if datetime.now() - cached_time < CACHE_DURATION:
            print(f"Using cached data for {ticker}")
            return cache[ticker]["data"]

    # Only one uncached market-data request can happen at a time
    with _market_data_lock:

        # Check cache again in case another agent fetched it
        # while this request was waiting for the lock
        cache = load_cache()

        if ticker in cache:
            cached_time = datetime.fromisoformat(cache[ticker]["timestamp"])

            if datetime.now() - cached_time < CACHE_DURATION:
                print(f"Using cached data for {ticker}")
                return cache[ticker]["data"]

        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

        if not api_key:
            raise ValueError("ALPHA_VANTAGE_API_KEY is not set")

        url = "https://www.alphavantage.co/query"

        params = {
            "function": "OVERVIEW",
            "symbol": ticker,
            "apikey": api_key,
        }

        # Enforce spacing between Alpha Vantage requests
        elapsed = time.monotonic() - _last_api_call

        if elapsed < API_CALL_INTERVAL:
            time.sleep(API_CALL_INTERVAL - elapsed)

        print(f"Calling Alpha Vantage for {ticker}")

        response = requests.get(
            url,
            params=params,
            timeout=10,
        )

        _last_api_call = time.monotonic()

        response.raise_for_status()

        data = response.json()

        if not data:
            raise ValueError(f"No data returned for {ticker}")

        if "Note" in data:
            raise RuntimeError(
                f"Alpha Vantage rate limit: {data['Note']}"
            )

        if "Information" in data:
            raise RuntimeError(
                f"Alpha Vantage message: {data['Information']}"
            )

        if "Error Message" in data:
            raise ValueError(f"Invalid ticker: {ticker}")

        cache[ticker] = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }

        save_cache(cache)

        return data


@function_tool
def get_stock_data(ticker: str) -> dict:
    """
    Get fundamental stock data from Alpha Vantage.

    Args:
        ticker: Stock ticker symbol, such as NVDA or MSFT.
    """
    return fetch_stock_data(ticker)