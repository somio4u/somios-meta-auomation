"""Agent 6 — Visual Agent. For Craft/Process pillar posts, generates a
moodboard/concept-art-style image via Gemini. Industry/Culture posts on Facebook
are text-forward by default — visuals stay optional there."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage
from lib.gemini_api import generate_image, build_visual_prompt

VISUAL_PILLARS = {"craft", "process"}


def maybe_generate(topic: str, pillar: str, draft_id: str):
    pillar_lower = pillar.lower()
    if not any(p in pillar_lower for p in VISUAL_PILLARS):
        return None
    prompt = build_visual_prompt(topic, pillar)
    rel_path = os.path.join("data", "images", f"{draft_id}.png")
    abs_path = os.path.join(storage.BASE, rel_path)
    generate_image(prompt, abs_path)
    return rel_path.replace("\\", "/")


if __name__ == "__main__":
    if len(sys.argv) > 3:
        print(maybe_generate(sys.argv[1], sys.argv[2], sys.argv[3]))
    else:
        print("Usage: python visual_agent.py '<topic>' '<pillar>' '<draft_id>'")
