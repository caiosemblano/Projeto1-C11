"""Q3: evolução das categorias e do volume de prêmios por década."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.plotting import GOLD, NAVY, WINE

SLUG = "q03_evolucao"
QUESTION = (
    "Como o perfil da Academia evoluiu ao longo das décadas em termos de "
    "diversidade de categorias e quantidade de prêmios distribuídos por cerimônia?"
)


def compute(df: pd.DataFrame) -> pd.DataFrame:
    grouped = (
        df.groupby("decade", as_index=False)
        .agg(
            n_categories=("category", "nunique"),
            n_categories_canon=("category_canon", "nunique"),
            n_nominations=("winner", "size"),
            n_wins=("winner", "sum"),
            n_ceremonies=("year_ceremony", "nunique"),
        )
        .sort_values("decade")
    )
    grouped["n_wins"] = grouped["n_wins"].astype(int)
    grouped["wins_per_ceremony"] = grouped["n_wins"] / grouped["n_ceremonies"]
    grouped["nominations_per_ceremony"] = (
        grouped["n_nominations"] / grouped["n_ceremonies"]
    )
    return grouped.reset_index(drop=True)


def plot(result: pd.DataFrame) -> Figure:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=True, layout="constrained")
    cat_ax, volume_ax = axes

    cat_ax.plot(
        result["decade"],
        result["n_categories"],
        marker="o",
        color=NAVY,
        label="Nomes originais",
    )
    cat_ax.plot(
        result["decade"],
        result["n_categories_canon"],
        marker="s",
        color=GOLD,
        label="Após unificar Melhor Filme",
    )
    cat_ax.set_ylabel("Categorias distintas")
    cat_ax.set_title("Diversidade de categorias por década")
    cat_ax.legend(frameon=False, loc="upper left")

    volume_ax.plot(
        result["decade"],
        result["nominations_per_ceremony"],
        marker="o",
        color=NAVY,
        label="Indicações / cerimônia",
    )
    volume_ax.plot(
        result["decade"],
        result["wins_per_ceremony"],
        marker="s",
        color=WINE,
        label="Vitórias / cerimônia",
    )
    volume_ax.set_xlabel("Década")
    volume_ax.set_ylabel("Média por cerimônia")
    volume_ax.set_title("Volume de reconhecimento por noite")
    volume_ax.legend(frameon=False, loc="upper left")

    fig.suptitle("Q3 · Expansão da Academia ao longo do tempo", color=NAVY)
    return fig
