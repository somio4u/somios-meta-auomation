"""Agent 7 — Publisher Agent. NEVER publishes directly. It prepares the final
post and sends it to you on Telegram for approval. Actual publishing only
happens from inbox_agent.py, after you reply "approve <id>" on Telegram."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from lib import storage, telegram_api, meta_api, image_host


def prepare_for_approval(caption: str, platform: str, pillar: str, image_rel_path: str = None,
                          source: str = "calendar", topic: str = "", draft_id: str = None) -> str:
    draft_id = draft_id or storage.new_id()
    pending = {
        "id": draft_id,
        "status": "pending",
        "platform": platform,
        "pillar": pillar,
        "topic": topic,
        "source": source,
        "caption": caption,
        "image_path": image_rel_path,
        "history": [{"caption": caption, "note": "initial"}],
        "created_at": storage.today_str(),
    }
    storage.write_json(pending, "pending_approval", f"{draft_id}.json")
    _notify(pending)
    return draft_id


def resend_for_approval(pending: dict, feedback: str):
    pending["history"].append({"caption": pending["caption"], "note": f"revised: {feedback}"})
    storage.write_json(pending, "pending_approval", f"{pending['id']}.json")
    _notify(pending)


def _notify(pending: dict):
    instructions = (
        f"\n\n---\nID: {pending['id']} | {pending['platform']} | {pending['pillar']}\n"
        f"Reply with one of:\n"
        f"approve {pending['id']}\n"
        f"reject {pending['id']}\n"
        f"revise {pending['id']}: <what to change>"
    )
    text = pending["caption"] + instructions
    if pending.get("image_path"):
        abs_path = os.path.join(storage.BASE, pending["image_path"])
        telegram_api.send_photo(abs_path, text)
    else:
        telegram_api.send_message(text)


def publish_approved(pending: dict) -> str:
    if pending["platform"] == "facebook":
        post_id = meta_api.post_to_facebook(pending["caption"])
    elif pending["platform"] == "instagram":
        if not pending.get("image_path"):
            raise ValueError("Instagram posts require an image.")
        abs_path = os.path.join(storage.BASE, pending["image_path"])
        image_url = image_host.upload_image(abs_path)
        post_id = meta_api.post_to_instagram(image_url, pending["caption"])
    else:
        raise ValueError(f"Unknown platform: {pending['platform']}")

    log_line = (f"- {storage.today_str()} | {pending['platform']} | {pending['pillar']} | "
                f"post_id={post_id} | draft_id={pending['id']}")
    storage.append_markdown(log_line, "reports", f"publish_log_{storage.today_str()[:7]}.md")
    return post_id
