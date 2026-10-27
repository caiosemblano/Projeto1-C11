import matplotlib.pyplot as plt
import pandas as pd

from projeto1_c11.questions import (
    q01_conversao,
    q02_precursoras,
    q03_evolucao,
    q04_eficiencia,
    q05_concentracao,
    q06_persistencia,
    q07_atuacao,
    q08_nomenclatura,
    q09_elegibilidade,
    q10_concorrentes,
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


def test_q06_counts_losses_before_first_win(oscars: pd.DataFrame) -> None:
    result = q06_persistencia.compute(oscars)
    late = result.loc[result["name"].eq("Late")].iloc[0]
    snubbed = result.loc[result["name"].eq("Snubbed")].iloc[0]
    star = result.loc[result["name"].eq("Star")].iloc[0]

    assert int(late["losses_before_first_win"]) == 2
    assert int(late["wins"]) == 1
    assert int(late["first_win_year"]) == 2012
    assert late["status"] == q06_persistencia.STATUS_LATE

    assert int(snubbed["nominations"]) == 3
    assert int(snubbed["wins"]) == 0
    assert int(snubbed["losses_before_first_win"]) == 3
    assert pd.isna(snubbed["first_win_year"])
    assert snubbed["status"] == q06_persistencia.STATUS_NEVER

    assert int(star["losses_before_first_win"]) == 0
    assert "Legend" not in set(result["name"])

    fig = q06_persistencia.plot(result)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_q07_splits_leading_and_supporting(oscars: pd.DataFrame) -> None:
    result = q07_atuacao.compute(oscars)
    star = result.loc[result["name"].eq("Star")].iloc[0]
    support = result.loc[result["name"].eq("Support Star")].iloc[0]
    newcomer = result.loc[result["name"].eq("Newcomer")].iloc[0]

    assert int(star["nominations"]) == 5
    assert int(star["wins"]) == 2
    assert int(star["leading_nominations"]) == 5
    assert int(star["supporting_nominations"]) == 0
    assert star["win_rate"] == 0.4

    assert int(support["supporting_nominations"]) == 1
    assert int(support["leading_nominations"]) == 0
    assert int(newcomer["leading_nominations"]) == 1

    by_decade = q07_atuacao.decade_breakdown(oscars)
    assert "ACTOR IN A LEADING ROLE" in set(by_decade["category_canon"])
    assert "ACTRESS IN A SUPPORTING ROLE" in set(by_decade["category_canon"])

    fig = q07_atuacao.plot(result)
    assert fig.axes
    plt.close(fig)


def test_q08_tracks_historical_aliases(oscars: pd.DataFrame) -> None:
    result = q08_nomenclatura.compute(oscars)
    best_picture = result.loc[result["category_canon"].eq("BEST PICTURE")]
    acting = result.loc[result["category_canon"].eq("ACTOR IN A LEADING ROLE")]

    assert set(best_picture["category"]) == {"OUTSTANDING PICTURE", "BEST PICTURE"}
    assert int(best_picture["n_distinct_names"].iloc[0]) == 2
    assert set(acting["category"]) == {"ACTOR", "ACTOR IN A LEADING ROLE"}
    assert int(acting["n_distinct_names"].iloc[0]) == 2

    renamed = q08_nomenclatura.renamed_families(result)
    assert {"BEST PICTURE", "ACTOR IN A LEADING ROLE"} <= set(renamed["category_canon"])

    fig = q08_nomenclatura.plot(result)
    assert fig.axes
    plt.close(fig)


def test_q09_calendar_gap_and_ceremony_offset(oscars: pd.DataFrame) -> None:
    result = q09_elegibilidade.compute(oscars)
    year_1933 = result.loc[result["year_ceremony"].eq(1933)].iloc[0]
    year_1935 = result.loc[result["year_ceremony"].eq(1935)].iloc[0]

    assert (result["lag_film_ceremony"] == 1).all()
    assert int(year_1933["ceremony_offset"]) == 0
    assert int(year_1935["ceremony_offset"]) == 1
    assert int(year_1935["calendar_gap"]) == 2

    anomalies = q09_elegibilidade.calendar_anomalies(result)
    assert 1935 in set(anomalies["year_ceremony"])

    fig = q09_elegibilidade.plot(result)
    assert len(fig.axes) == 2
    plt.close(fig)


def test_q10_win_probability_is_one_over_nominees(oscars: pd.DataFrame) -> None:
    result = q10_concorrentes.compute(oscars)
    year_1950 = result.loc[result["year_ceremony"].eq(1950)].iloc[0]
    year_2020 = result.loc[result["year_ceremony"].eq(2020)].iloc[0]

    assert int(year_1950["n_nominees"]) == 2
    assert int(year_1950["n_winners"]) == 1
    assert year_1950["win_prob"] == 0.5
    assert int(year_2020["n_nominees"]) == 2
    assert year_2020["win_prob"] == 0.5

    by_decade = q10_concorrentes.category_competition_by_decade(oscars)
    assert not by_decade.empty

    fig = q10_concorrentes.plot(result)
    assert fig.axes
    plt.close(fig)
