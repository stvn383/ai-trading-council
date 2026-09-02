import os
import requests
from dotenv import load_dotenv

load_dotenv()


def get_stock_data(ticker: str) -> dict:
    """
    Get fundamental data for a stock from Alpha Vantage.
    """

    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")

    if not api_key:
        raise ValueError("ALPHA_VANTAGE_API_KEY is not set")

    url = "https://www.alphavantage.co/query"

    params = {
        "function": "OVERVIEW",
        "symbol": ticker.upper(),
        "apikey": api_key,
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if not data:
        raise ValueError(f"No data returned for {ticker}")

    if "Note" in data:
        raise RuntimeError(f"Alpha Vantage rate limit: {data['Note']}")

    if "Error Message" in data:
        raise ValueError(f"Invalid ticker: {ticker}")

    return data

if __name__ == "__main__":
    data = get_stock_data("NVDA")
    print(data)