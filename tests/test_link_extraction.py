"""Tests for list-page link extraction."""


def test_extract_links_from_list_html():
    """Test extracting article links from list page HTML."""
    from tsm.crawler.extract_links import extract_links

    html = '<a href="/news/123.html">案件通报</a>'
    links = extract_links(html, "https://a.gov.cn/list")
    assert links == ["https://a.gov.cn/news/123.html"]