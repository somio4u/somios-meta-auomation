import json
import os
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(BASE, "data")

DIRS = [
    "insights", "ideas", "calendar", "drafts", "images",
    "images/user_supplied", "reports", "pending_approval", "telegram_state",
]


def ensure_dirs():
    for d in DIRS:
        os.makedirs(os.path.join(DATA, d), exist_ok=True)


def path(*parts):
    return os.path.join(DATA, *parts)


def read_text(*parts, default=None):
    p = path(*parts)
    if not os.path.exists(p):
        return default
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def read_json(*parts, default=None):
    p = path(*parts)
    if not os.path.exists(p):
        return default
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(data, *parts):
    p = path(*parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    return p


def append_markdown(text, *parts):
    p = path(*parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "a", encoding="utf-8") as f:
        f.write(text + "\n\n")
    return p


def list_files(*parts):
    p = path(*parts)
    if not os.path.isdir(p):
        return []
    return sorted(os.listdir(p))


def today_str():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def new_id():
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
