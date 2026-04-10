"""Step 7: Publicar en TikTok (Content Posting API) y YouTube (Data API v3)."""
import os

import requests
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from .config import Config


# ── YouTube ───────────────────────────────────────────────────────────────────

def publish_youtube(video_path: str, script: dict, config: Config) -> str:
    """Upload the final video to YouTube and return its public URL.

    Uses an OAuth2 refresh token so no interactive browser flow is needed at
    runtime. Generate the refresh token once with the youtube_auth helper
    (not included here — see Google's OAuth2 documentation).

    Args:
        video_path: Absolute path to the final MP4.
        script:     Script dict produced by step 1 (title, description, hashtags).
        config:     Pipeline configuration.

    Returns:
        Public YouTube watch URL, e.g. "https://www.youtube.com/watch?v=<id>".
    """
    creds = Credentials(
        token=None,
        refresh_token=config.youtube_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=config.youtube_client_id,
        client_secret=config.youtube_client_secret,
    )
    youtube = build("youtube", "v3", credentials=creds)

    hashtag_block = "  ".join(f"#{tag}" for tag in script.get("hashtags", []))
    description = f"{script.get('description', '')}\n\n{hashtag_block}".strip()

    body = {
        "snippet": {
            "title": script["title"][:100],
            "description": description[:5000],
            "tags": script.get("hashtags", []),
            "categoryId": "22",  # People & Blogs
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
        },
    }

    media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _, response = request.next_chunk()

    video_id = response["id"]
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"    YouTube → {url}")
    return url


# ── TikTok ───────────────────────────────────────────────────────────────────

_TIKTOK_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"


def publish_tiktok(video_path: str, script: dict, config: Config) -> str:
    """Upload the final video to TikTok via the Content Posting API v2.

    Flow:
        1. POST to /video/init/ → get publish_id + upload_url.
        2. PUT the raw video bytes to upload_url in a single chunk.

    TikTok processes the upload asynchronously; the publish_id can be used
    with /post/publish/status/fetch/ to poll for the final post URL.

    Args:
        video_path: Absolute path to the final MP4.
        script:     Script dict produced by step 1.
        config:     Pipeline configuration (TikTok access token).

    Returns:
        The publish_id string returned by TikTok.
    """
    headers = {
        "Authorization": f"Bearer {config.tiktok_access_token}",
        "Content-Type": "application/json; charset=UTF-8",
    }

    file_size = os.path.getsize(video_path)

    # 1. Initialise the upload session
    init_payload = {
        "post_info": {
            "title": script["title"][:150],
            "privacy_level": "PUBLIC_TO_EVERYONE",
            "disable_duet": False,
            "disable_comment": False,
            "disable_stitch": False,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": file_size,
            "chunk_size": file_size,
            "total_chunk_count": 1,
        },
    }

    init_resp = requests.post(
        _TIKTOK_INIT_URL, json=init_payload, headers=headers, timeout=30
    )
    init_resp.raise_for_status()
    data = init_resp.json()["data"]
    publish_id: str = data["publish_id"]
    upload_url: str = data["upload_url"]

    # 2. Upload video bytes in a single chunk
    with open(video_path, "rb") as f:
        video_bytes = f.read()

    upload_headers = {
        "Content-Type": "video/mp4",
        "Content-Range": f"bytes 0-{file_size - 1}/{file_size}",
        "Content-Length": str(file_size),
    }
    upload_resp = requests.put(
        upload_url, data=video_bytes, headers=upload_headers, timeout=300
    )
    upload_resp.raise_for_status()

    print(f"    TikTok publish_id → {publish_id}")
    return publish_id
