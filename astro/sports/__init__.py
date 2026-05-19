"""KinAstro Sports Astrology public API."""

from __future__ import annotations

from .models import MatchInput, PredictionResult, SportsPrediction, TeamProfile


def analyze_sports_horary(*args, **kwargs):
    """Lazy-load sports horary analyzer."""
    from .sports_horary import analyze_sports_horary as _fn

    return _fn(*args, **kwargs)


def analyze_event_chart_with_team_natal(*args, **kwargs):
    """Lazy-load event + team natal dashboard analyzer."""
    from .sports_horary import analyze_event_chart_with_team_natal as _fn

    return _fn(*args, **kwargs)


def render_streamlit(*args, **kwargs):
    """Lazy-load Streamlit renderer."""
    from .renderer import render_streamlit as _fn

    return _fn(*args, **kwargs)


def predict_match(*args, **kwargs):
    """Lazy-load legacy prediction engine."""
    from .prediction_engine import predict_match as _fn

    return _fn(*args, **kwargs)


__all__ = [
    "MatchInput",
    "PredictionResult",
    "SportsPrediction",
    "TeamProfile",
    "analyze_sports_horary",
    "analyze_event_chart_with_team_natal",
    "render_streamlit",
    "predict_match",
]
