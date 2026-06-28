"""
Template Manager module for Mint PDF.
Defines layout templates, handles custom JSON templates loading, and implements inheritance resolving.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from .logger import logger

TEMPLATES_DIR = Path("templates")

class Template:
    """Represents a document layout template defining typography, sizes, and margins."""
    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        extends: Optional[str] = None,
        margins: Optional[Dict[str, float]] = None,
        typography: Optional[Dict[str, float]] = None,
        heading_styles: Optional[Dict[str, float]] = None
    ):
        self.name = name
        self.description = description
        self.category = category
        self.extends = extends
        
        # Default layout values if not supplied
        self.margins = margins or {
            "top": 54.0, "bottom": 54.0, "left": 54.0, "right": 54.0
        }
        self.typography = typography or {
            "body_font_size": 10.5, "body_leading": 15.0
        }
        self.heading_styles = heading_styles or {
            "h1_size": 20.0, "h1_leading": 24.0,
            "h2_size": 15.0, "h2_leading": 19.0,
            "h3_size": 12.0, "h3_leading": 16.0
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "extends": self.extends,
            "margins": self.margins,
            "typography": self.typography,
            "heading_styles": self.heading_styles
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """Instantiates a Template object from a dictionary."""
        required = ["name", "description", "category"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field '{field}' in template definition.")
        return cls(
            name=data["name"],
            description=data["description"],
            category=data["category"],
            extends=data.get("extends"),
            margins=data.get("margins"),
            typography=data.get("typography"),
            heading_styles=data.get("heading_styles")
        )

class TemplateManager:
    """Manages document layout templates and dynamically loads/resolves custom JSON files."""
    
    # 25 Built-in layouts
    BUILTIN_TEMPLATES = [
        Template("Standard", "Generic clean layout for multi-purpose use", "General"),
        Template("Executive", "Formal corporate report layout with prominent titles", "Business",
                 margins={"top": 72.0, "bottom": 72.0, "left": 72.0, "right": 72.0}),
        Template("Technical Report", "Structured layout with technical sections and code blocks", "Technical",
                 margins={"top": 54.0, "bottom": 54.0, "left": 45.0, "right": 45.0},
                 typography={"body_font_size": 10.0, "body_leading": 14.0}),
        Template("Thesis", "Academic style for university thesis and dissertations", "Academic",
                 margins={"top": 72.0, "bottom": 72.0, "left": 90.0, "right": 54.0}), # wider left margin for binding
        Template("Novel", "Compact text layout suited for books and storytelling", "Creative",
                 margins={"top": 60.0, "bottom": 60.0, "left": 72.0, "right": 72.0},
                 typography={"body_font_size": 11.5, "body_leading": 17.0}),
        Template("Resume", "Sleek column layout for personal CVs", "Personal",
                 margins={"top": 36.0, "bottom": 36.0, "left": 36.0, "right": 36.0},
                 typography={"body_font_size": 9.5, "body_leading": 13.0}),
        Template("Business Proposal", "Modern layout targeted for selling services or ideas", "Business"),
        Template("Newsletter", "Multi-column informal layout for updates", "Publication",
                 margins={"top": 45.0, "bottom": 45.0, "left": 45.0, "right": 45.0}),
        Template("Invoice", "Structured grids for financial billing details", "Business"),
        Template("Syllabus", "Clear tabular layout suited for courses and classes", "Academic"),
        Template("Meeting Minutes", "Action-oriented layout for notes and tasks", "Business"),
        Template("Research Paper", "Double column standard for scientific papers", "Academic"),
        Template("Whitepaper", "Highly formatted authoritative report layout", "Business"),
        Template("User Manual", "Step-by-step documentation template", "Technical"),
        Template("Class Handout", "Simple summary list with notes sections", "Academic"),
        Template("Portfolio", "Image-centric showcase layout", "Creative"),
        Template("Legal Contract", "Numbered clauses with formal borders", "Legal",
                 margins={"top": 72.0, "bottom": 72.0, "left": 72.0, "right": 72.0}),
        Template("Pitch Deck", "Landscape presentation-friendly PDF slides", "Business"),
        Template("Internal Memo", "Header-focused brief corporate memo", "Business"),
        Template("Recipe Book", "Two-column list layout with instruction steps", "Creative"),
        Template("Case Study", "Callout-focused layout for success stories", "Business"),
        Template("Press Release", "Standard layout with media contact sections", "Business"),
        Template("Standard Draft", "Minimal formatting draft style for reviews", "General",
                 typography={"body_font_size": 12.0, "body_leading": 18.0}),
        Template("Formal Letter", "Addressee-focused correspondence layout", "Personal"),
        Template("Project Plan", "Task list and milestone track style layout", "Technical")
    ]

    CUSTOM_TEMPLATES: Dict[str, Template] = {}

    @classmethod
    def load_custom_templates(cls) -> None:
        """Scans the templates/ folder for custom JSON layouts."""
        cls.CUSTOM_TEMPLATES.clear()
        
        if not TEMPLATES_DIR.exists():
            try:
                TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create templates directory: {e}")
                return
                
        try:
            for item in TEMPLATES_DIR.iterdir():
                if item.is_file() and item.suffix.lower() == ".json":
                    try:
                        with open(item, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        tmpl_obj = Template.from_dict(data)
                        
                        key = tmpl_obj.name.title()
                        cls.CUSTOM_TEMPLATES[key] = tmpl_obj
                        logger.info(f"Registered custom template layout: {key} from {item.name}")
                    except Exception as e:
                        logger.error(f"Error parsing custom template file {item.name}: {e}")
        except Exception as e:
            logger.error(f"Error scanning templates directory: {e}")

    @classmethod
    def get_all_templates(cls) -> List[Template]:
        """Returns resolved list of all templates."""
        cls.load_custom_templates()
        all_resolved = []
        
        # Load built-ins
        for t in cls.BUILTIN_TEMPLATES:
            all_resolved.append(cls.resolve_inheritance(t))
            
        # Load customs
        for name, t in cls.CUSTOM_TEMPLATES.items():
            all_resolved.append(cls.resolve_inheritance(t))
            
        return all_resolved

    @classmethod
    def get_template_names(cls) -> List[str]:
        """Returns all layout template names."""
        return [t.name for t in cls.get_all_templates()]

    @classmethod
    def get_template_raw(cls, name: str) -> Optional[Template]:
        """Gets a raw (unresolved) template by name."""
        name_title = name.title()
        
        # Search customs
        if name_title in cls.CUSTOM_TEMPLATES:
            return cls.CUSTOM_TEMPLATES[name_title]
            
        # Search built-ins
        for t in cls.BUILTIN_TEMPLATES:
            if t.name.title() == name_title:
                return t
        return None

    @classmethod
    def get_template(cls, name: str) -> Template:
        """Gets a resolved template by name, falls back to Standard."""
        # Ensure customs are loaded
        if not cls.CUSTOM_TEMPLATES:
            cls.load_custom_templates()
            
        raw_tmpl = cls.get_template_raw(name)
        if raw_tmpl:
            return cls.resolve_inheritance(raw_tmpl)
            
        # Fallback to standard
        return cls.resolve_inheritance(cls.BUILTIN_TEMPLATES[0])

    @classmethod
    def resolve_inheritance(cls, template: Template) -> Template:
        """
        Recursively resolves inheritance for a template by merging child details
        over parent definitions.
        """
        if not template.extends:
            return template
            
        parent = cls.get_template_raw(template.extends)
        if not parent or parent.name.lower() == template.name.lower():
            # Prevent infinite recursion loop
            return template
            
        # Resolve parent hierarchy first
        resolved_parent = cls.resolve_inheritance(parent)
        
        # Merge properties
        merged_margins = {**(resolved_parent.margins or {})}
        if template.margins:
            merged_margins.update(template.margins)
            
        merged_typography = {**(resolved_parent.typography or {})}
        if template.typography:
            merged_typography.update(template.typography)
            
        merged_headings = {**(resolved_parent.heading_styles or {})}
        if template.heading_styles:
            merged_headings.update(template.heading_styles)
            
        return Template(
            name=template.name,
            description=template.description,
            category=template.category,
            extends=template.extends,
            margins=merged_margins,
            typography=merged_typography,
            heading_styles=merged_headings
        )
