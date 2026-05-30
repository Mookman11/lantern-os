from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_better_contract_names_modes_and_boundaries() -> None:
    text = read("docs/BETTER-IPHONE-APP-CONCEPT.md")
    required = [
        "BETTER is the future iPhone shell",
        "BetterSafe",
        "BetterFun",
        "No native iPhone app, App Store listing, or",
        "PWA/Shortcut-first",
        "No gambling framing",
        "not medical, legal, financial, emergency, surveillance, child-facing, or autonomous authority",
        "observe -> record -> compare -> propose -> human approve -> apply -> verify -> repeat",
        "must communicate through one protocol",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_dashboard_links_better_and_revenue_demo() -> None:
    html = read("apps/lantern-garage/public/index.html")
    required = [
        "BETTER iPhone",
        "BetterSafe",
        "BetterFun",
        "PWA/Shortcut-first; no native permission claim yet.",
        "/view?path=docs/BETTER-IPHONE-APP-CONCEPT.md",
        "/demo-1000.html",
        "Demo $1000",
    ]
    missing = [phrase for phrase in required if phrase not in html]
    assert missing == []


def test_demo_surface_sells_real_service_not_fake_revenue() -> None:
    html = read("apps/lantern-garage/public/demo-1000.html")
    required = [
        "Lantern Cloud OS Copilot",
        "$1000",
        "Manual invoice only",
        "private AI copilot",
        "GPT, Claude, and Copilot",
        "What You Buy",
        "Why Buy Today",
        "Who Buys",
        "personal RAG memory",
        "monthly AI seat path",
        "$99/month personal mirror",
        "$500/month operator copilot care",
        "Current Model Move",
        "Turn It On In 60",
        "ASI/RAG Proof Card",
        "manifests/evidence/asi-local-pdf-convergence-2026-05-29.md",
        "/api/command",
        "!one",
        "!converge",
        "!superjarvis",
    ]
    missing = [phrase for phrase in required if phrase not in html]
    assert missing == []


def test_demo_surface_uses_plain_buyer_style_not_theme_park_chrome() -> None:
    html = read("apps/lantern-garage/public/demo-1000.html")
    required = [
        'data-style="plain-buyer-demo"',
        "--demo-bg: #f7f5ef",
        "--demo-accent: #0b5cad",
        "font-family: Georgia",
        "box-shadow: 0 10px 28px rgba(23, 32, 42, .06)",
    ]
    banned = [
        "linear-gradient(135deg, #dff7c8",
        "border: 4px solid #246b3a",
        "box-shadow: 0 16px 0 rgba(39, 107, 58",
        "#fff4b0",
        "#64b6de",
    ]
    missing = [phrase for phrase in required if phrase not in html]
    present = [phrase for phrase in banned if phrase in html]
    assert missing == []
    assert present == []


def test_one_hour_demo_doc_keeps_cash_truth_boundary() -> None:
    text = read("docs/ONE-HOUR-1000-DEMO.md")
    required = [
        "direct-invoice",
        "Lantern Cloud OS Copilot",
        "Founding Seat",
        "Price: `$1000` founding setup.",
        "Buyer pain",
        "Why A Person Buys",
        "They are not buying MCP, RAG, git, or agent labor. They are buying their own AI",
        "missing context layer around GPT, Claude, Copilot",
        "`$99/month` personal mirror",
        "`$500/month` operator copilot care",
        "manual invoice",
        "Current Model Optimization",
        "Send Packet",
        "I set up founding Lantern Cloud OS Copilot seats for $1000.",
        "Do not mark revenue as cleared until money clears externally",
        "no fake cleared cash",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_better_stone_parable_keeps_symbolic_boundary() -> None:
    text = read("docs/BETTER-STONE-PARABLE.md")
    required = [
        "one stone",
        "The stone is not a weapon",
        "washes the panic, false commands, and split-brain noise",
        "carries them home",
        "observe -> record -> compare -> propose -> human approve -> apply -> verify -> repeat",
        "no harm instructions",
        "no combat plan",
        "no proof, consent, prophecy, destiny, or command authority",
        "smallest reversible action",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_better_forward_entropy_study_names_small_reversing_forces() -> None:
    text = read("docs/BETTER-FORWARD-ENTROPY.md")
    required = [
        "Forward entropy",
        "dashboards split",
        "tunnels go stale",
        "commands fork",
        "Small reversing force",
        "POST /api/command",
        "Keep manual invoice separate from cleared cash",
        "one reversible fix",
        "What entropy is increasing?",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []
