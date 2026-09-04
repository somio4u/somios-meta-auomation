import os
import json
import requests

DEFAULT_MODEL = os.environ.get("GEMINI_TEXT_MODEL", "gemini-flash-latest")


def _endpoint(model):
    api_key = os.environ["GEMINI_API_KEY"]
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"


def call_llm(prompt: str, system: str = None, max_tokens: int = 4096, model: str = None) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": max_tokens},
    }
    if system:
        payload["systemInstruction"] = {"parts": [{"text": system}]}
    resp = requests.post(_endpoint(model or DEFAULT_MODEL), json=payload, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts)


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
