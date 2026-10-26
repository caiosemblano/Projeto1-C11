"""Carga, cache e limpeza do dataset The Oscar Award."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from projeto1_c11.categories import (
    canonicalize_category,
    decade,
    is_best_picture_category,
    is_honorary_category,
    normalize_label,
    strip_text,
)
from projeto1_c11.config import CACHE_CSV, KAGGLE_DATASET, KAGGLE_FILE, RAW_DATA_DIR

REQUIRED_COLUMNS = (
    "year_film",
    "year_ceremony",
    "ceremony",
    "category",
    "name",
    "film",
    "winner",
)


def load_raw(*, force: bool = False) -> pd.DataFrame:
    """Lê o CSV em cache ou baixa `the_oscar_award.csv` via KaggleHub."""
    if CACHE_CSV.exists() and not force:
        return pd.read_csv(CACHE_CSV)

    import kagglehub

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    downloaded = Path(kagglehub.dataset_download(KAGGLE_DATASET, path=KAGGLE_FILE))
    source = downloaded if downloaded.is_file() else downloaded / KAGGLE_FILE
    frame = pd.read_csv(source)
    frame.to_csv(CACHE_CSV, index=False)
    return frame


def coerce_winner(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.astype(bool)
    lowered = series.astype("string").str.strip().str.lower()
    return lowered.isin(["true", "1", "yes", "t"]).fillna(False).astype(bool)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Colunas ausentes no dataset: {missing}")

    out = df.copy()
    out["year_film"] = pd.to_numeric(out["year_film"], errors="coerce")
    out["year_ceremony"] = pd.to_numeric(out["year_ceremony"], errors="coerce")
    out["ceremony"] = pd.to_numeric(out["ceremony"], errors="coerce")
    out = out.dropna(subset=["year_ceremony", "category"])
    out["year_ceremony"] = out["year_ceremony"].astype("int64")

    out["category"] = normalize_label(out["category"])
    out["name"] = strip_text(out["name"])
    out["film"] = strip_text(out["film"])
    out = out.dropna(subset=["category"])

    source = out["canon_category"] if "canon_category" in out.columns else out["category"]
    out["category_canon"] = canonicalize_category(source)
    out["is_best_picture"] = is_best_picture_category(out["category_canon"])
    # canon_category às vezes mapeia honorários antigos para categorias competitivas.
    out["is_honorary"] = is_honorary_category(out["category"]) | is_honorary_category(
        out["category_canon"]
    )
    out["decade"] = decade(out["year_ceremony"].to_numpy())
    out["winner"] = coerce_winner(out["winner"])
    return out.reset_index(drop=True)


def competitive(df: pd.DataFrame) -> pd.DataFrame:
    """Indicações competitivas (exclui honorários/especiais)."""
    return df.loc[~df["is_honorary"]].copy()


def load_oscars(*, force: bool = False) -> pd.DataFrame:
    return clean(load_raw(force=force))
