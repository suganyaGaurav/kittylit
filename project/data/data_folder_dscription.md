data Folder – Overview

The data/ module contains all datasets, embeddings, indexes, and preprocessing scripts required for the KittyLit recommendation system and agent-orchestrated retrieval pipeline.
This folder ensures clean data separation, fast lookups, and reproducible preprocessing, following governance-first principles.

Folder Structure & Purpose
1. clean/ : Contains cleaned and validated dataset files.
Used for production loading to ensure data consistency and integrity.

Purpose: 
  * Final preprocessed book records
  * Noise-free, normalized values 
  * Ready for embedding + UI population

2. raw/ : Stores the original, unmodified source data.

Purpose: 
* Acts as the “ground truth” dataset
* Ensures reproducibility
* Helps with debugging, audits, and governance requirements

3. scripts/ : Includes helper preprocessing scripts used to transform raw → clean → indexed datasets.

Purpose: 
* Embedding generation
* Metadata cleanup
* Index building
* Automating data preparation steps
* File Descriptions
  
4. api_usage.json : Tracks how many times API-based retrieval was used during testing.

Purpose: 
* Observability 
* Usage monitoring
* Helps in optimization decisions

5. books_dataset.json : Primary book dataset used for:

* Cache preload
* Dropdown value generation
* Initial recommendation logic

Purpose: Acts as the central metadata source for the full application.

6. faiss_index.bin : Vector index generated using FAISS for fast semantic search.

Purpose: 
  * Enables vector similarity lookup
  * Accelerates RAG retrieval
  * Core component for high-speed recommendations

7. kittylit_books (SQLite DB) : SQLite database containing structured book records.

Purpose: Acts as the authoritative structured datastore

Used by:
• cache loaders
• agent orchestrator
• fallback mechanisms

8. metadata.pkl : Serialized metadata required for embedding models.

Purpose:

* Stores mapping between book IDs, vectors, and metadata. 
* Ensures consistent embedding-to-record linking.
* Faster warm starts
* Design Principles 
* Strict separation of raw, clean, and indexed data
* Reproducible preprocessing (scripts folder)

Governance compliance: audit trails, raw preservation


Supports cache-first → DB → vector-search fallback pipeline
