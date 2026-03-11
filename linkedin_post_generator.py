"""
LinkedIn post generator using Claude claude-opus-4-6.
Takes a YouTube video transcript and generates a LinkedIn post
that matches the speaker's tone of voice.
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
        A LinkedIn post as a string, matching the speaker's tone.
    """
    client = anthropic.Anthropic()

    system_prompt = """You are an expert at transforming YouTube video transcripts into
compelling LinkedIn posts. Your task is to:

1. Carefully analyze the speaker's tone, vocabulary, and communication style from the transcript
2. Identify the key insights, takeaways, and most compelling points
3. Write a LinkedIn post that sounds authentically like the speaker — not a summary, but
   a post that captures their personality, energy, and unique way of expressing ideas
4. Structure the post for LinkedIn's format: engaging hook, valuable content, clear CTA
5. Use the speaker's own phrases and expressions where natural
6. Keep it between 150-300 words — punchy and shareable
7. End with a question or call-to-action that invites engagement
8. Do NOT use excessive emojis — match the speaker's actual style
9. Do NOT include hashtags unless the speaker's style clearly calls for them

Output ONLY the LinkedIn post text, nothing else."""

    user_message = f"""Here is a YouTube video transcript to transform into a LinkedIn post.

Video title: {video_title}
Video URL: {video_url}

Full transcript:
{transcript}

Write a LinkedIn post in the speaker's authentic tone of voice based on this transcript."""

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
