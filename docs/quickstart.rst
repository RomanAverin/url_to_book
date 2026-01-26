Quickstart
==========

This guide will help you get started with url_to_book.


Installation
------------

Install from PyPI::

    pip install url_to_book


Basic Usage
-----------

The simplest way to convert a web article:

.. code-block:: python

    from url_to_book import (
        extract_article,
        download_images,
        convert_to_document,
        render_document,
        cleanup_images,
    )

    # 1. Extract article from URL
    article = extract_article("https://example.com/article")
    print(f"Title: {article.title}")
    print(f"Found {len(article.images)} images")

    # 2. Download images (optional)
    images = download_images(article, max_images=5)

    # 3. Convert to document
    document = convert_to_document(article, images)

    # 4. Render to desired format
    render_document(document, "output.pdf")

    # 5. Clean up temporary image files
    cleanup_images(images)


Step-by-Step Pipeline
---------------------

The conversion process consists of four main steps:

1. **Extract Article** - Download and parse the web page
2. **Download Images** - Download referenced images (optional)
3. **Convert to Document** - Create a universal document structure
4. **Render Document** - Output to PDF, EPUB, FB2, or Markdown


Extract Article
~~~~~~~~~~~~~~~

.. code-block:: python

    from url_to_book import extract_article

    article = extract_article("https://example.com/article", timeout=30)

    # Access article data
    print(article.title)       # Article title
    print(article.authors)     # List of authors
    print(article.content)     # List of ContentBlock objects
    print(article.images)      # List of image URLs
    print(article.source_url)  # Original URL


Download Images
~~~~~~~~~~~~~~~

.. code-block:: python

    from url_to_book import download_images

    # With progress callback
    def on_progress(downloaded, total):
        print(f"Downloaded {downloaded}/{total} images")

    images = download_images(
        article,
        max_images=10,
        include_top_image=True,
        progress_callback=on_progress,
    )

    # Images are saved to temporary files
    for img in images:
        print(f"{img.original_url} -> {img.path} ({img.width}x{img.height})")


Convert to Document
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from url_to_book import convert_to_document

    document = convert_to_document(article, images)

    # You can modify the document before rendering
    document.metadata.title = "Custom Title"
    document.metadata.authors = ["Author Name"]


Render Document
~~~~~~~~~~~~~~~

.. code-block:: python

    from url_to_book import render_document, RenderOptions, list_formats

    # See available formats
    print(list_formats())  # ['pdf', 'epub', 'fb2', 'md']

    # Render to PDF with custom font
    options = RenderOptions(font_family="noto-serif")
    render_document(document, "output.pdf", options=options)

    # Render to EPUB
    render_document(document, "output.epub", format="epub")

    # Render to FB2
    render_document(document, "output.fb2", format="fb2")

    # Render to Markdown
    render_document(document, "output.md", format="md")


Cleanup
~~~~~~~

.. code-block:: python

    from url_to_book import cleanup_images

    # Remove temporary image files
    cleanup_images(images)


Async Usage (for GUI)
---------------------

For GTK or other async applications:

.. code-block:: python

    import asyncio
    from url_to_book import (
        extract_article_async,
        download_images_async,
        convert_to_document,
        render_document,
        cleanup_images,
    )

    async def convert_article(url: str, output_path: str):
        # Extract and download in background
        article = await extract_article_async(url)
        images = await download_images_async(article, max_images=5)

        # These are fast, no need for async
        document = convert_to_document(article, images)
        render_document(document, output_path)
        cleanup_images(images)

    # Run
    asyncio.run(convert_article("https://example.com", "output.pdf"))


GTK Integration Example
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    import asyncio
    from gi.repository import GLib
    from url_to_book import (
        extract_article_async,
        download_images_async,
        convert_to_document,
        render_document,
        cleanup_images,
    )

    class ArticleConverter:
        def __init__(self, progress_bar, status_label):
            self.progress_bar = progress_bar
            self.status_label = status_label

        def update_progress(self, downloaded, total):
            # Called from thread pool, use idle_add
            GLib.idle_add(
                self.progress_bar.set_fraction,
                downloaded / total
            )

        async def convert(self, url: str, output_path: str):
            GLib.idle_add(self.status_label.set_text, "Extracting article...")
            article = await extract_article_async(url)

            GLib.idle_add(self.status_label.set_text, "Downloading images...")
            images = await download_images_async(
                article,
                max_images=5,
                progress_callback=self.update_progress,
            )

            GLib.idle_add(self.status_label.set_text, "Converting...")
            document = convert_to_document(article, images)
            render_document(document, output_path)
            cleanup_images(images)

            GLib.idle_add(self.status_label.set_text, "Done!")


Available Fonts
---------------

For PDF output, you can specify different fonts:

.. code-block:: python

    from url_to_book import list_fonts, RenderOptions, render_document

    # List available fonts on your system
    fonts = list_fonts()
    print(fonts)  # ['noto-sans', 'dejavu-sans', 'liberation-sans', ...]

    # Use a specific font
    options = RenderOptions(font_family="noto-serif")
    render_document(document, "output.pdf", options=options)


Error Handling
--------------

.. code-block:: python

    from url_to_book import (
        extract_article,
        render_document,
        RenderError,
    )
    import requests

    try:
        article = extract_article("https://example.com/article")
    except requests.RequestException as e:
        print(f"Failed to fetch article: {e}")

    try:
        render_document(document, "output.pdf")
    except RenderError as e:
        print(f"Failed to render: {e}")
