"""Normalização de categorias históricas do Oscar."""

from __future__ import annotations

import numpy as np
import pandas as pd

BEST_PICTURE_CANON = "BEST PICTURE"

BEST_PICTURE_ALIASES = {
    "OUTSTANDING PICTURE": BEST_PICTURE_CANON,
    "OUTSTANDING PRODUCTION": BEST_PICTURE_CANON,
    "OUTSTANDING MOTION PICTURE": BEST_PICTURE_CANON,
    "BEST MOTION PICTURE": BEST_PICTURE_CANON,
    "BEST PICTURE": BEST_PICTURE_CANON,
}

ACTOR_LEADING_CANON = "ACTOR IN A LEADING ROLE"
ACTRESS_LEADING_CANON = "ACTRESS IN A LEADING ROLE"
ACTOR_SUPPORTING_CANON = "ACTOR IN A SUPPORTING ROLE"
ACTRESS_SUPPORTING_CANON = "ACTRESS IN A SUPPORTING ROLE"

ACTING_LEADING_ALIASES = {
    "ACTOR": ACTOR_LEADING_CANON,
    "ACTRESS": ACTRESS_LEADING_CANON,
}

CATEGORY_ALIASES = {**BEST_PICTURE_ALIASES, **ACTING_LEADING_ALIASES}

ACTING_CATEGORIES = (
    ACTOR_LEADING_CANON,
    ACTRESS_LEADING_CANON,
    ACTOR_SUPPORTING_CANON,
    ACTRESS_SUPPORTING_CANON,
)

LEADING_ACTING_CATEGORIES = frozenset({ACTOR_LEADING_CANON, ACTRESS_LEADING_CANON})
SUPPORTING_ACTING_CATEGORIES = frozenset(
    {ACTOR_SUPPORTING_CANON, ACTRESS_SUPPORTING_CANON}
)

HONORARY_MARKERS = (
    "HONORARY",
    "JEAN HERSHOLT",
    "IRVING G. THALBERG",
    "GORDON E. SAWYER",
    "AWARD OF COMMENDATION",
    "SPECIAL AWARD",
    "SPECIAL ACHIEVEMENT",
    "SPECIAL FOREIGN LANGUAGE",
)

COUNTRY_AWARD_MARKERS = (
    "INTERNATIONAL FEATURE FILM",
    "FOREIGN LANGUAGE FILM",
    "INTERNATIONAL FILM",
)


def strip_text(values: pd.Series) -> pd.Series:
    """Remove espaços extras e trata string vazia como ausente, preservando a caixa."""
    cleaned = values.astype("string").str.replace(r"\s+", " ", regex=True).str.strip()
    return cleaned.replace("", pd.NA)


def normalize_label(values: pd.Series) -> pd.Series:
    """Versão em caixa alta de `strip_text`, usada em nomes de categoria."""
    return strip_text(values).str.upper()


def canonicalize_category(category: pd.Series) -> pd.Series:
    """Unifica aliases históricos: Melhor Filme e atuação principal (ACTOR/ACTRESS)."""
    return normalize_label(category).replace(CATEGORY_ALIASES)


def is_best_picture_category(category_canon: pd.Series) -> pd.Series:
    return category_canon.eq(BEST_PICTURE_CANON).fillna(False)


def _contains_any(labels: pd.Series, markers: tuple[str, ...]) -> pd.Series:
    text = labels.fillna("").astype(str)
    mask = pd.Series(False, index=labels.index)
    for marker in markers:
        mask = mask | text.str.contains(marker, regex=False)
    return mask


def is_honorary_category(category: pd.Series) -> pd.Series:
    return _contains_any(category, HONORARY_MARKERS)


def is_country_award_category(category_canon: pd.Series) -> pd.Series:
    """FOREIGN / INTERNATIONAL: o campo `name` costuma ser o país, não a pessoa."""
    return _contains_any(category_canon, COUNTRY_AWARD_MARKERS)


def is_acting_category(category_canon: pd.Series) -> pd.Series:
    """Quatro categorias competitivas de atuação (principal e coadjuvante)."""
    return category_canon.isin(ACTING_CATEGORIES).fillna(False)


def is_leading_acting_category(category_canon: pd.Series) -> pd.Series:
    return category_canon.isin(LEADING_ACTING_CATEGORIES).fillna(False)


def is_supporting_acting_category(category_canon: pd.Series) -> pd.Series:
    return category_canon.isin(SUPPORTING_ACTING_CATEGORIES).fillna(False)


def decade(year_ceremony: np.ndarray | pd.Series) -> np.ndarray:
    """Anos de cerimônia → década (1920, 1930, …) via NumPy."""
    years = np.asarray(year_ceremony, dtype=np.int64)
    return (years // 10) * 10
