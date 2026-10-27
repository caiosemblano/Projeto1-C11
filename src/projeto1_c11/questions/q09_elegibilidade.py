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
    (1933, "Última janela 1927/28–1932/33"),
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


def plot(result: pd.DataFrame) -> Figure:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 1, figsize=(11, 7.5), sharex=True, layout="constrained")
    lag_ax, volume_ax = axes

    lag_constant = (
        float(result["lag_film_ceremony"].mode().iloc[0])
        if not result.empty
        else 1.0
    )
    lag_ax.axhline(
        lag_constant,
        color=GOLD,
        linestyle="--",
        linewidth=1.8,
        label=f"lag do CSV (sempre {lag_constant:.0f})",
    )
    lag_ax.step(
        result["year_ceremony"],
        result["ceremony_offset"],
        where="post",
        color=NAVY,
        linewidth=2.4,
        label="offset do calendário (ano − 1927 − edição)",
    )
    lag_ax.set_ylabel("Anos")
    lag_ax.set_title("Lag do CSV vs. mudança permanente de calendário")
    lag_ax.set_ylim(-0.2, 1.45)
    lag_ax.legend(frameon=False, loc="center right")
    if result["year_ceremony"].le(1933).any():
        lag_ax.text(
            0.02,
            0.18,
            "1928–1933: offset = 0\n(janelas 1927/28–1932/33)",
            transform=lag_ax.transAxes,
            fontsize=8,
            color=NAVY,
        )
    if result["year_ceremony"].eq(1935).any():
        lag_ax.text(
            0.22,
            0.55,
            "1935–hoje: offset = lag = 1",
            transform=lag_ax.transAxes,
            fontsize=8,
            color=NAVY,
        )

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
    label_offsets = {
        1933: (6, -28),
        1935: (8, 14),
        COVID_CEREMONY_YEAR: (-110, 12),
    }
    for year, text in MILESTONES:
        match = result.loc[result["year_ceremony"].eq(year)]
        if match.empty:
            continue
        volume_ax.axvline(year, color=SLATE, alpha=0.35, linestyle="--", linewidth=1)
        row = match.iloc[0]
        volume_ax.annotate(
            text,
            (row["year_ceremony"], row["n_nominations"]),
            textcoords="offset points",
            xytext=label_offsets.get(year, (8, 12)),
            fontsize=8,
            color=NAVY,
            arrowprops={"arrowstyle": "-", "color": SLATE, "lw": 0.6},
        )

    fig.suptitle("Q9 · Janelas de elegibilidade e o calendário da Academia", color=NAVY)
    return fig
