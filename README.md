# url_to_book

[![PyPI version](https://badge.fury.io/py/url-to-book.svg)](https://pypi.org/project/url-to-book/)
[![Python versions](https://img.shields.io/pypi/pyversions/url-to-book.svg)](https://pypi.org/project/url-to-book/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

CLI tool to extract article content from a web page and save it in various formats (PDF, EPUB, FB2, Markdown).

## Features

- Extracts article text, title, and images
- Preserves text formatting (bold, italic, links)
- Multiple output formats: PDF, EPUB, FB2, Markdown
- Filters out ads and tracking images
- Supports Cyrillic text
- Multiple font choices with Unicode/Cyrillic support (Noto Sans, Liberation, DejaVu, Free fonts)
- Automatic font detection and fallback

## Installation

### From PyPI (recommended)

```bash
pip install url-to-book
```

### From source

```bash
git clone https://github.com/RomanAverin/url_to_book.git
cd url_to_book
pip install -e .
```

## Usage

```bash
# Basic usage (uses default font)
url-to-book https://example.com/article -o article.pdf

# With custom title
url-to-book https://example.com/article -o article.pdf --title "My Title"

# Without images
url-to-book https://example.com/article -o article.pdf --no-images

# Verbose output
url-to-book https://example.com/article -o article.pdf -v

# List available fonts
url-to-book --list-fonts

# Use specific font (sans-serif)
url-to-book https://example.com/article -o article.pdf --font noto-sans

# Use serif font
url-to-book https://example.com/article -o article.pdf --font noto-serif

# Use Liberation Sans (metrics-compatible with Arial)
url-to-book https://example.com/article -o article.pdf --font liberation-sans

# With verbose output showing which font is used
url-to-book https://example.com/article -o article.pdf -v --font noto-serif
```

## Output Formats

The tool supports multiple output formats. Each format has different capabilities and use cases.

### Supported Formats

Use `--list-formats` to see available formats:

```bash
url-to-book --list-formats
```

Output:
```
Available output formats:
  * pdf (features: fonts, images, links)
  * epub (features: images, links)
  * fb2 (features: images, links)
  * md (features: images, links)
```

### Format Comparison

| Format | Description | Features | Best For |
|--------|-------------|----------|----------|
| **PDF** | Portable Document Format | fonts, images, links | Printing, universal reading, archiving |
| **EPUB** | Electronic Publication | images, links | E-readers (Kindle, Kobo, etc.) |
| **FB2** | FictionBook 2.0 (XML) | images, links | Russian e-book readers |
| **MD** | Markdown with YAML frontmatter | images, links | Further processing, version control |

**Feature explanation:**
- **fonts** - Customizable font families (8 options for PDF)
- **images** - Embedded images support
- **links** - Clickable hyperlinks preserved

### Format Usage Examples

#### Extract to PDF (default)

```bash
# Default format (PDF)
url-to-book https://example.com/article -o article.pdf

# Explicit format specification
url-to-book https://example.com/article -o article.pdf -f pdf

# PDF with custom font
url-to-book https://example.com/article -o article.pdf --font noto-serif
```

#### Extract to EPUB

```bash
# For e-readers
url-to-book https://example.com/article -o article.epub -f epub

# EPUB without images (smaller file)
url-to-book https://example.com/article -o article.epub -f epub --no-images
```

#### Extract to FB2

```bash
# For Russian e-book readers
url-to-book https://example.com/article -o article.fb2 -f fb2

# FB2 with limited images
url-to-book https://example.com/article -o article.fb2 -f fb2 --max-images 5
```

#### Extract to Markdown

```bash
# For version control or further processing
url-to-book https://example.com/article -o article.md -f md

# Images will be saved to article_images/ directory
```

### Converting Markdown Files

You can convert previously extracted Markdown files to other formats:

```bash
# First, extract to Markdown
url-to-book https://example.com/article -o article.md -f md

# Then convert to PDF
url-to-book article.md -o article.pdf -f pdf

# Or to EPUB
url-to-book article.md -o article.epub -f epub

# Or to FB2
url-to-book article.md -o article.fb2 -f fb2
```

This workflow is useful for:
- Extracting once, converting to multiple formats
- Editing content before final conversion
- Version control of article content

### Format-Specific Notes

**PDF:**
- Only format supporting font selection (use `--font` option)
- Best for printing and archiving
- Supports 8 font families (see "Available Fonts" section)

**EPUB:**
- Standard format for most e-readers
- Reflowable text (adapts to screen size)
- Wide compatibility (Calibre, Apple Books, etc.)

**FB2:**
- XML-based format popular in Russia
- Good for Russian-language e-book readers
- Embedded images as base64

**Markdown:**
- Human-readable plain text
- YAML frontmatter with metadata (title, authors, source URL)
- Images saved to `{filename}_images/` directory
- Can be edited before converting to other formats

### Available Fonts

**Note:** Font selection is only available for PDF format.

The tool supports the following font families with Unicode/Cyrillic support:

- **noto-sans** (Noto Sans) - Google's comprehensive sans-serif font
- **noto-serif** (Noto Serif) - Google's comprehensive serif font
- **liberation-sans** (Liberation Sans) - Metrics-compatible with Arial
- **liberation-serif** (Liberation Serif) - Metrics-compatible with Times New Roman
- **free-sans** (Free Sans) - GNU FreeFont sans-serif
- **free-serif** (Free Serif) - GNU FreeFont serif
- **dejavu-sans** (DejaVu Sans) - Popular Linux sans-serif font
- **dejavu-serif** (DejaVu Serif) - Popular Linux serif font

The tool will automatically detect which fonts are installed in your system and use the first available one as default. Use `--list-fonts` to see which fonts are available on your system.

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linter
uv run pylint url_to_book
```

## License

MIT
