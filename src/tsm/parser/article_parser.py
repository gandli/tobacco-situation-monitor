"""Parse article detail pages."""

from dataclasses import dataclass


@dataclass
class Article:
    """Parsed article data."""

    title: str
    published_at: str
    content_clean: str


def parse_article(html: str) -> Article:
    """Parse article title, date, and content from HTML.

    Args:
        html: HTML content of an article detail page.

    Returns:
        Article with title, published_at, and cleaned content.
    """
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    # Extract title from h1
    title = ""
    h1 = soup.find("h1")
    if h1:
        title = h1.get_text(strip=True)

    # Extract published date from time element
    published_at = ""
    time_elem = soup.find("time")
    if time_elem:
        published_at = time_elem.get_text(strip=True)

    # Extract content from div with id='content'
    content_clean = ""
    content_div = soup.find("div", id="content")
    if content_div:
        content_clean = content_div.get_text(strip=True)

    return Article(title=title, published_at=published_at, content_clean=content_clean)