# Setup Guide — complete beginner walkthrough

This assumes you've never done any of this before. Every step says exactly which
app to open, what to click, and what to type. Nothing goes live to Facebook/Instagram
until you approve it on Telegram — that's built into the code, not something you
configure.

**Apps you'll use in this guide:** your web browser, **PowerShell** (already built
into Windows — I already confirmed it's on your PC), and later, the **Telegram** app
on your phone.

**Already done for you:** I've already run the local, harmless part of Step 1 (`git
init`, adding the files, and the first commit) directly in this folder. You're
picking up from "create the GitHub repository and send the code there" — that part
needs your own GitHub login, which I can't do for you.

---

## STEP 1 — Create the repository on GitHub's website

1. Open your web browser (Chrome, Edge, whatever you normally use).
2. Go to: `https://github.com/new`
   (Log in first if it asks you to.)
3. You'll see a form. Fill it in exactly like this:
   - **Repository name**: type `odia-ott-content-system`
   - **Description**: leave blank, doesn't matter
   - Find the **Private** / **Public** toggle — click **Private** (so your code and any notes stay only visible to you)
   - Scroll down to "Initialize this repository with:" — leave **every checkbox unchecked** (no README, no .gitignore, no license). This matters — if you check any of these, the next steps will get more complicated.
4. Click the green **Create repository** button at the bottom.
5. GitHub now shows you a page titled "Quick setup" with some commands on it. **Ignore that page for now** — leave this browser tab open, you'll come back to copy your repository's web address from it in Step 3.

---

## STEP 2 — Create a GitHub login token (so your PC is allowed to send code)

GitHub no longer accepts your normal password for this — you need a special token instead. It's a one-time setup.

1. In the same browser, go to: `https://github.com/settings/tokens`
2. Click **Generate new token** → choose **Generate new token (classic)**.
3. If asked to confirm your password/2FA, do so.
4. Fill in the form:
   - **Note**: type `odia content system` (just a label so you remember what it's for)
   - **Expiration**: choose `90 days` (or longer if you prefer — you can always make a new one later)
   - Under **Select scopes**, check the box next to **repo** (this checks all the sub-boxes under it automatically — that's fine, leave them all checked)
5. Scroll down, click the green **Generate token** button.
6. GitHub shows you a long string starting with `ghp_...`. **Copy it now** (click the copy icon next to it) and paste it somewhere temporary, like Notepad. **You will not be able to see it again once you leave this page.**

---

## STEP 3 — Open PowerShell and connect this folder to GitHub

1. Click the **Start menu** (Windows icon, bottom-left of your screen).
2. Type `PowerShell`
3. Click on **Windows PowerShell** (blue icon) when it appears in the search results.
4. A dark blue window opens — this is your terminal. Type the following command to go to the project folder, then press **Enter**:

```
cd "C:\Users\user\Documents\odia-ott-content-system"
```

5. Go back to your browser tab from Step 1 (the "Quick setup" page). Find the line that looks like:
   `https://github.com/YOUR-USERNAME/odia-ott-content-system.git`
   Copy that exact URL.

6. Back in PowerShell, type this, but **replace the URL** with the one you just copied:

```
git remote add origin https://github.com/YOUR-USERNAME/odia-ott-content-system.git
```

Press **Enter**. (No visible output means it worked.)

7. Now type this and press **Enter**:

```
git push -u origin main
```

8. A window may pop up asking you to sign in to GitHub — if it's a browser popup, sign in normally. If instead PowerShell asks for a **username** and **password** directly in the terminal:
   - **Username**: your GitHub username
   - **Password**: paste the `ghp_...` token from Step 2 (NOT your real GitHub password — pasting won't show any characters on screen, that's normal for password fields, just paste and press Enter)

9. You should see output ending in something like `Branch 'main' set up to track 'origin/main'.` That means it worked. Refresh your GitHub repository page in the browser — you should now see all the project files there.

**If you get stuck on any message here, copy the exact red/error text from PowerShell and send it to me — I'll tell you exactly what it means.**

---

## STEP 4 — Meta Developer setup (Facebook + Instagram)

**Before you start, make sure:**
- You have a **Facebook Page** for your brand (not your personal profile).
- Your **Instagram account is set to Business or Creator**: open the Instagram app → tap your profile → tap the menu (☰, top-right) → **Settings and privacy** → **Account type and tools** → switch to Business or Creator if it isn't already.
- Instagram is **linked to the Page**: on Facebook, go to your Page → **Settings** → **Linked Accounts** → **Instagram** → connect it.

**Now the developer app:**

1. In your browser, go to `https://developers.facebook.com`
2. Click **My Apps** (top-right) → **Create App**.
3. Choose the app type **Business** → click **Next** → give it a name like `Odia OTT Content System` → click **Create App** (you may need to re-enter your Facebook password).
4. On the app's dashboard (left sidebar), click **Add Product** (or the **+** next to "Add Products to Your App"). Find and add:
   - **Facebook Login**
   - **Instagram Graph API** (search "Instagram" if you don't see it immediately)
5. Go to `https://developers.facebook.com/tools/explorer`
6. Top-right dropdown: select the app you just created.
7. Find the dropdown labeled "User or Page" → select your Facebook Page.
8. Click **Get Token** → **Get User Access Token**. A checklist of permissions appears — check these boxes:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_read_user_content`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_manage_insights`
   - `instagram_content_publish`
9. Click **Generate Access Token**, approve the popup that appears.
10. You now have a token in the box at the top of the page — copy it into Notepad temporarily. This one only lasts ~1 hour, so we immediately trade it for a longer one below.

**Turn it into a 60-day token:**

11. On the app dashboard, click **Settings → Basic** (left sidebar). Copy the **App ID** and **App Secret** (click "Show" for the secret) into Notepad.
12. Back in PowerShell, type this command, replacing the three placeholders with your actual App ID, App Secret, and the short token from step 10:

```
curl "https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_SHORT_TOKEN"
```

13. Press Enter. The response contains `"access_token":"..."` — copy that long value into Notepad and label it **META_PAGE_ACCESS_TOKEN**. This is good for about 60 days.

**Get your two IDs:**

14. In PowerShell, type (replacing the token):

```
curl "https://graph.facebook.com/v21.0/me/accounts?access_token=YOUR_LONG_LIVED_TOKEN"
```

Find `"id": "..."` in the response — copy it and label it **META_PAGE_ID**.

15. Then type (replacing both placeholders):

```
curl "https://graph.facebook.com/v21.0/YOUR_PAGE_ID?fields=instagram_business_account&access_token=YOUR_LONG_LIVED_TOKEN"
```

Find the `"id": "..."` under `instagram_business_account` — copy it and label it **META_IG_BUSINESS_ID**.

You should now have three values in Notepad: `META_PAGE_ACCESS_TOKEN`, `META_PAGE_ID`, `META_IG_BUSINESS_ID`.

**Note:** this token expires in ~60 days — when posts start failing later, come back and redo steps 8–13.

---

## STEP 5 — Get a Gemini API key

This one key powers everything the system generates — ideas, captions, hooks, analysis, and images.

1. In your browser, go to `https://aistudio.google.com/apikey`
2. Sign in with a Google account if asked.
3. Click **Create API Key**.
4. Copy the key shown and label it **GEMINI_API_KEY** in Notepad.

---

## STEP 6 — Create your Telegram bot (this is how you approve posts from your phone)

1. On your phone, open the **Telegram** app.
2. In the search bar at the top, type `BotFather` and tap on the result with the blue checkmark (the official one).
3. Tap **Start** at the bottom.
4. Type `/newbot` and send it.
5. It asks for a name — type anything, e.g. `Odia OTT Content Bot`, send it.
6. It asks for a username — must end in `bot`, e.g. `OdiaOTTContentBot`, send it.
7. BotFather replies with a message containing a token like `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`. Copy this and label it **TELEGRAM_BOT_TOKEN** in Notepad.
8. Now search for the bot username you just created (e.g. `OdiaOTTContentBot`) in Telegram's search bar, open the chat, and send it any message, like `hi`. This step is required — without it, the bot doesn't know who you are yet.
9. On your PC browser, visit this address (replace the token with yours):
   `https://api.telegram.org/bot123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/getUpdates`
10. You'll see text containing `"chat":{"id":123456789,...}` — that number is your **TELEGRAM_CHAT_ID**. Copy it into Notepad.

---

## STEP 7 — Get an imgbb image-hosting key

Instagram's API needs to fetch your generated images from a genuinely public URL. Since your GitHub repo is private, a free image host (imgbb.com) is used instead — it's a one-time signup.

1. Go to `https://api.imgbb.com/`
2. Sign in or create a free account if asked.
3. Copy the API key shown on that page and label it **IMGBB_API_KEY** in Notepad.

---

## STEP 8 — Add all 7 secrets to GitHub

1. In your browser, go to your repository: `https://github.com/YOUR-USERNAME/odia-ott-content-system`
2. Click **Settings** (top menu of the repo, not your account settings).
3. In the left sidebar, click **Secrets and variables** → **Actions**.
4. Click the green **New repository secret** button.
5. Add each of these one at a time (click "New repository secret" again for each one) — **Name** exactly as shown, **Secret** = the value you saved in Notepad:

| Name | Value |
|---|---|
| `GEMINI_API_KEY` | from Step 5 |
| `META_PAGE_ACCESS_TOKEN` | from Step 4.13 |
| `META_PAGE_ID` | from Step 4.14 |
| `META_IG_BUSINESS_ID` | from Step 4.15 |
| `TELEGRAM_BOT_TOKEN` | from Step 6.7 |
| `TELEGRAM_CHAT_ID` | from Step 6.10 |
| `IMGBB_API_KEY` | from Step 7 |

These values never appear in your code — GitHub only injects them while a scheduled run is happening.

---

## STEP 9 — Turn on Actions and generate your first content

1. On your repo page, click the **Actions** tab (top menu).
2. If you see a message about enabling workflows, click **"I understand my workflows, go ahead and enable them"**.
3. In the left sidebar, click **"One-time Seed (initial ideas + calendar)"**.
4. On the right, click the **Run workflow** dropdown button → click the green **Run workflow** button that appears.
5. Wait about 1–2 minutes, then refresh the page — you should see a run with a green checkmark. (You can click into it to see the log if you're curious.)
6. In your repo's file browser, open the `data/ideas/` and `data/calendar/` folders — you should now see JSON files with real content, committed automatically.

---

## STEP 10 — Test the daily pipeline and your first approval

1. Actions tab → click **"Daily Content Pipeline"** in the sidebar → **Run workflow** → **Run workflow**.
2. Within a couple of minutes, check Telegram on your phone — you should get a message from your bot with a draft caption (and sometimes an image) and two buttons underneath: **Approve** and **Reject**.
3. To act on it:
   - **Tap Approve** → it posts live within ~5 minutes. No typing needed.
   - **Tap Reject** → discards it, nothing posted.
   - **Just reply to that message** with what you'd like changed (e.g. "make this shorter") → it rewrites the caption and sends you a new version with fresh buttons — repeat as many times as you like, no need to type an id.

(If you ever need it, typing `approve <id>` / `reject <id>` / `revise <id>: <notes>` still works too — the id is the number shown near the buttons.)

---

## STEP 11 — Send your own poster/photo for a post (optional, whenever you want)

Just send your Telegram bot a **photo**, with a caption describing the context, e.g.:

> "This is the poster for our new thriller. Focus on the color contrast between the two halves."

By default this becomes an Instagram post under the Craft pillar. To change that, add a tag anywhere in the caption:
- `platform:facebook`
- `pillar:industry`

Within ~5 minutes you'll get the drafted caption back on Telegram with the same Approve/Reject buttons and reply-to-revise flow.

---

## From here on, it runs itself

- **Daily** (~9 AM IST): drafts and sends you one post for approval.
- **Every ~5 minutes**: checks Telegram for your reply.
- **Weekly** (Sunday): reviews the week's performance by pillar+platform.
- **Monthly** (1st): full review, checks for persona drift, rebuilds the 30-day plan.

You don't need to keep your PC or the Telegram app open — GitHub runs the schedule, and Telegram delivers the notification whenever your phone next checks in.

## Troubleshooting

- **PowerShell shows a red error you don't understand at any step**: copy the exact text and send it to me.
- **No Telegram message ever arrives**: Actions tab → click the failed/latest run → read the red error line — usually a secret name was typed wrong in Step 8.
- **Posts stop going out after ~2 months**: your Meta token expired — redo Step 4, sections "Now the developer app" through "Turn it into a 60-day token", and update the `META_PAGE_ACCESS_TOKEN` secret in Step 8.
- **Gemini image generation fails**: Google occasionally renames its image models. Check `https://ai.google.dev/gemini-api/docs/image-generation` for the current model id, then add a repository secret named `GEMINI_IMAGE_MODEL` with that id.
- **Gemini text generation fails** (ideas/captions/hooks/reports): similarly, check `https://ai.google.dev/gemini-api/docs/models` for the current model id, then add a repository secret named `GEMINI_TEXT_MODEL` with that id.
- **Instagram publish fails with "Only photo or video can be accepted as media type"**: your `IMGBB_API_KEY` secret is missing or wrong — recheck Step 7/8.
