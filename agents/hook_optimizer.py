"""Agent 5 — Hook Optimizer. Rates and picks the best hook/opening line for a draft."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib.llm_api import call_llm_json
from lib.persona import FULL_CONTEXT

PROMPT = """{persona}
Based on this post: {draft}

Generate: 15 first-line hook options (IG) or opening-line options (FB) in the Voice
above, 10 caption/opening variations, 5 comment-bait questions that a fellow
filmmaker or genuine regional-cinema fan would actually want to answer — not generic
engagement bait.

Rate each for: curiosity, relatability to industry peers vs. general audience, share
potential, risk of sounding like generic marketing instead of an insider's voice.

Return JSON: {{"hooks": [...], "caption_variations": [...], "comment_bait_questions": [...],
"top_3": [{{"text": "...", "why": "..."}}]}}
"""


def optimize(draft_caption: str) -> dict:
    return call_llm_json(PROMPT.format(persona=FULL_CONTEXT, draft=draft_caption), max_tokens=16384)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(optimize(sys.argv[1]))
    else:
        print("Usage: python hook_optimizer.py '<draft caption text>'")
