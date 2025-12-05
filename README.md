KittyLit – A Responsible AI Book Recommendation System (RAG + Agent Architecture)

A production-minded MVP designed with reliability, governance, and evaluation embedded from the beginning.

Project Overview

KittyLit is an AI-driven book recommendation system built using a custom Retrieval-Augmented Generation (RAG) pipeline and an agent-based orchestrator.

The objective was not to build a large application, but to demonstrate how a real-world GenAI system should be designed—prioritizing correctness, safety, explainability, fallback logic, and monitoring from day one.

This repository reflects a practical understanding of how to design and operate trustworthy, scalable, and transparent AI systems.

Key System Features
1. Responsible AI Principles Built into the Design

PII detection and redaction

Safety and child-appropriate content rules

Transparent outputs with citations

Confidence scoring and fallback reasoning

Intent classification to prevent unsafe actions

2. Custom RAG Pipeline

Cleaned and validated book dataset

MiniLM embedding model

FAISS vector index

Hybrid retrieval (semantic + metadata filters)

Reranking for improved relevance

Context sufficiency checks before generation

3. Agent Orchestrator with Deterministic Control

Rule-based routing across DB, RAG, and LLM

Custom fallback logic

Short-term conversational memory

Summary-based long-term memory

Complete traceability through structured logs

4. Fallback-First Architecture

To minimize hallucinations and control cost, the system follows:

Cache → Database → RAG → External API → LLM

Every step has clear decision criteria and logging.

5. Evaluation Framework

Evaluation was integrated into the design, not added later.
Metrics include:

Recall@K

MRR and nDCG

Groundedness checks

Hallucination detection

Citation precision

Latency distribution (p50, p95)

Cost-per-query

Fallback activation rate

6. Monitoring and Observability

Structured logs for each stage of the pipeline

Retrieval scoring logs

Error and fallback tracing

Latency breakdown per component

Confidence and risk indicators

This ensures every answer is traceable and reproducible.

Tech Stack

Backend: Python, Flask or FastAPI
Embeddings: MiniLM Sentence Transformer
Vector Store: FAISS
LLM: OpenAI / Bedrock LLM
Database: SQLite / JSON Cache
Memory: Buffer memory + summary memory
Monitoring: Custom structured logging

Architecture Summary
User Query
    ↓
Governance Layer (PII, safety, intent)
    ↓
Routing Logic
    ├── Cache Lookup
    ├── Database Query
    ├── RAG Retrieval (FAISS)
    ├── LLM Generation (fallback)
    ↓
Explainability Layer
    (Sources, confidence, fallback reason)
    ↓
Final Answer

Repository Structure
kittylit/
│
├── app.py                     # Main backend application
├── data/
│     └── books_dataset.json   # Book metadata
│
├── utils/
│     ├── data_loader.py       # Data ingestion utilities
│     └── options.py           # Constants and filters
│
├── rag_pipeline/              # Embeddings, FAISS, retrieval logic
├── agent/                     # Routing, fallback, and memory logic
│
├── static/                    # CSS, JS, images
└── templates/                 # HTML templates

How to Run the Application
git clone https://github.com/<your-username>/kittylit
cd kittylit
pip install -r requirements.txt
python app.py


Access the application at:
http://localhost:5000

Why This Project Matters

KittyLit demonstrates an end-to-end understanding of:

* RAG system behavior in real-world scenarios

* Agentic routing and controlled tool execution

* Fallback logic to ensure reliability

* Governance-first AI design

* Proper evaluation of retrieval and generation

* Observability and monitoring practices

Although a small project, KittyLit was built with the mindset of a GenAI architect, focusing on clarity, safety, and engineering discipline.

Contributions and Collaboration

If you work in RAG, agent systems, responsible AI, cloud AI, or evaluation frameworks, feel free to connect or collaborate.
