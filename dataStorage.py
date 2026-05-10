"""
================================================================================
MARKET DATA STORAGE ENGINE
================================================================================

This program connects to the FYERS API and downloads historical OHLCV
(Open, High, Low, Close, Volume) market data for multiple trading symbols.

The system is designed as a scalable market data pipeline that:

1. Downloads symbol master files from multiple exchanges.
2. Fetches historical candle data for each symbol.
3. Uses multithreading for faster parallel data collection.
4. Applies API rate limiting to avoid exceeding FYERS limits.
5. Cleans, merges, and stores market data efficiently in Parquet format.

The stored parquet files can later be used for:
- Quantitative research
- Backtesting trading strategies
- Algorithmic trading systems
- Data analysis pipelines
- Real-time analytics applications

Author: Vaibhav Saxena
================================================================================
"""
# ============================================================
# IMPORTING LIBRARIES
# ============================================================

# pandas is used for working with tables/dataframes
import pandas as pd

# FYERS API library
from fyers_apiv3 import fyersModel

# Importing client ID from another file
from credentials import client_id

# Used for timezone conversion
import pytz

# Used for date and time operations
import datetime as dt

# Used for file and folder operations
import os

# Used for running multiple tasks at the same time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Lock helps prevent multiple threads from modifying data together
from threading import Lock

# Used for timestamps and delays
import time

# deque is useful for storing request timestamps efficiently
from collections import deque


# ============================================================
# CONFIGURATION SECTION
# ============================================================

"""
This section contains all important settings used in the program.

Keeping settings in one place makes the program easier to manage.
"""

# Folder where parquet files will be stored
PARQUET_DIR = "parquet_data"

# Maximum API requests allowed per second
MAX_PER_SECOND = 8

# Maximum API requests allowed per minute
MAX_PER_MINUTE = 180

# Create parquet folder if it does not exist
os.makedirs(PARQUET_DIR, exist_ok=True)

# Get today's date
TODAY = dt.date.today()


# ============================================================
# SYMBOL MASTER COLUMN NAMES
# ============================================================

"""
FYERS provides symbol data files without proper column names.

So we manually assign column names based on FYERS documentation.
"""

COLUMNS = [
    "fytoken",
    "symbol_details",
    "exchange_instrument_type",
    "minimum_lot_size",
    "tick_size",
    "isin",
    "trading_session",
    "last_update_date",
    "expiry_date",
    "symbol_ticker",
    "exchange",
    "segment",
    "scrip_code",
    "underlying_symbol",
    "underlying_scrip_code",
    "strike_price",
    "option_type",
    "underlying_fytoken",
    "reserved_column_1",
    "reserved_column_2",
    "reserved_column_3"
]


# ============================================================
# EXCHANGE FILE URLS
# ============================================================

"""
These URLs contain all available market symbols.

Each URL belongs to a different exchange segment.
"""

URLS = {
    "NSE_CD": "https://public.fyers.in/sym_details/NSE_CD.csv",
    "NSE_FO": "https://public.fyers.in/sym_details/NSE_FO.csv",
    "NSE_COM": "https://public.fyers.in/sym_details/NSE_COM.csv",
    "NSE_CM": "https://public.fyers.in/sym_details/NSE_CM.csv",
    "BSE_CM": "https://public.fyers.in/sym_details/BSE_CM.csv",
    "BSE_FO": "https://public.fyers.in/sym_details/BSE_FO.csv",
    "MCX_COM": "https://public.fyers.in/sym_details/MCX_COM.csv"
}


# ============================================================
# RATE LIMITER VARIABLES
# ============================================================

"""
The API allows only limited requests.

We store request timestamps here so that we do not cross
the allowed API limits.
"""

# Stores request timestamps
request_times = deque()

# Lock prevents multiple threads from changing data together
lock = Lock()


# ============================================================
# INITIALIZE FYERS API
# ============================================================

def initialize_fyers():
    """
    Creates and returns FYERS API object.

    The access token is read from a text file.

    Returns:
    -------
    FyersModel
        Connected FYERS API object
    """

    # Read access token from file
    with open("access_token.txt", "r") as file:
        access_token = file.read()

    # Create FYERS API object
    fyers = fyersModel.FyersModel(
        client_id=client_id,
        token=access_token,
        is_async=False,
        log_path=""
    )

    return fyers


# ============================================================
# LOAD SYMBOL MASTER DATA
# ============================================================

def load_symbol_master():
    """
    Downloads symbol data from all exchange files.

    All exchange dataframes are merged into one dataframe.

    Returns:
    -------
    DataFrame
        Combined symbol master dataframe
    """

    # Empty list for storing dataframes
    dataframes = []

    # Loop through all exchange URLs
    for source_name, url in URLS.items():

        print(f"Downloading symbols from {source_name}")

        # Read CSV file from internet
        df = pd.read_csv(
            url,
            header=None,
            names=COLUMNS
        )

        # Add source exchange name
        df["source_file"] = source_name

        # Store dataframe in list
        dataframes.append(df)

    # Merge all dataframes together
    master_df = pd.concat(dataframes, ignore_index=True)

    print("All symbol files merged successfully")

    return master_df


# ============================================================
# RATE LIMITER FUNCTION
# ============================================================

def rate_limiter():
    """
    Controls API request speed.

    Why do we need this?

    APIs usually allow only limited requests.
    If we send too many requests quickly,
    the API may block us temporarily.

    This function makes sure that:
    - We do not exceed requests per second
    - We do not exceed requests per minute
    """

    while True:

        # Lock makes thread-safe operations possible
        with lock:

            # Current timestamp
            now = time.time()

            # Remove timestamps older than 60 seconds
            while request_times and now - request_times[0] > 60:
                request_times.popleft()

            # Total requests in last minute
            requests_last_minute = len(request_times)

            # Total requests in last second
            requests_last_second = sum(
                1 for t in request_times
                if now - t <= 1
            )

            # Check if request is allowed
            if (
                requests_last_second < MAX_PER_SECOND
                and requests_last_minute < MAX_PER_MINUTE
            ):

                # Save current timestamp
                request_times.append(now)

                return

        # Wait a little before checking again
        time.sleep(0.05)


# ============================================================
# FETCH HISTORICAL MARKET DATA
# ============================================================

def historical_data(fyers, symbol):
    """
    Downloads historical candle data for a symbol.

    Parameters:
    ----------
    fyers : FyersModel
        Connected FYERS API object

    symbol : str
        Trading symbol

    Returns:
    -------
    DataFrame
        Historical OHLCV market data
    """

    # API request parameters
    data = {
        "symbol": symbol,
        "resolution": "5S",
        "date_format": "1",
        "range_from": TODAY,
        "range_to": TODAY,
        "cont_flag": "1"
    }

    # Send API request
    response = fyers.history(data=data)

    # Extract candle data
    candles = response["candles"]

    # Convert candle data into dataframe
    df = pd.DataFrame(
        candles,
        columns=[
            "date",
            "open",
            "high",
            "low",
            "close",
            "volume"
        ]
    )

    # Convert UNIX timestamp into datetime
    df["date"] = pd.to_datetime(
        df["date"],
        unit="s"
    )

    # Convert UTC timezone to Indian timezone
    ist = pytz.timezone("Asia/Kolkata")

    df["date"] = (
        df["date"]
        .dt.tz_localize("UTC")
        .dt.tz_convert(ist)
        .dt.tz_localize(None)
    )

    # Set date column as dataframe index
    df.set_index("date", inplace=True)

    return df


# ============================================================
# SAVE DATA AS PARQUET FILE
# ============================================================

def update_parquet(symbol, new_df):
    """
    Saves market data into parquet file.

    If old data already exists:
    - old and new data are merged
    - duplicate timestamps are removed

    Parameters:
    ----------
    symbol : str
        Trading symbol

    new_df : DataFrame
        Newly downloaded market data
    """

    # Replace special characters for safe filename
    filename = (
        symbol
        .replace(":", "_")
        .replace("-", "_")
    )

    # Full parquet file path
    filepath = f"{PARQUET_DIR}/{filename}.parquet"

    # Check if file already exists
    if os.path.exists(filepath):

        # Read old parquet data
        old_df = pd.read_parquet(filepath)

        # Merge old and new data
        combined_df = pd.concat(
            [old_df, new_df]
        )

    else:

        # If no file exists, use only new data
        combined_df = new_df.copy()

    # Sort data by datetime
    combined_df = combined_df.sort_index()

    # Remove duplicate timestamps
    combined_df = combined_df[
        ~combined_df.index.duplicated()
    ]

    # Save dataframe as parquet file
    combined_df.to_parquet(
        filepath,
        index=True,
        engine="pyarrow"
    )

    print(f"{symbol} updated successfully")


# ============================================================
# PROCESS ONE SYMBOL
# ============================================================

def fetch_symbol(fyers, symbol):
    """
    Downloads and saves data for one symbol.

    Parameters:
    ----------
    fyers : FyersModel
        Connected FYERS API object

    symbol : str
        Trading symbol

    Returns:
    -------
    str
        Success or failure message
    """

    try:

        # Check API rate limit before request
        rate_limiter()

        # Download historical data
        df = historical_data(fyers, symbol)

        # If no data is returned, skip saving
        if df.empty:
            return f"{symbol} has no data for today"

        # Save data into parquet file
        update_parquet(symbol, df)

        return f"{symbol} completed"

    except Exception as error:

        return f"{symbol} failed -> {error}"


# ============================================================
# RUN PARALLEL DATA FETCHING
# ============================================================

def run_parallel_fetch(fyers, symbols):
    """
    Downloads data for multiple symbols simultaneously.

    Multithreading makes the program much faster.

    Parameters:
    ----------
    fyers : FyersModel
        Connected FYERS API object

    symbols : array-like
        List of trading symbols
    """

    # Create thread pool
    with ThreadPoolExecutor(max_workers=8) as executor:

        # Submit all tasks to thread pool
        futures = [
            executor.submit(fetch_symbol, fyers, symbol)
            for symbol in symbols
        ]

        # Print result whenever a task finishes
        for future in as_completed(futures):

            print(future.result())


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():
    """
    Main function of the program.

    Program Flow:
    -------------
    1. Connect to FYERS
    2. Download symbol master data
    3. Extract unique symbols
    4. Download historical data
    5. Save data into parquet files
    """

    print("Program Started")

    # Step 1: Initialize FYERS API
    fyers = initialize_fyers()

    # Step 2: Load all symbols
    master_df = load_symbol_master()

    # Step 3: Get unique symbols
    symbols = (
        master_df["symbol_ticker"]
        .dropna()
        .unique()
    )

    print(f"Total Symbols Found: {len(symbols)}")

    # Step 4: Fetch historical data
    run_parallel_fetch(fyers, symbols)

    print("Program Finished")


# ============================================================
# PROGRAM STARTS HERE
# ============================================================

if __name__ == "__main__":
    """
    __name__ == "__main__"

    This is a very important Python concept.

    It means:
    - Run the main() function only if this file
    is executed directly.

    This is considered best practice in Python.
    """

    main()
