"""URL to Book - Convert web articles to PDF, EPUB, FB2, and Markdown.

This package provides a complete pipeline for converting web articles
to various ebook formats.

Main API functions:
    - extract_article: Download and parse article from URL
    - download_images: Download article images
    - convert_to_document: Convert to universal document format
    - render_document: Render document to file (PDF, EPUB, FB2, MD)
    - cleanup_images: Remove temporary image files

Async API (for GUI applications):
    - extract_article_async: Async version of extract_article
    - download_images_async: Async version of download_images

Data classes:
    - ExtractedArticle: Parsed article with content blocks
    - ContentBlock: Heading or paragraph from article
    - DownloadedImage: Downloaded image file info
    - Document: Universal document for rendering
    - DocumentMetadata: Document title, authors, etc.
    - RenderOptions: Rendering options (fonts, images)

Example:
    >>> from url_to_book import (
    ...     extract_article,
    ...     download_images,
    ...     convert_to_document,
    ...     render_document,
    ...     cleanup_images,
    ... )
    >>>
    >>> article = extract_article("https://example.com/article")
    >>> images = download_images(article, max_images=5)
    >>> document = convert_to_document(article, images)
    >>> render_document(document, "output.epub", format="epub")
    >>> cleanup_images(images)
"""

__version__ = "1.1.0"

# Core data classes
from .extractor import ExtractedArticle, ContentBlock
from .image_handler import DownloadedImage

# Document model
from .renderers import (
    Document,
    DocumentMetadata,
    RenderOptions,
    RenderError,
    # Block types
    HeadingBlock,
    ParagraphBlock,
    ImageBlock,
    HorizontalRuleBlock,
    InlineElement,
    InlineType,
    ContentBlockType,
)

# Main API functions
from .api import (
    extract_article,
    download_images,
    convert_to_document,
    render_document,
    cleanup_images,
    list_formats,
    list_fonts,
)

# Async API
from .async_api import (
    extract_article_async,
    download_images_async,
)

__all__ = [
    # Version
    "__version__",
    # Core data classes
    "ExtractedArticle",
    "ContentBlock",
    "DownloadedImage",
    # Document model
    "Document",
    "DocumentMetadata",
    "RenderOptions",
    "RenderError",
    # Block types
    "HeadingBlock",
    "ParagraphBlock",
    "ImageBlock",
    "HorizontalRuleBlock",
    "InlineElement",
    "InlineType",
    "ContentBlockType",
    # Main API
    "extract_article",
    "download_images",
    "convert_to_document",
    "render_document",
    "cleanup_images",
    "list_formats",
    "list_fonts",
    # Async API
    "extract_article_async",
    "download_images_async",
]
