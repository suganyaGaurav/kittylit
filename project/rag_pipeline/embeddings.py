'''
embeddings.py
-------------
Module to build and update a FAISS semantic search index from the children's book dataset using embeddings.

Author: Ammu
Date: 2025-08-12
'''
import os  # For file path operations
import json  # To load book data from JSON file
import pickle  # To save/load metadata as binary
import logging  # To log info and errors

import numpy as np  # For numeric arrays (embeddings)
import faiss  # Facebook AI similarity search library for fast vector indexing
from sentence_transformers import SentenceTransformer  # Model to create embeddings

# Setup basic logging with timestamp, level and message format
logging.basicConfig(
    level=logging.INFO,  # Log info and above (warning, error)
    format='[%(asctime)s][%(levelname)s] %(message)s',  # Format for each log line
    datefmt='%Y-%m-%d %H:%M:%S'  # Timestamp format
)

# Base directory two levels up from this file's location (project root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Paths for data and index files relative to project root
DATA_PATH = os.path.join(BASE_DIR, "data", "books_dataset.json")  # Dataset JSON file
INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index.bin")  # Serialized FAISS index file
META_PATH = os.path.join(BASE_DIR, "data", "metadata.pkl")  # Serialized metadata (book info)

# Embedding model name to be loaded for sentence-transformer
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def load_books():
    """Load book dataset from JSON file."""
    try:
        # Open dataset file in read mode with UTF-8 encoding
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            books = json.load(f)  # Parse JSON string into Python list of dicts
        logging.info(f"Loaded {len(books)} books from dataset.")  # Log count
        return books  # Return book list
    except Exception as e:
        logging.error(f"Failed to load dataset: {e}")  # Log error if any
        return []  # Return empty list on failure


def create_embeddings(books, model):
    """Create vector embeddings for books using given SentenceTransformer model."""
    try:
        # Prepare a list of text strings combining relevant book info for semantic embedding
        texts = [
            f"{b['title']} by {b['author']} | {b['genre']} | Age {b['age_group']} | {b['language']} | {b['publication_year']}"
            for b in books
        ]
        # Use model to encode all texts into a NumPy array of embeddings
        embeddings = model.encode(texts, convert_to_numpy=True)
        logging.info(f"Created embeddings for {len(books)} books.")  # Log success
        return embeddings  # Return embedding matrix
    except Exception as e:
        logging.error(f"Error creating embeddings: {e}")  # Log error
        return None  # Return None if failure


def build_faiss_index():
    """Build a fresh FAISS index from the entire book dataset and save it with metadata."""
    books = load_books()  # Load all books from JSON file
    if not books:
        logging.error("No books loaded; cannot build FAISS index.")  # Abort if no data
        return

    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)  # Load embedding model
        logging.info(f"Loaded embedding model: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        logging.error(f"Failed to load embedding model: {e}")
        return

    embeddings = create_embeddings(books, model)  # Create embeddings for all books
    if embeddings is None:
        logging.error("Embedding creation failed; aborting index build.")  # Abort if fail
        return

    dim = embeddings.shape[1]  # Embedding dimension size
    index = faiss.IndexFlatL2(dim)  # Create FAISS index with L2 distance metric
    index.add(embeddings)  # Add embeddings to index
    logging.info(f"FAISS index created with dimension {dim} and {index.ntotal} vectors.")

    # Save index and metadata files to disk for persistence
    try:
        faiss.write_index(index, INDEX_PATH)  # Save FAISS index file
        with open(META_PATH, "wb") as f:
            pickle.dump(books, f)  # Save book metadata list as pickle file
        logging.info(f"Saved FAISS index to {INDEX_PATH} and metadata to {META_PATH}.")
    except Exception as e:
        logging.error(f"Failed to save index or metadata: {e}")


def update_faiss_index(new_books):
    """
    Add new books to existing FAISS index and update metadata.

    Args:
        new_books (list): New book dicts to add.

    Notes:
        If no existing index, creates a new one.
        This function updates files on disk but does NOT update any database.
    """
    if not new_books:
        logging.warning("No new books provided for update.")
        return

    try:
        model = SentenceTransformer(EMBEDDING_MODEL_NAME)  # Load model for embedding
        logging.info(f"Loaded embedding model for update: {EMBEDDING_MODEL_NAME}")
    except Exception as e:
        logging.error(f"Failed to load embedding model: {e}")
        return

    embeddings = create_embeddings(new_books, model)  # Embed new books
    if embeddings is None:
        logging.error("Embedding creation failed; aborting index update.")
        return

    # Try to load existing FAISS index and metadata from disk
    if os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        try:
            index = faiss.read_index(INDEX_PATH)  # Load index file
            with open(META_PATH, "rb") as f:
                books = pickle.load(f)  # Load metadata list
            logging.info(f"Loaded existing index with {index.ntotal} vectors and {len(books)} metadata entries.")
        except Exception as e:
            logging.error(f"Failed to load existing index or metadata: {e}")
            return
    else:
        logging.info("No existing index found, creating a new one.")  # Fresh start
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        books = []

    index.add(embeddings)  # Add new book embeddings to index
    books.extend(new_books)  # Append new book metadata to list
    logging.info(f"Updated index with {len(new_books)} new books. Total vectors now: {index.ntotal}")

    # Save updated index and metadata back to disk
    try:
        faiss.write_index(index, INDEX_PATH)
        with open(META_PATH, "wb") as f:
            pickle.dump(books, f)
        logging.info("Saved updated FAISS index and metadata successfully.")
    except Exception as e:
        logging.error(f"Failed to save updated index or metadata: {e}")


if __name__ == "__main__":
    # If run as a script, build the full FAISS index
    build_faiss_index()



'''
DESCRIPTION:
------------
Transforms the children's book dataset into embeddings using a SentenceTransformer model,
builds a FAISS index for fast semantic search, and saves metadata for retrieval mapping.

FEATURES:
---------
- Configurable embedding model name.
- Full index build and incremental update support.
- Robust error handling and logging.
- Saves index and metadata to disk.
- Suitable for integration with RAG pipelines.

REQUIREMENTS:
-------------
pip install sentence-transformers faiss-cpu numpy

USAGE:
------
Run as a script to build or update the index:
    python embeddings.py
'''
