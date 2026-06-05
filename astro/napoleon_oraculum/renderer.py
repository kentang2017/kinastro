from __future__ import annotations

import random

import streamlit as st

from astro.napoleon_oraculum.data import get_oraculum_answer, question_pairs


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        .fate-hero {
            background: radial-gradient(circle at 20% 20%, rgba(250, 204, 21, 0.24), rgba(88, 28, 135, 0.24));
            border: 1px solid rgba(250, 204, 21, 0.35);
            border-left: 6px solid #facc15;
            border-radius: 12px;
            padding: 18px 20px;
            margin-bottom: 14px;
        }
        .fate-card {
            background: rgba(15, 23, 42, 0.65);
            border: 1px solid rgba(250, 204, 21, 0.25);
            border-radius: 12px;
            padding: 14px 16px;
            margin-top: 10px;
        }
        .fate-answer {
            font-size: 1.04rem;
            line-height: 1.7;
            color: #fef3c7;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_streamlit() -> dict[str, object]:
    """Render Napoleon's Book of Fate module and return payload for AI context."""
    _inject_styles()

    st.markdown(
        """
        <div class="fate-hero">
            <h3 style="margin:0;">👑 Napoleon’s Book of Fate · 拿破崙命運之書</h3>
            <p style="margin:6px 0 0 0; opacity:.9;">
                Select your question, invoke a sacred number, and reveal the Oraculum decree.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    question_indices = list(range(16))
    question_idx = st.selectbox(
        "問題 / Question",
        options=question_indices,
        format_func=lambda idx: f"{idx + 1}. {question_pairs[idx]['en']}｜{question_pairs[idx]['zh']}",
        key="napoleon_oraculum_question",
    )

    mode_col, number_col = st.columns([5, 6])
    with mode_col:
        mode = st.radio(
            "取數方式 / Number",
            ["manual", "random"],
            format_func=lambda x: "手動選數" if x == "manual" else "儀式隨機",
            horizontal=True,
            key="napoleon_oraculum_mode",
        )

    if mode == "manual":
        with number_col:
            number = st.select_slider(
                "數字（1-16）",
                options=list(range(1, 17)),
                value=st.session_state.get("napoleon_oraculum_number", 8),
                key="napoleon_oraculum_number_slider",
            )
        st.session_state["napoleon_oraculum_number"] = number
    else:
        if "napoleon_oraculum_number" not in st.session_state:
            st.session_state["napoleon_oraculum_number"] = 8
        with number_col:
            st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
            if st.button("🎲 擲命運之數 / Cast", key="napoleon_oraculum_cast", width="stretch"):
                st.session_state["napoleon_oraculum_number"] = random.randint(1, 16)
        number = st.session_state["napoleon_oraculum_number"]

    st.info(f"Question #{question_idx + 1} · Number {number}")

    reveal_clicked = st.button("🔓 揭示神諭 / Reveal", key="napoleon_oraculum_reveal", width="stretch")

    payload: dict[str, object] = {}
    if reveal_clicked:
        result = get_oraculum_answer(question_idx, number - 1)
        payload = result
        st.markdown('<div class="fate-card">', unsafe_allow_html=True)
        st.markdown(f"**Letter / 命符**: `{result['letter']}`")
        st.markdown(f"**Question / 問題**: {result['question_en']}\n\n{result['question_zh']}")
        st.markdown(f"<div class='fate-answer'>{result['answer']}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("Oraculum Mapping / 對照表預覽", expanded=False):
        from astro.napoleon_oraculum.data import oraculum

        row = oraculum[question_idx]
        st.write({str(i + 1): row[i] for i in range(16)})

    return payload
