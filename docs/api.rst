API Reference
=============

This page documents the public API of url_to_book.


Main API Functions
------------------

These are the primary functions for the conversion pipeline.

.. autofunction:: url_to_book.extract_article

.. autofunction:: url_to_book.download_images

.. autofunction:: url_to_book.convert_to_document

.. autofunction:: url_to_book.render_document

.. autofunction:: url_to_book.cleanup_images


Utility Functions
-----------------

.. autofunction:: url_to_book.list_formats

.. autofunction:: url_to_book.list_fonts


Async API
---------

Asynchronous versions for use with asyncio-based applications.

.. autofunction:: url_to_book.extract_article_async

.. autofunction:: url_to_book.download_images_async


Data Classes
------------

ExtractedArticle
~~~~~~~~~~~~~~~~

.. autoclass:: url_to_book.ExtractedArticle
   :members:
   :undoc-members:

ContentBlock
~~~~~~~~~~~~

.. autoclass:: url_to_book.ContentBlock
   :members:
   :undoc-members:

DownloadedImage
~~~~~~~~~~~~~~~

.. autoclass:: url_to_book.DownloadedImage
   :members:
   :undoc-members:


Document Model
--------------

Document
~~~~~~~~

.. autoclass:: url_to_book.Document
   :members:
   :undoc-members:

DocumentMetadata
~~~~~~~~~~~~~~~~

.. autoclass:: url_to_book.DocumentMetadata
   :members:
   :undoc-members:

RenderOptions
~~~~~~~~~~~~~

.. autoclass:: url_to_book.RenderOptions
   :members:
   :undoc-members:


Block Types
-----------

These classes represent different types of content blocks in a document.

.. autoclass:: url_to_book.HeadingBlock
   :members:
   :undoc-members:

.. autoclass:: url_to_book.ParagraphBlock
   :members:
   :undoc-members:

.. autoclass:: url_to_book.ImageBlock
   :members:
   :undoc-members:

.. autoclass:: url_to_book.HorizontalRuleBlock
   :members:
   :undoc-members:

.. autoclass:: url_to_book.InlineElement
   :members:
   :undoc-members:

.. autoclass:: url_to_book.InlineType
   :members:
   :undoc-members:


Exceptions
----------

.. autoclass:: url_to_book.RenderError
   :members:
   :undoc-members:
