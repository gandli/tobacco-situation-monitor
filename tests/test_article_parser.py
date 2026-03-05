"""Test article parsing from detail pages."""

import pytest

from tsm.parser.article_parser import Article, parse_article


def test_parse_article_fields():
    """Parse article title, date, and content from HTML."""
    html = "<h1>某地查获假烟案</h1><time>2026-03-01</time><div id='content'>正文</div>"
    article = parse_article(html)
    assert article.title == "某地查获假烟案"
    assert "正文" in article.content_clean