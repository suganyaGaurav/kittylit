"""
app.data_loader.py
------------------
Load and normalize books dataset; produce dropdown values for UI.

Quick test:
>>> from app.data_loader import load_books_dataset, get_dropdown_values
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger("kittylit.data_loader")

_CACHE = []

def load_books_dataset(path: str = "data/books_dataset.json"):
    """
    Load dataset once and cache in process memory.
    Returns list of normalized dicts.
    """
    global _CACHE
    if _CACHE:
        logger.debug("load_books_dataset: returning cached dataset (len=%s)", len(_CACHE))
        return _CACHE
    p = Path(path)
    if not p.exists():
        logger.warning("load_books_dataset: file not found: %s", path)
        _CACHE = []
        return _CACHE
    try:
        raw = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(raw, list):
            logger.warning("load_books_dataset: expected list at top-level")
            raw = []
        normalized = []
        for item in raw:
            normalized.append({
                "title": item.get("title"),
                "authors": item.get("authors") or [],
                "isbn": item.get("isbn"),
                "language": item.get("language"),
                "genre": item.get("genre"),
                "pub_year": item.get("pub_year") or item.get("year"),
                "age": item.get("age") or item.get("age_group"),
                "raw": item
            })
        _CACHE = normalized
        logger.info("load_books_dataset: loaded %s records from %s", len(_CACHE), path)
    except Exception as e:
        logger.exception("load_books_dataset: failed to load dataset: %s", e)
        _CACHE = []
    return _CACHE

def get_dropdown_values(dataset=None):
    """
    Return deduped, sorted dropdown values: genres, languages, years, ages.
    """
    ds = dataset or load_books_dataset()
    genres = set()
    languages = set()
    years = set()
    ages = set()
    for it in ds:
        if it.get("genre"):
            genres.add(str(it["genre"]).strip())
        if it.get("language"):
            languages.add(str(it["language"]).strip())
        if it.get("pub_year"):
            try:
                years.add(int(str(it["pub_year"]).split("-")[0]))
            except Exception:
                pass
        if it.get("age"):
            ages.add(str(it["age"]).strip())
    return {
        "genres": sorted(genres),
        "languages": sorted(languages),
        "years": sorted(years, reverse=True),
        "ages": sorted(ages)
    }
