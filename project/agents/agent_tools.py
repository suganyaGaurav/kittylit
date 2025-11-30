"""
agents/agent_tools.py
---------------------
Helper functions for:
- Fetching live book data from Google Books API,
- Managing in-memory cache,
- Tracking daily API usage quota,
- Normalizing API responses to our internal book schema.

Author: Ammu
Date: 2025-08-13
"""

import requests           # To make HTTP calls to Google Books API
import json               # For reading/writing JSON usage files
import os                 # To check file existence
import logging            # For structured logging
from datetime import datetime  # For date/time handling
from .errors import LiveDataFetchError  # Custom exception for live data fetch failures

# Configure logger for this module
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s][agent_tools] %(message)s')
logger = logging.getLogger(__name__)

# Simple in-memory cache dictionary (non-persistent, only for current runtime)
CACHE = {}

# Path to file that stores daily API usage info persistently
USAGE_FILE = "data/api_usage.json"

# Google Books API daily call limit to avoid quota breach
DAILY_LIMIT = 600


def can_make_api_call() -> bool:
    """
    Check if the daily API call quota has been reached.
    Reads usage from JSON file, resets daily count if new day.

    Returns:
        bool: True if API calls can be made, False if limit reached.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    usage = {"date": today_str, "count": 0}

    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage = json.load(f)

    # Reset count if stored date differs from today
    if usage.get("date") != today_str:
        logger.debug("New day detected. Resetting daily API call count.")
        usage = {"date": today_str, "count": 0}

    can_call = usage.get("count", 0) < DAILY_LIMIT
    logger.debug(f"API call quota check: {usage.get('count', 0)} used out of {DAILY_LIMIT}. Can call: {can_call}")
    return can_call


def increment_api_call_count():
    """
    Increase the daily API call count by one and save it persistently.
    Resets count if the day has changed since last record.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    usage = {"date": today_str, "count": 0}

    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage = json.load(f)

    if usage.get("date") != today_str:
        logger.debug("New day detected during increment. Resetting count to 0.")
        usage = {"date": today_str, "count": 0}

    usage["count"] = usage.get("count", 0) + 1
    logger.debug(f"Incremented API call count to {usage['count']}")

    with open(USAGE_FILE, "w") as f:
        json.dump(usage, f)


def get_daily_api_call_count() -> int:
    """
    Returns the number of API calls made today.
    Reads usage from JSON file and resets count if date changed.

    Returns:
        int: Number of API calls made today.
    """
    today_str = datetime.now().strftime("%Y-%m-%d")
    usage = {"date": today_str, "count": 0}

    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, "r") as f:
            usage = json.load(f)

    if usage.get("date") != today_str:
        return 0

    return usage.get("count", 0)


def fetch_live_data(query_params):
    """
    Fetch book info from Google Books API based on filters.
    Respects daily API quota. Raises error if quota exceeded or API fails.

    Args:
        query_params (dict): Query filters like title, genre, language, year.

    Returns:
        list[dict]: Normalized book data matching internal schema.

    Raises:
        LiveDataFetchError: If API quota exceeded or call fails.
    """
    if not can_make_api_call():
        logger.warning("Daily API call limit reached. Using fallback.")
        raise LiveDataFetchError(
            "Daily API call limit reached. Falling back to local database."
        )

    try:
        url = "https://www.googleapis.com/books/v1/volumes"

        q_parts = []
        if query_params.get("title"):
            q_parts.append(f'intitle:{query_params["title"]}')
        if query_params.get("genre"):
            q_parts.append(f'subject:{query_params["genre"]}')

        q = " ".join(q_parts) if q_parts else "children"

        params = {
            "q": q,
            "maxResults": 40,
        }
        if query_params.get("language"):
            params["langRestrict"] = query_params["language"]

        logger.debug(f"Making Google Books API call with params: {params}")
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            logger.error(f"Google API error with status code: {response.status_code}")
            raise LiveDataFetchError(f"Google API returned status code {response.status_code}")

        increment_api_call_count()

        data = response.json()
        normalized_books = normalize_google_books_response(data, query_params.get("year"))
        logger.debug(f"Fetched {len(normalized_books)} books from live API.")
        return normalized_books

    except Exception as e:
        logger.error(f"Error during live data fetch: {e}")
        raise LiveDataFetchError(f"Error fetching live data: {str(e)}")


def normalize_google_books_response(api_response, filter_year=None):
    """
    Convert Google Books API raw data to internal standard book dictionary.

    Args:
        api_response (dict): Raw JSON response from Google Books API.
        filter_year (str or None): Optional publication year filter.

    Returns:
        list[dict]: List of normalized books with keys: title, author, year, description, isbn, thumbnail_url, source
    """
    normalized = []

    items = api_response.get("items", [])
    for item in items:
        volume_info = item.get("volumeInfo", {})

        pub_date = volume_info.get("publishedDate", "")
        pub_year = pub_date.split("-")[0] if pub_date else None

        if filter_year and pub_year and filter_year != pub_year:
            continue

        isbn = None
        for identifier in volume_info.get("industryIdentifiers", []):
            if identifier.get("type") == "ISBN_13":
                isbn = identifier.get("identifier")
                break
        if not isbn and volume_info.get("industryIdentifiers"):
            isbn = volume_info["industryIdentifiers"][0].get("identifier")

        book = {
            "title": volume_info.get("title", "Unknown Title"),
            "author": ", ".join(volume_info.get("authors", [])) if volume_info.get("authors") else "Unknown Author",
            "year": pub_year,
            "description": volume_info.get("description", ""),
            "isbn": isbn,
            "thumbnail_url": volume_info.get("imageLinks", {}).get("thumbnail"),
            "source": "google_books"
        }
        normalized.append(book)

    logger.debug(f"Normalized {len(normalized)} books from API response.")
    return normalized


def get_cached_results(query_hash):
    """
    Get cached results for a query hash from in-memory cache.

    Args:
        query_hash (str): Unique key for query.

    Returns:
        dict or None: Cached data dict containing 'timestamp' and 'data', or None if missing.
    """
    result = CACHE.get(query_hash)
    logger.debug(f"Cache {'hit' if result else 'miss'} for query hash {query_hash}")
    return result


def set_cache_results(query_hash, results):
    """
    Store results in cache with current timestamp.

    Args:
        query_hash (str): Unique key for query.
        results (list[dict]): Book list to cache.
    """
    CACHE[query_hash] = {
        "timestamp": datetime.now(),
        "data": results
    }
    logger.debug(f"Cache set for query hash {query_hash} with {len(results)} results.")
