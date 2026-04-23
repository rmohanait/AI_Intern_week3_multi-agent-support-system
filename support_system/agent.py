"""
Root Router Agent — the entry point for the multi-agent support system.

This agent receives all incoming queries and routes them to the
appropriate specialist sub-agent:

  billing_agent  → order status, charges, payment questions
  support_agent  → complaints, tickets, escalations
  returns_agent  → return requests (via A2A remote service)

Run with:
    adk web support_system
"""

import os
from dotenv import load_dotenv
from google.adk.agents import Agent

from support_system.billing_agent import billing_agent
from support_system.support_agent import support_agent
from returns_service.agent import root_agent as returns_agent

load_dotenv()

# NOTE: returns_agent is imported directly from returns_service due to an
# a2a-sdk version incompatibility with google-adk 1.31.1.
# The returns_service is still structured as a standalone A2A-compatible
# service — once SDK versions align, swap this import back to RemoteA2aAgent:
#
#   from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
#   returns_agent = RemoteA2aAgent(
#       name="returns_agent",
#       agent_card_url="http://localhost:8001/.well-known/agent.json",
#   )

# ------------------------------------------------------------------
# Root Router Agent
# ------------------------------------------------------------------
root_agent = Agent(
    name="customer_support_router",
    model="gemini-2.5-flash",
    instruction="""You are the main Customer Support router for an e-commerce company.

Your ONLY job is to understand the customer's intent and delegate to the
correct specialist agent. Do not answer questions yourself.

Routing rules:
  → billing_agent   : order status, tracking, charges, invoices, payment issues
  → support_agent   : complaints, bugs, service issues, escalations, ticket status
  → returns_agent   : return requests, refund eligibility, "I want to return", "send it back"

Examples:
  "Where is my order?"                    → billing_agent
  "I was charged twice"                   → billing_agent
  "My product is broken"                  → support_agent
  "I've been waiting 3 weeks, this is awful" → support_agent
  "I want to return my headphones"        → returns_agent
  "Can I get a refund on order #5?"       → returns_agent

Always greet the customer warmly before routing.
If the intent is unclear, ask one clarifying question.
""",
    sub_agents=[billing_agent, support_agent, returns_agent],
)
