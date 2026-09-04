"""Runs on a ~10 minute cron via GitHub Actions. Checks Telegram for your replies
and acts on them:
  approve <id>          -> publishes the pending draft live
  reject <id>           -> discards it
  revise <id>: <notes>  -> rewrites the draft with your feedback, resends for approval
Also handles you sending a photo (a poster/still) with a caption: that's treated as
a brand-new "quick post" request — no calendar slot needed. Add "platform:facebook"
or "pillar:industry" etc. anywhere in the caption to override the defaults
(platform:instagram, pillar:craft)."""
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage, telegram_api
from agents import publisher_agent, copywriting_agent

APPROVE_RE = re.compile(r"^\s*approve\s+(\S+)", re.IGNORECASE)
REJECT_RE = re.compile(r"^\s*reject\s+(\S+)", re.IGNORECASE)
REVISE_RE = re.compile(r"^\s*revise\s+(\S+)\s*:\s*(.+)", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"(platform|pillar)\s*:\s*(\w+)", re.IGNORECASE)


def _load_pending(draft_id):
    return storage.read_json("pending_approval", f"{draft_id}.json", default=None)


def _save_pending(pending):
    storage.write_json(pending, "pending_approval", f"{pending['id']}.json")


def _handle_text(text: str):
    m = APPROVE_RE.match(text)
    if m:
        pending = _load_pending(m.group(1))
        if not pending:
            telegram_api.send_message(f"No pending draft with id {m.group(1)}.")
            return
        try:
            post_id = publisher_agent.publish_approved(pending)
            pending["status"] = "published"
            _save_pending(pending)
            telegram_api.send_message(f"Published {pending['id']} to {pending['platform']} (post id {post_id}).")
        except Exception as e:
            telegram_api.send_message(f"Publish failed for {pending['id']}: {e}")
        return

    m = REJECT_RE.match(text)
    if m:
        pending = _load_pending(m.group(1))
        if pending:
            pending["status"] = "rejected"
            _save_pending(pending)
            telegram_api.send_message(f"Rejected {pending['id']}.")
        return

    m = REVISE_RE.match(text)
    if m:
        draft_id, feedback = m.group(1), m.group(2).strip()
        pending = _load_pending(draft_id)
        if not pending:
            telegram_api.send_message(f"No pending draft with id {draft_id}.")
            return
        new_caption = copywriting_agent.revise(pending["caption"], feedback)
        pending["caption"] = new_caption
        publisher_agent.resend_for_approval(pending, feedback)
        return


def _handle_photo(message: dict):
    photos = message.get("photo", [])
    if not photos:
        return
    caption = message.get("caption", "") or ""

    platform, pillar = "instagram", "Craft"
    for key, value in TAG_RE.findall(caption):
        if key.lower() == "platform":
            platform = value.lower()
        elif key.lower() == "pillar":
            pillar = value.capitalize()
    context_text = TAG_RE.sub("", caption).strip() or "No extra context given — infer from the image."

    file_id = photos[-1]["file_id"]
    draft_id = storage.new_id()
    image_rel = f"data/images/user_supplied/{draft_id}.jpg"
    telegram_api.download_file(file_id, os.path.join(storage.BASE, image_rel))

    new_caption = copywriting_agent.write_from_image_context(context_text, pillar, platform)
    publisher_agent.prepare_for_approval(
        new_caption, platform, pillar, image_rel_path=image_rel,
        source="quick_post", topic=context_text, draft_id=draft_id,
    )


def poll():
    storage.ensure_dirs()
    state = storage.read_json("telegram_state", "offset.json", default={"offset": None})
    updates = telegram_api.get_updates(offset=state["offset"])

    for update in updates:
        message = update.get("message") or update.get("edited_message")
        if message:
            if "photo" in message:
                _handle_photo(message)
            elif "text" in message:
                _handle_text(message["text"])
        state["offset"] = update["update_id"] + 1

    storage.write_json(state, "telegram_state", "offset.json")


if __name__ == "__main__":
    poll()
