# Setup Guide (start to finish, zero prior Meta/GitHub-Actions experience assumed)

Do these in order. Nothing goes live to Facebook/Instagram until you approve it on Telegram — that gate is built into the code, not something you have to remember to enable.

---

## 1. Push this folder to a GitHub repo

1. Go to https://github.com/new
2. Repository name: `odia-ott-content-system` (or anything you like)
3. Set it to **Private** (it will hold your automation code — the actual secrets never go into the repo itself, see step 5).
4. Don't initialize with a README (you already have files here).
5. On your PC, in this folder, run:

```bash
git init
git add .
git commit -m "Initial content system"
git branch -M main
git remote add origin https://github.com/<your-username>/odia-ott-content-system.git
git push -u origin main
```

If asked to sign in, use your GitHub username and a **Personal Access Token** as the password (GitHub → Settings → Developer settings → Personal access tokens → generate one with `repo` scope) — GitHub stopped accepting plain passwords for git operations.

---

## 2. Meta Developer setup (Facebook + Instagram)

**Prerequisites:**
- A Facebook **Page** for your brand (not a personal profile).
- Your Instagram account switched to **Business or Creator** (Instagram app → Settings → Account type).
- Instagram linked to the Page (Facebook Page → Settings → Linked Accounts → Instagram).

**Steps:**
1. https://developers.facebook.com → **My Apps → Create App** → type **Business** → name it, e.g. "Odia OTT Content System".
2. In the app dashboard, **Add Product** → add **Facebook Login** and **Instagram Graph API**.
3. Go to https://developers.facebook.com/tools/explorer → select your app → select your Page under "User or Page" → **Get Token → Get User Access Token** → check these permissions:
   `pages_show_list`, `pages_read_engagement`, `pages_read_user_content`, `pages_manage_posts`, `instagram_basic`, `instagram_manage_insights`, `instagram_content_publish`
   → **Generate Access Token**.
4. This token expires in ~1 hour — exchange it for a long-lived one (~60 days). In a terminal (App ID/Secret are under app dashboard → Settings → Basic):

```bash
curl -i -X GET "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id={app-id}&client_secret={app-secret}&fb_exchange_token={short-lived-token}"
```

5. Get your Page ID:
```bash
curl -i -X GET "https://graph.facebook.com/v21.0/me/accounts?access_token={long-lived-token}"
```
Copy the `id` field — that's `META_PAGE_ID`.

6. Get your Instagram Business Account ID:
```bash
curl -i -X GET "https://graph.facebook.com/v21.0/{page-id}?fields=instagram_business_account&access_token={long-lived-token}"
```
That's `META_IG_BUSINESS_ID`.

7. Save the long-lived token as `META_PAGE_ACCESS_TOKEN`.

**Note:** the token expires in ~60 days. When posts start failing, come back and redo steps 3–4. (A future upgrade — a Meta "System User" token — never expires, but isn't needed to get started.)

---

## 3. Get a Gemini API key

https://aistudio.google.com/apikey → sign in → **Create API Key**. This is `GEMINI_API_KEY`.

---

## 4. Get an Anthropic API key

This system calls Claude directly (not through the Claude Code app) to generate ideas, captions and hooks on a schedule, so it needs its own API key:
https://console.anthropic.com/settings/keys → **Create Key**. This is `ANTHROPIC_API_KEY`.

---

## 5. Create your Telegram bot (this is how you'll approve posts from your phone)

1. Open Telegram, search for **@BotFather**, start a chat.
2. Send `/newbot`, give it a name and a username (must end in `bot`, e.g. `OdiaOTTContentBot`).
3. BotFather replies with a token like `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` — this is `TELEGRAM_BOT_TOKEN`.
4. Send your new bot any message (e.g. "hi") so it knows about you.
5. Get your chat ID by visiting this URL in a browser (replace the token):
   `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates`
   Look for `"chat":{"id":123456789,...}` — that number is `TELEGRAM_CHAT_ID`.

---

## 6. Add all secrets to GitHub

Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**, and add each of these one at a time:

- `ANTHROPIC_API_KEY`
- `GEMINI_API_KEY`
- `META_PAGE_ACCESS_TOKEN`
- `META_PAGE_ID`
- `META_IG_BUSINESS_ID`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

These never touch the repo's code — GitHub injects them only while a workflow is running.

---

## 7. Turn on Actions and seed the system

1. Repo → **Actions** tab → if prompted, click "I understand my workflows, go ahead and enable them."
2. Find **"One-time Seed (initial ideas + calendar)"** in the left sidebar → **Run workflow** → Run.
   (You can do this from GitHub's mobile app too — no PC needed.)
3. Wait ~1–2 minutes, then check the repo's `data/ideas/` and `data/calendar/` folders — you should see fresh JSON files, committed automatically by the bot.

---

## 8. Test the daily pipeline manually

Repo → Actions → **"Daily Content Pipeline"** → Run workflow. Within a couple minutes you should get a Telegram message from your bot with a draft caption (and an image, if the pillar called for one) plus instructions like:

```
approve 20260904091500
reject 20260904091500
revise 20260904091500: <what to change>
```

Reply directly in that Telegram chat. Nothing posts until you send `approve <id>`. The bot checks for your reply every ~10 minutes (via the "Poll Telegram Approvals" workflow, which is already scheduled).

- `revise <id>: make the hook punchier` → regenerates the caption with your note and resends it to you for approval again — repeat as many times as you want.
- `reject <id>` → discards it, nothing is posted.

---

## 9. Send your own poster/photo for a post

Just send the bot a **photo** on Telegram, with a caption describing the context, e.g.:

> "This is the poster for our new thriller. Focus on the color grading contrast between the two halves."

By default it becomes an Instagram post under **The Craft** pillar. To override, add tags anywhere in the caption:
- `platform:facebook`
- `pillar:industry`

Within ~10 minutes (next poll cycle) you'll get the drafted caption back for approval, same as above.

---

## 10. Ongoing schedule (already wired up, nothing more to do)

- **Daily** (~9 AM IST): drafts and sends one post for approval.
- **Every ~10 min**: checks Telegram for your approve/reject/revise replies.
- **Weekly** (Sunday): Performance Analyst reviews the week by pillar+platform.
- **Monthly** (1st): Growth Director reviews the month, checks persona drift, rebuilds the 30-day plan.

## Troubleshooting

- **No Telegram message ever arrives**: check the workflow's logs (Actions tab → click the run) for the actual error — usually a missing/misnamed secret.
- **Posts stop going out after ~2 months**: your Meta token expired — redo section 2, steps 3–4, and update the `META_PAGE_ACCESS_TOKEN` secret.
- **GitHub disables scheduled workflows after 60 days of repo inactivity**: shouldn't happen here since the daily workflow commits every day, but if you ever see workflows silently stop, go to Actions → the workflow → re-enable it.
- **Gemini image generation fails**: Google renames/retires image models occasionally. Check https://ai.google.dev/gemini-api/docs/image-generation for the current model id and update the `GEMINI_IMAGE_MODEL` secret/env var (add it as a secret if you need to override the default in `lib/gemini_api.py`).
