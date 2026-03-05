"""Extract article links from list pages."""

from urllib.parse import urljoin


def extract_links(html: str, base_url: str) -> list[str]:
    """Extract article links from HTML content.

    Args:
        html: HTML content to parse.
        base_url: Base URL for resolving relative links.

    Returns:
        List of absolute URLs found in href attributes.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        absolute_url = urljoin(base_url, href)
        links.append(absolute_url)
    return links