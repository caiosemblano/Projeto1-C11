"""Q10: número de concorrentes por categoria e a expansão de Melhor Filme."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.categories import decade
from projeto1_c11.data import competitive
from projeto1_c11.plotting import GOLD, NAVY, SLATE, WINE

SLUG = "q10_concorrentes"
QUESTION = (
    "Qual a proporção média de concorrentes por categoria ao longo das "
    "décadas (especialmente a expansão de 5 para até 10 indicados em Melhor "
    "Filme a partir de 2010)? Como isso alterou a probabilidade matemática "
    "de vitória?"
)

ERA_SPANS = (
    (1945, 2009, "5 indicados", SLATE),
    (2010, 2021, "Expansão 8–10", GOLD),
    (2022, 2026, "10 fixos", WINE),
)


def compute(df: pd.DataFrame) -> pd.DataFrame:
    rows = competitive(df).dropna(subset=["film"])
    bp = rows.loc[rows["is_best_picture"]]
    if bp.empty:
        return pd.DataFrame(
            columns=[
                "year_ceremony",
                "n_nominees",
                "n_winners",
                "win_prob",
                "decade",
                "other_mean_nominees",
                "other_win_prob",
            ]
        )

    yearly = (
        bp.groupby("year_ceremony", as_index=False)
        .agg(n_nominees=("film", "nunique"), n_winners=("winner", "sum"))
        .sort_values("year_ceremony")
    )
    yearly["n_winners"] = yearly["n_winners"].astype(int)
    yearly["win_prob"] = 1.0 / yearly["n_nominees"]
    yearly["decade"] = decade(yearly["year_ceremony"].to_numpy())

    others = rows.loc[~rows["is_best_picture"]]
    if others.empty:
        yearly["other_mean_nominees"] = pd.NA
        yearly["other_win_prob"] = pd.NA
        return yearly.reset_index(drop=True)

    per_category = (
        others.groupby(["year_ceremony", "category_canon"], as_index=False)
        .size()
        .rename(columns={"size": "n_nominees"})
    )
    other_yearly = per_category.groupby("year_ceremony", as_index=False).agg(
        other_mean_nominees=("n_nominees", "mean")
    )
    other_yearly["other_win_prob"] = 1.0 / other_yearly["other_mean_nominees"]
    yearly = yearly.merge(other_yearly, on="year_ceremony", how="left")
    return yearly.reset_index(drop=True)


def category_competition_by_decade(df: pd.DataFrame) -> pd.DataFrame:
    rows = competitive(df)
    if rows.empty:
        return pd.DataFrame(
            columns=["decade", "mean_nominees", "median_nominees", "n_category_years"]
        )
    per = (
        rows.groupby(["decade", "year_ceremony", "category_canon"], as_index=False)
        .size()
        .rename(columns={"size": "n_nominees"})
    )
    return (
        per.groupby("decade", as_index=False)
        .agg(
            mean_nominees=("n_nominees", "mean"),
            median_nominees=("n_nominees", "median"),
            n_category_years=("n_nominees", "size"),
        )
        .sort_values("decade")
        .reset_index(drop=True)
    )


def plot(result: pd.DataFrame) -> Figure:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True, layout="constrained")
    nominees_ax, prob_ax = axes

    if result.empty:
        nominees_ax.set_title("Sem indicações a Melhor Filme")
        fig.suptitle("Q10 · Concorrentes e probabilidade de vitória", color=NAVY)
        return fig

    years_min = int(result["year_ceremony"].min())
    years_max = int(result["year_ceremony"].max())
    for start, end, label, color in ERA_SPANS:
        left = max(start, years_min)
        right = min(end, years_max)
        if left > right:
            continue
        nominees_ax.axvspan(left - 0.5, right + 0.5, color=color, alpha=0.12, label=label)

    nominees_ax.plot(
        result["year_ceremony"],
        result["n_nominees"],
        color=NAVY,
        linewidth=2.2,
        marker="o",
        markersize=3.5,
        label="Indicados a Melhor Filme",
    )
    nominees_ax.axhline(5, color=SLATE, linestyle="--", linewidth=1, alpha=0.7)
    nominees_ax.axhline(10, color=GOLD, linestyle="--", linewidth=1, alpha=0.7)
    nominees_ax.set_ylabel("Indicados")
    nominees_ax.set_title("Tamanho da cédula de Melhor Filme")
    nominees_ax.legend(frameon=False, loc="upper left", fontsize=8)

    prob_ax.plot(
        result["year_ceremony"],
        result["win_prob"],
        color=WINE,
        linewidth=2.2,
        label="P(vitória) em Melhor Filme = 1/N",
    )
    if result["other_win_prob"].notna().any():
        prob_ax.plot(
            result["year_ceremony"],
            result["other_win_prob"],
            color=SLATE,
            linewidth=1.6,
            alpha=0.85,
            label="P média nas demais categorias",
        )
    prob_ax.axhline(0.20, color=SLATE, linestyle=":", linewidth=1, alpha=0.8)
    prob_ax.axhline(0.10, color=GOLD, linestyle=":", linewidth=1, alpha=0.8)
    prob_ax.set_xlabel("Ano da cerimônia")
    prob_ax.set_ylabel("Probabilidade individual")
    prob_ax.set_title("De 20% para 10%: o custo matemático da cédula maior")
    prob_ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda value, _: f"{value:.0%}")
    )
    prob_ax.legend(frameon=False, loc="upper right", fontsize=8)

    fig.suptitle("Q10 · Concorrentes e probabilidade de vitória", color=NAVY)
    return fig
