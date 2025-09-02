class Document:
    """Простая заглушка для объекта Document из python-docx."""
    def __init__(self, *args, **kwargs):
        self.styles = []
        self.element = type('Body', (), {'body': []})()

    def add_paragraph(self, text):
        # Метод присутствует для совместимости, но ничего не делает
        pass

    def save(self, path):
        # Создаем пустой файл, чтобы имитировать сохранение документа
        with open(path, 'w', encoding='utf-8') as f:
            f.write('')
