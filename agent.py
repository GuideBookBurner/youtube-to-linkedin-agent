"""
YouTube → LinkedIn Agent

Scrapes the latest video from a YouTube channel, extracts the transcript,
generates a LinkedIn post in the speaker's tone using Claude, and posts it.

Usage:
    python agent.py                  # full run (scrape → generate → post)
    python agent.py --dry-run        # generate post but don't publish to LinkedIn
    python agent.py --channel <URL>  # override the default channel URL
"""

import argparse
import os
import sys

from dotenv import load_dotenv

from youtube_scraper import scrape_latest_video
from linkedin_post_generator import generate_linkedin_post
from linkedin_poster import LinkedInPoster

# Default channel
DEFAULT_CHANNEL_URL = "https://www.youtube.com/channel/UCXTg_CjVldLQ1RH8jxTTqiw"


def run(channel_url: str, dry_run: bool = False) -> None:
    """
    Main agent pipeline:
      1. Scrape latest YouTube video + transcript
      2. Generate LinkedIn post with Claude
      3. Post to LinkedIn (unless --dry-run)
    """
    # ── Step 1: Scrape ──────────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 1: Scraping latest YouTube video")
    print("=" * 60)
    video = scrape_latest_video(channel_url)
    print(f"\nTitle      : {video['title']}")
    print(f"URL        : {video['url']}")
    print(f"Upload date: {video.get('upload_date', 'N/A')}")
    print(f"Transcript : {len(video['transcript'].split())} words\n")

    # ── Step 2: Generate post ────────────────────────────────────────────────
    print("=" * 60)
    print("STEP 2: Generating LinkedIn post")
    print("=" * 60)
    post_text = generate_linkedin_post(
        transcript=video["transcript"],
        video_title=video["title"],
        video_url=video["url"],
    )

    print("\n" + "=" * 60)
    print("Generated LinkedIn post:")
    print("=" * 60)
    print(post_text)
    print("=" * 60 + "\n")

    # ── Step 3: Publish ──────────────────────────────────────────────────────
    if dry_run:
        print("DRY RUN: skipping LinkedIn publish. Post content shown above.")
        return

    print("STEP 3: Publishing to LinkedIn")
    print("=" * 60)
    poster = LinkedInPoster()
    result = poster.post(post_text)
    post_id = result.get("id", "unknown")
    print(f"Successfully posted to LinkedIn! Post ID: {post_id}")
    print(f"View at: https://www.linkedin.com/feed/update/{post_id}/")


def main() -> None:
    load_dotenv()

    # Validate essential env vars early (only ANTHROPIC_API_KEY is needed for --dry-run)
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY is not set.", file=sys.stderr)
        print("Copy .env.example to .env and fill in your credentials.", file=sys.stderr)
        sys.exit(1)

    parser = argparse.ArgumentParser(description="YouTube → LinkedIn Agent")
    parser.add_argument(
        "--channel",
        default=os.environ.get("YOUTUBE_CHANNEL_URL", DEFAULT_CHANNEL_URL),
        help="YouTube channel URL to scrape (default: env YOUTUBE_CHANNEL_URL or hardcoded default)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate the post but do NOT publish it to LinkedIn",
    )
    args = parser.parse_args()

    run(channel_url=args.channel, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
