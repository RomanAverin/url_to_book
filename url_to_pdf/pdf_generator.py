import re
from pathlib import Path
from typing import Optional

from fpdf import FPDF

from .extractor import ExtractedArticle
from .image_handler import DownloadedImage

HEADING_SIZES = {
    1: 16,
    2: 14,
    3: 13,
    4: 12,
    5: 11,
    6: 11,
}

DEJAVU_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "C:/Windows/Fonts/DejaVuSans.ttf",
]

DEJAVU_BOLD_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
]

DEJAVU_ITALIC_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Oblique.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Oblique.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-Oblique.ttf",
    "C:/Windows/Fonts/DejaVuSans-Oblique.ttf",
]

DEJAVU_BOLD_ITALIC_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    "/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-BoldOblique.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-BoldOblique.ttf",
    "/usr/share/fonts/TTF/DejaVuSans-BoldOblique.ttf",
    "C:/Windows/Fonts/DejaVuSans-BoldOblique.ttf",
]


def find_font(paths: list[str]) -> Optional[str]:
    """Find first existing font from list of paths."""
    for path in paths:
        if Path(path).exists():
            return path
    return None


class ArticlePDF(FPDF):
    def __init__(self):
        super().__init__()
        self.font_family_name = "DejaVu"
        self._setup_fonts()

    def _setup_fonts(self):
        """Setup Unicode fonts for Cyrillic support."""
        regular_font = find_font(DEJAVU_FONT_PATHS)
        bold_font = find_font(DEJAVU_BOLD_PATHS)
        italic_font = find_font(DEJAVU_ITALIC_PATHS)
        bold_italic_font = find_font(DEJAVU_BOLD_ITALIC_PATHS)

        if regular_font:
            self.add_font(self.font_family_name, "", regular_font)
            if bold_font:
                self.add_font(self.font_family_name, "B", bold_font)
            if italic_font:
                self.add_font(self.font_family_name, "I", italic_font)
            if bold_italic_font:
                self.add_font(self.font_family_name, "BI", bold_italic_font)
            self.set_font(self.font_family_name, size=12)
        else:
            self.font_family_name = "Helvetica"
            self.set_font("Helvetica", size=12)

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
) -> None:
    """Generate PDF from extracted article with images."""
    pdf = ArticlePDF()
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
    if article.publish_date:
        meta_parts.append(f"Date: {article.publish_date.strftime('%Y-%m-%d')}")
    meta_parts.append(f"Source: {article.source_url}")

    if meta_parts:
        pdf.set_font(pdf.font_family_name, size=10)
        pdf.set_text_color(100, 100, 100)
        for meta in meta_parts:
            pdf.multi_cell(0, 6, meta)
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)

    images_to_insert = list(images)

    if images_to_insert:
        top_img = images_to_insert.pop(0)
        _insert_image(pdf, top_img, effective_width)

    content_blocks = article.content if article.content else []
    paragraph_count = sum(1 for b in content_blocks if b.type == "paragraph")
    image_interval = max(1, paragraph_count // (len(images_to_insert) + 1)) if images_to_insert else 0
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
            if images_to_insert and image_interval > 0 and paragraph_idx % image_interval == 0:
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
            parts.append(("text", html_text[last_end:match.start()]))

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
            style = ("B" if bold else "") + ("I" if italic else "")
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
