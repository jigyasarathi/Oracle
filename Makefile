.PHONY: install ingest run ask test lint eval adk docker

install:
	pip install -e ".[dev]"

ingest:
	python scripts/ingest_docs.py

run:
	uvicorn oracle.api:app --reload --port 8080

ask:
	python scripts/ask.py "$(Q)"

test:
	pytest

lint:
	ruff check .

eval:
	python evals/run_evals.py

adk:
	adk web adk_agents

docker:
	docker build -t oracle:local .
