"""Agent 3 — Calendar Agent. Turns ideas into a 30-day rotating calendar."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage
from lib.claude_api import call_claude_json
from lib.persona import FULL_CONTEXT

PROMPT = """{persona}
Turn these ideas into a 30 day calendar: {ideas_json}

Rotate pillar and platform so consecutive days never repeat the same pillar+platform
combo. Weight toward Instagram for Craft/Process content, Facebook for Industry/
Culture content, per the platform split above.

For each day return an object with: day (1-30), date, topic, pillar, platform,
format, hook, best_posting_time, cta, goal (reach/engagement/shares/followers/
industry_credibility).

Return a JSON array of 30 such objects.
"""


def latest_ideas_file():
    files = [f for f in storage.list_files("ideas") if f.startswith("ideas_")]
    if not files:
        raise FileNotFoundError("No ideas file found — run ideation_agent.py first.")
    return sorted(files)[-1]


def run():
    storage.ensure_dirs()
    ideas = storage.read_json("ideas", latest_ideas_file())
    calendar = call_claude_json(
        PROMPT.format(persona=FULL_CONTEXT, ideas_json=json.dumps(ideas)),
        max_tokens=8192,
    )
    month = storage.today_str()[:7]
    path = storage.write_json(calendar, "calendar", f"calendar_{month}.json")
    print(f"Wrote {path} ({len(calendar)} days)")
    return calendar


if __name__ == "__main__":
    run()
