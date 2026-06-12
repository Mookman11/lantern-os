---
description: /debug invokes the diagnostic and transparency assistant for Lantern Dream Journal (ORION). It provides real-time visibility into Convergence IO — routing, fallbacks, tier enforcement, and symbolic processing. Use it when something behaves unexpectedly, when a canned response appears, or when you need to verify which provider/agent/door is active.
---

## Steps

1. **Identify the symptom.** What is wrong? Canned response? Wrong agent? Offline fallback when online expected? Wrong door opened?
2. **Check server state.** Is the server running? Which PID? What is the working directory? Is it the expected repo?
3. **Verify API endpoints.** Hit `/api/health`, `/api/agent/health`, and the relevant chat endpoint with curl/Invoke-RestMethod. Inspect the response body and `source` field.
4. **Trace the code path.** Find where the response originates: `dreamChatReply`, `streamFromServer`, `cloud-server.js`, or offline fallback. grep for the exact reply text.
5. **Check environment.** Are `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, or `OLLAMA_BASE_URL` set? Which provider was requested vs which was attempted?
6. **Inspect recent commits.** Is the running code from before or after a relevant fix? `git log` the file that should have changed.
7. **Report findings.** State the root cause, the fix or workaround, and whether a server restart or commit is needed.
