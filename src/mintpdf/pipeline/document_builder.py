import re
from typing import List, Tuple

from ..domain.models import (
    CodeBlock,
    Document,
    Heading,
    Image,
    Metadata,
    Paragraph,
    Quote,
    Section,
    Table,
)


class DocumentBuilder:
    """Stage 2: Document Builder. Parses raw markdown text into a domain Document model."""

    def build(self, text: str, metadata: Metadata) -> Document:
        sections: List[Section] = []
        current_section = Section(title=None)

        lines = text.splitlines()
        i = 0
        total_lines = len(lines)

        while i < total_lines:
            line = lines[i]
            line_stripped = line.strip()

            # Skip empty lines
            if not line_stripped:
                i += 1
                continue

            # 1. Code Block parsing (```)
            if line_stripped.startswith("```"):
                code_lines = []
                i += 1
                while i < total_lines and not lines[i].strip().startswith("```"):
                    code_lines.append(lines[i])
                    i += 1
                i += 1  # skip closing ```
                current_section.elements.append(CodeBlock(code="\n".join(code_lines)))
                continue

            # 2. Table parsing (|)
            if line_stripped.startswith("|"):
                table_lines = []
                while i < total_lines and lines[i].strip().startswith("|"):
                    table_lines.append(lines[i])
                    i += 1

                headers, rows = self._parse_table(table_lines)
                if headers:
                    current_section.elements.append(Table(headers=headers, rows=rows))
                continue

            # 3. Blockquotes (>)
            if line_stripped.startswith(">"):
                quote_lines = []
                while i < total_lines and lines[i].strip().startswith(">"):
                    quote_text = lines[i].strip()[1:].strip()
                    quote_lines.append(quote_text)
                    i += 1
                current_section.elements.append(Quote(text=" ".join(quote_lines)))
                continue

            # 4. Heading 1 (#)
            if line_stripped.startswith("# "):
                title_text = line_stripped[2:].strip()
                if current_section.title or current_section.elements:
                    sections.append(current_section)
                current_section = Section(title=title_text)
                current_section.elements.append(Heading(text=title_text, level=1))
                i += 1
                continue

            # 5. Heading 2 (##)
            if line_stripped.startswith("## "):
                title_text = line_stripped[3:].strip()
                current_section.elements.append(Heading(text=title_text, level=2))
                i += 1
                continue

            # 6. Heading 3 (###)
            if line_stripped.startswith("### "):
                title_text = line_stripped[4:].strip()
                current_section.elements.append(Heading(text=title_text, level=3))
                i += 1
                continue

            # 7. Images (![alt](path))
            if line_stripped.startswith("!["):
                img_match = re.match(r"^!\[(.*?)\]\((.*?)\)$", line_stripped)
                if img_match:
                    alt_text = img_match.group(1)
                    img_path_str = img_match.group(2)
                    current_section.elements.append(Image(path=img_path_str, caption=alt_text))
                i += 1
                continue

            # 8. Lists (Bullet and numbered lists)
            bullet_match = re.match(r"^(\s*)[-\*\+]\s+(.+)$", line)
            num_match = re.match(r"^(\s*)\d+\.\s+(.+)$", line)

            if bullet_match or num_match:
                while i < total_lines:
                    curr_line = lines[i]
                    b_match = re.match(r"^(\s*)[-\*\+]\s+(.+)$", curr_line)
                    n_match = re.match(r"^(\s*)\d+\.\s+(.+)$", curr_line)

                    if not (b_match or n_match):
                        break

                    current_section.elements.append(Paragraph(text=curr_line))
                    i += 1
                continue

            # 9. Default Paragraph block
            paragraph_lines = []
            while i < total_lines:
                curr_stripped = lines[i].strip()
                if not curr_stripped:
                    break
                if curr_stripped.startswith("#"):
                    break
                if curr_stripped.startswith(">"):
                    break
                if curr_stripped.startswith("|"):
                    break
                if curr_stripped.startswith("```"):
                    break
                if re.match(r"^(\s*)[-\*\+]\s+", lines[i]) or re.match(r"^(\s*)\d+\.\s+", lines[i]):
                    break

                paragraph_lines.append(curr_stripped)
                i += 1

            paragraph_text = " ".join(paragraph_lines)
            current_section.elements.append(Paragraph(text=paragraph_text))

        if current_section.title or current_section.elements:
            sections.append(current_section)

        return Document(metadata=metadata, sections=sections)

    def _parse_table(self, table_lines: List[str]) -> Tuple[List[str], List[List[str]]]:
        headers: List[str] = []
        rows: List[List[str]] = []

        for line in table_lines:
            line = line.strip()
            if not line.startswith("|") or not line.endswith("|"):
                continue

            parts = [p.strip() for p in line.split("|")[1:-1]]
            if all(re.match(r"^:?-+:?$", p) for p in parts):
                continue

            if not headers:
                headers = parts
            else:
                rows.append(parts)

        return headers, rows
