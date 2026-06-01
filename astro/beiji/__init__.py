# -*- coding: utf-8 -*-
"""
北極神數 (Beiji Shenshu) module.

宋代邵康節五大神數之一，以北斗七星（破軍星）為核心，
結合奇門九星、六十四卦、二十八宿，特色是「簡單、神奇、快而準」。
"""

from .calculator import (
    BeijiInput,
    BeijiResult,
    BeijiShenshu,
    QueryResult,
    TiaowenDatabase,
    compute_beiji,
    compute_ke,
    get_calculator,
    get_hour_branch,
    get_year_ganzhi,
)

def render_beiji_chart(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_beiji_chart renderer for this package."""
    from ui.handlers.tab_beiji.render import render_beiji_chart as _fn
    return _fn(*args, **kwargs)

def render_beiji_search(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_beiji_search renderer for this package."""
    from ui.handlers.tab_beiji.render import render_beiji_search as _fn
    return _fn(*args, **kwargs)

def render_streamlit(*args, **kwargs):  # type: ignore[no-redef]
    """Lazy-load the render_streamlit renderer for this package."""
    from ui.handlers.tab_beiji.render import render_streamlit as _fn
    return _fn(*args, **kwargs)

__all__ = [
    # 資料類別
    "BeijiInput",
    "BeijiResult",
    "BeijiShenshu",
    "QueryResult",
    "TiaowenDatabase",
    # 便捷函式
    "compute_beiji",
    "compute_ke",
    "get_calculator",
    "get_hour_branch",
    "get_year_ganzhi",
    # 渲染函式
    "render_beiji_chart",
    "render_beiji_search",
    "render_streamlit",
]
