"""
retriever.py
------------
Retrieve and re-rank books from the FAISS semantic index based on user filters.

Author: Ammu
Date: 2025-08-12
"""

import os  # For file path manipulation
import faiss  # FAISS library for similarity search on vector embeddings
import pickle  # To load and save Python objects like metadata
import logging
from sentence_transformers import SentenceTransformer  # Model to generate text embeddings

# Configure logging for detailed debug output
logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s][retriever] %(message)s')
logger = logging.getLogger(__name__)

DEBUG = True  # Toggle debug logs; you can set to False in production

# ==============================
# Paths for FAISS index & metadata files on disk
# ==============================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index.bin")
META_PATH = os.path.join(BASE_DIR, "data", "metadata.pkl")

# ==============================
# Load embedding model ONCE to avoid reloading on every search
# ==============================
model = SentenceTransformer("all-MiniLM-L6-v2")

# ==============================
# Load FAISS index and metadata ONCE at startup for repeated queries
# ==============================
try:
    index = faiss.read_index(INDEX_PATH)
    logger.debug(f"Loaded FAISS index with {index.ntotal} vectors.")
except Exception as e:
    logger.error(f"Error loading FAISS index: {e}")
    raise

try:
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)
    logger.debug(f"Loaded {len(metadata)} metadata records.")
except Exception as e:
    logger.error(f"Error loading metadata: {e}")
    raise


def search_books(filters, top_k=50):
    """
    Search FAISS index with semantic query derived from filters,
    then apply stricter filtering and rank results by similarity.

    Args:
        filters (dict): Filter parameters, e.g. language, genre, age_group, year_range (string like '2010-2020')
        top_k (int): Number of nearest neighbors to retrieve from FAISS index before filtering.

    Returns:
        list of dicts: Top matching books, with similarity scores.
    """

    logger.debug(f"Incoming Filters: {filters}")

    # 1. Build query string from filters
    query_parts = []
    if filters.get("language"):
        query_parts.append(filters["language"])
    if filters.get("genre"):
        query_parts.append(filters["genre"])
    if filters.get("age_group"):
        query_parts.append(f"age {filters['age_group']}")
    if filters.get("year_range"):
        query_parts.append(filters["year_range"])

    query = " ".join(query_parts)
    logger.debug(f"Query String for FAISS: '{query}'")

    # 2. Generate embedding vector
    query_vec = model.encode([query], convert_to_numpy=True)

    # 3. Search FAISS index
    distances, indices = index.search(query_vec, top_k)
    logger.debug(f"FAISS returned {len(indices[0])} results.")

    # 4. Map indices to metadata and add similarity scores
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        book = metadata[idx].copy()
        book["similarity"] = float(dist)
        results.append(book)

    # 5. Apply stricter filtering and penalize similarity scores where needed
    filtered_results = []
    for book in results:
        reasons = []

        # Language filter: skip mismatch
        if filters.get("language") and book.get("language", "").lower() != filters["language"].lower():
            reasons.append(f"Language mismatch: {book.get('language')}")
            continue

        # Genre filter: skip mismatch
        if filters.get("genre") and filters["genre"].lower() not in book.get("genre", "").lower():
            reasons.append(f"Genre mismatch: {book.get('genre')}")
            continue

        # Age group filter: penalize similarity if outside age range
        if filters.get("age_group"):
            try:
                start_age, end_age = map(int, book.get("age_group", "0-0").split("-"))
                filter_age = int(filters["age_group"])
                if not (start_age <= filter_age <= end_age):
                    book["similarity"] += 0.3
                    reasons.append(f"Age penalty: {book.get('age_group')}")
            except Exception as e:
                reasons.append(f"Age parse error: {e}")

        # Year range filter: penalize similarity if outside publication year range
        if filters.get("year_range"):
            try:
                start_year, end_year = map(int, filters["year_range"].replace(" ", "").split("-"))
                pub_year = int(book.get("publication_year", 0))
                if not (start_year <= pub_year <= end_year):
                    book["similarity"] += 0.5
                    reasons.append(f"Year penalty: {pub_year}")
            except Exception as e:
                reasons.append(f"Year parse error: {e}")

        if DEBUG:
            logger.debug(f"Book: '{book.get('title')}' | Reasons: {', '.join(reasons) if reasons else 'All filters matched'}")

        filtered_results.append(book)

    # 6. Sort by similarity ascending (best matches first)
    filtered_results.sort(key=lambda x: x["similarity"])

    logger.debug(f"Final filtered results count: {len(filtered_results)}")

    # 7. Return top 10 results
    return filtered_results[:10]
