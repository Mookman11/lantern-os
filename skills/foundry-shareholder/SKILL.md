---
name: foundry-shareholder
description: Central FOUNDRY shareholder consolidation skill for Lantern OS. Use when Codex or a coworker agent needs to consolidate the Lantern OS repo universe, separate cloud metered costs from offline/server-farm capacity, prepare shareholder-facing evidence, manage dual-boot/phone/server-farm expansion boundaries, or promote artifacts into the clean Lantern OS control plane.
---

# FOUNDRY Shareholder

Use this skill from `C:\tmp\lantern-os` when preparing shareholder-facing
Lantern OS work.

## Loop

1. Inspect repo status, remotes, manifests, artifacts, and dirty source repos.
2. Run `scripts/Invoke-LanternConvergenceLoop.ps1`.
3. Fix the first 2-4 actionable issues before expanding scope.
4. Retire or hold stale surfaces explicitly.
5. Promote only evidence-backed artifacts.
6. Regenerate PDFs after report changes.
7. Validate with targeted checks.
8. Commit and push the clean control plane.

## Repo Universe

Read `manifests/foundry-shareholder-repos.md` before making shareholder claims.
Treat named repositories as evidence sources unless the operator explicitly
asks to mutate them.

Read `manifests/FOUNDRY-MATRIX-RAG-DOLLHOUSE.md` when the user asks for local
RAG, server-farm expansion, iPhone edge-node work, son-PC dual boot, or a
matrix/dollhouse view.

## Token Policy

Offline-only/local/server-farm Foundry tokens are unmetered internal capacity.
Do not call them "Lite", do not rate them per token, and do not bill them as
cloud burn. Cloud/API escalation remains metered and must use current provider
pricing.

## Hardware Expansion

- Primary PC: first dual-boot target, physical install held.
- Son's PC: second dual-boot candidate after read-only readiness checks.
- iPhone and second phone: edge nodes first; true phone dual boot is held until
  exact model, backup, boot path, risk, and rollback are verified.
- Server farm: local inference pool; inventory nodes, GPUs/NPUs, storage,
  power, cooling, network, and remote access before capacity claims.

## Matrix RAG Dollhouse

Build the matrix as rooms and lanes:

- rooms: repos, PDFs/docs, Windows surfaces, dual boot, server farm, phones,
  shareholders;
- lanes: ingest, normalize, chunk, embed, index, retrieve, rerank, compress,
  handoff;
- metadata: source path, repo, commit, page, line, hash, evidence class,
  confidence, and operator boundary.

## Evidence Classes

Separate verified local state, source-repo evidence, operator assertions,
official web sources, cloud-metered costs, offline capacity, and projections.
