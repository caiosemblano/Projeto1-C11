"""Q9: janela year_film vs. year_ceremony e o calendário das cerimônias."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.config import ACADEMY_ORIGIN_YEAR, COVID_CEREMONY_YEAR
from projeto1_c11.plotting import GOLD, NAVY, SLATE, WINE

SLUG = "q09_elegibilidade"
QUESTION = (
    "Existe diferença histórica no comportamento de year_film vs. "
    "year_ceremony (janelas de elegibilidade atípicas, pandemia ou os "
    "primeiros anos da Academia)?"
)

MILESTONES = (
    (1933, "Janelas 1927/28–1932/33"),
    (1935, "Alinhamento ao ano civil"),
    (COVID_CEREMONY_YEAR, "Janela COVID-19"),
)


def compute(df: pd.DataFrame) -> pd.DataFrame:
    yearly = (
        df.groupby(["ceremony", "year_ceremony"], as_index=False)
        .agg(
            year_film=("year_film", "first"),
            n_nominations=("winner", "size"),
            n_categories=("category", "nunique"),
        )
        .sort_values("ceremony")
    )
    yearly["lag_film_ceremony"] = yearly["year_ceremony"] - yearly["year_film"]
    yearly["calendar_gap"] = yearly["year_ceremony"].diff()
    yearly["ceremony_offset"] = yearly["year_ceremony"] - (
        ACADEMY_ORIGIN_YEAR + yearly["ceremony"]
    )
    return yearly.reset_index(drop=True)


def calendar_anomalies(result: pd.DataFrame) -> pd.DataFrame:
    gaps = result["calendar_gap"]
    return result.loc[gaps.notna() & gaps.ne(1)].copy()


def _annotate_milestone(ax, result: pd.DataFrame, year: int, text: str, y_col: str) -> None:
    match = result.loc[result["year_ceremony"].eq(year)]
    if match.empty:
        return
    row = match.iloc[0]
    ax.annotate(
        text,
        (row["year_ceremony"], row[y_col]),
        textcoords="offset points",
        xytext=(8, 12),
        fontsize=8,
        color=NAVY,
        arrowprops={"arrowstyle": "-", "color": SLATE, "lw": 0.6},
    )


def plot(result: pd.DataFrame) -> Figure:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True, layout="constrained")
    lag_ax, volume_ax = axes

    lag_ax.plot(
        result["year_ceremony"],
        result["lag_film_ceremony"],
        marker="o",
        color=GOLD,
        label="year_ceremony − year_film",
    )
    lag_ax.plot(
        result["year_ceremony"],
        result["ceremony_offset"],
        marker="s",
        color=NAVY,
        label="offset do calendário (ano − 1927 − edição)",
    )
    lag_ax.set_ylabel("Anos")
    lag_ax.set_title("Lag do CSV vs. mudança permanente de calendário")
    lag_ax.legend(frameon=False, loc="center right")
    for year, text in MILESTONES:
        _annotate_milestone(lag_ax, result, year, text, "ceremony_offset")

    volume_ax.plot(
        result["year_ceremony"],
        result["n_nominations"],
        color=WINE,
        linewidth=2,
        label="Indicações por cerimônia",
    )
    volume_ax.set_xlabel("Ano da cerimônia")
    volume_ax.set_ylabel("Indicações")
    volume_ax.set_title("Volume de reconhecimento e marcos regulamentares")
    for year, text in MILESTONES:
        match = result.loc[result["year_ceremony"].eq(year)]
        if match.empty:
            continue
        volume_ax.axvline(year, color=SLATE, alpha=0.35, linestyle="--", linewidth=1)
        _annotate_milestone(volume_ax, result, year, text, "n_nominations")

    fig.suptitle("Q9 · Janelas de elegibilidade e o calendário da Academia", color=NAVY)
    return fig
