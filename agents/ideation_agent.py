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

Generate 10 content ideas for the next 5 days, spread across ALL SIX pillars
(Craft, Industry, Process, Culture, Personal Life, People & Reflection) — don't
over-index on the professional ones. Include at least 3 that are Personal Life or
People & Reflection, not just Craft/Industry/Process/Culture.
Distribute across platforms per the Platform Split above; where an Industry idea
can genuinely use one of the verified facts above, ground it in that — otherwise
keep it a real, honest opinion rather than a fabricated data point.

Vary genuinely: not every idea needs to be about your projects — books, plays,
a colleague, your son, a person who inspired you this week, a moment of pride or
struggle, are all fair game and should show up regularly, not as rare exceptions.

For every idea include: topic, pillar, platform, format, hook (the scroll-stopping
IG hook or FB opening line), target_audience, why_it_fits_persona, why_now.

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
    ideas = call_llm_json(PROMPT.format(persona=FULL_CONTEXT, industry_facts=facts), max_tokens=16384)
    path = storage.write_json(ideas, "ideas", f"ideas_{storage.today_str()}.json")
    print(f"Wrote {path} ({len(ideas)} ideas)")
    return ideas


if __name__ == "__main__":
    run()
