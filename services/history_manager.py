"""
Chat History Management Service.

Handles persistent storage and retrieval of conversation sessions and messages.
Allows users to switch between previous chats and start new ones.
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from config import CHAT_HISTORY_FILE, DATA_DIR


class HistoryManager:
    def __init__(self, storage_path: Path = CHAT_HISTORY_FILE):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self._save_raw({"sessions": []})

    def _load_raw(self) -> dict:
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading chat history: {e}")
            return {"sessions": []}

    def _save_raw(self, data: dict):
        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error writing chat history: {e}")

    def get_all_sessions(self) -> List[Dict]:
        """Return list of session metadata sorted by latest update first."""
        data = self._load_raw()
        sessions = data.get("sessions", [])
        return sorted(sessions, key=lambda s: s.get("updated_at", ""), reverse=True)

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Retrieve full session data including messages."""
        data = self._load_raw()
        for s in data.get("sessions", []):
            if s.get("id") == session_id:
                return s
        return None

    def create_session(self, title: str = "New Support Chat") -> Dict:
        """Create a new chat session."""
        now = datetime.now().isoformat()
        new_session = {
            "id": str(uuid.uuid4()),
            "title": title,
            "created_at": now,
            "updated_at": now,
            "messages": []
        }
        data = self._load_raw()
        data.setdefault("sessions", []).insert(0, new_session)
        self._save_raw(data)
        return new_session

    def add_message(
        self,
        session_id: str,
        sender: str,
        text: str,
        metadata: Optional[dict] = None
    ) -> Dict:
        """Append a message to a session and update session timestamp."""
        now = datetime.now().isoformat()
        msg_id = str(uuid.uuid4())
        message = {
            "id": msg_id,
            "sender": sender,  # "user", "bot", or "system"
            "text": text,
            "timestamp": now,
            "metadata": metadata or {}
        }

        data = self._load_raw()
        sessions = data.get("sessions", [])
        session = next((s for s in sessions if s.get("id") == session_id), None)

        if not session:
            # Create session if it doesn't exist
            session = {
                "id": session_id,
                "title": text[:32] + ("..." if len(text) > 32 else "") if sender == "user" else "Support Chat",
                "created_at": now,
                "updated_at": now,
                "messages": [message]
            }
            sessions.insert(0, session)
        else:
            session.setdefault("messages", []).append(message)
            session["updated_at"] = now
            # If title is default and user sent first message, update title
            if sender == "user" and (session.get("title") in ("New Support Chat", "New Chat", "Untitled Chat") or len(session["messages"]) <= 2):
                clean_title = text.strip().replace("\n", " ")
                session["title"] = clean_title[:32] + ("..." if len(clean_title) > 32 else "")

        self._save_raw(data)
        return message

    def update_session_title(self, session_id: str, new_title: str) -> bool:
        """Update session title."""
        data = self._load_raw()
        for s in data.get("sessions", []):
            if s.get("id") == session_id:
                s["title"] = new_title.strip()
                s["updated_at"] = datetime.now().isoformat()
                self._save_raw(data)
                return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session."""
        data = self._load_raw()
        initial_len = len(data.get("sessions", []))
        data["sessions"] = [s for s in data.get("sessions", []) if s.get("id") != session_id]
        if len(data["sessions"]) < initial_len:
            self._save_raw(data)
            return True
        return False

    def clear_all(self):
        """Clear all chat history."""
        self._save_raw({"sessions": []})
