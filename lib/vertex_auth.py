"""Shared Vertex AI auth/endpoint helpers used by llm_api.py and gemini_api.py.

Vertex AI authenticates with a GCP service account (GCP_SERVICE_ACCOUNT_KEY,
the raw JSON key content, plus GCP_PROJECT_ID) instead of the Gemini Developer
API's api-key-in-URL model — this sidesteps Google's September 2026
deprecation of unrestricted Gemini API keys entirely, since IAM service
accounts were never affected by that change.
"""
import os
import json

from google.oauth2 import service_account
from google.auth.transport.requests import Request

_SCOPES = ["https://www.googleapis.com/auth/cloud-platform"]
_credentials = None


def _load_credentials():
    info = json.loads(os.environ["GCP_SERVICE_ACCOUNT_KEY"])
    return service_account.Credentials.from_service_account_info(info, scopes=_SCOPES)


def access_token() -> str:
    global _credentials
    if _credentials is None:
        _credentials = _load_credentials()
    if not _credentials.valid:
        _credentials.refresh(Request())
    return _credentials.token


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {access_token()}"}


def endpoint(model: str, method: str = "generateContent") -> str:
    project = os.environ["GCP_PROJECT_ID"]
    location = os.environ.get("GCP_LOCATION") or "us-central1"
    return (
        f"https://{location}-aiplatform.googleapis.com/v1/projects/{project}"
        f"/locations/{location}/publishers/google/models/{model}:{method}"
    )
