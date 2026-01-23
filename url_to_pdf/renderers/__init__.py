"""Renderers package for document conversion.

This package provides a unified document model and multiple output format renderers.
"""

from .base import BaseRenderer, RenderError, RenderOptions, Renderer
from .converter import ArticleToDocumentConverter
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
from .markdown_parser import MarkdownToDocumentConverter
from .registry import get_renderer, list_formats, registry

# Import renderers to trigger registration
from . import epub_renderer  # noqa: F401
from . import fb2_renderer  # noqa: F401
from . import markdown_renderer  # noqa: F401
from . import pdf_renderer  # noqa: F401

# Re-export font utilities from PDF renderer for CLI compatibility
from .pdf_renderer import (
    find_available_fonts,
    get_default_font,
    get_font_families,
    FontFamily,
)

__all__ = [
    # Document model
    "Document",
    "DocumentMetadata",
    "ContentBlockType",
    "HeadingBlock",
    "ParagraphBlock",
    "ImageBlock",
    "HorizontalRuleBlock",
    "InlineElement",
    "InlineType",
    # Base classes
    "BaseRenderer",
    "Renderer",
    "RenderOptions",
    "RenderError",
    # Converters
    "ArticleToDocumentConverter",
    "MarkdownToDocumentConverter",
    # Registry
    "registry",
    "get_renderer",
    "list_formats",
    # Font utilities
    "find_available_fonts",
    "get_default_font",
    "get_font_families",
    "FontFamily",
]
