"""
book_reader.py — Read PDF and EPUB files and extract plain text.
"""

import os
from pathlib import Path


def read_pdf(filepath: str) -> str:
    """Extract all text from a PDF file using PyMuPDF."""
    import fitz  # PyMuPDF

    doc = fitz.open(filepath)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text")
        if text.strip():
            pages.append(f"--- Page {i + 1} ---\n{text.strip()}")
    doc.close()
    return "\n\n".join(pages)


def read_epub(filepath: str) -> str:
    """Extract all text from an EPUB file using ebooklib + BeautifulSoup."""
    import ebooklib
    from ebooklib import epub
    from bs4 import BeautifulSoup

    book = epub.read_epub(filepath, options={"ignore_ncx": True})
    chapters = []
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_content(), "html.parser")
        text = soup.get_text(separator="\n", strip=True)
        if text.strip():
            chapters.append(text.strip())
    return "\n\n".join(chapters)


def read_book(filepath: str) -> str:
    """
    Read a book file (PDF or EPUB) and return its text content.
    Raises ValueError for unsupported formats.
    """
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return read_pdf(filepath)
    elif ext == ".epub":
        return read_epub(filepath)
    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .pdf, .epub, or .txt")


def list_books(directory: str) -> list[str]:
    """List all supported book files in a directory."""
    supported = {".pdf", ".epub", ".txt"}
    books = []
    for f in Path(directory).iterdir():
        if f.suffix.lower() in supported and f.is_file():
            books.append(str(f))
    return sorted(books)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python book_reader.py <file_path>")
        print("Supported formats: .pdf, .epub, .txt")
        sys.exit(1)

    filepath = sys.argv[1]
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    text = read_book(filepath)
    print(f"=== Extracted {len(text):,} characters from {Path(filepath).name} ===\n")
    # Print first 2000 characters as preview
    print(text[:2000])
    if len(text) > 2000:
        print(f"\n... [{len(text) - 2000:,} more characters] ...")
