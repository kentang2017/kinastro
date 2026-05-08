"""Registry-driven sidebar system selector component."""

from __future__ import annotations

from typing import Callable

from ui.state import SessionKeys


def render_system_selector(
    *,
    st_module,
    t: Callable[[str], str],
    search_query: str,
    current_system: str | None,
    lang: str,
) -> str | None:
    """Render categorized system selector from `astro.system_registry`.

    Args:
        st_module: Streamlit module (`streamlit as st`).
        t: i18n translate function.
        search_query: User input in search box.
        current_system: Current selected system id.
        lang: Current language code.

    Returns:
        Selected system id (or existing one if unchanged).
    """

    from astro.system_registry import list_categories, get_systems_by_category, CATEGORY_ICONS

    selected_system = current_system
    query = (search_query or "").strip().lower()
    beginner_systems = {"tab_western", "tab_ziwei"}

    for category in list_categories():
        systems = get_systems_by_category(category)
        if query:
            filtered = []
            for sys in systems:
                tab_label = t(sys.tab_key)
                hint_label = t(sys.hint_key)
                if query in tab_label.lower() or query in hint_label.lower() or query in sys.name_en.lower() or query in sys.name_zh.lower():
                    filtered.append(sys)
            if not filtered:
                continue
        else:
            filtered = systems

        cat_has_active = selected_system is not None and any(s.id == selected_system for s in filtered)
        cat_label = f"{CATEGORY_ICONS.get(category, '📌')} {t(category)}"

        with st_module.expander(cat_label, expanded=cat_has_active or bool(query)):
            col_a, col_b = st_module.columns(2, gap="small")
            for idx, sys in enumerate(filtered):
                is_active = sys.id == selected_system
                beginner = (
                    "🌟 推薦入門"
                    if lang in ("zh", "zh_cn")
                    else "🌟 Start here"
                ) if sys.id in beginner_systems else ""
                badge_html = (
                    f'<div class="ka-system-card-badge">{beginner}</div>'
                    if beginner
                    else ""
                )
                card_html = (
                    '<div class="ka-system-card" '
                    f'style="--ka-system-accent:{sys.accent_color};">'
                    f'<div class="ka-system-card-title">{t(sys.tab_key)}</div>'
                    f"{badge_html}"
                    "</div>"
                )
                with (col_a if idx % 2 == 0 else col_b):
                    st_module.markdown(card_html, unsafe_allow_html=True)
                    if is_active:
                        if st_module.button(
                            "✨ " + t("generate_chart_btn"),
                            key=f"_sys_btn_{sys.id}",
                            width="stretch",
                            type="primary",
                            help=t(sys.hint_key),
                        ):
                            selected_system = sys.id
                            st_module.session_state[SessionKeys.SYSTEM_SELECT] = selected_system
                            st_module.rerun()
                    else:
                        if st_module.button(
                            t(sys.tab_key),
                            key=f"_sys_btn_{sys.id}",
                            width="stretch",
                            type="secondary",
                            help=t(sys.hint_key),
                        ):
                            selected_system = sys.id
                            st_module.session_state[SessionKeys.SYSTEM_SELECT] = selected_system
                            st_module.rerun()

    return selected_system
