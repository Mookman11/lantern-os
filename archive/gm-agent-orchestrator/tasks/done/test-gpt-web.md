# Test GPT Web Agent

role_owner: claude
fallback_owner: claude
risk_class: low
budget_class: minimal
terminal_rule: done|failed

## Objective

Verify the Crash Cart GPT Web API fallback system works end-to-end.

## Task

Send a test message to the GPT Web API at `http://localhost:3000/api/chat` and verify response.

Message: "What is 2+2?"

Expected: Response contains actual text from ChatGPT.

## Success Criteria

- Response received from API
- Response contains substantive content (not error)
