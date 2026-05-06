# Contributing

## Dev loop

```bash
pip install -r requirements-dev.txt
pre-commit install
make test-fast       # under 10 s
make experiment      # full benchmark (~5 min)
```

## Style
- Ruff is the source of truth for lint and format. CI runs both `ruff check` and `ruff format --check`.
- Type hints at module boundaries (`src/api`, `src/drift/base.py`, etc.). `mypy` is non-blocking but encouraged.
- Tests must not require external services unless marked `@pytest.mark.integration`.

## Adding a new drift detector
1. Subclass `src.drift.base.DriftDetector`.
2. Register it in `src.drift.factory._REGISTRY`.
3. Add a parametrized entry to `tests/test_drift_detectors.py`.
4. Document hyperparameters in the docstring.
5. Re-run `python -m src.pipelines.experiment` and refresh `paper/results.tex` via `python scripts/fill_paper_numbers.py`.

## Adding a Grafana panel
1. Edit (or copy) the JSON in `deploy/grafana/dashboards/`.
2. Restart Grafana; provisioning watches the directory.
3. If the panel relies on a new metric, add the metric in `src/api/metrics.py` and emit it from either the API or the drift monitor.
