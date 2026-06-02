"""
Real-time Agent Swarm Dashboard
WebSocket-based live agent status monitoring
"""

from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import json
import asyncio
from datetime import datetime
from delegation import MCPDelegationService, SwarmAgent, AgentStatus

app = Flask(__name__)
CORS(app)

# Global delegation service
delegation_service = MCPDelegationService()

# Pre-register agents
@app.before_request
def init_agents():
    if len(delegation_service.agents) == 0:
        agents = [
            SwarmAgent(
                id="agent_001",
                name="Dream Journal",
                agent_type="dream_journal",
                endpoint="localhost",
                port=5000
            ),
            SwarmAgent(
                id="agent_002",
                name="Audit Verification",
                agent_type="audit",
                endpoint="localhost",
                port=5001
            ),
            SwarmAgent(
                id="agent_003",
                name="Bayesian Model",
                agent_type="bayesian",
                endpoint="localhost",
                port=5002
            ),
            SwarmAgent(
                id="agent_004",
                name="Lucid Dreaming",
                agent_type="lucid",
                endpoint="localhost",
                port=5003
            ),
            SwarmAgent(
                id="agent_005",
                name="Statistics Monitor",
                agent_type="stats",
                endpoint="localhost",
                port=5004
            )
        ]
        delegation_service.register_agents_batch(agents)

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def get_status():
    """Get current swarm status"""
    return jsonify(delegation_service.get_swarm_status())

@app.route('/api/metrics')
def get_metrics():
    """Get swarm metrics"""
    return jsonify(delegation_service.get_metrics_summary())

@app.route('/api/delegation/test', methods=['POST'])
def test_delegation():
    """Test delegation to random agent"""
    import random
    job = {
        "id": f"job_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "type": "test"
    }
    
    # Synchronous wrapper
    loop = asyncio.new_event_loop()
    result = loop.run_until_complete(delegation_service.smart_delegation(job))
    loop.close()
    
    return jsonify(result)

@app.route('/api/agents')
def get_agents():
    """Get all agents with detailed info"""
    agents_data = []
    for agent_id, agent in delegation_service.agents.items():
        agents_data.append({
            "id": agent_id,
            "name": agent.name,
            "type": agent.agent_type,
            "status": agent.status.value,
            "endpoint": f"{agent.endpoint}:{agent.port}",
            "metrics": {
                "jobs_completed": agent.metrics.jobs_completed,
                "jobs_failed": agent.metrics.jobs_failed,
                "avg_latency_ms": agent.metrics.avg_latency_ms,
                "memory_mb": agent.metrics.memory_mb,
                "cpu_percent": agent.metrics.cpu_percent
            },
            "delegation_count": agent.delegation_count
        })
    return jsonify(agents_data)

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Agent Swarm Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Monaco', monospace; background: #0a0e27; color: #00ff00; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { text-align: center; margin-bottom: 30px; color: #00ffff; text-shadow: 0 0 10px #00ffff; }
        
        .metrics-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .metric-card {
            background: #1a1e3f;
            border: 1px solid #00ff00;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
        }
        
        .metric-card h3 { color: #00ffff; font-size: 12px; margin-bottom: 10px; }
        .metric-card .value { font-size: 32px; color: #00ff00; font-weight: bold; }
        .metric-card .unit { color: #888; font-size: 12px; }
        
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }
        
        .agent-card {
            background: #1a1e3f;
            border: 2px solid #00ff00;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
            transition: all 0.3s;
        }
        
        .agent-card:hover { border-color: #00ffff; box-shadow: 0 0 20px rgba(0, 255, 255, 0.5); }
        
        .agent-card h3 { color: #00ffff; margin-bottom: 10px; }
        
        .status-badge {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        
        .status-sleeping { background: #444; color: #999; }
        .status-idle { background: #0a4; color: #0ff; }
        .status-working { background: #fa0; color: #000; }
        .status-error { background: #f44; color: #fff; }
        
        .agent-metric { display: flex; justify-content: space-between; margin: 8px 0; font-size: 12px; }
        .agent-metric-label { color: #00ffff; }
        .agent-metric-value { color: #00ff00; font-weight: bold; }
        
        .controls { text-align: center; margin: 30px 0; }
        button {
            background: #00ff00;
            color: #000;
            border: none;
            padding: 12px 30px;
            border-radius: 4px;
            font-weight: bold;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        button:hover { background: #00ffff; box-shadow: 0 0 20px rgba(0, 255, 0, 0.5); }
        
        .log { background: #0a0e27; border: 1px solid #00ff00; padding: 15px; border-radius: 4px; max-height: 200px; overflow-y: auto; }
        .log-entry { font-size: 12px; margin: 5px 0; color: #0f0; }
        .log-entry.error { color: #f44; }
        
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .working { animation: pulse 1s infinite; }
        
        .header-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .timestamp { color: #888; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header-info">
            <h1>⚙️ Agent Swarm Dashboard</h1>
            <div class="timestamp">Updated: <span id="timestamp">--:--:--</span></div>
        </div>
        
        <div class="metrics-row">
            <div class="metric-card">
                <h3>Total Agents</h3>
                <div class="value" id="total-agents">0</div>
            </div>
            <div class="metric-card">
                <h3>Active Agents</h3>
                <div class="value" id="active-agents">0</div>
            </div>
            <div class="metric-card">
                <h3>Working</h3>
                <div class="value" id="working-agents">0</div>
            </div>
            <div class="metric-card">
                <h3>Avg Latency</h3>
                <div class="value" id="avg-latency">0</div>
                <div class="unit">ms</div>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="testDelegation()">Test Delegation</button>
            <button onclick="refreshDashboard()">Refresh</button>
        </div>
        
        <h2 style="color: #00ffff; margin: 30px 0 15px 0;">Agents</h2>
        <div class="agents-grid" id="agents-container">
            <!-- Agents will be populated here -->
        </div>
        
        <h2 style="color: #00ffff; margin: 30px 0 15px 0;">Activity Log</h2>
        <div class="log" id="activity-log">
            <div class="log-entry">Waiting for activity...</div>
        </div>
    </div>
    
    <script>
        const logEntries = [];
        
        function addLog(message, isError = false) {
            const timestamp = new Date().toLocaleTimeString();
            logEntries.unshift(`[${timestamp}] ${message}`);
            if (logEntries.length > 20) logEntries.pop();
            
            const logDiv = document.getElementById('activity-log');
            logDiv.innerHTML = logEntries.map(e => 
                `<div class="log-entry ${e.includes('ERROR') ? 'error' : ''}">${e}</div>`
            ).join('');
        }
        
        async function refreshDashboard() {
            try {
                // Fetch metrics
                const metricsResp = await fetch('/api/metrics');
                const metrics = await metricsResp.json();
                
                document.getElementById('total-agents').textContent = metrics.agents_summary.sleeping + metrics.agents_summary.idle + metrics.agents_summary.working + metrics.agents_summary.error;
                document.getElementById('active-agents').textContent = metrics.agents_summary.idle + metrics.agents_summary.working;
                document.getElementById('working-agents').textContent = metrics.agents_summary.working;
                document.getElementById('avg-latency').textContent = Math.round(metrics.swarm_avg_latency_ms);
                
                // Fetch agents
                const agentsResp = await fetch('/api/agents');
                const agents = await agentsResp.json();
                
                const container = document.getElementById('agents-container');
                container.innerHTML = agents.map(agent => `
                    <div class="agent-card">
                        <h3>${agent.name}</h3>
                        <div class="status-badge status-${agent.status}">${agent.status.toUpperCase()}</div>
                        <div class="agent-metric">
                            <span class="agent-metric-label">Type:</span>
                            <span class="agent-metric-value">${agent.type}</span>
                        </div>
                        <div class="agent-metric">
                            <span class="agent-metric-label">Jobs Completed:</span>
                            <span class="agent-metric-value">${agent.metrics.jobs_completed}</span>
                        </div>
                        <div class="agent-metric">
                            <span class="agent-metric-label">Avg Latency:</span>
                            <span class="agent-metric-value">${Math.round(agent.metrics.avg_latency_ms)}ms</span>
                        </div>
                        <div class="agent-metric">
                            <span class="agent-metric-label">Delegations:</span>
                            <span class="agent-metric-value">${agent.delegation_count}</span>
                        </div>
                        <div class="agent-metric">
                            <span class="agent-metric-label">Endpoint:</span>
                            <span class="agent-metric-value" style="font-size: 11px;">${agent.endpoint}</span>
                        </div>
                    </div>
                `).join('');
                
                document.getElementById('timestamp').textContent = new Date().toLocaleTimeString();
                addLog(`Dashboard updated. ${agents.length} agents active.`);
                
            } catch (e) {
                addLog(`ERROR: ${e.message}`, true);
            }
        }
        
        async function testDelegation() {
            try {
                addLog('🚀 Testing delegation...');
                const resp = await fetch('/api/delegation/test', { method: 'POST' });
                const result = await resp.json();
                
                if (result.success) {
                    addLog(`✓ Job delegated to ${result.agent}: ${Math.round(result.latency_ms)}ms`);
                } else {
                    addLog(`✗ Delegation failed: ${result.error}`, true);
                }
                
                // Refresh after 1s
                setTimeout(refreshDashboard, 1000);
            } catch (e) {
                addLog(`ERROR: ${e.message}`, true);
            }
        }
        
        // Auto-refresh every 3 seconds
        setInterval(refreshDashboard, 3000);
        
        // Initial load
        refreshDashboard();
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    print("Starting Agent Swarm Dashboard...")
    print("Visit: http://localhost:5100")
    app.run(host='0.0.0.0', port=5100, debug=False)
