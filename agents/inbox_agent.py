"""Runs on a ~1 minute cron (external cron-job.org ping, GitHub's own schedule
kept only as a backup). Checks Telegram for your input
and acts on it. Three ways to respond to a draft, from easiest to most manual:
  1. Tap the Approve/Reject button under the message.
  2. Just reply to the message with your feedback — that revises it and
     resends for approval, no typing an id required.
  3. Type "approve <id>" / "reject <id>" / "revise <id>: <notes>" manually.
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


def _find_pending_by_message_id(message_id):
    for fname in storage.list_files("pending_approval"):
        if not fname.endswith(".json"):
            continue
        data = storage.read_json("pending_approval", fname)
        if data and data.get("telegram_message_id") == message_id and data.get("status") == "pending":
            return data
    return None


def _approve(pending):
    if pending.get("status") != "pending":
        return f"{pending['id']} was already {pending.get('status')} — ignoring duplicate approve."
    try:
        post_id = publisher_agent.publish_approved(pending)
        pending["status"] = "published"
        _save_pending(pending)
        return f"Published {pending['id']} to {pending['platform']} (post id {post_id})."
    except Exception as e:
        return f"Publish failed for {pending['id']}: {e}"


def _reject(pending):
    if pending.get("status") != "pending":
        return f"{pending['id']} was already {pending.get('status')}."
    pending["status"] = "rejected"
    _save_pending(pending)
    return f"Rejected {pending['id']}."


def _revise(pending, feedback):
    if pending.get("status") != "pending":
        return f"{pending['id']} was already {pending.get('status')} — ignoring duplicate revise."
    new_caption = copywriting_agent.revise(pending["caption"], feedback)
    pending["caption"] = new_caption
    publisher_agent.resend_for_approval(pending, feedback)
    return None  # resend_for_approval already sends the new draft; no extra message needed


def _ack(callback_query_id: str, text: str = None):
    """Telegram only accepts answerCallbackQuery within a short window of the
    button tap — our poll can run minutes later, so this can legitimately
    fail. It's just the little loading-spinner/toast UI nicety, not required
    for the actual approve/reject to have worked, so never let it crash the run."""
    try:
        telegram_api.answer_callback_query(callback_query_id, text)
    except Exception:
        pass


def _handle_callback(callback_query: dict):
    data = callback_query.get("data", "")
    if ":" not in data:
        return
    action, draft_id = data.split(":", 1)
    pending = _load_pending(draft_id)
    if not pending:
        _ack(callback_query["id"], "Draft not found.")
        return

    if action == "approve":
        result = _approve(pending)
    elif action == "reject":
        result = _reject(pending)
    else:
        return

    _ack(callback_query["id"], result[:200])
    telegram_api.send_message(result)


def _handle_text(text: str):
    m = APPROVE_RE.match(text)
    if m:
        pending = _load_pending(m.group(1))
        if not pending:
            telegram_api.send_message(f"No pending draft with id {m.group(1)}.")
            return
        telegram_api.send_message(_approve(pending))
        return

    m = REJECT_RE.match(text)
    if m:
        pending = _load_pending(m.group(1))
        if not pending:
            telegram_api.send_message(f"No pending draft with id {m.group(1)}.")
            return
        telegram_api.send_message(_reject(pending))
        return

    m = REVISE_RE.match(text)
    if m:
        draft_id, feedback = m.group(1), m.group(2).strip()
        pending = _load_pending(draft_id)
        if not pending:
            telegram_api.send_message(f"No pending draft with id {draft_id}.")
            return
        result = _revise(pending, feedback)
        if result:
            telegram_api.send_message(result)
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


def _handle_message(message: dict):
    if "photo" in message:
        _handle_photo(message)
        return

    text = message.get("text")
    if not text:
        return

    reply_to = message.get("reply_to_message")
    is_explicit_command = APPROVE_RE.match(text) or REJECT_RE.match(text) or REVISE_RE.match(text)
    if reply_to and not is_explicit_command:
        pending = _find_pending_by_message_id(reply_to.get("message_id"))
        if pending:
            result = _revise(pending, text.strip())
            if result:
                telegram_api.send_message(result)
            return

    _handle_text(text)


def poll():
    storage.ensure_dirs()
    state = storage.read_json("telegram_state", "offset.json", default={"offset": None})
    updates = telegram_api.get_updates(offset=state["offset"])

    for update in updates:
        try:
            if "callback_query" in update:
                _handle_callback(update["callback_query"])
            else:
                message = update.get("message") or update.get("edited_message")
                if message:
                    _handle_message(message)
        except Exception as e:
            # Never let one bad update block/retry-loop the rest of the queue —
            # advance past it regardless and log what happened.
            print(f"inbox_agent: failed to handle update {update.get('update_id')}: {e}")
        finally:
            state["offset"] = update["update_id"] + 1
            storage.write_json(state, "telegram_state", "offset.json")


if __name__ == "__main__":
    poll()
