"""
Main Window Controller for the AI Customer Support Agent.

Integrates Sidebar, Chat View, Message Input, n8n Client, and Chat History.
Orchestrates background threads, signals, and UI state.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QSplitter, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

from config import AppConfig, load_config
from services.history_manager import HistoryManager
from services.n8n_client import N8nChatWorker, BackendHealthChecker
from ui.sidebar import SidebarWidget
from ui.chat_view import ChatView
from ui.message_input import MessageInputWidget
from ui.settings_dialog import SettingsDialog
from ui.styles import APP_STYLESHEET


class MainWindow(QMainWindow):
    """Main desktop application window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Offline AI Customer Support Agent — PyQt5")
        self.resize(1100, 750)
        self.setMinimumSize(850, 550)

        # Apply global styles
        self.setStyleSheet(APP_STYLESHEET)

        # Load Configuration and History Services
        self.config = load_config()
        self.history_mgr = HistoryManager()
        self.active_session_id = None
        self.current_worker = None

        self._init_ui()
        self._init_session()
        self._init_health_timer()

    def _init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Horizontal Splitter for Sidebar and Chat View
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)

        # 1. Sidebar Widget
        self.sidebar = SidebarWidget()
        self.sidebar.new_chat_requested.connect(self._create_new_chat)
        self.sidebar.session_selected.connect(self._switch_session)
        self.sidebar.session_delete_requested.connect(self._delete_session)
        self.sidebar.session_rename_requested.connect(self._rename_session)
        self.sidebar.settings_requested.connect(self._open_settings)
        splitter.addWidget(self.sidebar)

        # 2. Main Right Area (Chat View + Input)
        chat_container = QWidget()
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        chat_layout.setSpacing(0)

        self.chat_view = ChatView()
        self.chat_view.suggestion_requested.connect(self._on_suggestion_clicked)
        chat_layout.addWidget(self.chat_view, 1)

        self.message_input = MessageInputWidget()
        self.message_input.message_submitted.connect(self._send_message)
        chat_layout.addWidget(self.message_input, 0)

        splitter.addWidget(chat_container)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)

    def _init_session(self):
        """Load or create the initial chat session."""
        sessions = self.history_mgr.get_all_sessions()
        if sessions:
            self._switch_session(sessions[0]["id"])
        else:
            self._create_new_chat()

    def _init_health_timer(self):
        """Periodically probe n8n and Ollama health in background."""
        if self.config.auto_check_health:
            self.health_timer = QTimer(self)
            self.health_timer.timeout.connect(self._run_health_check)
            self.health_timer.start(self.config.health_check_interval_seconds * 1000)
            # Immediate initial probe
            QTimer.singleShot(500, self._run_health_check)

    def _run_health_check(self):
        """Spawn background worker to check local services."""
        self.health_worker = BackendHealthChecker(self.config)
        self.health_worker.health_checked.connect(self._on_health_checked)
        self.health_worker.start()

    def _on_health_checked(self, health: dict):
        """Update sidebar and header status badges."""
        self.sidebar.update_health_status(health)
        n8n_ok = health.get("n8n_ok", False)
        webhook_ok = health.get("webhook_ok", False)
        ollama_ok = health.get("ollama_ok", False)

        if n8n_ok and webhook_ok and ollama_ok:
            self.chat_view.update_header_status(True, "Online")
        elif n8n_ok and not webhook_ok:
            self.chat_view.update_header_status(False, "Workflow Inactive")
        elif not n8n_ok:
            self.chat_view.update_header_status(False, "n8n Offline")
        elif not ollama_ok:
            self.chat_view.update_header_status(False, "Ollama Offline")

    def _create_new_chat(self):
        """Start a brand new conversation."""
        session = self.history_mgr.create_session("New Support Chat")
        self.active_session_id = session["id"]
        self.sidebar.populate_sessions(self.history_mgr.get_all_sessions(), self.active_session_id)
        self.chat_view.set_session_info(session["title"], session["id"])
        self.chat_view.show_welcome()

    def _switch_session(self, session_id: str):
        """Switch view to the specified session."""
        session = self.history_mgr.get_session(session_id)
        if not session:
            return
        self.active_session_id = session_id
        self.sidebar.populate_sessions(self.history_mgr.get_all_sessions(), self.active_session_id)
        self.chat_view.set_session_info(session.get("title", ""), session_id)
        self.chat_view.display_session_messages(session.get("messages", []))

    def _delete_session(self, session_id: str):
        """Delete session and switch to another or create new."""
        self.history_mgr.delete_session(session_id)
        sessions = self.history_mgr.get_all_sessions()
        if sessions:
            self._switch_session(sessions[0]["id"])
        else:
            self._create_new_chat()

    def _rename_session(self, session_id: str, new_title: str):
        """Rename an existing session."""
        self.history_mgr.update_session_title(session_id, new_title)
        if self.active_session_id == session_id:
            self.chat_view.set_session_info(new_title, session_id)

    def _on_suggestion_clicked(self, query_text: str):
        """Populate and immediately dispatch a suggested question."""
        self._send_message(query_text)

    def _send_message(self, text: str):
        """Handle user message submission and initiate background n8n query."""
        if not self.active_session_id:
            session = self.history_mgr.create_session("New Support Chat")
            self.active_session_id = session["id"]

        # 1. Record user message in history and render bubble
        user_msg = self.history_mgr.add_message(
            self.active_session_id,
            sender="user",
            text=text
        )
        self.chat_view.add_user_message(text, user_msg.get("timestamp", ""))

        # 2. Update UI state to loading
        self.message_input.set_loading(True)
        self.chat_view.set_typing(True)

        # 3. Spawn background worker QThread for non-blocking HTTP request
        target_url = self.config.get_effective_webhook_url()
        self.current_worker = N8nChatWorker(
            webhook_url=target_url,
            message=text,
            session_id=self.active_session_id,
            timeout=self.config.request_timeout
        )
        self.current_worker.response_received.connect(self._on_bot_response)
        self.current_worker.error_occurred.connect(self._on_worker_error)
        self.current_worker.finished_request.connect(self._on_worker_finished)
        self.current_worker.start()

    def _on_bot_response(self, response_data: dict):
        """Handle successful response from n8n AI Agent."""
        text = response_data.get("text", "")
        ticket_id = response_data.get("ticket_id")
        order_id = response_data.get("order_id")

        # Save to history with extracted metadata
        bot_msg = self.history_mgr.add_message(
            self.active_session_id,
            sender="bot",
            text=text,
            metadata={"ticket_id": ticket_id, "order_id": order_id}
        )

        # Render message bubble
        self.chat_view.add_bot_message(
            text=text,
            timestamp=bot_msg.get("timestamp", ""),
            ticket_id=ticket_id,
            order_id=order_id
        )

        # Refresh sidebar session titles
        session = self.history_mgr.get_session(self.active_session_id)
        if session:
            self.chat_view.set_session_info(session.get("title", ""), self.active_session_id)
            self.sidebar.populate_sessions(self.history_mgr.get_all_sessions(), self.active_session_id)

    def _on_worker_error(self, title: str, details: str, error_code: str):
        """Handle errors returned from n8n worker thread."""
        self.history_mgr.add_message(
            self.active_session_id,
            sender="error",
            text=details,
            metadata={"title": title, "code": error_code}
        )
        self.chat_view.add_error_message(title, details)

    def _on_worker_finished(self):
        """Reset input and typing state when request concludes."""
        self.chat_view.set_typing(False)
        self.message_input.set_loading(False)
        self.current_worker = None

    def _open_settings(self):
        """Open settings dialog."""
        dialog = SettingsDialog(self.config, self)
        dialog.settings_saved.connect(self._on_settings_saved)
        dialog.exec_()

    def _on_settings_saved(self, new_config: AppConfig):
        """Apply newly saved settings."""
        self.config = new_config
        self._run_health_check()
