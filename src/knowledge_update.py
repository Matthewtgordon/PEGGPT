class KnowledgeStore:
    """
    Maintains master knowledge.json. Provides deterministic ingest and pruning.
    All session outputs produce 'fragments' appended to knowledge.json via ingest().
    """

    def load(path="knowledge.json"):
        return json_load(path)

    def save(data, path="knowledge.json"):
        json_dump_pretty(data, path)

    def ingest_fragment(store, fragment):
        """
        fragment schema:
        {
          "type": "goal|idea|project|memory|task|state",
          "operation": "add|update|archive|delete",
          "payload": {...},
          "tags": [],
          "timestamp": "ISO8601",
          "session_id": "YYYYMMDD-HHMMSS"
        }
        """
        route = {
            "goal": _ingest_goal,
            "idea": _ingest_idea,
            "project": _ingest_project,
            "memory": _ingest_memory,
            "task": _ingest_task,
            "state": _ingest_state
        }[fragment["type"]]
        route(store, fragment)
        _append_history(store, fragment)
        prune(store)

    def _find(collection, key, value):
        for item in collection:
            if item[key] == value:
                return item
        return None

    def _ingest_goal(store, frag):
        p = frag["payload"]
        existing = _find(store["goals"], "id", p["id"])
        if frag["operation"] in ("add", "update"):
            if existing: existing.update(p)
            else: store["goals"].append(p)
        elif frag["operation"] == "archive" and existing:
            existing["status"] = "completed"
            existing["completed_at"] = frag["timestamp"]
        elif frag["operation"] == "delete" and existing:
            store["goals"].remove(existing)

    def _ingest_idea(store, frag):
        p = frag["payload"]
        existing = _find(store["ideas"], "id", p["id"])
        if frag["operation"] in ("add", "update"):
            if existing: existing.update(p)
            else: store["ideas"].append(p)
        elif frag["operation"] in ("archive", "delete") and existing:
            existing["status"] = "archived" if frag["operation"] == "archive" else "deleted"

    def _ingest_project(store, frag):
        p = frag["payload"]
        existing = _find(store["projects"], "id", p["id"])
        if existing: existing.update(p)
        else: store["projects"].append(p)

    def _ingest_memory(store, frag):
        p = frag["payload"]
        existing = _find(store["memory_blocks"], "id", p["id"])
        if existing: existing.update(p)
        else: store["memory_blocks"].append(p)

    def _ingest_task(store, frag):
        p = frag["payload"]
        proj = _find(store["projects"], "id", p["project_id"])
        if not proj: return
        existing = _find(proj["tasks"], "task_id", p["task_id"])
        if frag["operation"] in ("add", "update"):
            if existing: existing.update(p)
            else: proj["tasks"].append(p)
        elif frag["operation"] == "archive" and existing:
            existing["status"] = "completed"
        elif frag["operation"] == "delete" and existing:
            proj["tasks"].remove(existing)

    def _ingest_state(store, frag):
        store["state"].update(frag["payload"])

    def _append_history(store, frag):
        store["history"].append({
            "entry_id": uuid4(),
            "timestamp": frag["timestamp"],
            "action": f"{frag['type']}:{frag['operation']}",
            "fragment_id": frag.get("payload", {}).get("id"),
            "summary": frag.get("summary", "")
        })
        store["history"] = store["history"][-store["meta"]["retention_policy"]["max_history_entries"]:]

    def prune(store):
        now = utcnow()
        # Archive completed goals after retention window
        for g in list(store["goals"]):
            if g.get("status") == "completed":
                age = days_between(now, g.get("completed_at"))
                if age > store["meta"]["retention_policy"]["completed_goal_archive_days"]:
                    # Optionally move to separate archive file; here we keep but tag
                    g.setdefault("tags", []).append("#archived")
        # Archive stale ideas
        for i in store["ideas"]:
            if i["status"] == "active":
                age = days_between(now, i.get("updated_at"))
                if age > store["meta"]["retention_policy"]["inactive_idea_archive_days"]:
                    i["status"] = "archived"

    # Public workflow
    def update_from_session(fragments):
        store = load()
        for f in fragments:
            ingest_fragment(store, f)
        store["last_updated_utc"] = utcnow_iso()
        save(store)

# SESSION FRAGMENT EXAMPLE

────

{
  "type": "idea",
  "operation": "add",
  "payload": {
    "id": "idea_new_scheduler",
    "text": "AI-driven retail schedule generator using PEG macros.",
    "status": "active",
    "origin": "20250725-002000",
    "created_at": "2025-07-25T00:20:00-04:00",
    "updated_at": "2025-07-25T00:20:00-04:00",
    "tags": ["#PEG_Build"]
  },
  "timestamp": "2025-07-25T00:20:00-04:00",
  "session_id": "20250725-002000"
}
