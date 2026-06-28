from mintpdf.template_manager import Template, TemplateManager
from mintpdf.theme_manager import ThemeManager


def test_template_manager_defaults():
    # Resolve Standard template
    t = TemplateManager.get_template("Standard")
    assert t.name == "Standard"
    assert t.category == "General"

    # Check fallback structure values
    assert t.margins["top"] == 54.0
    assert t.margins["bottom"] == 54.0


def test_template_inheritance():
    # Parent layout
    parent = Template(
        name="Parent",
        description="Parent layout",
        category="Test",
        margins={"top": 72.0, "bottom": 72.0, "left": 72.0, "right": 72.0},
        typography={"body_font_size": 11.0},
    )

    # Register parent template
    TemplateManager.CUSTOM_TEMPLATES["Parent"] = parent

    # Child inherits all except left margin
    child = Template(
        name="Child",
        description="Child layout",
        category="Test",
        extends="Parent",
        margins={"left": 50.0},
    )

    # Resolve inheritance via TemplateManager
    resolved_child = TemplateManager.resolve_inheritance(child)

    assert resolved_child.margins["top"] == 72.0  # inherited
    assert resolved_child.margins["left"] == 50.0  # overridden
    assert resolved_child.typography["body_font_size"] == 11.0  # inherited

    # Clean up
    del TemplateManager.CUSTOM_TEMPLATES["Parent"]


def test_theme_manager_defaults():
    # Theme collection
    names = ThemeManager.get_all_theme_names()
    assert "Professional" in names

    t = ThemeManager.get_theme("Professional")
    assert t.name == "Professional"
    assert t.primary == "#1B2A4A"
