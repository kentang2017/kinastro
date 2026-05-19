"""
kinastro_vs — 足球比賽占星預測工具
Football Match Astrology Prediction Tool

融合 John Frawley 的《Sports Astrology》(西洋卜卦占星)
與 Simon Chokoisky 的《Gambler's Dharma》(Vedic 吠陀占星)。
"""

__version__ = "0.1.0"


def render_streamlit(*args, **kwargs):
    """Lazy-load Streamlit renderer to keep package import lightweight."""
    from .renderer import render_streamlit as _fn
    return _fn(*args, **kwargs)


def analyze_sports_horary(*args, **kwargs):
    """Lazy-load core sports-horary analyzer."""
    from .sports_horary import analyze_sports_horary as _fn
    return _fn(*args, **kwargs)


__all__ = ["render_streamlit", "analyze_sports_horary", "__version__"]
