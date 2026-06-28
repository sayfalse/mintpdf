"""
Formatter module for Mint PDF.
Parses structures like headings, code blocks, lists, and tables,
and formats them into ReportLab-compatible Flowables.
Supports nested list indentation and auto-wrapped, margin-fitting tables.
"""

import re
from typing import List, Any, Tuple
from pathlib import Path
from PIL import Image as PILImage # type: ignore

from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, KeepTogether, PageBreak # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore
from reportlab.lib.colors import HexColor # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT # type: ignore

from .theme_manager import Theme
from .template_manager import Template
from .font_manager import FontManager
from .logger import logger

def convert_markdown_inline(text: str) -> str:
    """
    Translates inline Markdown markers to ReportLab-supported XML tags.
    """
    # 1. Escape XML characters to avoid parsing errors
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    
    # 2. Bold: **text** or __text__
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"__(.*?)__", r"<b>\1</b>", text)
    
    # 3. Italic: *text* or _text_
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    text = re.sub(r"_(.*?)_", r"<i>\1</i>", text)
    
    # 4. Inline code: `code` (rendered in courier font)
    text = re.sub(r"`(.*?)`", r'<font face="Courier" color="#805AD5"><b>\1</b></font>', text)
    
    # 5. Hyperlinks: [text](url) -> <a href="url">text</a>
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2" color="#3182CE"><u>\1</u></a>', text)
    
    return text

def parse_markdown_table(table_lines: List[str]) -> Tuple[List[str], List[List[str]]]:
    """
    Parses raw Markdown table lines into headers and row cells.
    """
    headers = []
    rows = []
    
    for line in table_lines:
        line = line.strip()
        if not line.startswith("|") or not line.endswith("|"):
            continue
            
        parts = [p.strip() for p in line.split("|")[1:-1]]
        
        # Check if divider row (e.g. |---|---|)
        if all(re.match(r"^:?-+:?$", p) for p in parts):
            continue
            
        if not headers:
            headers = parts
        else:
            rows.append(parts)
            
    return headers, rows

def format_text_to_flowables(
    text: str,
    theme: Theme,
    template: Template,
    font_name: str = "Helvetica",
    page_width: float = 612.0 # Default Letter width
) -> List[Any]:
    """
    Parses raw text/markdown into structured ReportLab Flowables.
    Supports auto-wrapped table columns scaled to the page margins, 
    and multi-level indented lists.
    
    Args:
        text: Raw input text.
        theme: Selected visual theme.
        template: Selected template.
        font_name: Selected font family.
        page_width: Page width in points (default: 612.0).
        
    Returns:
        List of ReportLab flowable elements.
    """
    # Resolve safe font name
    font_name = FontManager.get_safe_font_name(font_name)
    logger.info(f"Formatting document structure using Template: {template.name}, Theme: {theme.name}, Font: {font_name} (safe)")
    
    styles = getSampleStyleSheet()
    flowables = []
    
    # Extract colors from theme
    c_primary = HexColor(theme.primary)
    c_secondary = HexColor(theme.secondary)
    c_accent = HexColor(theme.accent)
    c_text = HexColor(theme.text)
    
    # Calculate printable width based on template margins
    left_m = template.margins.get("left", 54.0)
    right_m = template.margins.get("right", 54.0)
    printable_width = page_width - left_m - right_m
    
    # Resolve typography sizes from template configuration
    body_sz = template.typography.get("body_font_size", 10.5)
    body_ld = template.typography.get("body_leading", 15.0)
    
    h1_sz = template.heading_styles.get("h1_size", 20.0)
    h1_ld = template.heading_styles.get("h1_leading", 24.0)
    
    h2_sz = template.heading_styles.get("h2_size", 15.0)
    h2_ld = template.heading_styles.get("h2_leading", 19.0)
    
    h3_sz = template.heading_styles.get("h3_size", 12.0)
    h3_ld = template.heading_styles.get("h3_leading", 16.0)

    # Define custom Typography Styles based on selected Font and Theme
    heading1_style = ParagraphStyle(
        'MintH1',
        parent=styles['Heading1'],
        fontName=f"{font_name}-Bold" if font_name in ["Helvetica", "Times-Roman"] else font_name,
        fontSize=h1_sz,
        leading=h1_ld,
        textColor=c_primary,
        spaceBefore=18,
        spaceAfter=10,
        keepWithNext=True
    )
    
    heading2_style = ParagraphStyle(
        'MintH2',
        parent=styles['Heading2'],
        fontName=f"{font_name}-Bold" if font_name in ["Helvetica", "Times-Roman"] else font_name,
        fontSize=h2_sz,
        leading=h2_ld,
        textColor=c_secondary,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )
    
    heading3_style = ParagraphStyle(
        'MintH3',
        parent=styles['Heading3'],
        fontName=f"{font_name}-Bold" if font_name in ["Helvetica", "Times-Roman"] else font_name,
        fontSize=h3_sz,
        leading=h3_ld,
        textColor=c_accent,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'MintBody',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=body_sz,
        leading=body_ld,
        textColor=c_text,
        spaceAfter=10,
        alignment=TA_LEFT
    )
    
    quote_style = ParagraphStyle(
        'MintQuote',
        parent=styles['Normal'],
        fontName=f"{font_name}-Oblique" if font_name in ["Helvetica", "Times-Roman"] else font_name,
        fontSize=body_sz - 0.5,
        leading=body_ld - 1.0,
        textColor=HexColor("#4A5568"),
        leftIndent=24,
        rightIndent=12,
        spaceBefore=8,
        spaceAfter=8
    )
    
    code_style = ParagraphStyle(
        'MintCode',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=body_sz - 1.5,
        leading=body_ld - 3.0,
        textColor=HexColor("#1A202C"),
        spaceAfter=0
    )
    
    lines = text.splitlines()
    i = 0
    total_lines = len(lines)
    
    while i < total_lines:
        line = lines[i]
        line_stripped = line.strip()
        
        # Skip empty lines
        if not line_stripped:
            i += 1
            continue
            
        # 1. Code Block parsing (```)
        if line_stripped.startswith("```"):
            code_lines = []
            i += 1
            while i < total_lines and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1 # skip closing ```
            
            code_content = "\n".join(code_lines)
            escaped_code = convert_markdown_inline(code_content)
            
            p_code = Paragraph(escaped_code.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style)
            tbl = Table([[p_code]], colWidths=[printable_width])
            tbl.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), HexColor("#F7FAFC")),
                ('BOX', (0,0), (-1,-1), 0.5, HexColor(theme.border)),
                ('PADDING', (0,0), (-1,-1), 8),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            flowables.append(tbl)
            flowables.append(Spacer(1, 10))
            continue
            
        # 2. Table parsing (|) with auto-wrapping Paragraph cells scaled to printable width
        if line_stripped.startswith("|"):
            table_lines = []
            while i < total_lines and lines[i].strip().startswith("|"):
                table_lines.append(lines[i])
                i += 1
                
            try:
                headers, rows = parse_markdown_table(table_lines)
                if headers:
                    table_data = []
                    
                    # Style headers
                    header_row = []
                    for h in headers:
                        h_formatted = convert_markdown_inline(h)
                        header_row.append(Paragraph(f"<b>{h_formatted}</b>", ParagraphStyle('TH', parent=body_style, textColor=HexColor("#FFFFFF"))))
                    table_data.append(header_row)
                    
                    # Style rows
                    for r in rows:
                        row_cells = []
                        for cell in r:
                            cell_formatted = convert_markdown_inline(cell)
                            row_cells.append(Paragraph(cell_formatted, body_style))
                        while len(row_cells) < len(headers):
                            row_cells.append(Paragraph("", body_style))
                        table_data.append(row_cells[:len(headers)])
                        
                    # Divide printable width evenly among columns
                    col_width = printable_width / len(headers)
                    t_flowable = Table(table_data, colWidths=[col_width] * len(headers))
                    
                    t_flowable.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), c_primary),
                        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                        ('VALIGN', (0,0), (-1,-1), 'TOP'),
                        ('GRID', (0,0), (-1,-1), 0.5, HexColor(theme.border)),
                        ('PADDING', (0,0), (-1,-1), 6),
                        ('ROWBACKGROUNDS', (0,1), (-1,-1), [HexColor("#FFFFFF"), HexColor(theme.table_row_alt)]),
                    ]))
                    flowables.append(t_flowable)
                    flowables.append(Spacer(1, 12))
            except Exception as e:
                logger.error(f"Error compiling table: {e}", exc_info=True)
            continue
            
        # 3. Blockquotes (>)
        if line_stripped.startswith(">"):
            quote_lines = []
            while i < total_lines and lines[i].strip().startswith(">"):
                quote_text = lines[i].strip()[1:].strip()
                quote_lines.append(quote_text)
                i += 1
                
            quote_content = " ".join(quote_lines)
            formatted_quote = convert_markdown_inline(quote_content)
            
            p_quote = Paragraph(formatted_quote, quote_style)
            tbl = Table([[p_quote]], colWidths=[printable_width - 10.0])
            tbl.setStyle(TableStyle([
                ('LINELEFT', (0,0), (0,-1), 3.0, c_accent),
                ('BACKGROUND', (0,0), (-1,-1), HexColor("#FAF5FF") if theme.name == "Purple" else HexColor("#F7FAFC")),
                ('PADDING', (0,0), (-1,-1), 6),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ]))
            flowables.append(tbl)
            flowables.append(Spacer(1, 10))
            continue
            
        # 4. Heading 1 (#)
        if line_stripped.startswith("# "):
            title_text = line_stripped[2:].strip()
            formatted_title = convert_markdown_inline(title_text)
            flowables.append(Paragraph(formatted_title, heading1_style))
            i += 1
            continue
            
        # 5. Heading 2 (##)
        if line_stripped.startswith("## "):
            title_text = line_stripped[3:].strip()
            formatted_title = convert_markdown_inline(title_text)
            flowables.append(Paragraph(formatted_title, heading2_style))
            i += 1
            continue
            
        # 6. Heading 3 (###)
        if line_stripped.startswith("### "):
            title_text = line_stripped[4:].strip()
            formatted_title = convert_markdown_inline(title_text)
            flowables.append(Paragraph(formatted_title, heading3_style))
            i += 1
            continue

        # 7. Images (![alt](path))
        if line_stripped.startswith("!["):
            img_match = re.match(r"^!\[(.*?)\]\((.*?)\)$", line_stripped)
            if img_match:
                alt_text = img_match.group(1)
                img_path_str = img_match.group(2)
                img_path = Path(img_path_str)
                
                if img_path.exists() and img_path.is_file():
                    try:
                        with PILImage.open(img_path) as pil_img:
                            w, h = pil_img.size
                        max_w = min(400.0, printable_width)
                        scale = min(1.0, max_w / w)
                        img_w = w * scale
                        img_h = h * scale
                        
                        flowables.append(Image(str(img_path), width=img_w, height=img_h))
                        if alt_text:
                            caption_style = ParagraphStyle(
                                'Caption',
                                parent=body_style,
                                fontName=f"{font_name}-Oblique" if font_name in ["Helvetica", "Times-Roman"] else font_name,
                                fontSize=body_sz - 1.5,
                                alignment=TA_CENTER,
                                textColor=HexColor("#718096")
                            )
                            flowables.append(Paragraph(alt_text, caption_style))
                        flowables.append(Spacer(1, 10))
                    except Exception as e:
                        logger.error(f"Failed to format image {img_path}: {e}")
                        flowables.append(Paragraph(f"[Image Error: {alt_text} ({img_path.name})]", body_style))
                else:
                    flowables.append(Paragraph(f"[Image File Not Found: {img_path_str}]", body_style))
                    
                i += 1
                continue

        # 8. Lists (Bullet and numbered lists) with Nested Indentation level tracking
        # We match on original unstripped line 'line' to preserve leading whitespace indents
        bullet_match = re.match(r"^(\s*)[-\*\+]\s+(.+)$", line)
        num_match = re.match(r"^(\s*)\d+\.\s+(.+)$", line)
        
        if bullet_match or num_match:
            list_flowables = []
            while i < total_lines:
                curr_line = lines[i]
                b_match = re.match(r"^(\s*)[-\*\+]\s+(.+)$", curr_line)
                n_match = re.match(r"^(\s*)\d+\.\s+(.+)$", curr_line)
                
                if not (b_match or n_match):
                    break
                    
                if b_match:
                    indent_spaces = len(b_match.group(1))
                    bullet_char = "&bull;"
                    content_text = b_match.group(2).strip()
                else:
                    indent_spaces = len(n_match.group(1))
                    bullet_char = f"{n_match.group(2)}." # wait! let's verify regex groups!
                    # regex is ^(\s*)\d+\.\s+(.+)$
                    # group 1 = spaces, group 2 = content text
                    # We also need the number from match! Let's get actual raw match to extract number
                    raw_num_match = re.match(r"^(\s*)(\d+)\.\s+(.+)$", curr_line)
                    bullet_char = f"{raw_num_match.group(2)}." if raw_num_match else "1."
                    content_text = raw_num_match.group(3).strip() if raw_num_match else ""
                    
                # Determine nested indent level: 2 spaces or 4 spaces standard
                level = indent_spaces // 2
                list_left_indent = 15 + (level * 15)
                
                formatted_item = convert_markdown_inline(content_text)
                
                list_item_style = ParagraphStyle(
                    f'MintListItem_L{level}',
                    parent=body_style,
                    leftIndent=list_left_indent,
                    firstLineIndent=-12,
                    spaceAfter=4
                )
                
                list_flowables.append(Paragraph(f"{bullet_char} {formatted_item}", list_item_style))
                i += 1
                
            flowables.extend(list_flowables)
            flowables.append(Spacer(1, 6))
            continue

        # 9. Default Paragraph block
        paragraph_lines = []
        while i < total_lines:
            curr_stripped = lines[i].strip()
            # Stop conditions for paragraph grouping
            if not curr_stripped:
                break
            if curr_stripped.startswith("#"):
                break
            if curr_stripped.startswith(">"):
                break
            if curr_stripped.startswith("|"):
                break
            if curr_stripped.startswith("```"):
                break
            if re.match(r"^(\s*)[-\*\+]\s+", lines[i]) or re.match(r"^(\s*)\d+\.\s+", lines[i]):
                break
                
            paragraph_lines.append(curr_stripped)
            i += 1
            
        paragraph_text = " ".join(paragraph_lines)
        formatted_para = convert_markdown_inline(paragraph_text)
        flowables.append(Paragraph(formatted_para, body_style))
        flowables.append(Spacer(1, 8))

    return flowables
