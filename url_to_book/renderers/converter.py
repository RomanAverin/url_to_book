import re
from typing import Optional

from ..extractor import ExtractedArticle
from ..image_handler import DownloadedImage
from .document import (
    Document,
    DocumentMetadata,
    HeadingBlock,
    ImageBlock,
    InlineElement,
    InlineType,
    ParagraphBlock,
)


class ArticleToDocumentConverter:
    """Converts ExtractedArticle to universal Document format."""

    def convert(
        self,
        article: ExtractedArticle,
        images: Optional[list[DownloadedImage]] = None,
    ) -> Document:
        """Convert article to Document.

        Args:
            article: Extracted article data
            images: Optional list of downloaded images

        Returns:
            Document with metadata and content blocks
        """
        metadata = DocumentMetadata(
            title=article.title,
            authors=article.authors,
            source_url=article.source_url,
        )

        blocks = []
        images_to_insert = list(images) if images else []

        # Insert first image at top if available
        if images_to_insert:
            top_img = images_to_insert.pop(0)
            blocks.append(
                ImageBlock(
                    path=top_img.path,
                    url=top_img.original_url,
                    width=top_img.width,
                    height=top_img.height,
                )
            )

        # Calculate image distribution
        content_blocks = article.content if article.content else []
        paragraph_count = sum(1 for b in content_blocks if b.type == "paragraph")
        image_interval = (
            max(1, paragraph_count // (len(images_to_insert) + 1))
            if images_to_insert
            else 0
        )
        paragraph_idx = 0

        # Process content blocks
        for block in content_blocks:
            if block.type == "heading":
                blocks.append(
                    HeadingBlock(
                        level=block.level,
                        content=self._parse_inline(block.html or block.text),
                    )
                )
            else:
                content = block.html if block.html else block.text
                blocks.append(ParagraphBlock(content=self._parse_inline(content)))

                paragraph_idx += 1
                if (
                    images_to_insert
                    and image_interval > 0
                    and paragraph_idx % image_interval == 0
                ):
                    img = images_to_insert.pop(0)
                    blocks.append(
                        ImageBlock(
                            path=img.path,
                            url=img.original_url,
                            width=img.width,
                            height=img.height,
                        )
                    )

        # Append remaining images
        for img in images_to_insert:
            blocks.append(
                ImageBlock(
                    path=img.path,
                    url=img.original_url,
                    width=img.width,
                    height=img.height,
                )
            )

        return Document(metadata=metadata, blocks=blocks)

    def _parse_inline(self, html_text: str) -> list[InlineElement]:
        """Parse HTML text into inline elements.

        Handles <b>, <i>, <u>, and <a href="..."> tags.
        """
        tag_pattern = re.compile(
            r'<(/?)([biu])>|<a href="([^"]+)">|</a>', re.IGNORECASE
        )

        elements: list[InlineElement] = []
        last_end = 0
        bold = False
        italic = False
        link_url: Optional[str] = None

        def get_current_type() -> InlineType:
            if link_url:
                return InlineType.LINK
            if bold:
                return InlineType.BOLD
            if italic:
                return InlineType.ITALIC
            return InlineType.TEXT

        def add_text(text: str):
            if not text:
                return
            current_type = get_current_type()
            elements.append(
                InlineElement(type=current_type, content=text, url=link_url)
            )

        for match in tag_pattern.finditer(html_text):
            # Add text before this tag
            if match.start() > last_end:
                add_text(html_text[last_end : match.start()])

            if match.group(0) == "</a>":
                link_url = None
            elif match.group(3):  # <a href="...">
                link_url = match.group(3)
            elif match.group(1) == "/":  # Closing tag
                tag = match.group(2).lower()
                if tag == "b":
                    bold = False
                elif tag == "i":
                    italic = False
            else:  # Opening tag
                tag = match.group(2).lower()
                if tag == "b":
                    bold = True
                elif tag == "i":
                    italic = True

            last_end = match.end()

        # Add remaining text
        if last_end < len(html_text):
            add_text(html_text[last_end:])

        # If no elements were parsed, treat the whole text as plain text
        if not elements and html_text.strip():
            elements.append(InlineElement(type=InlineType.TEXT, content=html_text))

        return elements
