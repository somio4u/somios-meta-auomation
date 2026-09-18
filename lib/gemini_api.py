import os
import base64
import time
import requests

from lib import vertex_auth

GEMINI_IMAGE_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
MAX_RETRIES = 7


def generate_image(prompt: str, out_path: str) -> str:
    """Generates an image with Gemini (via Vertex AI) and writes it to out_path.
    Model names on Google's side change over time — if this starts failing,
    check https://ai.google.dev/gemini-api/docs/image-generation for the current
    model id and update GEMINI_IMAGE_MODEL (env var) accordingly."""
    url = vertex_auth.endpoint(GEMINI_IMAGE_MODEL)
    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    resp = None
    for attempt in range(MAX_RETRIES):
        resp = requests.post(url, json=payload, headers=vertex_auth.auth_headers(), timeout=120)
        if resp.status_code in RETRY_STATUS_CODES and attempt < MAX_RETRIES - 1:
            time.sleep(min(2 ** attempt, 30))
            continue
        break
    resp.raise_for_status()
    data = resp.json()

    parts = data["candidates"][0]["content"]["parts"]
    image_b64 = None
    for p in parts:
        inline = p.get("inlineData") or p.get("inline_data")
        if inline:
            image_b64 = inline.get("data")
            break
    if not image_b64:
        raise RuntimeError(f"Gemini returned no image data: {data}")

    image_bytes = base64.b64decode(image_b64)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    return out_path


def build_visual_prompt(topic: str, pillar: str) -> str:
    """Generates a designed graphic-card style prompt — deliberately NOT a fake
    photo of real people/events (that would be misleading for insider/scoop
    content). This is for Hot Takes and Industry Scoops only; Project Highlights
    and Personal Life should use real photos, not AI-generated ones."""
    pillar_lower = pillar.lower()
    if "hot take" in pillar_lower:
        style = ("Bold, modern quote-card graphic design for an Instagram opinion post. "
                 "Strong typography-led layout, high contrast, dark cinematic background "
                 "texture (not a real photo of a specific person/place), editorial magazine feel.")
    else:
        style = ("Bold, modern 'breaking update' announcement graphic-card design for an "
                 "Instagram industry-news post. Strong typography-led layout, high contrast, "
                 "abstract cinematic background texture (not a real photo of a specific "
                 "person/event), editorial feel.")
    return f"{style}\nSubject/topic: {topic}"
