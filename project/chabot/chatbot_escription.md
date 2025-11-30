ChatBot Module – Overview

This folder is reserved for the upcoming ChatBot subsystem of the KittyLit architecture.
It follows the same clean-architecture, modular, explainable design used across the project, preparing the system for seamless integration of conversational intelligence.

* Even though implementation is in progress, this folder defines the structure and responsibilities of the future chatbot pipeline. Planned Folder Purpose

The ChatBot module will provide:

* A natural-language interface for parents. 
* Retrieval-augmented responses using book metadata
* Safety-filtered conversational flow
* Stateful and stateless memory handling
* Explainability logs for debugging and governance
* It will function independently while integrating tightly with the RAG pipeline, Agents, and App layers.
* Planned File Descriptions (Future Implementation)

__init__.py : 

* Initializes the ChatBot module.
* Prepares imports, exposes shared helper functions, and sets up basic configuration.

chat_engine.py :

*Core engine that processes incoming user messages. Will handle:

* Query parsing
* Intent detection
* Routing to RAG / Agents
* Conversation state management

This file will serve as the “heart” of chatbot intelligence.

memory_manager.py : Responsible for managing multi-turn context. Handles:

* Short-term session memory
* Long-term profile memory (local JSON / DB)
* Forgetting strategy
* Safety filters for personal data retention
* This supports a reliable, human-like conversation experience.

governance_filters.py : Implements Responsible AI safeguards:

* PII filters
* Content risk detection
* Guardrails for inappropriate or unsafe questions
* Logging for audit trail
* Ensures every conversation aligns with governance and compliance principles.

response_templates.py : Stores reusable structured reply templates to maintain:

* Tone consistency
* Clear and safe messaging
* Traditional family-aligned phrasing
* Context-aware fallback responses
* Useful for avoiding hallucinations and ensuring stable output.

router.py : Orchestrates how chatbot queries flow between components:

* ChatBot → RAG
* ChatBot → Agents
* ChatBot → Cache/DB lookup
* ChatBot → Safety fallback
* Acts similar to the Agents’ routes.py but specific to conversational flow.

models/ : A dedicated subfolder for fine-tuned or LoRA-based models used for:

* Parenting Q&A
* Book recommendations
* Domain-specific guidance
* Supports the HelpChatbot planned for later phases.

Design Principles :

* Separation of concerns
* Governance-first architecture
* Strict explainability logging
* End-to-end testability
* Future-proof modular layout

