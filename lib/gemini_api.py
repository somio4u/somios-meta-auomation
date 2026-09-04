import os
import base64
import requests

GEMINI_IMAGE_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image")


def generate_image(prompt: str, out_path: str) -> str:
    """Generates an image with Gemini and writes it to out_path.
    Model names on Google's side change over time — if this starts failing,
    check https://ai.google.dev/gemini-api/docs/image-generation for the current
    model id and update GEMINI_IMAGE_MODEL (env var) accordingly."""
    api_key = os.environ["GEMINI_API_KEY"]
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_IMAGE_MODEL}:generateContent?key={api_key}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    resp = requests.post(url, json=payload, timeout=120)
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
    base = (
        "Cinematic concept-art / moodboard still for an Odia OTT production. "
        "Moody, high-contrast color grade, film-still composition (not stock photo, "
        "not corporate, not clip-art). Shallow depth of field, naturalistic lighting."
    )
    if pillar.lower() == "process":
        base += " Style: raw behind-the-scenes monitor/set photo, slightly desaturated, documentary feel."
    return f"{base}\nSubject/topic: {topic}"
