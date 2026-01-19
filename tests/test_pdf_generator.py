import pytest


class TestWriteFormattedTextParsing:
    def test_parse_bold_tags(self):
        import re

        html_text = "Text <b>bold</b> normal"
        tag_pattern = re.compile(r'<(/?)([biu])>|<a href="([^"]+)">|</a>', re.IGNORECASE)

        parts = []
        last_end = 0
        for match in tag_pattern.finditer(html_text):
            if match.start() > last_end:
                parts.append(("text", html_text[last_end:match.start()]))

            if match.group(0) == "</a>":
                parts.append(("end_link", None))
            elif match.group(3):
                parts.append(("start_link", match.group(3)))
            elif match.group(1) == "/":
                parts.append(("end_" + match.group(2).lower(), None))
            else:
                parts.append(("start_" + match.group(2).lower(), None))

            last_end = match.end()

        if last_end < len(html_text):
            parts.append(("text", html_text[last_end:]))

        assert parts == [
            ("text", "Text "),
            ("start_b", None),
            ("text", "bold"),
            ("end_b", None),
            ("text", " normal"),
        ]

    def test_parse_link_tags(self):
        import re

        html_text = 'Visit <a href="https://example.com">site</a> now'
        tag_pattern = re.compile(r'<(/?)([biu])>|<a href="([^"]+)">|</a>', re.IGNORECASE)

        parts = []
        last_end = 0
        for match in tag_pattern.finditer(html_text):
            if match.start() > last_end:
                parts.append(("text", html_text[last_end:match.start()]))

            if match.group(0) == "</a>":
                parts.append(("end_link", None))
            elif match.group(3):
                parts.append(("start_link", match.group(3)))
            elif match.group(1) == "/":
                parts.append(("end_" + match.group(2).lower(), None))
            else:
                parts.append(("start_" + match.group(2).lower(), None))

            last_end = match.end()

        if last_end < len(html_text):
            parts.append(("text", html_text[last_end:]))

        assert parts == [
            ("text", "Visit "),
            ("start_link", "https://example.com"),
            ("text", "site"),
            ("end_link", None),
            ("text", " now"),
        ]

    def test_parse_mixed_formatting(self):
        import re

        html_text = "<b>Bold <i>and italic</i></b>"
        tag_pattern = re.compile(r'<(/?)([biu])>|<a href="([^"]+)">|</a>', re.IGNORECASE)

        parts = []
        last_end = 0
        for match in tag_pattern.finditer(html_text):
            if match.start() > last_end:
                parts.append(("text", html_text[last_end:match.start()]))

            if match.group(0) == "</a>":
                parts.append(("end_link", None))
            elif match.group(3):
                parts.append(("start_link", match.group(3)))
            elif match.group(1) == "/":
                parts.append(("end_" + match.group(2).lower(), None))
            else:
                parts.append(("start_" + match.group(2).lower(), None))

            last_end = match.end()

        if last_end < len(html_text):
            parts.append(("text", html_text[last_end:]))

        assert ("start_b", None) in parts
        assert ("start_i", None) in parts
        assert ("end_i", None) in parts
        assert ("end_b", None) in parts
