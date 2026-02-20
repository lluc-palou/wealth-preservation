"""
Raw Data Collection Pipeline — Fiat Debasement & Wealth Allocation Study

This script pulls all raw data required to analyse fiat debasement and compare purchasing power
preservation across BTC, gold, equities, and USD cash. It collects macro series from FRED and
market price series from yfinance, saves each as an individual CSV in raw_data/, and records
pull metadata in raw_data/metadata.json for full reproducibility.
"""

import os
import json
import time
import pandas as pd
import yfinance as yf
from fredapi import Fred
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, Optional


# ── Configuration ─────────────────────────────────────────────────────────────

# Earliest date where BTC data is meaningful and macro coverage is solid
START_DATE = "2010-01-01"
END_DATE   = datetime.today().strftime("%Y-%m-%d")

# Output directory
RAW_DATA_DIR = "raw_data"
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# FRED API key — set as environment variable FRED_API_KEY
load_dotenv()
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# FRED series to pull: (series_id, output_filename, human_readable_name, frequency)
FRED_SERIES = [
    ("M2SL",     "m2_monthly.csv",        "M2 Money Supply",              "monthly"),
    ("CPIAUCSL", "cpi_monthly.csv",        "CPI All Urban Consumers",      "monthly"),
    ("GDP",      "gdp_quarterly.csv",      "Gross Domestic Product",       "quarterly"),
    ("DFF",      "fed_funds_daily.csv",    "Federal Funds Effective Rate", "daily"),
    ("DFII10",   "tips_10y_daily.csv",     "10-Year TIPS Real Yield",      "daily"),
]

# yfinance tickers to pull: (ticker, output_filename, human_readable_name, frequency)
YFINANCE_TICKERS = [
    ("BTC-USD", "btc_usd_daily.csv",  "Bitcoin USD Price",  "daily"),
    ("^GSPC",   "sp500_daily.csv",    "S&P 500 Index",      "daily"),
    ("GC=F",    "gold_daily.csv",     "Gold Futures Price", "daily"),
]


# ── Helper Functions ───────────────────────────────────────────────────────────

def print_series_summary(name: str, series: pd.Series, source: str) -> None:
    """
    Prints a diagnostic summary for a pulled series including date range, observation count and NaN count.

    Args:
        name: Human-readable name of the series
        series: Pulled pandas Series with DatetimeIndex
        source: Source identifier string (e.g. 'FRED', 'yfinance')

    Returns:
        None
    """
    n_obs  = len(series)
    n_nans = series.isna().sum()
    date_min = series.index.min().strftime("%Y-%m-%d") if not series.empty else "N/A"
    date_max = series.index.max().strftime("%Y-%m-%d") if not series.empty else "N/A"

    print(
        f"  [{source}] {name}\n"
        f"    Range: {date_min} → {date_max} | Obs: {n_obs} | NaNs: {n_nans}"
    )


def build_metadata_entry(
    name: str,
    source: str,
    identifier: str,
    frequency: str,
    filename: str,
    series: pd.Series,
    pulled_at: str
) -> Dict[str, Any]:
    """
    Builds a metadata dictionary entry for a single pulled series.

    Args:
        name: Human-readable series name
        source: Data source ('FRED' or 'yfinance')
        identifier: FRED series ID or yfinance ticker symbol
        frequency: Data frequency string ('daily', 'monthly', 'quarterly')
        filename: Output CSV filename
        series: The pulled pandas Series
        pulled_at: ISO timestamp string of when the pull was executed

    Returns:
        Dictionary with full metadata for the series
    """
    return {
        "name":        name,
        "source":      source,
        "identifier":  identifier,
        "frequency":   frequency,
        "filename":    filename,
        "date_start":  series.index.min().strftime("%Y-%m-%d") if not series.empty else None,
        "date_end":    series.index.max().strftime("%Y-%m-%d") if not series.empty else None,
        "n_obs":       len(series),
        "n_nans":      int(series.isna().sum()),
        "pulled_at":   pulled_at
    }


def save_series_to_csv(series: pd.Series, filename: str, column_name: str) -> None:
    """
    Saves a pandas Series to CSV in the raw_data directory with a named value column.

    Args:
        series: Time series with DatetimeIndex to save
        filename: Target filename (not full path)
        column_name: Label to use for the value column in the CSV

    Returns:
        None
    """
    output_path = os.path.join(RAW_DATA_DIR, filename)
    df = series.rename(column_name).to_frame()
    df.index.name = "date"
    df.to_csv(output_path)


# ── FRED Collection ────────────────────────────────────────────────────────────

def fetch_all_fred_series(fred_client: Fred, pulled_at: str) -> Dict[str, Any]:
    """
    Fetches all configured FRED series, saves each to CSV, and returns metadata entries.

    Args:
        fred_client: Authenticated fredapi.Fred client instance
        pulled_at: ISO timestamp string used to tag all metadata entries

    Returns:
        Dictionary mapping filename to metadata entry for each successfully pulled series
    """
    metadata: Dict[str, Any] = {}

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Pulling FRED series...")

    for series_id, filename, name, frequency in FRED_SERIES:
        try:
            series = fred_client.get_series(series_id, observation_start=START_DATE, observation_end=END_DATE)
            series.index = pd.to_datetime(series.index)

            print_series_summary(name, series, "FRED")
            save_series_to_csv(series, filename, series_id)

            metadata[filename] = build_metadata_entry(
                name=name,
                source="FRED",
                identifier=series_id,
                frequency=frequency,
                filename=filename,
                series=series,
                pulled_at=pulled_at
            )

        except Exception as e:
            print(f"  [FRED] ERROR pulling {name} ({series_id}): {e}")

        # Respect FRED rate limits
        time.sleep(0.5)

    return metadata


# ── yfinance Collection ────────────────────────────────────────────────────────

def fetch_all_yfinance_tickers(pulled_at: str) -> Dict[str, Any]:
    """
    Fetches all configured yfinance tickers using adjusted close prices, saves each to CSV, and returns metadata entries.

    Args:
        pulled_at: ISO timestamp string used to tag all metadata entries

    Returns:
        Dictionary mapping filename to metadata entry for each successfully pulled ticker
    """
    metadata: Dict[str, Any] = {}

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Pulling yfinance tickers...")

    for ticker, filename, name, frequency in YFINANCE_TICKERS:
        try:
            raw = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False, auto_adjust=True)

            if raw.empty:
                print(f"  [yfinance] WARNING: No data returned for {ticker}")
                continue

            # Use Close price as the primary price series
            series = raw["Close"].squeeze()
            series.index = pd.to_datetime(series.index)
            # Flatten MultiIndex column name if present
            series.name = ticker

            print_series_summary(name, series, "yfinance")
            save_series_to_csv(series, filename, ticker)

            metadata[filename] = build_metadata_entry(
                name=name,
                source="yfinance",
                identifier=ticker,
                frequency=frequency,
                filename=filename,
                series=series,
                pulled_at=pulled_at
            )

        except Exception as e:
            print(f"  [yfinance] ERROR pulling {name} ({ticker}): {e}")

    return metadata


# ── Metadata Persistence ───────────────────────────────────────────────────────

def save_metadata(metadata: Dict[str, Any], pulled_at: str) -> None:
    """
    Saves the full metadata dictionary to raw_data/metadata.json, including a top-level pull summary.

    Args:
        metadata: Dictionary mapping filenames to their metadata entries
        pulled_at: ISO timestamp string for the pull session

    Returns:
        None
    """
    metadata_path = os.path.join(RAW_DATA_DIR, "metadata.json")

    output = {
        "pull_timestamp": pulled_at,
        "start_date":     START_DATE,
        "end_date":       END_DATE,
        "n_series":       len(metadata),
        "series":         metadata
    }

    with open(metadata_path, "w") as f:
        json.dump(output, f, indent=4)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Metadata saved → {metadata_path}")


# ── Entry Point ────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Orchestrates the full data collection pipeline: validates config, pulls FRED and yfinance
    series, saves CSVs to raw_data/, and writes metadata.json.

    Args:
        None

    Returns:
        None
    """
    pulled_at = datetime.now().isoformat()

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting raw data collection pipeline")
    print(f"  Window: {START_DATE} → {END_DATE}")
    print(f"  Output: {RAW_DATA_DIR}/")

    # Validate FRED key before starting
    if not FRED_API_KEY:
        raise EnvironmentError(
            "FRED_API_KEY environment variable not set. "
            "Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html"
        )

    fred_client = Fred(api_key=FRED_API_KEY)

    # Pull all series
    fred_metadata     = fetch_all_fred_series(fred_client, pulled_at)
    yfinance_metadata = fetch_all_yfinance_tickers(pulled_at)

    # Merge metadata and persist
    full_metadata = {**fred_metadata, **yfinance_metadata}
    save_metadata(full_metadata, pulled_at)

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Pipeline complete — {len(full_metadata)} series saved to {RAW_DATA_DIR}/")


if __name__ == "__main__":
    main()