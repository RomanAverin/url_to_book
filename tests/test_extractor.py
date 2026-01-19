import pytest
from lxml import html

from url_to_pdf.extractor import ContentBlock, _clean_html, _extract_content_blocks


class TestCleanHtml:
    def test_plain_text(self):
        element = html.fromstring("<p>Simple text</p>")
        result = _clean_html(element)
        assert result == "Simple text"

    def test_bold_tag(self):
        element = html.fromstring("<p>Text with <b>bold</b> word</p>")
        result = _clean_html(element)
        assert result == "Text with <b>bold</b> word"

    def test_strong_to_bold(self):
        element = html.fromstring("<p>Text with <strong>strong</strong> word</p>")
        result = _clean_html(element)
        assert result == "Text with <b>strong</b> word"

    def test_italic_tag(self):
        element = html.fromstring("<p>Text with <i>italic</i> word</p>")
        result = _clean_html(element)
        assert result == "Text with <i>italic</i> word"

    def test_em_to_italic(self):
        element = html.fromstring("<p>Text with <em>emphasis</em> word</p>")
        result = _clean_html(element)
        assert result == "Text with <i>emphasis</i> word"

    def test_link_preserved(self):
        element = html.fromstring('<p>Check <a href="https://example.com">this link</a></p>')
        result = _clean_html(element, "https://base.com")
        assert '<a href="https://example.com">' in result
        assert "this link" in result
        assert "</a>" in result

    def test_link_relative_url(self):
        element = html.fromstring('<p>See <a href="/page">here</a></p>')
        result = _clean_html(element, "https://example.com")
        assert '<a href="https://example.com/page">' in result

    def test_anchor_link_ignored(self):
        element = html.fromstring('<p>Jump to <a href="#section">section</a></p>')
        result = _clean_html(element)
        assert "<a" not in result
        assert "section" in result

    def test_nested_tags(self):
        element = html.fromstring("<p>Text <b>bold and <i>italic</i></b> end</p>")
        result = _clean_html(element)
        assert "<b>" in result
        assert "<i>" in result
        assert "</i>" in result
        assert "</b>" in result


class TestExtractContentBlocks:
    def test_extracts_headings(self):
        doc = html.fromstring("<article><h2>Title</h2><p>Paragraph text here.</p></article>")
        blocks = _extract_content_blocks(doc)

        headings = [b for b in blocks if b.type == "heading"]
        assert len(headings) == 1
        assert headings[0].text == "Title"
        assert headings[0].level == 2

    def test_extracts_paragraphs(self):
        doc = html.fromstring(
            "<article><p>This is a long enough paragraph to pass the filter.</p></article>"
        )
        blocks = _extract_content_blocks(doc)

        paragraphs = [b for b in blocks if b.type == "paragraph"]
        assert len(paragraphs) == 1

    def test_filters_short_paragraphs(self):
        doc = html.fromstring("<article><p>Short</p></article>")
        blocks = _extract_content_blocks(doc)

        paragraphs = [b for b in blocks if b.type == "paragraph"]
        assert len(paragraphs) == 0
