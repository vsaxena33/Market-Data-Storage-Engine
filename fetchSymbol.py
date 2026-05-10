# ============================================================
# IMPORTING LIBRARIES
# ============================================================

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

# Maximum API requests allowed per second
MAX_PER_SECOND = 8

# Maximum API requests allowed per minute
MAX_PER_MINUTE = 180


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
