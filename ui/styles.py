"""
Modern Stylesheet (QSS) and Theme Definitions.

Provides professional, cohesive visual styling with deep slate hues,
refined typography, glowing status badges, and rounded message bubble cards.
"""

APP_STYLESHEET = """
/* Global Window Reset */
QWidget {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: #e2e8f0;
    background-color: transparent;
}

QMainWindow {
    background-color: #0f111a;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #131622;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: #2d334d;
    min-height: 25px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #475569;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    height: 0px;
}

/* Sidebar Styling */
#sidebarWidget {
    background-color: #161824;
    border-right: 1px solid #232738;
}

#sidebarHeader {
    padding: 18px 16px 14px 16px;
    border-bottom: 1px solid #232738;
}

#appLogoTitle {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 0.5px;
}

#appLogoSubtitle {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 2px;
}

#btnNewChat {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 12px 16px;
    text-align: center;
}

#btnNewChat:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #60a5fa, stop:1 #3b82f6);
}

#btnNewChat:pressed {
    background: #1d4ed8;
}

#sectionLabel {
    font-size: 11px;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1px;
    padding: 10px 16px 6px 16px;
}

/* Chat Session List */
QListWidget#sessionList {
    border: none;
    background-color: transparent;
    padding: 4px 8px;
}

QListWidget#sessionList::item {
    background-color: transparent;
    border-radius: 8px;
    padding: 10px 12px;
    margin: 3px 4px;
    color: #cbd5e1;
}

QListWidget#sessionList::item:hover {
    background-color: #212538;
    color: #ffffff;
}

QListWidget#sessionList::item:selected {
    background-color: #282e46;
    color: #ffffff;
    border-left: 3px solid #3b82f6;
}

/* Sidebar Footer & Status */
#sidebarFooter {
    background-color: #12141d;
    border-top: 1px solid #232738;
    padding: 12px 16px;
}

#statusBox {
    background-color: #1a1d2c;
    border: 1px solid #292e44;
    border-radius: 8px;
    padding: 8px 10px;
    margin-bottom: 8px;
}

#statusDotGreen {
    color: #10b981;
    font-size: 14px;
    font-weight: bold;
}

#statusDotYellow {
    color: #f59e0b;
    font-size: 14px;
    font-weight: bold;
}

#statusDotRed {
    color: #ef4444;
    font-size: 14px;
    font-weight: bold;
}

#btnSettings {
    background-color: #1e2235;
    color: #cbd5e1;
    font-size: 12px;
    font-weight: 500;
    border: 1px solid #2d334d;
    border-radius: 6px;
    padding: 8px 12px;
}

#btnSettings:hover {
    background-color: #2b304a;
    color: #ffffff;
    border-color: #3b82f6;
}

/* Main Chat Area Header */
#chatHeader {
    background-color: #131520;
    border-bottom: 1px solid #232738;
    padding: 14px 24px;
}

#chatHeaderTitle {
    font-size: 15px;
    font-weight: 700;
    color: #ffffff;
}

#chatHeaderSubtitle {
    font-size: 11px;
    color: #94a3b8;
}

#headerPillLive {
    background-color: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}

#headerPillWarning {
    background-color: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.35);
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}

#headerPillOffline {
    background-color: rgba(239, 68, 68, 0.15);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 600;
}

/* Welcome Screen */
#welcomeContainer {
    background-color: transparent;
    padding: 40px 20px;
}

#welcomeIcon {
    font-size: 48px;
    margin-bottom: 8px;
}

#welcomeTitle {
    font-size: 26px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}

#welcomeSubtitle {
    font-size: 14px;
    color: #94a3b8;
    max-width: 650px;
    line-height: 1.4;
    margin-top: 6px;
    margin-bottom: 24px;
}

#suggestionCard {
    background-color: #1a1d2e;
    border: 1px solid #282d45;
    border-radius: 12px;
    padding: 16px 18px;
    text-align: left;
}

#suggestionCard:hover {
    background-color: #232840;
    border-color: #3b82f6;
}

#suggestionCardTitle {
    font-size: 13px;
    font-weight: 600;
    color: #ffffff;
}

#suggestionCardSub {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 4px;
}

/* Message Bubbles */
#chatScrollArea {
    background-color: #0f111a;
    border: none;
}

#messagesContainer {
    background-color: #0f111a;
}

/* User Message */
#userBubbleWidget {
    background-color: transparent;
    margin-bottom: 14px;
}

#userBubbleCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2563eb, stop:1 #1d4ed8);
    border: none;
    border-radius: 14px;
    border-top-right-radius: 3px;
    padding: 12px 16px;
}

#userMessageText {
    font-size: 13.5px;
    color: #ffffff;
    line-height: 1.45;
}

#userMessageTime {
    font-size: 10.5px;
    color: #bfdbfe;
    margin-top: 6px;
}

/* AI Bot Message */
#botBubbleWidget {
    background-color: transparent;
    margin-bottom: 14px;
}

#botBubbleCard {
    background-color: #191c2b;
    border: 1px solid #282d44;
    border-radius: 14px;
    border-top-left-radius: 3px;
    padding: 14px 18px;
}

#botMessageText {
    font-size: 13.5px;
    color: #f1f5f9;
    line-height: 1.5;
}

#botMessageTime {
    font-size: 10.5px;
    color: #64748b;
    margin-top: 6px;
}

/* Ticket Verification Card */
#ticketCard {
    background-color: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.35);
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 8px;
}

#ticketCardHeader {
    font-size: 12px;
    font-weight: 700;
    color: #34d399;
}

#ticketCardId {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 14px;
    font-weight: 700;
    color: #ffffff;
    background-color: #132420;
    border: 1px solid #10b981;
    border-radius: 4px;
    padding: 3px 8px;
    margin: 6px 0;
}

/* Error Card */
#errorCard {
    background-color: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.35);
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 14px;
}

#errorTitle {
    font-size: 13.5px;
    font-weight: 700;
    color: #f87171;
}

#errorDetails {
    font-size: 12px;
    color: #cbd5e1;
    line-height: 1.45;
    margin-top: 6px;
}

/* Typing Indicator */
#typingIndicatorWidget {
    background-color: #191c2b;
    border: 1px solid #282d44;
    border-radius: 12px;
    padding: 10px 16px;
    margin-bottom: 12px;
}

#typingText {
    font-size: 12px;
    font-style: italic;
    color: #94a3b8;
}

/* Bottom Input Area */
#inputAreaWidget {
    background-color: #131520;
    border-top: 1px solid #232738;
    padding: 14px 24px 16px 24px;
}

#inputCard {
    background-color: #191c2c;
    border: 1px solid #2c324c;
    border-radius: 12px;
    padding: 4px 8px;
}

#inputCard:focus-within {
    border-color: #3b82f6;
    background-color: #1c2032;
}

QTextEdit#messageInput {
    background-color: transparent;
    border: none;
    color: #ffffff;
    font-size: 13.5px;
    padding: 8px 6px;
}

#btnSend {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3b82f6, stop:1 #2563eb);
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 8px 18px;
    margin: 4px;
}

#btnSend:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #60a5fa, stop:1 #3b82f6);
}

#btnSend:disabled {
    background-color: #272d42;
    color: #64748b;
}

#inputShortcutHint {
    font-size: 11px;
    color: #64748b;
    margin-top: 6px;
}

/* Settings Dialog */
QDialog#settingsDialog {
    background-color: #131622;
}

#dialogHeaderTitle {
    font-size: 18px;
    font-weight: 700;
    color: #ffffff;
}

#dialogHeaderSub {
    font-size: 12px;
    color: #94a3b8;
    margin-bottom: 14px;
}

QLabel#fieldLabel {
    font-size: 12.5px;
    font-weight: 600;
    color: #cbd5e1;
    margin-bottom: 4px;
}

QLineEdit#settingsInput {
    background-color: #1b1e2e;
    border: 1px solid #2d334c;
    border-radius: 8px;
    color: #ffffff;
    font-size: 13px;
    padding: 8px 12px;
}

QLineEdit#settingsInput:focus {
    border-color: #3b82f6;
}

QCheckBox {
    font-size: 12.5px;
    color: #cbd5e1;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid #475569;
    background-color: #1b1e2e;
}

QCheckBox::indicator:checked {
    background-color: #3b82f6;
    border-color: #3b82f6;
}

#btnTestConnection {
    background-color: #232840;
    color: #93c5fd;
    font-size: 12.5px;
    font-weight: 600;
    border: 1px solid #3b82f6;
    border-radius: 8px;
    padding: 8px 16px;
}

#btnTestConnection:hover {
    background-color: #2b3252;
}

#btnDialogSave {
    background-color: #2563eb;
    color: #ffffff;
    font-size: 13px;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
}

#btnDialogSave:hover {
    background-color: #1d4ed8;
}

#btnDialogCancel {
    background-color: #1f2334;
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 500;
    border: 1px solid #333a54;
    border-radius: 8px;
    padding: 8px 16px;
}

#btnDialogCancel:hover {
    background-color: #282d44;
}
"""
