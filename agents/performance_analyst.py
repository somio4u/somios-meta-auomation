"""Agent 9 — Performance Analyst (weekly). Reviews pillar/platform performance
and rebuilds the next 7 days."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage, meta_api
from lib.claude_api import call_claude
from lib.persona import FULL_CONTEXT

PROMPT = """{persona}
Here is my performance data from last week: {insights_json}

Break results down by pillar AND platform, not just by post. Tell me: which pillar
is actually resonating, which platform is underperforming for which pillar, top 3
posts and why, bottom 3 and why, any post that broke persona voice and how it
performed relative to on-persona posts, formats worth doubling down on, formats to
drop. Rebuild the next 7 days based on what actually happened.
"""


def run():
    storage.ensure_dirs()
    insights = {
        "facebook": meta_api.get_page_insights(),
        "instagram": meta_api.get_ig_insights(),
        "publish_log": storage.read_text("reports", f"publish_log_{storage.today_str()[:7]}.md", default=None),
    }
    report = call_claude(PROMPT.format(persona=FULL_CONTEXT, insights_json=json.dumps(insights)))
    path = storage.append_markdown(report, "reports", f"weekly_performance_{storage.today_str()}.md")
    print(f"Wrote {path}")
    return report


if __name__ == "__main__":
    run()
