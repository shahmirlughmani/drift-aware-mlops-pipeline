"""Render the architecture diagram as PNG using matplotlib.

Standalone fallback for environments without `@mermaid-js/mermaid-cli`. The
canonical source remains `architecture/architecture.mmd`. This script keeps
the rendered figure in sync via an explicit data structure.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "architecture" / "architecture.png"

# (x, y, w, h, label, kind) where kind in {svc, store, ci, plane}
NODES = {
    "client":  (0.5, 5.6, 1.6, 0.9, "Streaming source\n(ELEC2)", "svc"),
    "api":     (3.4, 5.8, 2.0, 1.2, "FastAPI service\n/predict /reload", "svc"),
    "model":   (3.4, 4.1, 2.0, 0.8, "Online model\n(SGD / Hoeffding)", "store"),
    "drift":   (6.6, 5.8, 2.2, 1.2, "Drift monitor\nHybrid detector", "svc"),
    "prom":    (9.6, 6.1, 1.8, 0.9, "Prometheus\n+ alerts", "store"),
    "graf":    (9.6, 4.6, 1.8, 0.9, "Grafana\ndashboards", "store"),
    "mlflow":  (3.4, 1.8, 2.0, 1.0, "MLflow tracking\n+ registry", "store"),
    "pg":      (0.5, 2.0, 1.6, 0.8, "PostgreSQL\nmetadata", "store"),
    "art":     (0.5, 0.6, 1.6, 0.8, "Artifact store\n(volume / S3)", "store"),
    "trainer": (6.6, 1.8, 2.2, 1.0, "Trainer service\nwarmup + retrain", "svc"),
    "gh":      (9.6, 2.6, 1.8, 0.8, "GitHub Actions", "ci"),
    "ghcr":    (9.6, 1.4, 1.8, 0.8, "GHCR registry", "ci"),
    "aws":     (9.6, 0.2, 1.8, 0.8, "AWS ECS/Fargate", "ci"),
}

EDGES = [
    ("client", "api",   "POST /predict (x, y)"),
    ("api",    "model", ""),
    ("api",    "prom",  "/metrics"),
    ("drift",  "prom",  "/metrics :9100"),
    ("prom",   "graf",  "datasource"),
    ("drift",  "api",   "POST /reload"),
    ("api",    "mlflow", "load Production"),
    ("trainer","mlflow", "log + register"),
    ("mlflow", "pg",    "metadata"),
    ("mlflow", "art",   "artifacts"),
    ("gh",     "ghcr",  "build/push"),
    ("ghcr",   "aws",   "deploy"),
    ("ghcr",   "api",   "pull"),
    ("ghcr",   "drift", "pull"),
    ("ghcr",   "trainer","pull"),
]

COLORS = {
    "svc":   ("#0e2d3a", "#37c5d9", "#dfe6f3"),
    "store": ("#1c2330", "#8da7c4", "#dfe6f3"),
    "ci":    ("#2a1a2f", "#b066c2", "#f1dff7"),
}


def draw() -> Path:
    fig, ax = plt.subplots(figsize=(15.0, 8.0))
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 7.5)
    ax.set_facecolor("#070b13")
    ax.axis("off")

    plane_boxes = [
        (0.2, 5.3, 9.4, 1.9, "Inference & data plane"),
        (8.7, 4.3, 3.0, 2.9, "Observability"),
        (0.2, 0.2, 9.3, 3.0, "Tracking & registry"),
        (8.7, 0.0, 3.0, 3.5, "CI / CD"),
    ]
    for (x, y, w, h, title) in plane_boxes:
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.10",
            linewidth=1.0, edgecolor="#5677b1", facecolor="#0b1220"
        ))
        ax.text(x + 0.15, y + h - 0.22, title, color="#9fb4d8",
                fontsize=10, fontweight="bold")

    boxes: dict[str, tuple[float, float, float, float]] = {}
    for k, (x, y, w, h, label, kind) in NODES.items():
        bg, edge, text = COLORS[kind]
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.12",
            linewidth=1.5, edgecolor=edge, facecolor=bg
        ))
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center",
                color=text, fontsize=10, fontweight="bold")
        boxes[k] = (x, y, w, h)

    def anchor(node: str, side: str) -> tuple[float, float]:
        x, y, w, h = boxes[node]
        return {
            "left":  (x, y + h / 2),
            "right": (x + w, y + h / 2),
            "top":   (x + w / 2, y + h),
            "bot":   (x + w / 2, y),
        }[side]

    def best_sides(a: str, b: str) -> tuple[str, str]:
        ax_, ay, aw, ah = boxes[a]
        bx_, by, bw, bh = boxes[b]
        cax, cay = ax_ + aw / 2, ay + ah / 2
        cbx, cby = bx_ + bw / 2, by + bh / 2
        if abs(cbx - cax) > abs(cby - cay):
            return ("right", "left") if cbx > cax else ("left", "right")
        return ("top", "bot") if cby > cay else ("bot", "top")

    for src, dst, label in EDGES:
        s_side, d_side = best_sides(src, dst)
        sx, sy = anchor(src, s_side)
        dx, dy = anchor(dst, d_side)
        arrow = FancyArrowPatch(
            (sx, sy), (dx, dy),
            arrowstyle="->", mutation_scale=14,
            color="#7a9bc7", linewidth=1.2,
            connectionstyle="arc3,rad=0.12",
        )
        ax.add_patch(arrow)
        if label:
            mx, my = (sx + dx) / 2, (sy + dy) / 2 + 0.08
            ax.text(mx, my, label, color="#bccae0", fontsize=8,
                    ha="center", va="center")

    # Legend
    handles = [
        mpatches.Patch(color="#0e2d3a", label="Service"),
        mpatches.Patch(color="#1c2330", label="Storage / data store"),
        mpatches.Patch(color="#2a1a2f", label="CI/CD"),
    ]
    leg = ax.legend(handles=handles, loc="lower left", facecolor="#0b1220",
                    edgecolor="#5677b1", labelcolor="#dfe6f3")
    for txt in leg.get_texts():
        txt.set_color("#dfe6f3")

    ax.set_title("Drift-Aware Adaptive Retraining: System Architecture",
                 color="#dfe6f3", fontsize=13, fontweight="bold", pad=18)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=200, facecolor="#070b13", bbox_inches="tight")
    plt.close(fig)
    return OUT


if __name__ == "__main__":
    p = draw()
    print(f"Wrote {p}")
