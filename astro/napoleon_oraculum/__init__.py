from .data import answers, get_oraculum_answer, oraculum, question_pairs, questions, questions_zh


def render_streamlit():
    """Lazy-load renderer implementation and return latest Oraculum payload."""
    from .renderer import render_streamlit as _render_streamlit

    return _render_streamlit()

__all__ = [
    "answers",
    "get_oraculum_answer",
    "oraculum",
    "question_pairs",
    "questions",
    "questions_zh",
    "render_streamlit",
]
