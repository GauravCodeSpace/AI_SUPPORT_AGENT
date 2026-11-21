"""
Message Input Widget Component.

Provides a multi-line auto-wrapping text input that sends on Enter
and inserts a new line on Shift+Enter, accompanied by a styled Send button.
"""

from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTextEdit,
    QPushButton, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize


class ChatInputField(QTextEdit):
    """Custom QTextEdit capturing Enter and Shift+Enter keystrokes."""
    send_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("messageInput")
        self.setPlaceholderText("Ask about your order, delivery status, or describe an issue... (Enter to send)")
        self.setAcceptRichText(False)
        self.setFixedHeight(54)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                # Shift+Enter: insert standard newline
                super().keyPressEvent(event)
            else:
                # Enter alone: emit send request
                self.send_requested.emit()
                event.accept()
        else:
            super().keyPressEvent(event)


class MessageInputWidget(QWidget):
    """Full input control panel with input card, send button, and keyboard hint."""
    message_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("inputAreaWidget")
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(18, 10, 18, 14)
        main_layout.setSpacing(6)

        # Container Card
        card = QWidget()
        card.setObjectName("inputCard")
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(10, 4, 6, 4)
        card_layout.setSpacing(8)

        # Input field
        self.input_field = ChatInputField()
        self.input_field.send_requested.connect(self._on_send_clicked)
        card_layout.addWidget(self.input_field, 1)

        # Send Button
        self.btn_send = QPushButton("Send ➤")
        self.btn_send.setObjectName("btnSend")
        self.btn_send.setCursor(Qt.PointingHandCursor)
        self.btn_send.clicked.connect(self._on_send_clicked)
        card_layout.addWidget(self.btn_send, 0, Qt.AlignVCenter)

        main_layout.addWidget(card)

        # Shortcut hint
        hint_layout = QHBoxLayout()
        hint_layout.setContentsMargins(4, 0, 4, 0)
        self.hint_label = QLabel("Press Enter to send, Shift+Enter for new line • Local offline processing")
        self.hint_label.setObjectName("inputShortcutHint")
        hint_layout.addWidget(self.hint_label)
        hint_layout.addStretch()

        main_layout.addLayout(hint_layout)

    def _on_send_clicked(self):
        text = self.input_field.toPlainText().strip()
        if text:
            self.input_field.clear()
            self.message_submitted.emit(text)

    def set_loading(self, is_loading: bool):
        """Enable or disable input while waiting for AI response."""
        self.btn_send.setEnabled(not is_loading)
        self.input_field.setEnabled(not is_loading)
        if is_loading:
            self.btn_send.setText("Sending...")
        else:
            self.btn_send.setText("Send ➤")
            self.input_field.setFocus()

    def set_text(self, text: str):
        """Pre-populate input text (e.g. from suggestion card)."""
        self.input_field.setPlainText(text)
        self.input_field.setFocus()
        cursor = self.input_field.textCursor()
        cursor.movePosition(cursor.End)
        self.input_field.setTextCursor(cursor)
