"""Tests for fixed-width sidebar layout markup."""

from __future__ import annotations

from astro.chart_theme import SIDEBAR_FIXED_WIDTH_PX, build_sidebar_fixed_layout_markup


def test_sidebar_fixed_width_constant():
    assert SIDEBAR_FIXED_WIDTH_PX == 400


def test_sidebar_layout_markup_contains_width_and_toggle_hooks():
    markup = build_sidebar_fixed_layout_markup(420)
    assert "--ka-sidebar-width: 420px" in markup
    assert 'aria-expanded="true"' in markup
    assert 'aria-expanded="false"' in markup
    assert "stSidebarCollapsedControl" not in markup  # native toggle untouched
    assert "translateX(-100%)" in markup
    assert "stSidebarResizeHandle" in markup