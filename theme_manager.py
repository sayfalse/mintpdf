"""
Theme Manager module for Mint PDF.
Defines color palettes and visual styles, and dynamically loads custom themes from JSON.
"""

import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from logger import logger

THEMES_DIR = Path("themes")

class Theme:
    """Represents a document styling theme with specific color hex values."""
    def __init__(
        self,
        name: str,
        primary: str,
        secondary: str,
        accent: str,
        text: str,
        bg: str = "#FFFFFF",
        border: str = "#E2E8F0",
        table_header_bg: Optional[str] = None,
        table_row_alt: str = "#F7FAFC",
        link_color: str = "#3182CE"
    ):
        self.name = name
        self.primary = primary
        self.secondary = secondary
        self.accent = accent
        self.text = text
        self.bg = bg
        self.border = border
        self.table_header_bg = table_header_bg if table_header_bg else primary
        self.table_row_alt = table_row_alt
        self.link_color = link_color

    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "text": self.text,
            "bg": self.bg,
            "border": self.border,
            "table_header_bg": self.table_header_bg,
            "table_row_alt": self.table_row_alt,
            "link_color": self.link_color
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Theme":
        """Instantiates a Theme object from dictionary data with strict validation."""
        required = ["name", "primary", "secondary", "accent", "text"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in theme definition.")
        
        # Color string format validation
        for field in ["primary", "secondary", "accent", "text", "bg", "border", "table_row_alt", "link_color"]:
            if field in data and not str(data[field]).startswith("#"):
                raise ValueError(f"Color field '{field}' must be a valid hex code starting with '#'.")
                
        return cls(
            name=data["name"],
            primary=data["primary"],
            secondary=data["secondary"],
            accent=data["accent"],
            text=data["text"],
            bg=data.get("bg", "#FFFFFF"),
            border=data.get("border", "#E2E8F0"),
            table_header_bg=data.get("table_header_bg"),
            table_row_alt=data.get("table_row_alt", "#F7FAFC"),
            link_color=data.get("link_color", "#3182CE")
        )

class ThemeManager:
    """Manages document themes and dynamically registers custom JSON styling files."""
    
    BUILTIN_THEMES = {
        "Blue": Theme("Blue", "#1A365D", "#2B6CB0", "#3182CE", "#2D3748", "#FFFFFF"),
        "Green": Theme("Green", "#1C4532", "#38A169", "#48BB78", "#2D3748", "#FFFFFF"),
        "Purple": Theme("Purple", "#44337A", "#6B46C1", "#805AD5", "#2D3748", "#FFFFFF"),
        "Gray": Theme("Gray", "#2D3748", "#4A5568", "#718096", "#1A202C", "#FFFFFF"),
        "Black": Theme("Black", "#000000", "#1A202C", "#4A5568", "#1A202C", "#FFFFFF"),
        "White": Theme("White", "#718096", "#E2E8F0", "#EDF2F7", "#2D3748", "#FFFFFF", border="#CBD5E0", table_row_alt="#F7FAFC"),
        "Ocean": Theme("Ocean", "#0C2340", "#008080", "#20B2AA", "#1A202C", "#FAFAFA"),
        "Forest": Theme("Forest", "#1E352F", "#556B2F", "#8F9779", "#1A202C", "#FAF9F6"),
        "Professional": Theme("Professional", "#1B2A4A", "#3F51B5", "#FF5722", "#212121", "#FFFFFF"),
        "Minimal": Theme("Minimal", "#212121", "#616161", "#9E9E9E", "#212121", "#FFFFFF", border="#E2E8F0")
    }

    # Loaded custom themes
    CUSTOM_THEMES: Dict[str, Theme] = {}

    @classmethod
    def load_custom_themes(cls) -> None:
        """
        Scans the themes/ folder for JSON files and registers valid custom themes.
        """
        cls.CUSTOM_THEMES.clear()
        
        if not THEMES_DIR.exists():
            try:
                THEMES_DIR.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create themes directory: {e}")
                return
                
        try:
            for item in THEMES_DIR.iterdir():
                if item.is_file() and item.suffix.lower() == ".json":
                    try:
                        with open(item, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        theme_obj = Theme.from_dict(data)
                        
                        # Use title cased theme name as key
                        key = theme_obj.name.title()
                        cls.CUSTOM_THEMES[key] = theme_obj
                        logger.info(f"Registered custom theme: {key} from {item.name}")
                    except Exception as e:
                        logger.error(f"Error parsing custom theme file {item.name}: {e}")
        except Exception as e:
            logger.error(f"Error scanning themes directory: {e}")

    @classmethod
    def get_all_theme_names(cls) -> List[str]:
        """Returns lists of all available (built-in + custom) theme names."""
        # Always reload on name list retrieval to check for drop-in updates
        cls.load_custom_themes()
        names = list(cls.BUILTIN_THEMES.keys()) + list(cls.CUSTOM_THEMES.keys())
        # Deduplicate preserving order
        seen = set()
        return [n for n in names if not (n in seen or seen.add(n))]

    @classmethod
    def get_theme(cls, name: str) -> Theme:
        """
        Gets a theme by name. Check custom themes first, then built-in.
        Falls back to Professional theme if not found.
        """
        # Ensure latest custom themes are loaded
        if not cls.CUSTOM_THEMES:
            cls.load_custom_themes()
            
        name_title = name.title()
        if name_title in cls.CUSTOM_THEMES:
            return cls.CUSTOM_THEMES[name_title]
        return cls.BUILTIN_THEMES.get(name_title, cls.BUILTIN_THEMES["Professional"])
