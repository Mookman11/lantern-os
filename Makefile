.PHONY: test test-dream build-dream up-dream down-dream logs-dream pull-dream-model check-node convergence quickstart

test:
	python -m pytest tests -q

test-dream:
	python -m pytest tests/test_fallacy_detector.py tests/test_audit_chain.py tests/test_anti_entropy_memory.py -q

build-dream:
	docker compose -f docker-compose.dream-journal.yml build

up-dream:
	docker compose -f docker-compose.dream-journal.yml up -d

down-dream:
	docker compose -f docker-compose.dream-journal.yml down

logs-dream:
	docker compose -f docker-compose.dream-journal.yml logs -f dream-journal

pull-dream-model:
	docker compose -f docker-compose.dream-journal.yml exec ollama ollama pull $${OLLAMA_MODEL:-llama3.2}

check-node:
	cd apps/lantern-garage && npm run check

convergence:
	pwsh -NoProfile -ExecutionPolicy Bypass -File ./scripts/Invoke-LanternConvergenceLoop.ps1 -Root . -Output manifests/evidence/convergence-local.json -CloudVirtualization

quickstart:
	pwsh -NoProfile -ExecutionPolicy Bypass -File ./start-dual-servers.ps1
