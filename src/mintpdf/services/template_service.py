from typing import List

from ..template_manager import Template, TemplateManager


class TemplateService:
    """Service to manage layout templates."""

    def get_template(self, name: str) -> Template:
        return TemplateManager.get_template(name)

    def get_template_names(self) -> List[str]:
        return TemplateManager.get_template_names()

    def get_all_templates(self) -> List[Template]:
        return TemplateManager.get_all_templates()

    def load_custom_templates(self) -> None:
        TemplateManager.load_custom_templates()
