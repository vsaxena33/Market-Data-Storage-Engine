# pandas is used for working with tables/dataframes
import pandas as pd

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
