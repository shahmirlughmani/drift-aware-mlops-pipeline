.PHONY: help install install-dev lint format test test-fast cov clean \
        data train experiment ablation sensitivity bootstrap reproduce \
        serve drift-service \
        docker-build up down logs paper architecture all

PYTHON ?= python
PIP    ?= pip

help:
	@echo "Targets:"
	@echo "  install         pip install runtime requirements"
	@echo "  install-dev     pip install dev requirements"
	@echo "  lint            ruff + mypy"
	@echo "  format          ruff format + black"
	@echo "  test            full pytest suite with coverage"
	@echo "  test-fast       unit tests only (skip slow/integration)"
	@echo "  data            download and preprocess ELEC2 dataset"
	@echo "  train           train baseline + online models, log to MLflow"
	@echo "  experiment      run full prequential drift-detector benchmark"
	@echo "  ablation        HybridDD ablation: drop one component at a time"
	@echo "  sensitivity     sweep consensus_window x confidence_threshold"
	@echo "  bootstrap       95% bootstrap CIs on headline metrics"
	@echo "  reproduce       end-to-end: experiment + ablation + sensitivity + paper"
	@echo "  serve           run FastAPI inference locally"
	@echo "  drift-service   run drift monitor locally"
	@echo "  up              docker compose up -d full stack"
	@echo "  down            docker compose down"
	@echo "  logs            tail compose logs"
	@echo "  paper           build IEEE LaTeX paper"
	@echo "  architecture    render Mermaid architecture diagram"
	@echo "  all             data + train + experiment + paper"

install:
	$(PIP) install -r requirements.txt

install-dev:
	$(PIP) install -r requirements-dev.txt
	pre-commit install || true

lint:
	ruff check src tests
	mypy src || true

format:
	ruff format src tests
	black src tests

test:
	pytest

test-fast:
	pytest -m "not slow and not integration"

cov:
	pytest --cov=src --cov-report=html
	@echo "Open htmlcov/index.html"

clean:
	rm -rf build dist *.egg-info .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
	find . -type d -name __pycache__ -exec rm -rf {} +

data:
	$(PYTHON) -m src.data.download
	$(PYTHON) -m src.data.preprocess

train:
	$(PYTHON) -m src.pipelines.train

experiment:
	$(PYTHON) -m src.pipelines.experiment

ablation:
	$(PYTHON) -m experiments.ablation

sensitivity:
	$(PYTHON) -m experiments.sensitivity

bootstrap:
	$(PYTHON) -m experiments.bootstrap_ci

reproduce:
	bash scripts/reproduce.sh

serve:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

drift-service:
	$(PYTHON) -m src.monitoring.drift_service

docker-build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f --tail=100

paper:
	cd paper && pdflatex -interaction=nonstopmode main.tex && bibtex main && pdflatex -interaction=nonstopmode main.tex && pdflatex -interaction=nonstopmode main.tex

architecture:
	@command -v mmdc >/dev/null 2>&1 || { echo "mermaid-cli (mmdc) not found. npm i -g @mermaid-js/mermaid-cli"; exit 1; }
	mmdc -i architecture/architecture.mmd -o architecture/architecture.png -b transparent -w 1600

all: data train experiment paper
