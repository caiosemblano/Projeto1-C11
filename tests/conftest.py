import matplotlib

matplotlib.use("Agg")

import pandas as pd
import pytest


def _row(
    year_film: int,
    year_ceremony: int,
    ceremony: int,
    category: str,
    name: str | None,
    film: str | None,
    winner: bool,
) -> dict[str, object]:
    return {
        "year_film": year_film,
        "year_ceremony": year_ceremony,
        "ceremony": ceremony,
        "category": category,
        "name": name,
        "film": film,
        "winner": winner,
    }


@pytest.fixture
def raw_oscars() -> pd.DataFrame:
    return pd.DataFrame(
        [
            _row(1949, 1950, 22, "OUTSTANDING PICTURE", "Producer A", "Champ", True),
            _row(1949, 1950, 22, "DIRECTING", "Director A", "Champ", True),
            _row(1949, 1950, 22, "ACTOR", "Actor A", "Champ", False),
            _row(1949, 1950, 22, "OUTSTANDING PICTURE", "Producer B", "Snub", False),
            _row(1949, 1950, 22, "DIRECTING", "Director B", "Snub", False),
            _row(1949, 1950, 22, "HONORARY AWARD", "Legend", None, True),
            _row(1949, 1950, 22, "SPECIAL EFFECTS", "FX Studio", "Snub", False),
            _row(2019, 2020, 92, "BEST PICTURE", "Producer C", "Champ", False),
            _row(2019, 2020, 92, "DIRECTING", "Director C", "Champ", True),
            _row(2019, 2020, 92, "FILM EDITING", "Editor C", "Champ", True),
            _row(2019, 2020, 92, "BEST PICTURE", "Producer D", "Sweep", True),
            _row(2019, 2020, 92, "FILM EDITING", "Editor E", "Indie", True),
            _row(2015, 2016, 88, "ACTOR", "Star", "One", True),
            _row(2016, 2017, 89, "ACTOR", "Star", "Two", False),
            _row(2017, 2018, 90, "ACTOR", "Star", "Three", False),
            _row(2018, 2019, 91, "ACTOR", "Star", "Four", False),
            _row(2021, 2022, 94, "ACTOR", "Star", "Five", True),
        ]
    )


@pytest.fixture
def oscars(raw_oscars: pd.DataFrame) -> pd.DataFrame:
    from projeto1_c11.data import clean

    return clean(raw_oscars)
