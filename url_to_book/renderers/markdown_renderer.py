import shutil
from pathlib import Path
from typing import Optional

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
class MarkdownRenderer(BaseRenderer):
    """Renders Document to Markdown format with YAML frontmatter."""

    SUPPORTED_FEATURES = {"images", "links"}

    @property
    def format_name(self) -> str:
        return "md"

    @property
    def file_extension(self) -> str:
        return ".md"

    def render(
        self, document: Document, output_path: Path, options: Optional[RenderOptions] = None
    ) -> Path:
        """Render document to Markdown file.

        Images are copied to {output_name}_images/ directory.
        """
        options = options or RenderOptions()
        output_path = Path(output_path)

        # Ensure .md extension
        if output_path.suffix.lower() != ".md":
            output_path = output_path.with_suffix(".md")

        # Create images directory if needed
        images_dir = output_path.parent / f"{output_path.stem}_images"
        if options.include_images:
            images_dir.mkdir(parents=True, exist_ok=True)

        lines: list[str] = []

        # YAML frontmatter
        lines.append("---")
        lines.append(f"title: \"{self._escape_yaml(document.metadata.title)}\"")
        if document.metadata.authors:
            authors_str = ", ".join(document.metadata.authors)
            lines.append(f"authors: \"{self._escape_yaml(authors_str)}\"")
        if document.metadata.source_url:
            lines.append(f"source: \"{document.metadata.source_url}\"")
        if document.metadata.language:
            lines.append(f"language: \"{document.metadata.language}\"")
        lines.append("---")
        lines.append("")

        # Content blocks
        image_counter = 0
        for block in document.blocks:
            if isinstance(block, HeadingBlock):
                heading_prefix = "#" * block.level
                text = self._render_inline(block.content)
                lines.append(f"{heading_prefix} {text}")
                lines.append("")

            elif isinstance(block, ParagraphBlock):
                text = self._render_inline(block.content)
                lines.append(text)
                lines.append("")

            elif isinstance(block, ImageBlock):
                if options.include_images and block.path and block.path.exists():
                    image_counter += 1
                    image_name = f"image{image_counter}{block.path.suffix}"
                    image_dest = images_dir / image_name
                    shutil.copy2(block.path, image_dest)
                    rel_path = f"{images_dir.name}/{image_name}"
                    lines.append(f"![{block.alt}]({rel_path})")
                elif block.url:
                    lines.append(f"![{block.alt}]({block.url})")
                lines.append("")

            elif isinstance(block, HorizontalRuleBlock):
                lines.append("---")
                lines.append("")

        # Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines), encoding="utf-8")

        return output_path

    def _render_inline(self, elements: list[InlineElement]) -> str:
        """Render inline elements to Markdown text."""
        parts = []
        for elem in elements:
            text = elem.content
            if elem.type == InlineType.BOLD:
                parts.append(f"**{text}**")
            elif elem.type == InlineType.ITALIC:
                parts.append(f"*{text}*")
            elif elem.type == InlineType.LINK and elem.url:
                parts.append(f"[{text}]({elem.url})")
            else:
                parts.append(text)
        return "".join(parts)

    def _escape_yaml(self, text: str) -> str:
        """Escape special characters for YAML string."""
        return text.replace("\\", "\\\\").replace('"', '\\"')
