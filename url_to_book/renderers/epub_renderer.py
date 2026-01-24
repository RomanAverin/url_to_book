import mimetypes
from pathlib import Path
from typing import Optional

from ebooklib import epub

from .base import BaseRenderer, RenderOptions
from .document import (
    Document,
    HeadingBlock,
    HorizontalRuleBlock,
    ImageBlock,
    InlineElement,
    InlineType,
    ParagraphBlock,
)
from .registry import registry


@registry.register
class EPUBRenderer(BaseRenderer):
    """Renders Document to EPUB format."""

    SUPPORTED_FEATURES = {"images", "links"}

    @property
    def format_name(self) -> str:
        return "epub"

    @property
    def file_extension(self) -> str:
        return ".epub"

    def render(  # pylint: disable=too-many-statements
        self, document: Document, output_path: Path, options: Optional[RenderOptions] = None
    ) -> Path:
        """Render document to EPUB file."""
        options = options or RenderOptions()
        output_path = Path(output_path)

        if output_path.suffix.lower() != ".epub":
            output_path = output_path.with_suffix(".epub")

        book = epub.EpubBook()

        # Set metadata
        book.set_identifier("id-" + document.metadata.title[:50].replace(" ", "-"))
        book.set_title(document.metadata.title)
        book.set_language(document.metadata.language or "en")

        for author in document.metadata.authors:
            book.add_author(author)

        if document.metadata.source_url:
            book.add_metadata("DC", "source", document.metadata.source_url)

        # Create main chapter
        chapter = epub.EpubHtml(title=document.metadata.title, file_name="content.xhtml")

        html_parts = ['<html><body>']
        html_parts.append(f"<h1>{self._escape_html(document.metadata.title)}</h1>")

        # Add metadata section
        if document.metadata.authors or document.metadata.source_url:
            html_parts.append('<div class="metadata" style="color: #666; margin-bottom: 20px;">')
            if document.metadata.authors:
                authors_str = ", ".join(document.metadata.authors)
                html_parts.append(f"<p>Authors: {self._escape_html(authors_str)}</p>")
            if document.metadata.source_url:
                html_parts.append(
                    f'<p>Source: <a href="{document.metadata.source_url}">'
                    f"{self._escape_html(document.metadata.source_url)}</a></p>"
                )
            html_parts.append("</div>")

        # Process content blocks
        image_counter = 0
        for block in document.blocks:
            if isinstance(block, HeadingBlock):
                level = min(block.level, 6)
                text = self._render_inline_html(block.content)
                html_parts.append(f"<h{level}>{text}</h{level}>")

            elif isinstance(block, ParagraphBlock):
                text = self._render_inline_html(block.content)
                html_parts.append(f"<p>{text}</p>")

            elif isinstance(block, ImageBlock):
                if options.include_images and block.path and block.path.exists():
                    image_counter += 1
                    image_name = f"image{image_counter}{block.path.suffix}"

                    # Read and embed image
                    mime_type = mimetypes.guess_type(str(block.path))[0] or "image/jpeg"
                    image_content = block.path.read_bytes()

                    epub_image = epub.EpubImage()
                    epub_image.file_name = f"images/{image_name}"
                    epub_image.media_type = mime_type
                    epub_image.content = image_content
                    book.add_item(epub_image)

                    alt = self._escape_html(block.alt)
                    html_parts.append(
                        f'<div class="image"><img src="images/{image_name}" alt="{alt}"/></div>'
                    )

            elif isinstance(block, HorizontalRuleBlock):
                html_parts.append("<hr/>")

        html_parts.append("</body></html>")
        chapter.content = "\n".join(html_parts)

        book.add_item(chapter)

        # Add navigation
        book.toc = [epub.Link("content.xhtml", document.metadata.title, "content")]
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        # Set spine
        book.spine = ["nav", chapter]

        # Add default CSS
        style = """
        body { font-family: serif; margin: 5%; }
        h1, h2, h3, h4, h5, h6 { margin-top: 1em; margin-bottom: 0.5em; }
        p { margin: 0.5em 0; text-align: justify; }
        .metadata { border-bottom: 1px solid #ccc; padding-bottom: 1em; }
        .image { text-align: center; margin: 1em 0; }
        .image img { max-width: 100%; height: auto; }
        a { color: #0066cc; }
        """
        css = epub.EpubItem(
            uid="style", file_name="style.css", media_type="text/css", content=style
        )
        book.add_item(css)
        chapter.add_link(href="style.css", rel="stylesheet", type="text/css")

        # Write EPUB
        output_path.parent.mkdir(parents=True, exist_ok=True)
        epub.write_epub(str(output_path), book, {})

        return output_path

    def _render_inline_html(self, elements: list[InlineElement]) -> str:
        """Render inline elements to HTML."""
        parts = []
        for elem in elements:
            text = self._escape_html(elem.content)
            if elem.type == InlineType.BOLD:
                parts.append(f"<strong>{text}</strong>")
            elif elem.type == InlineType.ITALIC:
                parts.append(f"<em>{text}</em>")
            elif elem.type == InlineType.LINK and elem.url:
                parts.append(f'<a href="{elem.url}">{text}</a>')
            else:
                parts.append(text)
        return "".join(parts)

    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
