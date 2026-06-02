"""
Swarm Orchestrator
Manages agent swarm lifecycle, coordination, and work distribution
"""

import asyncio
import json
from typing import List, Dict, Any
from datetime import datetime
from delegation import MCPDelegationService, SwarmAgent, AgentStatus

class SwarmOrchestrator:
    """Orchestrates multi-agent swarm with MCP delegation"""
    
    def __init__(self, delegation_service: MCPDelegationService):
        self.service = delegation_service
        self.work_queue: List[Dict] = []
        self.running = False
    
    async def start_swarm(self):
        """Start swarm orchestrator"""
        self.running = True
        print("\n[SWARM] 🚀 Starting Agent Swarm Orchestrator...")
        print(f"[SWARM] Registered agents: {len(self.service.agents)}")
        
        # Health check all agents
        await self.service.health_check_all()
        
        print("[SWARM] ✓ Swarm online and ready")
    
    async def distribute_work(self, jobs: List[Dict[str, Any]]):
        """Distribute work across swarm"""
        print(f"\n[SWARM] 📋 Distributing {len(jobs)} jobs...")
        
        for job in jobs:
            if not self.running:
                break
            
            result = await self.service.smart_delegation(job)
            
            if result.get("success"):
                print(f"[SWARM] ✓ {result['agent']}: {result['job_id']} ({result['latency_ms']:.0f}ms)")
            else:
                print(f"[SWARM] ✗ Job {job.get('id')} failed: {result.get('error')}")
            
            await asyncio.sleep(0.1)  # Small delay between delegations
    
    async def monitor_swarm(self, interval: int = 5):
        """Monitor swarm health"""
        print(f"\n[SWARM] 👁️  Starting swarm monitor (interval: {interval}s)...")
        
        while self.running:
            status = self.service.get_swarm_status()
            metrics = self.service.get_metrics_summary()
            
            print(f"\n[MONITOR] {datetime.utcnow().strftime('%H:%M:%S')}")
            print(f"  Active: {status['active_agents']}/{status['total_agents']} | Working: {status['working_agents']}")
            print(f"  Jobs: {metrics['total_jobs_completed']} completed, {metrics['total_jobs_failed']} failed")
            print(f"  Avg latency: {metrics['swarm_avg_latency_ms']:.0f}ms")
            
            await asyncio.sleep(interval)
    
    async def scale_swarm(self, target_agents: int):
        """Scale swarm size (add/remove agents)"""
        current = len(self.service.agents)
        
        if target_agents > current:
            print(f"\n[SCALE] Scaling up: {current} → {target_agents}")
            for i in range(current, target_agents):
                agent = SwarmAgent(
                    id=f"agent_{i+1:03d}",
                    name=f"Agent-{i+1}",
                    agent_type="generic",
                    endpoint="localhost",
                    port=5000 + i
                )
                self.service.register_agent(agent)
        elif target_agents < current:
            print(f"\n[SCALE] Scaling down: {current} → {target_agents}")
            # Would remove agents here
    
    async def run_demo(self):
        """Run demonstration"""
        await self.start_swarm()
        
        # Generate test jobs
        jobs = [
            {"id": f"job_{i:03d}", "type": "test"} 
            for i in range(20)
        ]
        
        # Start monitoring in background
        monitor_task = asyncio.create_task(self.monitor_swarm(interval=3))
        
        # Distribute work
        await self.distribute_work(jobs)
        
        # Final summary
        print("\n[SWARM] 📊 Final Summary:")
        metrics = self.service.get_metrics_summary()
        status = self.service.get_swarm_status()
        
        print(f"  Total Jobs: {metrics['total_jobs_completed']}")
        print(f"  Success Rate: {metrics['success_rate']:.1f}%")
        print(f"  Swarm Avg Latency: {metrics['swarm_avg_latency_ms']:.0f}ms")
        print(f"  Agent States: {metrics['agents_summary']}")
        
        self.running = False
        monitor_task.cancel()

async def main():
    # Initialize delegation service
    delegation_service = MCPDelegationService()
    
    # Create orchestrator
    orchestrator = SwarmOrchestrator(delegation_service)
    
    # Run demo
    await orchestrator.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
