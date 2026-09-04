"""Agent 3 — Calendar Agent. Turns ideas into a 5-day rotating calendar."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage
from lib.llm_api import call_llm_json
from lib.persona import FULL_CONTEXT

PROMPT = """{persona}
Turn these ideas into a 5 day calendar: {ideas_json}

Rotate across all six pillars so consecutive days never repeat the same
pillar+platform combo, and so Personal Life / People & Reflection show up in
this batch too, not just the professional pillars. Weight toward Instagram for
Craft/Process/visual-Personal content, Facebook for Industry/Culture/Reflection
content, per the platform split above — but the pillar just sets direction, the
day's actual post has freedom within it.

For each day return an object with: day (1-5), date, topic, pillar, platform,
format, hook, best_posting_time, cta, goal (reach/engagement/shares/followers/
industry_credibility).

Return a JSON array of 5 such objects.
"""


def latest_ideas_file():
    files = [f for f in storage.list_files("ideas") if f.startswith("ideas_")]
    if not files:
        raise FileNotFoundError("No ideas file found — run ideation_agent.py first.")
    return sorted(files)[-1]


def run():
    storage.ensure_dirs()
    ideas = storage.read_json("ideas", latest_ideas_file())
    calendar = call_llm_json(
        PROMPT.format(persona=FULL_CONTEXT, ideas_json=json.dumps(ideas)),
        max_tokens=8192,
    )
    path = storage.write_json(calendar, "calendar", f"calendar_{storage.new_id()}.json")
    print(f"Wrote {path} ({len(calendar)} days)")
    return calendar


if __name__ == "__main__":
    run()
