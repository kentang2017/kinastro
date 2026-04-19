"""
astro/chart_renderer_v2.py — Cultural SVG Chart Wrapper (v2)

Provides ``build_cultural_svg()`` which wraps any raw SVG string in a
culturally-themed container with CSS class, hover glow, and optional
slow-spin animation.  All culture-specific visual effects are driven by
the CSS classes defined in ``styles/custom.css`` and
``astro/chart_theme.py`` — this module only generates the HTML wrapper.
"""

from __future__ import annotations

from astro.icons import SYSTEM_CSS_CLASS

# ═══════════════════════════════════════════════════════════════
# Cultural SVG wrapper
# ═══════════════════════════════════════════════════════════════

def build_cultural_svg(
    svg_content: str,
    system_key: str,
    *,
    title: str = "",
    animate_spin: bool = False,
    extra_class: str = "",
) -> str:
    """Wrap *svg_content* in a themed ``<div>`` with culture CSS class.

    Parameters
    ----------
    svg_content : str
        Raw SVG markup (``<svg …>…</svg>``).
    system_key : str
        The system tab key, e.g. ``"tab_aztec"``.  Used to look up the
        CSS class from :data:`astro.icons.SYSTEM_CSS_CLASS`.
    title : str, optional
        Optional heading rendered above the chart.
    animate_spin : bool, optional
        If *True*, add the ``chart-slow-spin`` class for a gentle
        continuous rotation animation.
    extra_class : str, optional
        Additional CSS classes to append to the container.

    Returns
    -------
    str
        An HTML string safe for ``st.markdown(..., unsafe_allow_html=True)``.
    """
    culture_cls = SYSTEM_CSS_CLASS.get(system_key, "")
    spin_cls = " chart-slow-spin" if animate_spin else ""
    extra = f" {extra_class}" if extra_class else ""

    classes = f"chart-v2-container chart-glow-wrap{spin_cls} {culture_cls}{extra}".strip()

    parts: list[str] = []
    parts.append(f'<div class="{classes}">')
    if title:
        parts.append(f'<div class="chart-v2-title">{title}</div>')
    parts.append(svg_content)
    parts.append("</div>")
    return "\n".join(parts)


def build_culture_info_card(
    system_key: str,
    heading: str,
    body: str,
) -> str:
    """Return a small glassmorphism popup card with cultural styling.

    This is the 'click-to-reveal detail card' described in the UI spec.
    """
    culture_cls = SYSTEM_CSS_CLASS.get(system_key, "")
    return (
        f'<div class="culture-info-card {culture_cls}">'
        f'<h4>{heading}</h4>'
        f'<p>{body}</p>'
        f'</div>'
    )
