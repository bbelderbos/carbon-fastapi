.PHONY: venv
venv:
	python3.9 -m venv venv

.PHONY: install
install:
	pip install -r requirements-dev.txt

.PHONY: lint
lint:
	flake8 src tests

.PHONY: typing
typing:
	mypy src tests

.PHONY: test
test:
	pytest

.PHONY: cov
cov:
	pytest --cov=src --cov-report term-missing

.PHONY: run
run:
	uvicorn src.api:app --reload

.PHONY: ci
ci: lint typing test
