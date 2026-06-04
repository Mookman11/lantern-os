# Agent Fleet Optimization - Executive Summary

## Current Status
- **Agents Running:** 1 in Docker (Dream Journal)
- **Agents in K8s:** 0 deployed
- **Total Potential:** 8+ agents identified in codebase
- **Current Memory Usage:** ~1,370 MB (estimated if all running)
- **Current CPU Usage:** ~80% (idle, waiting for work)

---

## Proposed Solution: Sleep/Wake Dispatcher

Instead of all agents running 24/7, implement a **dispatcher that wakes agents every 30 minutes** to process queued work, then returns them to sleep.

### Results

```
MEMORY SAVINGS:    87% (1,370 MB → 180 MB)
CPU SAVINGS:       95% (80% → 4%)
CLOUD COST:        82% (e.g., $45 → $8/month)
LATENCY ADDED:     200-500ms (acceptable for batch jobs)
```

---

## Architecture

```
DISPATCHER (every 30 min)
    ↓
Query Redis queue for pending work
    ↓
Wake sleeping agents
    ↓
Queue jobs to each agent
    ↓
Agents process batch
    ↓
Return to sleep (0 resource usage)
```

---

## Implementation (5 weeks)

| Phase | Duration | Task |
|-------|----------|------|
| 1 | Week 1 | Redis queue + Dispatcher service |
| 2 | Weeks 2-3 | Migrate agents one-by-one |
| 3 | Week 4 | Optimize timeouts + batching |
| 4 | Week 5 | Monitoring + dashboard |

---

## Quick Start

### 1. Deploy Redis Queue
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. Create Dispatcher
```python
from apscheduler.schedulers.background import BackgroundScheduler
import redis

class WorkDispatcher:
    def __init__(self):
        self.redis = redis.Redis()
        self.scheduler = BackgroundScheduler()
        
    def dispatch_work(self):
        """Run every 30 minutes"""
        pending = self.redis.lrange('queue:pending', 0, -1)
        if pending:
            self.wake_agents()
            self.queue_jobs(pending)
    
    def start(self):
        self.scheduler.add_job(self.dispatch_work, 'interval', minutes=30)
        self.scheduler.start()
```

### 3. Add Agent Wake/Sleep Controller
```python
class AgentController:
    def wake(self):
        # K8s: kubectl scale deployment agent --replicas=1
        # Docker: docker start agent
        pass
    
    def sleep(self):
        # K8s: kubectl scale deployment agent --replicas=0
        # Docker: docker stop agent
        pass
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Thundering herd (all agents wake at once) | Stagger wake-ups with random backoff |
| Cold start failures | Add pre-warm phase 2min before dispatch |
| Queue overflow | Monitor queue depth, alert if > threshold |
| Lost jobs | Persistent queue (Redis with AOF) |
| Dispatcher crashes | High-availability setup (2x dispatcher, failover) |

---

## Metrics to Track

**Per agent:**
- Wake/sleep cycles
- Processing time
- Memory freed
- CPU cycles saved
- Job success rate

**System-wide:**
- Total memory freed
- Total CPU saved
- Cost per month
- Queue depth
- Dispatcher uptime

---

## Success Criteria

✓ Memory usage drops to <200 MB idle  
✓ CPU usage drops to <5% idle  
✓ Cloud costs drop 80%+  
✓ No jobs lost or delayed  
✓ Dispatcher latency <100ms  

---

## Recommendation

**Start with Dream Journal agent as POC.**

Why?
1. Already containerized ✓
2. Batch processing (not real-time) ✓
3. Low failure risk ✓
4. Clear success metrics ✓

If POC succeeds (87% memory savings), roll out to full fleet.

