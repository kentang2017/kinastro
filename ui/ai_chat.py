"""Global AI chat panel for KinAstro.

Provides:
- ``set_ai_context(system_key, chart_obj, page_content)`` – stores chart
  context in ``st.session_state`` so the fixed-bottom chat can use it.
- ``render_global_ai_chat()`` – renders the fixed-bottom AI chat panel.
"""

from __future__ import annotations

import os

import streamlit as st

from astro.ai_analysis import (
    CerebrasClient,
    OpenAIClient,
    CustomProviderClient,
    RateLimitError,
    CEREBRAS_MODEL_OPTIONS,
    CEREBRAS_MODEL_DESCRIPTIONS,
    DEFAULT_SYSTEM_PROMPT,
    DEFAULT_SYSTEM_PROMPT_EN,
    detect_language,
    format_chart_for_prompt,
)
from ui.helpers import t


def set_ai_context(system_key: str, chart_obj, page_content: str = "") -> None:
    """Store chart data for the global fixed AI chat panel.

    Parameters
    ----------
    system_key : str
        The system tab key (e.g. ``"tab_western"``).
    chart_obj : object
        The chart object produced by the compute function.
    page_content : str
        Optional extra text content rendered on the page.
    """
    st.session_state["_global_chat_system"] = system_key
    st.session_state["_global_chat_chart"] = chart_obj
    st.session_state["_global_chat_page_content"] = page_content


# Backward-compatible aliases used by legacy handler code
render_ai_button = set_ai_context
_render_ai_button = set_ai_context
_render_ai_chat = set_ai_context


def render_global_ai_chat() -> None:
    """Render the fixed-bottom AI chat panel using stored chart context."""
    _system_key = st.session_state.get("_global_chat_system", "")
    _chart_obj = st.session_state.get("_global_chat_chart")
    _page_content = st.session_state.get("_global_chat_page_content", "")

    if not _system_key:
        _system_key = st.session_state.get("_system_select", "")

    if not _system_key:
        return

    _user_avatar = "👦" if st.session_state.get("_calc_gender") == "male" else "👧"
    _ck = f"_ai_chat_global_{_system_key}"

    if _ck not in st.session_state:
        st.session_state[_ck] = []

    st.divider()

    st.markdown('<div class="ai-chat-fixed-panel">', unsafe_allow_html=True)
    st.markdown(
        f'<div class="ai-chat-header">{t("ai_chat_header")}</div>',
        unsafe_allow_html=True,
    )

    _clear_key = f"{_ck}_clear"
    if st.button(t("ai_chat_clear"), key=_clear_key, type="secondary"):
        st.session_state[_ck] = []
        st.rerun()

    _chat_box = st.container(height=400)
    _history = st.session_state[_ck]

    if not _history:
        with _chat_box.chat_message("assistant", avatar="🧙"):
            st.markdown(t("ai_chat_welcome"))

    for _msg in _history:
        with _chat_box.chat_message(_msg["role"], avatar="🧙" if _msg["role"] == "assistant" else _user_avatar):
            st.markdown(_msg["content"])

    _input_key = f"{_ck}_input"
    _user_input = st.chat_input(t("ai_chat_placeholder"), key=_input_key)

    st.markdown('</div>', unsafe_allow_html=True)

    if _user_input:
        _history.append({"role": "user", "content": _user_input})
        with _chat_box.chat_message("user", avatar=_user_avatar):
            st.markdown(_user_input)

        _provider = st.session_state.get("_ai_provider", "cerebras")

        if _provider == "openai":
            _api_key = st.session_state.get("_ai_openai_key", "").strip()
            if not _api_key:
                st.error(t("ai_openai_key_missing"))
                return
        elif _provider == "custom":
            _api_key = st.session_state.get("_ai_custom_key", "").strip()
            if not _api_key:
                st.error(t("ai_custom_key_missing"))
                return
            _custom_host = st.session_state.get("_ai_custom_host", "").strip().rstrip("/")
            if not _custom_host:
                st.error(t("ai_custom_host_missing"))
                return
            _custom_base_url = _custom_host
            if not st.session_state.get("_ai_custom_models"):
                st.error(t("ai_custom_model_missing"))
                return
        else:
            _api_key = ""
            try:
                _api_key = st.secrets.get("CEREBRAS_API_KEY", "")
            except (FileNotFoundError, KeyError, AttributeError):
                pass
            if not _api_key:
                _api_key = os.environ.get("CEREBRAS_API_KEY", "")
            if not _api_key:
                st.error(t("ai_key_missing"))
                return

        if _chart_obj is not None:
            chart_prompt = format_chart_for_prompt(
                _system_key, _chart_obj, page_content=_page_content,
            )
        else:
            chart_prompt = t("ai_no_chart")

        _user_lang = detect_language(_user_input)
        if _user_lang == "en":
            _sys_prompt = DEFAULT_SYSTEM_PROMPT_EN
        else:
            _sys_prompt = st.session_state.get("ai_system_prompt", DEFAULT_SYSTEM_PROMPT)

        _api_messages = [
            {"role": "system", "content": _sys_prompt},
            {"role": "user", "content": chart_prompt},
            {"role": "assistant", "content": t("ai_chat_welcome")},
        ]
        for _msg in _history:
            _api_messages.append({"role": _msg["role"], "content": _msg["content"]})

        with _chat_box.chat_message("assistant", avatar="🧙"):
            with st.spinner(t("ai_analyzing")):
                try:
                    if _provider == "openai":
                        client = OpenAIClient(api_key=_api_key)
                    elif _provider == "custom":
                        client = CustomProviderClient(api_key=_api_key, base_url=_custom_base_url)
                    else:
                        client = CerebrasClient(api_key=_api_key)
                    result = client.chat(
                        messages=_api_messages,
                        model=st.session_state.get("_ai_model_select", CEREBRAS_MODEL_OPTIONS[0]),
                        max_tokens=st.session_state.get("_ai_max_tokens", 8192),
                        temperature=st.session_state.get("_ai_temperature", 0.7),
                    )
                    st.markdown(result)
                    _history.append({"role": "assistant", "content": result})
                except RateLimitError:
                    st.warning(t("ai_rate_limit"))
                except Exception as e:
                    st.error(t("ai_error").format(str(e)))

        st.session_state[_ck] = _history
