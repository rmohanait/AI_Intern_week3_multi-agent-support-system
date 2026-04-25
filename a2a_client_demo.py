"""
A2A Client Demo — shows how another agent (or service) can call the
support_system A2A server using standard HTTP requests.

This demonstrates the A2A protocol: the caller is also an agent or service
that needs to query customer support programmatically.

Usage:
  # 1. Start the A2A server in one terminal:
  #    adk api_server --a2a --host 0.0.0.0 --port 8080 .
  #
  # 2. Run this demo in another terminal:
  #    python a2a_client_demo.py

Requires: httpx (pip install httpx)
"""

import json
import time

try:
    import httpx
except ImportError:
    print("Install httpx first: pip install httpx")
    raise

BASE_URL = "http://localhost:8080/apps/support_system"


def discover_agent():
    """Fetch the Agent Card — the A2A capability manifest."""
    resp = httpx.get(f"{BASE_URL}/.well-known/agent.json")
    resp.raise_for_status()
    card = resp.json()
    print("=== Agent Card ===")
    print(f"  Name:        {card.get('name', 'unknown')}")
    print(f"  Description: {card.get('description', 'n/a')}")
    print(f"  Version:     {card.get('version', 'n/a')}")
    return card


def create_session() -> str:
    """Create a new session and return the session ID."""
    resp = httpx.post(f"{BASE_URL}/sessions", json={})
    resp.raise_for_status()
    session = resp.json()
    session_id = session["id"]
    print(f"\n=== Session created: {session_id} ===")
    return session_id


def run_query(session_id: str, query: str) -> str:
    """Send a message and wait for the response."""
    print(f"\n>>> User: {query}")

    payload = {
        "session_id": session_id,
        "new_message": {
            "role": "user",
            "parts": [{"text": query}]
        }
    }
    resp = httpx.post(f"{BASE_URL}/run", json=payload, timeout=60.0)
    resp.raise_for_status()

    # Extract the final text response
    result = resp.json()
    for event in reversed(result.get("events", [])):
        content = event.get("content", {})
        if content.get("role") == "model":
            parts = content.get("parts", [])
            for part in parts:
                if "text" in part:
                    reply = part["text"].strip()
                    print(f"<<< Agent: {reply}")
                    return reply

    print("<<< Agent: (no response)")
    return ""


def main():
    print("A2A Client Demo — Customer Support System\n")

    # Step 1: Discover the agent
    try:
        discover_agent()
    except httpx.ConnectError:
        print("ERROR: Cannot connect to A2A server.")
        print("Start it first with: adk api_server --a2a --host 0.0.0.0 --port 8080 .")
        return

    # Step 2: Create a session
    session_id = create_session()

    # Step 3: Run test queries
    queries = [
        "Hi, can you check orders for Alice Johnson?",
        "And what is the status of order number 2?",
    ]

    for query in queries:
        run_query(session_id, query)
        time.sleep(1)  # Be polite to the API

    print("\n=== Demo complete ===")


if __name__ == "__main__":
    main()
