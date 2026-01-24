import re
from pathlib import Path

import yaml

from .document import (
    ContentBlockType,
    Document,
    DocumentMetadata,
    HeadingBlock,
    HorizontalRuleBlock,
    ImageBlock,
    InlineElement,
    InlineType,
    ParagraphBlock,
)


class MarkdownToDocumentConverter:
    """Converts Markdown files to Document format."""

    def convert(self, markdown_path: Path) -> Document:
        """Convert Markdown file to Document.

        Args:
            markdown_path: Path to the Markdown file

        Returns:
            Document with parsed content
        """
        content = markdown_path.read_text(encoding="utf-8")
        base_dir = markdown_path.parent

        metadata, body = self._parse_frontmatter(content)
        blocks = self._parse_blocks(body, base_dir)

        return Document(metadata=metadata, blocks=blocks)

    def _parse_frontmatter(self, content: str) -> tuple[DocumentMetadata, str]:
        """Parse YAML frontmatter and return metadata and body.

        Args:
            content: Full markdown content

        Returns:
            Tuple of (DocumentMetadata, body_without_frontmatter)
        """
        frontmatter_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
        match = frontmatter_pattern.match(content)

        if match:
            yaml_content = match.group(1)
            body = content[match.end() :]

            try:
                data = yaml.safe_load(yaml_content) or {}
            except yaml.YAMLError:
                data = {}

            title = data.get("title", "Untitled")
            authors_raw = data.get("authors", "")
            if isinstance(authors_raw, str):
                authors = [a.strip() for a in authors_raw.split(",") if a.strip()]
            elif isinstance(authors_raw, list):
                authors = authors_raw
            else:
                authors = []

            metadata = DocumentMetadata(
                title=title,
                authors=authors,
                source_url=data.get("source"),
                language=data.get("language"),
            )
        else:
            body = content
            metadata = DocumentMetadata(title="Untitled")

        return metadata, body

    def _parse_blocks(self, content: str, base_dir: Path) -> list[ContentBlockType]:
        """Parse Markdown content into blocks.

        Args:
            content: Markdown body (without frontmatter)
            base_dir: Base directory for resolving relative paths

        Returns:
            List of content blocks
        """
        blocks: list[ContentBlockType] = []
        lines = content.split("\n")
        i = 0

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                i += 1
                continue

            # Heading
            heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if heading_match:
                level = len(heading_match.group(1))
                text = heading_match.group(2)
                blocks.append(
                    HeadingBlock(level=level, content=self._parse_inline(text))
                )
                i += 1
                continue

            # Horizontal rule
            if re.match(r"^(-{3,}|\*{3,}|_{3,})\s*$", line):
                blocks.append(HorizontalRuleBlock())
                i += 1
                continue

            # Image (standalone line)
            image_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", line)
            if image_match:
                alt = image_match.group(1)
                src = image_match.group(2)
                block = self._create_image_block(src, alt, base_dir)
                blocks.append(block)
                i += 1
                continue

            # Paragraph (collect consecutive non-empty lines)
            para_lines = []
            while i < len(lines) and lines[i].strip():
                # Check if next line is a special block
                if re.match(r"^#{1,6}\s+", lines[i]):
                    break
                if re.match(r"^(-{3,}|\*{3,}|_{3,})\s*$", lines[i]):
                    break
                if re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", lines[i]):
                    break

                para_lines.append(lines[i])
                i += 1

            if para_lines:
                text = " ".join(para_lines)
                blocks.append(ParagraphBlock(content=self._parse_inline(text)))

        return blocks

    def _create_image_block(
        self, src: str, alt: str, base_dir: Path
    ) -> ImageBlock:
        """Create ImageBlock from source path/URL.

        Args:
            src: Image source (URL or relative path)
            alt: Alt text
            base_dir: Base directory for relative paths

        Returns:
            ImageBlock with appropriate path or URL
        """
        if src.startswith(("http://", "https://")):
            return ImageBlock(url=src, alt=alt)

        # Local path
        local_path = base_dir / src
        if local_path.exists():
            return ImageBlock(path=local_path, alt=alt)

        # Treat as URL if local path doesn't exist
        return ImageBlock(url=src, alt=alt)

    def _parse_inline(self, text: str) -> list[InlineElement]:
        """Parse Markdown inline formatting.

        Handles **bold**, *italic*, and [links](url).

        Args:
            text: Markdown text to parse

        Returns:
            List of InlineElement objects
        """
        elements: list[InlineElement] = []
        pattern = re.compile(
            r"\*\*([^*]+)\*\*"  # **bold**
            r"|\*([^*]+)\*"  # *italic*
            r"|\[([^\]]+)\]\(([^)]+)\)"  # [text](url)
        )

        last_end = 0
        for match in pattern.finditer(text):
            # Add text before match
            if match.start() > last_end:
                plain_text = text[last_end : match.start()]
                if plain_text:
                    elements.append(InlineElement(type=InlineType.TEXT, content=plain_text))

            if match.group(1):  # Bold
                elements.append(
                    InlineElement(type=InlineType.BOLD, content=match.group(1))
                )
            elif match.group(2):  # Italic
                elements.append(
                    InlineElement(type=InlineType.ITALIC, content=match.group(2))
                )
            elif match.group(3):  # Link
                elements.append(
                    InlineElement(
                        type=InlineType.LINK, content=match.group(3), url=match.group(4)
                    )
                )

            last_end = match.end()

        # Add remaining text
        if last_end < len(text):
            remaining = text[last_end:]
            if remaining:
                elements.append(InlineElement(type=InlineType.TEXT, content=remaining))

        # If no elements, treat whole text as plain
        if not elements and text.strip():
            elements.append(InlineElement(type=InlineType.TEXT, content=text))

        return elements
