"""
Settings Dialog Component.

Allows users to configure and test n8n webhook URLs, Ollama server parameters,
timeouts, and toggle between production and test webhooks.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QCheckBox, QPushButton, QSpinBox,
    QFrame, QMessageBox, QTextEdit, QScrollArea, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from config import AppConfig, save_config
from services.n8n_client import BackendHealthChecker


class SettingsDialog(QDialog):
    """Configuration modal for backend connection parameters."""
    settings_saved = pyqtSignal(AppConfig)

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsDialog")
        self.setWindowTitle("Settings — Backend Configuration")
        self.setFixedSize(620, 680)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.config = config
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(14)

        # Header
        header_title = QLabel("⚙️ Backend Connection Settings")
        header_title.setObjectName("dialogHeaderTitle")
        header_sub = QLabel(
            "Configure endpoints for your local n8n AI workflow and Ollama model. "
            "These services run locally and offline."
        )
        header_sub.setObjectName("dialogHeaderSub")
        header_sub.setWordWrap(True)
        layout.addWidget(header_title)
        layout.addWidget(header_sub)

        # Form Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(12)

        # 1. Production Webhook URL
        lbl_prod = QLabel("n8n Production Chat Webhook URL:")
        lbl_prod.setObjectName("fieldLabel")
        self.input_prod_url = QLineEdit(self.config.n8n_webhook_url)
        self.input_prod_url.setObjectName("settingsInput")
        self.input_prod_url.setPlaceholderText("http://localhost:5678/webhook/<webhook_id>/chat")
        form_layout.addWidget(lbl_prod)
        form_layout.addWidget(self.input_prod_url)

        # 2. Test Webhook URL
        lbl_test = QLabel("n8n Test Chat Webhook URL (Canvas test mode):")
        lbl_test.setObjectName("fieldLabel")
        self.input_test_url = QLineEdit(self.config.n8n_test_webhook_url)
        self.input_test_url.setObjectName("settingsInput")
        self.input_test_url.setPlaceholderText("http://localhost:5678/webhook-test/<webhook_id>/chat")
        form_layout.addWidget(lbl_test)
        form_layout.addWidget(self.input_test_url)

        # 3. Toggle Test Mode Checkbox
        self.chk_use_test = QCheckBox("Use Test Webhook URL instead of Production")
        self.chk_use_test.setChecked(self.config.use_test_endpoint)
        form_layout.addWidget(self.chk_use_test)

        # 4. Ollama Base URL
        lbl_ollama = QLabel("Ollama Server URL:")
        lbl_ollama.setObjectName("fieldLabel")
        self.input_ollama_url = QLineEdit(self.config.ollama_base_url)
        self.input_ollama_url.setObjectName("settingsInput")
        self.input_ollama_url.setPlaceholderText("http://127.0.0.1:11434")
        form_layout.addWidget(lbl_ollama)
        form_layout.addWidget(self.input_ollama_url)

        # 5. Ollama Model Name
        lbl_model = QLabel("Ollama Model Name:")
        lbl_model.setObjectName("fieldLabel")
        self.input_model = QLineEdit(self.config.ollama_model)
        self.input_model.setObjectName("settingsInput")
        self.input_model.setPlaceholderText("gemma4:26b")
        form_layout.addWidget(lbl_model)
        form_layout.addWidget(self.input_model)

        # 6. Request Timeout
        lbl_timeout = QLabel("Request Timeout (seconds):")
        lbl_timeout.setObjectName("fieldLabel")
        self.spin_timeout = QSpinBox()
        self.spin_timeout.setObjectName("settingsInput")
        self.spin_timeout.setRange(10, 600)
        self.spin_timeout.setValue(self.config.request_timeout)
        form_layout.addWidget(lbl_timeout)
        form_layout.addWidget(self.spin_timeout)

        # 7. Diagnostic Test Button
        btn_test = QPushButton("🔍 Test Connection Now")
        btn_test.setObjectName("btnTestConnection")
        btn_test.setCursor(Qt.PointingHandCursor)
        btn_test.clicked.connect(self._run_connection_test)
        form_layout.addWidget(btn_test)

        # Test results box
        self.test_output = QTextEdit()
        self.test_output.setObjectName("settingsInput")
        self.test_output.setReadOnly(True)
        self.test_output.setFixedHeight(120)
        self.test_output.setPlaceholderText("Click 'Test Connection Now' to verify n8n, Ollama, and Webhook status...")
        form_layout.addWidget(self.test_output)

        scroll.setWidget(form_widget)
        layout.addWidget(scroll, 1)

        # Action Buttons (Cancel / Save)
        btn_box = QHBoxLayout()
        btn_box.setSpacing(10)
        btn_box.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setObjectName("btnDialogCancel")
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)

        btn_save = QPushButton("Save Settings")
        btn_save.setObjectName("btnDialogSave")
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self._save_and_close)

        btn_box.addWidget(btn_cancel)
        btn_box.addWidget(btn_save)
        layout.addLayout(btn_box)

    def _run_connection_test(self):
        """Run diagnostics and print live results."""
        self.test_output.setPlainText("Testing local connection to n8n and Ollama...")
        # Create temp config from current dialog inputs
        temp_config = AppConfig(
            n8n_webhook_url=self.input_prod_url.text().strip(),
            n8n_test_webhook_url=self.input_test_url.text().strip(),
            use_test_endpoint=self.chk_use_test.isChecked(),
            ollama_base_url=self.input_ollama_url.text().strip(),
            ollama_model=self.input_model.text().strip(),
            request_timeout=self.spin_timeout.value()
        )

        results = BackendHealthChecker.check_all(temp_config)

        report = []
        # n8n
        if results["n8n_ok"]:
            report.append(f"✓ n8n Base: {results['n8n_message']}")
        else:
            report.append(f"✗ n8n Base: {results['n8n_message']}")

        # Ollama
        if results["ollama_ok"]:
            report.append(f"✓ Ollama Server: {results['ollama_message']}")
        else:
            report.append(f"✗ Ollama Server: {results['ollama_message']}")

        # Webhook
        if results["webhook_ok"]:
            report.append(f"✓ Webhook Route: {results['webhook_message']}")
        else:
            report.append(f"⚠️ Webhook Route: {results['webhook_message']}")

        effective_url = temp_config.get_effective_webhook_url()
        report.append(f"\nTarget Endpoint: {effective_url}")

        if not results["webhook_ok"] and "Inactive" in results["webhook_message"]:
            report.append(
                "\nHint: In n8n (http://localhost:5678), open workflow 'Customer Support Agent' "
                "and toggle the switch in the top bar to 'Active' / 'Publish'."
            )

        self.test_output.setPlainText("\n".join(report))

    def _save_and_close(self):
        """Persist settings and close dialog."""
        self.config.n8n_webhook_url = self.input_prod_url.text().strip()
        self.config.n8n_test_webhook_url = self.input_test_url.text().strip()
        self.config.use_test_endpoint = self.chk_use_test.isChecked()
        self.config.ollama_base_url = self.input_ollama_url.text().strip()
        self.config.ollama_model = self.input_model.text().strip()
        self.config.request_timeout = self.spin_timeout.value()

        if save_config(self.config):
            self.settings_saved.emit(self.config)
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "Failed to save configuration file.")
