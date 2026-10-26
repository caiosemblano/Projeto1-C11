"""Q1: volume de indicações vs. taxa de conversão em vitórias."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.config import FILM_KEY, RANDOM_SEED
from projeto1_c11.data import competitive
from projeto1_c11.plotting import GOLD, NAVY, SLATE, WINE

SLUG = "q01_conversao"
QUESTION = (
    "Qual é a relação entre o volume de indicações de um filme e sua taxa de "
    "conversão em vitórias? Existe um ponto de virada?"
)

NOMINATION_BINS = [0, 1, 3, 6, 9, np.inf]
NOMINATION_LABELS = ["1", "2–3", "4–6", "7–9", "10+"]


def compute(df: pd.DataFrame) -> pd.DataFrame:
    films = competitive(df).dropna(subset=["film"])
    grouped = films.groupby(list(FILM_KEY), as_index=False).agg(
        nominations=("winner", "size"),
        wins=("winner", "sum"),
        year_film=("year_film", "first"),
    )
    grouped["wins"] = grouped["wins"].astype(int)
    grouped["win_rate"] = grouped["wins"] / grouped["nominations"]
    return grouped.sort_values(
        ["wins", "nominations"], ascending=False
    ).reset_index(drop=True)


def _corr(left: pd.Series, right: pd.Series) -> float:
    x = np.asarray(left, dtype=float)
    y = np.asarray(right, dtype=float)
    if x.size < 2 or np.std(x) == 0 or np.std(y) == 0:
        return float("nan")
    return float(np.corrcoef(x, y)[0, 1])


def correlations(result: pd.DataFrame) -> pd.Series:
    nominations = result["nominations"]
    wins = result["wins"]
    return pd.Series(
        {
            "pearson": _corr(nominations, wins),
            "spearman": _corr(nominations.rank(), wins.rank()),
        }
    )


def conversion_by_bin(result: pd.DataFrame) -> pd.DataFrame:
    binned = result.assign(
        nomination_bin=pd.cut(
            result["nominations"],
            bins=NOMINATION_BINS,
            labels=NOMINATION_LABELS,
            include_lowest=True,
        )
    )
    return (
        binned.groupby("nomination_bin", observed=True)
        .agg(
            n_films=("film", "size"),
            mean_wins=("wins", "mean"),
            mean_win_rate=("win_rate", "mean"),
        )
        .reset_index()
    )


def _film_label(row: pd.Series, width: int = 28) -> str:
    title = str(row["film"])
    if len(title) > width:
        title = title[: width - 1] + "…"
    return f"{title} ({int(row['year_ceremony'])})"


def plot(result: pd.DataFrame) -> Figure:
    import matplotlib.pyplot as plt

    stats = correlations(result)
    bins = conversion_by_bin(result)
    rng = np.random.default_rng(RANDOM_SEED)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6.2), layout="constrained")
    scatter_ax, bin_ax = axes

    jitter = rng.uniform(-0.22, 0.22, size=len(result))
    snubbed = result["wins"].eq(0)
    scatter_ax.scatter(
        result.loc[snubbed, "nominations"] + jitter[snubbed.to_numpy()],
        result.loc[snubbed, "wins"],
        alpha=0.35,
        s=28,
        c=SLATE,
        label="0 vitórias",
        zorder=2,
    )
    scatter_ax.scatter(
        result.loc[~snubbed, "nominations"] + jitter[~snubbed.to_numpy()],
        result.loc[~snubbed, "wins"],
        alpha=0.55,
        s=32,
        c=GOLD,
        label="≥ 1 vitória",
        zorder=3,
    )

    champions = result.nlargest(2, ["wins", "nominations"])
    snubs = result.loc[snubbed].nlargest(2, "nominations")
    champion_offsets = [(12, 12), (-92, 10)]
    snub_offsets = [(-125, 18), (14, 18)]
    for (_, row), offset in zip(champions.iterrows(), champion_offsets, strict=False):
        scatter_ax.annotate(
            _film_label(row),
            (row["nominations"], row["wins"]),
            textcoords="offset points",
            xytext=offset,
            fontsize=8,
            color=NAVY,
            arrowprops={"arrowstyle": "-", "color": SLATE, "lw": 0.6},
        )
    for (_, row), offset in zip(snubs.iterrows(), snub_offsets, strict=False):
        scatter_ax.annotate(
            _film_label(row),
            (row["nominations"], row["wins"]),
            textcoords="offset points",
            xytext=offset,
            fontsize=8,
            color=SLATE,
            arrowprops={"arrowstyle": "-", "color": SLATE, "lw": 0.6},
        )

    scatter_ax.set_xlabel("Indicações")
    scatter_ax.set_ylabel("Vitórias")
    scatter_ax.set_title("Indicações vs. vitórias por filme")
    pearson = stats["pearson"]
    spearman = stats["spearman"]
    scatter_ax.text(
        0.02,
        0.98,
        f"Pearson r = {pearson:.2f}\nSpearman ρ = {spearman:.2f}",
        transform=scatter_ax.transAxes,
        va="top",
        ha="left",
        fontsize=10,
        color=NAVY,
        bbox={"boxstyle": "round,pad=0.3", "facecolor": "white", "alpha": 0.9, "edgecolor": "none"},
    )
    scatter_ax.set_ylim(-0.4, float(result["wins"].max()) + 1.8)
    scatter_ax.legend(loc="lower left", frameon=True, framealpha=0.92, edgecolor="none")

    bin_ax.bar(bins["nomination_bin"].astype(str), bins["mean_win_rate"], color=WINE)
    bin_ax.set_xlabel("Faixa de indicações")
    bin_ax.set_ylabel("Taxa média de vitória")
    bin_ax.set_title("Ponto de virada: conversão por volume")
    bin_ax.set_ylim(0, max(0.5, float(bins["mean_win_rate"].max()) * 1.15))
    for x_pos, rate, n_films in zip(
        range(len(bins)), bins["mean_win_rate"], bins["n_films"], strict=True
    ):
        bin_ax.text(
            x_pos,
            rate + 0.01,
            f"{rate:.0%}\nn={int(n_films)}",
            ha="center",
            va="bottom",
            fontsize=8,
            color=NAVY,
        )

    fig.suptitle("Q1 · Conversão de indicações em estatuetas", color=NAVY)
    return fig
