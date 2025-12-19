# Nick notes

## 2025-12-18 — Module 1: Deterministic LLM workflows (chaining, structure, reliability)

**Status:** Completed mini-module (videos + ran `_1_workflow.py` and `_2_agent.py`)

### Why this module mattered to me

- It validated what I’ve been trying to do: build **predictable, step-based (deterministic) pipelines** instead of “magic agent” behavior everywhere.
- The bigger win is **observability**: I can finally see _exactly_ what’s happening inside a chain (each call, each step), then measure **time + cost** per step.

### Key lesson: deterministic chain > agentic system (for reliability)

- Deterministic workflows are easier to:
  - debug
  - regression-test
  - explain to stakeholders
  - control cost (because steps are explicit)
- Agentic systems add flexibility, but can add unpredictability and harder-to-debug behavior.

### Observability insight (Weave traces)

- Weave gives a trace for each run that makes it easy to answer:
  - Which step is slow?
  - Which step is expensive?
  - What changed when prompts/models changed?
  - Where did the chain produce weak output?

**Trace link (example run):**

- https://wandb.ai/itprodirect/agents-course-live/weave/traces?view=traces_default&peekPath=%2Fitprodirect%2Fagents-course-live%2Fcalls%2F019b33f5-2eba-7740-91e5-fcba837f95e6%3FhideTraceTree%3D0

### What I ran (CLI)

- `python _1_workflow.py` (deterministic transcript analysis chain)
- `python _2_agent.py` (agent calls tools; validates tool-call tracing + logging)

### How I want to apply this to Policy Denial AI Assistant (action plan)

**Goal:** Track **latency + cost** of every LLM call and every pipeline step, so I can optimize and price the product correctly.

**Plan:**

1. Convert the denial assistant into a **named-step pipeline**, e.g.:
   - `extract_denial_reasons()`
   - `retrieve_policy_sections()`
   - `map_denial_to_policy_language()`
   - `draft_response_summary()`
   - `qc_and_citations()`
2. Wrap each step / LLM call with Weave tracing so every step logs:
   - `step_name`
   - `model`
   - `latency_ms`
   - token usage (input/output)
   - estimated cost (from token usage + pricing map)
   - identifiers: `claim_id`, `carrier`, `policy_form`, `loss_date`, `doc_id`
3. Use Weave traces to find the top offenders:
   - Most expensive step
   - Slowest step
   - Steps that fail / retry
4. Optimize by:
   - reducing unnecessary calls
   - tightening prompts
   - using smaller models for early extraction steps
   - caching deterministic outputs when possible

### Practical takeaway (simple rule)

**Default to deterministic chains** for core insurance workflows (trust + auditability + cost control).  
Add agent autonomy only where it clearly saves time (tool selection / exploration).
