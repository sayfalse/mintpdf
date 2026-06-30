import re
from pathlib import Path
from typing import Any, List

from PIL import Image as PILImage  # type: ignore
from reportlab.lib.colors import HexColor  # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_LEFT  # type: ignore
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet  # type: ignore
from reportlab.platypus import (  # type: ignore
    Image as RLImage,
)
from reportlab.platypus import (
    Paragraph as RLParagraph,
)
from reportlab.platypus import (
    Spacer,
    TableStyle,
)
from reportlab.platypus import (
    Table as RLTable,
)

from ..domain.models import (
    CodeBlock,
    Document,
    Heading,
    Image,
    Paragraph,
    Quote,
    Table,
    Template,
    Theme,
)
from ..font_manager import FontManager
from ..formatter import convert_markdown_inline
from ..logger import logger


class Renderer:
    """Stage 4: Renderer. Converts domain document elements into ReportLab Flowables."""

    def render(
        self,
        document: Document,
        theme: Theme,
        template: Template,
        font_name: str = "Helvetica",
        page_width: float = 612.0,
    ) -> List[Any]:
        font_name = FontManager.get_safe_font_name(font_name)
        logger.info(
            f"Rendering document elements using Template: {template.name}, Theme: {theme.name}, Font: {font_name}"
        )

        styles = getSampleStyleSheet()
        flowables: List[Any] = []

        # Extract colors from theme
        c_primary = HexColor(theme.primary)
        c_secondary = HexColor(theme.secondary)
        c_accent = HexColor(theme.accent)
        c_text = HexColor(theme.text)

        # Calculate printable width based on template margins
        margins = template.margins or {}
        left_m = margins.get("left", 54.0)
        right_m = margins.get("right", 54.0)
        printable_width = page_width - left_m - right_m

        # Resolve typography sizes from template configuration
        typography = template.typography or {}
        body_sz = typography.get("body_font_size", 10.5)
        body_ld = typography.get("body_leading", 15.0)

        heading_styles = template.heading_styles or {}
        h1_sz = heading_styles.get("h1_size", 20.0)
        h1_ld = heading_styles.get("h1_leading", 24.0)
        h2_sz = heading_styles.get("h2_size", 15.0)
        h2_ld = heading_styles.get("h2_leading", 19.0)
        h3_sz = heading_styles.get("h3_size", 12.0)
        h3_ld = heading_styles.get("h3_leading", 16.0)

        # Define custom Typography Styles based on selected Font and Theme
        heading1_style = ParagraphStyle(
            "MintH1",
            parent=styles["Heading1"],
            fontName=(
                f"{font_name}-Bold" if font_name in ["Helvetica", "Times-Roman"] else font_name
            ),
            fontSize=h1_sz,
            leading=h1_ld,
            textColor=c_primary,
            spaceBefore=18,
            spaceAfter=10,
            keepWithNext=True,
        )

        heading2_style = ParagraphStyle(
            "MintH2",
            parent=styles["Heading2"],
            fontName=(
                f"{font_name}-Bold" if font_name in ["Helvetica", "Times-Roman"] else font_name
            ),
            fontSize=h2_sz,
            leading=h2_ld,
            textColor=c_secondary,
            spaceBefore=14,
            spaceAfter=8,
            keepWithNext=True,
        )

        heading3_style = ParagraphStyle(
            "MintH3",
            parent=styles["Heading3"],
            fontName=(
                f"{font_name}-Bold" if font_name in ["Helvetica", "Times-Roman"] else font_name
            ),
            fontSize=h3_sz,
            leading=h3_ld,
            textColor=c_accent,
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True,
        )

        body_style = ParagraphStyle(
            "MintBody",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=body_sz,
            leading=body_ld,
            textColor=c_text,
            spaceAfter=10,
            alignment=TA_LEFT,
        )

        quote_style = ParagraphStyle(
            "MintQuote",
            parent=styles["Normal"],
            fontName=(
                f"{font_name}-Oblique" if font_name in ["Helvetica", "Times-Roman"] else font_name
            ),
            fontSize=body_sz - 0.5,
            leading=body_ld - 1.0,
            textColor=HexColor("#4A5568"),
            leftIndent=24,
            rightIndent=12,
            spaceBefore=8,
            spaceAfter=8,
        )

        code_style = ParagraphStyle(
            "MintCode",
            parent=styles["Code"],
            fontName="Courier",
            fontSize=body_sz - 1.5,
            leading=body_ld - 3.0,
            textColor=HexColor("#1A202C"),
            spaceAfter=0,
        )

        for section in document.sections:
            for element in section.elements:
                # 1. Code Block
                if isinstance(element, CodeBlock):
                    escaped_code = convert_markdown_inline(element.code)
                    p_code = RLParagraph(
                        escaped_code.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style
                    )
                    tbl = RLTable([[p_code]], colWidths=[printable_width])
                    tbl.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F7FAFC")),
                                ("BOX", (0, 0), (-1, -1), 0.5, HexColor(theme.border)),
                                ("PADDING", (0, 0), (-1, -1), 8),
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ]
                        )
                    )
                    flowables.append(tbl)
                    flowables.append(Spacer(1, 10))

                # 2. Table
                elif isinstance(element, Table):
                    headers = element.headers
                    rows = element.rows
                    try:
                        table_data = []

                        # Style headers
                        header_row = []
                        for h in headers:
                            h_formatted = convert_markdown_inline(h)
                            header_row.append(
                                RLParagraph(
                                    f"<b>{h_formatted}</b>",
                                    ParagraphStyle(
                                        "TH", parent=body_style, textColor=HexColor("#FFFFFF")
                                    ),
                                )
                            )
                        table_data.append(header_row)

                        # Style rows
                        for r in rows:
                            row_cells = []
                            for cell in r:
                                cell_formatted = convert_markdown_inline(cell)
                                row_cells.append(RLParagraph(cell_formatted, body_style))
                            while len(row_cells) < len(headers):
                                row_cells.append(RLParagraph("", body_style))
                            table_data.append(row_cells[: len(headers)])

                        # Divide printable width evenly among columns
                        col_width = printable_width / len(headers)
                        t_flowable = RLTable(table_data, colWidths=[col_width] * len(headers))

                        t_flowable.setStyle(
                            TableStyle(
                                [
                                    ("BACKGROUND", (0, 0), (-1, 0), c_primary),
                                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                    ("GRID", (0, 0), (-1, -1), 0.5, HexColor(theme.border)),
                                    ("PADDING", (0, 0), (-1, -1), 6),
                                    (
                                        "ROWBACKGROUNDS",
                                        (0, 1),
                                        (-1, -1),
                                        [HexColor("#FFFFFF"), HexColor(theme.table_row_alt)],
                                    ),
                                ]
                            )
                        )
                        flowables.append(t_flowable)
                        flowables.append(Spacer(1, 12))
                    except Exception as e:
                        logger.error(f"Error compiling table: {e}", exc_info=True)

                # 3. Blockquotes
                elif isinstance(element, Quote):
                    formatted_quote = convert_markdown_inline(element.text)
                    p_quote = RLParagraph(formatted_quote, quote_style)
                    tbl = RLTable([[p_quote]], colWidths=[printable_width - 10.0])
                    tbl.setStyle(
                        TableStyle(
                            [
                                ("LINELEFT", (0, 0), (0, -1), 3.0, c_accent),
                                (
                                    "BACKGROUND",
                                    (0, 0),
                                    (-1, -1),
                                    (
                                        HexColor("#FAF5FF")
                                        if theme.name == "Purple"
                                        else HexColor("#F7FAFC")
                                    ),
                                ),
                                ("PADDING", (0, 0), (-1, -1), 6),
                                ("TOPPADDING", (0, 0), (-1, -1), 2),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                            ]
                        )
                    )
                    flowables.append(tbl)
                    flowables.append(Spacer(1, 10))

                # 4. Heading
                elif isinstance(element, Heading):
                    formatted_title = convert_markdown_inline(element.text)
                    if element.level == 1:
                        flowables.append(RLParagraph(formatted_title, heading1_style))
                    elif element.level == 2:
                        flowables.append(RLParagraph(formatted_title, heading2_style))
                    else:
                        flowables.append(RLParagraph(formatted_title, heading3_style))

                # 5. Image
                elif isinstance(element, Image):
                    img_path = Path(element.path)
                    if img_path.exists() and img_path.is_file():
                        try:
                            with PILImage.open(img_path) as pil_img:
                                img_width, img_height = pil_img.size
                            max_w = min(400.0, printable_width)
                            scale = min(1.0, max_w / img_width)
                            img_w = img_width * scale
                            img_h = img_height * scale

                            flowables.append(RLImage(str(img_path), width=img_w, height=img_h))
                            if element.caption:
                                caption_style = ParagraphStyle(
                                    "Caption",
                                    parent=body_style,
                                    fontName=(
                                        f"{font_name}-Oblique"
                                        if font_name in ["Helvetica", "Times-Roman"]
                                        else font_name
                                    ),
                                    fontSize=body_sz - 1.5,
                                    alignment=TA_CENTER,
                                    textColor=HexColor("#718096"),
                                )
                                flowables.append(RLParagraph(element.caption, caption_style))
                            flowables.append(Spacer(1, 10))
                        except Exception as e:
                            logger.error(f"Failed to format image {img_path}: {e}")
                            flowables.append(
                                RLParagraph(
                                    f"[Image Error: {element.caption} ({img_path.name})]",
                                    body_style,
                                )
                            )
                    else:
                        flowables.append(
                            RLParagraph(f"[Image File Not Found: {element.path}]", body_style)
                        )

                # 6. Paragraph (can be normal or lists)
                elif isinstance(element, Paragraph):
                    line = element.text
                    bullet_match = re.match(r"^(\s*)[-\*\+]\s+(.+)$", line)
                    num_match = re.match(r"^(\s*)\d+\.\s+(.+)$", line)

                    if bullet_match or num_match:
                        # Extract list content
                        if bullet_match is not None:
                            indent_spaces = len(bullet_match.group(1))
                            bullet_char = "&bull;"
                            content_text = bullet_match.group(2).strip()
                        else:
                            assert num_match is not None
                            indent_spaces = len(num_match.group(1))
                            raw_num_match = re.match(r"^(\s*)(\d+)\.\s+(.+)$", line)
                            bullet_char = f"{raw_num_match.group(2)}." if raw_num_match else "1."
                            content_text = raw_num_match.group(3).strip() if raw_num_match else ""

                        level = indent_spaces // 2
                        list_left_indent = 15 + (level * 15)

                        formatted_item = convert_markdown_inline(content_text)

                        list_item_style = ParagraphStyle(
                            f"MintListItem_L{level}",
                            parent=body_style,
                            leftIndent=list_left_indent,
                            firstLineIndent=-12,
                            spaceAfter=4,
                        )

                        flowables.append(
                            RLParagraph(f"{bullet_char} {formatted_item}", list_item_style)
                        )
                    else:
                        # Normal Paragraph
                        formatted_para = convert_markdown_inline(element.text)
                        flowables.append(RLParagraph(formatted_para, body_style))
                        flowables.append(Spacer(1, 8))

        return flowables
