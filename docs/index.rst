url_to_book
===========

**url_to_book** is a Python library and CLI tool for converting web articles
to various ebook formats: PDF, EPUB, FB2, and Markdown.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   quickstart
   api


Features
--------

- Extract articles from any URL with automatic content detection
- Download and embed images with smart filtering (removes ads, trackers)
- Convert to multiple formats: PDF, EPUB, FB2, Markdown
- Configurable fonts for PDF output
- Async API for GUI applications
- Progress callbacks for download tracking


Installation
------------

Install from PyPI::

    pip install url_to_book


Quick Example
-------------

.. code-block:: python

    from url_to_book import (
        extract_article,
        download_images,
        convert_to_document,
        render_document,
        cleanup_images,
    )

    # Extract article from URL
    article = extract_article("https://example.com/article")

    # Download images
    images = download_images(article, max_images=5)

    # Convert to document
    document = convert_to_document(article, images)

    # Render to PDF
    render_document(document, "output.pdf")

    # Clean up temporary files
    cleanup_images(images)


CLI Usage
---------

The package also provides a command-line interface::

    # Convert to PDF
    url-to-book https://example.com/article -o article.pdf

    # Convert to EPUB
    url-to-book https://example.com/article -o article.epub -f epub

    # List available fonts
    url-to-book --list-fonts


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
