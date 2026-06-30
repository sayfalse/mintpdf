import sys
from typing import Optional

from .cli import MintCLI
from .logger import logger
from .services import (
    ConfigurationService,
    CoverPageService,
    DocumentAnalysisService,
    ExportService,
    FontService,
    MetadataService,
    TemplateService,
    ThemeService,
    TOCService,
)
from .settings import AppSettings
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

        # Instantiate pipeline stages
        from .pipeline import (
            DocumentBuilder,
            DocumentLoader,
            LayoutBuilder,
            PDFExporter,
            Renderer,
        )

        loader = DocumentLoader()
        builder = DocumentBuilder()
        layout_builder = LayoutBuilder()
        renderer = Renderer()
        exporter = PDFExporter()

        # Instantiate services
        config_service = ConfigurationService()
        theme_service = ThemeService()
        template_service = TemplateService()
        font_service = FontService()
        analysis_service = DocumentAnalysisService()
        metadata_service = MetadataService()
        cover_page_service = CoverPageService()
        toc_service = TOCService()
        export_service = ExportService(
            document_loader=loader,
            document_builder=builder,
            layout_builder=layout_builder,
            renderer=renderer,
            exporter=exporter,
        )

        # Step 1: Handle first-launch configuration setup
        settings: Optional[AppSettings] = None

        if config_service.is_first_launch():
            logger.info("First launch detected. Running setup wizard.")
            settings = config_service.run_setup_wizard()
        else:
            settings = config_service.load_config()

            # If config exists but is corrupted, run setup wizard
            if settings is None:
                logger.warning(
                    "Configuration loaded as None (possible corruption). Rerunning setup wizard."
                )
                settings = config_service.run_setup_wizard()

        # Step 2: Register system/custom fonts
        try:
            font_service.register_fonts()
        except Exception as e:
            logger.error(f"Error registering fonts on startup: {e}")

        # Step 3: Run the interactive CLI Loop
        logger.info("Launching main CLI interactive loop.")
        assert settings is not None
        cli = MintCLI(
            settings,
            config_service,
            theme_service,
            template_service,
            font_service,
            analysis_service,
            metadata_service,
            cover_page_service,
            toc_service,
            export_service,
        )
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
