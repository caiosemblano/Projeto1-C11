import pandas as pd

from projeto1_c11.categories import (
    BEST_PICTURE_CANON,
    decade,
    is_country_award_category,
)
from projeto1_c11.data import clean


def test_outstanding_picture_becomes_best_picture(oscars: pd.DataFrame) -> None:
    outstanding = oscars.loc[oscars["category"].eq("OUTSTANDING PICTURE")]
    assert outstanding["category_canon"].eq(BEST_PICTURE_CANON).all()
    assert outstanding["is_best_picture"].all()


def test_honorary_flag_and_missing_film(oscars: pd.DataFrame) -> None:
    honorary = oscars.loc[oscars["category"].eq("HONORARY AWARD")]
    assert honorary["is_honorary"].all()
    assert honorary["film"].isna().all()


def test_special_effects_is_competitive(oscars: pd.DataFrame) -> None:
    effects = oscars.loc[oscars["category"].eq("SPECIAL EFFECTS")]
    assert not effects["is_honorary"].any()


def test_country_award_categories_are_detected() -> None:
    labels = pd.Series(["INTERNATIONAL FEATURE FILM", "DIRECTING", "FOREIGN LANGUAGE FILM"])
    assert list(is_country_award_category(labels)) == [True, False, True]


def test_decade_uses_numpy_floor(oscars: pd.DataFrame) -> None:
    assert set(oscars["decade"]) == {1950, 2010, 2020}
    assert (decade(oscars["year_ceremony"]) == oscars["decade"].to_numpy()).all()


def test_honorary_flag_follows_original_category_not_just_canon() -> None:
    raw = pd.DataFrame(
        {
            "year_film": [1950],
            "year_ceremony": [1951],
            "ceremony": [23],
            "category": ["HONORARY FOREIGN LANGUAGE FILM AWARD"],
            "canon_category": ["INTERNATIONAL FEATURE FILM"],
            "name": [pd.NA],
            "film": ["Rashomon"],
            "winner": [True],
        }
    )
    cleaned = clean(raw)
    assert bool(cleaned.loc[0, "is_honorary"]) is True
    assert cleaned.loc[0, "category_canon"] == "INTERNATIONAL FEATURE FILM"


def test_clean_strips_text_and_coerces_winner() -> None:
    raw = pd.DataFrame(
        {
            "year_film": [1997],
            "year_ceremony": ["1998"],
            "ceremony": [70],
            "category": ["  Best Picture  "],
            "name": ["  James Cameron  "],
            "film": [" Titanic "],
            "winner": ["True"],
        }
    )
    cleaned = clean(raw)
    assert cleaned.loc[0, "category"] == "BEST PICTURE"
    assert cleaned.loc[0, "name"] == "James Cameron"
    assert cleaned.loc[0, "film"] == "Titanic"
    assert bool(cleaned.loc[0, "winner"]) is True
    assert bool(cleaned.loc[0, "is_best_picture"]) is True
