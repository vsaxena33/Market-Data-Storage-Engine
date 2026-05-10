# ============================================================
# IMPORTING LIBRARIES
# ============================================================

# FYERS API library
from fyers_apiv3 import fyersModel

# Importing client ID from another file
from credentials import client_id


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
