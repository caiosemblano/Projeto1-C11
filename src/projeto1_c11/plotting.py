"""Estilo compartilhado e gravação das figuras do pitch."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure

from projeto1_c11.config import FIGURE_DPI, FIGURES_DIR

GOLD = "#C9A227"
NAVY = "#1F3A5F"
SLATE = "#5C6B7A"
WINE = "#8C2F39"
CREAM = "#F7F1E3"


def apply_style() -> None:
    sns.set_theme(style="whitegrid", context="talk", font_scale=0.85)
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": CREAM,
            "axes.edgecolor": SLATE,
            "axes.titleweight": "bold",
            "axes.titlesize": 14,
            "axes.labelsize": 12,
            "savefig.facecolor": "white",
            "savefig.bbox": "tight",
        }
    )


def save_fig(fig: Figure, name: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, dpi=FIGURE_DPI, bbox_inches="tight")
    return path
