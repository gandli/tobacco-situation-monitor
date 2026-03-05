"""HTTP fetcher for list pages and article pages."""

from typing import Optional


def fetch(url: str, timeout: float = 10.0) -> str:
    """Fetch HTML content from a URL.

    Args:
        url: The URL to fetch.
        timeout: Request timeout in seconds.

    Returns:
        HTML content as string.

    Raises:
        httpx.HTTPError: If the request fails.
    """
    import httpx

    response = httpx.get(url, timeout=timeout, follow_redirects=True)
    response.raise_for_status()
    return response.text