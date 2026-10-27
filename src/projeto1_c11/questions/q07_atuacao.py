"""Q7: recordistas e evolução das categorias de atuação."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.categories import (
    is_acting_category,
    is_leading_acting_category,
    is_supporting_acting_category,
)
from projeto1_c11.config import TOP_N
from projeto1_c11.data import competitive
from projeto1_c11.plotting import GOLD, NAVY, WINE

SLUG = "q07_atuacao"
QUESTION = (
    "Qual a evolução e representatividade das categorias de atuação "
    "(Ator/Atriz Principal e Coadjuvante) — quem são os recordistas de "
    "indicações e vitórias nessas quatro categorias?"
)


def _acting_rows(df: pd.DataFrame) -> pd.DataFrame:
    acting = competitive(df).dropna(subset=["name"])
    return acting.loc[is_acting_category(acting["category_canon"])].copy()


def compute(df: pd.DataFrame) -> pd.DataFrame:
    acting = _acting_rows(df)
    if acting.empty:
        return pd.DataFrame(
            columns=[
                "name",
                "nominations",
                "wins",
                "win_rate",
                "leading_nominations",
                "supporting_nominations",
                "first_year",
                "last_year",
            ]
        )

    acting["is_leading"] = is_leading_acting_category(acting["category_canon"])
    acting["is_supporting"] = is_supporting_acting_category(acting["category_canon"])
    grouped = acting.groupby("name", as_index=False).agg(
        nominations=("winner", "size"),
        wins=("winner", "sum"),
        leading_nominations=("is_leading", "sum"),
        supporting_nominations=("is_supporting", "sum"),
        first_year=("year_ceremony", "min"),
        last_year=("year_ceremony", "max"),
    )
    grouped["wins"] = grouped["wins"].astype(int)
    grouped["leading_nominations"] = grouped["leading_nominations"].astype(int)
    grouped["supporting_nominations"] = grouped["supporting_nominations"].astype(int)
    grouped["win_rate"] = grouped["wins"] / grouped["nominations"]
    return grouped.sort_values(
        ["nominations", "wins"], ascending=False
    ).reset_index(drop=True)


def decade_breakdown(df: pd.DataFrame) -> pd.DataFrame:
    acting = _acting_rows(df)
    if acting.empty:
        return pd.DataFrame(
            columns=["decade", "category_canon", "n_nominations", "n_wins"]
        )
    grouped = (
        acting.groupby(["decade", "category_canon"], as_index=False)
        .agg(n_nominations=("winner", "size"), n_wins=("winner", "sum"))
        .sort_values(["decade", "category_canon"])
    )
    grouped["n_wins"] = grouped["n_wins"].astype(int)
    return grouped.reset_index(drop=True)


def plot(result: pd.DataFrame, *, top_n: int = TOP_N) -> Figure:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), layout="constrained")
    noms_ax, wins_ax = axes

    if result.empty:
        noms_ax.set_title("Sem indicações de atuação no recorte")
        wins_ax.set_title("Sem vitórias de atuação no recorte")
        fig.suptitle("Q7 · Recordistas de atuação", color=NAVY)
        return fig

    top_noms = result.nlargest(top_n, ["nominations", "wins"]).sort_values(
        "nominations"
    )
    noms_ax.barh(top_noms["name"], top_noms["nominations"], color=GOLD, label="Indicações")
    noms_ax.barh(top_noms["name"], top_noms["wins"], color=WINE, label="Vitórias")
    noms_ax.set_xlabel("Indicações (ouro) e vitórias (vinho)")
    noms_ax.set_title(f"Top {len(top_noms)} em indicações de atuação")
    noms_ax.legend(frameon=False, loc="lower right")

    top_wins = result.nlargest(top_n, ["wins", "nominations"]).sort_values("wins")
    wins_ax.barh(top_wins["name"], top_wins["wins"], color=WINE)
    wins_ax.set_xlabel("Estatuetas de atuação")
    wins_ax.set_title(f"Top {len(top_wins)} em vitórias de atuação")
    for y_pos, wins, nominations in zip(
        range(len(top_wins)), top_wins["wins"], top_wins["nominations"], strict=True
    ):
        wins_ax.text(
            wins + 0.08,
            y_pos,
            f"{int(wins)} vit. · {int(nominations)} ind.",
            va="center",
            ha="left",
            fontsize=8,
            color=NAVY,
        )

    fig.suptitle("Q7 · Ícones de atuação: volume vs. estatuetas", color=NAVY)
    return fig
