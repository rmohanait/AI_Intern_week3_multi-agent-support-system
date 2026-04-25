"""
Support Agent — connects to Supabase directly via supabase-py.

This agent handles support ticket queries using Python function tools
that wrap the Supabase client library. This demonstrates the alternative
to MCP: defining your own typed tool functions.

Stretch Goal — LoopAgent integration:
  After gathering ticket context and taking action (escalate/resolve),
  support_agent delegates to support_reply_loop (a LoopAgent sub-agent)
  to compose a polished, reviewed customer-facing reply.
"""

import os
from datetime import datetime
from dotenv import load_dotenv
from google.adk.agents import Agent
from supabase import create_client, Client

from support_system.loop_agent import support_reply_loop

load_dotenv()

# ------------------------------------------------------------------
# Supabase client (direct Python SDK approach)
# ------------------------------------------------------------------
def _get_client() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    return create_client(url, key)


# ------------------------------------------------------------------
# Tool functions — ADK converts these into callable tools for the LLM
# ------------------------------------------------------------------

def get_tickets_for_customer(customer_name: str) -> dict:
    """Fetch all support tickets for a customer by their name.

    Args:
        customer_name: The full or partial name of the customer.

    Returns:
        A dict with 'tickets' list or 'error' string.
    """
    try:
        db = _get_client()
        customers = (
            db.table("customers")
            .select("id, name, email, tier")
            .ilike("name", f"%{customer_name}%")
            .execute()
        )
        if not customers.data:
            return {"error": f"No customer found with name '{customer_name}'"}

        customer = customers.data[0]
        tickets = (
            db.table("support_tickets")
            .select("*")
            .eq("customer_id", customer["id"])
            .execute()
        )
        return {
            "customer": customer,
            "tickets": tickets.data,
            "ticket_count": len(tickets.data),
        }
    except Exception as e:
        return {"error": str(e)}


def get_open_tickets() -> dict:
    """Fetch all currently open or escalated support tickets.

    Returns:
        A dict with 'tickets' list and count.
    """
    try:
        db = _get_client()
        tickets = (
            db.table("support_tickets")
            .select("*, customers(name, email, tier)")
            .in_("status", ["open", "escalated"])
            .execute()
        )
        return {"tickets": tickets.data, "count": len(tickets.data)}
    except Exception as e:
        return {"error": str(e)}


def escalate_ticket(ticket_id: int, reason: str) -> dict:
    """Escalate a support ticket to the next level.

    Args:
        ticket_id: The ID of the support ticket to escalate.
        reason: The reason for escalation.

    Returns:
        A dict confirming escalation or an error.
    """
    try:
        db = _get_client()
        result = (
            db.table("support_tickets")
            .update({"status": "escalated"})
            .eq("id", ticket_id)
            .execute()
        )
        if result.data:
            return {
                "success": True,
                "message": f"Ticket #{ticket_id} escalated. Reason: {reason}",
                "ticket": result.data[0],
            }
        return {"error": f"Ticket #{ticket_id} not found"}
    except Exception as e:
        return {"error": str(e)}


def resolve_ticket(ticket_id: int) -> dict:
    """Mark a support ticket as resolved.

    Args:
        ticket_id: The ID of the support ticket to resolve.

    Returns:
        A dict confirming resolution or an error.
    """
    try:
        db = _get_client()
        result = (
            db.table("support_tickets")
            .update({"status": "resolved"})
            .eq("id", ticket_id)
            .execute()
        )
        if result.data:
            return {
                "success": True,
                "message": f"Ticket #{ticket_id} marked as resolved.",
                "ticket": result.data[0],
            }
        return {"error": f"Ticket #{ticket_id} not found"}
    except Exception as e:
        return {"error": str(e)}


# ------------------------------------------------------------------
# Agent definition
# ------------------------------------------------------------------
support_agent = Agent(
    name="support_agent",
    model="gemini-2.5-flash",
    instruction="""You are a Customer Support specialist agent.

You have access to tools to look up and manage support tickets in our database.
You also have a sub-agent called support_reply_loop that can draft and review
a polished customer-facing reply for you.

Support ticket status values: 'open', 'resolved', 'escalated'
Customer tier values: 'standard', 'premium' (premium customers get priority)

Your workflow:
  Step 1 — Gather context: use get_tickets_for_customer or get_open_tickets
  Step 2 — Take action: escalate_ticket or resolve_ticket as appropriate
  Step 3 — Draft reply: transfer to support_reply_loop to compose a polished
            customer-facing message that summarises what was done

Escalation triggers (escalate immediately if any are true):
  - Customer explicitly says they've been waiting a long time
  - Issue involves financial loss (wrong charge, missing refund)
  - Customer uses words like "frustrated", "terrible", "unacceptable"
  - Premium-tier customer with an open ticket older than 3 days

Always be empathetic, professional, and solution-focused.
""",
    tools=[
        get_tickets_for_customer,
        get_open_tickets,
        escalate_ticket,
        resolve_ticket,
    ],
    sub_agents=[support_reply_loop],
)
