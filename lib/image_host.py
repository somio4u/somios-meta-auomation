import os
import base64
import requests

IMGBB_UPLOAD_URL = "https://api.imgbb.com/1/upload"


def upload_image(abs_path: str) -> str:
    """Uploads an image to imgbb.com and returns a public URL.

    Instagram's publish API needs to fetch the image over a plain public URL
    with no auth — our GitHub repo is private, so raw.githubusercontent.com
    URLs aren't fetchable by Instagram's servers (they'd get GitHub's
    login-required response instead of the image). imgbb gives a genuinely
    public URL without needing to expose the rest of the repo."""
    api_key = os.environ["IMGBB_API_KEY"]
    with open(abs_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")
    resp = requests.post(IMGBB_UPLOAD_URL, data={"key": api_key, "image": image_b64}, timeout=60)
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("error", {}).get("message", resp.text)
        except ValueError:
            detail = resp.text
        raise requests.exceptions.HTTPError(f"{resp.status_code} error from imgbb: {detail}", response=resp)
    return resp.json()["data"]["url"]
