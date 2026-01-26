"""Async public API for url_to_book.

This module provides asynchronous versions of the main API functions
for use with asyncio-based applications (e.g., GTK with GLib.idle_add).

Example:
    >>> import asyncio
    >>> from url_to_book import (
    ...     extract_article_async,
    ...     download_images_async,
    ...     convert_to_document,
    ...     render_document,
    ...     cleanup_images,
    ... )
    >>>
    >>> async def main():
    ...     article = await extract_article_async("https://example.com/article")
    ...     images = await download_images_async(article, max_images=5)
    ...     document = convert_to_document(article, images)
    ...     output = render_document(document, "output.pdf")
    ...     cleanup_images(images)
    ...     return output
    >>>
    >>> asyncio.run(main())
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

from .extractor import ExtractedArticle
from .image_handler import DownloadedImage
from .api import (
    extract_article as _extract_article_sync,
    download_images as _download_images_sync,
)

# Default executor for blocking I/O operations
_executor = ThreadPoolExecutor(max_workers=4)


async def extract_article_async(
    url: str,
    timeout: int = 30,
    executor: Optional[ThreadPoolExecutor] = None,
) -> ExtractedArticle:
    """Extract article content from URL asynchronously.

    Downloads and parses the article in a thread pool to avoid blocking.

    Args:
        url: URL of the article to extract.
        timeout: Request timeout in seconds.
        executor: Optional custom ThreadPoolExecutor.

    Returns:
        ExtractedArticle containing title, content blocks, images, and metadata.

    Raises:
        requests.RequestException: If the URL cannot be fetched.

    Example:
        >>> import asyncio
        >>> async def main():
        ...     article = await extract_article_async("https://example.com")
        ...     print(article.title)
        >>> asyncio.run(main())
    """
    loop = asyncio.get_running_loop()
    exec = executor or _executor
    return await loop.run_in_executor(
        exec, lambda: _extract_article_sync(url, timeout)
    )


async def download_images_async(
    article: ExtractedArticle,
    max_images: int = 10,
    include_top_image: bool = True,
    progress_callback: Optional[Callable[[int, int], None]] = None,
    executor: Optional[ThreadPoolExecutor] = None,
) -> list[DownloadedImage]:
    """Download images from the extracted article asynchronously.

    Downloads images in a thread pool to avoid blocking the event loop.

    Args:
        article: Extracted article containing image URLs.
        max_images: Maximum number of images to download.
        include_top_image: Whether to download the main article image.
        progress_callback: Optional callback for progress updates.
            Called with (downloaded_count, total_count) after each download.
            Note: Callback is called from thread pool, use proper synchronization.
        executor: Optional custom ThreadPoolExecutor.

    Returns:
        List of successfully downloaded images.

    Note:
        Downloaded images are stored in temporary files. Use cleanup_images()
        to remove them when done.

    Example:
        >>> import asyncio
        >>> async def main():
        ...     article = await extract_article_async("https://example.com")
        ...     images = await download_images_async(article, max_images=5)
        ...     print(f"Downloaded {len(images)} images")
        >>> asyncio.run(main())
    """
    loop = asyncio.get_running_loop()
    exec = executor or _executor

    def download():
        return _download_images_sync(
            article,
            max_images=max_images,
            include_top_image=include_top_image,
            progress_callback=progress_callback,
        )

    return await loop.run_in_executor(exec, download)


__all__ = [
    "extract_article_async",
    "download_images_async",
]
