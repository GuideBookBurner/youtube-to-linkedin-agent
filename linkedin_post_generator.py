"""
LinkedIn post generator using Claude claude-opus-4-6.
Takes a YouTube video transcript and generates a LinkedIn post
written as an SEO professional sharing insights with their network.
"""

import anthropic


def generate_linkedin_post(transcript: str, video_title: str, video_url: str) -> str:
    """
    Generate a LinkedIn post from a YouTube transcript using Claude claude-opus-4-6.

    Args:
        transcript: The full transcript text from the YouTube video.
        video_title: The title of the YouTube video.
        video_url: The URL of the YouTube video.

    Returns:
        A LinkedIn post as a string, written as an SEO professional sharing insights.
    """
    client = anthropic.Anthropic()

    system_prompt = """You are a knowledgeable SEO professional sharing the latest insights and tips with your LinkedIn network. You have just watched a YouTube video and are posting about what you learned.

Your task is to write a LinkedIn post that:

1. Reads like a genuine SEO news update or insight share, not a video summary
2. Positions you (the poster) as a thoughtful SEO professional commenting on what's happening in the SEO world
3. Pulls out the most actionable tips, strategy shifts, or news-worthy points from the transcript
4. Opens with a strong, specific hook tied to the SEO insight, not a reference to the video
5. Flows in a conversational but professional tone, like sharing a useful update with colleagues
6. Keeps it between 150-300 words, punchy and easy to scan
7. Ends with a question or observation that invites colleagues to weigh in
8. Uses plain dashes (-) if a dash is needed, never em dashes
9. Does not use excessive emojis
10. Does not include hashtags

Output ONLY the LinkedIn post text, nothing else."""

    user_message = f"""Here is a YouTube video transcript about SEO. Write a LinkedIn post sharing the key insights as an SEO professional commenting on the topic.

Video title: {video_title}
Video URL: {video_url}

Full transcript:
{transcript}

Write the LinkedIn post as an SEO professional sharing useful insights with your network."""

    print("Generating LinkedIn post with Claude claude-opus-4-6...")

    full_response = ""
    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for text in stream.text_stream:
            print(text, end="", flush=True)
            full_response += text

    print()  # newline after streaming
    return full_response
