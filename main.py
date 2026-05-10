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

# We will use the symbol master data to get the list of symbols to download
from zds_symbolMaster import load_symbol_master

# Used to initialize Fyers API Object
from zds_initializer import initialize_fyers

# Downloads and saves data
from zds_fetchSymbol import run_parallel_fetch

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
