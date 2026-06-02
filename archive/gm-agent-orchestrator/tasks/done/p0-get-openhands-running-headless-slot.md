# P0: Get OpenHands running on headless slot (first run)

## Context
Facilitator evaluation complete (done/p0-evaluate-openhands-headless-facilitator-issue-196.md).
OpenHands headless selected as facilitator for issue #196.
Blocker: headless worktree is unprepared and no OpenHands install/run has been validated.

## Acceptance criteria
- [ ] OpenHands installed and runnable on this machine (pip install or docker)
- [ ] headless slot worktree prepared (git worktree present and clean)
- [ ] OpenHands runs at least one task in headless/non-interactive mode successfully
- [ ] AGENT_LOG.md updated with install method, version, and first-run result
- [ ] If docker path: confirm docker desktop is running and image pulled

## Slot
headless

## Instructions
1. Check if OpenHands is already installed: \pip show openhands\ or \docker images | grep openhands\
2. If not installed, install via: \pip install openhands-ai\ or pull docker image per docs
3. Prepare headless worktree: run the orch worktree setup script for slot=headless
4. Run a smoke test task headlessly and log the output
5. Update AGENT_LOG.md and complete this task via MCP complete_task action
