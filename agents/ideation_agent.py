"""Agent 2 — Ideation Agent. Generates 10 content ideas for the next 5 days."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage
from lib.llm_api import call_llm_json
from lib.persona import FULL_CONTEXT

PROMPT = """{persona}
Here are real, verified facts about the Odia film/OTT industry (use ONLY these for
anything data-specific — do not invent your own statistics, numbers, dates, or
claims of fact; if you have nothing verified to say, keep the idea general instead
of fabricating a number to sound specific):
{industry_facts}

Generate 10 content ideas for the next 5 days, weighted by pillar like this (not
equal rotation — this weighting is deliberate for growth):
- 4-5 ideas: Industry Scoops — grounded ONLY in the verified facts above. If there
  isn't enough real material for 4-5 genuine scoops, don't pad with invented ones —
  fall back to Hot Takes instead.
- 2-3 ideas: Hot Takes & Opinions — lists, rankings, sharp opinions, debate-bait.
- 1-2 ideas: Project Highlights — real past work only.
- 1-2 ideas: Personal Life — real, honest, zero industry voice.

Never invent camera/lighting/on-set/craft language for an idea unless the topic
itself is explicitly about being hands-on on a real, current set.

For every idea include: topic, pillar, platform, format (note when a format is a
Reel — that means a script/shot-list for the human to film, not an auto-published
video), hook (the scroll-stopping IG hook or FB opening line), target_audience,
why_it_fits_persona, why_now.

Return a JSON array of 10 objects with exactly these keys: topic, pillar, platform,
format, hook, target_audience, why_it_fits_persona, why_now.
"""


def _load_industry_facts():
    text = storage.read_text("industry_facts.md", default=None)
    if not text:
        return "(none provided yet — don't fabricate any; keep Industry ideas general/opinion-based instead)"
    return text


def run():
    storage.ensure_dirs()
    facts = _load_industry_facts()
    ideas = call_llm_json(PROMPT.format(persona=FULL_CONTEXT, industry_facts=facts), max_tokens=8192)
    path = storage.write_json(ideas, "ideas", f"ideas_{storage.today_str()}.json")
    print(f"Wrote {path} ({len(ideas)} ideas)")
    return ideas


if __name__ == "__main__":
    run()
