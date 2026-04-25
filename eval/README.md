# Eval Test Cases — Customer Support System

7 test cases covering all 3 agent paths (billing, support, returns) plus routing.

## Running Evals

From the `Week_3/` directory:

```bash
# Run all eval cases
adk eval support_system/agent.py eval/support_evals.json

# Run specific cases
adk eval support_system/agent.py eval/support_evals.json:billing_lookup_by_name,billing_lookup_by_order_id

# Print detailed results
adk eval support_system/agent.py eval/support_evals.json --print_detailed_results
```

## Test Cases

| ID | Agent Path | Description |
|----|-----------|-------------|
| `billing_lookup_by_name` | billing_agent | Look up orders by customer name |
| `billing_lookup_by_order_id` | billing_agent | Look up a specific order by ID |
| `support_ticket_lookup` | support_agent | Check ticket status by customer name |
| `support_escalation_frustrated_customer` | support_agent | Escalation triggered by frustration signals |
| `returns_eligibility_check` | returns_agent | Check return eligibility for an order |
| `returns_initiate_return` | returns_agent | Initiate return for a damaged item |
| `routing_ambiguous_query_clarification` | root router | Ambiguous input triggers clarifying question |

## Eval Format

Each case follows the ADK eval JSON format:

```json
{
  "name": "case_id",
  "data": [
    {
      "query": "customer message",
      "expected_tool_use": [{"tool_name": "...", "tool_input": {...}}],
      "expected_intermediate_agent_responses": [],
      "reference": "expected agent reply (used for response match scoring)"
    }
  ],
  "initial_session": {
    "state": {},
    "app_name": "support_system",
    "user_id": "test_user"
  }
}
```
