"""Agent 4 — Copywriting Agent. Writes full post copy in the Voice.

Two entry points:
- write_from_calendar_day(day): normal scheduled-calendar flow
- write_from_image_context(context, pillar, platform): the "I'm sending you a
  poster/photo with context" flow you can trigger from Telegram
- revise(draft, feedback): regenerate a draft using your Telegram feedback
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage
from lib.llm_api import call_llm
from lib.persona import FULL_CONTEXT

LANGUAGE_STYLE = """
LANGUAGE AND LENGTH (strict):
- Plain, everyday English — the words a person actually says out loud, not essay
  vocabulary. If a simpler word says the same thing, use the simpler word.
- SHORT. A handful of short lines total (roughly 3-6 short sentences/lines), not
  paragraphs of prose, even for Facebook.
- Hashtags depend on what this post is actually about:
  - If it's genuinely about your professional film/OTT work, AND the platform is
    Instagram: end with 3-6 specific, niche hashtags relevant to this exact post
    (e.g. #OdiaCinema #OTTOdisha) — never generic ones like #viral or #instagood,
    never more than 6.
  - If it's personal, casual, or generic (not about your professional film work),
    OR the platform is Facebook: NO hashtags at all, full stop. Do not add
    #OdiaCinema, #OTTOdisha, or any other hashtag just because it's a habit.
"""

CALENDAR_PROMPT = """{persona}
Write a complete post for this topic: {topic}
Pillar: {pillar} | Platform: {platform} | Format: {format}

If Instagram: first line hook that stops the scroll before "see more," then a short
craft-focused insight or BTS moment, one line inviting comments, a natural non-salesy
CTA.
If Facebook: an opening line that earns a read (not a hook-for-hook's-sake line),
then a short, genuine reflection or industry observation, ending in either a
milestone note, a tag to collaborators, or an open question to the audience.
""" + LANGUAGE_STYLE + """
Write in the Voice defined above — perceptive, witty, insider, never corporate.
Return ONLY the finished caption text, nothing else (no headers, no explanation).
"""

IMAGE_CONTEXT_PROMPT = """{persona}
I'm sending you a photo with this context from me: "{context}"

FIRST, work out what kind of moment this actually is — pick exactly one:
- PROFESSIONAL: a poster, a shot from a project, a craft/BTS moment, anything
  genuinely tied to your filmmaking work.
- PERSONAL: family, your own life, a relationship, a personal moment or milestone —
  nothing to do with your professional film work, even if the photo looks nice.
- GENERIC: doesn't clearly fit either (a general thought, something AI-related,
  a random observation, etc).

THEN write the post to match what you picked:
- If PROFESSIONAL: write as the filmmaker persona — craft-focused insight tied to
  what's in the image (lighting/color/framing/etc. ONLY if genuinely relevant to
  what's actually in the photo), in the established Voice.
- If PERSONAL: do NOT mention camera angles, lighting, color grading, "on set," or
  any filmmaking/craft language at all. Write like an actual person sharing a real
  moment — warm, simple, honest. No OTT/film-industry framing.
- If GENERIC: write naturally about what's actually there. Don't force a film angle
  onto content that has nothing to do with filmmaking.

Platform: {platform} (pillar as given: {pillar}, but override this in your own head
if the content clearly isn't Professional — a personal or generic moment should
just read as a normal, honest post, pillar label aside).
""" + LANGUAGE_STYLE + """
Hashtags — override the general rule above with this: only include hashtags that are
genuinely specific to THIS post's actual subject. Never add #OdiaCinema, #OTTOdisha,
or any film-industry hashtag to a PERSONAL or GENERIC post — those only belong on
posts that are actually about your professional film work. A personal post can go
with zero hashtags, or none at all, that's fine.

Write in the Voice defined above. Return ONLY the finished caption text.
"""

REVISE_PROMPT = """{persona}
Here is a draft post you wrote:
---
{draft}
---
I want this change: "{feedback}"

If my feedback says this is personal, casual, generic, or otherwise not about your
professional film work, strip out ALL camera/lighting/color-grading/"on set"/film-craft
language and industry hashtags entirely — write it like an actual person, not a
filmmaker persona.
""" + LANGUAGE_STYLE + """
Rewrite the full post incorporating that feedback, staying in the Voice defined above.
Return ONLY the finished caption text, nothing else.
"""


def write_from_calendar_day(day: dict) -> str:
    return call_llm(CALENDAR_PROMPT.format(
        persona=FULL_CONTEXT,
        topic=day["topic"], pillar=day["pillar"],
        platform=day["platform"], format=day.get("format", ""),
    ))


def write_from_image_context(context: str, pillar: str, platform: str) -> str:
    return call_llm(IMAGE_CONTEXT_PROMPT.format(
        persona=FULL_CONTEXT, context=context, pillar=pillar, platform=platform,
    ))


def revise(draft: str, feedback: str) -> str:
    return call_llm(REVISE_PROMPT.format(persona=FULL_CONTEXT, draft=draft, feedback=feedback))


def run_for_day(day: dict):
    storage.ensure_dirs()
    caption = write_from_calendar_day(day)
    draft = {"caption": caption, "pillar": day["pillar"], "platform": day["platform"],
              "topic": day["topic"], "format": day.get("format", "")}
    path = storage.write_json(draft, "drafts", f"day_{day['day']}_draft.json")
    print(f"Wrote {path}")
    return draft


if __name__ == "__main__":
    if len(sys.argv) > 1:
        day_arg = json.loads(sys.argv[1])
        run_for_day(day_arg)
    else:
        print("Usage: python copywriting_agent.py '<day-json>'")
