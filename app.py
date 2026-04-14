"""
堅占星 (Kin Astro) - 多體系占星排盤系統
Multi-System Astrology Chart Application

支援七政四餘（中國）、紫微斗數、西洋占星、印度占星（Jyotish）、宿曜道、泰國占星、
卡巴拉占星、阿拉伯占星（含 Picatrix 星體魔法、太陽知識大全 Shams al-Maʻārif）、
瑪雅占星、緬甸占星（Mahabote）、古埃及十度區間（Decans）、
納迪占星（Nadi Jyotish）、蒙古祖爾海（Zurkhai）、希臘占星（Hellenistic）
共十四種體系，使用 pyswisseph 進行天文計算。
"""

import os
import streamlit as st
from datetime import datetime, date, time

from astro.i18n import TRANSLATIONS, get_lang
from astro.chart_theme import MOBILE_CSS
from astro.qizheng.calculator import compute_chart
from astro.qizheng.chart_renderer import (
    render_chart_info,
    render_planet_table,
    render_house_table,
    render_aspect_summary,
    render_mansion_ring,
    render_bazi,
    render_shensha,
    render_dasha,
    render_transit_comparison,
    render_zhangguo,
)
from astro.qizheng.shensha import compute_shensha
from astro.qizheng.qizheng_dasha import compute_dasha
from astro.qizheng.qizheng_transit import compute_transit, compute_transit_now
from astro.qizheng.zhangguo import compute_zhangguo
from astro.qizheng.qizheng_electional import render_electional_tool
from astro.western.western import compute_western_chart, render_western_chart
from astro.western.western_transit import compute_western_transits
from astro.western.western_return import compute_solar_return
from astro.western.western_synastry import compute_synastry
from astro.vedic.indian import compute_vedic_chart, render_vedic_chart
from astro.vedic.vedic_dasha import compute_vimshottari, compute_yogini
from astro.vedic.ashtakavarga import compute_ashtakavarga
from astro.vedic.vedic_yogas import compute_yogas
from astro.vedic.bphs_engine import compute_bphs
from astro.sukkayodo import render_sukkayodo_chart
from astro.thai import (
    compute_thai_chart, render_thai_chart,
    calculate_thai_nine_grid, render_nine_grid,
    calculate_nine_palace_divination, render_nine_palace_divination,
)
from astro.kabbalistic import compute_kabbalistic_chart, render_kabbalistic_chart
from astro.arabic.arabic import compute_arabic_chart, render_arabic_chart
from astro.maya import compute_maya_chart, render_maya_chart
from astro.ziwei import compute_ziwei_chart, render_ziwei_chart
from astro.mahabote import compute_mahabote_chart, render_mahabote_chart
from astro.egyptian.decans import compute_decan_chart, render_decan_chart, render_decan_browse
from astro.vedic.nadi import compute_nadi_chart, render_nadi_chart
from astro.zurkhai import compute_zurkhai_chart, render_zurkhai_chart
from astro.western.hellenistic import compute_hellenistic_chart, render_hellenistic_chart, build_greek_horoscope_svg
from astro.western.ptolemy_dignities import PtolemyDignityCalculator, Planet as PtolPlanet, DignityType, dignity_to_chinese, SIGN_NAMES
from astro.western.fixed_stars import compute_fixed_star_positions, find_conjunctions
from astro.western.asteroids import compute_asteroids
from astro.export import render_download_buttons, western_chart_to_dict, vedic_chart_to_dict, chinese_chart_to_dict
from astro.natal_summary import generate_natal_summary
from astro.interpretations import (
    get_transit_reading, get_synastry_reading, get_dasha_reading,
    get_yogini_reading, get_qizheng_dasha_reading,
)
from astro.ai_analysis import (
    CerebrasClient,
    RateLimitError,
    CEREBRAS_MODEL_OPTIONS,
    CEREBRAS_MODEL_DESCRIPTIONS,
    load_system_prompts,
    save_system_prompts,
    format_chart_for_prompt,
)

from astro.arabic.picatrix_mansions import (
    render_mansion_lookup,
    render_planetary_hours_tool,
    render_talisman_generator,
    render_picatrix_browse,
    get_mansion_index,
    compute_moon_longitude,
)
from astro.arabic.shams_maarif import render_shams_browse, render_shams_chart
from astro.chinstar.chinstar import WanHuaXianQin


# ============================================================
# 頁面設定
# ============================================================
st.set_page_config(
    page_title="堅占星 Kin Astro",
    page_icon="⭐",
    layout="wide",
)

# ── Mobile-responsive CSS ──────────────────────────────────────
st.markdown(MOBILE_CSS, unsafe_allow_html=True)

# ── Initialise language from the persisted radio widget value ────────────────
# When the user clicks the language radio, Streamlit reruns the script with the
# new "_lang_radio" value already in session_state.  We read it here — before
# rendering the title — so that *all* content on the page uses the correct
# language in the same rerun.
if "_lang_radio" in st.session_state:
    st.session_state["lang"] = (
        "en" if st.session_state["_lang_radio"] == "English" else "zh"
    )
elif "lang" not in st.session_state:
    st.session_state["lang"] = "zh"


def t(key: str) -> str:
    """Return the translated string for *key* in the current UI language."""
    lang = st.session_state.get("lang", "zh")
    entry = TRANSLATIONS.get(key)
    if entry is None:
        return key
    return entry.get(lang, entry.get("zh", key))


def _render_reference_library():
    """Render the Arabic astrology reference library sub-tab content."""
    import os
    _ref_dir = os.path.join(os.path.dirname(__file__), "astro", "reference")
    _ref_files = [
        ("astrology_fortune.md", "占星與財富 / Astrology & Fortune"),
        ("astrology_magic.md", "占星魔法 / Astrological Magic"),
        ("astrology_military.md", "軍事占星 / Military Astrology"),
    ]
    for _fname, _title in _ref_files:
        _fpath = os.path.join(_ref_dir, _fname)
        if os.path.exists(_fpath):
            with open(_fpath, "r", encoding="utf-8") as _f:
                _content = _f.read()
            with st.expander(_title, expanded=False):
                st.markdown(_content)


def _render_bphs_result(bphs_result):
    """Render BPHS interpretation result in Streamlit."""
    import pandas as pd

    # ── 1. 行星品位 (Dignity) ──
    st.markdown("### 🏅 行星品位 (Graha Dignity)")
    st.caption("根據 BPHS 第5章：行星高低點與基本三角")
    _dignity_rows = []
    for d in bphs_result.dignities:
        status_icon = ""
        if d.uccha:
            status_icon = "⬆️"
        elif d.neecha:
            status_icon = "⬇️"
        elif d.moola_trikona:
            status_icon = "🔺"
        elif d.own_sign:
            status_icon = "🏠"
        _dignity_rows.append({
            "": status_icon,
            "行星": f"{d.planet_zh} ({d.planet})",
            "星座": f"{d.rashi_zh} ({d.rashi_en})",
            "品位": d.status_zh,
        })
    if _dignity_rows:
        st.dataframe(pd.DataFrame(_dignity_rows), hide_index=True, use_container_width=True)

    st.divider()

    # ── 2. 行星友敵關係 (Graha Maitri) ──
    st.markdown("### 🤝 行星友敵關係 (Graha Maitri)")
    st.caption("根據 BPHS 第6章：行星友敵關係")
    _maitri_rows = []
    for m in bphs_result.graha_maitri:
        _maitri_rows.append({
            "行星": f"{m.planet_zh} ({m.planet})",
            "友星 ✅": m.friends_zh,
            "中性 ⚖️": m.neutral_zh,
            "敵星 ❌": m.enemies_zh,
        })
    if _maitri_rows:
        st.dataframe(pd.DataFrame(_maitri_rows), hide_index=True, use_container_width=True)

    st.divider()

    # ── 3. 行星阿瓦斯塔 (Graha Avastha) ──
    st.markdown("### 🎭 行星阿瓦斯塔 (Graha Avastha)")
    st.caption("根據 BPHS 第15章：行星狀態章 — 12種阿瓦斯塔決定行星實際表現")
    for av in bphs_result.avasthas:
        strength_icon = {"強": "💪", "中": "⚖️", "弱": "⚠️"}.get(av.strength, "❓")
        with st.expander(f"{strength_icon} {av.planet_zh} ({av.planet}) — {av.avastha_name} [{av.strength}]"):
            st.markdown(f"**狀態 (Avastha):** {av.avastha_name}")
            st.markdown(f"**強度:** {av.strength}")
            st.markdown(f"**果報:** {av.reading_zh}")

    st.divider()

    # ── 4. 王者瑜伽 (Raja Yoga) ──
    st.markdown("### 👑 王者瑜伽與特殊組合 (Raja Yoga & Special Yogas)")
    st.caption("根據 BPHS 第14章：王者瑜伽與特殊瑜伽")
    for ry in bphs_result.raja_yogas:
        icon = "✅" if ry.is_present else "⬜"
        with st.expander(f"{icon} {ry.name}"):
            st.markdown(f"**說明:** {ry.description_zh}")
            st.markdown(f"**判斷:** {ry.reason_zh}")

    st.divider()

    # ── 5. 宮位果報 (Bhava Phala) ──
    st.markdown("### 🏛️ 宮位果報 (Bhava Phala)")
    st.caption("根據 BPHS 第13章：各宮位行星落入的具體果報")
    for br in bphs_result.bhava_readings:
        label_parts = [f"第{br.bhava}宮 {br.bhava_zh}"]
        if br.signification:
            label_parts.append(f"— {br.signification}")
        label = " ".join(label_parts)
        with st.expander(label):
            st.markdown(f"**宮主 (Lord):** {br.lord_zh} ({br.lord_key}) — 落在第 {br.lord_house} 宮")
            if br.lord_placement_zh:
                st.info(f"📖 宮主落宮解讀：{br.lord_placement_zh}")
            if br.planets_in_bhava:
                st.markdown("**入宮行星解讀：**")
                for pk, pk_zh, reading, level in br.planets_in_bhava:
                    level_str = f" [{level}]" if level else ""
                    st.markdown(f"- **{pk_zh}** ({pk}){level_str}：{reading}")
            if br.special_yogas:
                st.markdown("**相關特殊瑜伽：**")
                for sy in br.special_yogas:
                    st.markdown(f"- **{sy.get('name', '')}**：{sy.get('zh', '')}")
            if br.note_zh:
                st.caption(f"💡 {br.note_zh}")

    st.divider()

    # ── 6. 16分盤簡表 (Shodasa Varga Reference) ──
    st.markdown("### 📊 十六分盤參考 (Shodasa Varga)")
    st.caption("根據 BPHS 第9章：16種分盤的用途與判斷標準")
    _varga_rows = []
    for key, val in bphs_result.varga_info.get("vargas", {}).items():
        _varga_rows.append({
            "分盤": key,
            "名稱": val.get("zh", ""),
            "切割": val.get("division", ""),
            "用途": val.get("use", ""),
            "判斷": val.get("judgment", ""),
        })
    if _varga_rows:
        st.dataframe(pd.DataFrame(_varga_rows), hide_index=True, use_container_width=True)
    note = bphs_result.varga_info.get("general_note_zh", "")
    if note:
        st.caption(f"💡 {note}")


st.title(t("app_title"))
st.markdown(t("app_subtitle"))

# ============================================================
# 預設城市資料
# ============================================================
# Internal keys are Chinese; CITY_NAMES_EN maps them to English display names.
CITY_PRESETS = {
    "自訂": (0.0, 0.0, 0.0),
    "北京": (39.9042, 116.4074, 8.0),
    "上海": (31.2304, 121.4737, 8.0),
    "香港": (22.3193, 114.1694, 8.0),
    "台北": (25.0330, 121.5654, 8.0),
    "東京": (35.6762, 139.6503, 9.0),
    "首爾": (37.5665, 126.9780, 9.0),
    "新加坡": (1.3521, 103.8198, 8.0),
    "倫敦": (51.5074, -0.1278, 0.0),
    "紐約": (40.7128, -74.0060, -5.0),
    "仰光": (16.8661, 96.1951, 6.5),
    "烏蘭巴托": (47.9077, 106.8832, 8.0),
}

CITY_NAMES_EN = {
    "自訂": "Custom",
    "北京": "Beijing",
    "上海": "Shanghai",
    "香港": "Hong Kong",
    "台北": "Taipei",
    "東京": "Tokyo",
    "首爾": "Seoul",
    "新加坡": "Singapore",
    "倫敦": "London",
    "紐約": "New York",
    "仰光": "Yangon",
    "烏蘭巴托": "Ulaanbaatar",
}

# ============================================================
# 側邊欄 - 輸入排盤資料
# ============================================================
with st.sidebar:
    # ── Language switcher (top of sidebar) ──────────────────
    st.radio(
        "🌐 Language / 語言",
        options=["繁體中文", "English"],
        index=0 if st.session_state.get("lang", "zh") == "zh" else 1,
        key="_lang_radio",
        horizontal=True,
    )
    st.divider()

    st.header(t("sidebar_header"))

    # 日期時間輸入
    st.subheader(t("date_time"))
    birth_date = st.date_input(
        t("birth_date"),
        value=date(1990, 1, 1),
        min_value=date(1900, 1, 1),
        max_value=date(2100, 12, 31),
    )
    birth_time = st.time_input(t("birth_time"), value=time(12, 0))

    # 地點輸入
    st.subheader(t("birth_location"))
    _city_format = (
        (lambda c: CITY_NAMES_EN.get(c, c))
        if st.session_state.get("lang") == "en"
        else (lambda c: c)
    )
    city = st.selectbox(
        t("city_preset"),
        options=list(CITY_PRESETS.keys()),
        format_func=_city_format,
    )

    if city != "自訂":
        preset_lat, preset_lon, preset_tz = CITY_PRESETS[city]
        input_lat = st.number_input(
            t("latitude"), value=preset_lat, format="%.4f",
            min_value=-90.0, max_value=90.0,
        )
        input_lon = st.number_input(
            t("longitude"), value=preset_lon, format="%.4f",
            min_value=-180.0, max_value=180.0,
        )
        input_tz = st.number_input(
            t("timezone"), value=preset_tz, format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
        )
        location_name = CITY_NAMES_EN[city] if st.session_state.get("lang") == "en" else city
    else:
        input_lat = st.number_input(
            t("latitude"), value=39.9042, format="%.4f",
            min_value=-90.0, max_value=90.0,
        )
        input_lon = st.number_input(
            t("longitude"), value=116.4074, format="%.4f",
            min_value=-180.0, max_value=180.0,
        )
        input_tz = st.number_input(
            t("timezone"), value=8.0, format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
        )
        location_name = t("custom_location")

    # 排盤按鈕
    calculate = st.button(t("calculate_btn"), width='stretch', type="primary")

    # 性別（用於七政四餘宮位方向）
    st.subheader(t("gender_header"))
    _male_label = t("male")
    _female_label = t("female")
    gender_choice = st.radio(
        t("gender_label"),
        options=[_male_label, _female_label],
        index=0,
        horizontal=True,
    )
    gender = "male" if gender_choice == _male_label else "female"

    # ── Astrology system selector (dropdown in sidebar) ────────
    st.divider()
    _SYSTEM_KEYS = [
        "tab_chinese", "tab_ziwei", "tab_western", "tab_indian",
        "tab_sukkayodo", "tab_thai", "tab_kabbalistic", "tab_arabic",
        "tab_maya", "tab_mahabote", "tab_decans", "tab_nadi",
        "tab_zurkhai", "tab_hellenistic", "tab_chinstar", "tab_contact",
    ]
    _SYSTEM_LABELS = {
        "tab_chinese": t("tab_chinese"),
        "tab_ziwei": t("tab_ziwei"),
        "tab_western": t("tab_western"),
        "tab_indian": t("tab_indian"),
        "tab_sukkayodo": t("tab_sukkayodo"),
        "tab_thai": t("tab_thai"),
        "tab_kabbalistic": t("tab_kabbalistic"),
        "tab_arabic": t("tab_arabic"),
        "tab_maya": t("tab_maya"),
        "tab_mahabote": t("tab_mahabote"),
        "tab_decans": t("tab_decans"),
        "tab_nadi": t("tab_nadi"),
        "tab_zurkhai": t("tab_zurkhai"),
        "tab_hellenistic": t("tab_hellenistic"),
        "tab_chinstar": t("tab_chinstar"),
        "tab_contact": t("tab_contact"),
    }

    # Determine default index from session state
    _current = st.session_state.get("_system_select", _SYSTEM_KEYS[0])
    if _current in _SYSTEM_KEYS:
        _default_idx = _SYSTEM_KEYS.index(_current)
    else:
        _default_idx = 0

    _selected_system = st.selectbox(
        t("sidebar_system_label"),
        options=_SYSTEM_KEYS,
        index=_default_idx,
        format_func=lambda k: _SYSTEM_LABELS.get(k, k),
        key="_system_select",
    )

    # ── AI Analysis settings ──────────────────────────────────
    st.divider()
    st.header(t("ai_settings_header"))

    _ai_model = st.selectbox(
        t("ai_model_label"),
        options=CEREBRAS_MODEL_OPTIONS,
        index=0,
        key="_ai_model_select",
        help="\n".join(f"• {k}: {v}" for k, v in CEREBRAS_MODEL_DESCRIPTIONS.items()),
    )

    # System prompt selector
    _prompts_data = load_system_prompts()
    _prompts_list = _prompts_data.get("prompts", [])
    _prompt_names = [p["name"] for p in _prompts_list]
    _selected_prompt_name = _prompts_data.get("selected", "")

    if _prompt_names:
        _sel_idx = 0
        if _selected_prompt_name in _prompt_names:
            _sel_idx = _prompt_names.index(_selected_prompt_name)

        _chosen_prompt_name = st.selectbox(
            t("ai_select_prompt"),
            options=_prompt_names,
            index=_sel_idx,
            key="_ai_prompt_select",
            help=t("ai_select_prompt_help"),
        )
        _prompts_data["selected"] = _chosen_prompt_name

        # Fetch selected prompt content
        _prompt_content = ""
        for _pr in _prompts_list:
            if _pr["name"] == _chosen_prompt_name:
                _prompt_content = _pr["content"]
                break

        if "ai_system_prompt" not in st.session_state:
            st.session_state.ai_system_prompt = _prompt_content
        elif _chosen_prompt_name != st.session_state.get("_last_ai_prompt_name"):
            st.session_state.ai_system_prompt = _prompt_content
        st.session_state._last_ai_prompt_name = _chosen_prompt_name

        _new_content = st.text_area(
            t("ai_edit_prompt"),
            value=st.session_state.ai_system_prompt,
            height=120,
            placeholder=t("ai_edit_prompt_placeholder"),
            key="_ai_prompt_editor",
        )
        st.session_state.ai_system_prompt = _new_content

        _col_upd, _col_del = st.columns(2)
        with _col_upd:
            if st.button(t("ai_update_prompt_btn"), key="_ai_update_prompt"):
                for _pr in _prompts_list:
                    if _pr["name"] == _chosen_prompt_name:
                        _pr["content"] = _new_content
                        break
                if save_system_prompts(_prompts_data):
                    st.toast(t("ai_prompt_updated").format(_chosen_prompt_name))
        with _col_del:
            if st.button(t("ai_delete_prompt_btn"), key="_ai_delete_prompt",
                         disabled=len(_prompts_list) <= 1):
                _prompts_list = [p for p in _prompts_list if p["name"] != _chosen_prompt_name]
                _prompts_data["prompts"] = _prompts_list
                if _chosen_prompt_name == _selected_prompt_name and _prompts_list:
                    _prompts_data["selected"] = _prompts_list[0]["name"]
                if save_system_prompts(_prompts_data):
                    st.toast(t("ai_prompt_deleted").format(_chosen_prompt_name))
                    st.rerun()

    # Add new prompt
    if "ai_form_key_suffix" not in st.session_state:
        st.session_state.ai_form_key_suffix = 0
    _nk = st.session_state.ai_form_key_suffix
    with st.expander(t("ai_add_prompt_expander"), expanded=False):
        _new_name = st.text_input(t("ai_new_prompt_name"), key=f"_ai_new_name_{_nk}")
        _new_body = st.text_area(
            t("ai_new_prompt_content"), height=100,
            placeholder=t("ai_new_prompt_placeholder"),
            key=f"_ai_new_body_{_nk}",
        )
        if st.button(t("ai_save_new_prompt_btn"), key=f"_ai_save_new_{_nk}"):
            if _new_name and _new_body:
                _prompts_list.append({"name": _new_name, "content": _new_body})
                _prompts_data["prompts"] = _prompts_list
                if save_system_prompts(_prompts_data):
                    st.toast(t("ai_prompt_saved").format(_new_name))
                    st.session_state.ai_form_key_suffix += 1
                    st.rerun()

    # Temperature & max tokens
    _ai_max_tokens = st.slider(
        t("ai_max_tokens"), min_value=256, max_value=32768, value=8192, step=256,
        key="_ai_max_tokens",
        help=t("ai_max_tokens_help"),
    )
    _ai_temperature = st.slider(
        t("ai_temperature"), min_value=0.0, max_value=2.0, value=0.7, step=0.1,
        key="_ai_temperature",
        help=t("ai_temperature_help"),
    )

# ============================================================
# AI Analysis helper — reusable across all system tabs
# ============================================================

def _render_ai_button(system_key: str, chart_obj, btn_key: str = ""):
    """Render the AI analysis button and execute the analysis when clicked.

    Parameters
    ----------
    system_key : str
        The system tab key (e.g. ``"tab_western"``).
    chart_obj : object
        The chart object produced by the compute function.
    btn_key : str
        Optional unique key suffix for the button widget.
    """
    _bk = f"_ai_btn_{system_key}_{btn_key}" if btn_key else f"_ai_btn_{system_key}"
    st.divider()
    if st.button(t("ai_analyze_btn"), key=_bk):
        with st.spinner(t("ai_analyzing")):
            # Resolve API key from secrets or env
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

            try:
                client = CerebrasClient(api_key=_api_key)
                chart_prompt = format_chart_for_prompt(system_key, chart_obj)
                messages = [
                    {"role": "system", "content": st.session_state.get("ai_system_prompt", "")},
                    {"role": "user", "content": chart_prompt},
                ]
                result = client.chat(
                    messages=messages,
                    model=st.session_state.get("_ai_model_select", CEREBRAS_MODEL_OPTIONS[0]),
                    max_tokens=st.session_state.get("_ai_max_tokens", 8192),
                    temperature=st.session_state.get("_ai_temperature", 0.7),
                )
                with st.expander(t("ai_result_header"), expanded=True):
                    st.markdown(result)
            except RateLimitError:
                st.warning(t("ai_rate_limit"))
            except Exception as e:
                st.error(t("ai_error").format(str(e)))

# ============================================================
# Main Area — Render the selected astrology system
# 主區域 — 根據側邊欄選擇顯示對應占星體系
# ============================================================

if calculate:
    _params = dict(
        year=birth_date.year, month=birth_date.month, day=birth_date.day,
        hour=birth_time.hour, minute=birth_time.minute,
        timezone=input_tz, latitude=input_lat, longitude=input_lon,
        location_name=location_name,
    )
    # Store params in session_state for lazy per-tab computation
    st.session_state["_calc_params"] = _params
    st.session_state["_calc_gender"] = gender
    st.session_state["_calculated"] = True

_is_calculated = st.session_state.get("_calculated", False)

# --- 七政四餘（中國） ---
if _selected_system == "tab_chinese":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            _g = st.session_state["_calc_gender"]
            with st.spinner(t("spinner_chinese")):
                chart = compute_chart(**_p, gender=_g)

            # 子 tabs for the Chinese chart
            _ch_tab_natal, _ch_tab_shensha, _ch_tab_dasha, _ch_tab_transit, _ch_tab_zhangguo, _ch_tab_elect = st.tabs([
                t("ch_subtab_natal"),
                t("ch_subtab_shensha"),
                t("ch_subtab_dasha"),
                t("ch_subtab_transit"),
                t("ch_subtab_zhangguo"),
                t("ch_subtab_electional"),
            ])

            with _ch_tab_natal:
                render_chart_info(chart)
                st.divider()

                # 計算流時盤 for overlay
                _transit_now = compute_transit_now(timezone=input_tz)

                # 選擇是否顯示流時對盤
                _show_transit_overlay = st.checkbox(
                    t("show_transit_overlay"), value=False,
                )
                _transit_for_ring = _transit_now if _show_transit_overlay else None

                render_mansion_ring(chart, transit=_transit_for_ring)
                st.divider()
                render_bazi(chart)
                st.divider()
                render_planet_table(chart)
                st.divider()
                render_house_table(chart)
                st.divider()
                render_aspect_summary(chart)
                st.divider()
                render_download_buttons(chinese_chart_to_dict(chart), key_prefix="chinese")

            with _ch_tab_shensha:
                _shensha = compute_shensha(
                    year=chart.year,
                    solar_month=chart.solar_month,
                    julian_day=chart.julian_day,
                    hour_branch=chart.hour_branch,
                    timezone=chart.timezone,
                )
                render_shensha(chart, _shensha)

            with _ch_tab_dasha:
                from datetime import datetime as _dt
                _current_year = _dt.now().year
                _dasha = compute_dasha(
                    birth_year=chart.year,
                    ming_gong_branch=chart.ming_gong_branch,
                    gender=_g,
                    houses=chart.houses,
                    current_year=_current_year,
                )
                render_dasha(chart, _dasha)
                # Dasha interpretation
                if _dasha.current_period_idx >= 0:
                    _cur_period = _dasha.periods[_dasha.current_period_idx]
                    _reading = get_qizheng_dasha_reading(_cur_period.lord, get_lang())
                    if _reading:
                        st.divider()
                        st.subheader(t("dasha_reading_header"))
                        st.info(f"**{_cur_period.lord}** — {_reading}")

            with _ch_tab_transit:
                st.subheader(t("transit_header"))
                _t_col1, _t_col2, _t_col3 = st.columns(3)
                with _t_col1:
                    _t_date = st.date_input(
                        t("transit_date"),
                        value=datetime.now().date(),
                        key="transit_date_input",
                    )
                with _t_col2:
                    _t_time = st.time_input(
                        t("transit_time"),
                        value=datetime.now().time(),
                        key="transit_time_input",
                    )
                with _t_col3:
                    _t_tz = st.number_input(
                        t("transit_tz"),
                        value=input_tz,
                        format="%.1f",
                        min_value=-12.0, max_value=14.0, step=0.5,
                        key="transit_tz_input",
                    )

                _transit_custom = compute_transit(
                    year=_t_date.year, month=_t_date.month, day=_t_date.day,
                    hour=_t_time.hour, minute=_t_time.minute,
                    timezone=_t_tz,
                )
                render_transit_comparison(chart, _transit_custom)

            with _ch_tab_zhangguo:
                _zhangguo = compute_zhangguo(
                    planets=chart.planets,
                    houses=chart.houses,
                    gender=_g,
                )
                render_zhangguo(chart, _zhangguo)

            with _ch_tab_elect:
                render_electional_tool(timezone=input_tz)

            # AI Analysis button for Chinese
            _render_ai_button("tab_chinese", chart, btn_key="chinese")

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_chinese"))

# --- 紫微斗數 ---
elif _selected_system == "tab_ziwei":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_ziwei")):
                zw_chart = compute_ziwei_chart(**_p)
            render_ziwei_chart(zw_chart)
            _render_ai_button("tab_ziwei", zw_chart, btn_key="ziwei")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_ziwei"))

# --- 西洋占星 ---
elif _selected_system == "tab_western":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            sidereal_mode = st.checkbox(
                t("sidereal_label"),
                value=False,
                help=t("sidereal_help"),
            )
            with st.spinner(t("spinner_western")):
                w_params = dict(**_p, sidereal=sidereal_mode)
                w_chart = compute_western_chart(**w_params)

            _w_tab_natal, _w_tab_transit, _w_tab_return, _w_tab_synastry, _w_tab_dignity = st.tabs([
                t("western_subtab_natal"),
                t("western_subtab_transit"),
                t("western_subtab_return"),
                t("western_subtab_synastry"),
                t("western_subtab_dignity"),
            ])

            with _w_tab_natal:
                render_western_chart(w_chart)
                # Natal summary
                with st.expander(t("natal_summary_header"), expanded=True):
                    _summary = generate_natal_summary(
                        w_chart.planets, w_chart.houses,
                        getattr(w_chart, 'asc_sign', ''),
                        lang=get_lang(),
                    )
                    st.markdown(_summary)
                # Fixed stars & asteroids checkboxes
                _show_stars = st.checkbox(t("show_fixed_stars"), value=False, key="w_stars")
                _show_asteroids = st.checkbox(t("show_asteroids"), value=False, key="w_asteroids")
                if _show_stars:
                    stars = compute_fixed_star_positions(w_chart.julian_day)
                    p_lons = {p.name: p.longitude for p in w_chart.planets}
                    conjs = find_conjunctions(stars, p_lons)
                    if conjs:
                        st.markdown("#### ⭐ Fixed Star Conjunctions / 恆星合相")
                        st.dataframe([{"Star": c.star_name, "Planet": c.planet_name,
                                       "Orb": f"{c.orb:.2f}°", "Nature": c.nature,
                                       "Meaning": c.meaning_cn}
                                      for c in conjs], width="stretch")
                    else:
                        st.info("No fixed star conjunctions within orb.")
                if _show_asteroids:
                    asts = compute_asteroids(w_chart.julian_day)
                    if asts:
                        st.markdown("#### ☄️ Asteroids / 小行星")
                        st.dataframe([{"Name": f"{a.name} {a.symbol} ({a.name_cn})",
                                       "Sign": a.sign, "Degree": f"{a.sign_degree:.2f}°",
                                       "R": "R" if a.retrograde else "",
                                       "Meaning": a.meaning_cn}
                                      for a in asts], width="stretch")
                # Export
                render_download_buttons(western_chart_to_dict(w_chart), key_prefix="western")

            with _w_tab_transit:
                st.subheader(t("western_subtab_transit"))
                _wt_col1, _wt_col2 = st.columns(2)
                with _wt_col1:
                    _wt_date = st.date_input(t("transit_target_date"),
                                             value=datetime.now().date(),
                                             key="wt_date")
                with _wt_col2:
                    _wt_time = st.time_input("Time", value=datetime.now().time(),
                                             key="wt_time")
                w_transits = compute_western_transits(
                    w_chart, _wt_date.year, _wt_date.month, _wt_date.day,
                    _wt_time.hour, _wt_time.minute, input_tz,
                )
                if w_transits.aspects_to_natal:
                    st.dataframe([{"Transit": a.transit_planet, "Natal": a.natal_planet,
                                   "Aspect": a.aspect_name, "Orb": f"{a.orb:.1f}°",
                                   "Applying": "→" if a.is_applying else "←"}
                                  for a in w_transits.aspects_to_natal[:20]],
                                 width="stretch")
                    # Transit readings
                    st.subheader(t("transit_readings_header"))
                    _lang = get_lang()
                    for _ta in w_transits.aspects_to_natal[:5]:
                        _reading = _ta.interpretation_cn if _lang == "zh" else _ta.interpretation_en
                        st.info(f"**{_ta.transit_planet} {_ta.aspect_symbol} {_ta.natal_planet}** (orb {_ta.orb}°)\n\n{_reading}")
                else:
                    st.info("No transit aspects found.")

            with _w_tab_return:
                st.subheader(t("western_subtab_return"))
                _return_year = st.number_input(t("return_year_label"),
                                               value=datetime.now().year,
                                               min_value=1900, max_value=2100,
                                               key="return_year")
                sun_planet = next((p for p in w_chart.planets if p.name.startswith("Sun")), None)
                if sun_planet:
                    sr = compute_solar_return(
                        sun_planet.longitude, _return_year,
                        input_lat, input_lon, input_tz, location_name,
                    )
                    st.success(f"Solar Return: **{sr.return_date}**")
                    render_western_chart(sr.return_chart)
                else:
                    st.warning("Sun position not found in natal chart.")

            with _w_tab_synastry:
                st.subheader(t("synastry_header"))
                st.markdown(t("synastry_person_b"))
                _s_col1, _s_col2, _s_col3 = st.columns(3)
                with _s_col1:
                    _s_date = st.date_input("Date B", value=date(1990, 6, 15), key="syn_date")
                with _s_col2:
                    _s_time = st.time_input("Time B", value=time(12, 0), key="syn_time")
                with _s_col3:
                    _s_tz = st.number_input("TZ B", value=input_tz, key="syn_tz",
                                            min_value=-12.0, max_value=14.0, step=0.5)
                if st.button("Calculate Synastry / 計算合盤", key="syn_btn"):
                    w_b = compute_western_chart(
                        year=_s_date.year, month=_s_date.month, day=_s_date.day,
                        hour=_s_time.hour, minute=_s_time.minute,
                        timezone=_s_tz, latitude=input_lat, longitude=input_lon,
                        location_name=location_name,
                    )
                    syn = compute_synastry(w_chart, w_b, "Person A", "Person B")
                    st.metric("Harmony Score", f"{syn.harmony_summary:.3f}")
                    st.info(syn.summary_cn if get_lang() == "zh" else syn.summary_en)
                    if syn.element_compatibility:
                        st.write(f"🔮 {syn.element_compatibility}")
                    if syn.inter_aspects:
                        st.dataframe([{"A": a.planet_a, "B": a.planet_b,
                                       "Aspect": a.aspect_name, "Orb": f"{a.orb:.1f}°",
                                       "Score": f"{a.harmony_score:+.3f}"}
                                      for a in syn.inter_aspects[:20]],
                                     width="stretch")
                        # Synastry readings (top 5)
                        st.subheader(t("synastry_readings_header"))
                        _lang = get_lang()
                        for _sa in syn.inter_aspects[:5]:
                            _reading = _sa.interpretation_cn if _lang == "zh" else _sa.interpretation_en
                            st.info(f"**{_sa.planet_a} {_sa.aspect_symbol} {_sa.planet_b}** (orb {_sa.orb}°)\n\n{_reading}")

            with _w_tab_dignity:
                st.subheader(t("western_subtab_dignity"))
                _calc = PtolemyDignityCalculator()
                _PLANET_MAP = {"Sun": PtolPlanet.SUN, "Moon": PtolPlanet.MOON, "Mercury": PtolPlanet.MERCURY,
                               "Venus": PtolPlanet.VENUS, "Mars": PtolPlanet.MARS, "Jupiter": PtolPlanet.JUPITER, "Saturn": PtolPlanet.SATURN}
                _dignity_rows = []
                for p in w_chart.planets:
                    _pname = p.name.split("(")[0].strip().split()[0]
                    _ptol = _PLANET_MAP.get(_pname)
                    if _ptol:
                        _sign = getattr(p, 'sign', '') or ''
                        _sign_key = _sign.split()[0] if _sign else ''
                        _degree = getattr(p, 'sign_degree', p.longitude % 30)
                        _digs = _calc.get_dignities(_ptol, _sign_key, _degree, is_day_chart=True)
                        _score = _calc.calculate_total_score(_digs)
                        _dignity_rows.append({
                            "Planet": f"{_pname} ({_ptol.value})",
                            "Sign": f"{_sign_key} ({SIGN_NAMES.get(_sign_key, '')})",
                            "Degree": f"{_degree:.2f}°",
                            "Dignities": dignity_to_chinese(_digs),
                            "Score": _score,
                        })
                if _dignity_rows:
                    st.dataframe(_dignity_rows, width="stretch")
                else:
                    st.info("No traditional planet dignity data available.")

            # AI Analysis button for Western
            _render_ai_button("tab_western", w_chart, btn_key="western")

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_western"))

# --- 印度占星 ---
elif _selected_system == "tab_indian":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_indian")):
                v_chart = compute_vedic_chart(**_p)

            _v_tab_rashi, _v_tab_dasha, _v_tab_ashtaka, _v_tab_yogas, _v_tab_bphs = st.tabs([
                t("vedic_subtab_rashi"),
                t("vedic_subtab_dasha"),
                t("vedic_subtab_ashtaka"),
                t("vedic_subtab_yogas"),
                t("vedic_subtab_bphs"),
            ])

            with _v_tab_rashi:
                render_vedic_chart(v_chart)
                render_download_buttons(vedic_chart_to_dict(v_chart), key_prefix="vedic")

            with _v_tab_dasha:
                st.subheader(t("vedic_subtab_dasha"))
                moon_p = next((p for p in v_chart.planets if "Chandra" in p.name or "Moon" in p.name), None)
                if moon_p:
                    vim = compute_vimshottari(moon_p.longitude, v_chart.julian_day)
                    st.info(f"Moon Nakshatra: **{vim.moon_nakshatra}** | Lord: **{vim.moon_nakshatra_lord}** | Balance: {vim.balance_years:.2f} yrs")
                    for md in vim.mahadasha_periods:
                        _dasha_reading = get_dasha_reading(md.lord, get_lang())
                        with st.expander(f"**{md.lord}** ({md.lord_cn}) — {md.start_date} to {md.end_date} ({md.years:.1f} yrs)"):
                            if _dasha_reading:
                                st.markdown(f"📖 {_dasha_reading}")
                            if md.sub_periods:
                                st.dataframe([{"Lord": s.lord, "CN": s.lord_cn,
                                              "Start": s.start_date, "End": s.end_date,
                                              "Years": f"{s.years:.2f}"}
                                             for s in md.sub_periods],
                                             width="stretch")
                    st.divider()
                    st.markdown("##### Yogini Dasha (36-year cycle)")
                    yog = compute_yogini(moon_p.longitude, v_chart.julian_day)
                    st.dataframe([{"Yogini": p.lord, "CN": p.lord_cn,
                                  "Start": p.start_date, "End": p.end_date,
                                  "Years": f"{p.years:.2f}"}
                                 for p in yog.periods], width="stretch")
                    # Yogini reading for current period
                    if yog.periods:
                        _yog_reading = get_yogini_reading(yog.periods[0].lord, get_lang())
                        if _yog_reading:
                            st.info(f"📖 Current: {_yog_reading}")
                else:
                    st.warning("Moon position not found.")

            with _v_tab_ashtaka:
                st.subheader(t("vedic_subtab_ashtaka"))
                p_lons = {}
                for p in v_chart.planets:
                    key = p.name.split("(")[0].strip().split()[0]
                    _MAP = {"Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars",
                            "Budha": "Mercury", "Guru": "Jupiter", "Shukra": "Venus", "Shani": "Saturn"}
                    canonical = _MAP.get(key, key)
                    p_lons[canonical] = p.longitude
                asc_lon = getattr(v_chart, 'ascendant', 0.0) if hasattr(v_chart, 'ascendant') else 0.0
                if len(p_lons) >= 7:
                    av = compute_ashtakavarga(p_lons, asc_lon)
                    st.info(f"Sarvashtakavarga Total: **{av.sarva_total}**")
                    import pandas as pd
                    signs = ["Ari", "Tau", "Gem", "Can", "Leo", "Vir",
                             "Lib", "Sco", "Sag", "Cap", "Aqu", "Pis"]
                    rows = []
                    for bav in av.bav:
                        row = {"Planet": f"{bav.planet} ({bav.planet_cn})"}
                        for i, s in enumerate(signs):
                            row[s] = bav.bindus[i]
                        row["Total"] = bav.total
                        rows.append(row)
                    sarva_row = {"Planet": "SARVA"}
                    for i, s in enumerate(signs):
                        sarva_row[s] = av.sarva[i]
                    sarva_row["Total"] = av.sarva_total
                    rows.append(sarva_row)
                    st.dataframe(pd.DataFrame(rows), width="stretch")
                else:
                    st.warning("Insufficient planet data for Ashtakavarga.")

            with _v_tab_yogas:
                st.subheader(t("vedic_subtab_yogas"))
                p_lons_y = {}
                for p in v_chart.planets:
                    key = p.name.split("(")[0].strip().split()[0]
                    _MAP2 = {"Surya": "Sun", "Chandra": "Moon", "Mangal": "Mars",
                             "Budha": "Mercury", "Guru": "Jupiter", "Shukra": "Venus",
                             "Shani": "Saturn", "Rahu": "Rahu", "Ketu": "Ketu"}
                    canonical = _MAP2.get(key, key)
                    p_lons_y[canonical] = p.longitude
                asc_lon_y = getattr(v_chart, 'ascendant', 0.0) if hasattr(v_chart, 'ascendant') else 0.0
                yogas = compute_yogas(p_lons_y, asc_lon_y)
                for yg in yogas:
                    icon = "✅" if yg.is_present else "⬜"
                    with st.expander(f"{icon} {yg.name} ({yg.name_cn}) — {yg.strength}"):
                        st.write(yg.description_cn if get_lang() == "zh" else yg.description)

            with _v_tab_bphs:
                st.subheader("📜 " + t("vedic_subtab_bphs"))
                bphs_result = compute_bphs(v_chart.planets, v_chart.houses, v_chart.ascendant)
                _render_bphs_result(bphs_result)

            # AI Analysis button for Vedic
            _render_ai_button("tab_indian", v_chart, btn_key="vedic")

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_indian"))

# --- 宿曜道 ---
elif _selected_system == "tab_sukkayodo":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            st.subheader(t("sukkayodo_subheader"))
            st.info(t("sukkayodo_info"))
            st.markdown(t("desc_sukkayodo"))
            with st.spinner(t("spinner_indian")):
                _v_chart_sukka = compute_vedic_chart(**_p)
            render_sukkayodo_chart(_v_chart_sukka)
            _render_ai_button("tab_sukkayodo", _v_chart_sukka, btn_key="sukkayodo")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_sukkayodo"))

# --- 泰國占星 ---
elif _selected_system == "tab_thai":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_thai")):
                t_chart = compute_thai_chart(**_p)
            thai_tab_chart, thai_tab_nine = st.tabs(
                [t("thai_subtab_chart"), t("thai_subtab_nine")]
            )
            with thai_tab_chart:
                render_thai_chart(t_chart)
            with thai_tab_nine:
                nine_grid_result = calculate_thai_nine_grid(
                    birth_date.day, birth_date.month, birth_date.year
                )
                render_nine_grid(nine_grid_result)
                st.markdown("---")
                divination_result = calculate_nine_palace_divination(t_chart)
                render_nine_palace_divination(divination_result)
            _render_ai_button("tab_thai", t_chart, btn_key="thai")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_thai"))

# --- 卡巴拉占星 ---
elif _selected_system == "tab_kabbalistic":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_kabbalistic")):
                k_chart = compute_kabbalistic_chart(**_p)
            render_kabbalistic_chart(k_chart)
            _render_ai_button("tab_kabbalistic", k_chart, btn_key="kabbalistic")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_kabbalistic"))

# --- 阿拉伯占星 ---
elif _selected_system == "tab_arabic":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            arabic_subtab_chart, arabic_subtab_picatrix, arabic_subtab_shams, arabic_subtab_ref = st.tabs([
                t("arabic_subtab_chart"),
                t("arabic_subtab_picatrix"),
                t("arabic_subtab_shams"),
                t("arabic_subtab_reference"),
            ])

            with arabic_subtab_chart:
                with st.spinner(t("spinner_arabic")):
                    a_chart = compute_arabic_chart(**_p)
                render_arabic_chart(a_chart)

            # --- Picatrix 星體魔法 ---
            with arabic_subtab_picatrix:
                st.subheader(t("picatrix_subheader"))
                st.caption(t("picatrix_source"))

                _birth_moon_lon: float | None = compute_moon_longitude(
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    timezone=input_tz,
                )

                ptab_browse, ptab_mansions, ptab_hours, ptab_talisman = st.tabs([
                    t("picatrix_subtab_browse"),
                    t("picatrix_subtab_mansion"),
                    t("picatrix_subtab_hours"),
                    t("picatrix_subtab_talisman"),
                ])

                with ptab_browse:
                    render_picatrix_browse()

                with ptab_mansions:
                    st.info(f"🌙 使用出生月亮黃經 (Birth Moon Longitude)：{_birth_moon_lon:.2f}°")
                    render_mansion_lookup(moon_lon=_birth_moon_lon)

                with ptab_hours:
                    render_planetary_hours_tool(
                        year=birth_date.year,
                        month=birth_date.month,
                        day=birth_date.day,
                        timezone=input_tz,
                        latitude=input_lat,
                        longitude=input_lon,
                    )

                with ptab_talisman:
                    render_talisman_generator()

            # --- 太陽知識大全 (Shams al-Maʻārif) ---
            with arabic_subtab_shams:
                st.subheader(t("shams_subheader"))
                st.caption(t("shams_source"))

                # Compute Arabic chart if not already done
                try:
                    _a_chart_for_shams = a_chart
                except NameError:
                    with st.spinner(t("spinner_arabic")):
                        _a_chart_for_shams = compute_arabic_chart(**_p)
                _shams_planets = {
                    p.name.split("(")[0].strip().split()[-1]: p.longitude
                    for p in _a_chart_for_shams.planets
                }
                _shams_sun_idx: int | None = None
                for p in _a_chart_for_shams.planets:
                    if "Sun" in p.name:
                        _shams_sun_idx = int(p.longitude / 30.0)
                        break
                render_shams_chart(chart_planets=_shams_planets,
                                   birth_sign_idx=_shams_sun_idx)

            with arabic_subtab_ref:
                st.subheader(t("arabic_subtab_reference"))
                _render_reference_library()

            # AI Analysis button for Arabic
            _render_ai_button("tab_arabic", a_chart, btn_key="arabic")

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        arabic_subtab_chart, arabic_subtab_picatrix, arabic_subtab_shams, arabic_subtab_ref = st.tabs([
            t("arabic_subtab_chart"),
            t("arabic_subtab_picatrix"),
            t("arabic_subtab_shams"),
            t("arabic_subtab_reference"),
        ])

        with arabic_subtab_chart:
            st.info(t("info_calc_prompt"))
            st.markdown(t("desc_arabic"))

        with arabic_subtab_picatrix:
            st.subheader(t("picatrix_subheader"))
            st.caption(t("picatrix_source"))

            ptab_browse, ptab_mansions, ptab_hours, ptab_talisman = st.tabs([
                t("picatrix_subtab_browse"),
                t("picatrix_subtab_mansion"),
                t("picatrix_subtab_hours"),
                t("picatrix_subtab_talisman"),
            ])

            with ptab_browse:
                render_picatrix_browse()

            with ptab_mansions:
                render_mansion_lookup(moon_lon=None)

            with ptab_hours:
                render_planetary_hours_tool(
                    timezone=input_tz,
                    latitude=input_lat,
                    longitude=input_lon,
                )

            with ptab_talisman:
                render_talisman_generator()

        with arabic_subtab_shams:
            st.subheader(t("shams_subheader"))
            st.caption(t("shams_source"))
            st.markdown(t("desc_shams"))
            render_shams_browse()

        with arabic_subtab_ref:
            st.subheader(t("arabic_subtab_reference"))
            _render_reference_library()

# --- 瑪雅占星 ---
elif _selected_system == "tab_maya":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_maya")):
                m_chart = compute_maya_chart(**_p)
            render_maya_chart(m_chart)
            _render_ai_button("tab_maya", m_chart, btn_key="maya")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_maya"))

# --- 緬甸占星 (Mahabote) ---
elif _selected_system == "tab_mahabote":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_mahabote")):
                mb_chart = compute_mahabote_chart(**_p)
            render_mahabote_chart(mb_chart)
            _render_ai_button("tab_mahabote", mb_chart, btn_key="mahabote")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_mahabote"))

# --- 古埃及十度區間 (Decans) ---
elif _selected_system == "tab_decans":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_decans")):
                dc_chart = compute_decan_chart(**_p)
            render_decan_chart(dc_chart)
            _render_ai_button("tab_decans", dc_chart, btn_key="decans")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_decans_prompt"))
        render_decan_browse()

# --- 納迪占星 (Nadi Jyotish) ---
elif _selected_system == "tab_nadi":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_nadi")):
                nadi_chart = compute_nadi_chart(**_p)
            render_nadi_chart(nadi_chart)
            _render_ai_button("tab_nadi", nadi_chart, btn_key="nadi")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_nadi"))

# --- 蒙古祖爾海 (Zurkhai) ---
elif _selected_system == "tab_zurkhai":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_zurkhai")):
                zk_chart = compute_zurkhai_chart(**_p)
            render_zurkhai_chart(zk_chart)
            _render_ai_button("tab_zurkhai", zk_chart, btn_key="zurkhai")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_zurkhai"))

# --- 希臘占星 (Hellenistic) ---
elif _selected_system == "tab_hellenistic":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            st.markdown(t("desc_hellenistic"))
            # Hellenistic needs a western chart first
            with st.spinner(t("spinner_western")):
                _hellen_w = compute_western_chart(**_p)
            with st.spinner(t("spinner_hellenistic")):
                _hellen_chart = compute_hellenistic_chart(
                    _hellen_w,
                    birth_year=birth_date.year,
                    current_year=datetime.now().year,
                )
            _h_tab_chart, _h_tab_natal, _h_tab_prof, _h_tab_zr, _h_tab_lots, _h_tab_centiloquy = st.tabs([
                t("hellen_subtab_chart"),
                t("hellen_subtab_natal"),
                t("hellen_subtab_profections"),
                t("hellen_subtab_zr"),
                t("hellen_subtab_lots"),
                t("hellen_subtab_centiloquy"),
            ])
            with _h_tab_chart:
                _greek_svg = build_greek_horoscope_svg(
                    _hellen_chart,
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    tz=input_tz,
                    location=location_name,
                )
                st.markdown(_greek_svg, unsafe_allow_html=True)
                st.caption(
                    '<p style="text-align:center; color:#888; font-size:11px;">'
                    'Greek Horoscope (θέμα) — Square chart form after L 497 · '
                    'Whole-sign houses · ASC at left, MC at top'
                    '</p>',
                    unsafe_allow_html=True,
                )
            with _h_tab_natal:
                render_hellenistic_chart(_hellen_chart)
            with _h_tab_prof:
                if _hellen_chart.profection:
                    pf = _hellen_chart.profection
                    st.subheader("Annual Profections / 年限推進")
                    st.metric("Age", pf.current_age)
                    st.metric("Profected Sign", f"{pf.profected_sign} ({pf.profected_sign_cn})")
                    st.metric("Time Lord", f"{pf.time_lord} ({pf.time_lord_cn})")
                    st.info(f"House from Ascendant: {pf.house_from_asc}")
            with _h_tab_zr:
                if _hellen_chart.zodiacal_releasing:
                    st.subheader("Zodiacal Releasing (L1) / 黃道釋放")
                    st.dataframe([{"Sign": p.sign, "CN": p.sign_cn,
                                   "Ruler": p.ruler, "Years": p.years,
                                   "Start": p.start_date, "End": p.end_date}
                                  for p in _hellen_chart.zodiacal_releasing],
                                 width="stretch")
            with _h_tab_lots:
                if _hellen_chart.lots:
                    st.subheader("Greek Lots / 希臘點")
                    st.dataframe([{"Name": f"{l.name} ({l.name_cn})",
                                   "Sign": l.sign, "Degree": f"{l.sign_degree:.2f}°",
                                   "House": l.house, "Formula": l.formula_en,
                                   "Meaning": l.meaning_cn}
                                  for l in _hellen_chart.lots],
                                 width="stretch")

            with _h_tab_centiloquy:
                st.subheader("托勒密《百論》 / Ptolemy's Centiloquy")
                from astro.classic.ptolemy_centiloquy import get_random_aphorism, search_aphorism, get_all_aphorisms, format_aphorism
                # Daily aphorism
                st.info(format_aphorism(get_random_aphorism()))
                # Search
                _cent_query = st.text_input("🔍 搜尋關鍵字 / Search keyword", key="centiloquy_search")
                if _cent_query:
                    _results = search_aphorism(_cent_query)
                    if _results:
                        for _r in _results:
                            st.markdown(format_aphorism(_r))
                    else:
                        st.warning("未找到匹配的格言 / No matching aphorisms found.")
                else:
                    for _a in get_all_aphorisms():
                        with st.expander(f"第 {_a['id']} 條"):
                            st.markdown(_a["text"])

            # AI Analysis button for Hellenistic
            _render_ai_button("tab_hellenistic", _hellen_chart, btn_key="hellenistic")

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_hellenistic"))

# --- 萬化仙禽 (WanHua XianQin) ---
elif _selected_system == "tab_chinstar":
    st.markdown(t("desc_chinstar"))

    # ── Lunar date input ────────────────────────────────────────
    st.subheader(t("chinstar_lunar_input_header"))

    _auto_convert = st.checkbox(t("chinstar_use_auto"), value=True, key="chinstar_auto_convert")

    # Defaults (will be overridden by auto-convert or manual inputs)
    _chinstar_year = birth_date.year
    _chinstar_month = birth_date.month
    _chinstar_day = birth_date.day
    _chinstar_hour = birth_time.hour
    _auto_ok = False

    if _auto_convert and _is_calculated:
        try:
            import swisseph as _swe_cs
            from astro.ziwei import _solar_to_lunar as _cs_solar_to_lunar
            _p = st.session_state["_calc_params"]
            _cs_jd = _swe_cs.julday(
                _p["year"], _p["month"], _p["day"],
                _p["hour"] + _p["minute"] / 60.0 - _p["timezone"],
            )
            _cs_ly, _cs_lm, _cs_ld, _cs_leap = _cs_solar_to_lunar(_cs_jd)
            _chinstar_year = _cs_ly
            _chinstar_month = _cs_lm
            _chinstar_day = _cs_ld
            _chinstar_hour = _p["hour"]
            from astro.chinstar.chinstar import BRANCHES as _cs_br
            _cs_branch_idx = ((int(_chinstar_hour) + 1) // 2) % 12
            _cs_hour_branch = _cs_br[_cs_branch_idx]
            st.info(
                t("chinstar_auto_result").format(
                    year=_cs_ly, month=_cs_lm, day=_cs_ld,
                    hour=_cs_hour_branch,
                )
                + (t("chinstar_leap_month") if _cs_leap else "")
            )
            _auto_ok = True
        except Exception as _cs_conv_e:
            st.warning(t("chinstar_auto_convert_failed") + str(_cs_conv_e))

    if not _auto_ok:
        _cs_col1, _cs_col2, _cs_col3 = st.columns(3)
        with _cs_col1:
            _chinstar_year = st.number_input(
                t("chinstar_lunar_year"), value=int(_chinstar_year),
                min_value=1, max_value=2200, key="cs_year",
            )
        with _cs_col2:
            _chinstar_month = st.number_input(
                t("chinstar_lunar_month"), value=int(_chinstar_month),
                min_value=1, max_value=12, key="cs_month",
            )
        with _cs_col3:
            _chinstar_day = st.number_input(
                t("chinstar_lunar_day"), value=int(_chinstar_day),
                min_value=1, max_value=30, key="cs_day",
            )

    _cs_gender = "M" if gender == "male" else "F"

    if st.button(t("calculate_btn"), key="chinstar_calc_btn") or _auto_ok:
        try:
            with st.spinner(t("spinner_chinstar")):
                _cs_tool = WanHuaXianQin()
                _cs_chart = _cs_tool.build_chart(
                    year=int(_chinstar_year),
                    month=int(_chinstar_month),
                    day=int(_chinstar_day),
                    hour=int(_chinstar_hour),
                    gender=_cs_gender,
                )

            _cs_tab_chart, _cs_tab_xiangtai, _cs_tab_gui_jian, _cs_tab_text = st.tabs([
                t("chinstar_subtab_chart"),
                t("chinstar_subtab_xiangtai"),
                t("chinstar_subtab_gui_jian"),
                t("chinstar_subtab_text"),
            ])

            with _cs_tab_chart:
                from astro.chinstar.chinstar import BRANCHES as _cs_branches, QIN_ELEMENT as _cs_qin_elem

                bi = _cs_chart["basic_info"]
                p = _cs_chart["palaces"]
                s = _cs_chart["stars"]
                pat = _cs_chart["pattern"]

                # ── 宮位→禽 映射 ──────────────────────────────
                _cs_palace_bird = {
                    "命宮":   s["ming_xing"],
                    "財帛宮": s["derived"].get("財帛星", ""),
                    "兄弟宮": s["derived"].get("兄弟星", ""),
                    "田宅宮": s["derived"].get("田宅星", ""),
                    "子女宮": s["derived"].get("子息星", ""),
                    "奴僕宮": s["derived"].get("奴僕星", ""),
                    "夫妻宮": s["derived"].get("妻妾星", ""),
                    "疾厄宮": s["derived"].get("疾厄星", ""),
                    "遷移宮": s["derived"].get("遷移星", ""),
                    "官祿宮": s["derived"].get("官祿星", ""),
                    "福德宮": s["derived"].get("福德星", ""),
                    "相貌宮": s["derived"].get("相貌星", ""),
                }
                # 地支→宮名（反查）
                _cs_branch_to_palace = {v: k for k, v in p["twelve"].items()}

                # 特殊宮位地支（命/身/胎）
                _cs_ming_br = p["ming_gong"]["branch"]
                _cs_shen_br = p["shen_gong"]["branch"]
                _cs_tai_br  = p["tai_gong"]["branch"]

                # 五行色彩
                _cs_elem_bg = {
                    "木": "#d9f2d9", "火": "#ffe0d0",
                    "土": "#fffbcc", "金": "#e8e8e8", "水": "#cce5ff",
                }
                _cs_elem_bd = {
                    "木": "#388e3c", "火": "#c62828",
                    "土": "#f57f17", "金": "#616161", "水": "#1565c0",
                }

                def _cs_cell(branch_char: str) -> str:
                    palace = _cs_branch_to_palace.get(branch_char, "")
                    bird   = _cs_palace_bird.get(palace, "")
                    elem   = _cs_qin_elem.get(bird, "")
                    bg     = _cs_elem_bg.get(elem, "#f9f9f9")
                    bd     = _cs_elem_bd.get(elem, "#999")
                    badge  = ""
                    if branch_char == _cs_ming_br:
                        badge = '<span style="color:#c62828;font-size:10px;">★命</span> '
                        bd    = "#c62828"
                        bg    = "#fff0f0"
                    elif branch_char == _cs_shen_br:
                        badge = '<span style="color:#6a1b9a;font-size:10px;">☆身</span> '
                        bd    = "#6a1b9a"
                        bg    = "#f9f0ff"
                    elif branch_char == _cs_tai_br:
                        badge = '<span style="color:#e64a19;font-size:10px;">◎胎</span> '
                        bd    = "#e64a19"
                        bg    = "#fff3e0"
                    return (
                        f'<td style="width:100px;height:88px;text-align:center;'
                        f'vertical-align:middle;border:2px solid {bd};'
                        f'background:{bg};padding:4px 2px;border-radius:6px;">'
                        f'<div style="font-size:11px;color:#555;font-weight:bold;">'
                        f'{badge}{branch_char}宮</div>'
                        f'<div style="font-size:11px;color:#444;margin-top:2px;">{palace}</div>'
                        f'<div style="font-size:14px;color:#1a237e;font-weight:bold;'
                        f'margin-top:3px;">{bird}</div>'
                        f'<div style="font-size:10px;color:#888;">{elem}行</div>'
                        f'</td>'
                    )

                # 中央格（基本資料 + 三主星 + 格局）
                _cs_center_td = (
                    '<td colspan="2" rowspan="2" style="text-align:center;'
                    'vertical-align:middle;border:2px solid #444;'
                    'background:#fffde7;padding:10px 8px;border-radius:6px;'
                    'line-height:1.6;">'
                    '<div style="font-size:15px;font-weight:bold;color:#b71c1c;'
                    'letter-spacing:2px;">萬化仙禽</div>'
                    f'<div style="font-size:11px;margin-top:6px;">'
                    f'{bi["year"]}年{bi["month"]}月{bi["day"]}日 {bi["hour"]}時</div>'
                    f'<div style="font-size:11px;">{bi["gender"]}命 {bi["day_night"]}</div>'
                    f'<div style="font-size:11px;">{bi["season"]}季 · {bi["san_yuan"]}</div>'
                    '<hr style="margin:6px 0;border-color:#ccc;">'
                    f'<div style="font-size:11px;"><b>胎星</b>：{s["tai_xing"]}</div>'
                    f'<div style="font-size:11px;"><b>命星</b>：{s["ming_xing"]}</div>'
                    f'<div style="font-size:11px;"><b>身星</b>：{s["shen_xing"]}</div>'
                    '<hr style="margin:6px 0;border-color:#ccc;">'
                    f'<div style="font-size:11px;color:#5d4037;">'
                    f'<b>格局</b>：{pat["grade"]}</div>'
                    '</td>'
                )

                # 大六壬式四列排盤
                # Row 0: 巳(5)  午(6)  未(7)  申(8)
                # Row 1: 辰(4)  [CENTER]       酉(9)
                # Row 2: 卯(3)  [CENTER]       戌(10)
                # Row 3: 寅(2)  丑(1)  子(0)  亥(11)
                _cs_br = _cs_branches
                _cs_grid = (
                    '<table style="border-collapse:separate;border-spacing:4px;'
                    'margin:10px auto;font-family:\'Noto Serif TC\',serif;">'
                    "<tr>"
                    + _cs_cell(_cs_br[5])  + _cs_cell(_cs_br[6])
                    + _cs_cell(_cs_br[7])  + _cs_cell(_cs_br[8])
                    + "</tr><tr>"
                    + _cs_cell(_cs_br[4])  + _cs_center_td + _cs_cell(_cs_br[9])
                    + "</tr><tr>"
                    + _cs_cell(_cs_br[3])  + _cs_cell(_cs_br[10])
                    + "</tr><tr>"
                    + _cs_cell(_cs_br[2])  + _cs_cell(_cs_br[1])
                    + _cs_cell(_cs_br[0])  + _cs_cell(_cs_br[11])
                    + "</tr></table>"
                )
                st.markdown(_cs_grid, unsafe_allow_html=True)
                st.divider()

                # ── 吞啗分析 ──────────────────────────────
                st.markdown(t("chinstar_swallow_analysis_header"))
                _sw = _cs_chart["swallow_analysis"]
                if _sw:
                    _sw_rows = [{"對照": k, "判斷": v} for k, v in _sw.items()]
                    st.dataframe(_sw_rows, use_container_width=True, hide_index=True)
                else:
                    st.info(t("chinstar_no_swallow"))
                st.divider()

                # ── 情性賦 ──────────────────────────────
                st.markdown(t("chinstar_personality_header"))
                for _label, text in _cs_chart["personality"].items():
                    st.info(text)
                st.divider()

                # ── 格局 ──────────────────────────────
                st.markdown(t("chinstar_pattern_header").format(grade=pat["grade"]))
                st.write(pat["reason"])

                # ── 完整文字輸出（可複製） ──────────────────────
                with st.expander(t("chinstar_full_text_expander")):
                    st.code(WanHuaXianQin.format_chart(_cs_chart), language="")

            with _cs_tab_xiangtai:
                from astro.chinstar.chinstar import lookup_xiangtai, _get_xiangtai_fu

                st.markdown(t("chinstar_xiangtai_title"))

                # 查找匹配的相胎賦
                _xt_match = lookup_xiangtai(s["ming_xing"], s["tai_xing"])
                if _xt_match:
                    st.markdown(t("chinstar_xiangtai_match").format(
                        zhu=s["ming_xing"], tai=s["tai_xing"],
                    ))
                    _xt_cols = st.columns(2)
                    with _xt_cols[0]:
                        st.metric(t("chinstar_xiangtai_xingpin"), _xt_match["xing_pin"])
                    with _xt_cols[1]:
                        st.metric(t("chinstar_xiangtai_xiji"), _xt_match["xi_ji"])
                    st.info(f'**{t("chinstar_xiangtai_desc")}**：{_xt_match["desc"]}')
                    st.success(f'**{t("chinstar_xiangtai_poem")}**：\n\n{_xt_match["poem"]}')
                else:
                    st.warning(t("chinstar_xiangtai_no_match"))

                st.divider()

                # 顯示相胎賦全覽
                with st.expander(t("chinstar_xiangtai_ref")):
                    _xt_all = _get_xiangtai_fu()
                    _xt_rows = []
                    for _xt_e in _xt_all:
                        _xt_rows.append({
                            "主星": _xt_e["zhu"],
                            "胎星": _xt_e["tai"],
                            "形品": _xt_e["xing_pin"],
                            "喜忌": _xt_e["xi_ji"],
                            "論斷": _xt_e["desc"][:50] + "…" if len(_xt_e["desc"]) > 50 else _xt_e["desc"],
                        })
                    st.dataframe(_xt_rows, use_container_width=True, hide_index=True)

            with _cs_tab_gui_jian:
                from astro.chinstar.chinstar import (
                    lookup_gui_ge, lookup_jian_ge,
                    lookup_fulu_patterns, lookup_pinjian_patterns,
                )

                # 取主要禽星（胎星、命星）
                _gj_stars = [s["tai_xing"], s["ming_xing"]]
                if s["shen_xing"] not in _gj_stars:
                    _gj_stars.append(s["shen_xing"])

                # ── 福祿上格 ──
                st.markdown(t("chinstar_fulu_title"))
                _fulu_found = False
                for _gj_star in _gj_stars:
                    _fl = lookup_fulu_patterns(_gj_star)
                    if _fl:
                        _fulu_found = True
                        for _fl_e in _fl:
                            st.success(f'**{_fl_e["name"]}**（{_fl_e["stars"]}）— {_fl_e["condition"]}')
                if not _fulu_found:
                    st.info("—")
                st.divider()

                # ── 貧賤下命 ──
                st.markdown(t("chinstar_pinjian_title"))
                _pj_found = False
                for _gj_star in _gj_stars:
                    _pj = lookup_pinjian_patterns(_gj_star)
                    if _pj:
                        _pj_found = True
                        for _pj_e in _pj:
                            st.error(f'**{_pj_e["name"]}**（{_pj_e["stars"]}）— {_pj_e["condition"]}')
                if not _pj_found:
                    st.info("—")
                st.divider()

                # ── 各星貴格 / 賤格 ──
                for _gj_star in _gj_stars:
                    st.markdown(t("chinstar_gui_for_star").format(star=_gj_star))
                    _gui = lookup_gui_ge(_gj_star)
                    if _gui:
                        _gui_rows = [{"格局": g["name"], "干支": g["ganzhi"]} for g in _gui]
                        st.dataframe(_gui_rows, use_container_width=True, hide_index=True)
                    else:
                        st.info(t("chinstar_no_gui"))

                    st.markdown(t("chinstar_jian_for_star").format(star=_gj_star))
                    _jian = lookup_jian_ge(_gj_star)
                    if _jian:
                        _jian_rows = [{"格局": j["name"], "干支": j["ganzhi"]} for j in _jian]
                        st.dataframe(_jian_rows, use_container_width=True, hide_index=True)
                    else:
                        st.info(t("chinstar_no_jian"))
                    st.divider()

            with _cs_tab_text:
                import os as _cs_os
                _txt_path = _cs_os.path.join(
                    _cs_os.path.dirname(__file__),
                    "astro", "chinstar", "新刻刘伯温万化仙禽.txt",
                )
                if _cs_os.path.exists(_txt_path):
                    with open(_txt_path, "r", encoding="utf-8") as _cs_f:
                        _cs_txt = _cs_f.read()
                    st.text_area(t("chinstar_full_text_label"), _cs_txt, height=600)
                else:
                    st.warning(t("chinstar_text_not_found"))

            # AI Analysis button for Chinstar
            _render_ai_button("tab_chinstar", _cs_chart, btn_key="chinstar")

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        if not _is_calculated:
            st.info(t("info_calc_prompt"))

elif _selected_system == "tab_contact":
    st.header(t("contact_title"))
    st.markdown(t("contact_wechat"))

    st.subheader(t("contact_other_apps"))
    _apps = [
        ("https://iching.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/ichingshifa/master/pic/iching.png"),
        ("https://kintaiyi.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kintaiyi/master/pic/Untitled-1.png"),
        ("https://kinliuren.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinliuren/master/pic/Untitled-33.png"),
        ("https://kinqimen.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinqimen/master/pic/Untitled-22.png"),
        ("https://kinwuzhao.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinwuzhao/refs/heads/main/pic/wuzhao.png"),
        ("https://kintaixuan.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/taixuanshifa/master/pic/taixuan.png"),
        ("https://kinwangji.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinwangji/main/pic/kwj.png"),
        ("https://jingjue.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/jingjue/master/pic/jingjue.png"),
        ("https://liangtouqian.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/liangtouqian/main/pic/Untitled-44.png"),
    ]
    _cols = st.columns(3)
    for _i, (_url, _img) in enumerate(_apps):
        with _cols[_i % 3]:
            st.markdown(
                f'<a href="{_url}" target="_blank"><img src="{_img}" style="max-width:100%;height:auto;margin-bottom:8px;"></a>',
                unsafe_allow_html=True,
            )

    st.image(
        "https://raw.githubusercontent.com/kentang2017/kintaiyi/master/pic/20231205113526.jpg",
        use_container_width=True,
    )
    st.markdown(t("contact_wechat_id"))
    st.markdown(t("contact_qq"))

