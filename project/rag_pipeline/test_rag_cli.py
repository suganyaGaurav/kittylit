import sys
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Update BASE_DIR path to your project root if needed
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "data", "faiss_index.bin")
META_PATH = os.path.join(BASE_DIR, "data", "metadata.pkl")

def load_resources():
    # Load FAISS index
    index = faiss.read_index(INDEX_PATH)
    # Load metadata (book info)
    with open(META_PATH, "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

def embed_query(text, model):
    return model.encode([text])

def filter_books(books, age_group=None, genre=None, language=None, year_range=None):
    filtered = []
    start_year, end_year = None, None
    if year_range:
        try:
            start_year, end_year = map(int, year_range.split("-"))
        except Exception:
            pass
    for book in books:
        if age_group and str(book.get("age_group")) != str(age_group):
            continue
        if genre and book.get("genre", "").lower() != genre.lower():
            continue
        if language and book.get("language", "").lower() != language.lower():
            continue
        if start_year and end_year:
            try:
                year = int(book.get("publication_year"))
                if year < start_year or year > end_year:
                    continue
            except Exception:
                continue
        filtered.append(book)
    return filtered

def main():
    # Read filters from command line args
    args = sys.argv[1:]
    age_group = args[0] if len(args) > 0 else None
    genre = args[1] if len(args) > 1 else None
    language = args[2] if len(args) > 2 else None
    year_range = args[3] if len(args) > 3 else None

    print(f"Filters - Age Group: {age_group}, Genre: {genre}, Language: {language}, Year Range: {year_range}")

    index, metadata = load_resources()
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Create query text (concatenate filter values)
    query_text = " ".join(filter(None, [age_group, genre, language, year_range]))
    query_emb = embed_query(query_text, model)

    # Search in FAISS index - top 10 results
    D, I = index.search(np.array(query_emb).astype("float32"), 10)

    # Get candidate books from indices
    candidates = [metadata[i] for i in I[0]]

    # ADD THESE LINES to print candidates before filtering:
    print("\nFAISS candidate books before filtering:")
    for book in candidates:
        print(f" - {book.get('title')} by {book.get('author')} | Age: {book.get('age_group')} | Genre: {book.get('genre')} | Language: {book.get('language')} |     Year: {book.get('publication_year')}")


    # Apply strict filters on candidates
    results = filter_books(candidates, age_group, genre, language, year_range)

    print(f"\nFound {len(results)} books matching filters:")
    for book in results:
        print(f" - {book.get('title')} by {book.get('author')}")

if __name__ == "__main__":
    main()
