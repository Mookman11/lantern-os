"""
Build the capability training dataset for the local Ouro model (#1100).

The coding corpus teaches tool-call format but only covers coding tasks.
This script generates trajectories for the three new capability areas:
  1. web-lookup  — web_search + web_fetch
  2. documents   — generate_document + list_document_templates
  3. workspace   — workspace_read + workspace_write + workspace_list

Output: models/lantern-sigma0-coder/capability-data.jsonl
Format: {"instruction": "...", "input": "", "output": "..."}
        where output may contain <tool_call>{"name":...,"input":{...}}</tool_call>

The instruction contains a PREAMBLE with the available tools so the model
knows what's callable — same as the fc-toolace rows.

Run:
    python scripts/build_capability_dataset.py
    python scripts/build_capability_dataset.py --out path/to/out.jsonl --validate
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PREAMBLE = (
    "You are Keystone — a local-first AI assistant inside Keystone OS. "
    "You respond in plain language and call tools when needed.\n"
    "To call a tool, emit EXACTLY ONE tool call on a SINGLE LINE:\n"
    "<tool_call>{\"name\": \"TOOL_NAME\", \"input\": {\"KEY\": \"VALUE\"}}</tool_call>\n"
    "Emit the call and STOP. Do not explain it. Available tools:\n"
)

WEB_TOOLS_DESC = (
    "Tool: web_search\nDescription: Search the web for current information.\n"
    "Input: {\"query\": string}\n\n"
    "Tool: web_fetch\nDescription: Fetch the full text content of a URL.\n"
    "Input: {\"url\": string}\n"
)

DOC_TOOLS_DESC = (
    "Tool: generate_document\nDescription: Render a document (resume or cover-letter) from fields.\n"
    "Input: {\"template\": string, \"fields\": object, \"format\": string (html|markdown)}\n\n"
    "Tool: list_document_templates\nDescription: List available document templates and their fields.\n"
    "Input: {}\n"
)

WS_TOOLS_DESC = (
    "Tool: workspace_read\nDescription: Read a file from the user workspace.\n"
    "Input: {\"path\": string}\n\n"
    "Tool: workspace_write\nDescription: Write content to a file in the user workspace.\n"
    "Input: {\"path\": string, \"content\": string}\n\n"
    "Tool: workspace_list\nDescription: List files in the user workspace.\n"
    "Input: {\"subdir\": string (optional)}\n"
)


def _tc(name: str, inp: dict) -> str:
    return f"<tool_call>{json.dumps({'name': name, 'input': inp}, ensure_ascii=False)}</tool_call>"


def _row(preamble_addon: str, user_msg: str, output: str) -> dict:
    instruction = PREAMBLE + preamble_addon + "\nUser: " + user_msg
    return {"instruction": instruction, "input": "", "output": output}


# ── Web lookup trajectories ────────────────────────────────────────────────────

def web_lookup_rows() -> list[dict]:
    rows = []

    # search → direct answer
    rows.append(_row(WEB_TOOLS_DESC,
        "What is the current price of Bitcoin?",
        _tc("web_search", {"query": "Bitcoin price today USD 2026"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "Who won the most recent US presidential election?",
        _tc("web_search", {"query": "US presidential election result 2024"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "What are the latest interest rate decisions by the Federal Reserve?",
        _tc("web_search", {"query": "Federal Reserve interest rate decision 2026"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "Search for recent news about OpenAI.",
        _tc("web_search", {"query": "OpenAI news 2026"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "Find the documentation for the Python requests library.",
        _tc("web_search", {"query": "Python requests library documentation site:docs.python-requests.org OR site:pypi.org"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "Look up the current weather in San Francisco.",
        _tc("web_search", {"query": "current weather San Francisco CA"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "What is the population of Tokyo?",
        _tc("web_search", {"query": "population of Tokyo 2024 2025"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "Search for papers on retrieval-augmented generation.",
        _tc("web_search", {"query": "retrieval-augmented generation RAG papers arxiv 2024 2025"})))

    # fetch → direct
    rows.append(_row(WEB_TOOLS_DESC,
        "Fetch the content of https://api.github.com/repos/anthropics/claude-code",
        _tc("web_fetch", {"url": "https://api.github.com/repos/anthropics/claude-code"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "Can you read https://example.com for me?",
        _tc("web_fetch", {"url": "https://example.com"})))

    # plain answer (no tool needed)
    rows.append(_row(WEB_TOOLS_DESC,
        "What is 2 + 2?",
        "4. No tool needed — this is a direct arithmetic fact."))

    rows.append(_row(WEB_TOOLS_DESC,
        "Explain what retrieval-augmented generation means.",
        "Retrieval-augmented generation (RAG) is a technique where a language model retrieves relevant documents from an external knowledge base before generating a response. This grounds the output in real, up-to-date sources rather than relying solely on the model's training data."))

    rows.append(_row(WEB_TOOLS_DESC,
        "Search for the Keystone OS GitHub repository.",
        _tc("web_search", {"query": "Keystone OS lantern-os GitHub alex-place"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "What is the latest version of Node.js?",
        _tc("web_search", {"query": "latest Node.js LTS version 2026"})))

    rows.append(_row(WEB_TOOLS_DESC,
        "Fetch the README from https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/main/README.md",
        _tc("web_fetch", {"url": "https://raw.githubusercontent.com/anthropics/anthropic-sdk-python/main/README.md"})))

    # negative: should NOT call web for simple knowledge
    rows.append(_row(WEB_TOOLS_DESC,
        "How do I reverse a list in Python?",
        "Use `list[::-1]` for a reversed copy, or `list.reverse()` to reverse in-place. No web lookup needed — this is stable Python syntax."))

    rows.append(_row(WEB_TOOLS_DESC,
        "What does HTTP 404 mean?",
        "HTTP 404 means 'Not Found' — the server cannot find the requested resource. No search needed."))

    return rows


# ── Document generation trajectories ─────────────────────────────────────────

def document_rows() -> list[dict]:
    rows = []

    # list templates first
    rows.append(_row(DOC_TOOLS_DESC,
        "What document templates are available?",
        _tc("list_document_templates", {})))

    rows.append(_row(DOC_TOOLS_DESC,
        "Show me what fields the resume template needs.",
        _tc("list_document_templates", {})))

    # generate resume
    rows.append(_row(DOC_TOOLS_DESC,
        "Create an HTML resume for Jane Smith, a backend engineer with Python and PostgreSQL skills.",
        _tc("generate_document", {
            "template": "resume",
            "fields": {
                "name": "Jane Smith",
                "email": "jane@example.com",
                "location": "San Francisco, CA",
                "summary": "Backend engineer with 4 years of experience building scalable Python services.",
                "skills": ["Python", "PostgreSQL", "Docker", "REST APIs", "Node.js"],
                "experience": [
                    {
                        "title": "Backend Engineer",
                        "company": "Acme Corp",
                        "dates": "2022 – 2026",
                        "bullets": [
                            "Built Python microservices handling 50k requests/day",
                            "Migrated legacy monolith to Docker-based deployment",
                            "Designed PostgreSQL schemas for multi-tenant SaaS"
                        ]
                    }
                ]
            },
            "format": "html"
        })))

    # generate cover letter
    rows.append(_row(DOC_TOOLS_DESC,
        "Write a cover letter for John Doe applying to a Senior Engineer role at TechCo.",
        _tc("generate_document", {
            "template": "cover-letter",
            "fields": {
                "name": "John Doe",
                "email": "john@example.com",
                "date": "June 24, 2026",
                "company": "TechCo",
                "role": "Senior Engineer",
                "opening": "I am excited to apply for the Senior Engineer position at TechCo. My five years of experience building distributed systems aligns directly with your team's needs.",
                "body": "At my previous role at StartupXYZ, I led the migration of our monolithic backend to a microservices architecture, reducing deployment time by 60%. I am passionate about building reliable, observable systems and mentoring junior engineers.",
                "closing": "I would welcome the opportunity to discuss how my background can contribute to TechCo's engineering excellence."
            },
            "format": "html"
        })))

    # markdown format
    rows.append(_row(DOC_TOOLS_DESC,
        "Generate a Markdown resume for Alex Chen, data scientist.",
        _tc("generate_document", {
            "template": "resume",
            "fields": {
                "name": "Alex Chen",
                "email": "alex@example.com",
                "location": "Remote",
                "summary": "Data scientist specializing in NLP and recommendation systems.",
                "skills": ["Python", "PyTorch", "SQL", "scikit-learn", "Spark"],
                "experience": [
                    {
                        "title": "Data Scientist",
                        "company": "DataCo",
                        "dates": "2021 – 2026",
                        "bullets": [
                            "Built an NLP pipeline processing 1M daily documents",
                            "Improved recommendation CTR by 18% via collaborative filtering"
                        ]
                    }
                ]
            },
            "format": "markdown"
        })))

    # plain answer: no tool needed
    rows.append(_row(DOC_TOOLS_DESC,
        "What is the difference between a resume and a CV?",
        "A resume is a 1-2 page tailored summary of experience, skills, and accomplishments. A CV (curriculum vitae) is a comprehensive academic record covering all publications, presentations, and research — typically 2+ pages and common in academia and Europe. Use a resume for industry job applications."))

    # list → then generate
    rows.append(_row(DOC_TOOLS_DESC,
        "I'm not sure what fields to fill in. Can you show me the template schema?",
        _tc("list_document_templates", {})))

    # cover letter minimal fields
    rows.append(_row(DOC_TOOLS_DESC,
        "Quick cover letter for Maria Lopez applying to Product Designer at DesignStudio.",
        _tc("generate_document", {
            "template": "cover-letter",
            "fields": {
                "name": "Maria Lopez",
                "company": "DesignStudio",
                "role": "Product Designer",
                "opening": "I am applying for the Product Designer position at DesignStudio because I believe my five years of UX/UI work in fintech aligns well with your team's goals.",
                "body": "My design work has directly improved user retention metrics and streamlined onboarding flows. I am comfortable working across the full design lifecycle from research to high-fidelity prototypes.",
                "closing": "I look forward to discussing how I can contribute to DesignStudio."
            },
            "format": "html"
        })))

    return rows


# ── Workspace trajectories ────────────────────────────────────────────────────

def workspace_rows() -> list[dict]:
    rows = []

    # list workspace
    rows.append(_row(WS_TOOLS_DESC,
        "What files are in my workspace?",
        _tc("workspace_list", {})))

    rows.append(_row(WS_TOOLS_DESC,
        "Show me the files in my documents folder.",
        _tc("workspace_list", {"subdir": "documents"})))

    # read file
    rows.append(_row(WS_TOOLS_DESC,
        "Read my notes.txt file.",
        _tc("workspace_read", {"path": "notes.txt"})))

    rows.append(_row(WS_TOOLS_DESC,
        "Can you read resume.html from my workspace?",
        _tc("workspace_read", {"path": "resume.html"})))

    rows.append(_row(WS_TOOLS_DESC,
        "Show me what's in my job-application-notes.md file.",
        _tc("workspace_read", {"path": "job-application-notes.md"})))

    # write file
    rows.append(_row(WS_TOOLS_DESC,
        "Save this note to reminders.txt: 'Follow up with hiring manager at Acme on Monday'",
        _tc("workspace_write", {"path": "reminders.txt", "content": "Follow up with hiring manager at Acme on Monday"})))

    rows.append(_row(WS_TOOLS_DESC,
        "Create a file called goals-2026.md with the content: '# 2026 Goals\\n- Get new job\\n- Learn Rust'",
        _tc("workspace_write", {"path": "goals-2026.md", "content": "# 2026 Goals\n- Get new job\n- Learn Rust"})))

    rows.append(_row(WS_TOOLS_DESC,
        "Write my cover letter draft to cover-letter-draft.txt",
        _tc("workspace_write", {"path": "cover-letter-draft.txt", "content": "Dear Hiring Manager,\n\nI am applying for the Software Engineer position..."})))

    # list then read
    rows.append(_row(WS_TOOLS_DESC,
        "What files are in my workspace right now?",
        _tc("workspace_list", {})))

    rows.append(_row(WS_TOOLS_DESC,
        "Check if there's a file called budget.csv in the workspace.",
        _tc("workspace_list", {})))

    # plain answer (no tool)
    rows.append(_row(WS_TOOLS_DESC,
        "What is the user workspace?",
        "The user workspace is a consent-gated directory at `~/.keystone/workspace/` (or the path set by KEYSTONE_WORKSPACE). It stores your personal files outside the repository — notes, document drafts, exports. Files there are private to you and never committed to git."))

    rows.append(_row(WS_TOOLS_DESC,
        "How do I access my saved documents?",
        "Your documents are in the workspace directory (`~/.keystone/workspace/` by default). Use the `workspace_list` tool to see what's there, and `workspace_read` to read a file."))

    return rows


# ── Combined / multi-tool trajectories ───────────────────────────────────────

COMBINED_TOOLS_DESC = WEB_TOOLS_DESC + "\n" + DOC_TOOLS_DESC + "\n" + WS_TOOLS_DESC

def combined_rows() -> list[dict]:
    rows = []

    # research job → will need web_search first
    rows.append(_row(COMBINED_TOOLS_DESC,
        "Look up the job description for Staff Engineer at Stripe.",
        _tc("web_search", {"query": "Staff Engineer job description Stripe 2026 site:stripe.com OR site:linkedin.com"})))

    # save a note after research
    rows.append(_row(COMBINED_TOOLS_DESC,
        "Save my research notes about the Stripe job to stripe-notes.md",
        _tc("workspace_write", {"path": "stripe-notes.md", "content": "# Stripe Staff Engineer Research\n\nKey requirements: distributed systems, Go/Java, 8+ years XP\nCulture: API-first, high-reliability, data-driven\nNext step: tailor resume to distributed systems experience"})))

    # check workspace then generate doc
    rows.append(_row(COMBINED_TOOLS_DESC,
        "List my workspace files, then generate a resume for me.",
        _tc("workspace_list", {})))

    # generate document and confirm
    rows.append(_row(COMBINED_TOOLS_DESC,
        "Generate an HTML resume for Sam Park and save a note that the resume was created.",
        _tc("generate_document", {
            "template": "resume",
            "fields": {
                "name": "Sam Park",
                "email": "sam@example.com",
                "location": "New York, NY",
                "summary": "Full-stack engineer with expertise in React and Node.js.",
                "skills": ["React", "Node.js", "TypeScript", "PostgreSQL"],
                "experience": [
                    {
                        "title": "Full-Stack Engineer",
                        "company": "StartupABC",
                        "dates": "2023 – 2026",
                        "bullets": [
                            "Built React dashboard with real-time WebSocket updates",
                            "Designed REST API serving 500 active users"
                        ]
                    }
                ]
            },
            "format": "html"
        })))

    return rows


# ── Main ──────────────────────────────────────────────────────────────────────

def build_all() -> list[dict]:
    rows = []
    rows += web_lookup_rows()
    rows += document_rows()
    rows += workspace_rows()
    rows += combined_rows()
    return rows


def validate(rows: list[dict]) -> bool:
    required_keys = {"instruction", "input", "output"}
    errors = 0
    for i, row in enumerate(rows):
        if set(row.keys()) != required_keys:
            print(f"row {i}: unexpected keys {set(row.keys())}", file=sys.stderr)
            errors += 1
        if not isinstance(row["instruction"], str) or not row["instruction"].strip():
            print(f"row {i}: empty instruction", file=sys.stderr)
            errors += 1
        if not isinstance(row["output"], str) or not row["output"].strip():
            print(f"row {i}: empty output", file=sys.stderr)
            errors += 1
    return errors == 0


def main() -> None:
    parser = argparse.ArgumentParser(description="Build capability training dataset (#1100)")
    parser.add_argument("--out", default="models/lantern-sigma0-coder/capability-data.jsonl",
                        help="Output JSONL path")
    parser.add_argument("--validate", action="store_true", help="Validate output after writing")
    args = parser.parse_args()

    rows = build_all()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {len(rows)} rows to {out}")

    if args.validate:
        ok = validate(rows)
        if ok:
            print("Validation passed.")
        else:
            print("Validation FAILED.", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
