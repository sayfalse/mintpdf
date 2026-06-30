from mintpdf.domain.models import Document, Metadata
from mintpdf.event_dispatcher import EventDispatcher
from mintpdf.settings import AppSettings, FontEnum, PageSizeEnum, ThemeEnum


def test_event_dispatcher():
    dispatcher = EventDispatcher()
    calls = []

    def on_parsed(document):
        calls.append(document.metadata.title)

    dispatcher.subscribe("document:parsed", on_parsed)

    # Publish event
    doc = Document(metadata=Metadata(title="My Event Doc"))
    dispatcher.publish("document:parsed", document=doc)

    assert len(calls) == 1
    assert calls[0] == "My Event Doc"

    # Test listener exception safety
    def bad_listener(*args, **kwargs):
        raise ValueError("Bad listener")

    dispatcher.subscribe("document:parsed", bad_listener)
    # Should not crash during publish
    dispatcher.publish("document:parsed", document=doc)
    assert len(calls) == 2


def test_app_settings_env_overrides(monkeypatch):
    monkeypatch.setenv("MINT_OUTPUT_DIR", "env_out_dir")
    monkeypatch.setenv("MINT_THEME", "green")
    monkeypatch.setenv("MINT_DEFAULT_FONT", "roboto")
    monkeypatch.setenv("MINT_PAGE_SIZE", "a4")
    monkeypatch.setenv("MINT_AUTO_TOC", "false")
    monkeypatch.setenv("MINT_AUTO_PAGE_NUMBERS", "1")

    # Load settings with from_dict_with_defaults
    settings = AppSettings.from_dict_with_defaults({})

    assert settings.output_dir == "env_out_dir"
    assert settings.theme == ThemeEnum.GREEN
    assert settings.default_font == FontEnum.ROBOTO
    assert settings.page_size == PageSizeEnum.A4
    assert settings.auto_toc is False
    assert settings.auto_page_numbers is True
