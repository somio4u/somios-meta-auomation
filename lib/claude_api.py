import os
from anthropic import Anthropic

_client = None

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-5")


def _get_client():
    global _client
    if _client is None:
        _client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


def call_claude(prompt: str, system: str = None, max_tokens: int = 4096, model: str = None) -> str:
    client = _get_client()
    kwargs = {}
    if system:
        kwargs["system"] = system
    response = client.messages.create(
        model=model or DEFAULT_MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
        **kwargs,
    )
    return "".join(block.text for block in response.content if block.type == "text")


def call_claude_json(prompt: str, system: str = None, max_tokens: int = 4096, model: str = None):
    """Calls Claude and parses the reply as JSON. Raises ValueError with the raw
    text attached if parsing fails, so callers can save the raw output for review
    instead of losing it."""
    import json
    text = call_claude(prompt + "\n\nRespond with ONLY valid JSON, no prose, no markdown fences.",
                        system=system, max_tokens=max_tokens, model=model)
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise ValueError(f"Claude did not return valid JSON: {e}\n\nRAW OUTPUT:\n{text}")
