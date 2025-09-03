.PHONY: lint test

lint:
	flake8 .

test:
	python3 -m pytest tests/ -v
