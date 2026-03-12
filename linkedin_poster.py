"""
LinkedIn poster module using the LinkedIn API.
Handles OAuth2 authentication and posting to LinkedIn.
"""

import os
import requests


class LinkedInPoster:
    """Posts content to LinkedIn using the LinkedIn REST API."""

    API_BASE = "https://api.linkedin.com/v2"

    def __init__(self):
        self.access_token = os.environ.get("LINKEDIN_ACCESS_TOKEN")
        company_id = os.environ.get("LINKEDIN_COMPANY_ID")

        if not self.access_token:
            raise ValueError(
                "LINKEDIN_ACCESS_TOKEN is not set. "
                "Please provide your LinkedIn OAuth2 access token in the .env file."
            )
        if not company_id:
            raise ValueError(
                "LINKEDIN_COMPANY_ID is not set. "
                "Please provide your LinkedIn Company Page ID in the .env file."
            )

        self.author_urn = f"urn:li:organization:{company_id}"

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }

    def get_profile(self) -> dict:
        """Fetch the authenticated user's LinkedIn profile."""
        response = requests.get(
            f"{self.API_BASE}/me",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def post(self, text: str) -> dict:
        """
        Create a text post on LinkedIn.

        Args:
            text: The post content.

        Returns:
            The LinkedIn API response dict.
        """
        payload = {
            "author": self.author_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": "NONE",
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            },
        }

        response = requests.post(
            f"{self.API_BASE}/ugcPosts",
            headers=self._headers(),
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        return response.json()
