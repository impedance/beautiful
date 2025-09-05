#!/usr/bin/env python3
"""Test heading conversion with a sample HTML."""

import sys
from src.doc2md.heading_numbering import add_numbering_to_html

def test_conversion():
    # Sample HTML that might come from Mammoth
    sample_html = '''
    <html><body>
    <p>Общие сведения</p>
    <p>Веб-интерфейс</p>
    <p>Подготовка конфигурационных файлов</p>
    <p>Some other paragraph</p>
    </body></html>
    '''
    
    docx_path = "rosa-mr.docx"
    
    print("Original HTML:")
    print(sample_html)
    print("\n" + "="*50 + "\n")
    
    result = add_numbering_to_html(sample_html, docx_path)
    
    print("Converted HTML:")
    print(result)
    
    # Check specifically for the 4.1.2.1 case
    if "4.1.2.1" in result:
        print(f"\n✅ Found 4.1.2.1 heading!")
    else:
        print(f"\n❌ Did not find 4.1.2.1 heading")

if __name__ == "__main__":
    test_conversion()