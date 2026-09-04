import os
import json
import requests

_API = "https://api.telegram.org/bot{token}/{method}"


def _token():
    return os.environ["TELEGRAM_BOT_TOKEN"]


def _chat_id():
    return os.environ["TELEGRAM_CHAT_ID"]


def approve_reject_keyboard(draft_id: str) -> dict:
    return {
        "inline_keyboard": [[
            {"text": "Approve", "callback_data": f"approve:{draft_id}"},
            {"text": "Reject", "callback_data": f"reject:{draft_id}"},
        ]]
    }


def send_message(text: str, reply_markup: dict = None) -> dict:
    url = _API.format(token=_token(), method="sendMessage")
    data = {"chat_id": _chat_id(), "text": text}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    return r.json()


def send_photo(photo_path_or_url: str, caption: str, reply_markup: dict = None) -> dict:
    url = _API.format(token=_token(), method="sendPhoto")
    caption = caption[:1024]  # Telegram caption limit
    data = {"chat_id": _chat_id(), "caption": caption}
    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)
    if photo_path_or_url.startswith("http"):
        data["photo"] = photo_path_or_url
        r = requests.post(url, data=data, timeout=60)
    else:
        with open(photo_path_or_url, "rb") as f:
            r = requests.post(url, data=data, files={"photo": f}, timeout=60)
    r.raise_for_status()
    return r.json()


def answer_callback_query(callback_query_id: str, text: str = None):
    url = _API.format(token=_token(), method="answerCallbackQuery")
    data = {"callback_query_id": callback_query_id}
    if text:
        data["text"] = text
    r = requests.post(url, data=data, timeout=30)
    r.raise_for_status()
    return r.json()


def get_updates(offset=None):
    url = _API.format(token=_token(), method="getUpdates")
    params = {"timeout": 0}
    if offset is not None:
        params["offset"] = offset
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("result", [])


def download_file(file_id: str, out_path: str) -> str:
    url = _API.format(token=_token(), method="getFile")
    r = requests.get(url, params={"file_id": file_id}, timeout=30)
    r.raise_for_status()
    file_path = r.json()["result"]["file_path"]
    file_url = f"https://api.telegram.org/file/bot{_token()}/{file_path}"
    resp = requests.get(file_url, timeout=60)
    resp.raise_for_status()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(resp.content)
    return out_path
