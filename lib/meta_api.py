import os
import time
import requests

GRAPH = "https://graph.facebook.com/v21.0"


def _headers():
    return {"Authorization": f"Bearer {os.environ['META_PAGE_ACCESS_TOKEN']}"}


def _raise_with_body(resp):
    """requests' default raise_for_status() only reports the status code and
    URL, not Facebook's actual error message — which is the only useful part
    for diagnosing a failure. This attaches it, and never includes the token
    (it's in a header now, never in the URL)."""
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("error", {}).get("message", resp.text)
        except ValueError:
            detail = resp.text
        raise requests.exceptions.HTTPError(f"{resp.status_code} error from Meta API: {detail}", response=resp)


def get_page_insights(metrics="page_impressions,page_engaged_users", period="week"):
    page_id = os.environ["META_PAGE_ID"]
    r = requests.get(f"{GRAPH}/{page_id}/insights",
                      params={"metric": metrics, "period": period},
                      headers=_headers(), timeout=30)
    _raise_with_body(r)
    return r.json()


def get_ig_insights(metrics="reach,profile_views", period="week"):
    ig_id = os.environ["META_IG_BUSINESS_ID"]
    r = requests.get(f"{GRAPH}/{ig_id}/insights",
                      params={"metric": metrics, "period": period},
                      headers=_headers(), timeout=30)
    _raise_with_body(r)
    return r.json()


def post_to_facebook(caption: str) -> str:
    page_id = os.environ["META_PAGE_ID"]
    r = requests.post(f"{GRAPH}/{page_id}/feed",
                       params={"message": caption},
                       headers=_headers(), timeout=30)
    _raise_with_body(r)
    return r.json()["id"]


def post_to_instagram(image_url: str, caption: str) -> str:
    ig_id = os.environ["META_IG_BUSINESS_ID"]
    r = requests.post(f"{GRAPH}/{ig_id}/media",
                       params={"image_url": image_url, "caption": caption},
                       headers=_headers(), timeout=60)
    _raise_with_body(r)
    creation_id = r.json()["id"]

    # Instagram processes the container asynchronously — publishing before it's
    # FINISHED fails with "Media ID is not available." Poll status first.
    for _ in range(10):
        status_r = requests.get(f"{GRAPH}/{creation_id}",
                                 params={"fields": "status_code"},
                                 headers=_headers(), timeout=30)
        _raise_with_body(status_r)
        status = status_r.json().get("status_code")
        if status == "FINISHED":
            break
        if status == "ERROR":
            raise RuntimeError(f"Instagram media container {creation_id} failed processing (status ERROR).")
        time.sleep(3)
    else:
        raise RuntimeError(f"Instagram media container {creation_id} never finished processing in time.")

    r2 = requests.post(f"{GRAPH}/{ig_id}/media_publish",
                        params={"creation_id": creation_id},
                        headers=_headers(), timeout=60)
    _raise_with_body(r2)
    return r2.json()["id"]


def check_token_days_left():
    r = requests.get(f"{GRAPH}/debug_token",
                      params={"input_token": os.environ["META_PAGE_ACCESS_TOKEN"]},
                      headers=_headers(), timeout=30)
    _raise_with_body(r)
    data = r.json().get("data", {})
    expires_at = data.get("expires_at")
    if not expires_at:
        return None
    return (expires_at - time.time()) / 86400
