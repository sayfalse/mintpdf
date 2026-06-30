"""
CLI module for Mint PDF.
Implements the interactive console UI, menus, wizard flows, and user inputs using Rich.
Supports consistent visual styling, progress bars, validation, and navigation hooks.
"""

import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.progress import (  # type: ignore
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

from .file_manager import (
    ensure_directory_exists,
    generate_auto_name,
    read_document,
)
from .logger import log_exception, logger
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
from .settings import AppSettings, FontEnum, MarginsSettings, PageSizeEnum, ThemeEnum
from .utils import clear_screen

# Global Console Instance
console = Console()


class NavigationBack(Exception):
    """Raised when a user inputs 'back' or 'b' to go back one step."""

    pass


class NavigationCancel(Exception):
    """Raised when a user inputs 'cancel' or 'c' to abort the current flow."""

    pass


class NavigationExit(Exception):
    """Raised when a user inputs 'exit' or 'e' to terminate the program."""

    pass


class MintCLI:
    """High-fidelity CLI handler for the Mint PDF terminal application."""

    def __init__(
        self,
        settings: AppSettings,
        config_service: ConfigurationService,
        theme_service: ThemeService,
        template_service: TemplateService,
        font_service: FontService,
        analysis_service: DocumentAnalysisService,
        metadata_service: MetadataService,
        cover_page_service: CoverPageService,
        toc_service: TOCService,
        export_service: ExportService,
    ):
        self.settings = settings
        self.config_service = config_service
        self.theme_service = theme_service
        self.template_service = template_service
        self.font_service = font_service
        self.analysis_service = analysis_service
        self.metadata_service = metadata_service
        self.cover_page_service = cover_page_service
        self.toc_service = toc_service
        self.export_service = export_service

    def _prompt(
        self,
        prompt_text: str,
        default: Optional[str] = None,
        choices: Optional[List[str]] = None,
        show_choices: bool = True,
    ) -> str:
        """
        Custom wrapper around Rich prompt that intercepts navigation commands.
        Supports:
          - 'b' or 'back' -> NavigationBack
          - 'c' or 'cancel' -> NavigationCancel
          - 'e' or 'exit' -> NavigationExit
        """
        nav_help = " [dim]([b]ack/[c]ancel/[e]xit)[/dim]"
        full_prompt = f"{prompt_text}{nav_help}"

        nav_choices = ["b", "back", "c", "cancel", "e", "exit"]
        extended_choices = None
        if choices:
            extended_choices = choices + nav_choices
            extended_choices = [c.lower() for c in extended_choices]

        raw_response = Prompt.ask(
            full_prompt,
            default=default,
            choices=extended_choices,
            show_choices=show_choices,
            console=console,
        )
        response = str(raw_response).strip() if raw_response is not None else ""

        resp_lower = response.lower()
        if resp_lower in ("b", "back"):
            raise NavigationBack()
        elif resp_lower in ("c", "cancel"):
            raise NavigationCancel()
        elif resp_lower in ("e", "exit"):
            raise NavigationExit()

        return response

    def run(self) -> None:
        """Starts the main application loop."""
        while True:
            try:
                clear_screen()
                self._draw_header()
                self._draw_main_menu()

                choice = Prompt.ask(
                    "Select an option (1-7)",
                    choices=["1", "2", "3", "4", "5", "6", "7"],
                    show_choices=False,
                    console=console,
                ).strip()

                if choice == "1":
                    self.create_new_pdf_flow()
                elif choice == "2":
                    self.open_existing_project_flow()
                elif choice == "3":
                    self.browse_templates_flow()
                elif choice == "4":
                    self.settings_flow()
                elif choice == "5":
                    self.help_flow()
                elif choice == "6":
                    self.about_flow()
                elif choice == "7":
                    self.exit_app()
            except NavigationCancel:
                self._show_info_panel("Operation cancelled. Returning to main menu.")
                self._wait_for_key()
            except NavigationBack:
                pass  # Already at root menu
            except NavigationExit:
                self.exit_app()
            except Exception as e:
                log_exception(e, "Unexpected error in CLI loop")
                self._show_error_panel(
                    f"An unexpected error occurred: {e}\nSee logs/mint_pdf.log for full details."
                )
                self._wait_for_key()

    # ==========================================
    # STYLIZED RICH PANELS
    # ==========================================
    def _draw_header(self) -> None:
        """Draws the beautiful Mint PDF banner."""
        banner = Text.assemble(
            (" 🌿 MINT PDF ", "bold green reverse"),
            (" — AI-Free Professional PDF Generator ", "bold white"),
            ("v1.0.0", "dim green"),
        )
        console.print(
            Panel(Align.center(banner), style="green", border_style="green", expand=False)
        )
        console.print(f"[dim]Output Folder: {self.settings.output_dir}[/dim]\n")

    def _draw_main_menu(self) -> None:
        """Prints the list of main menu choices."""
        table = Table(show_header=False, box=None)
        table.add_row(
            "[bold green]1.[/bold green] Create New PDF",
            "[dim white]Convert text, markdown, or docx into styled PDF[/dim white]",
        )
        table.add_row(
            "[bold green]2.[/bold green] Open Existing Project",
            "[dim white]List and inspect previously generated output files[/dim white]",
        )
        table.add_row(
            "[bold green]3.[/bold green] Browse Templates",
            "[dim white]Explore 25+ professional document structures[/dim white]",
        )
        table.add_row(
            "[bold green]4.[/bold green] Settings",
            "[dim white]Configure default fonts, margins, page dimensions[/dim white]",
        )
        table.add_row(
            "[bold green]5.[/bold green] Help",
            "[dim white]Usage documentation, shortcuts, FAQ[/dim white]",
        )
        table.add_row(
            "[bold green]6.[/bold green] About",
            "[dim white]Mint PDF application context[/dim white]",
        )
        table.add_row(
            "[bold green]7.[/bold green] Exit", "[dim white]Safely quit application[/dim white]"
        )

        console.print(
            Panel(
                table,
                title="[bold green]Main Menu[/bold green]",
                border_style="green",
                expand=False,
            )
        )
        console.print(
            "\n[dim]At any prompt, type 'b' for Back, 'c' for Cancel, or 'e' to Exit.[/dim]\n"
        )

    def _show_success_panel(self, msg: str) -> None:
        console.print(
            Panel(f"[bold green]✓ SUCCESS:[/bold green] {msg}", border_style="green", expand=False)
        )

    def _show_warning_panel(self, msg: str) -> None:
        console.print(
            Panel(
                f"[bold yellow]! WARNING:[/bold yellow] {msg}", border_style="yellow", expand=False
            )
        )

    def _show_error_panel(self, msg: str) -> None:
        console.print(
            Panel(f"[bold red]❌ ERROR:[/bold red] {msg}", border_style="red", expand=False)
        )

    def _show_info_panel(self, msg: str) -> None:
        console.print(
            Panel(f"[bold cyan]i INFO:[/bold cyan] {msg}", border_style="cyan", expand=False)
        )

    def _wait_for_key(self) -> None:
        console.print("\n[dim]Press Enter to continue...[/dim]")
        sys.stdin.readline()

    def exit_app(self) -> None:
        console.print("\n[bold green]Thank you for using Mint PDF! Goodbye. 🌿[/bold green]\n")
        sys.exit(0)

    # ==========================================
    # WORKFLOW: CREATE NEW PDF
    # ==========================================
    def create_new_pdf_flow(self) -> None:
        """Runs the 12-step PDF creation workflow."""
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 1 of 12: Accept Text Input[/bold green]",
                border_style="green",
                expand=False,
            )
        )

        content = ""
        orig_filename = None

        while True:
            try:
                console.print("\nChoose input method:")
                console.print("  [green]1.[/green] Paste text directly")
                console.print("  [green]2.[/green] Load from file (TXT, MD, DOCX)")
                method = self._prompt("Select option (1-2)", default="1", choices=["1", "2"])

                if method == "1":
                    console.print(
                        "\n[yellow]Paste your text below. When done, press Ctrl+Z then Enter (Windows) or Ctrl+D (Unix) to submit:[/yellow]\n"
                    )
                    lines = sys.stdin.read()
                    content = lines
                    break
                elif method == "2":
                    filepath_str = self._prompt("Enter the absolute file path to load")
                    path = Path(filepath_str).expanduser().resolve()
                    if not path.exists():
                        self._show_error_panel(f"File {path} does not exist.")
                        continue
                    if path.suffix.lower() not in [".txt", ".md", ".docx"]:
                        self._show_error_panel(
                            "Unsupported file format. Please use .txt, .md, or .docx."
                        )
                        continue

                    try:
                        content = read_document(path)
                        orig_filename = path.name
                        console.print(
                            f"[green]✓ Successfully loaded {len(content)} characters from {path.name}[/green]"
                        )
                        break
                    except Exception as e:
                        log_exception(e, f"Failed to load document: {path}")
                        self._show_error_panel(f"Failed to read document: {e}")
                        continue
            except NavigationBack:
                return

        if not content.strip():
            self._show_error_panel("Empty content. Cannot generate PDF.")
            self._wait_for_key()
            return

        # Step 2: Document analysis
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 2 of 12: Running Document Analyzer[/bold green]",
                border_style="green",
                expand=False,
            )
        )
        with console.status("[bold blue]Analyzing document structure offline...[/bold blue]"):
            analysis = self.analysis_service.analyze(content, orig_filename)
            time.sleep(0.5)  # subtle timing for visual comfort

        # Print analyzer results
        table = Table(title="Structure Metrics", expand=False, show_lines=True)
        table.add_column("Structural Element", style="cyan bold")
        table.add_column("Count", style="magenta", justify="right")
        table.add_row("Detected Title", analysis.title)
        table.add_row("Document Category", analysis.document_type)
        table.add_row("Headings (H1)", str(analysis.headings_count))
        table.add_row("Subheadings (H2/H3)", str(analysis.subheadings_count))
        table.add_row("Paragraph Blocks", str(analysis.paragraphs_count))
        table.add_row("List Items", str(analysis.lists_count))
        table.add_row("Tables", str(analysis.tables_count))
        table.add_row("Images", str(analysis.images_count))
        table.add_row("Quotes", str(analysis.quotes_count))
        table.add_row("Code Blocks", str(analysis.code_blocks_count))
        table.add_row("References", str(analysis.references_count))
        table.add_row("Estimated Pages", str(analysis.estimated_pages))
        console.print(table)

        rec_table = Table(title="Heuristic Recommendations", show_header=False, box=None)
        rec_table.add_row(
            "[yellow]Recommended Template:[/yellow]",
            f"[cyan]{analysis.recommended_template}[/cyan]",
        )
        rec_table.add_row(
            "[yellow]Recommended Theme:[/yellow]", f"[cyan]{analysis.recommended_theme}[/cyan]"
        )
        rec_table.add_row(
            "[yellow]Recommended Font:[/yellow]", f"[cyan]{analysis.recommended_font}[/cyan]"
        )
        rec_table.add_row(
            "[yellow]Suggested Filename:[/yellow]", f"[cyan]{analysis.recommended_filename}[/cyan]"
        )
        console.print(Panel(rec_table, border_style="yellow", expand=False))

        self._wait_for_key()

        # Step 3: Collect metadata
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 3 of 12: Collect Document Metadata[/bold green]",
                border_style="green",
                expand=False,
            )
        )
        try:
            title = self._prompt("Document Title", default=analysis.title)
            subtitle = self._prompt("Subtitle (optional)", default="")
            author = self._prompt("Author (optional)", default="")
            org = self._prompt("Organization (optional)", default="")
            doc_date = self._prompt("Date", default=datetime.now().strftime("%Y-%m-%d"))
            ver = self._prompt("Version", default="1.0.0")
            desc = self._prompt("Description / Abstract (optional)", default="")
        except NavigationBack:
            # Restart flow
            self.create_new_pdf_flow()
            return

        metadata = self.metadata_service.create_metadata(
            title=title,
            subtitle=subtitle if subtitle else None,
            author=author if author else None,
            organization=org if org else None,
            date=doc_date,
            version=ver,
            description=desc if desc else None,
        )

        # Step 4: Template selection
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 4 of 12: Layout Template Selection[/bold green]",
                border_style="green",
                expand=False,
            )
        )
        templates = self.template_service.get_all_templates()

        # Display templates in standard columns
        t_table = Table(title="Available Templates", show_lines=True)
        t_table.add_column("No.", style="cyan", justify="right")
        t_table.add_column("Name", style="green bold")
        t_table.add_column("Category", style="magenta")
        t_table.add_column("Description", style="white")

        for idx, t in enumerate(templates):
            t_table.add_row(str(idx + 1), t.name, t.category, t.description)
        console.print(t_table)

        template_names = self.template_service.get_template_names()
        try:
            tmpl_choice = self._prompt(
                "Choose layout template",
                default=analysis.recommended_template,
                choices=template_names,
            )
            selected_template = self.template_service.get_template(tmpl_choice)
        except NavigationBack:
            self.create_new_pdf_flow()
            return

        # Step 5: Theme selection
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 5 of 12: Theme Selection[/bold green]",
                border_style="green",
                expand=False,
            )
        )
        themes = self.theme_service.get_all_theme_names()

        th_table = Table(title="Available Themes", show_lines=True)
        th_table.add_column("Name", style="cyan bold")
        th_table.add_column("Primary Color", style="white")
        th_table.add_column("Secondary Color", style="white")
        th_table.add_column("Accent Color", style="white")

        for name in themes:
            th = self.theme_service.get_theme(name)
            th_table.add_row(
                name,
                f"[{th.primary}]{th.primary}[/]",
                f"[{th.secondary}]{th.secondary}[/]",
                f"[{th.accent}]{th.accent}[/]",
            )
        console.print(th_table)

        try:
            theme_choice = self._prompt(
                "Choose visual theme", default=analysis.recommended_theme, choices=themes
            )
            selected_theme = self.theme_service.get_theme(theme_choice)
        except NavigationBack:
            self.create_new_pdf_flow()
            return

        # Step 6: Font selection
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 6 of 12: Typography Font Selection[/bold green]",
                border_style="green",
                expand=False,
            )
        )
        fonts = self.font_service.get_supported_fonts()
        for idx, fn in enumerate(fonts):
            console.print(f"  [green]{idx+1:2d}.[/green] {fn}")
        try:
            font_choice = self._prompt(
                "Choose font family", default=analysis.recommended_font, choices=fonts
            )
        except NavigationBack:
            self.create_new_pdf_flow()
            return

        # Step 7: Page settings
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 7 of 12: Page Configuration[/bold green]",
                border_style="green",
                expand=False,
            )
        )

        # Load from template configurations
        doc_settings = AppSettings(
            output_dir=self.settings.output_dir,
            theme=ThemeEnum.from_str(selected_theme.name),
            default_template=selected_template.name,
            default_font=FontEnum.from_str(font_choice),
            page_size=self.settings.page_size,
            margins=MarginsSettings(**(selected_template.margins or {})),
            language=self.settings.language,
            auto_toc=self.settings.auto_toc,
            auto_page_numbers=self.settings.auto_page_numbers,
        )

        # Display current template margins
        console.print(f"  Page Dimensions:     [cyan]{doc_settings.page_size}[/cyan]")
        console.print(
            f"  Margins (Left/Right):[cyan]{doc_settings.margins.left}pt / {doc_settings.margins.right}pt[/cyan]"
        )
        console.print(
            f"  Margins (Top/Bottom):[cyan]{doc_settings.margins.top}pt / {doc_settings.margins.bottom}pt[/cyan]"
        )
        console.print(f"  Auto Page Numbers:   [cyan]{doc_settings.auto_page_numbers}[/cyan]")
        console.print(f"  Auto TOC:            [cyan]{doc_settings.auto_toc}[/cyan]")

        try:
            custom_cfg = Confirm.ask(
                "\nCustomize these page settings for this document?", default=False, console=console
            )

            if custom_cfg:
                page_sz = self._prompt(
                    "Page size",
                    default=doc_settings.page_size.value,
                    choices=["LETTER", "A4", "LEGAL"],
                )
                doc_settings.page_size = PageSizeEnum.from_str(page_sz)

                top_m = float(
                    self._prompt("Top margin (pt)", default=str(doc_settings.margins.top))
                )
                bottom_m = float(
                    self._prompt("Bottom margin (pt)", default=str(doc_settings.margins.bottom))
                )
                left_m = float(
                    self._prompt("Left margin (pt)", default=str(doc_settings.margins.left))
                )
                right_m = float(
                    self._prompt("Right margin (pt)", default=str(doc_settings.margins.right))
                )

                doc_settings.margins = MarginsSettings(
                    top=top_m, bottom=bottom_m, left=left_m, right=right_m
                )

                auto_pg = Confirm.ask(
                    "Enable page numbering?",
                    default=doc_settings.auto_page_numbers,
                    console=console,
                )
                doc_settings.auto_page_numbers = auto_pg

                auto_t = Confirm.ask(
                    "Enable table of contents?", default=doc_settings.auto_toc, console=console
                )
                doc_settings.auto_toc = auto_t
        except NavigationBack:
            self.create_new_pdf_flow()
            return

        # Step 8: Cover Page
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 8 of 12: Cover Page Setup[/bold green]",
                border_style="green",
                expand=False,
            )
        )
        try:
            has_cover = Confirm.ask(
                "Include a professional cover page in the document?", default=True, console=console
            )
        except NavigationBack:
            self.create_new_pdf_flow()
            return

        # Step 9-11: Summarize Pre-generation Settings
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 9-11 of 12: Visual Summary & Validation[/bold green]",
                border_style="green",
                expand=False,
            )
        )

        summary_table = Table(title="Pre-Generation Summary", expand=True, show_lines=True)
        summary_table.add_column("Section", style="yellow bold", width=25)
        summary_table.add_column("Property Settings", style="white")

        summary_table.add_row("Document Title", metadata.title)
        summary_table.add_row("Author", metadata.author or "Not Specified")
        summary_table.add_row(
            "Design Theme", f"{selected_theme.name} (Primary: {selected_theme.primary})"
        )
        summary_table.add_row(
            "Layout Template", f"{selected_template.name} ({selected_template.category})"
        )
        summary_table.add_row("Font Family", font_choice)
        summary_table.add_row(
            "Page Configuration",
            f"Size: {doc_settings.page_size.value} | Margins: L={doc_settings.margins.left}pt, R={doc_settings.margins.right}pt, T={doc_settings.margins.top}pt, B={doc_settings.margins.bottom}pt",
        )
        summary_table.add_row("Auto Outline Bookmarks", "Enabled")
        summary_table.add_row("Cover Page Included", "Yes" if has_cover else "No")
        summary_table.add_row("TOC Section Generated", "Yes" if doc_settings.auto_toc else "No")
        summary_table.add_row(
            "Page Numbers Printed", "Yes" if doc_settings.auto_page_numbers else "No"
        )

        console.print(summary_table)

        # Step 12: PDF Name Collision resolving
        out_dir = Path(self.settings.output_dir)
        ensure_directory_exists(out_dir)

        suggested_name = analysis.recommended_filename
        final_path = out_dir / suggested_name

        if final_path.exists():
            console.print(
                f"\n[bold yellow]Collision warning: Output file '{suggested_name}' already exists.[/bold yellow]"
            )
            console.print("  [green]1.[/green] Replace existing file")
            console.print("  [green]2.[/green] Rename automatically (e.g. filename_1.pdf)")
            console.print("  [green]3.[/green] Enter new name manually")
            console.print("  [green]4.[/green] Cancel generation")

            try:
                collision_choice = self._prompt(
                    "Select collision recovery option (1-4)",
                    default="2",
                    choices=["1", "2", "3", "4"],
                )
                if collision_choice == "1":
                    logger.info(f"User chose to overwrite: {final_path.name}")
                elif collision_choice == "2":
                    final_path = generate_auto_name(out_dir, suggested_name)
                    console.print(f"[green]✓ Renamed automatically to: {final_path.name}[/green]")
                elif collision_choice == "3":
                    new_name_input = self._prompt("Enter new filename (including .pdf)")
                    if not new_name_input.endswith(".pdf"):
                        new_name_input += ".pdf"
                    final_path = out_dir / new_name_input
                elif collision_choice == "4":
                    raise NavigationCancel()
            except NavigationBack:
                self.create_new_pdf_flow()
                return

        try:
            proceed = Confirm.ask(
                "\nProceed to compile PDF document?", default=True, console=console
            )
            if not proceed:
                raise NavigationCancel()
        except NavigationBack:
            self.create_new_pdf_flow()
            return

        # Perform actual generation using interactive Progress Bar
        clear_screen()
        console.print(
            Panel(
                "[bold green]Step 12 of 12: Compiling PDF Document[/bold green]",
                border_style="green",
                expand=False,
            )
        )

        success = False
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(bar_width=30),
            TaskProgressColumn(),
            console=console,
        ) as progress:

            t1 = progress.add_task("Reading source content...", total=100)
            time.sleep(0.15)
            progress.update(t1, completed=100)

            t2 = progress.add_task("Running structural analyzer...", total=100)
            time.sleep(0.2)
            progress.update(t2, completed=100)

            t3 = progress.add_task("Formatting page layouts...", total=100)
            time.sleep(0.25)
            progress.update(t3, completed=100)

            t4 = progress.add_task("Compiling PDF flowables...", total=100)
            success = self.export_service.export_to_pdf(
                content, final_path, metadata, doc_settings, has_cover=has_cover
            )
            progress.update(t4, completed=100)

        if success:
            self._show_success_panel(
                f"PDF document generated successfully!\nSaved path: [cyan]{final_path}[/cyan]"
            )
        else:
            self._show_error_panel(
                "Failed to compile PDF document. Check logs/mint_pdf.log for detail logs."
            )

        self._wait_for_key()

    # ==========================================
    # WORKFLOW: OPEN EXISTING PROJECT
    # ==========================================
    def open_existing_project_flow(self) -> None:
        """Lists previously generated PDF files inside the output folder."""
        clear_screen()
        console.print(
            Panel(
                "[bold green]Open Existing Project[/bold green]", border_style="green", expand=False
            )
        )

        out_dir = Path(self.settings.output_dir)
        ensure_directory_exists(out_dir)

        pdf_files = []
        try:
            for item in out_dir.iterdir():
                if item.is_file() and item.suffix.lower() == ".pdf":
                    pdf_files.append(item)
        except Exception as e:
            log_exception(e, f"Error checking output folder: {out_dir}")
            self._show_error_panel(f"Failed to scan output directory: {e}")
            self._wait_for_key()
            return

        pdf_files = sorted(pdf_files, key=lambda p: p.stat().st_mtime, reverse=True)

        if not pdf_files:
            self._show_warning_panel("No generated PDFs found in the output folder.")
            self._wait_for_key()
            return

        table = Table(title="Generated PDFs (Most Recent First)", expand=True, show_lines=True)
        table.add_column("No.", style="cyan", justify="right", width=5)
        table.add_column("Filename", style="green bold")
        table.add_column("File Size", style="magenta", justify="right")
        table.add_column("Generated Date", style="yellow")

        for idx, path in enumerate(pdf_files):
            size_kb = path.stat().st_size / 1024.0
            mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            table.add_row(str(idx + 1), path.name, f"{size_kb:.1f} KB", mtime)

        console.print(table)
        self._wait_for_key()

    # ==========================================
    # WORKFLOW: BROWSE TEMPLATES
    # ==========================================
    def browse_templates_flow(self) -> None:
        """Displays a structured table showing all 25+ templates."""
        clear_screen()
        console.print(
            Panel(
                "[bold green]Browse Templates Library[/bold green]",
                border_style="green",
                expand=False,
            )
        )

        table = Table(title="Mint PDF Templates Library", expand=True, show_lines=True)
        table.add_column("Name", style="green bold", width=20)
        table.add_column("Category", style="cyan", width=15)
        table.add_column("Description", style="white")

        for t in self.template_service.get_all_templates():
            table.add_row(t.name, t.category, t.description)

        console.print(table)
        self._wait_for_key()

    # ==========================================
    # WORKFLOW: SETTINGS
    # ==========================================
    def settings_flow(self) -> None:
        """Displays configuration menu to update specific settings."""
        while True:
            clear_screen()
            console.print(
                Panel(
                    "[bold green]Application Settings[/bold green]",
                    border_style="green",
                    expand=False,
                )
            )

            table = Table(show_header=False, box=None)
            table.add_row("[green]1.[/green] Output Directory", self.settings.output_dir)
            table.add_row("[green]2.[/green] Default Theme", self.settings.theme.value)
            table.add_row("[green]3.[/green] Default Template", self.settings.default_template)
            table.add_row("[green]4.[/green] Default Font", self.settings.default_font.value)
            table.add_row("[green]5.[/green] Default Page Size", self.settings.page_size.value)
            table.add_row(
                "[green]6.[/green] Default Margins",
                f"Top={self.settings.margins.top}pt, Bottom={self.settings.margins.bottom}pt, Left={self.settings.margins.left}pt, Right={self.settings.margins.right}pt",
            )
            table.add_row("[green]7.[/green] Default Language", self.settings.language)
            table.add_row("[green]8.[/green] Auto Table of Contents", str(self.settings.auto_toc))
            table.add_row(
                "[green]9.[/green] Auto Page Numbers", str(self.settings.auto_page_numbers)
            )

            console.print(Panel(table, title="Current Configuration Settings", border_style="cyan"))
            console.print(
                "\n[dim]Choose an item number (1-9) to modify, or type 'b' to save & return.[/dim]\n"
            )

            try:
                choice = self._prompt("Select option to modify (or 'b' to return)", default="b")

                if choice == "b":
                    self.config_service.save_config(self.settings)
                    break

                if choice == "1":
                    val = self._prompt("Enter Output Directory", default=self.settings.output_dir)
                    path = Path(val).expanduser().resolve()
                    if ensure_directory_exists(path):
                        self.settings.output_dir = str(path)
                        console.print("[green]✓ Output folder updated successfully.[/green]")
                    else:
                        self._show_error_panel("Folder could not be created/verified.")
                        self._wait_for_key()

                elif choice == "2":
                    themes = self.theme_service.get_all_theme_names()
                    val = self._prompt(
                        "Enter Default Theme", default=self.settings.theme.value, choices=themes
                    )
                    self.settings.theme = ThemeEnum.from_str(val)

                elif choice == "3":
                    templates = self.template_service.get_template_names()
                    val = self._prompt(
                        "Enter Default Template",
                        default=self.settings.default_template,
                        choices=templates,
                    )
                    self.settings.default_template = val

                elif choice == "4":
                    fonts = self.font_service.get_supported_fonts()
                    val = self._prompt(
                        "Enter Default Font",
                        default=self.settings.default_font.value,
                        choices=fonts,
                    )
                    self.settings.default_font = FontEnum.from_str(val)

                elif choice == "5":
                    val = self._prompt(
                        "Enter Default Page Size",
                        default=self.settings.page_size.value,
                        choices=["LETTER", "A4", "LEGAL"],
                    )
                    self.settings.page_size = PageSizeEnum.from_str(val)

                elif choice == "6":
                    top = float(
                        self._prompt("Top Margin (pt)", default=str(self.settings.margins.top))
                    )
                    bottom = float(
                        self._prompt(
                            "Bottom Margin (pt)", default=str(self.settings.margins.bottom)
                        )
                    )
                    left = float(
                        self._prompt("Left Margin (pt)", default=str(self.settings.margins.left))
                    )
                    right = float(
                        self._prompt("Right Margin (pt)", default=str(self.settings.margins.right))
                    )
                    self.settings.margins = MarginsSettings(
                        top=top, bottom=bottom, left=left, right=right
                    )

                elif choice == "7":
                    val = self._prompt("Enter Default Language", default=self.settings.language)
                    self.settings.language = val

                elif choice == "8":
                    bool_val = Confirm.ask(
                        "Enable Auto TOC by default?",
                        default=self.settings.auto_toc,
                        console=console,
                    )
                    self.settings.auto_toc = bool_val

                elif choice == "9":
                    bool_val = Confirm.ask(
                        "Enable Auto Page Numbers by default?",
                        default=self.settings.auto_page_numbers,
                        console=console,
                    )
                    self.settings.auto_page_numbers = bool_val

                # Save immediately upon every modification
                self.config_service.save_config(self.settings)

            except NavigationBack:
                self.config_service.save_config(self.settings)
                break
            except ValueError as ve:
                self._show_error_panel(f"Validation Error: {ve}")
                self._wait_for_key()

    # ==========================================
    # WORKFLOW: HELP
    # ==========================================
    def help_flow(self) -> None:
        """Displays help instructions and FAQs."""
        clear_screen()
        console.print(
            Panel(
                "[bold green]Help & Documentation[/bold green]", border_style="green", expand=False
            )
        )

        help_text = (
            "[bold cyan]Supported Input Formats:[/bold cyan]\n"
            "  - Plain Text (.txt): Basic whitespace formatting.\n"
            "  - Markdown (.md): Supports headings (#), code blocks (```), tables, lists, and quotes.\n"
            "  - Microsoft Word (.docx): Standard paragraph layout import.\n\n"
            "[bold cyan]Navigation Shortcuts (type in any prompt):[/bold cyan]\n"
            "  - [green]b[/green] or [green]back[/green]    : Return to previous input step.\n"
            "  - [green]c[/green] or [green]cancel[/green]  : Cancel current workflow and return to Main Menu.\n"
            "  - [green]e[/green] or [green]exit[/green]    : Close the program safely.\n\n"
            "[bold cyan]Offline Analyzer Engine:[/bold cyan]\n"
            "  Mint PDF parses formatting tokens automatically and recommends the best matched\n"
            "  combination of styling templates and themes. You can always override these suggestions."
        )
        console.print(Panel(help_text, title="Usage Guide", border_style="cyan"))
        self._wait_for_key()

    # ==========================================
    # WORKFLOW: ABOUT
    # ==========================================
    def about_flow(self) -> None:
        """Displays credits and general information."""
        clear_screen()

        about_text = (
            "[bold green]Mint PDF[/bold green]\n"
            "[yellow]Version 1.0.0[/yellow]\n\n"
            "A professional offline PDF generator built entirely in Python.\n"
            "Converts plain text and markdown documents into publication-quality prints.\n"
            "Designed for clean and modular local systems.\n\n"
            "[dim]Created by Antigravity under clean-architecture guidelines.[/dim]"
        )
        console.print(
            Panel(
                Align.center(about_text), title="About Mint PDF", border_style="green", expand=False
            )
        )
        self._wait_for_key()
