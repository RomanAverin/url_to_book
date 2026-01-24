from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fpdf import FPDF

from .base import BaseRenderer, RenderError, RenderOptions
from .document import (
    Document,
    HeadingBlock,
    HorizontalRuleBlock,
    ImageBlock,
    InlineElement,
    InlineType,
    ParagraphBlock,
)
from .registry import registry


@dataclass
class FontFamily:
    """Describes a font family with all its styles."""

    name: str  # Internal name (e.g., "noto-sans")
    display_name: str  # Display name (e.g., "Noto Sans")
    regular: list[str]  # Paths to regular font files
    bold: list[str]  # Paths to bold font files
    italic: list[str]  # Paths to italic font files
    bold_italic: list[str]  # Paths to bold italic font files


HEADING_SIZES = {
    1: 16,
    2: 14,
    3: 13,
    4: 12,
    5: 11,
    6: 11,
}

FONT_WEIGHTS = {
    "regular": 400,
    "bold": 700,
    "italic": 400,
    "bold_italic": 700,
}

FONT_FAMILIES = {
    "noto-sans": FontFamily(
        name="noto-sans",
        display_name="Noto Sans",
        regular=[
            "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf",
            "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/noto/NotoSans-Regular.ttf",
        ],
        bold=[
            "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf",
            "/usr/share/fonts/google-noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/noto/NotoSans-Bold.ttf",
        ],
        italic=[
            "/usr/share/fonts/google-noto-vf/NotoSans-Italic[wght].ttf",
            "/usr/share/fonts/google-noto/NotoSans-Italic.ttf",
            "/usr/share/fonts/noto/NotoSans-Italic.ttf",
        ],
        bold_italic=[
            "/usr/share/fonts/google-noto-vf/NotoSans-Italic[wght].ttf",
            "/usr/share/fonts/google-noto/NotoSans-BoldItalic.ttf",
            "/usr/share/fonts/noto/NotoSans-BoldItalic.ttf",
        ],
    ),
    "noto-serif": FontFamily(
        name="noto-serif",
        display_name="Noto Serif",
        regular=[
            "/usr/share/fonts/google-noto-vf/NotoSerif[wght].ttf",
            "/usr/share/fonts/google-noto/NotoSerif-Regular.ttf",
            "/usr/share/fonts/noto/NotoSerif-Regular.ttf",
        ],
        bold=[
            "/usr/share/fonts/google-noto-vf/NotoSerif[wght].ttf",
            "/usr/share/fonts/google-noto/NotoSerif-Bold.ttf",
            "/usr/share/fonts/noto/NotoSerif-Bold.ttf",
        ],
        italic=[
            "/usr/share/fonts/google-noto-vf/NotoSerif-Italic[wght].ttf",
            "/usr/share/fonts/google-noto/NotoSerif-Italic.ttf",
            "/usr/share/fonts/noto/NotoSerif-Italic.ttf",
        ],
        bold_italic=[
            "/usr/share/fonts/google-noto-vf/NotoSerif-Italic[wght].ttf",
            "/usr/share/fonts/google-noto/NotoSerif-BoldItalic.ttf",
            "/usr/share/fonts/noto/NotoSerif-BoldItalic.ttf",
        ],
    ),
    "liberation-sans": FontFamily(
        name="liberation-sans",
        display_name="Liberation Sans",
        regular=[
            "/usr/share/fonts/liberation-sans/LiberationSans-Regular.ttf",
            "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ],
        bold=[
            "/usr/share/fonts/liberation-sans/LiberationSans-Bold.ttf",
            "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ],
        italic=[
            "/usr/share/fonts/liberation-sans/LiberationSans-Italic.ttf",
            "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        ],
        bold_italic=[
            "/usr/share/fonts/liberation-sans/LiberationSans-BoldItalic.ttf",
            "/usr/share/fonts/liberation-sans-fonts/LiberationSans-BoldItalic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
        ],
    ),
    "liberation-serif": FontFamily(
        name="liberation-serif",
        display_name="Liberation Serif",
        regular=[
            "/usr/share/fonts/liberation-serif/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        ],
        bold=[
            "/usr/share/fonts/liberation-serif/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        ],
        italic=[
            "/usr/share/fonts/liberation-serif/LiberationSerif-Italic.ttf",
            "/usr/share/fonts/liberation-serif-fonts/LiberationSerif-Italic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        ],
        bold_italic=[
            "/usr/share/fonts/liberation-serif/LiberationSerif-BoldItalic.ttf",
            "/usr/share/fonts/liberation-serif-fonts/LiberationSerif-BoldItalic.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
        ],
    ),
    "free-sans": FontFamily(
        name="free-sans",
        display_name="Free Sans",
        regular=[
            "/usr/share/fonts/gnu-free/FreeSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ],
        bold=[
            "/usr/share/fonts/gnu-free/FreeSansBold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        ],
        italic=[
            "/usr/share/fonts/gnu-free/FreeSansOblique.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf",
        ],
        bold_italic=[
            "/usr/share/fonts/gnu-free/FreeSansBoldOblique.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBoldOblique.ttf",
        ],
    ),
    "free-serif": FontFamily(
        name="free-serif",
        display_name="Free Serif",
        regular=[
            "/usr/share/fonts/gnu-free/FreeSerif.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
        ],
        bold=[
            "/usr/share/fonts/gnu-free/FreeSerifBold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
        ],
        italic=[
            "/usr/share/fonts/gnu-free/FreeSerifItalic.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf",
        ],
        bold_italic=[
            "/usr/share/fonts/gnu-free/FreeSerifBoldItalic.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf",
        ],
    ),
    "dejavu-sans": FontFamily(
        name="dejavu-sans",
        display_name="DejaVu Sans",
        regular=[
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "C:/Windows/Fonts/DejaVuSans.ttf",
        ],
        bold=[
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
            "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
        ],
        italic=[
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Oblique.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-Oblique.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-Oblique.ttf",
            "C:/Windows/Fonts/DejaVuSans-Oblique.ttf",
        ],
        bold_italic=[
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
            "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf",
            "/usr/share/fonts/dejavu/DejaVuSans-BoldOblique.ttf",
            "/usr/share/fonts/TTF/DejaVuSans-BoldOblique.ttf",
            "C:/Windows/Fonts/DejaVuSans-BoldOblique.ttf",
        ],
    ),
    "dejavu-serif": FontFamily(
        name="dejavu-serif",
        display_name="DejaVu Serif",
        regular=[
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/dejavu-serif-fonts/DejaVuSerif.ttf",
            "/usr/share/fonts/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/TTF/DejaVuSerif.ttf",
            "C:/Windows/Fonts/DejaVuSerif.ttf",
        ],
        bold=[
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/dejavu-serif-fonts/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/TTF/DejaVuSerif-Bold.ttf",
            "C:/Windows/Fonts/DejaVuSerif-Bold.ttf",
        ],
        italic=[
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf",
            "/usr/share/fonts/dejavu-serif-fonts/DejaVuSerif-Italic.ttf",
            "/usr/share/fonts/dejavu/DejaVuSerif-Italic.ttf",
            "/usr/share/fonts/TTF/DejaVuSerif-Italic.ttf",
            "C:/Windows/Fonts/DejaVuSerif-Italic.ttf",
        ],
        bold_italic=[
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf",
            "/usr/share/fonts/dejavu-serif-fonts/DejaVuSerif-BoldItalic.ttf",
            "/usr/share/fonts/dejavu/DejaVuSerif-BoldItalic.ttf",
            "/usr/share/fonts/TTF/DejaVuSerif-BoldItalic.ttf",
            "C:/Windows/Fonts/DejaVuSerif-BoldItalic.ttf",
        ],
    ),
}

LINK_COLOR = (0, 0, 180)


def find_font(paths: list[str]) -> Optional[str]:
    """Find first existing font from list of paths."""
    for path in paths:
        if Path(path).exists():
            return path
    return None


def is_variable_font(font_path: str) -> bool:
    """Check if font is a variable font by filename."""
    return "[wght]" in font_path


def get_font_families() -> dict[str, FontFamily]:
    """Get all available font families."""
    return FONT_FAMILIES


def find_available_fonts() -> list[str]:
    """Find all available font families in the system."""
    available = []
    for name, family in FONT_FAMILIES.items():
        if find_font(family.regular):
            available.append(name)
    return available


def get_default_font() -> str:
    """Get the first available font family name."""
    available = find_available_fonts()
    if not available:
        raise RuntimeError(
            "No Unicode fonts found. Please install one of the following:\n"
            "  - Noto Sans: sudo dnf install google-noto-sans-fonts\n"
            "  - Liberation Sans: sudo dnf install liberation-sans-fonts\n"
            "  - DejaVu Sans: sudo dnf install dejavu-sans-fonts\n"
            "  - Free Sans: sudo dnf install gnu-free-sans-fonts\n"
            "\nFor Debian/Ubuntu use 'apt install', for Arch use 'pacman -S'."
        )
    return available[0]


def get_font_family(name: Optional[str] = None) -> FontFamily:
    """Get font family by name or return default."""
    if name is None:
        name = get_default_font()

    if name not in FONT_FAMILIES:
        available = list(FONT_FAMILIES.keys())
        raise ValueError(
            f"Unknown font family '{name}'.\n"
            f"Available fonts: {', '.join(available)}\n"
            f"Use --list-fonts to see which fonts are available in your system."
        )

    family = FONT_FAMILIES[name]
    if not find_font(family.regular):
        raise RuntimeError(
            f"Font family '{name}' ({family.display_name}) is not installed.\n"
            f"Please install it or choose another font using --list-fonts."
        )

    return family


class ArticlePDF(FPDF):
    """Custom PDF class with Unicode font support."""

    def __init__(self, font_family_name: Optional[str] = None):
        super().__init__()
        self._custom_font_family = get_font_family(font_family_name)
        self._font_name = "UnicodeFont"
        self._setup_fonts()

    def _setup_fonts(self):
        """Setup Unicode fonts for Cyrillic support."""
        regular_font = find_font(self._custom_font_family.regular)
        bold_font = find_font(self._custom_font_family.bold)
        italic_font = find_font(self._custom_font_family.italic)
        bold_italic_font = find_font(self._custom_font_family.bold_italic)

        if not regular_font:
            raise RuntimeError(
                f"Font family '{self._custom_font_family.name}' "
                f"({self._custom_font_family.display_name}) "
                f"could not be loaded. The regular font file is missing.\n"
                f"Use --list-fonts to see available fonts."
            )

        self._add_font_with_variations(regular_font, "", FONT_WEIGHTS["regular"])
        if bold_font:
            self._add_font_with_variations(bold_font, "B", FONT_WEIGHTS["bold"])
        if italic_font:
            self._add_font_with_variations(italic_font, "I", FONT_WEIGHTS["italic"])
        if bold_italic_font:
            self._add_font_with_variations(
                bold_italic_font, "BI", FONT_WEIGHTS["bold_italic"]
            )

        self.set_font(self._font_name, size=12)

    def _add_font_with_variations(self, font_path: str, style: str, weight: int):
        """Add font with variable font support."""
        try:
            if is_variable_font(font_path):
                self.add_font(
                    self._font_name,
                    style,  # type: ignore[arg-type]
                    font_path,
                    variations={"wght": weight},  # pyright: ignore[reportCallIssue]
                )
            else:
                self.add_font(self._font_name, style, font_path)  # type: ignore[arg-type]
        except (TypeError, AttributeError):
            try:
                self.add_font(self._font_name, style, font_path)  # type: ignore[arg-type]
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Failed to add font {font_path} (style: {style}): {fallback_error}"
                ) from fallback_error

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font(self._font_name, size=8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


@registry.register
class PDFRenderer(BaseRenderer):
    """Renders Document to PDF format."""

    SUPPORTED_FEATURES = {"fonts", "images", "links"}

    @property
    def format_name(self) -> str:
        return "pdf"

    @property
    def file_extension(self) -> str:
        return ".pdf"

    def render(  # pylint: disable=protected-access
        self, document: Document, output_path: Path, options: Optional[RenderOptions] = None
    ) -> Path:
        """Render document to PDF file."""
        options = options or RenderOptions()
        output_path = Path(output_path)

        if output_path.suffix.lower() != ".pdf":
            output_path = output_path.with_suffix(".pdf")

        try:
            pdf = ArticlePDF(font_family_name=options.font_family)
        except (RuntimeError, ValueError) as e:
            raise RenderError(str(e)) from e

        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        effective_width = pdf.w - pdf.l_margin - pdf.r_margin

        # Title
        pdf.set_font(pdf._font_name, "B", 18)
        pdf.multi_cell(0, 10, document.metadata.title)
        pdf.ln(5)

        # Metadata
        meta_parts = []
        if document.metadata.authors:
            meta_parts.append(f"Authors: {', '.join(document.metadata.authors)}")
        if document.metadata.source_url:
            meta_parts.append(f"Source: {document.metadata.source_url}")

        if meta_parts:
            pdf.set_font(pdf._font_name, size=10)
            pdf.set_text_color(100, 100, 100)
            for meta in meta_parts:
                pdf.multi_cell(0, 6, meta)
                pdf.ln()
            pdf.set_text_color(0, 0, 0)
            pdf.ln(10)

        # Content blocks
        for block in document.blocks:
            if isinstance(block, HeadingBlock):
                pdf.ln(4)
                size = HEADING_SIZES.get(block.level, 12)
                pdf.set_font(pdf._font_name, "B", size)
                text = self._inline_to_text(block.content)
                pdf.multi_cell(0, 8, text)
                pdf.ln(2)
                pdf.set_font(pdf._font_name, size=12)

            elif isinstance(block, ParagraphBlock):
                pdf.set_font(pdf._font_name, size=12)
                self._write_inline_elements(pdf, block.content)
                pdf.ln(4)

            elif isinstance(block, ImageBlock):
                if options.include_images:
                    self._insert_image(pdf, block, effective_width)

            elif isinstance(block, HorizontalRuleBlock):
                pdf.ln(5)
                y = pdf.get_y()
                pdf.line(pdf.l_margin, y, pdf.w - pdf.r_margin, y)
                pdf.ln(5)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(output_path))

        return output_path

    def _inline_to_text(self, elements: list[InlineElement]) -> str:
        """Convert inline elements to plain text."""
        return "".join(elem.content for elem in elements)

    def _write_inline_elements(  # pylint: disable=protected-access
        self, pdf: ArticlePDF, elements: list[InlineElement]
    ):
        """Write inline elements with formatting to PDF."""
        for elem in elements:
            if elem.type == InlineType.BOLD:
                pdf.set_font(pdf._font_name, "B", 12)
            elif elem.type == InlineType.ITALIC:
                pdf.set_font(pdf._font_name, "I", 12)
            else:
                pdf.set_font(pdf._font_name, "", 12)

            if elem.type == InlineType.LINK and elem.url:
                pdf.set_text_color(*LINK_COLOR)
                pdf.write(7, elem.content, elem.url)
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.write(7, elem.content)

        pdf.ln()

    def _insert_image(
        self, pdf: ArticlePDF, block: ImageBlock, max_width: float
    ) -> None:
        """Insert image into PDF."""
        if not block.path or not block.path.exists():
            return

        try:
            width = block.width or 100
            height = block.height or 100

            img_width = min(width, max_width)
            scale = img_width / width
            img_height = height * scale

            if pdf.get_y() + img_height > pdf.h - pdf.b_margin:
                pdf.add_page()

            x = pdf.l_margin + (max_width - img_width) / 2
            pdf.image(str(block.path), x=x, w=img_width)
            pdf.ln(8)
        except Exception:
            pass
