# ============================================================
# IMPORTING LIBRARIES
# ============================================================

# Used for timezone conversion
import pytz

# pandas is used for working with tables/dataframes
import pandas as pd

# Used for date and time operations
import datetime as dt


# ============================================================
# GLOBAL VARIABLE
# ============================================================

"""
This section contains all global variables used in the program.

Keeping settings in one place makes the program easier to manage.
"""

# Get today's date
TODAY = dt.date.today()


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

