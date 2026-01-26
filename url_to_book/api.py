"""High-level public API for url_to_book.

This module provides convenient wrapper functions for the main conversion pipeline:
    URL → extract_article → download_images → convert_to_document → render_document

Example:
    >>> from url_to_book import (
    ...     extract_article,
    ...     download_images,
    ...     convert_to_document,
    ...     render_document,
    ...     cleanup_images,
    ... )
    >>> article = extract_article("https://example.com/article")
    >>> images = download_images(article, max_images=5)
    >>> document = convert_to_document(article, images)
    >>> output = render_document(document, "output.pdf")
    >>> cleanup_images(images)
"""

from pathlib import Path
from typing import Callable, Optional, Union

from .extractor import ExtractedArticle, extract_article as _extract_article
from .image_handler import (
    DownloadedImage,
    download_images as _download_images,
    download_top_image as _download_top_image,
    cleanup_images,
)
from .renderers import (
    ArticleToDocumentConverter,
    Document,
    RenderOptions,
    get_renderer,
    list_formats,
    find_available_fonts,
)


def extract_article(url: str, timeout: int = 30) -> ExtractedArticle:
    """Extract article content from URL.

    Downloads and parses the article from the given URL, extracting
    structured content blocks (headings, paragraphs), metadata, and images.

    Args:
        url: URL of the article to extract.
        timeout: Request timeout in seconds.

    Returns:
        ExtractedArticle containing title, content blocks, images, and metadata.

    Raises:
        requests.RequestException: If the URL cannot be fetched.
        ValueError: If the URL is invalid.

    Example:
        >>> article = extract_article("https://example.com/post")
        >>> print(article.title)
        'Example Article'
        >>> print(len(article.content))
        15
    """
    return _extract_article(url, timeout)


def download_images(
    article: ExtractedArticle,
    max_images: int = 10,
    include_top_image: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> list[DownloadedImage]:
    """Download images from the extracted article.

    Downloads and validates images referenced in the article.
    Filters out ads, trackers, and low-quality images automatically.

    Args:
        article: Extracted article containing image URLs.
        max_images: Maximum number of images to download.
        include_top_image: Whether to download the main article image.
        progress_callback: Optional callback for progress updates.
            Called with (downloaded_count, total_count) after each download.

    Returns:
        List of successfully downloaded images.

    Note:
        Downloaded images are stored in temporary files. Use cleanup_images()
        to remove them when done.

    Example:
        >>> def on_progress(downloaded, total):
        ...     print(f"Downloaded {downloaded}/{total}")
        >>> images = download_images(article, max_images=5, progress_callback=on_progress)
        >>> print(len(images))
        5
    """
    downloaded: list[DownloadedImage] = []
    skip_urls: set[str] = set()

    if include_top_image and article.top_image:
        top_img = _download_top_image(
            article.top_image, verbose=False, show_progress=False
        )
        if top_img:
            downloaded.append(top_img)
            skip_urls.add(article.top_image)
            if progress_callback:
                progress_callback(1, min(max_images, len(article.images)))

    remaining = max_images - len(downloaded)
    if remaining > 0 and article.images:
        more_images = _download_images(
            article.images,
            max_images=remaining,
            verbose=False,
            skip_urls=skip_urls,
            show_progress=False,
            progress_callback=progress_callback,
        )
        downloaded.extend(more_images)

    return downloaded


def convert_to_document(
    article: ExtractedArticle,
    images: Optional[list[DownloadedImage]] = None,
) -> Document:
    """Convert extracted article to a Document.

    Transforms the article into a universal document format that can be
    rendered to any supported output format (PDF, EPUB, FB2, Markdown).

    Args:
        article: Extracted article to convert.
        images: Optional list of downloaded images to include.

    Returns:
        Document with metadata and content blocks ready for rendering.

    Example:
        >>> document = convert_to_document(article, images)
        >>> document.metadata.title = "Custom Title"  # Override title
        >>> print(document.metadata.source_url)
        'https://example.com/post'
    """
    converter = ArticleToDocumentConverter()
    return converter.convert(article, images)


def render_document(
    document: Document,
    output_path: Union[Path, str],
    format: Optional[str] = None,
    options: Optional[RenderOptions] = None,
) -> Path:
    """Render document to file.

    Renders the document to the specified format. If format is not specified,
    it is inferred from the output_path extension.

    Args:
        document: Document to render.
        output_path: Output file path.
        format: Output format (pdf, epub, fb2, md). If None, inferred from extension.
        options: Optional rendering options (fonts, images, etc.).

    Returns:
        Path to the generated file.

    Raises:
        ValueError: If format is unknown or cannot be inferred.

    Example:
        >>> from url_to_book import RenderOptions
        >>> options = RenderOptions(font_family="noto-serif")
        >>> output = render_document(document, "book.pdf", options=options)
        >>> print(output)
        PosixPath('book.pdf')
    """
    output_path = Path(output_path)

    if format is None:
        ext = output_path.suffix.lower().lstrip(".")
        format_map = {"md": "md", "markdown": "md"}
        format = format_map.get(ext, ext)

    if not format:
        raise ValueError(
            f"Cannot infer format from path '{output_path}'. "
            f"Specify format explicitly or use a supported extension."
        )

    renderer = get_renderer(format)
    options = options or RenderOptions()

    return renderer.render(document, output_path, options)


def list_fonts() -> list[str]:
    """List available font families for PDF rendering.

    Returns:
        List of font family names available on the system.

    Example:
        >>> fonts = list_fonts()
        >>> print(fonts)
        ['noto-sans', 'dejavu-sans', 'liberation-sans']
    """
    return find_available_fonts()


__all__ = [
    "extract_article",
    "download_images",
    "convert_to_document",
    "render_document",
    "cleanup_images",
    "list_formats",
    "list_fonts",
]
