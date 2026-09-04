# Odia OTT Storyteller — Content System

A 10-agent content-ops pipeline for a Facebook Page + Instagram Business account,
written as a Modern Regional Storyteller & OTT Creative Architect (Odia cinema).
Runs 24/7 on GitHub Actions (free tier) — no PC or app needs to stay open.
**Every post is reviewed and approved by you on Telegram before it goes live.**

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for the full first-time setup (Meta, Gemini,
Telegram, GitHub Secrets) — start there if this is your first time running it.

## How it works

```
GitHub Actions (cron)                                  Your phone
──────────────────────                                 ──────────
daily.yml   → Copywriting → Hook Optimizer → Visual  →  Telegram: draft sent
                                                          │
                                                    approve / reject / revise
                                                          │
poll_telegram.yml (every ~5 min)  ←──────────────────────
   └─ approve → Publisher Agent posts live to Facebook/Instagram
   └─ reject  → discarded
   └─ revise  → Copywriting rewrites it, resends for approval (loops)

weekly.yml  → Performance Analyst (pillar+platform breakdown, rebuilds next 7 days)
monthly.yml → Page Analyst + Growth Director (persona-drift check, rebuilds 30 days)
```

You can also just send the Telegram bot a **photo** (a poster/still) with a caption
describing context — it skips the calendar entirely and drafts a post around that
image, still gated by the same approve/reject/revise flow. See SETUP_GUIDE.md Step 10.

## Agent map

| # | Agent | File | Job |
|---|-------|------|-----|
| 1 | Page Analyst | `agents/page_analyst.py` | Monthly: checks live data against the persona/pillars, flags drift |
| 2 | Ideation Agent | `agents/ideation_agent.py` | Generates 50 ideas across pillars/platforms |
| 3 | Calendar Agent | `agents/calendar_agent.py` | Builds the rotating 30-day calendar |
| 4 | Copywriting Agent | `agents/copywriting_agent.py` | Writes full post copy in the Voice; also handles image+context posts and revisions |
| 5 | Hook Optimizer | `agents/hook_optimizer.py` | Rates/generates hook and caption variants for reference |
| 6 | Visual Agent | `agents/visual_agent.py` | Gemini-generated moodboard/concept-art image for Craft/Process posts |
| 7 | Publisher Agent | `agents/publisher_agent.py` | Sends drafts to Telegram for approval; only publishes once approved |
| 8 | Orchestrator | `orchestrator.py` | Runs the daily/weekly/monthly/poll pipelines, logs everything |
| 9 | Performance Analyst | `agents/performance_analyst.py` | Weekly pillar+platform performance review |
| 10 | Growth Director | `agents/growth_director.py` | Monthly full review + 3 growth scenarios, rebuilds the 30-day plan |
| — | Inbox Agent | `agents/inbox_agent.py` | Polls Telegram for your approve/reject/revise replies and photo posts |

The persona and content pillars live in one place — `lib/persona.py` — and every
agent imports from there, so the voice can't drift between agents.

## Folder structure

```
odia-ott-content-system/
  agents/            the 9 agents + inbox_agent
  lib/                persona.py, llm_api.py, gemini_api.py, meta_api.py,
                       telegram_api.py, image_host.py, storage.py
  data/
    insights/          raw Meta insights pulls
    ideas/             ideation output
    calendar/          30-day calendar + pointer.json (tracks which day is next)
    drafts/            copy + hook-optimizer output per day
    images/            Gemini-generated + user-supplied images (committed to
                       the repo so raw.githubusercontent.com can serve them
                       publicly for Instagram's API)
    pending_approval/  drafts awaiting your Telegram approve/reject/revise
    reports/           diagnosis / weekly / monthly / publish logs
  .github/workflows/   daily.yml, poll_telegram.yml, weekly.yml, monthly.yml, seed.yml
  orchestrator.py       entry point: daily | weekly | monthly | poll | seed
  requirements.txt
  .env.example          local-only reference; real values go in GitHub Secrets
```

## Running locally (optional, for testing before you rely on GitHub Actions)

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in real values, this file is gitignored
dotenv run -- python orchestrator.py seed     # first time only
dotenv run -- python orchestrator.py daily
dotenv run -- python orchestrator.py poll      # check Telegram replies
```

(`dotenv` here is the CLI that ships with the `python-dotenv` package in requirements.txt.)

## Known limits

- **Meta token expires ~every 60 days** — you'll need to regenerate it (SETUP_GUIDE §2). No automatic renewal is possible without a Meta "System User," which isn't set up here.
- **Persona drift** is the main thing to actively watch, not a bug — Performance Analyst checks for it weekly, Growth Director checks it monthly.
- **Gemini model names change** over time on Google's side — if image or text generation starts failing, check the current model ids (see SETUP_GUIDE troubleshooting) and override via the `GEMINI_IMAGE_MODEL` / `GEMINI_TEXT_MODEL` env vars.
- **One Google API key powers everything** — Gemini handles both text generation (ideas, captions, hooks, analysis) and image generation. There's no separate Anthropic/Claude key in this system.
- **Approval polling has up to a ~5 minute delay** (GitHub Actions cron granularity), not instant.
- **Posting cadence is intentionally capped at one post/day** by the daily calendar pointer, to stay well under Meta's spam-detection thresholds for automated posting.
- **Meta's Insights metric names change/deprecate periodically.** `lib/meta_api.py` uses reasonable defaults (`page_impressions`, `page_engaged_users`, `reach`, `profile_views`); if `page_analyst`/`performance_analyst`/`growth_director` start erroring on the insights call, check the current valid metric names at https://developers.facebook.com/docs/graph-api/reference/v21.0/insights and adjust the `metrics=` defaults in `lib/meta_api.py`.
