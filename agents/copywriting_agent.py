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
    (e.g. #OdiaCinema #OTTOdisha, or something specific to the actual project/topic)
    — never more than 6.
  - If it's personal, casual, or generic (not about your professional film work),
    OR the platform is Facebook: NO hashtags at all, full stop.
  - Either way, NEVER use a hashtag that's just a generic label describing the post
    TYPE rather than its actual specific subject — banned examples include #beautiful,
    #family, #industry, #personalpost, #viral, #instagood. A hashtag has to name the
    real, specific thing this post is about, not the category it falls into.
"""

CALENDAR_PROMPT = """{persona}
Write a complete post for this topic: {topic}
Pillar: {pillar} | Platform: {platform} | Format: {format}

The pillar sets direction, not a fixed template — write what actually fits:
- Industry Scoops: lead with the reveal/news itself, insider-voice, grounded only
  in real verified information — never invent a specific claim to sound more "in
  the know" than you actually are.
- Hot Takes & Opinions: a clear, specific opinion or list — built to make people
  agree/disagree in the comments, not just nod along.
- Project Highlights: real credibility, tied to actual past work — craft language
  is fine HERE specifically since it's about real work you actually did.
- Personal Life: write like an actual person sharing a real moment — no industry
  voice, no camera/lighting/craft language, no forced CTA, just something true.
If it's a Reel format: write it as a short script/shot-list concept (what's said,
what's shown, in order) — this is for the human to film, not an auto-published video.
If Instagram: open with a line that stops the scroll before "see more."
If Facebook: open with a line that earns a read (not a hook-for-hook's-sake line).
""" + LANGUAGE_STYLE + """
Write in the Voice defined above — perceptive, sharp, insider, never corporate.
Return ONLY the finished caption text, nothing else (no headers, no explanation).
"""

IMAGE_CONTEXT_PROMPT = """{persona}
I'm sending you a photo with this context from me: "{context}"

FIRST, work out what kind of moment this actually is — pick exactly one:
- INDUSTRY: a poster, a project announcement, an industry event/person, anything
  tied to your work — but as the insider/curator, NOT hands-on craft, UNLESS the
  photo is clearly an actual live shoot you're on (then craft language is fine).
- PERSONAL: family, your own life, a relationship, a personal moment or milestone —
  nothing to do with your work, even if the photo looks nice.
- GENERIC: doesn't clearly fit either (a general thought, something AI-related,
  a random observation, etc).

THEN write the post to match what you picked:
- If INDUSTRY (not an actual live shoot): write as the insider — what this means,
  why it matters, your actual take — NOT camera/lighting/color-grading language.
- If INDUSTRY and it IS an actual live shoot: craft language is fine here.
- If PERSONAL: do NOT mention camera angles, lighting, color grading, "on set," or
  any industry/craft language at all. Write like an actual person sharing a real
  moment — warm, simple, honest.
- If GENERIC: write naturally about what's actually there. Don't force an industry
  or film angle onto content that has nothing to do with it.

Platform: {platform} (pillar as given: {pillar}, but override this in your own head
if the content clearly isn't Industry — a personal or generic moment should
just read as a normal, honest post, pillar label aside).
""" + LANGUAGE_STYLE + """
Hashtags — override the general rule above with this: only include hashtags that are
genuinely specific to THIS post's actual subject. Never add #OdiaCinema, #OTTOdisha,
or any film-industry hashtag to a PERSONAL or GENERIC post — those only belong on
posts that are actually about your industry work. Never use a generic
label hashtag either way (#family, #beautiful, #personalpost, etc.) — a hashtag
names the real specific thing, not the category. A personal post can go with zero
hashtags, that's fine.

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
