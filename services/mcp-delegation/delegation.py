"""
MCP Local Delegation Service
Enables local coordination and delegation between agents via MCP
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, asdict, field
from enum import Enum

class AgentStatus(Enum):
    SLEEPING = "sleeping"
    IDLE = "idle"
    WORKING = "working"
    ERROR = "error"
    UNREACHABLE = "unreachable"

@dataclass
class AgentMetrics:
    """Agent performance metrics"""
    name: str
    status: AgentStatus = AgentStatus.SLEEPING
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    last_heartbeat: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    jobs_completed: int = 0
    jobs_failed: int = 0
    avg_latency_ms: float = 0.0
    uptime_seconds: int = 0

@dataclass
class SwarmAgent:
    """Swarm agent representation"""
    id: str
    name: str
    agent_type: str
    endpoint: str
    port: int
    status: AgentStatus = AgentStatus.SLEEPING
    metrics: AgentMetrics = field(default_factory=lambda: AgentMetrics(name="default"))
    last_ping: float = 0.0
    delegation_count: int = 0

class MCPDelegationService:
    """MCP-based local delegation coordinator"""
    
    def __init__(self, mcp_gateway_url: str = "http://localhost:8000"):
        self.gateway_url = mcp_gateway_url
        self.agents: Dict[str, SwarmAgent] = {}
        self.delegation_history: List[Dict] = []
        self.swarm_state = {
            "total_agents": 0,
            "active_agents": 0,
            "working_agents": 0,
            "failed_agents": 0,
            "total_delegations": 0,
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def register_agent(self, agent: SwarmAgent):
        """Register agent in swarm"""
        self.agents[agent.id] = agent
        self.swarm_state["total_agents"] = len(self.agents)
        print(f"[MCP] Agent registered: {agent.name} ({agent.agent_type})")
    
    def register_agents_batch(self, agents: List[SwarmAgent]):
        """Register multiple agents"""
        for agent in agents:
            self.register_agent(agent)
        print(f"[MCP] Registered {len(agents)} agents")
    
    async def health_check_all(self):
        """Check health of all agents"""
        print(f"\n[MCP] Health checking {len(self.agents)} agents...")
        
        for agent_id, agent in self.agents.items():
            await self.ping_agent(agent)
    
    async def ping_agent(self, agent: SwarmAgent):
        """Ping individual agent"""
        import time
        try:
            # Simulate HTTP health check
            start = time.time()
            
            # In production: requests.get(f"http://{agent.endpoint}:{agent.port}/health")
            # For now, mock successful ping
            await asyncio.sleep(0.1)
            
            elapsed = (time.time() - start) * 1000
            agent.last_ping = time.time()
            agent.status = AgentStatus.IDLE
            
            print(f"[PING] {agent.name}: OK ({elapsed:.0f}ms)")
            
        except Exception as e:
            agent.status = AgentStatus.UNREACHABLE
            print(f"[PING] {agent.name}: FAIL ({str(e)})")
    
    async def delegate_work(self, agent_id: str, job: Dict[str, Any]) -> Dict:
        """Delegate work to specific agent"""
        if agent_id not in self.agents:
            return {"error": f"Agent {agent_id} not found", "held": True}
        
        agent = self.agents[agent_id]
        
        if agent.status == AgentStatus.SLEEPING:
            print(f"[DELEGATE] Waking {agent.name}...")
            agent.status = AgentStatus.IDLE
        
        if agent.status != AgentStatus.IDLE:
            return {"error": f"Agent {agent.name} not available", "held": True}
        
        # Transition to working
        agent.status = AgentStatus.WORKING
        agent.delegation_count += 1
        
        print(f"[DELEGATE] Job assigned to {agent.name}: {job.get('id', 'unknown')}")
        
        try:
            # Simulate work execution
            import time
            start = time.time()
            await asyncio.sleep(0.5)  # Simulate processing
            elapsed = (time.time() - start) * 1000
            
            # Update metrics
            agent.metrics.jobs_completed += 1
            agent.metrics.avg_latency_ms = (agent.metrics.avg_latency_ms + elapsed) / 2
            agent.status = AgentStatus.IDLE
            
            delegation = {
                "timestamp": datetime.utcnow().isoformat(),
                "agent_id": agent_id,
                "job_id": job.get("id"),
                "status": "completed",
                "latency_ms": elapsed
            }
            
            self.delegation_history.append(delegation)
            self.swarm_state["total_delegations"] += 1
            
            return {
                "success": True,
                "agent": agent.name,
                "job_id": job.get("id"),
                "latency_ms": elapsed
            }
            
        except Exception as e:
            agent.metrics.jobs_failed += 1
            agent.status = AgentStatus.ERROR
            return {"error": str(e), "held": True}
    
    async def smart_delegation(self, job: Dict[str, Any]) -> Dict:
        """Auto-select best agent and delegate"""
        print(f"\n[SMART-DELEGATE] Finding best agent for job: {job.get('id')}")
        
        # Filter available agents
        available = [
            a for a in self.agents.values()
            if a.status in [AgentStatus.IDLE, AgentStatus.SLEEPING]
        ]
        
        if not available:
            return {"error": "No agents available", "held": True}
        
        # Select by least latency
        best_agent = min(available, key=lambda a: a.metrics.avg_latency_ms or 0)
        
        print(f"[SMART-DELEGATE] Selected: {best_agent.name} (avg {best_agent.metrics.avg_latency_ms:.0f}ms)")
        
        return await self.delegate_work(best_agent.id, job)
    
    def get_swarm_status(self) -> Dict:
        """Get current swarm status"""
        active = sum(1 for a in self.agents.values() if a.status != AgentStatus.SLEEPING)
        working = sum(1 for a in self.agents.values() if a.status == AgentStatus.WORKING)
        failed = sum(1 for a in self.agents.values() if a.status == AgentStatus.ERROR)
        
        return {
            "total_agents": len(self.agents),
            "active_agents": active,
            "working_agents": working,
            "error_agents": failed,
            "idle_agents": active - working,
            "total_delegations": self.swarm_state["total_delegations"],
            "agents": [
                {
                    "id": a.id,
                    "name": a.name,
                    "status": a.status.value,
                    "jobs_completed": a.metrics.jobs_completed,
                    "avg_latency_ms": a.metrics.avg_latency_ms,
                    "delegation_count": a.delegation_count
                }
                for a in self.agents.values()
            ]
        }
    
    def get_metrics_summary(self) -> Dict:
        """Get swarm-wide metrics"""
        total_jobs = sum(a.metrics.jobs_completed for a in self.agents.values())
        total_failed = sum(a.metrics.jobs_failed for a in self.agents.values())
        avg_latency = sum(a.metrics.avg_latency_ms for a in self.agents.values()) / len(self.agents) if self.agents else 0
        
        return {
            "total_jobs_completed": total_jobs,
            "total_jobs_failed": total_failed,
            "swarm_avg_latency_ms": avg_latency,
            "success_rate": (total_jobs / (total_jobs + total_failed) * 100) if (total_jobs + total_failed) > 0 else 0,
            "agents_summary": {
                "sleeping": sum(1 for a in self.agents.values() if a.status == AgentStatus.SLEEPING),
                "idle": sum(1 for a in self.agents.values() if a.status == AgentStatus.IDLE),
                "working": sum(1 for a in self.agents.values() if a.status == AgentStatus.WORKING),
                "error": sum(1 for a in self.agents.values() if a.status == AgentStatus.ERROR)
            }
        }

if __name__ == "__main__":
    import asyncio
    
    # Test
    service = MCPDelegationService()
    
    # Register agents
    agents = [
        SwarmAgent(
            id="agent_001",
            name="dream_journal",
            agent_type="dream_journal",
            endpoint="localhost",
            port=5000
        ),
        SwarmAgent(
            id="agent_002",
            name="audit_verify",
            agent_type="audit",
            endpoint="localhost",
            port=5001
        ),
        SwarmAgent(
            id="agent_003",
            name="bayesian_model",
            agent_type="bayesian",
            endpoint="localhost",
            port=5002
        )
    ]
    
    service.register_agents_batch(agents)
    
    async def test():
        # Health check
        await service.health_check_all()
        
        # Delegate work
        job = {"id": "job_001", "type": "dream_log"}
        result = await service.smart_delegation(job)
        print(f"\nDelegation result: {json.dumps(result, indent=2)}")
        
        # Status
        print(f"\nSwarm status:\n{json.dumps(service.get_swarm_status(), indent=2)}")
        print(f"\nMetrics:\n{json.dumps(service.get_metrics_summary(), indent=2)}")
    
    asyncio.run(test())
