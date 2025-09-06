# doc2md

`doc2md` — инструмент командной строки для конвертации технической документации из
формата DOCX в набор Markdown-файлов согласно внутреннему стандарту.

## Установка

1. Убедитесь, что установлены **Python 3.11+** и [Poetry](https://python-poetry.org/).
2. Установите зависимости:

   ```bash
   poetry install
   ```

## Конфигурация

API-ключ и параметры OpenRouter задаются в файле `.env` в корне репозитория:

```env
OPENROUTER_API_KEY="your_api_key_here"
OPENROUTER_API_URL="https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL="gpt-4o-mini"
OPENROUTER_HTTP_REFERER="https://example.com"  # optional
OPENROUTER_APP_TITLE="Example"  # optional
```

## Использование

Основная команда — `run`:

```bash
poetry run doc2md run input.docx --out output_dir \
  --model gpt-4o-mini --dry-run
```

Опции:

- `--out` — директория для сохранения результатов (по умолчанию `output`).
- `--model` — модель OpenRouter для форматирования.
- `--dry-run` — выполнить только этап препроцессинга без обращения к LLM.
- `--style-map` — путь к кастомному файлу стилей Mammoth.
- `--rules-path` — путь к файлу правил форматирования.
- `--samples-dir` — каталог с примерами форматирования.

После успешного завершения в указанной директории появятся Markdown-файлы
глав, а также `toc.json` с оглавлением.

## JSON Schema

Ответ LLM включает манифест главы с метаданными. Его структура задаётся
`CHAPTER_MANIFEST_SCHEMA` в `src/doc2md/schema.py`. Клиент LLM проверяет
манифест по этой схеме перед записью файлов, а тесты убеждаются, что схема
работает корректно.

## Тесты

Запуск линтеров и тестов:

```bash
ruff .
black --check .
mypy .
pytest
```

## Лицензия

Проект распространяется под лицензией MIT.
