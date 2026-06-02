"""
astro/shaozi/renderer.py — 邵子神數渲染器

邵子神數 SVG/HTML 渲染器，用於在 Streamlit 中顯示邵子神數推算結果。
"""

from typing import Any, Dict
import streamlit as st


def render_shaozi_placeholder() -> None:
    """顯示邵子神數的占位符提示訊息。"""
    st.info("請先填寫出生資料並點擊「起盤」按鈕來計算邵子神數推算結果。")


def render_shaozi_result(result) -> None:
    """
    渲染邵子神數的主推算結果。

    Args:
        result: ShaoziResult 物件，包含邵子神數的計算結果。
    """
    st.success("邵子神數計算完成！")

    # 基本資訊
    with st.expander("📅 基本資訊", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("年柱", result.year_gz)
            st.metric("日柱", result.day_gz)
        with col2:
            st.metric("月柱", result.month_gz)
            st.metric("時柱", result.hour_gz)

    # 起數結果
    with st.expander("🔢 起數結果", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("集號（年）", result.year_digit)
            st.metric("月位", result.month_digit)
        with col2:
            st.metric("日位", result.day_digit)
            st.metric("時位", result.hour_digit)

    # 條文資訊
    with st.expander("📜 條文資訊", expanded=True):
        st.subheader(f"{result.gua_name} - {result.tiaowen_id}")
        st.text_area(
            "條文內容",
            result.tiaowen_text,
            height=200,
            disabled=True,
            label_visibility="collapsed",
        )

    # 河洛數與納音
    with st.expander("🌊 河洛數與納音", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("年河洛數", result.he_luo_year)
            st.metric("日河洛數", result.he_luo_day)
        with col2:
            st.metric("年納音", result.nayin_year)
            st.metric("日納音", result.nayin_day)

    # 配卦資訊
    with st.expander("괘 配卦資訊", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("卦年", result.gua_year)
            st.metric("卦月", result.gua_month)
        with col2:
            st.metric("卦日", result.gua_day)
            st.metric("卦時", result.gua_hour)


def render_shaozi_64key_section(full_result: Dict[str, Any]) -> None:
    """
    渲染邵子神數的64鑰匙進階細調結果。

    Args:
        full_result: ShaoziFullShenShu.cast_plate() 返回的字典。
    """
    st.success("64鑰匙細調計算完成！")

    base_num = full_result.get("base_number", 0)
    st.subheader(f"🔑 64鑰匙鑰匙號碼：{base_num:04d}")

    # 鑰匙名稱
    key_info = full_result.get("key", {})
    if key_info:
        st.caption(key_info.get("名稱", ""))

    # 詳細計算過程
    with st.expander("🔍 詳細計算過程", expanded=False):
        calc = full_result.get("calculation", {})
        for k, v in calc.items():
            st.write(f"{k}: {v}")

    # 完整條文
    tiaowen = full_result.get("tiaowen_text", "")
    with st.expander("📋 完整條文", expanded=True):
        st.text_area("條文內容", tiaowen, height=250, disabled=True)


def render_shaozi_tiaowen_browser() -> None:
    """
    渲染邵子神數條文資料庫瀏覽器。
    發現: 6144 條條文，按鑰匙號碼 1001-7144 編號。
    """
    st.header("📚 邵子神數條文庫")
    st.caption("完整條文資料庫，共 6144 條")

    # 搜尋欄位
    search_id = st.text_input(
        "🔍 按鑰匙號碼搜尋（例：1001）",
        placeholder="輸入 4 位數字鑰匙號碼",
        help="邵子神數條文按鑰匙號碼 1001-7144 編號",
    )

    if search_id:
        # 簡單實現：顯示提示
        st.info(
            f"此處應顯示鑰匙號碼 **{search_id}** 的條文內容\n\n"
            "完整條文瀏覽功能需整合資料庫檔案（shaozi_tiaowen_6144.json）"
        )
        st.code(
            "邵子神數條文結構：\n"
            f"- 鑰匙號碼：1001-7144\n"
            f"- 條文數量：6144 條\n"
            f"- 搜尋格式：4 位數字（例：1001）",
            language="text",
        )
