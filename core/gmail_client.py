import os
import base64
import logging
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger("GmailAIResponder")
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


class GmailClient:
    def __init__(self, credentials_file="config/credentials.json", token_file="config/token.json"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing Gmail API token...")
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    raise FileNotFoundError(
                        f"credentials.json not found at {self.credentials_file}.\n"
                        "Download from: https://console.cloud.google.com/apis/credentials"
                    )
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, "w") as f:
                f.write(creds.to_json())
        return build("gmail", "v1", credentials=creds)

    def fetch_unread(self, max_results=10):
        try:
            query = "is:unread label:INBOX -category:promotions -category:social"
            res = self.service.users().messages().list(
                userId="me", q=query, maxResults=max_results
            ).execute()
            return res.get("messages", [])
        except HttpError as e:
            logger.error(f"Failed to fetch emails: {e}")
            return []

    def get_detail(self, msg_id):
        try:
            msg = self.service.users().messages().get(
                userId="me", id=msg_id, format="full"
            ).execute()
            headers = {h["name"].lower(): h["value"] for h in msg["payload"]["headers"]}
            body = self._extract_body(msg["payload"])
            return {
                "id": msg_id,
                "threadId": msg["threadId"],
                "subject": headers.get("subject", "(no subject)"),
                "sender": headers.get("from", ""),
                "body": body,
            }
        except Exception as e:
            logger.error(f"Failed to get detail for {msg_id}: {e}")
            return None

    def _extract_body(self, payload):
        if "parts" in payload:
            for part in payload["parts"]:
                text = self._extract_body(part)
                if text:
                    return text
        if payload.get("mimeType") == "text/plain":
            data = payload["body"].get("data", "")
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
        return ""

    def send_reply(self, email_detail, reply_body):
        subject = email_detail["subject"]
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"
        mime = MIMEText(reply_body)
        mime["to"] = email_detail["sender"]
        mime["subject"] = subject
        mime["In-Reply-To"] = email_detail["threadId"]
        mime["References"] = email_detail["threadId"]
        raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
        try:
            self.service.users().messages().send(
                userId="me",
                body={"raw": raw, "threadId": email_detail["threadId"]}
            ).execute()
            logger.info(f"Reply sent to {email_detail['sender']}")
            return True
        except Exception as e:
            logger.error(f"Failed to send reply: {e}")
            return False

    def mark_processed(self, msg_id, label_name):
        all_labels = self.service.users().labels().list(userId="me").execute().get("labels", [])
        label_map = {l["name"]: l["id"] for l in all_labels}
        if label_name not in label_map:
            created = self.service.users().labels().create(
                userId="me",
                body={"name": label_name, "labelListVisibility": "labelShow",
                      "messageListVisibility": "show"},
            ).execute()
            label_id = created["id"]
        else:
            label_id = label_map[label_name]
        self.service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"removeLabelIds": ["UNREAD"], "addLabelIds": [label_id]},
        ).execute()
