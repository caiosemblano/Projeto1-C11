"""Q2: categorias correlacionadas com a vitória em Melhor Filme."""

from __future__ import annotations

import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.categories import BEST_PICTURE_CANON
from projeto1_c11.config import FILM_KEY, MIN_CATEGORY_WINS, TOP_N
from projeto1_c11.data import competitive
from projeto1_c11.plotting import GOLD, NAVY

SLUG = "q02_precursoras"
QUESTION = (
    "Para um filme vencer Melhor Filme, quais outras categorias historicamente "
    "têm a maior correlação de vitória conjunta?"
)

RESULT_COLUMNS = (
    "category",
    "n_films",
    "n_bp_winners",
    "n_won_x",
    "n_won_both",
    "p_x_given_bp",
    "p_bp_given_x",
    "phi",
)


def phi_coefficient(left: np.ndarray, right: np.ndarray) -> float:
    """Coeficiente phi (correlação de Pearson entre duas binárias)."""
    a = np.asarray(left, dtype=bool)
    b = np.asarray(right, dtype=bool)
    n11 = np.float64(np.sum(a & b))
    n10 = np.float64(np.sum(a & ~b))
    n01 = np.float64(np.sum(~a & b))
    n00 = np.float64(np.sum(~a & ~b))
    denom = np.sqrt((n11 + n10) * (n01 + n00) * (n11 + n01) * (n10 + n00))
    if denom == 0:
        return float("nan")
    return float((n11 * n00 - n10 * n01) / denom)


def compute(
    df: pd.DataFrame, *, min_category_wins: int = MIN_CATEGORY_WINS
) -> pd.DataFrame:
    rows = competitive(df).dropna(subset=["film"])
    bp_noms = rows.loc[rows["is_best_picture"], list(FILM_KEY)].drop_duplicates()
    if bp_noms.empty:
        return pd.DataFrame(columns=list(RESULT_COLUMNS))

    wins = rows.loc[rows["winner"], list(FILM_KEY) + ["category_canon"]].drop_duplicates()
    wins = wins.merge(bp_noms, on=list(FILM_KEY), how="inner")
    index = pd.MultiIndex.from_frame(bp_noms)
    if wins.empty:
        matrix = pd.DataFrame(index=index)
    else:
        wins = wins.assign(flag=1)
        matrix = wins.pivot_table(
            index=list(FILM_KEY),
            columns="category_canon",
            values="flag",
            aggfunc="max",
            fill_value=0,
        )
        matrix = matrix.reindex(index, fill_value=0)

    if BEST_PICTURE_CANON in matrix.columns:
        won_bp = matrix[BEST_PICTURE_CANON].to_numpy(dtype=bool)
    else:
        won_bp = np.zeros(len(matrix), dtype=bool)

    n_bp_winners = int(won_bp.sum())
    n_films = int(len(matrix))
    records: list[dict[str, object]] = []
    for category in matrix.columns:
        if category == BEST_PICTURE_CANON:
            continue
        won_x = matrix[category].to_numpy(dtype=bool)
        n_won_x = int(won_x.sum())
        if n_won_x < min_category_wins:
            continue
        n_both = int(np.sum(won_x & won_bp))
        records.append(
            {
                "category": category,
                "n_films": n_films,
                "n_bp_winners": n_bp_winners,
                "n_won_x": n_won_x,
                "n_won_both": n_both,
                "p_x_given_bp": n_both / n_bp_winners if n_bp_winners else np.nan,
                "p_bp_given_x": n_both / n_won_x if n_won_x else np.nan,
                "phi": phi_coefficient(won_bp, won_x),
            }
        )

    result = pd.DataFrame.from_records(records, columns=list(RESULT_COLUMNS))
    if result.empty:
        return result
    return result.sort_values("phi", ascending=False).reset_index(drop=True)


def plot(result: pd.DataFrame, *, top_n: int = TOP_N) -> Figure:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(11, 7), layout="constrained")
    if result.empty:
        ax.set_title("Sem categorias com suporte suficiente")
        return fig

    top = result.nlargest(top_n, "phi").sort_values("phi")
    labels = top["category"].str.title()
    ax.barh(labels, top["phi"], color=GOLD)
    ax.set_xlabel("Coeficiente φ (filme indicado a Melhor Filme)")
    ax.set_ylabel("Categoria")
    ax.set_title("Categorias precursoras da vitória em Melhor Filme")
    max_phi = float(top["phi"].max()) if len(top) else 0.0
    ax.set_xlim(0, max(0.15, max_phi * 1.42))
    for y_pos, phi, p_x in zip(
        range(len(top)), top["phi"], top["p_x_given_bp"], strict=True
    ):
        inside = phi > max_phi * 0.62
        ax.text(
            phi - 0.01 if inside else phi + 0.008,
            y_pos,
            f"φ={phi:.2f} · P(X|BP)={p_x:.0%}",
            va="center",
            ha="right" if inside else "left",
            fontsize=8,
            color="white" if inside else NAVY,
        )
    fig.suptitle("Q2 · Correlação conjunta com Melhor Filme", color=NAVY)
    return fig
