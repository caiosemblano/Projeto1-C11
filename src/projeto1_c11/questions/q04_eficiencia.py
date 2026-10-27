"""Q4: volume de indicações e eficiência (taxa de vitória) por profissional."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.categories import is_country_award_category
from projeto1_c11.config import MIN_NOMINATIONS, TOP_N
from projeto1_c11.data import competitive
from projeto1_c11.plotting import GOLD, NAVY, WINE

SLUG = "q04_eficiencia"
QUESTION = (
    "Quais profissionais ou entidades possuem o maior histórico de indicações "
    "e quem tem a melhor eficiência entre os mais indicados?"
)


def compute(
    df: pd.DataFrame, *, min_nominations: int = MIN_NOMINATIONS
) -> pd.DataFrame:
    people = competitive(df).dropna(subset=["name"])
    people = people.loc[~is_country_award_category(people["category_canon"])]
    grouped = people.groupby("name", as_index=False).agg(
        nominations=("winner", "size"),
        wins=("winner", "sum"),
        first_year=("year_ceremony", "min"),
        last_year=("year_ceremony", "max"),
    )
    grouped = grouped.loc[grouped["nominations"] >= min_nominations].copy()
    grouped["wins"] = grouped["wins"].astype(int)
    grouped["win_rate"] = grouped["wins"] / grouped["nominations"]
    return grouped.sort_values(
        ["nominations", "wins"], ascending=False
    ).reset_index(drop=True)


def plot(result: pd.DataFrame, *, top_n: int = TOP_N) -> Figure:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), layout="constrained")
    noms_ax, rate_ax = axes

    top_noms = result.nlargest(top_n, "nominations").sort_values("nominations")
    noms_ax.barh(top_noms["name"], top_noms["nominations"], color=GOLD)
    noms_ax.set_xlabel("Indicações")
    noms_ax.set_title(f"Top {top_n} em volume de indicações")

    top_rate = result.nlargest(top_n, ["win_rate", "nominations"]).sort_values(
        "win_rate"
    )
    rate_ax.barh(top_rate["name"], top_rate["win_rate"], color=WINE)
    rate_ax.set_xlabel("Taxa de vitória")
    rate_ax.set_title(f"Top {top_n} em eficiência (≥ {MIN_NOMINATIONS} indicações)")
    rate_ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda value, _: f"{value:.0%}"))

    fig.suptitle("Q4 · Star power: volume vs. eficiência", color=NAVY)
    return fig
