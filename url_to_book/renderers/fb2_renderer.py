import base64
import mimetypes
import uuid
import xml.etree.ElementTree as ET
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

FB2_NAMESPACE = "http://www.gribuser.ru/xml/fictionbook/2.0"
XLINK_NAMESPACE = "http://www.w3.org/1999/xlink"


@registry.register
class FB2Renderer(BaseRenderer):
    """Renders Document to FB2 format."""

    SUPPORTED_FEATURES = {"images", "links"}

    @property
    def format_name(self) -> str:
        return "fb2"

    @property
    def file_extension(self) -> str:
        return ".fb2"

    def render(  # pylint: disable=too-many-statements
        self, document: Document, output_path: Path, options: Optional[RenderOptions] = None
    ) -> Path:
        """Render document to FB2 file."""
        options = options or RenderOptions()
        output_path = Path(output_path)

        if output_path.suffix.lower() != ".fb2":
            output_path = output_path.with_suffix(".fb2")

        # Register namespaces
        ET.register_namespace("", FB2_NAMESPACE)
        ET.register_namespace("xlink", XLINK_NAMESPACE)

        # Create root element
        root = ET.Element(f"{{{FB2_NAMESPACE}}}FictionBook")

        # Description
        description = ET.SubElement(root, f"{{{FB2_NAMESPACE}}}description")
        title_info = ET.SubElement(description, f"{{{FB2_NAMESPACE}}}title-info")

        # Genre
        genre = ET.SubElement(title_info, f"{{{FB2_NAMESPACE}}}genre")
        genre.text = "nonfiction"

        # Authors
        if document.metadata.authors:
            for author_name in document.metadata.authors:
                author = ET.SubElement(title_info, f"{{{FB2_NAMESPACE}}}author")
                parts = author_name.strip().split(maxsplit=1)
                if len(parts) >= 1:
                    first_name = ET.SubElement(author, f"{{{FB2_NAMESPACE}}}first-name")
                    first_name.text = parts[0]
                if len(parts) >= 2:
                    last_name = ET.SubElement(author, f"{{{FB2_NAMESPACE}}}last-name")
                    last_name.text = parts[1]
        else:
            author = ET.SubElement(title_info, f"{{{FB2_NAMESPACE}}}author")
            first_name = ET.SubElement(author, f"{{{FB2_NAMESPACE}}}first-name")
            first_name.text = "Unknown"

        # Book title
        book_title = ET.SubElement(title_info, f"{{{FB2_NAMESPACE}}}book-title")
        book_title.text = document.metadata.title

        # Language
        lang = ET.SubElement(title_info, f"{{{FB2_NAMESPACE}}}lang")
        lang.text = document.metadata.language or "en"

        # Source URL as annotation
        if document.metadata.source_url:
            annotation = ET.SubElement(title_info, f"{{{FB2_NAMESPACE}}}annotation")
            p = ET.SubElement(annotation, f"{{{FB2_NAMESPACE}}}p")
            p.text = f"Source: {document.metadata.source_url}"

        # Document info
        doc_info = ET.SubElement(description, f"{{{FB2_NAMESPACE}}}document-info")
        doc_id = ET.SubElement(doc_info, f"{{{FB2_NAMESPACE}}}id")
        doc_id.text = str(uuid.uuid4())

        # Body
        body = ET.SubElement(root, f"{{{FB2_NAMESPACE}}}body")

        # Main section
        section = ET.SubElement(body, f"{{{FB2_NAMESPACE}}}section")

        # Title
        title_elem = ET.SubElement(section, f"{{{FB2_NAMESPACE}}}title")
        p = ET.SubElement(title_elem, f"{{{FB2_NAMESPACE}}}p")
        p.text = document.metadata.title

        # Binary images storage
        binaries: list[tuple[str, str, bytes]] = []
        image_counter = 0

        # Process content blocks
        for block in document.blocks:
            if isinstance(block, HeadingBlock):
                subtitle = ET.SubElement(section, f"{{{FB2_NAMESPACE}}}subtitle")
                self._add_inline_content(subtitle, block.content)

            elif isinstance(block, ParagraphBlock):
                p = ET.SubElement(section, f"{{{FB2_NAMESPACE}}}p")
                self._add_inline_content(p, block.content)

            elif isinstance(block, ImageBlock):
                if options.include_images and block.path and block.path.exists():
                    image_counter += 1
                    image_id = f"image{image_counter}"
                    mime_type = mimetypes.guess_type(str(block.path))[0] or "image/jpeg"
                    image_data = block.path.read_bytes()
                    binaries.append((image_id, mime_type, image_data))

                    # Add image reference
                    image_elem = ET.SubElement(section, f"{{{FB2_NAMESPACE}}}image")
                    image_elem.set(f"{{{XLINK_NAMESPACE}}}href", f"#{image_id}")

            elif isinstance(block, HorizontalRuleBlock):
                ET.SubElement(section, f"{{{FB2_NAMESPACE}}}empty-line")

        # Add binary data for images
        for image_id, mime_type, data in binaries:
            binary = ET.SubElement(root, f"{{{FB2_NAMESPACE}}}binary")
            binary.set("id", image_id)
            binary.set("content-type", mime_type)
            binary.text = base64.b64encode(data).decode("ascii")

        # Write file
        output_path.parent.mkdir(parents=True, exist_ok=True)

        tree = ET.ElementTree(root)
        ET.indent(tree, space="  ")

        with open(output_path, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            tree.write(f, encoding="UTF-8", xml_declaration=False)

        return output_path

    def _add_inline_content(self, parent: ET.Element, elements: list[InlineElement]):
        """Add inline elements to FB2 parent element."""
        if not elements:
            return

        # FB2 requires mixed content handling
        current_text = ""
        last_elem = None

        for elem in elements:
            if elem.type == InlineType.TEXT:
                current_text += elem.content
            elif elem.type == InlineType.BOLD:
                if current_text:
                    if last_elem is None:
                        parent.text = (parent.text or "") + current_text
                    else:
                        last_elem.tail = (last_elem.tail or "") + current_text
                    current_text = ""
                strong = ET.SubElement(parent, f"{{{FB2_NAMESPACE}}}strong")
                strong.text = elem.content
                last_elem = strong
            elif elem.type == InlineType.ITALIC:
                if current_text:
                    if last_elem is None:
                        parent.text = (parent.text or "") + current_text
                    else:
                        last_elem.tail = (last_elem.tail or "") + current_text
                    current_text = ""
                emphasis = ET.SubElement(parent, f"{{{FB2_NAMESPACE}}}emphasis")
                emphasis.text = elem.content
                last_elem = emphasis
            elif elem.type == InlineType.LINK:
                if current_text:
                    if last_elem is None:
                        parent.text = (parent.text or "") + current_text
                    else:
                        last_elem.tail = (last_elem.tail or "") + current_text
                    current_text = ""
                link = ET.SubElement(parent, f"{{{FB2_NAMESPACE}}}a")
                if elem.url:
                    link.set(f"{{{XLINK_NAMESPACE}}}href", elem.url)
                link.text = elem.content
                last_elem = link

        # Handle remaining text
        if current_text:
            if last_elem is None:
                parent.text = (parent.text or "") + current_text
            else:
                last_elem.tail = (last_elem.tail or "") + current_text
