import importlib.util
import inspect
from pathlib import Path
from typing import Dict, Optional

from ..logger import logger
from ..theme_manager import ThemeManager
from .base import BaseExporter, BaseLoader


class PluginManager:
    """Discovers, loads, and manages third-party plugins and extensions."""

    _instance: Optional["PluginManager"] = None
    _initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, plugins_dir: str = "plugins"):
        if self._initialized:
            return
        self.plugins_dir = Path(plugins_dir)
        self.loaders: Dict[str, BaseLoader] = {}
        self.exporters: Dict[str, BaseExporter] = {}
        self._initialized = True

    def discover_and_load(self) -> None:
        """Scan plugins directory, import .py modules, and register plugin classes."""
        if not self.plugins_dir.exists():
            try:
                self.plugins_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.error(f"Failed to create plugins directory: {e}")
                return

        logger.info(f"Scanning plugins from: {self.plugins_dir.resolve()}")
        for file_path in self.plugins_dir.glob("*.py"):
            if file_path.name.startswith("_"):
                continue
            try:
                self._load_plugin_module(file_path)
            except Exception as e:
                logger.error(f"Failed to load plugin from {file_path.name}: {e}", exc_info=True)

    def _load_plugin_module(self, file_path: Path) -> None:
        module_name = f"mintpdf.plugins.dynamic.{file_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Inspect the module for classes subclassing BaseLoader or BaseExporter
        for _, obj in inspect.getmembers(module, inspect.isclass):
            # Check loaders
            if issubclass(obj, BaseLoader) and obj is not BaseLoader:
                try:
                    loader_instance = obj()
                    for ext in loader_instance.supported_extensions():
                        ext_clean = ext.lower().strip()
                        self.loaders[ext_clean] = loader_instance
                        logger.info(
                            f"Registered Loader Plugin: {obj.__name__} for extension {ext_clean}"
                        )
                except Exception as e:
                    logger.error(f"Failed to instantiate loader plugin {obj.__name__}: {e}")

            # Check exporters
            elif issubclass(obj, BaseExporter) and obj is not BaseExporter:
                try:
                    exporter_instance = obj()
                    for fmt in exporter_instance.supported_formats():
                        fmt_clean = fmt.lower().strip()
                        self.exporters[fmt_clean] = exporter_instance
                        logger.info(
                            f"Registered Exporter Plugin: {obj.__name__} for format {fmt_clean}"
                        )
                except Exception as e:
                    logger.error(f"Failed to instantiate exporter plugin {obj.__name__}: {e}")

        # Check for theme registration
        if hasattr(module, "THEMES"):
            themes_list = module.THEMES
            if isinstance(themes_list, list):
                for theme in themes_list:
                    # Register theme with ThemeManager
                    if hasattr(theme, "name"):
                        ThemeManager.CUSTOM_THEMES[theme.name.title()] = theme
                        logger.info(f"Registered Custom Theme Plugin: {theme.name}")
