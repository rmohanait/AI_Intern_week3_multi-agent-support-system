"""
Returns Agent — handles return requests and refund eligibility.

Checks the 30-day return window and initiates returns via Supabase.
"""

import os
from datetime import datetime, date
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
# Tool: check_return_eligibility
# ------------------------------------------------------------------
def check_return_eligibility(order_id: int) -> dict:
    """Check whether an order is eligible for a return.

    Eligibility rules:
      - Order must exist and be in 'delivered' status
      - Order must have been placed within the last 30 days
      - Order must not already be in 'return_initiated' status

    Args:
        order_id: The ID of the order to check.

    Returns:
        A dict with 'eligible' (bool), 'reason', and order details.
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
            return {
                "eligible": False,
                "reason": f"Order #{order_id} not found.",
                "order_id": order_id,
            }

        order = result.data[0]

        if order["status"] == "cancelled":
            return {
                "eligible": False,
                "reason": "Cancelled orders are not eligible for returns.",
                "order": order,
            }

        if order["status"] == "processing":
            return {
                "eligible": False,
                "reason": "Order is still processing. Returns can only be initiated after delivery.",
                "order": order,
            }

        if order["status"] == "return_initiated":
            return {
                "eligible": False,
                "reason": "A return has already been initiated for this order.",
                "order": order,
            }

        order_date = datetime.strptime(order["order_date"], "%Y-%m-%d").date()
        days_since_order = (date.today() - order_date).days

        if days_since_order > 30:
            return {
                "eligible": False,
                "reason": f"Return window has expired. Order was placed {days_since_order} days ago (limit: 30 days).",
                "order": order,
                "days_since_order": days_since_order,
            }

        return {
            "eligible": True,
            "reason": f"Order is eligible for return. Placed {days_since_order} days ago.",
            "order": order,
            "days_since_order": days_since_order,
            "days_remaining": 30 - days_since_order,
        }

    except Exception as e:
        return {"eligible": False, "reason": f"Error checking eligibility: {str(e)}"}


# ------------------------------------------------------------------
# Tool: initiate_return
# ------------------------------------------------------------------
def initiate_return(order_id: int, reason: str) -> dict:
    """Initiate a return for a delivered order.

    This updates the order status to 'return_initiated' and logs the reason.
    Always call check_return_eligibility first before calling this tool.

    Args:
        order_id: The ID of the order to return.
        reason:   The customer's reason for returning the item.

    Returns:
        A dict confirming the return initiation or an error.
    """
    try:
        db = _get_client()

        result = (
            db.table("orders")
            .update({"status": "return_initiated"})
            .eq("id", order_id)
            .eq("status", "delivered")
            .execute()
        )

        if not result.data:
            return {
                "success": False,
                "message": f"Could not initiate return for order #{order_id}. "
                           "It may not exist or may not be in 'delivered' status.",
            }

        order = result.data[0]
        return {
            "success": True,
            "message": (
                f"Return successfully initiated for order #{order_id} "
                f"({order['product']}, ${order['amount']}).\n"
                f"Return reason: {reason}\n"
                f"You will receive a prepaid shipping label within 24 hours. "
                f"Refund will be processed within 5-7 business days after we receive the item."
            ),
            "order": order,
            "return_reason": reason,
        }

    except Exception as e:
        return {"success": False, "message": f"Error initiating return: {str(e)}"}


# ------------------------------------------------------------------
# Returns Agent
# ------------------------------------------------------------------
returns_agent = Agent(
    name="returns_agent",
    model="gemini-2.5-flash",
    instruction="""You are a Returns & Refunds specialist agent.

You help customers return products and process refunds.

Your workflow for any return request:
  1. Ask for the order ID if not provided
  2. Call check_return_eligibility(order_id) to verify eligibility
  3. If NOT eligible: explain clearly why, and what alternatives exist
  4. If eligible: confirm with the customer what they want to return and why
  5. Call initiate_return(order_id, reason) to process it
  6. Summarize the next steps for the customer

Be empathetic — customers returning items may be frustrated.
Always explain the return process clearly (shipping label, refund timeline).
For premium-tier customers, mention expedited processing.

Return policy summary:
  - 30-day return window from order date
  - Items must have been delivered (not processing or cancelled)
  - Refund in 5-7 business days after receipt
  - Free prepaid shipping label provided
""",
    tools=[check_return_eligibility, initiate_return],
)
