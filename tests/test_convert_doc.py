import os
from docx import Document
from convert_doc import add_runs_to_paragraph, create_word_document
from bs4 import BeautifulSoup
import markdown

def test_add_runs_to_paragraph():
    md = "Hello **world** and *everyone* and ***bold-italic***."
    html = markdown.markdown(md)
    soup = BeautifulSoup(html, "html.parser")
    
    # We should have a single <p> element
    p_element = soup.find('p')
    assert p_element is not None
    
    doc = Document()
    p = doc.add_paragraph()
    add_runs_to_paragraph(p, p_element)
    
    # We expect several runs:
    # 1. "Hello "
    # 2. "world" (bold=True)
    # 3. " and "
    # 4. "everyone" (italic=True)
    # 5. " and "
    # 6. "bold-italic" (bold=True, italic=True)
    # 7. "."
    runs = p.runs
    assert len(runs) >= 6
    
    # Find the run containing "world"
    world_run = next(r for r in runs if r.text == "world")
    assert world_run.bold is True
    assert world_run.italic is not True
    
    # Find the run containing "everyone"
    everyone_run = next(r for r in runs if r.text == "everyone")
    assert everyone_run.bold is not True
    assert everyone_run.italic is True
    
    # Find the run containing "bold-italic"
    bi_run = next(r for r in runs if r.text == "bold-italic")
    assert bi_run.bold is True
    assert bi_run.italic is True

def test_horizontal_rule(tmp_path):
    from docx.oxml.ns import qn
    md_content = "Paragraph 1\n\n---\n\nParagraph 2"
    temp_md = tmp_path / "test.md"
    temp_md.write_text(md_content, encoding='utf-8')
    
    create_word_document(str(tmp_path), "test.md")
    
    output_docx = tmp_path / "test.docx"
    assert output_docx.exists()
    
    doc = Document(str(output_docx))
    assert len(doc.paragraphs) == 3
    
    # Check that the second paragraph has bottom border XML settings
    p = doc.paragraphs[1]
    pPr = p._p.get_or_add_pPr()
    pBdr = pPr.find(qn('w:pBdr'))
    assert pBdr is not None
    bottom = pBdr.find(qn('w:bottom'))
    assert bottom is not None
    assert bottom.get(qn('w:val')) == 'single'

