"""Agent 2 — Ideation Agent. Generates 50 content ideas for the next 30 days."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage
from lib.llm_api import call_llm_json
from lib.persona import FULL_CONTEXT

PROMPT = """{persona}
Generate 50 content ideas for the next 30 days, tagged by pillar (Craft/Industry/
Process/Culture) and platform (Instagram/Facebook). Distribute roughly:
- Instagram: Framing the Story carousels, OTT & Film Insights reels, Director's
  Journal stories, Modern Tools/Creative Tech teasers
- Facebook: Deep Dives on regional cinema, Milestones & Team Spotlights, Writer-
  Director's Desk reflections, Audience Dialogues

For every idea include: topic, pillar, platform, format, hook (the scroll-stopping
IG hook or FB opening line), target_audience, why_it_fits_persona, why_now.

Return a JSON array of 50 objects with exactly these keys: topic, pillar, platform,
format, hook, target_audience, why_it_fits_persona, why_now.
"""


def run():
    storage.ensure_dirs()
    ideas = call_llm_json(PROMPT.format(persona=FULL_CONTEXT), max_tokens=16384)
    path = storage.write_json(ideas, "ideas", f"ideas_{storage.today_str()}.json")
    print(f"Wrote {path} ({len(ideas)} ideas)")
    return ideas


if __name__ == "__main__":
    run()
