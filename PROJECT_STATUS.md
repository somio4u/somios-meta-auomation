# Project Status (last updated 2026-09-18, third pass)

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

## Active blocker: migrated Gemini calls to Vertex AI, owner still needs to do the GCP setup

The pipeline has been silently stuck since 2026-09-17 — no draft has gone to
Telegram approval since 09-16. Root cause, found by reading
`data/reports/orchestrator_log_2026-09.md`: the calendar pointer hit
`next_day: 6` on a 5-day batch, correctly triggering `auto_reseed`, which
calls Gemini and got **`403 Forbidden`**. This was **not** a stale-model-id
problem — Google retired unrestricted "Standard" Gemini API keys entirely in
September 2026, and the `GEMINI_API_KEY` secret here was one of those.

Rather than just rotate to a new-style "Authorization" key, the code has now
been switched to call Gemini through **Vertex AI** (GCP service-account auth)
instead of the Gemini Developer API (API-key auth) — this sidesteps the
whole API-key deprecation class of problem going forward, since IAM service
accounts don't expire the way API keys/rotate policies do.

What changed in code (already committed/pushed to this branch):
- New `lib/vertex_auth.py` — shared helper that turns a service-account JSON
  key (`GCP_SERVICE_ACCOUNT_KEY` env var) into a Bearer token via `google-auth`,
  and builds the `{location}-aiplatform.googleapis.com` endpoint URL from
  `GCP_PROJECT_ID` (+ optional `GCP_LOCATION`, defaults to `us-central1`).
- `lib/llm_api.py` and `lib/gemini_api.py` now call `vertex_auth.endpoint(...)`
  with `vertex_auth.auth_headers()` instead of building a `?key=` URL.
- `requirements.txt` gained `google-auth`.
- All 5 workflow YAML files (`daily`, `weekly`, `monthly`, `poll_telegram`,
  `seed`) now pass `GCP_PROJECT_ID` / `GCP_SERVICE_ACCOUNT_KEY` instead of
  `GEMINI_API_KEY`.
- `SETUP_GUIDE.md` Step 5 rewritten for the GCP project / Vertex AI API
  enable / service account / IAM role / JSON key flow; secrets table and
  troubleshooting section updated to match.

What's still needed from the repo owner (can't be done from a Claude Code
session — needs their Google Cloud console access):
1. Create/pick a GCP project, note its Project ID.
2. Enable the Vertex AI API on it.
3. Create a service account, grant it the **Vertex AI User** role.
4. Create a JSON key for it, download it.
5. Add `GCP_PROJECT_ID` and `GCP_SERVICE_ACCOUNT_KEY` (the raw JSON file
   contents) as GitHub repo secrets — `GEMINI_API_KEY` can be deleted once
   this is confirmed working.
6. Trigger `daily.yml` manually (or wait for the next scheduled run) — it
   should self-heal on its own since the calendar pointer was never advanced
   past the failed attempt.

## What to check / do next

- **Do the Vertex AI setup above first** — nothing else in this list matters
  until posts are flowing again.
- Confirm the next daily post actually reflects the new Industry-Insider voice
  (not old craft/filmmaker language) — check Telegram after the next `daily.yml`
  run or trigger it manually from the Actions tab.
- Keep adding real facts to `data/industry_facts.md` — Industry Scoops quality
  depends entirely on what's in there.
- Facebook publishing needs a **Page Access Token** specifically (not a User
  Access Token) — see `lib/meta_api.py` `post_to_facebook`; if Facebook posts
  ever start failing with permission errors again, this is the first thing to check.
