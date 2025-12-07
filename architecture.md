# KittyLit – System Architecture Overview

KittyLit is a responsible AI system designed to give parents safe, reliable, and age-appropriate
children’s book recommendations. The main recommendation engine is intentionally **deterministic**
and **non-LLM-dependent**, ensuring predictable behavior and zero hallucination risk.

This document explains the architecture of both:
1. The **main book search system** (Cache → DB → Orchestrator → Safety)
2. The **separate Help Chatbot**, which uses a small RAG pipeline

The two systems are isolated for safety and clarity.


------------------------------------------------------------
## 1. High-Level Architecture (Main Search Engine)

User (Parent)
→ UI  
→ Backend Routes  
→ Service Layer  
→ Agent Orchestrator  
→ Cache  
→ Database  
→ Safety Filters  
→ Final Ranked Output  

**Note:**  
The **main search engine does NOT use RAG or LLMs**.  
It is deterministic, rule-based, and fully explainable.


------------------------------------------------------------
## 2. Core Components (Main System)

### **1. UI Layer**
- Collects user inputs such as age, skill-level, preferred genre.
- Displays structured, safe recommendations.
- Emphasizes clarity, simplicity, and family-friendly interaction.

### **2. Backend Routing Layer (Flask)**
- Thin transport layer.
- Performs minimal validation.
- Forwards requests to the service layer.
- Keeps routing logic clean and isolated.

### **3. Service Layer**
- Performs structured input cleanup.
- Applies simple rule-based checks.
- Calls the Agent Orchestrator.
- Returns standardized output to UI.
- Helps keep `routes.py` clean and professional.

### **4. Agent Orchestrator (Central Decision Engine)**
The orchestrator is the “brain” of KittyLit’s main system.

It decides:
- Whether results should come from Cache or Database
- How to merge and rank book candidates
- Which deterministic rules apply (age filters, category matching)
- When to apply fallback logic (e.g., missing ISBN, low-match queries)
- How to maintain consistency and safety across responses

No LLM is used in the orchestrator.  
This ensures predictable, parent-trusted output.

### **5. Cache Layer**
- Preloaded at startup with most book records.
- Ensures fast responses.
- Reduces hits to the SQLite database.
- Acts as the first retrieval layer for all searches.

### **6. Database Layer (SQLite)**
- Stores curated book metadata.
- Acts as the authoritative source of truth.
- Designed for transparency and easy inspection.
- Works in sync with the cache for reliability.

### **7. Safety & Governance Filters**
Every output passes through:
- Age-appropriateness rules  
- Sensitive-topic checks  
- Stability rules for consistent recommendations  
- PII and unsafe content filters  
- Final validation to ensure trustworthiness  

These filters make KittyLit suitable for families, schools, and parent workflows.

### **8. Output Formatter**
- Structures results into a clean JSON format.
- Adds explanation and reasoning fields.
- Ensures UI consistency across all devices.


------------------------------------------------------------
## 3. Help Chatbot Architecture (Separate Flow)

The Help Chatbot is **independent** from the main search system.

Flow:
User → Chat UI → Chat Route → Chat Service → Mini Orchestrator  
→ **RAG Pipeline** → Fine-tuned MiniLM → Safety Filters → Response

### RAG Pipeline (Chatbot Only)
Used exclusively for:
- Answering parenting questions
- Book-related explanations
- Helping users understand categories, reading levels, or features

It uses:
- Domain-specific embeddings  
- A fine-tuned MiniLM  
- A curated text corpus  

This ensures helpful, low-risk responses while keeping
the main recommendation engine purely deterministic.

**Important:**  
RAG never influences the book recommendations themselves.


------------------------------------------------------------
## 4. End-to-End Flow Summary

### ⭐ Main Search
1. Parent enters query  
2. Routes → Service  
3. Orchestrator checks Cache → DB  
4. Books are merged and ranked  
5. Safety filters validate outputs  
6. UI receives stable recommendations  

### ⭐ Chatbot
1. User asks a help question  
2. RAG retrieves relevant text chunks  
3. MiniLM generates a short answer  
4. Safety filters clean output  
5. UI shows safe, guided response  


------------------------------------------------------------
## 5. Why This Architecture Works Well

- **Zero hallucination risk in main search**  
- **Deterministic and predictable** behavior  
- **Cache-first design for speed**  
- **Safety built into every step**  
- **Parents can trust the output**  
- **RAG is isolated to chatbot**, keeping the system clean  
- **Easy to audit, debug, and extend**  
- **Traditional engineering discipline**, avoiding unnecessary complexity  


------------------------------------------------------------
## 6. Diagram (Add Image in /docs/assets)
Save your architecture PNG/SVG and reference it like:

