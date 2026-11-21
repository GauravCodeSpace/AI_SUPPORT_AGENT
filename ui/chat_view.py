"""
Main Chat View Component.

Renders conversation message bubbles, welcome screen with suggested question cards,
complaint ticket verification cards, and typing indicators.
"""

from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QScrollArea, QFrame, QPushButton, QSizePolicy,
    QGridLayout, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer


class SuggestionCard(QFrame):
    """Clickable suggestion card on the welcome screen."""
    clicked = pyqtSignal(str)

    def __init__(self, title: str, subtitle: str, query_text: str, parent=None):
        super().__init__(parent)
        self.setObjectName("suggestionCard")
        self.setCursor(Qt.PointingHandCursor)
        self.query_text = query_text

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(3)

        lbl_title = QLabel(title)
        lbl_title.setObjectName("suggestionCardTitle")
        lbl_title.setWordWrap(True)

        lbl_sub = QLabel(subtitle)
        lbl_sub.setObjectName("suggestionCardSub")
        lbl_sub.setWordWrap(True)

        layout.addWidget(lbl_title)
        layout.addWidget(lbl_sub)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.query_text)
        super().mousePressEvent(event)


class WelcomeWidget(QWidget):
    """Greeting screen with suggestions when no chat messages exist."""
    suggestion_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("welcomeContainer")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        icon_lbl = QLabel("🤖")
        icon_lbl.setObjectName("welcomeIcon")
        icon_lbl.setAlignment(Qt.AlignCenter)

        title_lbl = QLabel("AI Customer Support Assistant")
        title_lbl.setObjectName("welcomeTitle")
        title_lbl.setAlignment(Qt.AlignCenter)

        subtitle_lbl = QLabel(
            "Welcome! Ask about order tracking, delivery schedules, product information, "
            "or file complaints. Powered entirely offline by your local n8n workflow and Ollama."
        )
        subtitle_lbl.setObjectName("welcomeSubtitle")
        subtitle_lbl.setAlignment(Qt.AlignCenter)
        subtitle_lbl.setWordWrap(True)

        layout.addWidget(icon_lbl)
        layout.addWidget(title_lbl)
        layout.addWidget(subtitle_lbl)

        # 2x2 Grid of suggested questions
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(14)
        grid.setContentsMargins(0, 10, 0, 0)

        card1 = SuggestionCard(
            "📦 Where is my order?",
            "Track package shipping details using your Order ID (e.g., ORD1001)",
            "Where is my order ORD1001?"
        )
        card1.clicked.connect(self.suggestion_selected.emit)

        card2 = SuggestionCard(
            "🔍 What is my order status?",
            "Check current order progress, amounts, and expected arrival date",
            "What is my order status for ORD1001?"
        )
        card2.clicked.connect(self.suggestion_selected.emit)

        card3 = SuggestionCard(
            "📝 I want to register a complaint.",
            "Describe your issue and register a new support ticket",
            "I want to register a complaint for order ORD1001. My email is customer@example.com."
        )
        card3.clicked.connect(self.suggestion_selected.emit)

        card4 = SuggestionCard(
            "⚠️ My product arrived damaged.",
            "Report damaged goods and create a complaint ticket automatically",
            "My product arrived damaged for order ORD1001. Please help me raise a complaint ticket. My email is customer@example.com."
        )
        card4.clicked.connect(self.suggestion_selected.emit)

        grid.addWidget(card1, 0, 0)
        grid.addWidget(card2, 0, 1)
        grid.addWidget(card3, 1, 0)
        grid.addWidget(card4, 1, 1)

        layout.addWidget(grid_widget)
        layout.addStretch()


class UserBubble(QWidget):
    """Right-aligned user chat bubble."""
    def __init__(self, text: str, timestamp: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("userBubbleWidget")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(30, 4, 10, 4)
        layout.setSpacing(8)
        layout.addStretch(1)

        card = QFrame()
        card.setObjectName("userBubbleCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 10, 14, 10)
        card_layout.setSpacing(4)

        msg_lbl = QLabel(text)
        msg_lbl.setObjectName("userMessageText")
        msg_lbl.setWordWrap(True)
        msg_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)

        card_layout.addWidget(msg_lbl)

        time_str = self._format_timestamp(timestamp)
        if time_str:
            time_lbl = QLabel(time_str)
            time_lbl.setObjectName("userMessageTime")
            time_lbl.setAlignment(Qt.AlignRight)
            card_layout.addWidget(time_lbl)

        layout.addWidget(card, 0)

    @staticmethod
    def _format_timestamp(ts: str) -> str:
        if not ts:
            return datetime.now().strftime("%I:%M %p")
        try:
            dt = datetime.fromisoformat(ts)
            return dt.strftime("%I:%M %p")
        except Exception:
            return ts[:16]


class BotBubble(QWidget):
    """Left-aligned AI assistant bubble with ticket/order badges if detected."""
    def __init__(
        self,
        text: str,
        timestamp: str = "",
        ticket_id: str = None,
        order_id: str = None,
        parent=None
    ):
        super().__init__(parent)
        self.setObjectName("botBubbleWidget")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 30, 4)
        layout.setSpacing(8)

        card = QFrame()
        card.setObjectName("botBubbleCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(8)

        # Header tag
        tag_lbl = QLabel("🛡️ Support Agent")
        tag_lbl.setStyleSheet("font-size: 11px; font-weight: 700; color: #60a5fa;")
        card_layout.addWidget(tag_lbl)

        # Message text
        msg_lbl = QLabel(text)
        msg_lbl.setObjectName("botMessageText")
        msg_lbl.setWordWrap(True)
        msg_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
        card_layout.addWidget(msg_lbl)

        # If a complaint ticket ID is present, render prominent ticket card
        if ticket_id:
            ticket_card = QFrame()
            ticket_card.setObjectName("ticketCard")
            t_layout = QVBoxLayout(ticket_card)
            t_layout.setContentsMargins(12, 10, 12, 10)
            t_layout.setSpacing(4)

            t_title = QLabel("✓ Complaint Ticket Created & Recorded")
            t_title.setObjectName("ticketCardHeader")

            t_id = QLabel(f"Ticket ID: {ticket_id}")
            t_id.setObjectName("ticketCardId")
            t_id.setTextInteractionFlags(Qt.TextSelectableByMouse)

            t_desc = QLabel("Recorded in the n8n complaint_tickets table with status: Open")
            t_desc.setStyleSheet("font-size: 11px; color: #94a3b8;")

            t_layout.addWidget(t_title)
            t_layout.addWidget(t_id)
            t_layout.addWidget(t_desc)
            card_layout.addWidget(ticket_card)

        # Timestamp
        time_str = UserBubble._format_timestamp(timestamp)
        if time_str:
            time_lbl = QLabel(time_str)
            time_lbl.setObjectName("botMessageTime")
            card_layout.addWidget(time_lbl)

        layout.addWidget(card, 0)
        layout.addStretch(1)


class ErrorBubble(QWidget):
    """System error notification bubble with troubleshooting help."""
    def __init__(self, title: str, details: str, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 4, 30, 4)

        card = QFrame()
        card.setObjectName("errorCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 12, 16, 12)
        card_layout.setSpacing(6)

        title_lbl = QLabel(f"⚠️ {title}")
        title_lbl.setObjectName("errorTitle")

        details_lbl = QLabel(details)
        details_lbl.setObjectName("errorDetails")
        details_lbl.setWordWrap(True)
        details_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)

        card_layout.addWidget(title_lbl)
        card_layout.addWidget(details_lbl)

        layout.addWidget(card, 0)
        layout.addStretch(1)


class TypingIndicator(QWidget):
    """Animated typing indicator showing AI agent processing state."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("typingIndicatorWidget")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        self.label = QLabel("🤖 AI Agent is thinking")
        self.label.setObjectName("typingText")
        layout.addWidget(self.label)
        layout.addStretch()

        self.dot_count = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)

    def start(self):
        self.dot_count = 0
        self.timer.start(350)
        self.show()

    def stop(self):
        self.timer.stop()
        self.hide()

    def _animate(self):
        self.dot_count = (self.dot_count + 1) % 4
        dots = "." * self.dot_count
        self.label.setText(f"🤖 AI Agent is thinking{dots}")


class ChatView(QWidget):
    """Scrollable container hosting conversation bubbles and headers."""
    suggestion_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Bar
        self.header = QWidget()
        self.header.setObjectName("chatHeader")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 12, 20, 12)

        titles_box = QVBoxLayout()
        titles_box.setSpacing(2)
        self.session_title = QLabel("Customer Support Assistant")
        self.session_title.setObjectName("chatHeaderTitle")
        self.session_sub = QLabel("Connected to local n8n AI Agent • Model: gemma4:26b")
        self.session_sub.setObjectName("chatHeaderSubtitle")
        titles_box.addWidget(self.session_title)
        titles_box.addWidget(self.session_sub)
        header_layout.addLayout(titles_box)

        header_layout.addStretch()

        self.pill_status = QLabel("● Service Check")
        self.pill_status.setObjectName("headerPillLive")
        header_layout.addWidget(self.pill_status)

        main_layout.addWidget(self.header)

        # Scroll Area for Messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("chatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Scroll Area Container Widget
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("messagesContainer")
        self.messages_layout = QVBoxLayout(self.scroll_content)
        self.messages_layout.setContentsMargins(18, 18, 18, 18)
        self.messages_layout.setSpacing(6)
        self.messages_layout.setAlignment(Qt.AlignTop)

        # Welcome Widget
        self.welcome_widget = WelcomeWidget()
        self.welcome_widget.suggestion_selected.connect(self.suggestion_requested.emit)
        self.messages_layout.addWidget(self.welcome_widget)

        # Typing Indicator (initially hidden)
        self.typing_indicator = TypingIndicator()
        self.typing_indicator.hide()

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area, 1)

    def set_session_info(self, title: str, session_id: str):
        """Update header bar with current session title and ID preview."""
        self.session_title.setText(title or "Support Chat")
        short_id = session_id[:8] if session_id else ""
        self.session_sub.setText(f"Session: #{short_id} • Local n8n Agent • Ollama gemma4:26b")

    def update_header_status(self, is_online: bool, text: str = "Online"):
        """Update the status pill in the top header."""
        if is_online:
            self.pill_status.setText(f"● {text}")
            self.pill_status.setObjectName("headerPillLive")
        else:
            self.pill_status.setText(f"● {text}")
            self.pill_status.setObjectName("headerPillWarning")
        self.pill_status.style().unpolish(self.pill_status)
        self.pill_status.style().polish(self.pill_status)

    def clear_view(self):
        """Remove all message bubbles."""
        # Hide welcome widget first
        self.welcome_widget.hide()
        # Remove bubble widgets except welcome & typing
        while self.messages_layout.count() > 0:
            item = self.messages_layout.takeAt(0)
            widget = item.widget()
            if widget and widget not in (self.welcome_widget, self.typing_indicator):
                widget.deleteLater()

    def show_welcome(self):
        """Reset view to welcome screen."""
        self.clear_view()
        self.messages_layout.addWidget(self.welcome_widget)
        self.welcome_widget.show()
        self.scroll_to_bottom()

    def display_session_messages(self, messages: list):
        """Load and display all messages for a session."""
        self.clear_view()
        if not messages:
            self.show_welcome()
            return

        self.welcome_widget.hide()
        for msg in messages:
            sender = msg.get("sender")
            text = msg.get("text", "")
            ts = msg.get("timestamp", "")
            meta = msg.get("metadata", {})

            if sender == "user":
                bubble = UserBubble(text, ts)
                self.messages_layout.addWidget(bubble)
            elif sender == "bot":
                ticket_id = meta.get("ticket_id")
                order_id = meta.get("order_id")
                bubble = BotBubble(text, ts, ticket_id, order_id)
                self.messages_layout.addWidget(bubble)
            elif sender == "error":
                title = meta.get("title", "Error")
                bubble = ErrorBubble(title, text)
                self.messages_layout.addWidget(bubble)

        self.scroll_to_bottom()

    def add_user_message(self, text: str, timestamp: str = ""):
        self.welcome_widget.hide()
        bubble = UserBubble(text, timestamp)
        self.messages_layout.addWidget(bubble)
        self.scroll_to_bottom()

    def add_bot_message(
        self,
        text: str,
        timestamp: str = "",
        ticket_id: str = None,
        order_id: str = None
    ):
        self.welcome_widget.hide()
        bubble = BotBubble(text, timestamp, ticket_id, order_id)
        self.messages_layout.addWidget(bubble)
        self.scroll_to_bottom()

    def add_error_message(self, title: str, details: str):
        self.welcome_widget.hide()
        bubble = ErrorBubble(title, details)
        self.messages_layout.addWidget(bubble)
        self.scroll_to_bottom()

    def set_typing(self, is_typing: bool):
        if is_typing:
            self.welcome_widget.hide()
            self.messages_layout.addWidget(self.typing_indicator)
            self.typing_indicator.start()
            self.scroll_to_bottom()
        else:
            self.typing_indicator.stop()
            self.messages_layout.removeWidget(self.typing_indicator)

    def scroll_to_bottom(self):
        """Smoothly auto-scroll to latest message."""
        QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))
