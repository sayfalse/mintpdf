# Changelog

All notable changes to **Mint PDF** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-29

### Added
- Complete standard package layout structure with `src/mintpdf` and Console Entry Scripts configured in `pyproject.toml`.
- Fully automated test suite using `pytest` covering settings, analyzers, markdown formatters, and PDF engine.
- Formally integrated code quality configurations for `Black`, `Ruff`, and `MyPy` with a strict 100-character line limit.
- Added type validation support using `pydantic.mypy` type check plugin.
- Added automated CI/CD pipelines via GitHub Actions workflows (`ci.yml` and `publish.yml`).
- Introduced case-insensitive Enum string validation recovery in `AppSettings`.
- Resolved multi-level template inheritance property overriding bug.

### Changed
- Refactored all internal source references from standalone imports to relative namespace module imports.
- Upgraded default color theme styling defaults to Professional theme palettes.
- Hardened inline table cell wrapping and heading bookmark generation logic.

---

## [0.1.0] - 2026-06-20

### Added
- Initial proof-of-concept release.
- Standalone command-line client script structure.
- ReportLab-based flowable document compile mechanics.
- Custom `NumberedCanvas` running headers and footers.
- Base ATX/Setext Markdown document analyzer logic.
- Built-in theme manager and layout templates dictionary registry.
