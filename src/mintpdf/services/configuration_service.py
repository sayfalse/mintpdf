from typing import Optional

from rich.console import Console

from ..config import (
    backup_corrupted_config,
    is_first_launch,
    load_config,
    run_setup_wizard,
    save_config,
)
from ..settings import AppSettings


class ConfigurationService:
    """Service to manage application configuration settings."""

    def load_config(self, console: Optional[Console] = None) -> Optional[AppSettings]:
        return load_config(console)

    def save_config(self, settings: AppSettings) -> bool:
        return save_config(settings)

    def is_first_launch(self) -> bool:
        return is_first_launch()

    def backup_corrupted_config(self, console: Optional[Console] = None) -> None:
        backup_corrupted_config(console)

    def run_setup_wizard(self, console: Optional[Console] = None) -> AppSettings:
        return run_setup_wizard(console)
