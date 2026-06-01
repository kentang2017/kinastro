"""
astro/medical_astrology — 醫學占星 / Iatromathematics

Classical Medical Astrology module combining:
- Zodiac Man (Homo Signorum) body-part correspondences
- Humoral theory (four humors / four temperaments)
- Egyptian Decan body-zone mapping
- Planetary hour electional rules for medical procedures
- Critical-day (crisis period) analysis for acute illness

Sources:
- Hippocrates, "Airs, Waters, Places"
- Galen, "On the Usefulness of the Parts"
- Ptolemy, "Tetrabiblos" Book III
- Avicenna, "Canon of Medicine" (Kitāb al-Qānūn fī al-Ṭibb)
- Picatrix (Ghāyat al-Ḥakīm)
- Medieval "Zodiac Man" manuscripts (Très Riches Heures du Duc de Berry)
- William Culpeper, "Astrological Judgement of Diseases"
"""

from .calculator import compute_medical_chart, MedicalChart

def render_streamlit(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_streamlit renderer for this package."""
    from ui.handlers.tab_medical_astrology.render import render_streamlit as _fn
    return _fn(*args, **kwargs)

__all__ = ["compute_medical_chart", "MedicalChart", "render_streamlit"]
