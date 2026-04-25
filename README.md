# Multi-Agent Customer Support System
### Built with Google ADK · Supabase · A2A Protocol

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│       Root Router Agent (ADK)        │
│       customer_support_router        │
└──────────┬──────────────┬────────────┘
           │              │            │
           ▼              ▼            ▼
    ┌────────────┐ ┌────────────┐ ┌─────────────────┐
    │  billing   │ │  support   │ │  returns_agent   │
    │   agent    │ │   agent    │ │ (RemoteA2aAgent) │
    │ (READ ONLY)│ └─────┬──────┘ └────────┬─────────┘
    └─────┬──────┘       │                 │ HTTP/A2A
          │              ▼                 ▼
     supabase-py   ┌─────────────┐  ┌──────────────────┐
     (read tools   │ support_    │  │  Returns Service  │
      only)        │ reply_loop  │  │  (port 8001)      │
                   │ (LoopAgent) │  │  check_eligibility│
                   └──────┬──────┘  │  initiate_return  │
                          │         └──────────────────┘
                 ┌────────┴────────┐
                 ▼                 ▼
          reply_drafter    reply_reviewer
          (drafts reply)   (approves or
                            requests revision,
                            calls exit_loop)
```

---

## Project Structure

```
Week_3/
├── support_system/
│   ├── __init__.py
│   ├── agent.py                  # Root router agent (entry point)
│   ├── billing_agent.py          # Orders/billing — READ ONLY (tool filtering)
│   ├── support_agent.py          # Tickets, escalations, delegates to loop
│   ├── loop_agent.py             # LoopAgent: drafter + reviewer sub-agents
│   └── returns_agent.py          # Calls returns service via A2A
├── eval/
│   ├── support_evals.json        # 7 ADK eval test cases
│   └── README.md                 # How to run evals
├── a2a_server.py                 # Launch support_system as A2A server
├── a2a_client_demo.py            # Demo: call the A2A server over HTTP
├── a2a.railway.toml              # Railway config for A2A deployment
├── railway.toml                  # Railway config for adk web deployment
├── seed.sql                      # Sample data for Supabase
├── requirements.txt
├── stretch_goals_summary.docx    # Full write-up with diagrams and code
└── README.md
```

---

## Setup

### 1. Prerequisites
- Python 3.10+
- A Supabase project ([supabase.com](https://supabase.com))
- A Google API key ([aistudio.google.com](https://aistudio.google.com/apikey))

### 2. Install dependencies
```bash
cd Week_3
pip install -r requirements.txt
```

### 3. Configure environment
```bash
cp .env.example .env
# Edit .env with your Supabase URL, Supabase key, and Google API key
```

### 4. Set up Supabase
- Create a new Supabase project
- Run the table creation SQL in SQL Editor
- Run `seed.sql` in SQL Editor to populate sample data
- Disable Row Level Security (RLS) on all tables

---

## Running the System

```bash
cd Week_3
adk web support_system
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

### Run as A2A server (optional)
```bash
adk api_server --a2a --host 0.0.0.0 --port 8080 .
```

Agent Card available at: `http://localhost:8080/apps/support_system/.well-known/agent.json`

---

## Test Scenarios

### Scenario 1: Billing — lookup by name
> *"What's the status of my orders? My name is Alice Johnson."*

Flow: Root → billing_agent → `get_orders_for_customer` → returns order list

---

### Scenario 2: Support — escalation + LoopAgent reply
> *"I've had a broken keyboard for 3 weeks and nobody has helped me."*

Flow: Root → support_agent → `get_tickets_for_customer` → `escalate_ticket` → support_reply_loop (drafter → reviewer up to 3x) → polished reply

---

### Scenario 3: Returns — eligibility check + initiate
> *"I want to return my headphones. The order ID is 1."*

Flow: Root → returns_agent (RemoteA2aAgent) → HTTP to port 8001 → `check_return_eligibility` → `initiate_return`

---

## Key Concepts

| Concept | What it does in this project |
|---------|------------------------------|
| **Sub-agents** | Root router delegates to specialist agents without answering itself |
| **LoopAgent** | Runs drafter → reviewer repeatedly until `exit_loop()` is called or max 3 iterations |
| **Tool Filtering** | billing_agent only receives `BILLING_READ_TOOLS` — write tools are defined but never passed to the agent |
| **A2A** | support_system exposes an Agent Card + `/run` endpoint; any service can call it over HTTP |
| **ADK Eval** | 7 test cases in `eval/support_evals.json` validated with `adk eval` |

---

## Stretch Goals

- [x] **LoopAgent** — `support_reply_loop` iterates drafter → reviewer up to 3 times; reviewer calls `exit_loop()` on approval
- [x] **Tool Filtering** — `billing_agent` receives only `BILLING_READ_TOOLS`; write tools excluded at agent definition
- [x] **Eval Test Cases** — 7 scenarios in `eval/support_evals.json` covering all agents and routing cases
- [x] **Expose via A2A** — `a2a_server.py` + `a2a.railway.toml` expose the full system as an A2A-compatible service
