agents Folder Overview

The agents/ module contains all agent-orchestration logic for the KittyLit system — including decision rules, ranking logic, agent tools, routing handlers, and the main orchestrator.
Each file follows clean-architecture principles with clear separation of concerns, explainability logs, and governance-first flows.

1. __init__.py : Initializes the agents package.

* Ensures clean namespace structure.
* Exposes shared functions/classes for use across the backend

Purpose: Acts as the entry point for the entire agent subsystem.

2. agent_tools.py : Utility functions and helper tools used by the Agent Orchestrator.

* Handles: Cache lookup helpers
* Database fetch utilities
* Query cleaning & normalization
* Input sanitation + basic governance filters

Purpose: Provides reusable, secure tools to support all agent decisions.

3. decision_rules.py : Contains the core rule-engine for conditional routing.
Decides:

* When to read from cache.
* When to fetch from DB.
* When to trigger fallback.
* When to escalate to safety filters

Purpose: Acts as the “decision brain” guiding every agent action.

4. errors.py : Centralized error-handling for the agents layer.
Includes:

* Custom exception classes.
* Structured logging patterns.
* Safe fallback responses

Purpose: Ensures reliability, debuggability, and predictable failure handling.

5. merge_and_rank.py : Merges outputs from multiple sources and ranks them.
Performs:

* Deduplication.
* Scoring + ranking.
* Combining cache + DB + live outputs

Purpose: Delivers clean, consistent, high-quality final results.

6. orchestrator.py : The main Agent Orchestrator coordinating the end-to-end workflow.
Responsibilities:

* Accept user query.
* Apply decision rules.
* Route to cache/DB/live modules.
* Merge and rank outputs.
* Return structured response

Purpose: Represents the intelligence layer of the entire system.

7. routes.py : Defines functions used by the /search and other app routes to keep all endpoints consistent with the agent pipeline.

Responsibilities:

* Handle incoming API requests.
* Pass structured payloads to the orchestrator.
* Return safe, filtered responses

Purpose: Ensures clean integration between app routes and the agents layer.

Structure Principles :

* Single-responsibility modules.
* Governance-first design.
* Explainability logs for reproducibility.
* Testability and modularity

