"""
DCF — Data Classification Format
Operationalizes P1 (Data Classification). Gates CCF (Capability Claim Format).

Every datum the system processes carries a class label. Labels propagate through
transformations: a summary of a FERPA record is still a FERPA record.

For Dream Journal v1.0.0, the primary classifications are:
- dream_content (user dreams — personal, not medical)
- user_identity (dreamer name, email)
- symbolic_data (symbols, lore, characters — user-created world-building)
- system_metadata (timestamps, agent selections, session state)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set


@dataclass
class ClassificationLabel:
    label: str  # e.g., "dream_content", "pii.email", "phi.diagnosis"
    sensitivity: str = "standard"  # public | standard | sensitive | restricted
    propagates: bool = True  # does this label survive transformations?
    retention_days: Optional[int] = None
    jurisdiction: str = "local"  # local | us | eu | global

    def to_dict(self) -> Dict[str, Any]:
        return {
            "label": self.label,
            "sensitivity": self.sensitivity,
            "propagates": self.propagates,
            "retention_days": self.retention_days,
            "jurisdiction": self.jurisdiction,
        }


@dataclass
class DataClassification:
    datum_id: str
    labels: Set[str] = field(default_factory=set)
    classified_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    classified_by: str = "system"
    source_datum_id: Optional[str] = None  # for derived data, tracks lineage

    def add_label(self, label: str) -> None:
        self.labels.add(label)

    def has_label(self, label: str) -> bool:
        return label in self.labels

    def has_any_sensitive(self, sensitive_labels: Optional[Set[str]] = None) -> bool:
        check = sensitive_labels or {"pii.email", "pii.ssn", "pii.financial", "phi.diagnosis", "coppa.under_13"}
        return bool(self.labels & check)

    def is_retained(self, label_definitions: Optional[Dict[str, ClassificationLabel]] = None) -> bool:
        """Check if this datum is still within retention policy for all its labels."""
        defs = label_definitions or {}
        classified_dt = datetime.fromisoformat(self.classified_at.replace("Z", "+00:00"))
        for label in self.labels:
            definition = defs.get(label)
            if definition and definition.retention_days is not None:
                age_days = (datetime.now(timezone.utc) - classified_dt).days
                if age_days > definition.retention_days:
                    return False
        return True

    def derive(self, new_datum_id: str, propagating_labels: Optional[Dict[str, ClassificationLabel]] = None) -> "DataClassification":
        """Create a derived classification. Only propagating labels survive."""
        if propagating_labels is None:
            inherited = set(self.labels)
        else:
            inherited = {l for l in self.labels if l in propagating_labels and propagating_labels[l].propagates}
        return DataClassification(
            datum_id=new_datum_id,
            labels=inherited,
            classified_by="derivation",
            source_datum_id=self.datum_id,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "datum_id": self.datum_id,
            "labels": sorted(self.labels),
            "classified_at": self.classified_at,
            "classified_by": self.classified_by,
            "source_datum_id": self.source_datum_id,
        }


# ── Standard labels for Dream Journal v1.0.0 ─────────────────────────────

DREAM_LABELS: Dict[str, ClassificationLabel] = {
    "dream_content": ClassificationLabel("dream_content", sensitivity="standard", propagates=True),
    "user_identity": ClassificationLabel("user_identity", sensitivity="sensitive", propagates=True, retention_days=365),
    "symbolic_data": ClassificationLabel("symbolic_data", sensitivity="standard", propagates=True),
    "system_metadata": ClassificationLabel("system_metadata", sensitivity="public", propagates=False),
    "agent_response": ClassificationLabel("agent_response", sensitivity="standard", propagates=False),
    "emotion_tag": ClassificationLabel("emotion_tag", sensitivity="standard", propagates=True),
    "csf_archive": ClassificationLabel("csf_archive", sensitivity="standard", propagates=True),
}
