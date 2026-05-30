from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_asi_local_pdf_convergence_records_named_sources_and_hashes() -> None:
    text = read("manifests/evidence/asi-local-pdf-convergence-2026-05-29.md")
    required = [
        "Artificial_Superintelligence.pdf",
        "Artificial Superintelligence (ASI) Alliance Vision Paper.pdf",
        "01ab8d_eff73f6238854c7e847f15f412148fb8.pdf",
        "Artificial Superintelligence (ASI) Alliance Vision Paper - CUDOS Edition.pdf",
        "B5F026E9786AF1B7A085495A6A7198D49938DF9AABF1E7545AF06BAF3E0EB590",
        "3412A5DD589A72602F97D9C5CCFB3C387AFD74DC5882FB40807CD6AE7F5EAA64",
        "A0483D2559138F2AB5D1E4F50DF32F9A756E39377C3640C55029C30F61090BAF",
        "25776B3A8543D7C334BA315083D255C1B8C62B8B7DBBF77319984877ADBC9A89",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []


def test_asi_local_pdf_convergence_keeps_claims_bounded() -> None:
    text = read("manifests/evidence/asi-local-pdf-convergence-2026-05-29.md")
    required = [
        "Promote the architectural pattern, not the investment narrative.",
        "candidate_ai_strategy",
        "decentralized_compute_reference",
        "agent_network_governance_reference",
        "token_boundary_reference",
        "ASI capability exists locally",
        "token issuance or investment advice",
        "agent networks can bypass human approval",
        "The smallest useful force is a local RAG card",
    ]
    missing = [phrase for phrase in required if phrase not in text]
    assert missing == []
