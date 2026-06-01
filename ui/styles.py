"""Styling utilities for KinAstro.

Provides CSS injection helpers and star-particle background animation.
All functions in this module interact with Streamlit's rendering pipeline.
"""

from __future__ import annotations

import os
import random

import streamlit as st

from astro.chart_theme import MOBILE_CSS


@st.cache_data(show_spinner=False)
def _load_custom_css() -> str:
    """Load custom.css from disk (cached so the file is only read once)."""
    _css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "custom.css")
    if os.path.exists(_css_path):
        with open(_css_path, "r", encoding="utf-8") as _f:
            return _f.read()
    return ""


def inject_custom_css() -> None:
    """Inject all custom CSS (mobile + custom.css) into the page."""
    st.markdown(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Cinzel:wght@400;600;700;900'
        '&family=Noto+Serif+TC:wght@300;400;700;900'
        '&family=Space+Grotesk:wght@300;400;500;600;700'
        '&family=Noto+Sans+TC:wght@300;400;500;700'
        '&family=Inter:wght@300;400;500;600'
        '&display=swap" rel="stylesheet">',
        unsafe_allow_html=True,
    )
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
    _custom = _load_custom_css()
    if _custom:
        st.markdown(f"<style>{_custom}</style>", unsafe_allow_html=True)

    _theme = st.session_state.get("_ka_theme", "modern")
    _valid_themes = {"modern", "classic", "mystic"}
    if _theme not in _valid_themes:
        _theme = "modern"
    st.markdown(
        f"""<script>
        (function() {{
            var app = window.parent.document.querySelector('.stApp');
            if (app) app.setAttribute('data-ka-theme', '{_theme}');
        }})();
        </script>""",
        unsafe_allow_html=True,
    )


def _build_star_particles_html() -> str:
    """Build CSS-based star particle background HTML (60 particles)."""
    parts = []
    for _ in range(60):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        dur = random.uniform(2.5, 6.0)
        delay = random.uniform(0, 5.0)
        opacity = random.uniform(0.3, 0.8)
        size = random.choices([1, 2, 3], weights=[1, 2, 1], k=1)[0]
        color = random.choices(["#EAB308", "#A78BFA", "#E0E0FF"], weights=[3, 1, 1], k=1)[0]
        parts.append(
            f'<div class="particle" style="'
            f"left:{x:.1f}%;top:{y:.1f}%;"
            f"width:{size}px;height:{size}px;"
            f"background:{color};"
            f"--duration:{dur:.1f}s;--delay:{delay:.1f}s;"
            f'--max-opacity:{opacity:.2f};"></div>'
        )
    return '<div class="star-particles">' + "".join(parts) + "</div>"


def inject_star_particles() -> None:
    """Inject CSS-based star particle background (cached per session)."""
    if not st.session_state.get("_star_particles", True):
        return
    if "_star_particles_html" not in st.session_state:
        st.session_state["_star_particles_html"] = _build_star_particles_html()
    st.markdown(st.session_state["_star_particles_html"], unsafe_allow_html=True)
