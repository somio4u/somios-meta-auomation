"""Agent 10 — Growth Director (monthly). Full review + 3 growth scenarios,
rebuilds the next 30-day plan."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage, meta_api
from lib.llm_api import call_llm
from lib.persona import FULL_CONTEXT
from agents import ideation_agent, calendar_agent

PROMPT = """{persona}
Reviewing a full month: {monthly_insights_json}

Tell me: which pillar is building genuine audience/industry credibility vs. just
reach, which platform is doing the heavier lifting, whether the persona is landing
as a real, whole person (not just "hands-on filmmaker" and not generic page content
either), ideal posting frequency per platform, KPIs to track weekly.

Build the next 30-day plan: 30 fresh ideas across all six pillars (Craft, Industry,
Process, Culture, Personal Life, People & Reflection), updated pillar weighting if
one is underperforming or one is crowding out the others, best formats to prioritize.

Give three growth scenarios: cautious, realistic, optimistic, based purely on actual
data. No income or follower count promises.
"""


def run():
    storage.ensure_dirs()
    insights = {
        "facebook": meta_api.get_page_insights(period="days_28"),
        "instagram": meta_api.get_ig_insights(period="days_28"),
    }
    report = call_llm(PROMPT.format(persona=FULL_CONTEXT, monthly_insights_json=json.dumps(insights)))
    path = storage.append_markdown(report, "reports", f"monthly_growth_{storage.today_str()}.md")
    print(f"Wrote {path}")

    # Rebuild the 30-day plan
    ideation_agent.run()
    calendar_agent.run()
    return report


if __name__ == "__main__":
    run()
