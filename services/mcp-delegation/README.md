# MCP Local Delegation + Agent Swarm + Real-Time Dashboard

**Status:** Production-Ready POC  
**Date:** June 2, 2026  
**Components:** MCP Delegation Service, Swarm Orchestrator, Real-Time Dashboard

---

## What This Does

Converts your Docker agent fleet into a **coordinated swarm** with:
- ✅ **Local MCP Delegation** — Smart agent selection + work distribution
- ✅ **Agent Swarm Management** — Multi-agent orchestration
- ✅ **Real-Time Dashboard** — Live agent status visualization (working/idle/sleeping)
- ✅ **Auto-Scaling** — Scale agents up/down on demand
- ✅ **Health Monitoring** — Continuous agent health checks
- ✅ **Smart Routing** — Delegate to fastest available agent

---

## Quick Start (5 Minutes)

### 1. Install Dependencies
```bash
cd lantern-os/services/mcp-delegation
pip install -r requirements.txt
```

### 2. Start Dashboard
```bash
python dashboard.py
```

**Visit:** http://localhost:5100

### 3. Run Swarm Demo
```bash
python orchestrator.py
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│      MCP Delegation Service             │
│  • Smart agent selection                │
│  • Work distribution                    │
│  • Metrics collection                   │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────────────────┐
    │                             │
    v                             v
┌──────────────────┐    ┌──────────────────┐
│ Swarm Agents     │    │ Real-Time        │
│ • Dream Journal  │    │ Dashboard        │
│ • Audit API      │    │ • Status view    │
│ • Bayesian Model │    │ • Metrics        │
│ • Lucid Dream    │    │ • Live updates   │
│ • Stats Monitor  │    └──────────────────┘
└──────────────────┘
```

---

## API Endpoints

### Dashboard UI
```
GET http://localhost:5100/
```

### Status API
```
GET http://localhost:5100/api/status
Returns: {total_agents, active_agents, working_agents, agents: [...]}
```

### Metrics API
```
GET http://localhost:5100/api/metrics
Returns: {total_jobs_completed, success_rate, swarm_avg_latency_ms, agents_summary}
```

### Agents API
```
GET http://localhost:5100/api/agents
Returns: Detailed agent list with metrics
```

### Test Delegation
```
POST http://localhost:5100/api/delegation/test
Returns: {success, agent, latency_ms} or {error, held}
```

---

## Dashboard Features

### Metrics Card
- Total Agents
- Active Agents
- Currently Working
- Average Latency

### Agent Cards (Real-Time)
- Agent name
- Status (sleeping/idle/working/error)
- Jobs completed
- Average latency
- Delegation count
- Endpoint

### Activity Log
- Live event stream
- Delegation results
- Errors and warnings

### Test Controls
- "Test Delegation" — Send a test job
- "Refresh" — Manual dashboard refresh
- Auto-updates every 3 seconds

---

## Agent States

| State | Meaning | Action |
|-------|---------|--------|
| **SLEEPING** | Not running | Woken by dispatcher |
| **IDLE** | Ready but not working | Can accept jobs |
| **WORKING** | Processing a job | No new jobs |
| **ERROR** | Failed state | Needs recovery |
| **UNREACHABLE** | Health check failed | Network issue |

---

## Usage Example

### Python Client
```python
from delegation import MCPDelegationService, SwarmAgent
import asyncio

service = MCPDelegationService()

# Register agents
agents = [
    SwarmAgent(id="a1", name="Dream Journal", agent_type="dream_journal", 
               endpoint="localhost", port=5000),
    SwarmAgent(id="a2", name="Audit API", agent_type="audit", 
               endpoint="localhost", port=5001)
]
service.register_agents_batch(agents)

# Delegate work
async def work():
    job = {"id": "job_001", "type": "test"}
    result = await service.smart_delegation(job)
    print(result)

asyncio.run(work())
```

### cURL
```bash
# Test delegation
curl -X POST http://localhost:5100/api/delegation/test

# Get status
curl http://localhost:5100/api/status

# Get agents
curl http://localhost:5100/api/agents
```

---

## Scaling

### Add Agents
```python
orchestrator = SwarmOrchestrator(delegation_service)
await orchestrator.scale_swarm(target_agents=10)
```

### Remove Agents
```python
# Orchestrator will gracefully drain and remove
await orchestrator.scale_swarm(target_agents=3)
```

---

## Monitoring

### Live Metrics
Dashboard auto-refreshes every 3 seconds showing:
- Agent status
- Job counts
- Latency trends
- Success rates

### Programmatic Access
```python
metrics = service.get_metrics_summary()
print(metrics)
# {
#   "total_jobs_completed": 150,
#   "success_rate": 98.5,
#   "swarm_avg_latency_ms": 45.2,
#   "agents_summary": {...}
# }
```

---

## Performance

**Expected Metrics:**
- Agent health check: 10-50ms
- Smart delegation: 30-100ms
- Job latency: 50-500ms (depends on task)
- Dashboard update: <1s (3s interval)

---

## Files

```
lantern-os/services/mcp-delegation/
├── delegation.py          (MCP service + SwarmAgent)
├── orchestrator.py        (Swarm orchestration)
├── dashboard.py          (Real-time web dashboard)
├── requirements.txt
└── README.md
```

---

## Next Steps

1. **Start Dashboard** → See agents in real-time
2. **Test Delegation** → Send jobs via UI
3. **Scale Up** → Add more agents
4. **Monitor Metrics** → Track performance
5. **Integrate with Dream Journal** → Add dispatcher trigger

---

**Status: ✅ PRODUCTION-READY**

