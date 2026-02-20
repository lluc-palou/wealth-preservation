"""
Raw Data Processing Pipeline — Fiat Debasement & Wealth Allocation Study

This script ingests the raw CSVs produced by fetch_raw_data.py, curates each series by aligning
to monthly frequency and clipping to the common BTC-constrained date range, engineers all analysis
features including asset returns, real cash return, debasement indicators and spread variables,
and produces a single clean rectangular dataframe saved to processed_data/analysis_df.csv.
The debasement indicators are standardized (z-score) and stored alongside raw values for use
in the EDA notebook.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Tuple
from scipy.interpolate import CubicSpline


# ── Configuration ─────────────────────────────────────────────────────────────

# BTC data starts meaningfully around late 2014 — all series are clipped to this
BTC_SERIES_START = "2014-01-01"

# Input and output directories
RAW_DATA_DIR       = "raw_data"
PROCESSED_DATA_DIR = "processed_data"
os.makedirs(PROCESSED_DATA_DIR, exist_ok=True)

# Debasement indicator column names used across multiple functions
DEBASEMENT_INDICATOR_COLUMNS = [
    "m2_yoy_pct",
    "cpi_yoy_pct",
    "real_m2_growth",
    "m2_to_gdp",
]


# ── Data Loading ───────────────────────────────────────────────────────────────

def load_raw_series(filename: str, value_column: str) -> pd.Series:
    """
    Loads a raw CSV from raw_data/ into a pandas Series with a parsed DatetimeIndex.

    Args:
        filename: CSV filename within raw_data/ directory
        value_column: Name of the value column to extract from the CSV

    Returns:
        pandas Series with DatetimeIndex sorted ascending, named after value_column
    """
    filepath = os.path.join(RAW_DATA_DIR, filename)
    df = pd.read_csv(filepath, index_col="date", parse_dates=True)
    series = df[value_column].sort_index()
    return series


def load_all_raw_series() -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series, pd.Series,
                                    pd.Series, pd.Series, pd.Series]:
    """
    Loads all eight raw series from raw_data/ and returns them as individual pandas Series.

    Args:
        None

    Returns:
        Tuple of (m2, cpi, gdp, fed_funds, tips_real_yield, btc, sp500, gold) as pandas Series
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Loading raw series from {RAW_DATA_DIR}/...")

    m2               = load_raw_series("m2_monthly.csv",     "M2SL")
    cpi              = load_raw_series("cpi_monthly.csv",    "CPIAUCSL")
    gdp              = load_raw_series("gdp_quarterly.csv",  "GDP")
    fed_funds        = load_raw_series("fed_funds_daily.csv","DFF")
    tips_real_yield  = load_raw_series("tips_10y_daily.csv", "DFII10")
    btc              = load_raw_series("btc_usd_daily.csv",  "BTC-USD")
    sp500            = load_raw_series("sp500_daily.csv",    "^GSPC")
    gold             = load_raw_series("gold_daily.csv",     "GC=F")

    print(f"  Loaded 8 raw series successfully")
    return m2, cpi, gdp, fed_funds, tips_real_yield, btc, sp500, gold


# ── Frequency Alignment ────────────────────────────────────────────────────────

def interpolate_gdp_to_monthly(gdp_quarterly: pd.Series) -> pd.Series:
    """
    Interpolates quarterly GDP series to monthly frequency using cubic spline interpolation,
    preserving the original quarterly anchor values exactly.

    Args:
        gdp_quarterly: Quarterly GDP series with DatetimeIndex

    Returns:
        Monthly GDP series with DatetimeIndex covering the same date range as input
    """
    # Build numeric timestamps for spline fitting
    gdp_clean = gdp_quarterly.dropna()
    numeric_timestamps = np.array([ts.timestamp() for ts in gdp_clean.index])
    gdp_values = gdp_clean.values

    spline = CubicSpline(numeric_timestamps, gdp_values)

    # Generate monthly date range spanning the quarterly series
    monthly_index = pd.date_range(
        start=gdp_clean.index.min(),
        end=gdp_clean.index.max(),
        freq="MS"
    )
    monthly_numeric_timestamps = np.array([ts.timestamp() for ts in monthly_index])
    interpolated_values = spline(monthly_numeric_timestamps)

    return pd.Series(interpolated_values, index=monthly_index, name="gdp_monthly")


def resample_daily_to_monthly_end(daily_series: pd.Series) -> pd.Series:
    """
    Resamples a daily series to monthly frequency by taking the last available observation
    of each month (month-end close), preserving price level semantics.

    Args:
        daily_series: Daily price or rate series with DatetimeIndex

    Returns:
        Monthly series with month-end DatetimeIndex
    """
    return daily_series.resample("ME").last()


def align_all_series_to_monthly(m2: pd.Series,
                                  cpi: pd.Series,
                                  gdp: pd.Series,
                                  fed_funds: pd.Series,
                                  tips_real_yield: pd.Series,
                                  btc: pd.Series,
                                  sp500: pd.Series,
                                  gold: pd.Series) -> pd.DataFrame:
    """
    Aligns all series to monthly frequency, clips to BTC_SERIES_START, performs an inner join
    on the monthly date index, and drops any remaining NaN rows to produce a clean rectangular frame.

    Args:
        m2: Monthly M2 money supply series
        cpi: Monthly CPI series
        gdp: Quarterly GDP series (will be interpolated inside this function)
        fed_funds: Daily Fed Funds rate series
        tips_real_yield: Daily 10-year TIPS real yield series
        btc: Daily BTC-USD price series
        sp500: Daily S&P 500 index series
        gold: Daily gold futures price series

    Returns:
        Clean monthly DataFrame with all series aligned, clipped and NaN-free
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Aligning all series to monthly frequency...")

    # Interpolate GDP quarterly → monthly
    gdp_monthly = interpolate_gdp_to_monthly(gdp)

    # Resample daily series to month-end
    fed_funds_monthly   = resample_daily_to_monthly_end(fed_funds).rename("fed_funds_rate")
    tips_monthly        = resample_daily_to_monthly_end(tips_real_yield).rename("tips_real_yield_10y")
    btc_monthly         = resample_daily_to_monthly_end(btc).rename("btc_price")
    sp500_monthly       = resample_daily_to_monthly_end(sp500).rename("sp500_price")
    gold_monthly        = resample_daily_to_monthly_end(gold).rename("gold_price")

    # Standardise monthly series index names for clean join
    m2_monthly  = m2.resample("ME").last().rename("m2")
    cpi_monthly = cpi.resample("ME").last().rename("cpi")

    # Align GDP monthly index to month-end to match other series
    gdp_monthly.index = gdp_monthly.index + pd.offsets.MonthEnd(0)

    # Inner join all series on monthly date index
    combined_df = pd.concat(
        [m2_monthly, cpi_monthly, gdp_monthly, fed_funds_monthly,
         tips_monthly, btc_monthly, sp500_monthly, gold_monthly],
        axis=1,
        join="inner"
    )

    # Clip to BTC data start and drop any residual NaN rows
    combined_df = combined_df.loc[BTC_SERIES_START:]
    rows_before_dropna = len(combined_df)
    combined_df = combined_df.dropna()
    rows_dropped = rows_before_dropna - len(combined_df)

    print(f"  Monthly frame shape after alignment: {combined_df.shape}")
    print(f"  Date range: {combined_df.index.min().date()} → {combined_df.index.max().date()}")
    print(f"  Rows dropped due to NaNs: {rows_dropped}")

    return combined_df


# ── Feature Engineering ────────────────────────────────────────────────────────

def compute_debasement_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes the four raw debasement indicator features from M2, CPI and GDP columns,
    then drops the intermediate raw level columns no longer needed.

    Args:
        df: Aligned monthly DataFrame containing m2, cpi, gdp_monthly columns

    Returns:
        DataFrame with debasement indicator columns added and raw level columns removed
    """
    # M2 year-over-year percentage change — primary money supply expansion signal
    df["m2_yoy_pct"] = df["m2"].pct_change(periods=12) * 100

    # CPI year-over-year percentage change — realized inflation / purchasing power loss
    df["cpi_yoy_pct"] = df["cpi"].pct_change(periods=12) * 100

    # Real M2 growth — excess monetary expansion beyond inflation
    df["real_m2_growth"] = df["m2_yoy_pct"] - df["cpi_yoy_pct"]

    # M2 to GDP ratio — structural debasement: how much money exists relative to economy size
    df["m2_to_gdp"] = df["m2"] / df["gdp_monthly"]

    # Drop intermediate raw level columns — no longer needed after feature derivation
    df = df.drop(columns=["m2", "cpi", "gdp_monthly"])

    return df


def compute_asset_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes monthly log returns for BTC, S&P 500 and gold from their price level columns,
    then drops the raw price level columns.

    Args:
        df: Monthly DataFrame containing btc_price, sp500_price, gold_price columns

    Returns:
        DataFrame with monthly log return columns added and raw price columns removed
    """
    # Log returns capture compounding correctly and are additive across time
    df["btc_return_monthly"]   = np.log(df["btc_price"]   / df["btc_price"].shift(1))
    df["sp500_return_monthly"] = np.log(df["sp500_price"] / df["sp500_price"].shift(1))
    df["gold_return_monthly"]  = np.log(df["gold_price"]  / df["gold_price"].shift(1))

    # Drop raw price levels — returns are the relevant quantity for comparison
    df = df.drop(columns=["btc_price", "sp500_price", "gold_price"])

    return df


def compute_cash_real_return(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes the monthly real return of holding USD cash as Fed Funds rate minus CPI YoY,
    annualized rate converted to a monthly figure.

    Args:
        df: Monthly DataFrame containing fed_funds_rate and cpi_yoy_pct columns

    Returns:
        DataFrame with cash_real_return_monthly column added
    """
    # Annualized real rate divided by 12 gives approximate monthly real cash return
    df["cash_real_return_monthly"] = (df["fed_funds_rate"] - df["cpi_yoy_pct"]) / 12 / 100

    return df


def compute_spread_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes return spread features representing outperformance of each asset over real USD cash,
    which directly answers the wealth allocation question.

    Args:
        df: Monthly DataFrame containing asset return and cash_real_return_monthly columns

    Returns:
        DataFrame with three spread columns added measuring excess return over real cash
    """
    # Positive spread = asset beat holding USD cash in real purchasing power terms
    df["btc_vs_cash_real_spread"]   = df["btc_return_monthly"]   - df["cash_real_return_monthly"]
    df["gold_vs_cash_real_spread"]  = df["gold_return_monthly"]  - df["cash_real_return_monthly"]
    df["sp500_vs_cash_real_spread"] = df["sp500_return_monthly"] - df["cash_real_return_monthly"]

    return df


def standardize_debasement_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds z-score standardized versions of the four debasement indicator columns,
    prefixed with 'z_', computed over the full available sample.

    Args:
        df: Monthly DataFrame containing the four raw debasement indicator columns

    Returns:
        DataFrame with four additional z-score standardized debasement columns added
    """
    for column_name in DEBASEMENT_INDICATOR_COLUMNS:
        column_mean   = df[column_name].mean()
        column_std    = df[column_name].std()
        standardized_column_name = f"z_{column_name}"
        df[standardized_column_name] = (df[column_name] - column_mean) / column_std

    return df


def compute_zscore_composite_debasement_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes the z-score composite debasement score by averaging the four standardized
    debasement indicator columns into a single scalar per month.

    Args:
        df: Monthly DataFrame containing z_m2_yoy_pct, z_cpi_yoy_pct,
            z_real_m2_growth, z_m2_to_gdp columns

    Returns:
        DataFrame with zscore_composite_debasement_score column added
    """
    standardized_columns = [f"z_{col}" for col in DEBASEMENT_INDICATOR_COLUMNS]
    df["zscore_composite_debasement_score"] = df[standardized_columns].mean(axis=1)

    return df


# ── Pipeline Orchestration ─────────────────────────────────────────────────────

def build_analysis_dataframe(aligned_df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs the full feature engineering pipeline on the aligned monthly DataFrame,
    producing the final analysis-ready frame with all derived features and no raw intermediates.

    Args:
        aligned_df: Clean monthly DataFrame from align_all_series_to_monthly()

    Returns:
        Final analysis DataFrame with all features engineered, standardized and NaN rows dropped
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Engineering features...")

    analysis_df = aligned_df.copy()

    # Stage 1: Debasement indicators from macro levels
    analysis_df = compute_debasement_indicators(analysis_df)

    # Stage 2: Monthly log returns for each asset
    analysis_df = compute_asset_returns(analysis_df)

    # Stage 3: Real cash return baseline
    analysis_df = compute_cash_real_return(analysis_df)

    # Stage 4: Spread features — excess return over real cash
    analysis_df = compute_spread_features(analysis_df)

    # Stage 5: Z-score standardize debasement indicators
    analysis_df = standardize_debasement_indicators(analysis_df)

    # Stage 6: Z-score composite debasement score
    analysis_df = compute_zscore_composite_debasement_score(analysis_df)

    # Drop rows with NaNs introduced by pct_change(12) lookback at series start
    rows_before = len(analysis_df)
    analysis_df = analysis_df.dropna()
    rows_dropped = rows_before - len(analysis_df)

    print(f"  Final dataframe shape: {analysis_df.shape}")
    print(f"  Date range: {analysis_df.index.min().date()} → {analysis_df.index.max().date()}")
    print(f"  Rows dropped after feature engineering NaNs: {rows_dropped}")
    print(f"  Columns: {list(analysis_df.columns)}")

    return analysis_df


def save_analysis_dataframe(analysis_df: pd.DataFrame) -> None:
    """
    Saves the final analysis DataFrame to processed_data/analysis_df.csv with the date index.

    Args:
        analysis_df: Fully engineered monthly analysis DataFrame

    Returns:
        None
    """
    output_path = os.path.join(PROCESSED_DATA_DIR, "analysis_df.csv")
    analysis_df.to_csv(output_path, index=True)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Analysis dataframe saved → {output_path}")


# ── Entry Point ────────────────────────────────────────────────────────────────

def main() -> None:
    """
    Orchestrates the full processing pipeline: loads raw CSVs, aligns all series to monthly
    frequency, engineers all analysis features, standardizes debasement indicators, and saves
    the final dataframe to processed_data/analysis_df.csv.

    Args:
        None

    Returns:
        None
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting data processing pipeline")

    # Stage 1: Load all raw series
    m2, cpi, gdp, fed_funds, tips_real_yield, btc, sp500, gold = load_all_raw_series()

    # Stage 2: Align everything to monthly frequency and inner join
    aligned_df = align_all_series_to_monthly(
        m2=m2,
        cpi=cpi,
        gdp=gdp,
        fed_funds=fed_funds,
        tips_real_yield=tips_real_yield,
        btc=btc,
        sp500=sp500,
        gold=gold
    )

    # Stage 3: Engineer all features and produce final analysis dataframe
    analysis_df = build_analysis_dataframe(aligned_df)

    # Stage 4: Persist final dataframe
    save_analysis_dataframe(analysis_df)

    print(f"[{datetime.now().strftime('%H:%M:%S')}] Processing pipeline complete")


if __name__ == "__main__":
    main()