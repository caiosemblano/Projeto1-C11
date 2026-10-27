"""Q6: persistência premiada e profissionais que nunca venceram."""

from __future__ import annotations

import pandas as pd
from matplotlib.figure import Figure

from projeto1_c11.categories import is_country_award_category
from projeto1_c11.config import TOP_N
from projeto1_c11.data import competitive
from projeto1_c11.plotting import GOLD, NAVY, SLATE, WINE

SLUG = "q06_persistencia"
QUESTION = (
    "Quais são os casos de persistência premiada — profissionais que mais "
    "acumularam indicações antes da primeira estatueta — e quem são os "
    "maiores injustiçados que nunca venceram?"
)

STATUS_LATE = "campeao_tardio"
STATUS_NEVER = "sem_vitoria"


def compute(df: pd.DataFrame) -> pd.DataFrame:
    people = competitive(df).dropna(subset=["name"])
    people = people.loc[~is_country_award_category(people["category_canon"])]

    totals = people.groupby("name", as_index=False).agg(
        nominations=("winner", "size"),
        wins=("winner", "sum"),
        first_year=("year_ceremony", "min"),
    )
    first_win = (
        people.loc[people["winner"], ["name", "year_ceremony"]]
        .groupby("name", as_index=False)
        .agg(first_win_year=("year_ceremony", "min"))
    )
    result = totals.merge(first_win, on="name", how="left")

    losses = people.loc[~people["winner"], ["name", "year_ceremony"]].merge(
        first_win, on="name", how="left"
    )
    before_first_win = losses.loc[
        losses["first_win_year"].isna()
        | (losses["year_ceremony"] < losses["first_win_year"])
    ]
    loss_counts = (
        before_first_win.groupby("name").size().rename("losses_before_first_win")
    )
    result = result.merge(loss_counts, on="name", how="left")
    result["losses_before_first_win"] = (
        result["losses_before_first_win"].fillna(0).astype(int)
    )
    result["wins"] = result["wins"].astype(int)
    result["first_win_year"] = result["first_win_year"].astype("Int64")
    result["status"] = STATUS_NEVER
    result.loc[result["wins"].gt(0), "status"] = STATUS_LATE
    return result.sort_values(
        ["losses_before_first_win", "nominations"], ascending=False
    ).reset_index(drop=True)


def late_champions(result: pd.DataFrame, *, top_n: int = TOP_N) -> pd.DataFrame:
    won = result.loc[result["wins"].gt(0)]
    return won.nlargest(top_n, ["losses_before_first_win", "nominations"]).sort_values(
        ["losses_before_first_win", "nominations"]
    )


def never_won(result: pd.DataFrame, *, top_n: int = TOP_N) -> pd.DataFrame:
    lost = result.loc[result["wins"].eq(0)]
    return lost.nlargest(top_n, "nominations").sort_values("nominations")


def plot(result: pd.DataFrame, *, top_n: int = TOP_N) -> Figure:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 7), layout="constrained")
    late_ax, snub_ax = axes

    late = late_champions(result, top_n=top_n)
    if late.empty:
        late_ax.set_title("Sem campeões tardios no recorte")
    else:
        late_ax.barh(late["name"], late["losses_before_first_win"], color=GOLD)
        late_ax.set_xlabel("Indicações perdidas antes da 1ª vitória")
        late_ax.set_title(f"Top {len(late)} · persistência premiada")
        max_loss = float(late["losses_before_first_win"].max())
        late_ax.set_xlim(0, max(1.0, max_loss * 1.28))
        for y_pos, losses, wins in zip(
            range(len(late)),
            late["losses_before_first_win"],
            late["wins"],
            strict=True,
        ):
            inside = losses > max_loss * 0.62
            late_ax.text(
                losses - 0.25 if inside else losses + 0.2,
                y_pos,
                f"{int(losses)} · {int(wins)} vit.",
                va="center",
                ha="right" if inside else "left",
                fontsize=8,
                color="white" if inside else NAVY,
            )

    snubs = never_won(result, top_n=top_n)
    if snubs.empty:
        snub_ax.set_title("Sem profissionais sem vitória no recorte")
    else:
        snub_ax.barh(snubs["name"], snubs["nominations"], color=WINE)
        snub_ax.set_xlabel("Indicações sem nenhuma estatueta")
        snub_ax.set_title(f"Top {len(snubs)} · injustiçados (0 vitórias)")
        max_noms = float(snubs["nominations"].max())
        snub_ax.set_xlim(0, max(1.0, max_noms * 1.22))
        for y_pos, nominations in zip(
            range(len(snubs)), snubs["nominations"], strict=True
        ):
            inside = nominations > max_noms * 0.62
            snub_ax.text(
                nominations - 0.25 if inside else nominations + 0.2,
                y_pos,
                str(int(nominations)),
                va="center",
                ha="right" if inside else "left",
                fontsize=8,
                color="white" if inside else SLATE,
            )

    fig.suptitle("Q6 · Persistência premiada e maiores esnobados", color=NAVY)
    return fig
