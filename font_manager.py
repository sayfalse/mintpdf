"""
Font Manager module for Mint PDF.
Handles registration of standard and custom fonts for ReportLab.
"""

from typing import List, Dict, Any
from pathlib import Path
from reportlab.pdfbase import pdfmetrics # type: ignore
from reportlab.pdfbase.ttfonts import TTFont # type: ignore

from logger import logger

FONTS_DIR = Path("fonts")

class FontManager:
    """Manages system and custom fonts for PDF generation."""
    
    SUPPORTED_FONTS = [
        "Times New Roman",
        "Arial",
        "Calibri",
        "Helvetica",
        "Georgia",
        "Garamond",
        "Roboto",
        "Open Sans",
        "Lato",
        "Inter"
    ]

    @classmethod
    def get_supported_fonts(cls) -> List[str]:
        """Returns list of supported font names."""
        return cls.SUPPORTED_FONTS

    @classmethod
    def get_safe_font_name(cls, font_name: str) -> str:
        """
        Validates if font_name is registered in ReportLab.
        If not, falls back to a standard built-in font (Helvetica, Times-Roman, Courier).
        """
        registered = pdfmetrics.getRegisteredFontNames()
        
        # Check exact match
        if font_name in registered:
            return font_name
            
        # Check case-insensitive match
        for r_font in registered:
            if r_font.lower() == font_name.lower():
                return r_font
                
        # Heuristic fallbacks
        serif_fonts = {"times new roman", "georgia", "garamond", "times-roman"}
        mono_fonts = {"courier", "consolas"}
        
        fn_lower = font_name.lower()
        if fn_lower in serif_fonts:
            return "Times-Roman"
        elif fn_lower in mono_fonts:
            return "Courier"
        else:
            return "Helvetica"

    @classmethod
    def register_fonts(cls) -> None:
        """
        Registers core fonts with ReportLab.
        Attempts to register TTF files if present in the fonts/ directory.
        """
        # Helvetica/Times are standard postscript fonts and already registered in ReportLab
        logger.info("Initializing FontManager...")
        
        if not FONTS_DIR.exists():
            FONTS_DIR.mkdir(exist_ok=True)
            
        # Example of registering custom fonts from the local directory if they exist
        for font_name in cls.SUPPORTED_FONTS:
            # ReportLab core fonts do not need registration
            if font_name in ["Helvetica", "Times-Roman"]:
                continue
                
            # If the user has put TTF files in the fonts dir, we register them
            font_file = FONTS_DIR / f"{font_name}.ttf"
            if font_file.exists():
                try:
                    pdfmetrics.registerFont(TTFont(font_name, str(font_file)))
                    logger.info(f"Registered custom font: {font_name}")
                except Exception as e:
                    logger.error(f"Failed to register custom font {font_name}: {e}")
            else:
                logger.debug(f"TTF file for {font_name} not found, using fallback/standard mappings.")
