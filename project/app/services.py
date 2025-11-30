"""
app/services.py
---------------
Form-based search pipeline:
 → Normalizes UI filters
 → Generates deterministic query hash
 → Calls Orchestrator
 → Applies post-filtering (genre + year)
 → Returns final curated items + metadata

Author: Suganya P
Date: 2025-11-30
"""

# ============================================================
# =                         IMPORTS                           =
# ============================================================

import logging
from flask import g

from agents.orchestrator import decide_and_fetch           # Main brain
from .utils import build_query_hash                        # Stable hash generator

logger = logging.getLogger("kittylit.services")


# ============================================================
# =                PARAM NORMALIZATION                       =
# ============================================================

def normalize_filters(raw: dict):
    """
    Convert UI filters into a clean, orchestrator-ready dict.
    """
    return {
        "age": raw.get("age"),
        "genre": raw.get("genre"),
        "language": raw.get("language"),
        "year": raw.get("year")
    }


# ============================================================
# =                POST-FILTERING HELPERS                   =
# ============================================================

def match_genre(book, requested_genre):
    """
    Strict genre filter.
    Book genre must match EXACTLY what the user selected.
    """
    if not requested_genre:
        return True

    book_genre = str(book.get("genre", "")).strip().lower()
    req = requested_genre.strip().lower()

    return book_genre == req


def match_year_range(book, year_range):
    """
    Check if book.publication_year falls inside UI-selected range (e.g. '2000-2009').
    """
    if not year_range:
        return True

    if "-" not in year_range:
        return True

    try:
        start, end = year_range.split("-")
        start, end = int(start), int(end)
    except:
        return True

    try:
        book_year = int(book.get("publication_year", 0))
    except:
        return False

    return start <= book_year <= end


# ============================================================
# =                MAIN SEARCH SERVICE                        =
# ============================================================

def search_service(raw_params: dict):
    """
    → Called by /search route
    → Normalizes filters
    → Builds query hash
    → Calls Orchestrator for top-K raw books
    → Applies strict genre + year-range filters
    → Returns final curated list + metadata
    """
    correlation_id = getattr(g, "correlation_id", None)

    # Normalize incoming data
    filters = normalize_filters(raw_params)

    # Build deterministic hash
    qh = build_query_hash(filters)

    logger.info(
        f"[SERVICE] Incoming filters cid={correlation_id}, qh={qh[:8]} → {filters}"
    )

    try:
        # ------------------------------------------------------------
        # RUN ORCHESTRATOR
        # ------------------------------------------------------------
        books, metadata = decide_and_fetch(
            qh=qh,
            qp=filters,
            ctx={"correlation_id": correlation_id}
        )

        metadata["correlation_id"] = correlation_id

        logger.info(
            "[SERVICE] Orchestrator returned %d raw books (cid=%s, qh=%s)",
            len(books), correlation_id, qh[:8]
        )

        # ------------------------------------------------------------
        # APPLY POST-FILTERING (GENRE + YEAR)
        # ------------------------------------------------------------
        filtered = []
        for book in books:

            # Strict Genre Filter
            if not match_genre(book, filters.get("genre")):
                continue

            # Year Range Filter
            if not match_year_range(book, filters.get("year")):
                continue

            filtered.append(book)

        logger.info(
            "[SERVICE] After filtering → %d books match UI filters",
            len(filtered)
        )

        return {
            "items": filtered,
            "metadata": metadata
        }

    except Exception as e:
        logger.exception("[SERVICE] Orchestrator failed: %s", e)

        return {
            "items": [],
            "metadata": {
                "correlation_id": correlation_id,
                "error": "orchestrator_failed",
                "detail": str(e)
            }
        }
