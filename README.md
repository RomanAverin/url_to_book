# url-to-pdf

CLI tool to extract article content from a web page and save it as PDF.

## Features

- Extracts article text, title, and images
- Preserves text formatting (bold, italic, links)
- Filters out ads and tracking images
- Supports Cyrillic text

## Installation

```bash
uv sync
```

## Usage

```bash
# Basic usage
url-to-pdf https://example.com/article -o article.pdf

# With custom title
url-to-pdf https://example.com/article -o article.pdf --title "My Title"

# Without images
url-to-pdf https://example.com/article -o article.pdf --no-images

# Verbose output
url-to-pdf https://example.com/article -o article.pdf -v
```

## Development

```bash
# Install dev dependencies
uv sync --extra dev

# Run tests
uv run pytest

# Run linter
uv run pylint url_to_pdf
```

## License

MIT
