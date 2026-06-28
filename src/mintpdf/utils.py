"""
Utility helper functions for Mint PDF.
Includes terminal clearing, text formatting, and measurements conversion.
"""

import os
import sys


def clear_screen() -> None:
    """Clears the terminal screen across different operating systems."""
    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")


def pt_to_inch(points: float) -> float:
    """Converts ReportLab points to inches (72 points = 1 inch)."""
    return points / 72.0


def inch_to_pt(inches: float) -> float:
    """Converts inches to ReportLab points (72 points = 1 inch)."""
    return inches * 72.0


def format_bytes(size_bytes: int) -> str:
    """Formats raw bytes size into human-readable format (KB, MB, etc.)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def truncate_text(text: str, max_chars: int = 100) -> str:
    """Truncates text to max_chars and appends ellipsis if truncated."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "..."
