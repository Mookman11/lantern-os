"""
Memory Layer for Dream Journal RP Bot (Goal 1)
Minimal persistent session memory with CSF export path.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class SessionMemory:
    def __init__(self, user_id: int, character: str = "default"):
        self.user_id = user_id
        self.character = character
        self.created_at = datetime.utcnow().isoformat()
        self.messages: List[Dict] = []
        self.mode = "IC"

    def add_message(self, content: str, mode: str = "IC"):
        self.messages.append({
            "timestamp": datetime.utcnow().isoformat(),
            "mode": mode,
            "content": content
        })
        self.mode = mode

    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "character": self.character,
            "created_at": self.created_at,
            "message_count": len(self.messages),
            "messages": self.messages
        }

    def export_jsonl(self) -> str:
        """Export session as JSONL (one message per line)."""
        lines = [json.dumps(msg) for msg in self.messages]
        return "\n".join(lines)

    def export_csf_stub(self) -> Dict:
        """Placeholder for CSF export (to be wired to cadd_dollhouse_csf)."""
        return {
            "format": "CSF-v1-stub",
            "session": self.to_dict(),
            "note": "Replace with real CSF encoding when cadd_dollhouse_csf is integrated."
        }


class MemoryStore:
    """In-memory store for active sessions (replace with persistent backend later)."""
    def __init__(self):
        self.sessions: Dict[int, SessionMemory] = {}

    def get_or_create(self, user_id: int, character: str = "default") -> SessionMemory:
        if user_id not in self.sessions:
            self.sessions[user_id] = SessionMemory(user_id, character)
        return self.sessions[user_id]

    def end_session(self, user_id: int) -> Optional[SessionMemory]:
        return self.sessions.pop(user_id, None)


# Global store instance
memory_store = MemoryStore()