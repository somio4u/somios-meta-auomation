import os
import requests

_API = "https://api.telegram.org/bot{token}/{method}"


def _token():
    return os.environ["TELEGRAM_BOT_TOKEN"]


def _chat_id():
    return os.environ["TELEGRAM_CHAT_ID"]


def send_message(text: str) -> dict:
    url = _API.format(token=_token(), method="sendMessage")
    r = requests.post(url, data={"chat_id": _chat_id(), "text": text}, timeout=30)
    r.raise_for_status()
    return r.json()


def send_photo(photo_path_or_url: str, caption: str) -> dict:
    url = _API.format(token=_token(), method="sendPhoto")
    caption = caption[:1024]  # Telegram caption limit
    if photo_path_or_url.startswith("http"):
        r = requests.post(url, data={"chat_id": _chat_id(), "caption": caption,
                                      "photo": photo_path_or_url}, timeout=60)
    else:
        with open(photo_path_or_url, "rb") as f:
            r = requests.post(url, data={"chat_id": _chat_id(), "caption": caption},
                               files={"photo": f}, timeout=60)
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
