# Architecture & Design Report

## 1. Architecture
The architecture splits computer-use automation into two distinct execution phases:
- **Discovery (LLM Loop):** Uses Playwright and an LLM to navigate legacy UIs, analyze state, and construct a structured artifact.
- **Deterministic Execution (Replay):** Runs recorded artifacts programmatically via multi-strategy locator cascades, eliminating LLM latency and non-determinism in production.

## 2. Artifact Schema
The `CapabilityArtifact` schema separates parameter declarations (`inputs`/`outputs`) from step execution logic. Each step maintains a ordered list of locator strategies (`test-id` -> `css` -> `xpath`), allowing resilient element matching.

## 3. Determinism & Error Handling
- **Locators:** Fallbacks handle minor DOM updates seamlessly.
- **Classification:** The engine explicitly categorizes outcomes into:
  - `SUCCESS`: Operational completion with extracted outputs.
  - `BUSINESS_OUTCOME`: Expected domain logic outcomes (e.g., "Member Not Found").
  - `HARD_FAILURE`: Technical blocks or unrecoverable automation failures.

## 4. Heterogeneity & Multi-Tenant
- **Surface Abstraction:** Playwright handles web surfaces. The locator abstraction supports extension to desktop automation (e.g., PyAutoGUI or Accessibility API coordinates) by swapping selector engines.
- **Multi-Tenant Sharing:** System base artifacts can be extended via tenant-specific locator overrides without re-recording base business flows.

## 5. Escalation & Handoff
When an exception occurs:
1. Automation pauses and captures screenshot/state context.
2. An intervention request alerts a human operator.
3. Control is transferred to the live browser session for human correction, then returned to the automation engine to resume or terminate gracefully.

## 6. Safety
- Domain allowlists enforce execution boundary constraints.
- Sensitive output dictionaries undergo automated key/pattern scrubbing for SSNs and tokens prior to persisting logs.

## 7. Cuts
- **Cut for Scope:** Full live co-browsing web UI (replaced with CLI operator takeover handoff).
- **Next Steps:** Desktop Accessibility API bindings and distributed queue workers (Celery/Redis) for parallel tenant execution.