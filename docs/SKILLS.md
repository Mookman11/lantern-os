# Lantern OS — Skills Inventory (Canonical Entry Point)

This is the single source of truth for every skill available to agents working on Lantern OS.

**Global (built-in) skills** are available to all projects.  
**Project skills** live under `.devin/skills/` inside this repo.

---

## Global Built-In Skills

These skills are provided by the Devin CLI and are always available.

| Skill | Purpose | When to invoke |
|---|---|---|
| **devin-for-terminal** | Devin CLI docs, commands, models, troubleshooting, configuration | `skill skill="devin-for-terminal"` |
| **declarative-repo-setup** | Generate and verify `environment.yaml` (Devin snapshot-setup blueprint) | `skill skill="declarative-repo-setup"` |

---

## Azure Skills

| Skill | Purpose | When to invoke |
|---|---|---|
| **azure-cost** | Query historical costs, forecast spending, optimize waste | Azure bills, cost by service/resource, trends, orphaned resources |
| **azure-ai** | AI Search, Speech, OpenAI, Document Intelligence | Vector/hybrid search, STT/TTS, OCR |
| **azure-hosted-copilot-sdk** | Build/deploy @github/copilot-sdk apps on Azure | CopilotClient, createSession, BYOM |
| **azure-deploy** | Run azd up / terraform apply / bicep deploy for prepared apps | Already has `.azure/deployment-plan.md` |
| **microsoft-foundry** | Deploy, evaluate, fine-tune Foundry agents | Agent deploy, SFT/DPO, prompt optimizer |
| **appinsights-instrumentation** | Instrument webapps with Application Insights | Telemetry patterns, SDK setup |
| **azure-kusto** | Query Azure Data Explorer (KQL) | Log analytics, time series, IoT telemetry |
| **azure-aigateway** | Configure API Management as AI Gateway | Semantic caching, token limits, MCP rate limiting |
| **azure-compliance** | Run compliance/security audits with azqr | Best-practice assessment, Key Vault expirations |
| **azure-diagnostics** | Debug Azure production issues | AppLens, AKS troubleshooting, log analysis |
| **azure-compute** | VM/VMSS recommendations, pricing, autoscale | VM family selection, connectivity, capacity reservations |
| **azure-enterprise-infra-planner** | Architect enterprise Azure infrastructure | Landing zones, hub-spoke, multi-region DR |
| **airunway-aks-setup** | Set up AI Runway on AKS | vLLM, KAITO, GPU inference on AKS |
| **azure-messaging** | Troubleshoot Event Hubs / Service Bus SDK errors | AMQP failures, message lock lost, dead letter |
| **azure-quotas** | Check/manage Azure quotas and capacity | vCPU limits, regional availability |
| **azure-storage** | Blob, File Shares, Queue, Table, Data Lake | Tiers (hot/cool/cold/archive), lifecycle management |
| **azure-resource-lookup** | List/find Azure resources across subscriptions | Resource inventory, tag analysis, orphaned disks |
| **azure-upgrade** | Upgrade Azure plans, tiers, SKUs, SDKs | Consumption→Flex, Redis migration, SDK modernization |
| **azure-validate** | Pre-deployment validation | Preflight checks, RBAC, what-if analysis |
| **azure-rbac** | Find least-privilege RBAC roles | Role assignment CLI/Bicep generation |
| **azure-cloud-migrate** | Cross-cloud migration (AWS/GCP → Azure) | Lambda→Functions, ECS→Container Apps |
| **azure-kubernetes** | AKS planning, networking, security, ops | SKU selection, CNI Overlay, VPA, spot nodes |
| **azure-prepare** | Prepare Azure apps for deployment (Bicep/Terraform) | Create/modernize apps, add auth, managed identity |
| **azure-resource-visualizer** | Generate Mermaid diagrams of resource groups | Architecture visualization, topology mapping |
| **azure-reliability** | Assess/improve reliability posture | Zone redundancy, failover, health probes |
| **entra-agent-id** | Microsoft Entra Agent Identity Blueprints | fmi_path, OBO, polyglot agent auth |
| **entra-app-registration** | Entra app registration, OAuth, MSAL | Console app auth, API permissions |

---

## How to Invoke a Skill

```bash
# List available skills
skill command=list

# Invoke a specific skill
skill skill="azure-cost"

# Search for skills by keyword
skill command=search path=. keywords="azure"
```

---

## Project-Specific Skills

To add a Lantern OS–specific skill, create:

```
.devin/skills/<skill-name>/
  SKILL.md
```

`SKILL.md` must contain:
- `WHEN:` — exact trigger phrases
- `DO NOT USE FOR:` — negative constraints
- Usage examples

No project-specific skills are currently registered.

---

**Last updated:** 2026-06-05
