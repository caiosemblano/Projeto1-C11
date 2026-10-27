"""Q5: concentração vs. pulverização das vitórias por cerimônia."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.categories import decade
from projeto1_c11.config import FILM_KEY, ROLLING_WINDOW
from projeto1_c11.data import competitive
from projeto1_c11.plotting import GOLD, NAVY, WINE

SLUG = "q05_concentracao"
QUESTION = (
    "Qual é o nível de concentração vs. democratização do Oscar ao longo do "
    "tempo: quantos filmes diferentes dividem os prêmios em uma cerimônia?"
)


def compute(df: pd.DataFrame, *, rolling_window: int = ROLLING_WINDOW) -> pd.DataFrame:
    winners = competitive(df)
    winners = winners.loc[winners["winner"]].dropna(subset=["film"])
    per_film = (
        winners.groupby(list(FILM_KEY), as_index=False)
        .size()
        .rename(columns={"size": "film_wins"})
    )
    yearly = (
        per_film.groupby("year_ceremony", as_index=False)
        .agg(
            n_winning_films=("film", "nunique"),
            n_awards=("film_wins", "sum"),
            max_film_wins=("film_wins", "max"),
        )
        .sort_values("year_ceremony")
    )
    yearly["top_film_share"] = yearly["max_film_wins"] / yearly["n_awards"]
    yearly["decade"] = decade(yearly["year_ceremony"].to_numpy())
    yearly["n_winning_films_ma"] = (
        yearly["n_winning_films"]
        .rolling(rolling_window, center=True, min_periods=1)
        .mean()
    )
    yearly["top_film_share_ma"] = (
        yearly["top_film_share"]
        .rolling(rolling_window, center=True, min_periods=1)
        .mean()
    )
    return yearly.reset_index(drop=True)


def decade_means(result: pd.DataFrame) -> pd.DataFrame:
    return (
        result.groupby("decade", as_index=False)
        .agg(
            mean_winning_films=("n_winning_films", "mean"),
            mean_top_film_share=("top_film_share", "mean"),
            n_ceremonies=("year_ceremony", "size"),
        )
        .sort_values("decade")
        .reset_index(drop=True)
    )


def plot(result: pd.DataFrame) -> Figure:
    import matplotlib.pyplot as plt

    by_decade = decade_means(result)
    fig, axes = plt.subplots(2, 1, figsize=(11, 8), sharex=False, layout="constrained")
    year_ax, decade_ax = axes

    year_ax.plot(
        result["year_ceremony"],
        result["n_winning_films"],
        color=GOLD,
        alpha=0.45,
        linewidth=1,
        label="Filmes vencedores",
    )
    year_ax.plot(
        result["year_ceremony"],
        result["n_winning_films_ma"],
        color=NAVY,
        linewidth=2.4,
        label=f"Média móvel ({ROLLING_WINDOW} anos)",
    )
    year_ax.set_xlabel("Ano da cerimônia")
    year_ax.set_ylabel("Filmes distintos com ≥ 1 vitória")
    year_ax.set_title("Varredura vs. pulverização, ano a ano")
    year_ax.legend(frameon=False, loc="upper left")

    decade_ax.bar(
        by_decade["decade"].astype(str),
        by_decade["mean_winning_films"],
        color=WINE,
    )
    decade_ax.set_xlabel("Década")
    decade_ax.set_ylabel("Média de filmes vencedores")
    decade_ax.set_title("Média por década")

    fig.suptitle("Q5 · Concentração das estatuetas", color=NAVY)
    return fig
