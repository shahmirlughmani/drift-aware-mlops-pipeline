#!/usr/bin/env bash
# Lightweight reproducer: one seed, two models, all detectors, synthetic streams only.
# Used in CI for a smoke run. Full benchmark: `make experiment`.
set -euo pipefail
cd "$(dirname "$0")/.."

python -m src.pipelines.experiment \
    --no-mlflow \
    --seeds 42 \
    --models sgd_logistic \
    --detectors adwin ddm eddm kswin page_hinkley hybrid \
    --streams sea hyperplane

python scripts/fill_paper_numbers.py || true
python scripts/plot_results.py        || true

echo
echo "results: experiments/results/results.csv"
ls -la experiments/results/
