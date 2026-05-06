#!/usr/bin/env bash
# Full reproducible benchmark: 6 detectors x 2 models x 3 streams x 3 seeds.
# Takes ~30-60 min on a single laptop CPU. Logs every run to MLflow.
set -euo pipefail
cd "$(dirname "$0")/.."

# Make sure the data is downloaded and preprocessed.
python -m src.data.download
python -m src.data.preprocess

python -m src.pipelines.experiment \
    --seeds 42 1337 2024 \
    --models sgd_logistic hoeffding_tree \
    --detectors adwin ddm eddm kswin page_hinkley hybrid \
    --streams elec2 sea hyperplane

python scripts/fill_paper_numbers.py
python scripts/plot_results.py

echo
echo "Done. Re-render paper: cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex"
