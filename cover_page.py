"""
Cover Page generator module for Mint PDF.
Provides layout blocks (Flowables) for professional front cover pages.
"""

from typing import List, Any
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle # type: ignore
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle # type: ignore
from reportlab.lib.colors import HexColor # type: ignore

from metadata import DocumentMetadata
from theme_manager import Theme

def create_cover_page(metadata: DocumentMetadata, theme: Theme) -> List[Any]:
    """
    Creates flowable elements representing a beautifully styled front cover page.
    Uses colors from the selected Theme to build matching banners and borders.
    
    Args:
        metadata: DocumentMetadata containing title, subtitle, author, etc.
        theme: Selected visual Theme with color definitions.
        
    Returns:
        List of ReportLab flowable elements.
    """
    story = []
    styles = getSampleStyleSheet()
    
    c_primary = HexColor(theme.primary)
    c_secondary = HexColor(theme.secondary)
    c_accent = HexColor(theme.accent)
    c_text = HexColor(theme.text)
    
    # 1. Title Box Style (Solid colored top bar)
    title_banner_style = ParagraphStyle(
        'CoverTitleText',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=28,
        leading=34,
        textColor=HexColor("#FFFFFF"),
        alignment=0 # Left aligned
    )
    
    # Create the title block
    p_title = Paragraph(metadata.title, title_banner_style)
    
    # Wrap in a banner table with primary theme background
    banner_table = Table([[p_title]], colWidths=[450])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_primary),
        ('PADDING', (0,0), (-1,-1), 24),
        ('BOTTOMPADDING', (0,0), (-1,-1), 32),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    story.append(Spacer(1, 40))
    story.append(banner_table)
    
    # 2. Accent bar
    accent_bar = Table([[""]], colWidths=[450], rowHeights=[4])
    accent_bar.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), c_accent),
        ('PADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(accent_bar)
    story.append(Spacer(1, 25))
    
    # 3. Subtitle
    if metadata.subtitle:
        subtitle_style = ParagraphStyle(
            'CoverSubtitleText',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=15,
            leading=20,
            textColor=c_secondary,
            spaceAfter=20
        )
        story.append(Paragraph(metadata.subtitle, subtitle_style))
        
    # Main abstract / description if provided
    if metadata.description:
        desc_style = ParagraphStyle(
            'CoverDescText',
            parent=styles['Normal'],
            fontName='Helvetica-Oblique',
            fontSize=10.5,
            leading=15,
            textColor=HexColor("#4A5568"),
            spaceAfter=20
        )
        story.append(Spacer(1, 10))
        story.append(Paragraph(metadata.description, desc_style))
        
    # Spacer pushing metadata to the bottom
    story.append(Spacer(1, 180))
    
    # 4. Metadata Details Block
    meta_label_style = ParagraphStyle(
        'CoverMetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=c_primary
    )
    
    meta_val_style = ParagraphStyle(
        'CoverMetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=c_text
    )
    
    meta_rows = []
    if metadata.author:
        meta_rows.append([Paragraph("AUTHOR", meta_label_style), Paragraph(metadata.author, meta_val_style)])
    if metadata.organization:
        meta_rows.append([Paragraph("ORGANIZATION", meta_label_style), Paragraph(metadata.organization, meta_val_style)])
    if metadata.date:
        meta_rows.append([Paragraph("DATE", meta_label_style), Paragraph(metadata.date, meta_val_style)])
    if metadata.version:
        meta_rows.append([Paragraph("VERSION", meta_label_style), Paragraph(metadata.version, meta_val_style)])
        
    if meta_rows:
        meta_table = Table(meta_rows, colWidths=[120, 330])
        meta_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, HexColor("#E2E8F0")),
        ]))
        story.append(meta_table)
        
    story.append(PageBreak())
    return story
