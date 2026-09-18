# Project Status (last updated 2026-09-18)

Read this first if you're a new Claude Code session picking this project up —
it covers what's actually happened and what's still open, faster than reading
the full commit history.

## What this is

A content-ops system for a Facebook Page + Instagram Business account, running
24/7 on GitHub Actions (free tier). Every post is drafted automatically, sent to
the owner on Telegram for approval (tap-to-approve buttons, or reply to revise),
and only published once approved. See `README.md` for the architecture and
`SETUP_GUIDE.md` for the full setup walkthrough.

## Current persona (as of the last rebuild)

The account is **not** a hands-on filmmaker/cinematographer persona. The real
identity: the owner is **Content In-Charge at Darangplus** (an Odia OTT platform)
— greenlights web series/short films, procures content, writes/gathers stories,
and has real insider access to Odia film/OTT industry people and plans. The goal
is explicitly **maximum Instagram growth**, not a broad "whole person" account.

Content is weighted across 4 pillars (see `lib/persona.py` for the full text):
- **Industry Scoops** (~45%) — real, verified industry news only (see
  `data/industry_facts.md` — the owner should keep adding real facts there;
  the system is instructed to never invent statistics/claims).
- **Hot Takes & Opinions** (~25%) — lists, rankings, debate-bait opinions.
- **Project Highlights** (~15%) — real past work only, not fiction.
- **Personal Life** (~15%) — real family/life moments, zero industry voice mixed in.

**The one hard rule**: never write camera/lighting/on-set/craft language unless
the owner is genuinely, currently hands-on on a real set that day. Default to
Insider, Opinion, or Personal voice otherwise.

## Known limitations, on purpose

- The system writes Reel **scripts/concepts**, not actual video — auto-published
  Instagram posts are photo-based. Filming/editing Reels is still manual.
- Image generation (Gemini) is only used for Hot Takes / Industry Scoops, as a
  designed graphic-card style (never a fake photo of real people/events — that
  would misrepresent insider content). Project Highlights / Personal Life should
  use real photos the owner supplies via the Telegram quick-post flow.

## Infrastructure notes

- Repo is **Public** (needed for unlimited free GitHub Actions minutes at the
  polling frequency below — this exposes the content calendar/drafts/reports
  and any personal photos sent via quick-post, but GitHub Secrets stay protected
  regardless of visibility).
- Telegram approval polling runs ~every 1 minute via an external cron-job.org
  ping hitting the GitHub Actions API (GitHub's own `schedule:` trigger isn't
  reliable at tight intervals, kept only as a backup).
- Image hosting for Instagram uses imgbb.com (the repo being public means
  `raw.githubusercontent.com` URLs would actually work now too, but imgbb is
  already wired up and working — no need to switch back).
- Every workflow's git-commit step retries with `pull --rebase` since 5
  different workflows commit to `main` and can race each other.

## What's been recently fixed (2026-09-18 session)

- `page_engaged_users` Meta insights metric was deprecated by Meta (June 2026) —
  replaced with `page_post_engagements`.
- 17 stale drafts generated under the old pre-rebuild persona were rejected/cleared.
- The calendar batch in progress at rebuild time was forced to regenerate so the
  next daily post reflects the new strategy immediately.

## What to check / do next

- Confirm the next daily post actually reflects the new Industry-Insider voice
  (not old craft/filmmaker language) — check Telegram after the next `daily.yml`
  run or trigger it manually from the Actions tab.
- Keep adding real facts to `data/industry_facts.md` — Industry Scoops quality
  depends entirely on what's in there.
- Facebook publishing needs a **Page Access Token** specifically (not a User
  Access Token) — see `lib/meta_api.py` `post_to_facebook`; if Facebook posts
  ever start failing with permission errors again, this is the first thing to check.
