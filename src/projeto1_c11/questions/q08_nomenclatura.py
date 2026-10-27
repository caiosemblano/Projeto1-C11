"""Q8: mudanças históricas nos nomes das categorias."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.plotting import GOLD, NAVY, SLATE, WINE

SLUG = "q08_nomenclatura"
QUESTION = (
    "Como a nomenclatura das categorias mudou ao longo da história do Oscar "
    "e o que isso revela sobre a modernização da indústria?"
)

NOMENCLATURE_FAMILIES = (
    "BEST PICTURE",
    "ACTOR IN A LEADING ROLE",
    "ACTRESS IN A LEADING ROLE",
    "INTERNATIONAL FEATURE FILM",
    "ART DIRECTION",
    "MAKEUP AND HAIRSTYLING",
)

FAMILY_COLORS = (NAVY, GOLD, WINE, SLATE, "#3D6B4F", "#6B4C9A")


def compute(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby(["category_canon", "category"], as_index=False).agg(
        first_year=("year_ceremony", "min"),
        last_year=("year_ceremony", "max"),
        n_ceremonies=("year_ceremony", "nunique"),
        n_entries=("winner", "size"),
    )
    grouped["n_distinct_names"] = grouped.groupby("category_canon")["category"].transform(
        "nunique"
    )
    return grouped.sort_values(
        ["category_canon", "first_year", "category"]
    ).reset_index(drop=True)


def renamed_families(result: pd.DataFrame) -> pd.DataFrame:
    return result.loc[result["n_distinct_names"].gt(1)].copy()


def _timeline_rows(result: pd.DataFrame) -> pd.DataFrame:
    preferred = result.loc[result["category_canon"].isin(NOMENCLATURE_FAMILIES)]
    if not preferred.empty:
        return preferred
    renamed = renamed_families(result)
    if not renamed.empty:
        return renamed
    return result


def plot(result: pd.DataFrame) -> Figure:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 8), layout="constrained")
    rows = _timeline_rows(result)
    if rows.empty:
        ax.set_title("Sem categorias para a linha do tempo")
        fig.suptitle("Q8 · Modernização dos nomes das categorias", color=NAVY)
        return fig

    rows = rows.sort_values(["category_canon", "first_year"]).reset_index(drop=True)
    families = list(dict.fromkeys(rows["category_canon"].tolist()))
    color_map = {
        family: FAMILY_COLORS[index % len(FAMILY_COLORS)]
        for index, family in enumerate(families)
    }

    labels = []
    for y_pos, row in rows.iterrows():
        color = color_map[row["category_canon"]]
        start = int(row["first_year"])
        end = int(row["last_year"])
        ax.hlines(y_pos, start, end, colors=color, linewidth=6, alpha=0.85)
        ax.plot([start, end], [y_pos, y_pos], "o", color=color, markersize=5)
        labels.append(str(row["category"]).title())

    ax.set_yticks(range(len(rows)), labels=labels)
    ax.set_xlabel("Ano da cerimônia")
    ax.set_ylabel("Nome original da categoria")
    ax.set_title("Linha do tempo das mudanças de nomenclatura")
    ax.invert_yaxis()

    handles = [
        plt.Line2D([0], [0], color=color_map[family], lw=4, label=family.title())
        for family in families
    ]
    ax.legend(
        handles=handles,
        frameon=False,
        loc="lower right",
        fontsize=8,
        title="Família canônica",
    )
    fig.suptitle("Q8 · Modernização dos nomes das categorias", color=NAVY)
    return fig
