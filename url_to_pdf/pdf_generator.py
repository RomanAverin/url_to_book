import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from fpdf import FPDF

from .extractor import ExtractedArticle
from .image_handler import DownloadedImage


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

# Font weight values for variable fonts
FONT_WEIGHTS = {
    "regular": 400,      # Normal weight
    "bold": 700,         # Bold weight
    "italic": 400,       # Italic uses regular weight
    "bold_italic": 700,  # Bold italic uses bold weight
}

# Font families with Unicode/Cyrillic support
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


def find_font(paths: list[str]) -> Optional[str]:
    """Find first existing font from list of paths."""
    for path in paths:
        if Path(path).exists():
            return path
    return None


def is_variable_font(font_path: str) -> bool:
    """Check if font is a variable font by filename.

    Variable fonts contain axis variations (e.g., [wght], [wdth]) in their names.

    Args:
        font_path: Path to the font file.

    Returns:
        True if the font is a variable font, False otherwise.
    """
    return "[wght]" in font_path


def get_font_families() -> dict[str, FontFamily]:
    """Get all available font families."""
    return FONT_FAMILIES


def find_available_fonts() -> list[str]:
    """Find all available font families in the system.

    Returns:
        List of font family names that are available in the system.
    """
    available = []
    for name, family in FONT_FAMILIES.items():
        if find_font(family.regular):
            available.append(name)
    return available


def get_default_font() -> str:
    """Get the first available font family name.

    Returns:
        Name of the first available font family.

    Raises:
        RuntimeError: If no fonts are available.
    """
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
    """Get font family by name or return default.

    Args:
        name: Font family name (e.g., 'noto-sans'). If None, returns default.

    Returns:
        FontFamily object for the requested font.

    Raises:
        ValueError: If the font family name is not found.
        RuntimeError: If the requested font is not available in the system.
    """
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
    def __init__(self, font_family_name: Optional[str] = None):
        """Initialize PDF with specified font family.

        Args:
            font_family_name: Name of the font family to use (e.g., 'noto-sans').
                            If None, uses the first available font.
        """
        super().__init__()
        self.font_family = get_font_family(font_family_name)
        self.font_family_name = "UnicodeFont"  # Internal name for FPDF
        self._setup_fonts()

    def _setup_fonts(self):
        """Setup Unicode fonts for Cyrillic support."""
        regular_font = find_font(self.font_family.regular)
        bold_font = find_font(self.font_family.bold)
        italic_font = find_font(self.font_family.italic)
        bold_italic_font = find_font(self.font_family.bold_italic)

        if not regular_font:
            raise RuntimeError(
                f"Font family '{self.font_family.name}' ({self.font_family.display_name}) "
                f"could not be loaded. The regular font file is missing.\n"
                f"Use --list-fonts to see available fonts."
            )

        # Add regular font
        self._add_font_with_variations(regular_font, "", FONT_WEIGHTS["regular"])

        # Add bold font if available
        if bold_font:
            self._add_font_with_variations(bold_font, "B", FONT_WEIGHTS["bold"])

        # Add italic font if available
        if italic_font:
            self._add_font_with_variations(italic_font, "I", FONT_WEIGHTS["italic"])

        # Add bold-italic font if available
        if bold_italic_font:
            self._add_font_with_variations(bold_italic_font, "BI", FONT_WEIGHTS["bold_italic"])

        self.set_font(self.font_family_name, size=12)

    def _add_font_with_variations(self, font_path: str, style: str, weight: int):
        """Add font with variable font support.

        For variable fonts (with [wght] in filename), adds the 'variations' parameter
        to specify the weight. For regular TTF fonts, adds them normally.

        Args:
            font_path: Path to the font file.
            style: Font style ("" for regular, "B" for bold, "I" for italic, "BI" for bold-italic).
            weight: Font weight value (e.g., 400 for regular, 700 for bold).
        """
        try:
            if is_variable_font(font_path):
                # Variable font: use variations parameter
                self.add_font(
                    self.font_family_name,
                    style,
                    font_path,
                    variations={"wght": weight}
                )
            else:
                # Regular TTF: add without variations
                self.add_font(self.font_family_name, style, font_path)
        except (TypeError, AttributeError):
            # Fallback: try adding without variations if there's an error
            # This handles cases where variations parameter is not supported
            try:
                self.add_font(self.font_family_name, style, font_path)
            except Exception as fallback_error:
                raise RuntimeError(
                    f"Failed to add font {font_path} (style: {style}): {fallback_error}"
                ) from fallback_error

    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family_name, size=8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


def generate_pdf(
    article: ExtractedArticle,
    images: list[DownloadedImage],
    output_path: str,
    custom_title: Optional[str] = None,
    font_family: Optional[str] = None,
) -> None:
    """Generate PDF from extracted article with images.

    Args:
        article: Extracted article data.
        images: List of downloaded images.
        output_path: Path where to save the PDF file.
        custom_title: Optional custom title for the PDF.
        font_family: Optional font family name (e.g., 'noto-sans').
                    If None, uses the first available font.
    """
    pdf = ArticlePDF(font_family_name=font_family)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    effective_width = pdf.w - pdf.l_margin - pdf.r_margin

    title = custom_title or article.title
    pdf.set_font(pdf.font_family_name, "B", 18)
    pdf.multi_cell(0, 10, title)
    pdf.ln(5)

    meta_parts = []
    if article.authors:
        meta_parts.append(f"Authors: {', '.join(article.authors)}")
    meta_parts.append(f"Source: {article.source_url}")

    if meta_parts:
        pdf.set_font(pdf.font_family_name, size=10)
        pdf.set_text_color(100, 100, 100)
        for meta in meta_parts:
            pdf.multi_cell(0, 6, meta)
            pdf.ln()
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)

    images_to_insert = list(images)

    if images_to_insert:
        top_img = images_to_insert.pop(0)
        _insert_image(pdf, top_img, effective_width)

    content_blocks = article.content if article.content else []
    paragraph_count = sum(1 for b in content_blocks if b.type == "paragraph")
    image_interval = (
        max(1, paragraph_count // (len(images_to_insert) + 1))
        if images_to_insert
        else 0
    )
    paragraph_idx = 0

    for block in content_blocks:
        if block.type == "heading":
            pdf.ln(4)
            size = HEADING_SIZES.get(block.level, 12)
            pdf.set_font(pdf.font_family_name, "B", size)
            pdf.multi_cell(0, 8, block.text)
            pdf.ln(2)
            pdf.set_font(pdf.font_family_name, size=12)
        else:
            pdf.set_font(pdf.font_family_name, size=12)
            content = block.html if block.html else block.text
            _write_formatted_text(pdf, content)
            pdf.ln(4)

            paragraph_idx += 1
            if (
                images_to_insert
                and image_interval > 0
                and paragraph_idx % image_interval == 0
            ):
                img = images_to_insert.pop(0)
                _insert_image(pdf, img, effective_width)

    for img in images_to_insert:
        _insert_image(pdf, img, effective_width)

    pdf.output(output_path)


LINK_COLOR = (0, 0, 180)  # Blue for links


def _write_formatted_text(pdf: ArticlePDF, html_text: str) -> None:
    """Write text with bold/italic/link formatting from HTML tags."""
    tag_pattern = re.compile(r'<(/?)([biu])>|<a href="([^"]+)">|</a>', re.IGNORECASE)

    parts = []
    last_end = 0
    for match in tag_pattern.finditer(html_text):
        if match.start() > last_end:
            parts.append(("text", html_text[last_end : match.start()]))

        if match.group(0) == "</a>":
            parts.append(("end_link", None))
        elif match.group(3):
            parts.append(("start_link", match.group(3)))
        elif match.group(1) == "/":
            parts.append(("end_" + match.group(2).lower(), None))
        else:
            parts.append(("start_" + match.group(2).lower(), None))

        last_end = match.end()

    if last_end < len(html_text):
        parts.append(("text", html_text[last_end:]))

    bold = False
    italic = False
    link_url = None

    for part_type, value in parts:
        if part_type == "text" and value:
            if bold and italic:
                style = "BI"
            elif bold:
                style = "B"
            elif italic:
                style = "I"
            else:
                style = ""
            pdf.set_font(pdf.font_family_name, style, 12)

            if link_url:
                pdf.set_text_color(*LINK_COLOR)
                pdf.write(7, value, link_url)
                pdf.set_text_color(0, 0, 0)
            else:
                pdf.write(7, value)
        elif part_type == "start_b":
            bold = True
        elif part_type == "end_b":
            bold = False
        elif part_type == "start_i":
            italic = True
        elif part_type == "end_i":
            italic = False
        elif part_type == "start_link":
            link_url = value
        elif part_type == "end_link":
            link_url = None

    pdf.ln()


def _insert_image(pdf: ArticlePDF, img: DownloadedImage, max_width: float) -> None:
    """Insert image into PDF, scaling to fit page width."""
    try:
        img_width = min(img.width, max_width)
        scale = img_width / img.width
        img_height = img.height * scale

        if pdf.get_y() + img_height > pdf.h - pdf.b_margin:
            pdf.add_page()

        x = pdf.l_margin + (max_width - img_width) / 2
        pdf.image(str(img.path), x=x, w=img_width)
        pdf.ln(8)
    except Exception:
        pass
