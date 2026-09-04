import os
import time
import requests

GRAPH = "https://graph.facebook.com/v21.0"


def _token():
    return os.environ["META_PAGE_ACCESS_TOKEN"]


def get_page_insights(metrics="page_impressions,page_engaged_users", period="week"):
    page_id = os.environ["META_PAGE_ID"]
    r = requests.get(f"{GRAPH}/{page_id}/insights",
                      params={"metric": metrics, "period": period, "access_token": _token()},
                      timeout=30)
    r.raise_for_status()
    return r.json()


def get_ig_insights(metrics="reach,profile_views", period="week"):
    ig_id = os.environ["META_IG_BUSINESS_ID"]
    r = requests.get(f"{GRAPH}/{ig_id}/insights",
                      params={"metric": metrics, "period": period, "access_token": _token()},
                      timeout=30)
    r.raise_for_status()
    return r.json()


def post_to_facebook(caption: str) -> str:
    page_id = os.environ["META_PAGE_ID"]
    r = requests.post(f"{GRAPH}/{page_id}/feed",
                       params={"message": caption, "access_token": _token()},
                       timeout=30)
    r.raise_for_status()
    return r.json()["id"]


def post_to_instagram(image_url: str, caption: str) -> str:
    ig_id = os.environ["META_IG_BUSINESS_ID"]
    r = requests.post(f"{GRAPH}/{ig_id}/media",
                       params={"image_url": image_url, "caption": caption, "access_token": _token()},
                       timeout=60)
    r.raise_for_status()
    creation_id = r.json()["id"]

    r2 = requests.post(f"{GRAPH}/{ig_id}/media_publish",
                        params={"creation_id": creation_id, "access_token": _token()},
                        timeout=60)
    r2.raise_for_status()
    return r2.json()["id"]


def check_token_days_left():
    r = requests.get(f"{GRAPH}/debug_token",
                      params={"input_token": _token(), "access_token": _token()},
                      timeout=30)
    r.raise_for_status()
    data = r.json().get("data", {})
    expires_at = data.get("expires_at")
    if not expires_at:
        return None
    return (expires_at - time.time()) / 86400
