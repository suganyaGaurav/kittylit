scripts Folder – Overview

The scripts/ directory contains all utility scripts used for data refresh, database preparation, cache warm-up, and external API sync.
These scripts are not part of the main runtime application, but they ensure that KittyLit stays updated, optimized, and production-ready.

Each script is modular, explainable, and safe to run independently.

File Descriptions

1. fetch_live_books.py : 

* Fetches fresh book metadata from external APIs and adds it to the local dataset.
* Used to keep the collection updated.

Purpose: Sync new arrivals, Track trending books, Maintain dataset freshness for RAG & search

2. preload_cache.py : 

* Loads essential data (books, metadata) into the cache layer before server startup.

Purpose: Reduce initial cold-start latency, Speed up the Agent Orchestrator, Ensure first request is always fast

3. preload_db.py : 

* Initializes or updates the SQLite database with clean book records.

Purpose: Database warm-up, Clean insert of metadata, Ensures DB is always ready for RAG + Agents

4. refresh_weekly.py :

* Scheduled maintenance script meant to run weekly (via CRON or Windows Task Scheduler).

Purpose:

* Refresh live data
* Rebuild FAISS index (optional)
* Refresh cache + metadata
* Maintain overall system hygiene

Folder: .ipynb_checkpoints

* Automatically created by Jupyter.
* Not used for application logic.

Structure Principles

* Separation of duties – each script does one job well
* Governance-friendly – clear logs, safe operations, no destructive writes

Automatable – designed for CRON, Task Scheduler, or CI/CD

Explainability-first – each script can be reviewed independently
