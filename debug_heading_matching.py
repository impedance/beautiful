#!/usr/bin/env python3
"""Debug heading matching."""

import sys
from src.doc2md.heading_numbering import extract_heading_structure_from_toc
from bs4 import BeautifulSoup

def debug_heading_matching():
    docx_path = "dev-portal-admin.docx"
    
    # Get TOC structure
    heading_structure = extract_heading_structure_from_toc(docx_path)
    
    # Create title map
    title_to_info = {}
    for level, number, title in heading_structure[:10]:  # First 10 headings
        title_to_info[title.lower()] = (level, number, title)
        print(f"TOC: {level} {number} '{title}' -> '{title.lower()}'")
    
    print("\n" + "="*60 + "\n")
    
    # Sample HTML paragraphs from the actual output
    sample_paragraphs = [
        "Архитектура комплекса",
        "Основные компоненты", 
        "Состав плагинов",
        "Система управления файлами",
        "База данных",
        "Общие сведения",
        "Назначение",
        "Функции"
    ]
    
    print("Testing paragraph matching:")
    for para_text in sample_paragraphs:
        para_lower = para_text.lower()
        print(f"\nParagraph: '{para_text}' -> '{para_lower}'")
        
        # Check exact match
        if para_lower in title_to_info:
            level, number, original_title = title_to_info[para_lower]
            print(f"  ✅ EXACT MATCH: H{level} {number} {original_title}")
            continue
        
        # Try fuzzy matching
        best_match = None
        best_score = 0
        
        for toc_title_lower, (level, number, original_title) in title_to_info.items():
            # Calculate similarity
            para_words = set(para_lower.split())
            toc_words = set(toc_title_lower.split())
            
            if len(para_words) > 0 and len(toc_words) > 0:
                intersection = len(para_words & toc_words)
                union = len(para_words | toc_words)
                score = intersection / union if union > 0 else 0
                
                # Also check if the text starts with the same words
                para_start = ' '.join(para_lower.split()[:3])  # First 3 words
                toc_start = ' '.join(toc_title_lower.split()[:3])
                if para_start == toc_start and len(para_start.strip()) > 0:
                    score += 0.3  # Boost score for matching start
                
                if score > 0.3:  # Show candidates
                    print(f"    Candidate: '{original_title}' score={score:.3f}")
                
                if score > best_score and score > 0.6:  # Higher threshold
                    best_score = score
                    best_match = (level, number, original_title)
        
        if best_match:
            level, number, original_title = best_match
            print(f"  ✅ FUZZY MATCH: H{level} {number} {original_title} (score={best_score:.3f})")
        else:
            print(f"  ❌ NO MATCH FOUND")

if __name__ == "__main__":
    debug_heading_matching()