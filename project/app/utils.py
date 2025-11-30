"""
app.utils.py
------------
Helpers: correlation id middleware, deterministic query hashing, response shaping.

Quick test:
>>> from app.utils import build_query_hash
>>> build_query_hash({'title':'X','year':2020})
"""

import hashlib
import uuid
import logging
from flask import g, request

logger = logging.getLogger("kittylit.utils")

# ----------------------------
# Correlation ID middleware
# ----------------------------
def generate_correlation_id():
    return str(uuid.uuid4())

def attach_correlation_id(app):
    """
    Middleware to attach X-Correlation-Id to request context (flask.g).
    """
    @app.before_request
    def _attach_cid():
        cid = request.headers.get("X-Correlation-Id") or generate_correlation_id()
        # store both on g and request for compatibility
        g.correlation_id = cid
        request.correlation_id = cid

# ----------------------------
# Query hash / response helpers
# ----------------------------
def build_query_hash(params: dict) -> str:
    """
    Create deterministic string from a fixed set of fields then hash it.
    Ensures cache keys are stable across processes.
    """
    keys = ["age", "genre", "language", "year", "title"]
    normalized = {k: str(params.get(k, "")).strip().lower() for k in keys}
    canonical = "|".join(f"{k}={normalized[k]}" for k in keys)
    h = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    logger.debug("build_query_hash: canonical=%s hash=%s", canonical, h)
    return h

def build_response(items, meta: dict):
    """
    Ensure the response meta contains required fields and return final payload.
    """
    meta = dict(meta or {})
    meta.setdefault("source_tried", [])
    meta.setdefault("source_used", None)
    meta.setdefault("latencies_ms", {})
    meta.setdefault("counts", {})
    return {"items": items or [], "meta": meta}
