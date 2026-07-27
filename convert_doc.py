"""
Markdown to DOCX Converter with README Link Support
Version: 1.1
Author: Craig Wilson
Date: 2025-02-20
Description:
    This script reads a Markdown README file, extracts links to other markdown documents,
    converts each to HTML using the `markdown` module with table support,
    then parses the HTML using BeautifulSoup to construct a Word document
    using python-docx. The output is a consolidated DOCX representing all linked content.

Dependencies:
    - markdown
    - beautifulsoup4
    - python-docx
Usage:
    python md_to_docx.py <root_folder> <readme_path> <output_docx>

Example:
    python md_to_docx.py ./docs ./docs/README.md ./output/architecture.docx
"""

import os
import sys
import re
import markdown
from bs4 import BeautifulSoup
from docx import Document


def change_extension_to_docx(filename):
    """Return a filename with its extension changed to .docx.

    If the filename has an extension, it is replaced with .docx. If it
    does not have an extension, .docx is appended.

    Args:
        filename (str): The input filename.

    Returns:
        str: The filename with a .docx extension.
    """
    base, ext = os.path.splitext(filename)
    if not ext:
        return f"{filename}.docx"
    return f"{base}.docx"

def add_html_to_docx(md_content):
    """
    Add parsed HTML content to a Word document object.

    Args:
        markdown (text) content.
    """

def create_word_document(folder, file_name):

    input_path = os.path.join(folder, file_name)
    output_name = change_extension_to_docx(file_name)
    output_path = os.path.join(folder, output_name)

    if os.path.exists(input_path):
        with open(input_path, 'r', encoding='utf-8') as f:
            md = f.read()

            doc = Document()

            html = markdown.markdown(md)
            soup = BeautifulSoup(html, "html.parser")

            for element in soup.contents:
                if element.name and element.name.startswith('h'):
                    level = int(element.name[1])
                    doc.add_heading(element.get_text(), level=level)
                elif element.name == 'p':
                    doc.add_paragraph(element.get_text())
                elif element.name in ['ul', 'ol']:
                    style = 'List Bullet' if element.name == 'ul' else 'List Number'
                    for li in element.find_all('li'):
                        doc.add_paragraph(li.get_text(), style=style)
                elif element.name == 'blockquote':
                    doc.add_paragraph(element.get_text(), style='Intense Quote')
        
            doc.save(output_path)

    else:
            print(f"WARNING: File not found - {input_path}")
    print(f"Document saved to: {output_path}")
