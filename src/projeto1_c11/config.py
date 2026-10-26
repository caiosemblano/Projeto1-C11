"""Caminhos e parâmetros globais da análise."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CACHE_CSV = RAW_DATA_DIR / "the_oscar_award.csv"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

KAGGLE_DATASET = "unanimad/the-oscar-award"
KAGGLE_FILE = "the_oscar_award.csv"

FILM_KEY = ("film", "year_ceremony")

MIN_NOMINATIONS = 5
TOP_N = 15
MIN_CATEGORY_WINS = 8
ROLLING_WINDOW = 5
RANDOM_SEED = 42
FIGURE_DPI = 150
