"""
n8n Backend Communication Service and Background Workers.

Handles asynchronous HTTP requests to n8n AI Agent workflows using PyQt5 QThread,
maintaining an uninterrupted, non-blocking UI experience.
Provides health diagnostics for local n8n and Ollama instances.
"""

import re
import json
import requests
from typing import Optional, Dict, Any, Tuple
from PyQt5.QtCore import QThread, pyqtSignal
from config import AppConfig


class N8nChatWorker(QThread):
    """
    Background worker thread to dispatch chat queries to n8n webhook
    and parse the AI Agent response.
    """
    response_received = pyqtSignal(dict)  # {"text": str, "ticket_id": Optional[str], "order_id": Optional[str], "raw": Any}
    error_occurred = pyqtSignal(str, str, str)  # error_title, detailed_message, error_code
    finished_request = pyqtSignal()

    def __init__(
        self,
        webhook_url: str,
        message: str,
        session_id: str,
        timeout: int = 120,
        parent=None
    ):
        super().__init__(parent)
        self.webhook_url = webhook_url.strip()
        self.message = message.strip()
        self.session_id = session_id.strip()
        self.timeout = timeout
        self._is_cancelled = False

    def cancel(self):
        """Mark worker as cancelled."""
        self._is_cancelled = True

    def run(self):
        if self._is_cancelled:
            self.finished_request.emit()
            return

        payload = {
            "chatInput": self.message,
            "sessionId": self.session_id
        }

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*"
        }

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            if self._is_cancelled:
                self.finished_request.emit()
                return

            # Check HTTP Status Codes
            if response.status_code == 200:
                result_text, raw_data = self._parse_n8n_response(response)
                ticket_id = self._extract_ticket_id(result_text)
                order_id = self._extract_order_id(result_text)

                self.response_received.emit({
                    "text": result_text,
                    "ticket_id": ticket_id,
                    "order_id": order_id,
                    "raw": raw_data,
                    "status_code": 200
                })

            elif response.status_code == 404:
                error_body = response.text
                if "is not registered" in error_body or "webhook" in error_body.lower():
                    title = "n8n Workflow Not Active"
                    details = (
                        "n8n responded that the webhook endpoint is not registered (404).\n\n"
                        "How to resolve:\n"
                        "1. Open n8n in your browser (http://localhost:5678).\n"
                        "2. Open your 'Customer Support Agent' workflow.\n"
                        "3. Click the 'Publish' or 'Active' toggle switch in the top-right bar.\n"
                        "4. Alternatively, switch to the 'Test Webhook URL' in Settings if you are testing inside the n8n canvas editor."
                    )
                    code = "N8N_INACTIVE_WORKFLOW"
                else:
                    title = "Endpoint Not Found (404)"
                    details = f"The configured webhook URL was not found on n8n:\n{self.webhook_url}\n\nPlease check your Settings."
                    code = "HTTP_404"
                self.error_occurred.emit(title, details, code)

            elif response.status_code in (500, 502, 503, 504):
                title = f"n8n Workflow Execution Error ({response.status_code})"
                details = (
                    f"n8n encountered an internal error while processing your request:\n\n"
                    f"{response.text[:500]}\n\n"
                    "Possible causes:\n"
                    "- Local Ollama service is stopped or not responding\n"
                    "- The Ollama model 'gemma4:26b' failed to load\n"
                    "- An error occurred in the n8n Data Table query"
                )
                self.error_occurred.emit(title, details, "N8N_SERVER_ERROR")

            else:
                title = f"Unexpected Backend Response ({response.status_code})"
                details = f"Server returned unexpected status code: {response.status_code}\n\nResponse:\n{response.text[:400]}"
                self.error_occurred.emit(title, details, f"HTTP_{response.status_code}")

        except requests.exceptions.ConnectionError as e:
            title = "Connection Refused — Backend Unavailable"
            details = (
                f"Could not connect to n8n at:\n{self.webhook_url}\n\n"
                "Please verify that:\n"
                "1. n8n is running locally (e.g., Docker container 'n8n' on port 5678).\n"
                "2. Your computer's firewall is not blocking localhost connections.\n"
                "3. The port number matches your configuration."
            )
            self.error_occurred.emit(title, details, "CONNECTION_REFUSED")

        except requests.exceptions.Timeout:
            title = "Request Timed Out"
            details = (
                f"The request timed out after {self.timeout} seconds.\n\n"
                "The local Ollama model (gemma4:26b) may require more time to compute on your hardware. "
                "You can increase the timeout limit in Settings."
            )
            self.error_occurred.emit(title, details, "REQUEST_TIMEOUT")

        except Exception as e:
            title = "Unexpected Client Error"
            details = f"An unexpected error occurred while communicating with the backend:\n{str(e)}"
            self.error_occurred.emit(title, details, "CLIENT_EXCEPTION")

        finally:
            self.finished_request.emit()

    def _parse_n8n_response(self, response: requests.Response) -> Tuple[str, Any]:
        """
        Robustly extracts output text from diverse n8n response payloads:
        - {"output": "..."}
        - {"text": "..."}
        - [{"output": "..."}]
        - Streaming NDJSON lines
        - Plain text fallback
        """
        content_type = response.headers.get("Content-Type", "")

        # Try JSON parsing
        try:
            data = response.json()
            if isinstance(data, dict):
                # Standard LangChain AI agent response key in n8n
                if "output" in data:
                    return str(data["output"]), data
                if "text" in data:
                    return str(data["text"]), data
                if "response" in data:
                    return str(data["response"]), data
                if "message" in data:
                    return str(data["message"]), data
                # If wrapped inside an inner object
                if "data" in data and isinstance(data["data"], dict) and "output" in data["data"]:
                    return str(data["data"]["output"]), data

            elif isinstance(data, list) and len(data) > 0:
                first_item = data[0]
                if isinstance(first_item, dict):
                    if "output" in first_item:
                        return str(first_item["output"]), data
                    if "text" in first_item:
                        return str(first_item["text"]), data
                    if "json" in first_item and isinstance(first_item["json"], dict):
                        inner = first_item["json"]
                        if "output" in inner:
                            return str(inner["output"]), data
                        if "text" in inner:
                            return str(inner["text"]), data

            return json.dumps(data, indent=2), data

        except ValueError:
            # Handle NDJSON or plain text
            raw_text = response.text.strip()
            # If streaming NDJSON chunks
            lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
            collected_chunks = []
            for line in lines:
                try:
                    chunk = json.loads(line)
                    if isinstance(chunk, dict) and "output" in chunk:
                        collected_chunks.append(chunk["output"])
                    elif isinstance(chunk, dict) and "text" in chunk:
                        collected_chunks.append(chunk["text"])
                except Exception:
                    pass

            if collected_chunks:
                return "".join(collected_chunks), lines

            return raw_text if raw_text else "Empty response received from AI Agent.", raw_text

    def _extract_ticket_id(self, text: str) -> Optional[str]:
        """Detect complaint ticket IDs like TKT-1001 or TKT-1728738291000."""
        match = re.search(r"\b(TKT-[A-Za-z0-9\-_]+)\b", text, re.IGNORECASE)
        return match.group(1) if match else None

    def _extract_order_id(self, text: str) -> Optional[str]:
        """Detect order IDs like ORD1001."""
        match = re.search(r"\b(ORD[0-9]{3,8})\b", text, re.IGNORECASE)
        return match.group(1) if match else None


class BackendHealthChecker(QThread):
    """
    Background worker that probes n8n and Ollama connectivity
    and returns a health status summary.
    """
    health_checked = pyqtSignal(dict)

    def __init__(self, config: AppConfig, parent=None):
        super().__init__(parent)
        self.config = config

    def run(self):
        status = self.check_all(self.config)
        self.health_checked.emit(status)

    @classmethod
    def check_all(cls, config: AppConfig) -> dict:
        """Synchronously check n8n, Ollama, and the configured webhook."""
        n8n_ok, n8n_msg = cls.check_n8n_base(config.n8n_base_url)
        ollama_ok, ollama_msg, models = cls.check_ollama(config.ollama_base_url, config.ollama_model)
        webhook_ok, webhook_msg = cls.check_webhook_endpoint(config.get_effective_webhook_url())

        overall_ok = n8n_ok and ollama_ok and webhook_ok

        return {
            "overall_ok": overall_ok,
            "n8n_ok": n8n_ok,
            "n8n_message": n8n_msg,
            "ollama_ok": ollama_ok,
            "ollama_message": ollama_msg,
            "ollama_models": models,
            "webhook_ok": webhook_ok,
            "webhook_message": webhook_msg,
            "effective_url": config.get_effective_webhook_url(),
        }

    @staticmethod
    def check_n8n_base(base_url: str) -> Tuple[bool, str]:
        """Check if n8n server responds on its base URL."""
        try:
            url = base_url.rstrip("/") + "/"
            resp = requests.get(url, timeout=3)
            if resp.status_code in (200, 301, 302):
                return True, f"n8n server is online ({resp.status_code})"
            return False, f"n8n responded with HTTP {resp.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "n8n connection refused (service offline)"
        except requests.exceptions.Timeout:
            return False, "n8n connection timed out"
        except Exception as e:
            return False, f"n8n check failed: {str(e)}"

    @staticmethod
    def check_ollama(base_url: str, required_model: str = "gemma4:26b") -> Tuple[bool, str, list]:
        """Check if local Ollama responds and contains the desired model."""
        try:
            url = base_url.rstrip("/") + "/api/tags"
            resp = requests.get(url, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                model_names = [m.get("name") for m in data.get("models", [])]
                if required_model in model_names:
                    return True, f"Ollama is running with '{required_model}'", model_names
                else:
                    return True, f"Ollama online, but model '{required_model}' not found in: {model_names}", model_names
            return False, f"Ollama returned HTTP {resp.status_code}", []
        except requests.exceptions.ConnectionError:
            return False, "Ollama connection refused (not running on port 11434)", []
        except requests.exceptions.Timeout:
            return False, "Ollama connection timed out", []
        except Exception as e:
            return False, f"Ollama check failed: {str(e)}", []

    @staticmethod
    def check_webhook_endpoint(webhook_url: str) -> Tuple[bool, str]:
        """Probe the configured chat webhook endpoint."""
        try:
            # Send an empty or OPTIONS/POST ping with 0 chat input
            # n8n returns 404 with hint if workflow is inactive
            resp = requests.post(
                webhook_url,
                json={"chatInput": "__ping__", "sessionId": "__ping__"},
                timeout=4
            )
            if resp.status_code == 200:
                return True, "Webhook is live and accepting messages (200 OK)"
            elif resp.status_code == 404:
                if "is not registered" in resp.text:
                    return False, "Workflow exists in n8n but is Inactive / Unpublished"
                return False, f"Webhook URL not found (404)"
            return False, f"Webhook returned HTTP {resp.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Webhook connection refused"
        except requests.exceptions.Timeout:
            return False, "Webhook request timed out"
        except Exception as e:
            return False, f"Webhook probe error: {str(e)}"
