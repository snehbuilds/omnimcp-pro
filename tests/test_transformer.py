"""Tests for ContentTransformer."""

from src.core.transformer import ContentTransformer


def test_transform_linkedin_link_stripping():
    raw_text = (
        "Check out our new open-source protocol gateway!\n\n"
        "Read the full docs here: https://github.com/example/omnimcp\n"
        "And test the playground: https://demo.omnimcp.pro"
    )
    result = ContentTransformer.transform_linkedin(raw_text)

    # External links must be extracted to first_comment to protect reach
    assert "https://github.com" not in result.body
    assert "https://demo.omnimcp.pro" not in result.body
    assert result.first_comment is not None
    assert "https://github.com/example/omnimcp" in result.first_comment
    assert "https://demo.omnimcp.pro" in result.first_comment
    assert len(result.warnings) > 0


def test_transform_linkedin_char_limit():
    long_text = "A" * 3500
    result = ContentTransformer.transform_linkedin(long_text)
    assert len(result.body) <= 3000
    assert result.body.endswith("...")


def test_transform_twitter_single_tweet():
    short_text = "OmniMCP Pro: sub-500ms protocol-native social publishing."
    result = ContentTransformer.transform_twitter(short_text)
    assert result.character_count <= 280
    assert len(result.thread_items) == 1
    assert result.body == short_text


def test_transform_twitter_thread_chunking():
    paragraphs = [
        "First point about agentic architecture that needs detailed explanation.",
        "Second point about Model Context Protocol standards and why JSON-RPC over stdio requires zero stdout pollution.",
        "Third point regarding anti-ban security guards: 180s cooldown, daily ceilings, and randomized human jitter delays.",
        "Fourth point detailing reach velocity metrics and why engagement velocity ratio matters more than vanity impressions.",
    ]
    long_text = "\n\n".join(paragraphs)
    result = ContentTransformer.transform_twitter(long_text)

    assert len(result.thread_items) > 1
    for idx, tweet in enumerate(result.thread_items, 1):
        assert len(tweet) <= 280
        assert f"({idx}/" in tweet


def test_transform_wordpress_markdown_to_html():
    markdown_text = (
        "# Protocol-Native Publishing\n\n"
        "Here is a code block:\n\n"
        "```python\n"
        "print('Hello OmniMCP')\n"
        "```\n\n"
        "> A quote about autonomous systems."
    )
    result = ContentTransformer.transform_wordpress(markdown_text, title="Architecture Guide")
    assert result.html_body is not None
    assert "<h1>Protocol-Native Publishing</h1>" in result.html_body
    assert "<code" in result.html_body
    assert "<blockquote>" in result.html_body
