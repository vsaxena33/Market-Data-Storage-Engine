# ============================================================
# IMPORTING LIBRARIES
# ============================================================

# pandas is used for working with tables/dataframes
import pandas as pd

# Used for file and folder operations
import os


# ============================================================
# CONFIGURATION SECTION
# ============================================================

"""
This section contains all important settings used in the program.

Keeping settings in one place makes the program easier to manage.
"""

# Folder where parquet files will be stored
PARQUET_DIR = "parquet_data"

# Create parquet folder if it does not exist
os.makedirs(PARQUET_DIR, exist_ok=True)


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
