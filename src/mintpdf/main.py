"""
Mint PDF - AI-Free Professional PDF Generator for the Terminal.
Main Entry Point.
"""

import sys

from .cli import MintCLI
from .config import is_first_launch, load_config, run_setup_wizard
from .font_manager import FontManager
from .logger import logger
from .utils import clear_screen


def main() -> None:
    """
    Main application orchestrator.
    Handles startup sequence, setup check, configuration loading,
    font initialization, and CLI invocation.
    """
    # Fix console encoding on Windows to prevent UnicodeEncodeError crashes
    if sys.platform.startswith("win"):
        if hasattr(sys.stdout, "reconfigure"):
            try:
                sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
                sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]
            except Exception:
                pass

    try:
        logger.info("Application starting up...")
        clear_screen()

        # Step 1: Handle first-launch configuration setup
        from typing import Optional

        from .settings import AppSettings

        settings: Optional[AppSettings] = None

        if is_first_launch():
            logger.info("First launch detected. Running setup wizard.")
            settings = run_setup_wizard()
        else:
            settings = load_config()

            # If config exists but is corrupted, run setup wizard
            if settings is None:
                logger.warning(
                    "Configuration loaded as None (possible corruption). Rerunning setup wizard."
                )
                settings = run_setup_wizard()

        # Step 2: Register system/custom fonts
        try:
            FontManager.register_fonts()
        except Exception as e:
            logger.error(f"Error registering fonts on startup: {e}")

        # Step 3: Run the interactive CLI Loop
        logger.info("Launching main CLI interactive loop.")
        assert settings is not None
        cli = MintCLI(settings)
        cli.run()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user (KeyboardInterrupt). Exiting.")
        print("\n\n[!] Operation interrupted. Goodbye! 🌿\n")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Unhandled exception in main thread: {e}", exc_info=True)
        print(f"\n[!] Fatal Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
