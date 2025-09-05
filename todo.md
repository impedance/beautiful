
### **Детальный план реализации: Конвертер DOCX → Markdown**

#### Прогресс
- [x] Фаза 0
- [x] Фаза 1
- [ ] Фаза 2

Это руководство описывает конкретные шаги для реализации каждого модуля в рамках ранее утвержденного плана.

#### **Фаза 0: Основы проекта и настройка окружения (1-2 дня)**

**Цель:** Подготовить рабочее пространство и базовую структуру приложения.

*   **Задача 0.1-0.2: Структура и зависимости**
    *   **Детальное описание реализации:**
        1.  Создайте корневую директорию проекта.
        2.  Внутри выполните `poetry init`, чтобы создать `pyproject.toml`.
        3.  Создайте структуру папок: `src/doc2md`, `tests`, `scripts`, `input`, `output`, `samples`.
        4.  Добавьте начальные зависимости: `poetry add typer rich python-dotenv`.
        5.  В `src/doc2md` создайте пустой `__init__.py`.

*   **Задача 0.3: Базовый CLI-интерфейс**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/cli.py`
        *   **Код:**
            ```python
            import typer
            from rich.console import Console

            app = typer.Typer()
            console = Console()

            @app.command()
            def run(
                docx_path: str = typer.Argument(..., help="Путь к входному DOCX файлу."),
                output_dir: str = typer.Option("output", "--out", "-o", help="Директория для сохранения Markdown файлов."),
                # ... другие опции будут добавлены позже
            ):
                """
                Конвертирует DOCX документацию в набор Markdown файлов.
                """
                console.print(f"[bold green]Запуск конвертации для файла:[/] {docx_path}")
                # Здесь будет основная логика пайплайна
                console.print(f"[bold green]Конвертация завершена. Результаты в:[/] {output_dir}")

            if __name__ == "__main__":
                app()
            ```

*   **Задача 0.4: Настройка логирования и конфигурации**
    *   **Детальное описание реализации:**
        1.  Создайте файл `.env` в корне проекта для хранения секретов и конфигураций:
            ```
            OPENROUTER_API_KEY="your_api_key_here"
            ```
        2.  Создайте модуль `src/doc2md/config.py` для загрузки этих переменных:
            ```python
            import os
            from dotenv import load_dotenv

            load_dotenv()

            API_KEY = os.getenv("OPENROUTER_API_KEY")
            # ... другие настройки
            ```

---

#### **Фаза 1: Препроцессинг и извлечение контента (3-5 дней)**

**Цель:** Надежно извлечь весь контент (текст и медиа) из DOCX и подготовить его для LLM.

*   **Задача 1.1: Модуль `preprocess.py` - конвертация в HTML (Mammoth)**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/preprocess.py`
        *   **Зависимости:** `poetry add mammoth`
        *   **Код:**
            ```python
            import mammoth

            def convert_docx_to_html(docx_path: str, style_map_path: str) -> str:
                """Конвертирует DOCX в HTML с использованием кастомной карты стилей."""
                with open(docx_path, "rb") as docx_file:
                    with open(style_map_path, "r") as style_map_file:
                        style_map = style_map_file.read()
                        result = mammoth.convert_to_html(docx_file, style_map=style_map)
                        return result.value
            ```
        *   **Артефакт:** Создайте файл `src/doc2md/mammoth_style_map.map` и скопируйте в него содержимое из вашего промта.

*   **Задача 1.2: Модуль `preprocess.py` - извлечение изображений (Pandoc)**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/preprocess.py`
        *   **Код:**
            ```python
            import subprocess
            import os

            def extract_images(docx_path: str, output_dir: str):
                """Извлекает изображения из DOCX с помощью Pandoc."""
                os.makedirs(output_dir, exist_ok=True)
                command = [
                    "pandoc",
                    docx_path,
                    "--extract-media",
                    output_dir,
                    "-t",
                    "markdown", # Нужно указать формат вывода, даже если нам нужен только медиа-контент
                    "-o",
                    os.devnull # Вывод markdown нам не нужен, отправляем в /dev/null
                ]
                subprocess.run(command, check=True)
            ```

*   **Задача 1.3: Модуль `splitter.py` - разделение на главы**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/splitter.py`
        *   **Зависимости:** `poetry add beautifulsoup4 lxml`
        *   **Код:**
            ```python
            from bs4 import BeautifulSoup
            from typing import List

            def split_html_by_h1(html_content: str) -> List[str]:
                """Разделяет HTML на части по тегу <h1>."""
                soup = BeautifulSoup(html_content, 'lxml')
                chapters = []
                current_chapter_tags = []
                h1_tags = soup.find_all('h1')

                if not h1_tags:
                    return [html_content] # Если нет H1, возвращаем весь документ как одну главу

                for h1 in h1_tags:
                    chapter_content = [str(h1)]
                    for sibling in h1.find_next_siblings():
                        if sibling.name == 'h1':
                            break
                        chapter_content.append(str(sibling))
                    chapters.append("\n".join(chapter_content))
                return chapters
            ```

---

#### **Фаза 2: Интеграция с LLM и форматирование (5-7 дней)**

**Цель:** Превратить "сырые" HTML-главы в чистовой Markdown с помощью LLM.

*   **Задача 2.1: Модуль `schema.py`**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/schema.py`
        *   **Код:** Скопируйте JSON-схему из промта в виде Python-словаря.
            ```python
            CHAPTER_MANIFEST_SCHEMA = {
                "type": "object",
                "required": ["chapter_number", "title", "filename", "slug", ...],
                # ... остальная часть схемы
            }
            ```

*   **Задача 2.2: Модуль `prompt_builder.py`**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/prompt_builder.py`
        *   **Логика:** Класс, который кэширует правила и примеры при инициализации.
            ```python
            class PromptBuilder:
                def __init__(self, rules_path: str, samples_dir: str):
                    with open(rules_path, 'r') as f:
                        self.rules = f.read()
                    # Логика загрузки 2-3 случайных примеров из samples_dir
                    self.examples = self._load_examples(samples_dir)

                def build_for_chapter(self, chapter_html: str) -> list:
                    # Формирует структуру сообщения для API
                    system_prompt = f"""
                    You are an expert DOCX to Markdown converter. Follow all rules precisely.
                    FORMATTING RULES:
                    {self.rules}
                    EXAMPLES:
                    {self.examples}
                    """
                    user_prompt = f"""
                    Convert this chapter HTML to Markdown. Return EXACTLY two blocks: a JSON manifest, then the Markdown content.
                    CHAPTER HTML:
                    ```html
                    {chapter_html}
                    ```
                    """
                    return [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                # ...
            ```

*   **Задача 2.3: Модуль `llm_client.py`**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/llm_client.py`
        *   **Зависимости:** `poetry add httpx jsonschema`
        *   **Код:**
            ```python
            import httpx
            import json
            import re
            from jsonschema import validate
            from .schema import CHAPTER_MANIFEST_SCHEMA
            from .config import API_KEY

            class LLMClient:
                def __init__(self):
                    self.api_url = "https://openrouter.ai/api/v1/chat/completions"
                    self.headers = {"Authorization": f"Bearer {API_KEY}"}

                def format_chapter(self, prompt: list) -> (dict, str):
                    # Логика запроса с использованием httpx.post
                    # ...
                    response_text = response.json()['choices'][0]['message']['content']

                    # Надежное извлечение блоков
                    json_match = re.search(r"```json\n(.*?)\n```", response_text, re.DOTALL)
                    md_match = re.search(r"```markdown\n(.*?)\n```", response_text, re.DOTALL)

                    if not json_match or not md_match:
                        raise ValueError("LLM response does not contain valid JSON and Markdown blocks.")

                    manifest = json.loads(json_match.group(1))
                    markdown = md_match.group(1)

                    validate(instance=manifest, schema=CHAPTER_MANIFEST_SCHEMA)
                    return manifest, markdown
            ```

---

#### **Фаза 3: Постобработка и валидация (4-6 дней)**

**Цель:** Гарантировать 100% соответствие результата внутреннему стандарту.

*   **Задача 3.1-3.3: Модули `postprocess.py` и `validators.py`**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/postprocess.py`
        *   **Логика:** Создайте класс `PostProcessor`, который принимает сырой Markdown и применяет к нему цепочку исправлений.
            ```python
            import re

            class PostProcessor:
                def __init__(self, markdown_content, chapter_number, doc_slug):
                    self.md = markdown_content
                    self.chapter_num = chapter_number
                    self.slug = doc_slug
                    self.h2_counter = 0

                def _normalize_headings(self, match):
                    self.h2_counter += 1
                    return f"## {self.chapter_num}.{self.h2_counter}"

                def run(self):
                    # 1. Нумерация заголовков
                    self.md = re.sub(r"^## (.*)", self._normalize_headings, self.md, flags=re.MULTILINE)
                    # ... аналогично для H3, H4 с вложенными счетчиками

                    # 2. Пути к изображениям
                    self.md = re.sub(
                        r"!\[(.*?)\]\((.*?)\)",
                        rf"![\1](/images/developer/administrator/{self.slug}/\2)",
                        self.md
                    )
                    # 3. Другие исправления (пунктуация в списках и т.д.)
                    return self.md
            ```
        *   **Файл:** `src/doc2md/validators.py` - реализуйте функции проверок, которые могут быть вызваны до и после постобработки для логирования проблем.

*   **Задача 3.4: Модуль `navigation.py`**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/navigation.py`
        *   **Зависимости:** `poetry add python-frontmatter`
        *   **Логика:**
            ```python
            import os
            import frontmatter
            import json

            def inject_navigation_and_create_toc(output_dir: str):
                # 1. Получить список всех .md файлов и отсортировать их
                # 2. Пройтись по списку, читая каждый файл
                # 3. Для файла i, prev = i-1, next = i+1
                # 4. Добавить/обновить `readPrev` и `readNext` в frontmatter
                # 5. Перезаписать файл
                # 6. Сгенерировать и сохранить toc.json
            ```

---

#### **Фаза 4: Финализация и UX (2-3 дня)**

**Цель:** Превратить набор скриптов в удобный и готовый к использованию инструмент.

*   **Задача 4.1-4.5: Интеграция всего в `cli.py`**
    *   **Детальное описание реализации:**
        *   **Файл:** `src/doc2md/cli.py`
        *   **Логика:** Обновите команду `run`, чтобы она последовательно вызывала все реализованные модули:
            1.  Создать slug из имени файла (`python-slugify`).
            2.  Вызвать `extract_images`.
            3.  Вызвать `convert_docx_to_html`.
            4.  Вызвать `split_html_by_h1`.
            5.  Начать цикл по главам:
                *   Вызвать `PromptBuilder`.
                *   Вызвать `LLMClient`.
                *   Вызвать `PostProcessor`.
                *   Сохранить финальный Markdown в файл из манифеста.
            6.  После цикла вызвать `inject_navigation_and_create_toc`.
            7.  Использовать `rich.progress` для красивого отображения процесса.

Этот детальный план предоставляет разработчикам четкую дорожную карту, минимизируя неопределенность и позволяя сосредоточиться на реализации каждого компонента в отдельности.