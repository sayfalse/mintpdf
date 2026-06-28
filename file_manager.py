"""
File Manager module for Mint PDF.
Handles file system operations, file listing, file reading, and conflict resolution safely.
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional
from docx import Document # type: ignore

from logger import logger

# Supported file extensions for document input
SUPPORTED_EXTENSIONS = {".txt", ".md", ".docx"}

def ensure_directory_exists(path: Path) -> bool:
    """
    Checks if a directory exists, and creates it if not.
    
    Args:
        path: Path to the directory.
        
    Returns:
        True if directory exists or was successfully created, False otherwise.
    """
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {path}: {e}", exc_info=True)
        return False

def list_supported_files(directory: Path) -> List[Path]:
    """
    Lists all TXT, MD, and DOCX files in the directory.
    
    Args:
        directory: Directory to search in.
        
    Returns:
        A list of Path objects to the matching files.
    """
    if not directory.exists() or not directory.is_dir():
        logger.warning(f"Directory {directory} does not exist or is not a directory.")
        return []
        
    found_files = []
    try:
        for item in directory.iterdir():
            if item.is_file() and item.suffix.lower() in SUPPORTED_EXTENSIONS:
                found_files.append(item)
    except Exception as e:
        logger.error(f"Error listing files in {directory}: {e}", exc_info=True)
        
    return sorted(found_files, key=lambda p: p.name.lower())

def read_text_file(path: Path) -> str:
    """
    Safely reads text from a TXT or MD file, trying multiple encodings.
    
    Args:
        path: Path to the file.
        
    Returns:
        Content of the file as string.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
        except Exception as e:
            logger.error(f"Error reading file {path} with encoding {encoding}: {e}")
            raise e
            
    raise UnicodeDecodeError(
        "utf-8", b"", 0, 0, f"Unable to decode text file {path} with standard encodings."
    )

def read_docx_file(path: Path) -> str:
    """
    Safely reads text content from a Microsoft DOCX file.
    
    Args:
        path: Path to the file.
        
    Returns:
        Content of the file as string with paragraph breaks.
    """
    try:
        doc = Document(path)
        full_text = []
        for paragraph in doc.paragraphs:
            full_text.append(paragraph.text)
        return "\n".join(full_text)
    except Exception as e:
        logger.error(f"Error reading docx file {path}: {e}", exc_info=True)
        raise e

def read_document(path: Path) -> str:
    """
    Reads the content of any supported document type based on its suffix.
    
    Args:
        path: Path to the file.
        
    Returns:
        Content of the file as string.
    """
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return read_text_file(path)
    elif suffix == ".docx":
        return read_docx_file(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

def generate_auto_name(directory: Path, filename: str) -> Path:
    """
    Generates a unique filename in the directory by appending numbers (e.g. file_1.pdf).
    
    Args:
        directory: Target directory.
        filename: Initial filename.
        
    Returns:
        A Path object that does not collide with existing files.
    """
    path = directory / filename
    if not path.exists():
        return path
        
    stem = path.stem
    suffix = path.suffix
    counter = 1
    
    while True:
        new_path = directory / f"{stem}_{counter}{suffix}"
        if not new_path.exists():
            return new_path
        counter += 1
