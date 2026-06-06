"""
Three Doors Game Engine — shared between Discord bot, web API, and chat

Usage:
    from three_doors_engine import ThreeDoorsEngine, SCENES

    engine = ThreeDoorsEngine("user-id-123")
    state = engine.start_game()          # returns current state dict
    new_state = engine.choose_door("A")  # advance by door letter or name
    image_prompt = engine.sd_prompt_for_state()  # Stable Diffusion prompt
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data" / "discord" / "three-doors"

# ── Canonical scene library ──
SCENES = {
    "moss-entry": {
        "text": (
            "You stand inside **The Moss Door**. The air is thick with green light, soft earth, "
            "and the smell of rain on ferns. Lanterns hang from ancient branches. A moss-covered fox "
            "sits beside you, wearing a brass tag that reads: **FRIEND OF THE ONE WHO CHOSE GREEN**. "
            "It looks up and says, *\"You came back.\"*"
        ),
        "doors": [
            {"name": "The Burrow Door", "label": "A", "description": "Small, root-framed, warm. Smells of rain and old blankets."},
            {"name": "The Sunken Bell Door", "label": "B", "description": "Half underwater. Rings softly when no one touches it."},
            {"name": "The Little Crown Door", "label": "C", "description": "Tiny golden door in a tree stump, widening when trusted."},
        ],
        "fox_present": True,
    },
    "burrow": {
        "text": (
            "You crawl through **The Burrow Door** into a snug earthen chamber lined with woven roots "
            "and faded quilts. Rain drums overhead. The fox curls up on a blanket and closes its eyes. "
            "A single lantern flickers in the corner."
        ),
        "doors": [
            {"name": "The Root Door", "label": "A", "description": "Twisted oak roots form an arch. Something hums beyond."},
            {"name": "The Ember Door", "label": "B", "description": "Warmth radiates. Ash drifts under the crack like snow."},
            {"name": "The Stream Door", "label": "C", "description": "Water rushes somewhere close. The floor is slick moss."},
        ],
        "fox_present": True,
    },
    "sunken-bell": {
        "text": (
            "Beneath **The Sunken Bell Door**, water reaches your ankles in a stone hallway. A bell hangs "
            "above, dripping, and it chimes once though no wind blows. Reflections of lanterns dance on "
            "the ceiling like fish."
        ),
        "doors": [
            {"name": "The Deep Door", "label": "A", "description": "Submerged stairs descend into green-black silence."},
            {"name": "The Echo Door", "label": "B", "description": "Your own voice returns as song from the other side."},
            {"name": "The Surface Door", "label": "C", "description": "Sunlight visible through cracks. The sound of birds."},
        ],
        "fox_present": True,
    },
    "little-crown": {
        "text": (
            "Through **The Little Crown Door**, the forest opens into a glade where every tree stump wears "
            "a tiny golden crown. Yours widened just enough to let you through. The fox trots ahead, its "
            "tail brushing against jeweled leaves."
        ),
        "doors": [
            {"name": "The Throne Door", "label": "A", "description": "Carved from a single black oak. Velvet moss for a seat."},
            {"name": "The Hollow Door", "label": "B", "description": "A door inside a hollow tree. Sap runs like amber."},
            {"name": "The Star Door", "label": "C", "description": "Visible only at twilight. Constellations map the hinges."},
        ],
        "fox_present": True,
    },
}

# ── Door-to-next-scene map ──
_NEXT_MAP = {
    "the burrow door": "burrow",
    "the sunken bell door": "sunken-bell",
    "the little crown door": "little-crown",
    "the root door": "moss-entry",
    "the ember door": "moss-entry",
    "the stream door": "moss-entry",
    "the deep door": "sunken-bell",
    "the echo door": "burrow",
    "the surface door": "little-crown",
    "the throne door": "little-crown",
    "the hollow door": "burrow",
    "the star door": "moss-entry",
}

# ── Image prompt templates per scene ──
_SD_PROMPTS = {
    "moss-entry": (
        "atmospheric dreamscape, moss-covered ancient forest doorway, glowing green lanterns hanging from "
        "twisted branches, a friendly fox with a brass tag sitting on soft earth, rain on ferns, volumetric fog, "
        "cinematic lighting, dark fantasy, liminal space, soft pastel anime aesthetic, cel-shaded, 16:9"
    ),
    "burrow": (
        "cozy underground burrow chamber, woven tree roots as walls, faded patchwork quilts, warm lantern glow, "
        "sleeping fox on a blanket, rain drumming on earth ceiling, soft amber light, dark fantasy, "
        "anime aesthetic, cel-shaded, intimate composition, 16:9"
    ),
    "sunken-bell": (
        "submerged stone hallway, water at ankles, ancient bronze bell dripping, chimes without wind, "
        "lantern reflections dancing on wet ceiling, green-black silence, volumetric mist, dark fantasy, "
        "anime aesthetic, cel-shaded, eerie but friendly, 16:9"
    ),
    "little-crown": (
        "enchanted forest glade at twilight, every tree stump wears a tiny golden crown, jeweled leaves, "
        "a fox trotting through dappled light, widening magical doorway, soft warm glow, dark fantasy, "
        "anime aesthetic, cel-shaded, magical realism, 16:9"
    ),
}


class ThreeDoorsEngine:
    """Session-bound Three Doors game engine."""

    def __init__(self, user_id: str, data_dir: Path | None = None):
        self.user_id = user_id
        self.data_dir = data_dir or DATA_DIR
        self._state: dict | None = None

    # ── Persistence ──

    def _state_path(self) -> Path:
        safe = re.sub(r"[^a-zA-Z0-9._-]+", "-", self.user_id).strip("-").lower() or "user"
        return self.data_dir / f"{safe}.json"

    def load(self) -> dict | None:
        path = self._state_path()
        if not path.exists():
            return None
        try:
            self._state = json.loads(path.read_text("utf-8"))
            return self._state
        except (json.JSONDecodeError, OSError):
            return None

    def save(self, state: dict) -> None:
        self._state = state
        path = self._state_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            json.dump(state, handle, ensure_ascii=False, indent=2)
            handle.write("\n")

    # ── Gameplay ──

    def start_game(self) -> dict:
        """Begin a new game or resume existing."""
        state = self.load()
        if state is not None:
            return state
        scene = SCENES["moss-entry"]
        state = {
            "scene_key": "moss-entry",
            "text": scene["text"],
            "doors": scene["doors"],
            "fox_present": scene["fox_present"],
            "history": ["Entered The Moss Door"],
        }
        self.save(state)
        return state

    def choose_door(self, choice: str) -> dict | None:
        """Advance game by door letter (A/B/C) or full name. Returns new state or None if invalid."""
        state = self.load()
        if not state:
            return None
        choice_lower = choice.lower().strip()
        current_doors = state.get("doors", [])
        chosen = None
        for d in current_doors:
            if d["label"].lower() == choice_lower or d["name"].lower() == choice_lower:
                chosen = d
                break
        if not chosen:
            return None
        next_key = _NEXT_MAP.get(chosen["name"].lower(), "moss-entry")
        next_scene = SCENES[next_key]
        new_state = {
            "scene_key": next_key,
            "text": next_scene["text"],
            "doors": next_scene["doors"],
            "fox_present": next_scene["fox_present"],
            "history": state.get("history", []) + [f"Chose {chosen['name']}"],
        }
        self.save(new_state)
        return new_state

    def reset(self) -> dict:
        """Start fresh, discarding saved state."""
        path = self._state_path()
        if path.exists():
            path.unlink()
        self._state = None
        return self.start_game()

    # ── Image / AI integration ──

    def sd_prompt_for_state(self, state: dict | None = None) -> str:
        """Return a Stable Diffusion prompt for the current (or given) scene."""
        s = state or self._state or self.load() or SCENES["moss-entry"]
        key = s.get("scene_key", "moss-entry")
        return _SD_PROMPTS.get(key, _SD_PROMPTS["moss-entry"])

    def image_suggestions_for_ai(self) -> list[dict]:
        """Return image generation suggestions for the current AI provider to use.

        Each dict contains:
            prompt: str — ideal SD prompt
            scene_key: str — which scene this represents
            description: str — human-readable door description
        """
        state = self.load() or SCENES["moss-entry"]
        current_doors = state.get("doors", [])
        results = []
        for door in current_doors:
            next_key = _NEXT_MAP.get(door["name"].lower(), "moss-entry")
            prompt = _SD_PROMPTS.get(next_key, _SD_PROMPTS["moss-entry"])
            results.append({
                "prompt": prompt,
                "scene_key": next_key,
                "description": door["description"],
                "door_name": door["name"],
                "door_label": door["label"],
            })
        return results

    def to_api_response(self, state: dict | None = None) -> dict:
        """Serialize state for JSON API response."""
        s = state or self.load() or SCENES["moss-entry"]
        return {
            "scene_key": s.get("scene_key", "moss-entry"),
            "text": s.get("text", ""),
            "doors": s.get("doors", []),
            "fox_present": s.get("fox_present", False),
            "history": s.get("history", []),
            "image_prompt": self.sd_prompt_for_state(s),
            "image_available": bool(os.getenv("STABLE_DIFFUSION_URL") or os.getenv("SD_WEBUI_URL")),
        }


def _demo():
    engine = ThreeDoorsEngine("demo-user")
    state = engine.start_game()
    print("Started:", state["scene_key"])
    print("Prompt:", engine.sd_prompt_for_state())
    new_state = engine.choose_door("A")
    if new_state:
        print("Chose A:", new_state["scene_key"])
        print("New prompt:", engine.sd_prompt_for_state(new_state))


if __name__ == "__main__":
    _demo()
