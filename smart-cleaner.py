import os
from bs4 import BeautifulSoup, NavigableString

def clean_html_file_final(input_path, output_path):
    """
    Интеллектуально очищает HTML-файл из DOCX, сохраняя нумерацию заголовков,
    структуру таблиц и форматирование кода, включая inline-выделение.
    """
    
    clean_css = """
    <style>
        body {
            font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px;
            margin: 20px auto; padding: 0 20px; color: #333;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: "Cambria", serif; line-height: 1.3; margin-top: 1.5em;
            margin-bottom: 0.5em; font-weight: bold;
        }
        h1 { font-size: 2em; text-align: center; }
        h2 { font-size: 1.75em; border-bottom: 1px solid #ccc; padding-bottom: 0.3em; }
        h3 { font-size: 1.5em; }
        h4 { font-size: 1.25em; }
        p, li { text-align: justify; margin-bottom: 1em; }
        ul, ol { padding-left: 40px; }
        table { width: 100%; border-collapse: collapse; margin: 1em 0; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; vertical-align: top; }
        th { background-color: #f2f2f2; font-weight: bold; text-align: center; }
        pre {
            background-color: #f0f0f0;
            padding: 1em;
            border: 1px solid #ddd;
            border-radius: 4px;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: "Courier New", Courier, monospace;
            margin: 1em 0;
        }
        a { color: #0056b3; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .center { text-align: center; }
        .table-subheader {
            text-align: center;
            font-weight: bold;
            background-color: #e9e9e9;
        }
        .highlight {
            background-color: #e0e0e0; /* Серый фон для выделения */
            padding: 2px 5px;
            border-radius: 3px;
            font-family: "Courier New", Courier, monospace;
        }
        img { max-width: 100%; height: auto; display: block; margin: 1em auto; }
    </style>
    """

    print(f"Чтение файла: {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f_in:
        soup = BeautifulSoup(f_in, 'html.parser')

    # 1. Заменяем старые стили на новые
    if soup.style:
        soup.style.replace_with(BeautifulSoup(clean_css, 'html.parser'))
        print("Блок <style> заменен на новый.")

    # 2. Преобразование тегов на основе классов
    heading_map = {
        "c42": "h2",
        "c14": "h3",
    }
    
    print("Преобразование <p> в заголовки...")
    for p_tag in soup.find_all('p'):
        span = p_tag.find('span', class_=lambda c: c in heading_map if c else False)
        if span:
            new_tag_name = heading_map.get(span['class'][0])
            if new_tag_name:
                full_text = p_tag.get_text(strip=True)
                p_tag.name = new_tag_name
                p_tag.string = full_text

    print("Обработка таблиц...")
    for table in soup.find_all('table'):
        num_columns = 0
        for tr in table.find_all('tr'):
            cols = tr.find_all(['td', 'th'])
            if len(cols) > 1:
                num_columns = len(cols)
                break
        if num_columns == 0: continue

        first_row = table.find('tr')
        if first_row:
            for td in first_row.find_all('td'):
                td.name = 'th'

        for tr in table.find_all('tr'):
            cells = tr.find_all(['td', 'th'])
            if len(cells) == 1:
                cell = cells[0]
                cell['colspan'] = num_columns
                cell['class'] = 'table-subheader'

    print("Объединение блоков кода...")
    code_classes = {'c25', 'c26', 'c27'}
    
    current_code_block = []
    for p_tag in soup.find_all('p'):
        if p_tag.get('class') and any(cls in code_classes for cls in p_tag.get('class')):
            current_code_block.append(p_tag)
        else:
            if current_code_block:
                pre_tag = soup.new_tag('pre')
                current_code_block[0].insert_before(pre_tag)
                full_code_text = '\n'.join(p.get_text(strip=True) for p in current_code_block)
                pre_tag.string = full_code_text
                for tag in current_code_block:
                    tag.decompose()
                current_code_block = []

    if current_code_block:
        pre_tag = soup.new_tag('pre')
        current_code_block[0].insert_before(pre_tag)
        full_code_text = '\n'.join(p.get_text(strip=True) for p in current_code_block)
        pre_tag.string = full_code_text
        for tag in current_code_block:
            tag.decompose()

    # 3. Финальная очистка
    print("Обработка <span> для выделения и удаление остальных...")
    highlight_classes = {'c16', 'c34'}
    for span in soup.find_all('span'):
        if span.get('class') and any(c in highlight_classes for c in span.get('class')):
            span.attrs = {}
            span['class'] = 'highlight'
        else:
            span.unwrap()

    print("Финальная очистка атрибутов...")
    allowed_attrs = {'href', 'src', 'id', 'start', 'colspan', 'class'}
    for tag in soup.find_all(True):
        attrs_to_remove = [attr for attr in tag.attrs if attr not in allowed_attrs]
        for attr in attrs_to_remove:
            del tag[attr]
        if 'class' in tag.attrs and not tag['class']:
            del tag['class']

    print(f"Сохранение очищенного файла в: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f_out:
        f_out.write(soup.prettify())
    
    print("Очистка успешно завершена!")

if __name__ == "__main__":
    input_file = "document.html" 
    output_file = "document_cleaned_final.html"

    if os.path.exists(input_file):
        clean_html_file_final(input_file, output_file)
    else:
        print(f"Ошибка: Файл '{input_file}' не найден.")