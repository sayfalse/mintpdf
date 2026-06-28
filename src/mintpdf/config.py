"""
Configuration manager for Mint PDF.
Handles loading, saving, migrations, corruption recovery, and the setup wizard.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from .logger import logger
from .settings import AppSettings

CONFIG_FILE = Path("config.json")


def get_default_output_dir() -> Path:
    """Returns the default output directory path based on the operating system."""
    return Path.home() / "Documents" / "Mint PDF"


def is_first_launch() -> bool:
    """Checks if the application is running for the first time by checking config existence."""
    return not CONFIG_FILE.exists()


def backup_corrupted_config(console: Optional[Console] = None) -> None:
    """
    Backs up a corrupted config.json by renaming it with a timestamp
    so user preferences are not fully deleted.
    """
    if not CONFIG_FILE.exists():
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"config.json.corrupted_{timestamp}"
    backup_path = CONFIG_FILE.parent / backup_name

    try:
        shutil.move(str(CONFIG_FILE), str(backup_path))
        msg = f"[bold yellow]! Corrupted configuration detected and backed up as: {backup_name}[/bold yellow]"
        if console:
            console.print(msg)
        logger.warning(f"Corrupted config.json moved to {backup_path}")
    except Exception as e:
        logger.error(f"Failed to backup corrupted config file: {e}")
        # Try deleting it as fallback to prevent boot loops
        try:
            CONFIG_FILE.unlink()
        except Exception:
            pass


def load_config(console: Optional[Console] = None) -> Optional[AppSettings]:
    """
    Loads configuration settings from config.json.
    Automatically handles schema migrations and corrupted file recovery.

    Returns:
        AppSettings object if loaded successfully, otherwise None (which prompts Setup).
    """
    if not CONFIG_FILE.exists():
        logger.info("Configuration file config.json does not exist.")
        return None

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ValueError("Configuration root must be a JSON object.")

        # Instantiate with safe default merging
        settings = AppSettings.from_dict_with_defaults(data)
        logger.info("Successfully loaded configuration.")

        # Check if schema migration is required
        current_version = AppSettings().config_version
        loaded_version = data.get("config_version", 0)

        if loaded_version < current_version:
            logger.info(f"Migrating config from version {loaded_version} to {current_version}.")
            settings.config_version = current_version
            # Auto save migrated config
            save_config(settings)
            if console:
                console.print(
                    f"[green]✓ Configuration migrated to schema version {current_version}.[/green]"
                )

        return settings
    except (json.JSONDecodeError, ValueError) as je:
        logger.error(f"Corrupted config file: {je}")
        backup_corrupted_config(console)
        return None
    except Exception as e:
        logger.error(f"Error loading configuration: {e}", exc_info=True)
        backup_corrupted_config(console)
        return None


def save_config(settings: AppSettings) -> bool:
    """
    Saves configuration settings to config.json.

    Args:
        settings: The AppSettings object to save.

    Returns:
        True if save was successful, False otherwise.
    """
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(settings.to_dict(), f, indent=4)
        logger.info(f"Saved configuration to {CONFIG_FILE}.")
        return True
    except Exception as e:
        logger.error(f"Error saving configuration: {e}", exc_info=True)
        return False


def run_setup_wizard(console: Optional[Console] = None) -> AppSettings:
    """
    Runs the interactive setup wizard for first-time launch.

    Args:
        console: Optional Rich Console for pretty output.

    Returns:
        A newly configured AppSettings instance.
    """
    if console is None:
        console = Console()

    console.print(
        Panel(
            "[bold green]Welcome to Mint PDF Setup Wizard![/bold green]\n\n"
            "This wizard will help you configure Mint PDF for its first run.\n"
            "No internet, no API keys, and no online services are required.",
            title="First Launch Setup",
            expand=False,
        )
    )

    default_dir = get_default_output_dir()
    console.print(f"\n[yellow]Default output folder:[/yellow] {default_dir}")

    # Prompt for output directory
    user_input = Prompt.ask(
        "Enter output directory (leave blank for default)",
        default=str(default_dir),
        console=console,
    ).strip()

    # Resolve the path and convert to absolute
    output_path = Path(user_input).expanduser().resolve()

    # Create the directory if it doesn't exist
    try:
        output_path.mkdir(parents=True, exist_ok=True)
        console.print(f"[green]✓ Output directory verified/created at:[/green] {output_path}")
    except Exception as e:
        console.print(
            f"[bold red]Error: Could not create folder {output_path} due to: {e}[/bold red]"
        )
        console.print(f"[yellow]Falling back to default:[/yellow] {default_dir}")
        output_path = default_dir
        output_path.mkdir(parents=True, exist_ok=True)

    # Initialize default AppSettings
    settings = AppSettings(
        config_version=AppSettings().config_version,
        output_dir=str(output_path),
        theme="Professional",
        default_template="Standard",
        default_font="Helvetica",
        page_size="LETTER",
        language="English",
        auto_toc=True,
        auto_page_numbers=True,
    )

    # Save the configuration
    success = save_config(settings)
    if success:
        console.print("\n[bold green]Setup completed successfully![/bold green]\n")
        logger.info("First launch setup completed successfully.")
    else:
        console.print("\n[bold red]Warning: Configuration could not be saved to disk.[/bold red]\n")
        logger.warning("First launch setup completed but config saving failed.")

    return settings
