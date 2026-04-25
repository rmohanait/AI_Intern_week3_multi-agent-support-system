"""
A2A Server — Stretch Goal: Expose support_system via ADK's A2A protocol.

This script starts ADK's FastAPI server with the --a2a flag enabled,
exposing the support_system as a proper A2A (Agent-to-Agent) service.

A2A endpoints (available once running):
  GET  /apps/support_system/.well-known/agent.json  — Agent Card (capabilities)
  POST /apps/support_system/runs                     — Start a new run
  GET  /apps/support_system/runs/{run_id}            — Poll run status
  POST /apps/support_system/sessions                 — Create a session

Usage:
  Local development (port 8080):
      python a2a_server.py

  Or directly via adk CLI:
      adk api_server --a2a --host 0.0.0.0 --port 8080 .

  Railway deployment:
      See a2a.railway.toml for the configuration.

Environment variables (same as adk web):
  GOOGLE_API_KEY or GOOGLE_GENAI_USE_VERTEXAI — required for Gemini
  SUPABASE_URL, SUPABASE_KEY                  — required for Supabase tools
"""

import os
import subprocess
import sys


def main():
    port = os.getenv("PORT", "8080")
    host = os.getenv("HOST", "0.0.0.0")

    cmd = [
        "adk", "api_server",
        "--a2a",
        "--host", host,
        "--port", port,
        ".",   # agents directory — ADK discovers support_system/ automatically
    ]

    print(f"Starting A2A server on {host}:{port}")
    print(f"Agent Card will be available at: http://{host}:{port}/apps/support_system/.well-known/agent.json")
    print(f"Command: {' '.join(cmd)}")
    print()

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nA2A server stopped.")
        sys.exit(0)


if __name__ == "__main__":
    main()
