"""
Billing Agent — connects to Supabase via supabase-py.

This agent handles order and billing queries by using Python function tools
that wrap the Supabase client directly.

NOTE on MCP: The original design used MCPToolset with the Supabase MCP server
(via npx). That approach requires Node.js and async context manager setup.
The direct supabase-py approach below achieves the same result and is more
reliable for local development. The MCP pattern is documented in comments.

MCP equivalent (requires Node.js + npx):
    from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
    supabase_mcp = MCPToolset(
        connection_params=StdioServerParameters(
            command="npx",
            args=["-y", "@supabase/mcp-server-supabase@latest",
                  "--supabase-url", SUPABASE_URL,
                  "--supabase-key", SUPABASE_KEY]
        )
    )
"""

import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from supabase import create_client, Client

load_dotenv()


# ------------------------------------------------------------------
# Supabase client
# ------------------------------------------------------------------
def _get_client() -> Client:
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_KEY", "")
    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
    return create_client(url, key)


# ------------------------------------------------------------------
# Tool functions
# ------------------------------------------------------------------

def get_orders_for_customer(customer_name: str) -> dict:
    """Fetch all orders for a customer by their name.

    Args:
        customer_name: The full or partial name of the customer.

    Returns:
        A dict with customer info and their orders list.
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
        orders = (
            db.table("orders")
            .select("*")
            .eq("customer_id", customer["id"])
            .execute()
        )
        return {
            "customer": customer,
            "orders": orders.data,
            "order_count": len(orders.data),
        }
    except Exception as e:
        return {"error": str(e)}


def get_order_by_id(order_id: int) -> dict:
    """Fetch a specific order by its ID.

    Args:
        order_id: The numeric ID of the order.

    Returns:
        A dict with the order details and customer info.
    """
    try:
        db = _get_client()
        result = (
            db.table("orders")
            .select("*, customers(name, email, tier)")
            .eq("id", order_id)
            .execute()
        )
        if not result.data:
            return {"error": f"Order #{order_id} not found"}
        return {"order": result.data[0]}
    except Exception as e:
        return {"error": str(e)}


def get_orders_by_email(email: str) -> dict:
    """Fetch all orders for a customer by their email address.

    Args:
        email: The customer's email address.

    Returns:
        A dict with customer info and their orders list.
    """
    try:
        db = _get_client()
        customers = (
            db.table("customers")
            .select("id, name, email, tier")
            .ilike("email", f"%{email}%")
            .execute()
        )
        if not customers.data:
            return {"error": f"No customer found with email '{email}'"}

        customer = customers.data[0]
        orders = (
            db.table("orders")
            .select("*")
            .eq("customer_id", customer["id"])
            .execute()
        )
        return {
            "customer": customer,
            "orders": orders.data,
            "order_count": len(orders.data),
        }
    except Exception as e:
        return {"error": str(e)}


# ------------------------------------------------------------------
# Agent definition
# ------------------------------------------------------------------
billing_agent = Agent(
    name="billing_agent",
    model="gemini-2.5-flash",
    instruction="""You are a Billing & Orders specialist agent.

You have tools to look up orders and customer info from our database.
Use the tools to fetch real data — never guess or make up order details.

Available tools:
- get_orders_for_customer(customer_name) — look up by name
- get_orders_by_email(email) — look up by email
- get_order_by_id(order_id) — look up a specific order

Order status values: 'delivered', 'processing', 'cancelled', 'return_initiated'
Customer tier values: 'standard', 'premium'

Your responsibilities:
- Look up order status and history for customers
- Answer billing and payment questions
- Explain order details clearly

If the customer gives their name, use get_orders_for_customer first.
If you have an order ID, use get_order_by_id.
Be concise, clear, and professional.
""",
    tools=[get_orders_for_customer, get_order_by_id, get_orders_by_email],
)
