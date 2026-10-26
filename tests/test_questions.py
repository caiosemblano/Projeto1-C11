import matplotlib.pyplot as plt
import pandas as pd

from projeto1_c11.questions import (
    q01_conversao,
    q02_precursoras,
    q03_evolucao,
    q04_eficiencia,
    q05_concentracao,
)


def _film(result: pd.DataFrame, film: str, year: int) -> pd.Series:
    match = result.loc[result["film"].eq(film) & result["year_ceremony"].eq(year)]
    assert len(match) == 1
    return match.iloc[0]


def test_q01_keeps_remakes_apart_and_drops_honorary(oscars: pd.DataFrame) -> None:
    result = q01_conversao.compute(oscars)
    champ_1950 = _film(result, "Champ", 1950)
    champ_2020 = _film(result, "Champ", 2020)

    assert champ_1950["nominations"] == 3
    assert champ_1950["wins"] == 2
    assert champ_2020["nominations"] == 3
    assert champ_2020["wins"] == 2
    assert "Legend" not in set(result["film"].dropna())

    snub = _film(result, "Snub", 1950)
    assert snub["nominations"] == 3
    assert snub["wins"] == 0

    grouped_by_title_only = result.groupby("film")["nominations"].sum()
    assert grouped_by_title_only.loc["Champ"] == 6


def test_q01_bins_and_plot(oscars: pd.DataFrame) -> None:
    result = q01_conversao.compute(oscars)
    bins = q01_conversao.conversion_by_bin(result)
    assert "mean_win_rate" in bins.columns
    stats = q01_conversao.correlations(result)
    assert {"pearson", "spearman"} <= set(stats.index)
    fig = q01_conversao.plot(result)
    assert fig.axes
    plt.close(fig)


def test_q02_conditional_probabilities_on_best_picture_nominees(
    oscars: pd.DataFrame,
) -> None:
    result = q02_precursoras.compute(oscars, min_category_wins=1)
    directing = result.loc[result["category"].eq("DIRECTING")].iloc[0]
    editing = result.loc[result["category"].eq("FILM EDITING")].iloc[0]

    assert directing["n_films"] == 4
    assert directing["n_bp_winners"] == 2
    assert directing["n_won_x"] == 2
    assert directing["n_won_both"] == 1
    assert directing["p_x_given_bp"] == 0.5
    assert directing["p_bp_given_x"] == 0.5

    assert editing["n_won_x"] == 1
    assert editing["n_won_both"] == 0
    assert editing["p_x_given_bp"] == 0.0
    assert editing["p_bp_given_x"] == 0.0

    fig = q02_precursoras.plot(result)
    assert fig.axes
    plt.close(fig)


def test_q03_counts_categories_per_decade(oscars: pd.DataFrame) -> None:
    result = q03_evolucao.compute(oscars)
    year_1950 = result.loc[result["decade"].eq(1950)].iloc[0]
    assert year_1950["n_ceremonies"] == 1
    assert year_1950["n_categories"] >= 4
    fig = q03_evolucao.plot(result)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_q04_filters_by_min_nominations(oscars: pd.DataFrame) -> None:
    result = q04_eficiencia.compute(oscars, min_nominations=5)
    assert list(result["name"]) == ["Star"]
    assert int(result.iloc[0]["nominations"]) == 5
    assert int(result.iloc[0]["wins"]) == 2
    assert result.iloc[0]["win_rate"] == 0.4

    fig = q04_eficiencia.plot(result)
    assert fig.axes
    plt.close(fig)


def test_q05_concentration_per_ceremony(oscars: pd.DataFrame) -> None:
    result = q05_concentracao.compute(oscars)
    year_1950 = result.loc[result["year_ceremony"].eq(1950)].iloc[0]
    year_2020 = result.loc[result["year_ceremony"].eq(2020)].iloc[0]

    assert year_1950["n_winning_films"] == 1
    assert year_1950["n_awards"] == 2
    assert year_1950["top_film_share"] == 1.0

    assert year_2020["n_winning_films"] == 3
    assert year_2020["n_awards"] == 4
    assert year_2020["max_film_wins"] == 2
    assert year_2020["top_film_share"] == 0.5

    fig = q05_concentracao.plot(result)
    assert fig.axes
    plt.close(fig)
