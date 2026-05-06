"""Generate the figures referenced in the IEEE paper from results.csv.

Outputs:
    paper/figures/accuracy_curve.png
    paper/figures/detection_delay.png
    paper/figures/cd_diagram.png
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS_CSV = ROOT / "experiments" / "results" / "results.csv"
FIG_DIR = ROOT / "paper" / "figures"

DETECTORS = ["adwin", "ddm", "eddm", "kswin", "page_hinkley", "hybrid"]
PRETTY = {"adwin": "ADWIN", "ddm": "DDM", "eddm": "EDDM",
          "kswin": "KSWIN", "page_hinkley": "Page-Hinkley", "hybrid": "HybridDD"}


def fig_accuracy(df: pd.DataFrame) -> Path:
    means = df.groupby(["stream", "detector"])["accuracy"].mean().unstack()
    means = means[[d for d in DETECTORS if d in means.columns]]
    means.columns = [PRETTY.get(c, c) for c in means.columns]

    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    means.plot(kind="bar", ax=ax, edgecolor="black", width=0.85)
    ax.set_ylabel("Prequential accuracy")
    ax.set_xlabel("")
    ax.set_ylim(0.6, 0.95)
    ax.legend(loc="lower right", ncol=3, fontsize=8)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    out = FIG_DIR / "accuracy_curve.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_detection_delay(df: pd.DataFrame) -> Path:
    sub = df[(df["stream"] != "elec2") & (~df["mean_detection_delay"].isna())]
    means = sub.groupby("detector")["mean_detection_delay"].mean()
    means = means.reindex([d for d in DETECTORS if d in means.index])
    means.index = [PRETTY.get(d, d) for d in means.index]

    fig, ax = plt.subplots(figsize=(6.0, 3.4))
    bars = ax.bar(means.index, means.values, color="#37c5d9", edgecolor="black")
    bars[-1].set_color("#e07b40")
    ax.set_ylabel("Mean detection delay (samples)")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    fig.tight_layout()
    out = FIG_DIR / "detection_delay.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def fig_cd_diagram(df: pd.DataFrame) -> Path:
    """Demsar critical-difference diagram on accuracy ranks."""
    pivot = df.pivot_table(index=["stream", "seed"], columns="detector",
                           values="accuracy")
    pivot = pivot.dropna(how="any")
    if pivot.shape[0] < 3 or pivot.shape[1] < 3:
        return FIG_DIR / "cd_diagram.png"

    ranks = pivot.rank(axis=1, ascending=False, method="average")
    avg = ranks.mean(axis=0).sort_values()
    k, n = pivot.shape[1], pivot.shape[0]
    q_alpha = {2: 1.960, 3: 2.343, 4: 2.569, 5: 2.728, 6: 2.850, 7: 2.949,
               8: 3.031, 9: 3.102, 10: 3.164}
    cd = q_alpha.get(k, 2.85) * np.sqrt(k * (k + 1) / (6 * n))

    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    y = 1.0
    ax.set_xlim(min(avg.values) - 0.3, max(avg.values) + 0.3)
    ax.set_ylim(0, 2)
    ax.set_yticks([])
    ax.set_xlabel("Average rank (lower is better)")
    for det, r in avg.items():
        ax.plot([r, r], [y, y + 0.25], color="black")
        ax.text(r, y + 0.32, PRETTY.get(det, det), rotation=45,
                ha="left", va="bottom", fontsize=9)
    ax.plot([avg.iloc[0], avg.iloc[0] + cd], [y - 0.15, y - 0.15],
            color="red", lw=2)
    ax.text(avg.iloc[0] + cd / 2, y - 0.28, f"CD = {cd:.2f}",
            color="red", ha="center", fontsize=9)
    ax.set_title("Nemenyi critical difference (alpha = 0.05)")
    fig.tight_layout()
    out = FIG_DIR / "cd_diagram.png"
    fig.savefig(out, dpi=200)
    plt.close(fig)
    return out


def main() -> None:
    if not RESULTS_CSV.exists():
        print(f"missing {RESULTS_CSV}; run the experiment driver first")
        return
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RESULTS_CSV)
    a = fig_accuracy(df)
    b = fig_detection_delay(df)
    c = fig_cd_diagram(df)
    print(f"wrote {a}\nwrote {b}\nwrote {c}")


if __name__ == "__main__":
    main()
