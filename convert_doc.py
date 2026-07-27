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
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


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

def add_runs_to_paragraph(paragraph, parent_element):
    """
    Recursively processes parent_element's children (text nodes and inline formatting tags)
    and adds them as runs to the paragraph with correct bold/italic formatting.
    """
    for child in parent_element.children:
        if child.name is None:  # Plain text node
            paragraph.add_run(child)
        else:
            is_bold = child.name in ['strong', 'b']
            is_italic = child.name in ['em', 'i']
            
            def traverse(node, bold=False, italic=False):
                if node.name is None:
                    run = paragraph.add_run(node)
                    if bold:
                        run.bold = True
                    if italic:
                        run.italic = True
                else:
                    new_bold = bold or (node.name in ['strong', 'b'])
                    new_italic = italic or (node.name in ['em', 'i'])
                    for sub_child in node.children:
                        traverse(sub_child, new_bold, new_italic)
            
            traverse(child, is_bold, is_italic)

def add_horizontal_rule(paragraph):
    """
    Adds a horizontal rule (bottom border) to a python-docx paragraph.
    """
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), 'auto')
    pBdr.append(bottom)
    pPr.append(pBdr)

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
                if element.name and len(element.name) == 2 and element.name[0] == 'h' and element.name[1].isdigit():
                    level = int(element.name[1])
                    p = doc.add_heading('', level=level)
                    add_runs_to_paragraph(p, element)
                elif element.name == 'p':
                    p = doc.add_paragraph()
                    add_runs_to_paragraph(p, element)
                elif element.name in ['ul', 'ol']:
                    style = 'List Bullet' if element.name == 'ul' else 'List Number'
                    for li in element.find_all('li'):
                        p = doc.add_paragraph(style=style)
                        add_runs_to_paragraph(p, li)
                elif element.name == 'blockquote':
                    p = doc.add_paragraph(style='Intense Quote')
                    add_runs_to_paragraph(p, element)
                elif element.name == 'hr':
                    p = doc.add_paragraph()
                    add_horizontal_rule(p)
        
            doc.save(output_path)

    else:
        print(f"WARNING: File not found - {input_path}")
    print(f"Document saved to: {output_path}")
