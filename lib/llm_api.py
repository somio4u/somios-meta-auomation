import os
import json
import time
import requests

from lib import vertex_auth

DEFAULT_MODEL = os.environ.get("GEMINI_TEXT_MODEL", "gemini-3.5-flash")
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 7


def call_llm(prompt: str, system: str = None, max_tokens: int = 4096, model: str = None) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}

    url = vertex_auth.endpoint(model or DEFAULT_MODEL)
    last_error = None
    for attempt in range(MAX_RETRIES):
        resp = requests.post(url, json=payload, headers=vertex_auth.auth_headers(), timeout=120)
        if resp.status_code in RETRY_STATUS_CODES and attempt < MAX_RETRIES - 1:
            last_error = resp
            time.sleep(min(2 ** attempt, 30))  # 1,2,4,8,16,30,30s
            continue
        if resp.status_code == 403:
            raise RuntimeError(
                "Vertex AI returned 403 Forbidden. Check that: (1) the Vertex AI "
                "API is enabled on the GCP project in GCP_PROJECT_ID, and (2) the "
                "service account in GCP_SERVICE_ACCOUNT_KEY has the 'Vertex AI "
                "User' (roles/aiplatform.user) IAM role on that project. "
                "Raw response: " + resp.text[:500]
            )
        resp.raise_for_status()
        data = resp.json()
        parts = data["candidates"][0]["content"]["parts"]
        return "".join(p.get("text", "") for p in parts)

    last_error.raise_for_status()


def call_llm_json(prompt: str, system: str = None, max_tokens: int = 4096, model: str = None):
    text = call_llm(prompt + "\n\nRespond with ONLY valid JSON, no prose, no markdown fences.",
                     system=system, max_tokens=max_tokens, model=model)
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini did not return valid JSON: {e}\n\nRAW OUTPUT:\n{text}")
