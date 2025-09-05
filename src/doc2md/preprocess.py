"""Utilities for preprocessing DOCX files."""

from __future__ import annotations

import os
import subprocess

import mammoth


def convert_docx_to_html(docx_path: str, style_map_path: str) -> str:
    """Convert DOCX to HTML using a Mammoth style map."""
    with open(docx_path, "rb") as docx_file, open(
        style_map_path, "r", encoding="utf-8"
    ) as style_map_file:
        style_map = style_map_file.read()
        result = mammoth.convert_to_html(docx_file, style_map=style_map)
    return result.value


def extract_images(docx_path: str, output_dir: str) -> None:
    """Extract images from DOCX using Pandoc."""
    os.makedirs(output_dir, exist_ok=True)
    command = [
        "pandoc",
        docx_path,
        "--extract-media",
        output_dir,
        "-t",
        "markdown",
        "-o",
        os.devnull,
    ]
    subprocess.run(command, check=True)
