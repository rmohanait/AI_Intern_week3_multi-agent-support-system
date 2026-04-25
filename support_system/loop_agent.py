"""
Support Reply Loop Agent — LoopAgent stretch goal.

Demonstrates ADK's LoopAgent pattern for iterative draft/review cycles.

Architecture:
  reply_drafter  → writes a polished customer-facing reply
  reply_reviewer → checks tone, accuracy, clarity; calls exit_loop() to approve
  support_reply_loop (LoopAgent) → runs drafter → reviewer up to 3 times

Usage:
  This agent is a sub-agent of support_agent. After the support agent
  has gathered context (ticket info, escalation status, etc.), it delegates
  to support_reply_loop to compose and polish the final reply.

  The loop exits when:
    (a) reply_reviewer approves the draft and calls exit_loop(), or
    (b) max_iterations=3 is reached (last draft is used as-is)
"""

from google.adk.agents import Agent, LoopAgent
from google.adk.tools import exit_loop


# ------------------------------------------------------------------
# Drafter Agent — writes the first (and revised) draft
# ------------------------------------------------------------------
reply_drafter_agent = Agent(
    name="reply_drafter",
    model="gemini-2.5-flash",
    instruction="""You are a customer support reply drafter.

Your job: read the conversation so far and write a polished, customer-facing reply.

If the reviewer has given feedback on a previous draft, incorporate that feedback
exactly — don't repeat the same mistakes.

Drafting guidelines:
  - Open with a warm acknowledgement of the customer's situation
  - Be specific: reference what was actually done (e.g., "Your ticket #42 has been
    escalated to our senior team", "Your order #7 is currently in processing")
  - Keep it concise — 3 to 5 sentences maximum
  - End with a clear next step or timeline for the customer
  - Professional but human tone — avoid robotic phrases like "I apologize for any
    inconvenience" or excessive exclamation marks

Output ONLY the reply text. No preamble like "Here is my draft:" or "Draft:".
""",
)


# ------------------------------------------------------------------
# Reviewer Agent — approves or requests revisions
# ------------------------------------------------------------------
reply_reviewer_agent = Agent(
    name="reply_reviewer",
    model="gemini-2.5-flash",
    instruction="""You are a quality reviewer for customer support replies.

Review the most recent draft from reply_drafter and evaluate it on 4 criteria:

  1. Tone       — Warm and professional? (not cold, not sycophantic)
  2. Accuracy   — Reflects what was actually done in this conversation?
  3. Clarity    — Easy to understand, free of jargon?
  4. Completeness — Gives the customer a clear next step or timeline?

Decision:
  → If the draft PASSES all 4 criteria: call exit_loop() immediately.
    Say "APPROVED" before calling exit_loop so the drafter knows.
  → If the draft FAILS any criterion: DO NOT call exit_loop.
    Instead, write a short revision note (max 2 sentences per issue) explaining
    exactly what needs to change. The drafter will revise on the next iteration.

Be strict but fair. A reply that is merely "okay" should still be approved
if it meets all 4 criteria at an acceptable level.
""",
    tools=[exit_loop],
)


# ------------------------------------------------------------------
# LoopAgent — runs drafter → reviewer up to 3 times
# ------------------------------------------------------------------
support_reply_loop = LoopAgent(
    name="support_reply_loop",
    description="Iteratively drafts and reviews a customer support reply until approved.",
    sub_agents=[reply_drafter_agent, reply_reviewer_agent],
    max_iterations=3,
)
