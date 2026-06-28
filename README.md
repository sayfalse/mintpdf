# Mint PDF

🌿 **AI-Free Professional PDF Generator for the Terminal**

Mint PDF is a production-quality offline CLI application that parses plain text and markdown documents and compiles them into beautifully formatted, publication-ready PDF files.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Installation Guide](#installation-guide)
4. [Usage Guide](#usage-guide)
5. [Configuration Guide](#configuration-guide)
6. [Template & Theme Guide](#template--theme-guide)
7. [Developer Guide](#developer-guide)
8. [Contribution Guide](#contribution-guide)

---

## Project Overview
Mint PDF works **100% offline** and requires **zero external cloud calls, API keys, or online models**. It utilizes a local rule-based structural scanner and compiler built on ReportLab to typeset professional documents automatically.

---

## Project Structure
```
mint-pdf/
│
├── main.py               # Application startup & bootstrapper
├── cli.py                # Command-line interface & guided workflows (using Rich)
├── config.py             # Configuration controller (migrations, backup & recovery)
├── settings.py           # Configuration schema definitions (validated via Pydantic)
├── pdf_engine.py         # Main PDF compiler & layout compositor (using ReportLab)
├── cover_page.py         # Front cover flowables generator
├── formatter.py          # Document structure parsing (lists, tables, blockquotes)
├── template_manager.py   # Layout templates manager (supports template inheritance)
├── theme_manager.py      # Theme palettes controller (supports custom JSON themes)
├── font_manager.py       # Font catalog (manages custom TTFs and default fallbacks)
├── document_analyzer.py  # Rule-based scanner (element counts and recommendations)
├── toc.py                # Dot-leader Table of Contents generator
├── metadata.py           # Pydantic model for document properties
├── file_manager.py       # Safe OS-independent filesystem utilities
├── utils.py              # Dimension conversions and utility helpers
├── logger.py             # Rotating file logs and error trace managers
│
├── config.json           # Active app configuration settings (auto-generated)
├── templates/            # Directory for custom template JSONs
├── themes/               # Directory for custom theme JSONs
├── fonts/                # Directory for user-installed custom TTFs
├── assets/               # Folder for document media assets (e.g. images)
├── icons/                # Folder for application icons
├── output/               # Default output directory for generated PDFs
├── logs/                 # Location of the debug file: logs/mint_pdf.log
│
├── README.md             # This document
└── requirements.txt      # Python dependencies manifest
```

---

## Installation Guide

### Prerequisites
- Python 3.12 or newer installed on your local computer.
- pip package manager.

### Steps
1. Navigate to the directory containing Mint PDF:
   ```bash
   cd "mint-pdf"
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## Usage Guide

1. **Setup Wizard**: On the very first run, Mint PDF asks for a default output directory. If left blank, it defaults to:
   `C:\Users\<CurrentUser>\Documents\Mint PDF\` (Windows).
2. **Create New PDF (Option 1)**:
   - **Step 1**: Choose whether to paste text or load a file (`.txt`, `.md`, `.docx`).
   - **Step 2**: The analyzer will display document statistics (lists, tables, images, code blocks) and recommend styles.
   - **Step 3**: Fill in document metadata (Title, Author, Organization, Version).
   - **Step 4**: Select a template layout (e.g. Standard, Executive, Thesis).
   - **Step 5**: Choose a visual color theme (e.g. Professional, Forest, Ocean).
   - **Step 6**: Pick a typography font family.
   - **Step 7**: Configure/fine-tune margins, page sizes, and numbering.
   - **Step 8**: Enable or disable the Cover Page.
   - **Step 9-11**: Review the pre-generation summary table.
   - **Step 12**: Confirm file name, handle name collision prompts, and generate the PDF.
3. **Open Existing Project (Option 2)**: Lists and summarizes previous output files found in the output directory.
4. **Settings Configuration (Option 4)**: Dynamically adjust default themes, margin sizes, A4/Letter dimensions, and default languages.

---

## Configuration Guide
The application settings are saved in `config.json` and validated strictly via `Pydantic` models:
- **`config_version`**: Schema validation version (used for automated migrations).
- **`output_dir`**: The folder where generated files are saved.
- **`theme`**: Active default theme choice (e.g. `Professional`, `Minimal`).
- **`default_template`**: Default layout choice.
- **`default_font`**: Typography choice (Times New Roman, Helvetica, Inter).
- **`page_size`**: Dimensions choice (`LETTER`, `A4`, `LEGAL`).
- **`margins`**: Sub-object specifying `top`, `bottom`, `left`, and `right` margins in points (pt).
- **`auto_toc`**: Boolean flag to enable dynamic index compilations.
- **`auto_page_numbers`**: Boolean flag to enable footer numbering.

*Recovery Mechanism*: If `config.json` becomes corrupted, the manager backs it up under a timestamp and regenerates a clean settings profile.

---

## Template & Theme Guide

### 1. Custom Themes
You can add custom color palettes by placing a `.json` file inside the `themes/` directory:
```json
{
  "name": "Custom Gold",
  "primary": "#D4AF37",
  "secondary": "#AA7C11",
  "accent": "#F3E5AB",
  "text": "#2C3E50",
  "bg": "#FFFFFF",
  "border": "#BDC3C7",
  "table_row_alt": "#FAF9F6",
  "link_color": "#D4AF37"
}
```

### 2. Custom Templates & Inheritance
You can create custom templates by dropping `.json` files inside the `templates/` directory. Templates support inheritance through the `extends` keyword. Fields not specified in the child template are recursively inherited from the parent template:
```json
{
  "name": "Fancy Draft",
  "extends": "Standard",
  "category": "Custom",
  "description": "Customized margins and font sizes",
  "margins": {
    "left": 72.0,
    "right": 72.0
  },
  "typography": {
    "body_font_size": 12.0
  }
}
```

---

## Developer Guide

### Key Module Workflows
- **`logger.py`**: Initializes rotating system logs in `logs/mint_pdf.log`. Standard output tracebacks are masked to prevent terminal clutter.
- **`document_analyzer.py`**: Runs Setext underline and ATX regex counts. Computes element densities and maps them to layout categories using a heuristic score matrix.
- **`formatter.py`**: Iterates original lines. It captures indents to format multi-level bulleted lists, wraps table cell data inside `Paragraph` flowables for text wrapping, and maps code blocks to grid panels.
- **`pdf_engine.py`**: Renders cover sheets, TOC flows, and body flowables, calling `NumberedCanvas` to draw headers and running footers on a two-pass render.

---

## Contribution Guide
1. **Clean Code**: Follow PEP 8 guidelines. All public functions must have docstrings and type hints.
2. **Error Handling**: Never output raw tracebacks directly to standard output. Use `logger.log_exception` to route traces to file logs.
3. **Immutability**: Maintain immutability patterns. Return new copies of configuration profiles rather than mutating them.
4. **Backward Compatibility**: Ensure schema changes increment the `config_version` and include appropriate defaults.
