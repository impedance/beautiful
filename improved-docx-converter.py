#!/usr/bin/env python3
"""
Улучшенный DOCX to Markdown Converter
Правильно обрабатывает заголовки и структуру документа
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.shared import Pt
from docx.oxml.ns import qn
import xml.etree.ElementTree as ET


class ImprovedDocxToMarkdownConverter:
    def __init__(self, input_file: str, add_frontmatter: bool = False):
        self.doc = Document(input_file)
        self.markdown_lines = []
        self.in_code_block = False
        self.add_frontmatter = add_frontmatter
        self.heading_map = self._build_heading_map()
        self.skip_next_paragraph = False
        
    def _build_heading_map(self) -> Dict[str, int]:
        """Создает карту соответствия стилей заголовкам"""
        heading_map = {}
        
        # Стандартные стили Word
        for i in range(1, 10):
            heading_map[f'Heading {i}'] = i
            heading_map[f'heading {i}'] = i
            heading_map[f'Заголовок {i}'] = i
            
        # Проверяем кастомные стили в документе
        for style in self.doc.styles:
            style_name = style.name
            if style_name:
                # Проверяем по размеру шрифта для определения уровня
                try:
                    if hasattr(style, 'font') and style.font.size:
                        size_pt = style.font.size.pt
                        # Эвристика: большие размеры = более высокие уровни заголовков
                        if size_pt >= 24:
                            heading_map[style_name] = 1
                        elif size_pt >= 18:
                            heading_map[style_name] = 2
                        elif size_pt >= 14:
                            heading_map[style_name] = 3
                except:
                    pass
                    
        return heading_map
    
    def _is_heading(self, para: Paragraph) -> Optional[int]:
        """Определяет, является ли параграф заголовком и возвращает его уровень"""
        
        # 1. Проверка по стилю
        if para.style and para.style.name:
            style_name = para.style.name
            if style_name in self.heading_map:
                return self.heading_map[style_name]
        
        # 2. Проверка по outline level (уровень структуры)
        try:
            outline_lvl = para._element.xpath('.//w:outlineLvl/@w:val', 
                                            namespaces={'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'})
            if outline_lvl:
                return int(outline_lvl[0]) + 1
        except:
            pass
        
        # 3. Эвристика по форматированию
        text = para.text.strip()
        if text and len(text) < 100:  # Заголовки обычно короткие
            # Проверяем, все ли runs жирные
            all_bold = all(run.bold for run in para.runs if run.text.strip())
            
            # Проверяем размер шрифта
            if para.runs:
                first_run = para.runs[0]
                if first_run.font.size:
                    size_pt = first_run.font.size.pt
                    if all_bold or size_pt > 12:
                        # Определяем уровень по размеру
                        if size_pt >= 20:
                            return 1
                        elif size_pt >= 16:
                            return 2
                        elif size_pt >= 14:
                            return 3
                        elif all_bold:
                            return 4
        
        # 4. Проверка по паттернам текста
        if text:
            # Нумерованные заголовки типа "1. Общие сведения", "1.1 Назначение"
            if re.match(r'^[\d\.]+\s+[А-ЯA-Z]', text):
                # Определяем уровень по количеству точек
                dots = text.split()[0].count('.')
                return min(dots + 1, 6)
                
        return None
        
    def convert(self) -> str:
        """Основной метод конвертации"""
        
        # Добавляем frontmatter если нужно
        if self.add_frontmatter:
            self._add_frontmatter()
        
        # Обрабатываем элементы документа
        for element in self.doc.element.body:
            if self.skip_next_paragraph:
                self.skip_next_paragraph = False
                continue
                
            if element.tag.endswith('p'):
                self._process_paragraph(element)
            elif element.tag.endswith('tbl'):
                self._process_table(element)
                
        # Закрываем открытый блок кода, если есть
        if self.in_code_block:
            self.markdown_lines.append("```")
            self.markdown_lines.append('')
            
        return '\n'.join(self.markdown_lines)
    
    def _add_frontmatter(self):
        """Добавляет frontmatter в начало документа"""
        self.markdown_lines.extend([
            '---',
            'title: Заголовок документа',
            '',
            'readPrev:',
            '  to: /path/to/prev',
            '  label: Предыдущий раздел',
            '',
            'readNext:',
            '  to: /path/to/next',  
            '  label: Следующий раздел',
            '---',
            ''
        ])
    
    def _process_paragraph(self, element):
        """Обработка параграфа"""
        para = Paragraph(element, self.doc)
        text = para.text.strip()
        
        if not text:
            if not self.in_code_block:
                self.markdown_lines.append('')
            return
        
        # Проверяем, является ли это заголовком
        heading_level = self._is_heading(para)
        if heading_level:
            # Убираем нумерацию из заголовка если есть
            clean_text = re.sub(r'^[\d\.]+\s+', '', text)
            self.markdown_lines.append(f"{'#' * heading_level} {clean_text}")
            self.markdown_lines.append('')
            return
            
        # Обработка списков
        if self._is_list_item(para):
            self._process_list_item(para)
            
        # Обработка блоков кода
        elif self._is_code_block(para):
            self._process_code_block(para)
            
        # Обработка примечаний
        elif text.startswith('Примечание'):
            self.markdown_lines.append(f"> {text}")
            self.markdown_lines.append('')
            
        # Обычный параграф
        else:
            formatted_text = self._format_inline_text(para)
            if not self.in_code_block:
                self.markdown_lines.append(formatted_text)
                self.markdown_lines.append('')
            else:
                self.markdown_lines.append(formatted_text)
    
    def _process_table(self, element):
        """Обработка таблицы"""
        table = Table(element, self.doc)
        
        if not table.rows:
            return
            
        self.markdown_lines.append('')
        
        # Обработка заголовка таблицы
        header_row = table.rows[0]
        header_cells = [self._clean_cell_text(cell) for cell in header_row.cells]
        self.markdown_lines.append('| ' + ' | '.join(header_cells) + ' |')
        
        # Разделитель с правильным выравниванием
        separator_parts = []
        for cell in header_cells:
            # Можно добавить логику определения выравнивания
            separator_parts.append('-' * max(3, len(cell)))
        self.markdown_lines.append('| ' + ' | '.join(separator_parts) + ' |')
        
        # Обработка строк данных
        for row in table.rows[1:]:
            cells = [self._clean_cell_text(cell) for cell in row.cells]
            self.markdown_lines.append('| ' + ' | '.join(cells) + ' |')
            
        self.markdown_lines.append('')
        
        # Проверяем подпись к таблице
        self._add_table_caption(element)
    
    def _clean_cell_text(self, cell) -> str:
        """Очистка текста ячейки таблицы"""
        text = cell.text.strip()
        # Заменяем переносы строк на <br> для многострочных ячеек
        text = text.replace('\n', '<br>')
        # Экранируем символы pipe
        text = text.replace('|', '\\|')
        return text
    
    def _format_inline_text(self, para) -> str:
        """Форматирование inline элементов"""
        result = []
        
        for run in para.runs:
            text = run.text
            
            # Обработка кода
            if run.font.name and ('Mono' in run.font.name or 'Courier' in run.font.name):
                if '`' not in text:  # Избегаем двойного форматирования
                    text = f"`{text}`"
            # Жирный текст
            elif run.bold and text.strip():
                if not text.startswith('**'):
                    text = f"**{text}**"
            # Курсив
            elif run.italic and text.strip():
                if not text.startswith('*'):
                    text = f"*{text}*"
                
            result.append(text)
            
        return ''.join(result)
    
    def _is_list_item(self, para) -> bool:
        """Проверка, является ли параграф элементом списка"""
        # Проверяем по стилю
        if para.style and para.style.name:
            style_lower = para.style.name.lower()
            if 'list' in style_lower or 'bullet' in style_lower:
                return True
            
        # Проверяем по тексту
        text = para.text.strip()
        # Маркированный список
        if text.startswith(('- ', '• ', '* ', '− ')):
            return True
        # Нумерованный список (но не заголовок)
        if re.match(r'^[a-zа-я]\)', text):  # буквенная нумерация
            return True
        if re.match(r'^\d+\)', text):  # цифровая с закрывающей скобкой
            return True
            
        return False
    
    def _process_list_item(self, para):
        """Обработка элемента списка"""
        text = para.text.strip()
        
        # Определяем уровень вложенности
        indent_level = self._get_indent_level(para)
        indent = '  ' * indent_level
        
        # Удаляем маркеры из текста
        text = re.sub(r'^[-•*−]\s*', '', text)
        text = re.sub(r'^[a-zа-я]\)\s*', '', text)
        text = re.sub(r'^\d+\)\s*', '', text)
        
        # В markdown используем простые маркеры
        self.markdown_lines.append(f"{indent}- {text}")
    
    def _is_code_block(self, para) -> bool:
        """Проверка, является ли параграф блоком кода"""
        # Проверяем по стилю
        if para.style and 'Code' in para.style.name:
            return True
            
        # Проверяем по шрифту
        all_mono = all(
            run.font.name and ('Courier' in run.font.name or 'Mono' in run.font.name)
            for run in para.runs if run.text.strip()
        )
        if all_mono and para.runs:
            return True
                
        # Проверяем по содержимому
        text = para.text.strip()
        code_indicators = [
            'sudo ', 'docker ', 'systemctl ', '$ ', '# ',
            'git ', 'python ', 'npm ', 'pip ',
            'CREATE ', 'SELECT ', 'INSERT ',
            'function ', 'class ', 'def ', 'import ',
            'version:', 'services:', '{', '}'
        ]
        return any(text.startswith(ind) for ind in code_indicators)
    
    def _process_code_block(self, para):
        """Обработка блока кода"""
        text = para.text.strip()
        
        if not self.in_code_block:
            language = self._detect_code_language(text)
            self.markdown_lines.append(f"```{language}")
            self.in_code_block = True
            
        self.markdown_lines.append(text)
        
        # Проверяем, конец ли блока кода
        # (следующий элемент не код)
        next_element = para._element.getnext()
        if next_element is not None:
            try:
                next_para = Paragraph(next_element, self.doc)
                if not self._is_code_block(next_para):
                    self.markdown_lines.append("```")
                    self.markdown_lines.append('')
                    self.in_code_block = False
            except:
                pass
    
    def _detect_code_language(self, text: str) -> str:
        """Определение языка программирования"""
        if any(text.startswith(cmd) for cmd in ['sudo', 'docker', 'systemctl', '$', 'git']):
            return 'bash'
        elif 'version:' in text or 'services:' in text:
            return 'yaml'
        elif text.startswith('[') and ']' in text:
            return 'ini'
        elif any(sql in text.upper() for sql in ['CREATE', 'SELECT', 'INSERT']):
            return 'sql'
        elif 'def ' in text or 'import ' in text:
            return 'python'
        else:
            return ''
    
    def _get_indent_level(self, para) -> int:
        """Получение уровня отступа"""
        if para.paragraph_format and para.paragraph_format.left_indent:
            indent_pt = para.paragraph_format.left_indent.pt
            return int(indent_pt / 36)  # 36pt = 1 уровень
        return 0
    
    def _add_table_caption(self, element):
        """Добавление подписи к таблице"""
        next_sibling = element.getnext()
        if next_sibling is not None and next_sibling.tag.endswith('p'):
            para = Paragraph(next_sibling, self.doc)
            text = para.text.strip()
            if text.startswith('Таблица'):
                self.markdown_lines.append(f"> {text}")
                self.markdown_lines.append('')
                # Помечаем, что следующий параграф уже обработан
                self.skip_next_paragraph = True


def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование: python improved_docx_to_markdown.py input.docx [output.md]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.docx', '.md')
    
    # Добавляем флаг для frontmatter
    add_frontmatter = '--frontmatter' in sys.argv
    
    if not Path(input_file).exists():
        print(f"Файл {input_file} не найден")
        sys.exit(1)
    
    print(f"Конвертация {input_file} -> {output_file}")
    
    try:
        converter = ImprovedDocxToMarkdownConverter(input_file, add_frontmatter)
        markdown_content = converter.convert()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
            
        print(f"✅ Успешно сконвертировано! Результат сохранен в {output_file}")
        
    except Exception as e:
        print(f"❌ Ошибка при конвертации: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()