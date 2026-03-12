"""
YouTube scraper module using yt-dlp and youtube-transcript-api.
Fetches the latest video from a channel and retrieves its transcript.
"""

import re

import yt_dlp
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled

# Keywords that indicate a video is about an event, meetup, or conference rather than educational content
_EVENT_KEYWORDS = re.compile(
    r"\b(event|meetup|meet-up|meet up|gathering|conference|summit|seminar|webinar|"
    r"live\s+stream|livestream|workshop|networking|speaker\s+series|panel|expo|"
    r"unconference|hackathon|bootcamp|boot\s+camp)\b",
    re.IGNORECASE,
)


def is_event_video(title: str, description: str = "") -> bool:
    """Return True if the video appears to be about an event rather than educational content."""
    return bool(_EVENT_KEYWORDS.search(title) or _EVENT_KEYWORDS.search(description or ""))


def get_latest_video(channel_url: str) -> dict:
    """
    Fetch metadata for the latest video from a YouTube channel.

    Args:
        channel_url: The YouTube channel URL.

    Returns:
        A dict with video_id, title, description, and url.
    """
    ydl_opts = {
        "quiet": True,
        "extract_flat": True,
        "playlist_items": "1-10",  # Fetch recent videos so we can skip event ones
        "forcejson": True,
    }

    channel_videos_url = f"{channel_url.rstrip('/')}/videos"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(channel_videos_url, download=False)

    if not info or "entries" not in info or not info["entries"]:
        raise ValueError(f"No videos found for channel: {channel_url}")

    for entry in info["entries"]:
        title = entry.get("title", "")
        description = entry.get("description", "")
        if is_event_video(title, description):
            print(f"Skipping event/conference video: '{title}'")
            continue

        video_id = entry.get("id") or entry.get("url", "").split("v=")[-1]
        return {
            "video_id": video_id,
            "title": title,
            "description": description,
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "duration": entry.get("duration"),
            "view_count": entry.get("view_count"),
            "upload_date": entry.get("upload_date"),
        }

    raise ValueError(
        f"No suitable educational videos found in the last 10 uploads for channel: {channel_url}"
    )


def get_transcript(video_id: str, preferred_languages: list[str] | None = None) -> str:
    """
    Retrieve the transcript for a YouTube video.

    Args:
        video_id: The YouTube video ID.
        preferred_languages: Ordered list of language codes to try (defaults to English).

    Returns:
        The full transcript as a single string.
    """
    if preferred_languages is None:
        preferred_languages = ["en", "en-US", "en-GB"]

    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)

        # Try preferred languages first (manually created), then auto-generated
        try:
            transcript = transcript_list.find_manually_created_transcript(preferred_languages)
        except NoTranscriptFound:
            transcript = transcript_list.find_generated_transcript(preferred_languages)

        segments = transcript.fetch()
        full_text = " ".join(seg.text for seg in segments)
        return full_text

    except TranscriptsDisabled:
        raise RuntimeError(f"Transcripts are disabled for video {video_id}.")
    except NoTranscriptFound:
        raise RuntimeError(
            f"No transcript found for video {video_id} in languages: {preferred_languages}"
        )


def scrape_latest_video(channel_url: str) -> dict:
    """
    High-level function: get the latest video and its transcript from a channel.

    Args:
        channel_url: The YouTube channel URL.

    Returns:
        A dict containing video metadata and the full transcript text.
    """
    print(f"Fetching latest video from: {channel_url}")
    video = get_latest_video(channel_url)
    print(f"Found video: '{video['title']}' ({video['url']})")

    print("Fetching transcript...")
    transcript = get_transcript(video["video_id"])
    print(f"Transcript retrieved ({len(transcript.split())} words)")

    return {**video, "transcript": transcript}
