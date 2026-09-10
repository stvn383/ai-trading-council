import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv
from agents import function_tool

load_dotenv()

CACHE_FILE = Path("stock_data_cache.json")
CACHE_DURATION = timedelta(hours=24)


def load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}

    with open(CACHE_FILE, "r") as file:
        return json.load(file)


def save_cache(cache: dict) -> None:
    with open(CACHE_FILE, "w") as file:
        json.dump(cache, file, indent=2)


def fetch_stock_data(ticker: str) -> dict:
    ticker = ticker.upper()

    cache = load_cache()

    if ticker in cache:
        cached_time = datetime.fromisoformat(cache[ticker]["timestamp"])

        if datetime.now() - cached_time < CACHE_DURATION:
            print(f"Using cached data for {ticker}")
            return cache[ticker]["data"]

    print(f"Calling Alpha Vantage for {ticker}")

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY is not set")

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": api_key,
    }

    time.sleep(1.1)

    response = requests.get(url, params=params, timeout=10)

    print("HTTP status:", response.status_code)
    print("Raw response:", response.text)

    response.raise_for_status()

    data = response.json()

    if not data:
        raise ValueError(f"No data returned for {ticker}")

    if "Note" in data:
        raise RuntimeError(f"Alpha Vantage rate limit: {data['Note']}")

    if "Information" in data:
        raise RuntimeError(f"Alpha Vantage message: {data['Information']}")

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