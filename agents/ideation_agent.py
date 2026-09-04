"""Agent 2 — Ideation Agent. Generates 50 content ideas for the next 30 days."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage
from lib.llm_api import call_llm_json
from lib.persona import FULL_CONTEXT

PROMPT = """{persona}
Generate 50 content ideas for the next 30 days, spread across ALL SIX pillars
(Craft, Industry, Process, Culture, Personal Life, People & Reflection) — don't
over-index on the professional ones. Aim for roughly a third of the ideas to be
Personal Life or People & Reflection, not just Craft/Industry/Process/Culture.
Distribute across platforms per the Platform Split above; some Industry ideas
should be grounded in a real, current, specific happening or data point in the
regional/OTT space, not just an abstract opinion.

Vary genuinely: not every idea needs to be about your projects — books, plays,
a colleague, your son, a person who inspired you this week, a moment of pride or
struggle, are all fair game and should show up regularly, not as rare exceptions.

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
