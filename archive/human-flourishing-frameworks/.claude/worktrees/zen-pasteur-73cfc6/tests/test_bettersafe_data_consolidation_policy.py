import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BetterSafeDataConsolidationPolicyTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def assert_contains_phrase(self, text: str, phrase: str) -> None:
        normalized_text = re.sub(r"\s+", " ", text)
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, normalized_text)

    def test_policy_blocks_private_data_and_public_chain_storage_by_default(self):
        doc = self.read("docs/bettersafe-data-consolidation-blockchain-policy.md")
        required_phrases = [
            "Raw private data consolidation: BLOCKED",
            "Public blockchain storage of personal data: BLOCKED",
            "Public blockchain storage of raw transcripts: BLOCKED",
            "Public blockchain storage of direct identifiers: BLOCKED",
            "Default statistical collection from people: BLOCKED",
            "Opt-in aggregate statistics: NOT_ENABLED_UNTIL_REVIEWED",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_policy_treats_hashes_of_private_data_as_sensitive(self):
        doc = self.read("docs/bettersafe-data-consolidation-blockchain-policy.md")
        required_phrases = [
            "Hashes are not automatically safe",
            "A hash of private data is still treated as sensitive unless a privacy/security review proves otherwise.",
            "Do not put hashes of private user data on a public blockchain during pilot.",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_policy_requires_opt_in_aggregate_threshold_for_future_statistics(self):
        doc = self.read("docs/bettersafe-data-consolidation-blockchain-policy.md")
        required_phrases = [
            "explicit opt-in",
            "purpose limitation",
            "data minimization",
            "aggregate-only output",
            "minimum group threshold before reporting",
            "minimum_n = 25",
            "INSUFFICIENT_GROUP_SIZE",
            "Do not report the value, subgroup detail, or residual calculation.",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_policy_limits_allowed_operational_evidence(self):
        doc = self.read("docs/bettersafe-data-consolidation-blockchain-policy.md")
        required_phrases = [
            "PR number",
            "commit SHA",
            "CI status",
            "smoke-check result",
            "operator-approved readiness action receipt",
            "correction ledger entry",
            "non-private release artifact checksum",
            "This evidence must avoid private user content",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_policy_requires_review_before_data_consolidation(self):
        doc = self.read("docs/bettersafe-data-consolidation-blockchain-policy.md")
        required_phrases = [
            "data inventory",
            "purpose statement",
            "collection fields",
            "retention rule",
            "consent/opt-in rule",
            "aggregation threshold",
            "de-identification risk review",
            "revocation/deletion handling",
            "security review",
            "privacy notice update",
            "tests proving blocked defaults",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_policy_answers_statistical_collection_question(self):
        doc = self.read("docs/bettersafe-data-consolidation-blockchain-policy.md")
        required_phrases = [
            "Are we collecting people's private data statistically?",
            "No. The pilot baseline blocks default people-level statistical collection.",
            "Only after a separate reviewed PR, explicit opt-in, minimum group threshold, and non-identifying aggregate-only design.",
            "Will private data go on public blockchain?",
            "No. Public chain use is blocked for private, identifying, transcript, household, health, safety, contact, device, or linkable user data.",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)


if __name__ == "__main__":
    unittest.main()
