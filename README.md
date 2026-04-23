# Multi-Agent Customer Support System
### Built with Google ADK · Supabase MCP · A2A Protocol

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────┐
│     Root Router Agent (ADK)     │
│   customer_support_router       │
└──────────┬──────────┬───────────┘
           │          │          │
           ▼          ▼          ▼
    ┌──────────┐ ┌──────────┐ ┌─────────────────┐
    │ billing  │ │ support  │ │  returns_agent   │
    │  agent   │ │  agent   │ │ (RemoteA2aAgent) │
    └────┬─────┘ └────┬─────┘ └────────┬─────────┘
         │            │                │ HTTP/A2A
         ▼            ▼                ▼
    Supabase MCP  supabase-py   ┌──────────────────┐
    (orders,      (support_     │  Returns Service  │
    customers)    tickets)      │  (port 8001)      │
                                │  check_eligibility│
                                │  initiate_return  │
                                └──────────────────┘
```

---

## Project Structure

```
Week_3/
├── support_system/              # Main ADK agent package
│   ├── agent.py                 # Root router agent (entry point)
│   └── sub_agents/
│       ├── billing_agent.py     # Handles orders/billing via Supabase MCP
│       └── support_agent.py     # Handles tickets via supabase-py tools
├── returns_service/             # Separate A2A service
│   └── agent.py                 # Returns agent (check + initiate return)
├── seed.sql                     # Sample data for Supabase
├── requirements.txt
├── .env.example                 # Copy to .env and fill in your keys
└── README.md
```

---

## Setup

### 1. Prerequisites
- Python 3.10+
- Node.js + npx (for Supabase MCP server)
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
- Run the table creation SQL from the earlier step in SQL Editor
- Run `seed.sql` in SQL Editor to populate sample data
- Disable Row Level Security (RLS) on all 3 tables for simplicity

---

## Running the System

You need **two terminals** running simultaneously.

### Terminal 1 — Start the Returns A2A Service (port 8001)
```bash
cd Week_3
adk api_server returns_service --port 8001
```

### Terminal 2 — Start the Main Support System
```bash
cd Week_3
adk web support_system
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

---

## Test Scenarios

### Scenario 1: Billing (MCP)
> *"What's the status of my order? My name is Alice Johnson."*

Expected flow: Root → billing_agent → Supabase MCP query → returns order details

---

### Scenario 2: Returns (A2A)
> *"I want to return my headphones. The order ID is 1."*

Expected flow: Root → returns_agent (RemoteA2aAgent) → HTTP to port 8001 → check_return_eligibility → initiate_return

---

### Scenario 3: Escalation
> *"I've had a broken keyboard for 3 weeks and nobody has helped me. This is unacceptable."*

Expected flow: Root → support_agent → get_tickets_for_customer → escalate_ticket (detects frustration keywords)

---

## Key Concepts

| Concept | What it does in this project |
|---------|------------------------------|
| **MCP** | billing_agent uses Supabase MCP server to query the DB via protocol |
| **A2A** | returns_service exposes an agent over HTTP; main system calls it remotely |
| **Sub-agents** | Root router delegates to specialists without answering itself |
| **RemoteA2aAgent** | ADK's built-in client for calling A2A-compatible agent services |

---

## Stretch Goals

- [ ] **LoopAgent** — wrap support_agent in a LoopAgent for multi-turn resolution flows
- [ ] **Tool Filtering** — use `readonly=True` on Supabase MCP to prevent writes
- [ ] **Eval Test Cases** — add 5+ eval scenarios in `evals/` folder
- [ ] **Expose via A2A** — wrap the entire support_system as an A2A service too
