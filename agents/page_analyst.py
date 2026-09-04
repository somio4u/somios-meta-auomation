"""Agent 1 — Page Analyst. Pulls live Page/IG data and checks it against the
persona and content pillars, then writes a 30-day roadmap."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage, meta_api
from lib.llm_api import call_llm
from lib.persona import FULL_CONTEXT

PROMPT = """{persona}
Here is my Page's data: {insights_json}

Analyze:
- How well does current content actually match my four pillars (Craft, Industry,
  Process, Culture)? Where has it drifted into generic content?
- Who is actually engaging with me, and which pillar do they respond to most?
- Which format is winning per platform (IG: carousel/reel/story; FB: long-form/
  milestone/dialogue)?
- What's silently killing my reach?

Finish with a realistic 30 day roadmap that pulls content back toward the pillars,
not away from them.
"""


def run():
    storage.ensure_dirs()
    insights = {
        "facebook": meta_api.get_page_insights(),
        "instagram": meta_api.get_ig_insights(),
    }
    storage.write_json(insights, "insights", f"insights_{storage.today_str()}.json")

    report = call_llm(PROMPT.format(persona=FULL_CONTEXT, insights_json=json.dumps(insights)))

    path = storage.append_markdown(report, "reports", f"page_diagnosis_{storage.today_str()}.md")
    print(f"Wrote {path}")
    return report


if __name__ == "__main__":
    run()
