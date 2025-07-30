#
# This script provides a class-based system for programmatically managing
# the Knowledge.json file. It allows for structured, auditable updates by
# ingesting "fragments" of new information, handling versioning, and
# maintaining a history log. This is intended for use by server-side agents
# or automated workflows.
#
import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from typing import List, Dict, Any

# --- Utility Functions (Placeholders) ---
# These would typically live in a shared 'utils.py' file.

def json_load(path: Path):
    """Loads a JSON file with error handling."""
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)

def json_dump_pretty(data: dict, path: Path):
    """Saves a dictionary to a JSON file with pretty printing."""
    with path.open('w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def utcnow_iso():
    """Returns the current UTC time in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()

def days_between(d1_str: str, d2_str: str) -> int:
    """
    Calculates the number of days between two ISO date strings.
    NOTE: Currently unused, reserved for future pruning logic.
    """
    try:
        d1 = datetime.fromisoformat(d1_str.replace('Z', '+00:00'))
        d2 = datetime.fromisoformat(d2_str.replace('Z', '+00:00'))
        return abs((d1 - d2).days)
    except (ValueError, TypeError):
        return float('inf') # Return a large number if dates are invalid

# --- Core KnowledgeStore Class ---

class KnowledgeStore:
    """
    Maintains master knowledge.json. Provides deterministic ingest and pruning.
    All session outputs produce 'fragments' appended to knowledge.json via ingest().
    """
    def __init__(self, path: str = "Knowledge.json"):
        self.path = Path(path)
        self.store = self._load()

    def _load(self):
        """Loads the knowledge store from the specified path."""
        if self.path.exists():
            return json_load(self.path)
        # PATCH: Harmonized default key to "metadata" to match save()
        return {
            "version": "1.0.0",
            "metadata": {"retention_policy": {}},
            "goals": [], "ideas": [], "projects": [], "memory_blocks": [],
            "state": {}, "history": []
        }

    def save(self):
        """Saves the current state of the knowledge store."""
        # PATCH: Added setdefault to prevent KeyError on older schemas
        self.store.setdefault("metadata", {})
        self.store["metadata"]["updated_at"] = utcnow_iso()
        json_dump_pretty(self.store, self.path)

    def _find(self, collection_name: str, key: str, value: Any):
        """Finds an item in a collection within the store."""
        collection = self.store.get(collection_name, [])
        for item in collection:
            if item.get(key) == value:
                return item
        return None

    def _ingest_goal(self, frag):
        p = frag["payload"]
        existing = self._find("goals", "id", p["id"])
        if frag["operation"] in ("add", "update"):
            if existing: existing.update(p)
            else: self.store["goals"].append(p)
        elif frag["operation"] == "archive" and existing:
            existing["status"] = "completed"
            existing["completed_at"] = frag["timestamp"]
        elif frag["operation"] == "delete" and existing:
            self.store["goals"].remove(existing)

    def _ingest_idea(self, frag):
        p = frag["payload"]
        existing = self._find("ideas", "id", p["id"])
        if frag["operation"] in ("add", "update"):
            if existing: existing.update(p)
            else: self.store["ideas"].append(p)
        elif frag["operation"] in ("archive", "delete") and existing:
            existing["status"] = "archived" if frag["operation"] == "archive" else "deleted"

    def _ingest_state(self, frag):
        self.store["state"].update(frag["payload"])

    def _append_history(self, frag):
        max_entries = self.store.get("metadata", {}).get("retention_policy", {}).get("max_history_entries", 1000)
        self.store["history"].append({
            "entry_id": str(uuid4()),
            "timestamp": frag["timestamp"],
            "action": f"{frag['type']}:{frag['operation']}",
            "fragment_id": frag.get("payload", {}).get("id"),
            "summary": frag.get("summary", "")
        })
        # Trim history to the max retention length
        self.store["history"] = self.store["history"][-max_entries:]

    def ingest_fragment(self, fragment: dict):
        """
        Ingests a single fragment to update the knowledge store.
        """
        # PATCH: Added placeholders for future types to avoid warnings
        route_map = {
            "goal": self._ingest_goal,
            "idea": self._ingest_idea,
            "state": self._ingest_state,
            "project": lambda s, f: None, # Placeholder
            "memory": lambda s, f: None,  # Placeholder
            "task": lambda s, f: None,    # Placeholder
        }
        
        frag_type = fragment.get("type")
        if frag_type in route_map:
            route_map[frag_type](self, fragment)
            self._append_history(fragment)
        else:
            print(f"Warning: Unknown fragment type '{frag_type}'. Skipping.")

    def update_from_session(self, fragments: List[Dict]):
        """Public workflow to update the store from a list of session fragments."""
        for f in fragments:
            self.ingest_fragment(f)
        self.save()
        print(f"Knowledge store updated with {len(fragments)} fragments and saved to {self.path}.")

# --- Example Usage ---
if __name__ == '__main__':
    # This demonstrates how the class would be used.
    ks = KnowledgeStore("Knowledge.json")

    # Example fragment from a session
    session_fragment_example = {
      "type": "idea",
      "operation": "add",
      "payload": {
        "id": "idea_new_scheduler_v2",
        "text": "AI-driven retail schedule generator using PEG macros.",
        "status": "active",
        "origin": "20250730-042000",
        "created_at": "2025-07-30T04:20:00-04:00",
        "updated_at": "2025-07-30T04:20:00-04:00",
        "tags": ["#PEG_Build"]
      },
      "timestamp": "2025-07-30T04:20:00-04:00",
      "session_id": "20250730-042000"
    }

    # Update the store with the new fragment
    ks.update_from_session([session_fragment_example])
