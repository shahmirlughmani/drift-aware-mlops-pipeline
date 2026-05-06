#!/usr/bin/env bash
# Regenerate every paper figure and table from raw seeds.
# Idempotent: safe to re-run.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> 1/5  Main benchmark (6 detectors × 3 streams × 2 models × 3 seeds)"
python -m src.pipelines.experiment \
    --seeds 42 1337 2024 \
    --models sgd_logistic hoeffding_tree \
    --detectors adwin ddm eddm kswin page_hinkley hybrid \
    --streams elec2 sea hyperplane \
    --no-mlflow

echo "==> 2/5  Ablation (HybridDD with one component disabled at a time)"
python -m experiments.ablation \
    --seeds 42 1337 2024 \
    --streams sea hyperplane \
    --models sgd_logistic

echo "==> 3/5  Sensitivity sweep (consensus_window × confidence_threshold)"
python -m experiments.sensitivity \
    --seeds 42 1337 \
    --streams sea hyperplane \
    --models sgd_logistic

echo "==> 4/5  Bootstrap 95% CIs on headline metrics"
python -m experiments.bootstrap_ci

echo "==> 5/5  Refresh paper macros and recompile IEEE LaTeX"
python scripts/fill_paper_numbers.py
make paper

echo
echo "Done."
echo "  Results : experiments/results/{results,ablation,sensitivity,bootstrap_ci}.{csv,json}"
echo "  Stats   : experiments/results/stats.json"
echo "  Paper   : paper/main.pdf"
