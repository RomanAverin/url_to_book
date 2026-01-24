from pathlib import Path

import click

from .extractor import extract_article
from .image_handler import cleanup_images, download_images, download_top_image
from .progress import ProgressReporter
from .renderers import (
    ArticleToDocumentConverter,
    MarkdownToDocumentConverter,
    RenderOptions,
    find_available_fonts,
    get_default_font,
    get_font_families,
    get_renderer,
    list_formats,
)
from .state_machine import JobState


def _handle_list_fonts() -> None:
    """Handle --list-fonts flag: display available fonts and exit."""
    available = find_available_fonts()
    all_families = get_font_families()

    if not available:
        click.echo("No fonts are available in the system.")
        click.echo("\nPlease install one of the following:")
        for name, family in all_families.items():
            click.echo(f"  - {family.display_name}")
        raise click.ClickException("No fonts available")

    try:
        default = get_default_font()
    except RuntimeError:
        default = None

    click.echo("Available fonts:")
    for name in available:
        family = all_families[name]
        default_mark = " (default)" if name == default else ""
        click.echo(f"  * {name} ({family.display_name}){default_mark}")


def _handle_list_formats() -> None:
    """Handle --list-formats flag: display available formats and exit."""
    formats = list_formats()
    click.echo("Available output formats:")
    for fmt in formats:
        renderer = get_renderer(fmt)
        features = ", ".join(sorted(renderer.SUPPORTED_FEATURES))
        click.echo(f"  * {fmt} (features: {features})")


def _validate_required_args(source: str | None, output: str | None) -> None:
    """Validate that required arguments are provided."""
    if not source:
        raise click.ClickException(
            "SOURCE is required (URL or path to .md file, unless using --list-fonts/--list-formats)"
        )
    if not output:
        raise click.ClickException("Output file path is required (-o/--output)")


def _show_font_info(font: str | None, verbose: bool) -> None:
    """Display information about the selected font."""
    if not verbose:
        return

    if font:
        click.echo(f"Using font: {font}")
    else:
        try:
            default_font = get_default_font()
            click.echo(f"Using default font: {default_font}")
        except RuntimeError:
            pass


def _show_article_info(article, url: str, verbose: bool) -> None:
    """Display extracted article information."""
    if not verbose:
        return

    click.echo(f"Extracting article from: {url}")
    click.echo(f"Title: {article.title}")
    click.echo(f"Text length: {len(article.text)} chars")
    click.echo(f"Top image: {article.top_image or 'None'}")
    click.echo(f"Found {len(article.images)} images")


def _download_article_images(article, no_images: bool, max_images: int, verbose: bool):
    """Download article images if needed."""
    top_image = None
    images = []

    if no_images:
        return top_image, images

    show_progress = not verbose

    if article.top_image:
        top_image = download_top_image(
            article.top_image, verbose=verbose, show_progress=show_progress
        )

    if article.images:
        skip_urls = {article.top_image} if article.top_image else set()
        images = download_images(
            article.images,
            max_images=max_images,
            verbose=verbose,
            skip_urls=skip_urls,
            show_progress=show_progress,
        )

    if not verbose:
        total = len(images) + (1 if top_image else 0)
        click.echo(f"Downloaded {total} image(s)")
    elif verbose:
        click.echo(
            f"Downloaded {len(images)} images" + (" + top image" if top_image else "")
        )

    return top_image, images


def _download_article_images_with_progress(
    article, no_images: bool, max_images: int, progress_reporter: ProgressReporter
):
    """Download article images with progress updates."""
    top_image = None
    images = []

    if no_images:
        return top_image, images

    total_images = 0
    if article.top_image:
        total_images += 1
    if article.images:
        total_images += min(len(article.images), max_images)

    def on_image_downloaded(downloaded: int, total: int):
        progress_reporter.update_images_progress(downloaded, total)

    if article.top_image:
        top_image = download_top_image(article.top_image, verbose=False, show_progress=False)
        if top_image:
            on_image_downloaded(1, total_images)

    if article.images:
        skip_urls = {article.top_image} if article.top_image else set()
        images = download_images(
            article.images,
            max_images=max_images,
            verbose=False,
            skip_urls=skip_urls,
            show_progress=False,
            progress_callback=on_image_downloaded,
        )

    return top_image, images


def _is_markdown_file(source: str) -> bool:
    """Check if source is a Markdown file path."""
    return source.endswith(".md") and not source.startswith(("http://", "https://"))


def _is_url(source: str) -> bool:
    """Check if source is a URL."""
    return source.startswith(("http://", "https://"))


@click.command()
@click.argument("source", required=False)
@click.option(
    "-o",
    "--output",
    help="Output file path",
)
@click.option(
    "-f",
    "--format",
    "output_format",
    default="pdf",
    type=click.Choice(["pdf", "epub", "fb2", "md"]),
    help="Output format (default: pdf)",
)
@click.option(
    "--list-formats",
    "show_formats",
    is_flag=True,
    default=False,
    help="List available output formats and exit",
)
@click.option(
    "--title",
    default=None,
    help="Custom title (overrides extracted/parsed title)",
)
@click.option(
    "--no-images",
    is_flag=True,
    default=False,
    help="Skip downloading and including images",
)
@click.option(
    "--max-images",
    default=10,
    type=int,
    help="Maximum number of images to include (default: 10)",
)
@click.option(
    "--font",
    default=None,
    help="Font family to use (only for PDF format)",
)
@click.option(
    "--list-fonts",
    is_flag=True,
    default=False,
    help="List available fonts and exit",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose output",
)
def main(  # pylint: disable=too-many-statements
    source: str | None,
    output: str | None,
    output_format: str,
    show_formats: bool = False,
    title: str | None = None,
    no_images: bool = False,
    max_images: int = 10,
    font: str | None = None,
    list_fonts: bool = False,
    verbose: bool = False,
) -> None:
    """Extract article from URL or convert Markdown file to various formats.

    SOURCE can be:
      - A URL to extract article from
      - A path to a .md file to convert

    Examples:
      url-to-book https://example.com/article -o article.pdf
      url-to-book https://example.com/article -o article.md -f md
      url-to-book article.md -o article.pdf -f pdf
      url-to-book article.md -o article.epub -f epub
    """
    # Handle --list-formats
    if show_formats:
        _handle_list_formats()
        return

    # Handle --list-fonts
    if list_fonts:
        _handle_list_fonts()
        return

    # Validate required arguments
    _validate_required_args(source, output)
    assert source is not None
    assert output is not None

    # Get renderer and validate font option
    renderer = get_renderer(output_format)
    if font and not renderer.supports_feature("fonts"):
        raise click.ClickException(
            f"Option --font is not supported for '{output_format}' format. "
            f"Font selection is only available for: pdf"
        )

    # Show font information (only for PDF)
    if output_format == "pdf":
        _show_font_info(font, verbose)

    all_images = []

    try:
        # Determine source type and process
        if _is_markdown_file(source):
            # Convert from Markdown file
            md_path = Path(source)
            if not md_path.exists():
                raise click.ClickException(f"Markdown file not found: {source}")

            if verbose:
                click.echo(f"Reading Markdown file: {source}")

            converter = MarkdownToDocumentConverter()
            document = converter.convert(md_path)

            # Override title if provided
            if title:
                document.metadata.title = title

            if verbose:
                click.echo(f"Title: {document.metadata.title}")
                click.echo(f"Blocks: {len(document.blocks)}")

        elif _is_url(source):
            # Extract from URL
            if not verbose:
                with ProgressReporter(source) as progress_reporter:
                    # Stage 1: Extract article
                    progress_reporter.update_state(JobState.EXTRACTING)
                    article = extract_article(source)

                    # Stage 2: Download images
                    progress_reporter.update_state(JobState.DOWNLOADING_IMAGES)
                    top_image, images = _download_article_images_with_progress(
                        article, no_images, max_images, progress_reporter
                    )
                    all_images = ([top_image] if top_image else []) + images

                    # Stage 3: Convert to Document
                    progress_reporter.update_state(JobState.GENERATING_PDF)
                    converter = ArticleToDocumentConverter()
                    document = converter.convert(article, all_images)

                    # Override title if provided
                    if title:
                        document.metadata.title = title

                    # Render
                    options = RenderOptions(
                        font_family=font, include_images=not no_images
                    )
                    renderer.render(document, Path(output), options)

                    # Stage 4: Completed
                    progress_reporter.update_state(JobState.COMPLETED)

                click.echo(f"Saved: {output}")
                return

            # Verbose mode
            article = extract_article(source)
            _show_article_info(article, source, verbose)

            top_image, images = _download_article_images(
                article, no_images, max_images, verbose
            )
            all_images = ([top_image] if top_image else []) + images

            converter = ArticleToDocumentConverter()
            document = converter.convert(article, all_images)

            if title:
                document.metadata.title = title

        else:
            raise click.ClickException(
                f"Invalid source: {source}\n"
                f"SOURCE must be a URL (http://... or https://...) "
                f"or a path to a .md file"
            )

        # Render document
        if verbose:
            click.echo(f"Generating {output_format.upper()}: {output}")

        options = RenderOptions(font_family=font, include_images=not no_images)
        renderer.render(document, Path(output), options)

        click.echo(f"Saved: {output}")

    except Exception as e:
        if verbose:
            import traceback  # pylint: disable=import-outside-toplevel
            traceback.print_exc()
        raise click.ClickException(f"Failed: {e}") from e
    finally:
        if all_images:
            cleanup_images(all_images)


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
