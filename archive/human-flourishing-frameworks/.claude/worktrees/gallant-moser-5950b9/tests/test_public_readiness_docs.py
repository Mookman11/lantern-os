import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PublicReadinessDocsTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def assert_contains_phrase(self, text: str, phrase: str) -> None:
        normalized_text = re.sub(r"\s+", " ", text)
        normalized_phrase = re.sub(r"\s+", " ", phrase)
        self.assertIn(normalized_phrase, normalized_text)

    def test_readme_preserves_operator_utility_sections(self):
        readme = self.read("README.md")
        required_sections = [
            "## Quick start",
            "## Configuration",
            "## API",
            "## Architecture",
            "## Node security model",
            "## Authority and releases",
            "## Flourishing metrics",
            "## Contributing",
            "## License",
        ]
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, readme)

    def test_readme_preserves_public_boundary_language(self):
        readme = self.read("README.md")
        required_phrases = [
            "Plain-language summary:",
            "fresh smoke evidence",
            "capability is not authority",
            "operator-reviewed",
            "not a government, enforcement system, autonomous authority, or production critical infrastructure",
            "not be described as a production governance authority",
            "public does not mean uncontrolled",
            "token-gated does not mean safe",
            "consent does not mean permanent",
            "a signal does not equal the person",
            "APKs/mobile apps are not public by default",
            "vehicle control is outside current allowed scope",
            "source-visible research software rather than a broadly licensed production framework",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(readme, phrase)

    def test_public_surface_policy_blocks_unsafe_collapses(self):
        policy = self.read("docs/public-surface-policy.md")
        required_phrases = [
            "Public does not mean uncontrolled",
            "Token-gated does not mean safe",
            "Consent does not mean permanent",
            "A signal does not equal the person",
            "Vehicle control",
            "Not allowed",
            "sensor pathway treated as actuator permission",
            "sensor signal treated as proof of a person's inner state",
            "vehicle = ordinary device",
            "release bundle = survival proof",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(policy, phrase)

    def test_public_surface_policy_classifies_p0_webcam_and_discord_routes(self):
        policy = self.read("docs/public-surface-policy.md")
        required_phrases = [
            "Operator webcam session",
            "Private / operator-only",
            "P0 readiness, not public by default",
            "visible preview",
            "hard off switch",
            "fresh consent each session",
            "Discord Lantern adapter",
            "Private / permissioned room",
            "P0 route, not public by default",
            "explicit allowed guild",
            "explicit allowed channel",
            "Do not join their room without their all permission",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(policy, phrase)

    def test_public_surface_policy_classifies_neurocognitive_decoding(self):
        policy = self.read("docs/public-surface-policy.md")
        required_phrases = [
            "Neurocognitive decoding / brain-signal AI",
            "Private / highest-sensitivity signal",
            "Not public; research/clinical consent gate only",
            "not literal mind reading",
            "brain signal = person",
            "brain prediction = consent",
            "no hidden cognitive-state inference",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(policy, phrase)

    def test_public_surface_policy_protects_minor_device_pilots(self):
        policy = self.read("docs/public-surface-policy.md")
        required_phrases = [
            "Protected minor device/sensor pilot",
            "PROTECTED_MINOR_SENSITIVE_DEVICE_PILOT",
            "highest-sensitivity pilot class",
            "Parent/guardian permission",
            "Child assent",
            "No public surface",
            "No training use",
            "No hidden telemetry",
            "No high-risk sensors by default",
            "GPS/location, camera, mic, contacts, messages, photos, health, school, biometrics, and financial data are blocked",
            "child can stop immediately",
            "parent permission = unlimited child data collection",
            "child assent = adult-style alpha testing",
            "child device = ordinary adult device",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(policy, phrase)

    def test_i18n_doc_is_honest_about_incomplete_readiness(self):
        doc = self.read("docs/internationalization-and-accessibility.md")
        required_phrases = [
            "HFF is not fully internationalized yet",
            "English-first",
            "Do not imply global accessibility yet",
            "Not established",
            "Translations may help people understand the project, but they can introduce",
            "Machine translated",
            "not authoritative",
            "HFF is not legal, medical, financial, or governance authority in any jurisdiction",
            "Flourishing metrics must not rank people, cultures, nations, or moral worth",
            "person -> bounded signal pathway -> optional device surface -> policy-controlled record",
            "person = sensor",
            "consent once = consent forever",
        ]
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assert_contains_phrase(doc, phrase)

    def test_readme_does_not_reintroduce_license_placeholder(self):
        readme = self.read("README.md")
        self.assertNotIn("[Add actual license here]", readme)


if __name__ == "__main__":
    unittest.main()
