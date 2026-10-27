"""Análise das 10 perguntas sobre o Oscar."""

from __future__ import annotations


def main() -> None:
    """Carrega o dataset, responde Q1–Q10 e grava as figuras."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from projeto1_c11.data import load_oscars
    from projeto1_c11.plotting import apply_style, save_fig
    from projeto1_c11.questions import QUESTIONS

    apply_style()
    frame = load_oscars()
    for question in QUESTIONS:
        result = question.compute(frame)
        fig = question.plot(result)
        path = save_fig(fig, question.SLUG)
        plt.close(fig)
        print(f"{question.SLUG}: {path}")
