"""
Sidebar Widget Component.

Hosts application branding, "New Chat" action, conversation history list,
local service status monitors (n8n & Ollama), and Settings access.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QMenu, QAction, QInputDialog, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize


class SidebarWidget(QWidget):
    """Left sidebar managing chats and backend health status."""
    new_chat_requested = pyqtSignal()
    session_selected = pyqtSignal(str)       # session_id
    session_delete_requested = pyqtSignal(str) # session_id
    session_rename_requested = pyqtSignal(str, str) # session_id, new_title
    settings_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebarWidget")
        self.setFixedWidth(270)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header (Logo & Brand)
        header = QWidget()
        header.setObjectName("sidebarHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 14)
        header_layout.setSpacing(10)

        logo_icon = QLabel("💬")
        logo_icon.setStyleSheet("font-size: 22px;")
        header_layout.addWidget(logo_icon)

        title_box = QVBoxLayout()
        title_box.setSpacing(1)
        app_title = QLabel("Support AI")
        app_title.setObjectName("appLogoTitle")
        app_sub = QLabel("Customer Agent • Offline")
        app_sub.setObjectName("appLogoSubtitle")
        title_box.addWidget(app_title)
        title_box.addWidget(app_sub)
        header_layout.addLayout(title_box)

        main_layout.addWidget(header)

        # 2. "New Chat" Button
        self.btn_new_chat = QPushButton("＋  New Chat")
        self.btn_new_chat.setObjectName("btnNewChat")
        self.btn_new_chat.setCursor(Qt.PointingHandCursor)
        self.btn_new_chat.clicked.connect(self.new_chat_requested.emit)
        main_layout.addWidget(self.btn_new_chat)

        # 3. Chat History List Header
        lbl_history = QLabel("Chat History")
        lbl_history.setObjectName("sectionLabel")
        main_layout.addWidget(lbl_history)

        # 4. Chat History List
        self.session_list = QListWidget()
        self.session_list.setObjectName("sessionList")
        self.session_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.session_list.customContextMenuRequested.connect(self._show_context_menu)
        self.session_list.itemClicked.connect(self._on_item_clicked)
        main_layout.addWidget(self.session_list, 1)

        # 5. Footer (Service Status Indicators + Settings Button)
        footer = QWidget()
        footer.setObjectName("sidebarFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(14, 12, 14, 14)
        footer_layout.setSpacing(8)

        # Status Box
        status_box = QWidget()
        status_box.setObjectName("statusBox")
        s_layout = QVBoxLayout(status_box)
        s_layout.setContentsMargins(8, 6, 8, 6)
        s_layout.setSpacing(4)

        # n8n Status Row
        n8n_row = QHBoxLayout()
        self.dot_n8n = QLabel("●")
        self.dot_n8n.setObjectName("statusDotYellow")
        self.lbl_n8n = QLabel("n8n: Checking...")
        self.lbl_n8n.setStyleSheet("font-size: 11.5px; color: #cbd5e1;")
        n8n_row.addWidget(self.dot_n8n)
        n8n_row.addWidget(self.lbl_n8n)
        n8n_row.addStretch()
        s_layout.addLayout(n8n_row)

        # Ollama Status Row
        ollama_row = QHBoxLayout()
        self.dot_ollama = QLabel("●")
        self.dot_ollama.setObjectName("statusDotYellow")
        self.lbl_ollama = QLabel("Ollama: Checking...")
        self.lbl_ollama.setStyleSheet("font-size: 11.5px; color: #cbd5e1;")
        ollama_row.addWidget(self.dot_ollama)
        ollama_row.addWidget(self.lbl_ollama)
        ollama_row.addStretch()
        s_layout.addLayout(ollama_row)

        footer_layout.addWidget(status_box)

        # Settings Button
        self.btn_settings = QPushButton("⚙  Settings")
        self.btn_settings.setObjectName("btnSettings")
        self.btn_settings.setCursor(Qt.PointingHandCursor)
        self.btn_settings.clicked.connect(self.settings_requested.emit)
        footer_layout.addWidget(self.btn_settings)

        main_layout.addWidget(footer)

    def populate_sessions(self, sessions: list, active_session_id: str = None):
        """Fill session list with saved conversations."""
        self.session_list.clear()
        for s in sessions:
            title = s.get("title", "Untitled Chat")
            session_id = s.get("id")
            item = QListWidgetItem(f"💬  {title}")
            item.setData(Qt.UserRole, session_id)
            item.setToolTip(f"ID: {session_id}\nCreated: {s.get('created_at', '')[:10]}")
            self.session_list.addItem(item)

            if active_session_id and session_id == active_session_id:
                self.session_list.setCurrentItem(item)

    def select_session(self, session_id: str):
        """Highlight active session item in list."""
        for i in range(self.session_list.count()):
            item = self.session_list.item(i)
            if item.data(Qt.UserRole) == session_id:
                self.session_list.setCurrentItem(item)
                break

    def update_health_status(self, health: dict):
        """Update live status dots and labels for n8n and Ollama."""
        # n8n
        n8n_ok = health.get("n8n_ok", False)
        webhook_ok = health.get("webhook_ok", False)
        if n8n_ok and webhook_ok:
            self.dot_n8n.setObjectName("statusDotGreen")
            self.lbl_n8n.setText("n8n: Live & Active")
        elif n8n_ok and not webhook_ok:
            self.dot_n8n.setObjectName("statusDotYellow")
            self.lbl_n8n.setText("n8n: Inactive Flow")
        else:
            self.dot_n8n.setObjectName("statusDotRed")
            self.lbl_n8n.setText("n8n: Offline")

        # Ollama
        ollama_ok = health.get("ollama_ok", False)
        if ollama_ok:
            self.dot_ollama.setObjectName("statusDotGreen")
            self.lbl_ollama.setText("Ollama: Ready")
        else:
            self.dot_ollama.setObjectName("statusDotRed")
            self.lbl_ollama.setText("Ollama: Offline")

        # Refresh styles
        for widget in (self.dot_n8n, self.dot_ollama):
            widget.style().unpolish(widget)
            widget.style().polish(widget)

    def _on_item_clicked(self, item: QListWidgetItem):
        session_id = item.data(Qt.UserRole)
        if session_id:
            self.session_selected.emit(session_id)

    def _show_context_menu(self, pos):
        item = self.session_list.itemAt(pos)
        if not item:
            return

        session_id = item.data(Qt.UserRole)
        current_title = item.text().replace("💬  ", "")

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #1e2235; border: 1px solid #2d334d; border-radius: 6px; padding: 4px; }
            QMenu::item { padding: 6px 18px; color: #f1f5f9; border-radius: 4px; }
            QMenu::item:selected { background-color: #3b82f6; }
        """)

        action_rename = QAction("✏️ Rename", self)
        action_delete = QAction("🗑️ Delete", self)

        menu.addAction(action_rename)
        menu.addAction(action_delete)

        action = menu.exec_(self.session_list.mapToGlobal(pos))
        if action == action_rename:
            new_title, ok = QInputDialog.getText(
                self, "Rename Chat", "Enter new chat title:", text=current_title
            )
            if ok and new_title.strip():
                item.setText(f"💬  {new_title.strip()}")
                self.session_rename_requested.emit(session_id, new_title.strip())

        elif action == action_delete:
            reply = QMessageBox.question(
                self, "Delete Chat",
                f"Are you sure you want to delete '{current_title}'?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.session_delete_requested.emit(session_id)
