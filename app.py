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
from astro.vedic.varga import compute_varga_chart, VARGA_KEYS, VARGA_INFO, render_single_varga
from astro.sukkayodo import render_sukkayodo_chart
from astro.thai import (
    compute_thai_chart, render_thai_chart,
    calculate_thai_nine_grid, render_nine_grid,
    calculate_nine_palace_divination, render_nine_palace_divination,
)
from astro.brahma_jati import (
    compute_brahma_jati, render_brahma_jati, render_brahma_jati_browse,
)
from astro.kabbalistic import compute_kabbalistic_chart, render_kabbalistic_chart
from astro.arabic.arabic import compute_arabic_chart, render_arabic_chart
from astro.maya import compute_maya_chart, render_maya_chart
from astro.aztec import compute_aztec_chart, render_aztec_chart
from astro.ziwei import compute_ziwei_chart, render_ziwei_chart
from astro.mahabote import compute_mahabote_chart, render_mahabote_chart
from astro.egyptian.decans import compute_decan_chart, render_decan_chart, render_decan_browse
from astro.vedic.nadi import compute_nadi_chart, render_nadi_chart
from astro.zurkhai import compute_zurkhai_chart, render_zurkhai_chart
from astro.tibetan import compute_tibetan_chart, render_tibetan_chart, build_kalachakra_mandala_svg
from astro.western.hellenistic import compute_hellenistic_chart, render_hellenistic_chart, build_greek_horoscope_svg
from astro.babylonian import compute_babylonian_chart, render_babylonian_chart, build_babylonian_planisphere_svg
from astro.yemeni import compute_yemeni_chart, render_yemeni_chart, build_yemeni_manzil_mandala_svg
from astro.western.ptolemy_dignities import PtolemyDignityCalculator, Planet as PtolPlanet, DignityType, dignity_to_chinese, SIGN_NAMES
from astro.western.fixed_stars import compute_fixed_star_positions, find_conjunctions
from astro.western.asteroids import compute_asteroids
from astro.export import western_chart_to_dict, vedic_chart_to_dict, chinese_chart_to_dict, generic_chart_to_dict
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
    DEFAULT_SYSTEM_PROMPT,
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
from astro.arabic.ms164_browser import render_ms164_browse
from astro.chinstar.chinstar import WanHuaXianQin


# ============================================================
# 頁面設定
# ============================================================
st.set_page_config(
    page_title="堅占星 Kin Astro",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="collapsed",
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
        st.dataframe(pd.DataFrame(_dignity_rows), hide_index=True, width='stretch')

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
        st.dataframe(pd.DataFrame(_maitri_rows), hide_index=True, width='stretch')

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
        st.dataframe(pd.DataFrame(_varga_rows), hide_index=True, width='stretch')
    note = bphs_result.varga_info.get("general_note_zh", "")
    if note:
        st.caption(f"💡 {note}")


st.title(t("app_title"))
st.markdown(
    '<p class="app-subtitle">' + t("app_subtitle") + '</p>',
    unsafe_allow_html=True,
)

# ============================================================
# 世界城市資料 (城市, 緯度, 經度, 時區)
# ============================================================
# Internal keys are Chinese; CITY_NAMES_EN maps them to English display names.
# 預設城市：香港
CITY_PRESETS = {
    "香港": (22.3193, 114.1694, 8.0),
    "北京": (39.9042, 116.4074, 8.0),
    "上海": (31.2304, 121.4737, 8.0),
    "台北": (25.0330, 121.5654, 8.0),
    "高雄": (22.6273, 120.3014, 8.0),
    "台中": (24.1477, 120.6736, 8.0),
    "台南": (22.9999, 120.2269, 8.0),
    "新北": (25.0120, 121.4657, 8.0),
    "桃園": (24.9936, 121.3010, 8.0),
    "新竹": (24.8138, 120.9675, 8.0),
    "基隆": (25.1276, 121.7392, 8.0),
    "嘉義": (23.4801, 120.4491, 8.0),
    "花蓮": (23.9910, 121.6108, 8.0),
    "屏東": (22.6762, 120.4929, 8.0),
    "宜蘭": (24.7570, 121.7533, 8.0),
    "彰化": (24.0518, 120.5161, 8.0),
    "苗栗": (24.5602, 120.8214, 8.0),
    "南投": (23.9061, 120.6942, 8.0),
    "雲林": (23.7092, 120.4313, 8.0),
    "台東": (22.7583, 121.1444, 8.0),
    "澎湖": (23.5711, 119.5793, 8.0),
    "廣州": (23.1291, 113.2644, 8.0),
    "深圳": (22.5431, 114.0579, 8.0),
    "澳門": (22.1987, 113.5439, 8.0),
    "成都": (30.5728, 104.0668, 8.0),
    "重慶": (29.4316, 106.9123, 8.0),
    "武漢": (30.5928, 114.3055, 8.0),
    "南京": (32.0603, 118.7969, 8.0),
    "杭州": (30.2741, 120.1551, 8.0),
    "西安": (34.3416, 108.9398, 8.0),
    "昆明": (25.0389, 102.7183, 8.0),
    "拉薩": (29.6500, 91.1000, 8.0),
    "烏魯木齊": (43.8256, 87.6168, 8.0),
    "天津": (39.3434, 117.3616, 8.0),
    "瀋陽": (41.8057, 123.4315, 8.0),
    "大連": (38.9140, 121.6147, 8.0),
    "哈爾濱": (45.8038, 126.5350, 8.0),
    "長春": (43.8171, 125.3235, 8.0),
    "濟南": (36.6512, 116.9972, 8.0),
    "青島": (36.0671, 120.3826, 8.0),
    "鄭州": (34.7466, 113.6254, 8.0),
    "長沙": (28.2282, 112.9388, 8.0),
    "福州": (26.0745, 119.2965, 8.0),
    "廈門": (24.4798, 118.0894, 8.0),
    "南昌": (28.6820, 115.8579, 8.0),
    "合肥": (31.8206, 117.2272, 8.0),
    "貴陽": (26.6470, 106.6302, 8.0),
    "南寧": (22.8170, 108.3665, 8.0),
    "海口": (20.0174, 110.3492, 8.0),
    "蘭州": (36.0611, 103.8343, 8.0),
    "太原": (37.8706, 112.5489, 8.0),
    "呼和浩特": (40.8424, 111.7490, 8.0),
    "石家莊": (38.0428, 114.5149, 8.0),
    "銀川": (38.4872, 106.2309, 8.0),
    "西寧": (36.6171, 101.7782, 8.0),
    "蘇州": (31.2990, 120.5853, 8.0),
    "無錫": (31.4906, 120.3119, 8.0),
    "寧波": (29.8683, 121.5440, 8.0),
    "溫州": (28.0000, 120.6500, 8.0),
    "珠海": (22.2710, 113.5767, 8.0),
    "佛山": (23.0218, 113.1218, 8.0),
    "東莞": (23.0208, 113.7518, 8.0),
    "東京": (35.6762, 139.6503, 9.0),
    "大阪": (34.6937, 135.5023, 9.0),
    "京都": (35.0116, 135.7681, 9.0),
    "首爾": (37.5665, 126.9780, 9.0),
    "釜山": (35.1796, 129.0756, 9.0),
    "新加坡": (1.3521, 103.8198, 8.0),
    "吉隆坡": (3.1390, 101.6869, 8.0),
    "曼谷": (13.7563, 100.5018, 7.0),
    "清邁": (18.7883, 98.9853, 7.0),
    "河內": (21.0278, 105.8342, 7.0),
    "胡志明市": (10.8231, 106.6297, 7.0),
    "雅加達": ((-6.2088), 106.8456, 7.0),
    "馬尼拉": (14.5995, 120.9842, 8.0),
    "金邊": (11.5564, 104.9282, 7.0),
    "仰光": (16.8661, 96.1951, 6.5),
    "新德里": (28.6139, 77.2090, 5.5),
    "孟買": (19.0760, 72.8777, 5.5),
    "加爾各答": (22.5726, 88.3639, 5.5),
    "班加羅爾": (12.9716, 77.5946, 5.5),
    "清奈": (13.0827, 80.2707, 5.5),
    "可倫坡": (6.9271, 79.8612, 5.5),
    "加德滿都": (27.7172, 85.3240, 5.75),
    "達卡": (23.8103, 90.4125, 6.0),
    "伊斯蘭堡": (33.6844, 73.0479, 5.0),
    "卡拉奇": (24.8607, 67.0011, 5.0),
    "喀布爾": (34.5553, 69.2075, 4.5),
    "德黑蘭": (35.6892, 51.3890, 3.5),
    "巴格達": (33.3152, 44.3661, 3.0),
    "利雅得": (24.7136, 46.6753, 3.0),
    "杜拜": (25.2048, 55.2708, 4.0),
    "多哈": (25.2854, 51.5310, 3.0),
    "安卡拉": (39.9334, 32.8597, 3.0),
    "伊斯坦堡": (41.0082, 28.9784, 3.0),
    "耶路撒冷": (31.7683, 35.2137, 2.0),
    "開羅": (30.0444, 31.2357, 2.0),
    "奈洛比": ((-1.2921), 36.8219, 3.0),
    "約翰尼斯堡": ((-26.2041), 28.0473, 2.0),
    "開普敦": ((-33.9249), 18.4241, 2.0),
    "拉哥斯": (6.5244, 3.3792, 1.0),
    "阿克拉": (5.6037, (-0.1870), 0.0),
    "卡薩布蘭卡": (33.5731, (-7.5898), 1.0),
    "烏蘭巴托": (47.9077, 106.8832, 8.0),
    "莫斯科": (55.7558, 37.6173, 3.0),
    "聖彼得堡": (59.9343, 30.3351, 3.0),
    "倫敦": (51.5074, (-0.1278), 0.0),
    "巴黎": (48.8566, 2.3522, 1.0),
    "柏林": (52.5200, 13.4050, 1.0),
    "羅馬": (41.9028, 12.4964, 1.0),
    "馬德里": (40.4168, (-3.7038), 1.0),
    "里斯本": (38.7223, (-9.1393), 0.0),
    "阿姆斯特丹": (52.3676, 4.9041, 1.0),
    "布魯塞爾": (50.8503, 4.3517, 1.0),
    "維也納": (48.2082, 16.3738, 1.0),
    "蘇黎世": (47.3769, 8.5417, 1.0),
    "斯德哥爾摩": (59.3293, 18.0686, 1.0),
    "奧斯陸": (59.9139, 10.7522, 1.0),
    "哥本哈根": (55.6761, 12.5683, 1.0),
    "赫爾辛基": (60.1699, 24.9384, 2.0),
    "華沙": (52.2297, 21.0122, 1.0),
    "布拉格": (50.0755, 14.4378, 1.0),
    "布達佩斯": (47.4979, 19.0402, 1.0),
    "雅典": (37.9838, 23.7275, 2.0),
    "都柏林": (53.3498, (-6.2603), 0.0),
    "紐約": (40.7128, (-74.0060), -5.0),
    "洛杉磯": (34.0522, (-118.2437), -8.0),
    "芝加哥": (41.8781, (-87.6298), -6.0),
    "休斯頓": (29.7604, (-95.3698), -6.0),
    "舊金山": (37.7749, (-122.4194), -8.0),
    "華盛頓": (38.9072, (-77.0369), -5.0),
    "多倫多": (43.6532, (-79.3832), -5.0),
    "溫哥華": (49.2827, (-123.1207), -8.0),
    "蒙特利爾": (45.5017, (-73.5673), -5.0),
    "墨西哥城": (19.4326, (-99.1332), -6.0),
    "哈瓦那": (23.1136, (-82.3666), -5.0),
    "波哥大": (4.7110, (-74.0721), -5.0),
    "利馬": ((-12.0464), (-77.0428), -5.0),
    "聖保羅": ((-23.5505), (-46.6333), -3.0),
    "里約熱內盧": ((-22.9068), (-43.1729), -3.0),
    "布宜諾斯艾利斯": ((-34.6037), (-58.3816), -3.0),
    "聖地亞哥": ((-33.4489), (-70.6693), -4.0),
    "悉尼": ((-33.8688), 151.2093, 10.0),
    "墨爾本": ((-37.8136), 144.9631, 10.0),
    "奧克蘭": ((-36.8485), 174.7633, 12.0),
    "檀香山": (21.3069, (-157.8583), -10.0),
    "自訂": (0.0, 0.0, 0.0),
}

CITY_NAMES_EN = {
    "香港": "Hong Kong",
    "北京": "Beijing",
    "上海": "Shanghai",
    "台北": "Taipei",
    "高雄": "Kaohsiung",
    "台中": "Taichung",
    "台南": "Tainan",
    "新北": "New Taipei",
    "桃園": "Taoyuan",
    "新竹": "Hsinchu",
    "基隆": "Keelung",
    "嘉義": "Chiayi",
    "花蓮": "Hualien",
    "屏東": "Pingtung",
    "宜蘭": "Yilan",
    "彰化": "Changhua",
    "苗栗": "Miaoli",
    "南投": "Nantou",
    "雲林": "Yunlin",
    "台東": "Taitung",
    "澎湖": "Penghu",
    "廣州": "Guangzhou",
    "深圳": "Shenzhen",
    "澳門": "Macau",
    "成都": "Chengdu",
    "重慶": "Chongqing",
    "武漢": "Wuhan",
    "南京": "Nanjing",
    "杭州": "Hangzhou",
    "西安": "Xi'an",
    "昆明": "Kunming",
    "拉薩": "Lhasa",
    "烏魯木齊": "Urumqi",
    "天津": "Tianjin",
    "瀋陽": "Shenyang",
    "大連": "Dalian",
    "哈爾濱": "Harbin",
    "長春": "Changchun",
    "濟南": "Jinan",
    "青島": "Qingdao",
    "鄭州": "Zhengzhou",
    "長沙": "Changsha",
    "福州": "Fuzhou",
    "廈門": "Xiamen",
    "南昌": "Nanchang",
    "合肥": "Hefei",
    "貴陽": "Guiyang",
    "南寧": "Nanning",
    "海口": "Haikou",
    "蘭州": "Lanzhou",
    "太原": "Taiyuan",
    "呼和浩特": "Hohhot",
    "石家莊": "Shijiazhuang",
    "銀川": "Yinchuan",
    "西寧": "Xining",
    "蘇州": "Suzhou",
    "無錫": "Wuxi",
    "寧波": "Ningbo",
    "溫州": "Wenzhou",
    "珠海": "Zhuhai",
    "佛山": "Foshan",
    "東莞": "Dongguan",
    "東京": "Tokyo",
    "大阪": "Osaka",
    "京都": "Kyoto",
    "首爾": "Seoul",
    "釜山": "Busan",
    "新加坡": "Singapore",
    "吉隆坡": "Kuala Lumpur",
    "曼谷": "Bangkok",
    "清邁": "Chiang Mai",
    "河內": "Hanoi",
    "胡志明市": "Ho Chi Minh City",
    "雅加達": "Jakarta",
    "馬尼拉": "Manila",
    "金邊": "Phnom Penh",
    "仰光": "Yangon",
    "新德里": "New Delhi",
    "孟買": "Mumbai",
    "加爾各答": "Kolkata",
    "班加羅爾": "Bangalore",
    "清奈": "Chennai",
    "可倫坡": "Colombo",
    "加德滿都": "Kathmandu",
    "達卡": "Dhaka",
    "伊斯蘭堡": "Islamabad",
    "卡拉奇": "Karachi",
    "喀布爾": "Kabul",
    "德黑蘭": "Tehran",
    "巴格達": "Baghdad",
    "利雅得": "Riyadh",
    "杜拜": "Dubai",
    "多哈": "Doha",
    "安卡拉": "Ankara",
    "伊斯坦堡": "Istanbul",
    "耶路撒冷": "Jerusalem",
    "開羅": "Cairo",
    "奈洛比": "Nairobi",
    "約翰尼斯堡": "Johannesburg",
    "開普敦": "Cape Town",
    "拉哥斯": "Lagos",
    "阿克拉": "Accra",
    "卡薩布蘭卡": "Casablanca",
    "烏蘭巴托": "Ulaanbaatar",
    "莫斯科": "Moscow",
    "聖彼得堡": "Saint Petersburg",
    "倫敦": "London",
    "巴黎": "Paris",
    "柏林": "Berlin",
    "羅馬": "Rome",
    "馬德里": "Madrid",
    "里斯本": "Lisbon",
    "阿姆斯特丹": "Amsterdam",
    "布魯塞爾": "Brussels",
    "維也納": "Vienna",
    "蘇黎世": "Zurich",
    "斯德哥爾摩": "Stockholm",
    "奧斯陸": "Oslo",
    "哥本哈根": "Copenhagen",
    "赫爾辛基": "Helsinki",
    "華沙": "Warsaw",
    "布拉格": "Prague",
    "布達佩斯": "Budapest",
    "雅典": "Athens",
    "都柏林": "Dublin",
    "紐約": "New York",
    "洛杉磯": "Los Angeles",
    "芝加哥": "Chicago",
    "休斯頓": "Houston",
    "舊金山": "San Francisco",
    "華盛頓": "Washington D.C.",
    "多倫多": "Toronto",
    "溫哥華": "Vancouver",
    "蒙特利爾": "Montreal",
    "墨西哥城": "Mexico City",
    "哈瓦那": "Havana",
    "波哥大": "Bogota",
    "利馬": "Lima",
    "聖保羅": "São Paulo",
    "里約熱內盧": "Rio de Janeiro",
    "布宜諾斯艾利斯": "Buenos Aires",
    "聖地亞哥": "Santiago",
    "悉尼": "Sydney",
    "墨爾本": "Melbourne",
    "奧克蘭": "Auckland",
    "檀香山": "Honolulu",
    "自訂": "Custom",
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
        input_lat = preset_lat
        input_lon = preset_lon
        input_tz = preset_tz
        location_name = CITY_NAMES_EN[city] if st.session_state.get("lang") == "en" else city
    else:
        input_lat = st.number_input(
            t("latitude"), value=22.3193, format="%.4f",
            min_value=-90.0, max_value=90.0,
        )
        input_lon = st.number_input(
            t("longitude"), value=114.1694, format="%.4f",
            min_value=-180.0, max_value=180.0,
        )
        input_tz = st.number_input(
            t("timezone"), value=8.0, format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
        )
        location_name = t("custom_location")

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

    # ── Astrology system selector (categorised for beginners) ──
    st.divider()
    st.markdown(
        f'<div class="sidebar-system-title">🌐 {t("sidebar_system_label")}</div>',
        unsafe_allow_html=True,
    )

    # Categorised system layout for easier navigation
    _SYSTEM_CATEGORIES = [
        ("cat_popular", ["tab_western", "tab_ziwei"]),
        ("cat_chinese", ["tab_chinese", "tab_chinstar"]),
        ("cat_western", ["tab_hellenistic", "tab_kabbalistic"]),
        ("cat_asian", ["tab_indian", "tab_nadi", "tab_sukkayodo", "tab_thai", "tab_mahabote", "tab_zurkhai", "tab_tibetan"]),
        ("cat_middle_east", ["tab_arabic", "tab_yemeni"]),
        ("cat_ancient", ["tab_maya", "tab_aztec", "tab_decans", "tab_babylonian"]),
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
        "tab_yemeni": t("tab_yemeni"),
        "tab_maya": t("tab_maya"),
        "tab_aztec": t("tab_aztec"),
        "tab_mahabote": t("tab_mahabote"),
        "tab_decans": t("tab_decans"),
        "tab_nadi": t("tab_nadi"),
        "tab_zurkhai": t("tab_zurkhai"),
        "tab_tibetan": t("tab_tibetan"),
        "tab_hellenistic": t("tab_hellenistic"),
        "tab_babylonian": t("tab_babylonian"),
        "tab_chinstar": t("tab_chinstar"),
    }

    # Short hints for each system (beginner-friendly)
    _SYSTEM_HINTS = {
        "tab_western": t("sys_hint_western"),
        "tab_ziwei": t("sys_hint_ziwei"),
        "tab_chinese": t("sys_hint_chinese"),
        "tab_indian": t("sys_hint_indian"),
        "tab_thai": t("sys_hint_thai"),
        "tab_kabbalistic": t("sys_hint_kabbalistic"),
        "tab_arabic": t("sys_hint_arabic"),
        "tab_yemeni": t("sys_hint_yemeni"),
        "tab_maya": t("sys_hint_maya"),
        "tab_aztec": t("sys_hint_aztec"),
        "tab_mahabote": t("sys_hint_mahabote"),
        "tab_decans": t("sys_hint_decans"),
        "tab_nadi": t("sys_hint_nadi"),
        "tab_zurkhai": t("sys_hint_zurkhai"),
        "tab_tibetan": t("sys_hint_tibetan"),
        "tab_hellenistic": t("sys_hint_hellenistic"),
        "tab_babylonian": t("sys_hint_babylonian"),
        "tab_sukkayodo": t("sys_hint_sukkayodo"),
        "tab_chinstar": t("sys_hint_chinstar"),
    }

    _BEGINNER_SYSTEMS = {"tab_western", "tab_ziwei"}
    _cur_lang = st.session_state.get("lang", "zh")

    # Resolve current selection
    if "_system_select" not in st.session_state:
        st.session_state["_system_select"] = "tab_western"
    _selected_system = st.session_state["_system_select"]

    # Render categorised buttons
    for _cat_key, _cat_systems in _SYSTEM_CATEGORIES:
        st.markdown(f'<div class="sidebar-cat">{t(_cat_key)}</div>', unsafe_allow_html=True)
        for _sk in _cat_systems:
            _is_active = (_sk == _selected_system)
            _btn_type = "primary" if _is_active else "secondary"
            _badge = ""
            if _sk in _BEGINNER_SYSTEMS:
                _badge_text = "推薦" if _cur_lang == "zh" else "Start here"
                _badge = f' <span class="beginner-badge">{_badge_text}</span>'
            if st.button(
                _SYSTEM_LABELS[_sk],
                key=f"_sys_btn_{_sk}",
                use_container_width=True,
                type=_btn_type,
                help=_SYSTEM_HINTS.get(_sk, ""),
            ):
                st.session_state["_system_select"] = _sk
                _selected_system = _sk
                st.rerun()

    # ── AI Analysis settings ──────────────────────────────────
    st.divider()
    with st.expander(t("ai_settings_header"), expanded=False):

        _ai_model = st.selectbox(
            t("ai_model_label"),
            options=CEREBRAS_MODEL_OPTIONS,
            index=0,
            key="_ai_model_select",
            help="\n".join(f"• {k}: {v}" for k, v in CEREBRAS_MODEL_DESCRIPTIONS.items()),
        )

        # Use the hardcoded default system prompt (no user editing)
        st.session_state.ai_system_prompt = DEFAULT_SYSTEM_PROMPT

        # Max tokens & temperature
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

    # ── About / Contact section (always visible at sidebar bottom) ──
    st.divider()
    with st.expander(t("tab_contact"), expanded=False):
        st.subheader(t("contact_title"))
        st.markdown(t("contact_wechat"))
        st.markdown(t("contact_wechat_id"))
        st.markdown(t("contact_qq"))
        st.subheader(t("contact_other_apps"))
        _contact_apps = [
            ("https://iching.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/ichingshifa/master/pic/iching.png"),
            ("https://kintaiyi.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kintaiyi/master/pic/Untitled-1.png"),
            ("https://kinliuren.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinliuren/master/pic/Untitled-33.png"),
            ("https://kinqimen.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinqimen/master/pic/Untitled-22.png"),
            ("https://kinwuzhao.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinwuzhao/refs/heads/main/pic/wuzhao.png"),
            ("https://kintaixuan.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/taixuanshifa/master/pic/taixuan.png"),
            ("https://kinwangji.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/kinwangji/refs/heads/main/pic/kwj.png"),
            ("https://jingjue.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/jingjue/master/pic/jingjue.png"),
            ("https://liangtouqian.streamlit.app/", "https://raw.githubusercontent.com/kentang2017/liangtouqian/main/pic/Untitled-44.png"),
        ]
        _contact_cols = st.columns(3)
        for _ci, (_curl, _cimg) in enumerate(_contact_apps):
            with _contact_cols[_ci % 3]:
                st.markdown(
                    f'<a href="{_curl}" target="_blank"><img src="{_cimg}" style="max-width:100%;height:auto;margin-bottom:8px;"></a>',
                    unsafe_allow_html=True,
                )
        st.image(
            "https://raw.githubusercontent.com/kentang2017/kintaiyi/master/pic/20231205113526.jpg",
            width='stretch',
        )

# ============================================================
# AI Analysis helper — reusable across all system tabs
# ============================================================

def _render_ai_button(system_key: str, chart_obj, btn_key: str = "",
                      page_content: str = ""):
    """Render the AI analysis button and execute the analysis when clicked.

    Parameters
    ----------
    system_key : str
        The system tab key (e.g. ``"tab_western"``).
    chart_obj : object
        The chart object produced by the compute function.
    btn_key : str
        Optional unique key suffix for the button widget.
    page_content : str
        Optional extra text content rendered on the page that should also
        be included in the AI analysis prompt.
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
                chart_prompt = format_chart_for_prompt(
                    system_key, chart_obj, page_content=page_content,
                )
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
# Welcome / Onboarding Section for Beginners
# 歡迎頁面 — 為初學者提供引導
# ============================================================

def _render_welcome():
    """Render a welcoming onboarding section for new users."""
    st.markdown(
        f'<div class="welcome-hero">'
        f'<h2>{t("welcome_hero_title")}</h2>'
        f'<p>{t("welcome_hero_body")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    _steps = [
        ("1️⃣", t("welcome_step1_title"), t("welcome_step1_body")),
        ("2️⃣", t("welcome_step2_title"), t("welcome_step2_body")),
        ("3️⃣", t("welcome_step3_title"), t("welcome_step3_body")),
    ]
    _cards_html = '<div class="step-row">'
    for _i, (_icon, _title, _body) in enumerate(_steps):
        _cards_html += (
            f'<div class="step-card">'
            f'<div class="step-num">{_i + 1}</div>'
            f'<h4>{_icon} {_title}</h4>'
            f'<p>{_body}</p>'
            f'</div>'
        )
    _cards_html += '</div>'
    st.markdown(_cards_html, unsafe_allow_html=True)

    st.info(t("welcome_quick_start"))


# ============================================================
# Main Area — Render the selected astrology system
# 主區域 — 根據側邊欄選擇顯示對應占星體系
# ============================================================

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

_is_calculated = True

# ── Show welcome onboarding for first-time visitors ────────────
if "_has_seen_welcome" not in st.session_state:
    _render_welcome()
    st.session_state["_has_seen_welcome"] = True

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
                # 計算流時盤 for overlay
                _transit_now = compute_transit_now(timezone=input_tz)

                # 選擇是否顯示流時對盤
                _show_transit_overlay = st.checkbox(
                    t("show_transit_overlay"), value=False,
                )
                _transit_for_ring = _transit_now if _show_transit_overlay else None

                render_mansion_ring(chart, transit=_transit_for_ring)
                _render_ai_button("tab_chinese", chart, btn_key="chinese")
                st.divider()
                render_chart_info(chart)
                st.divider()
                render_bazi(chart)
                st.divider()
                render_planet_table(chart)
                st.divider()
                render_house_table(chart)
                st.divider()
                render_aspect_summary(chart)

            with _ch_tab_shensha:
                _shensha = compute_shensha(
                    year=chart.year,
                    solar_month=chart.solar_month,
                    julian_day=chart.julian_day,
                    hour_branch=chart.hour_branch,
                    timezone=chart.timezone,
                    ming_gong_branch=chart.ming_gong_branch,
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
            _gender = st.session_state.get("_calc_gender", "男")
            with st.spinner(t("spinner_ziwei")):
                zw_chart = compute_ziwei_chart(**_p, gender=_gender)
            render_ziwei_chart(zw_chart, after_chart_hook=lambda: _render_ai_button("tab_ziwei", zw_chart, btn_key="ziwei"))
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
                _w_gender = st.session_state.get("_calc_gender")
                # Pre-compute natal summary so it can be included in AI analysis
                _summary = generate_natal_summary(
                    w_chart.planets, w_chart.houses,
                    getattr(w_chart, 'asc_sign', ''),
                    lang=get_lang(),
                )
                render_western_chart(
                    w_chart,
                    after_chart_hook=lambda: _render_ai_button(
                        "tab_western", w_chart,
                        btn_key="western", page_content=_summary,
                    ),
                    gender=_w_gender,
                )
                # Natal summary
                with st.expander(t("natal_summary_header"), expanded=True):
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

            _v_tab_rashi, _v_tab_dasha, _v_tab_ashtaka, _v_tab_yogas, _v_tab_bphs, _v_tab_varga = st.tabs([
                t("vedic_subtab_rashi"),
                t("vedic_subtab_dasha"),
                t("vedic_subtab_ashtaka"),
                t("vedic_subtab_yogas"),
                t("vedic_subtab_bphs"),
                t("vedic_subtab_varga"),
            ])

            with _v_tab_rashi:
                render_vedic_chart(v_chart, after_chart_hook=lambda: _render_ai_button("tab_indian", v_chart, btn_key="vedic"))

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

            with _v_tab_varga:
                st.subheader("📊 " + t("vedic_subtab_varga"))
                st.caption("根據 BPHS 第9章：Shodasa Varga 分盤系統 — 選擇分盤查看行星在各分盤中的位置")
                _varga_tab_labels = [f"{k} {VARGA_INFO[k]['zh']}" for k in VARGA_KEYS]
                _varga_tabs = st.tabs(_varga_tab_labels)
                for _vi, _vk in enumerate(VARGA_KEYS):
                    with _varga_tabs[_vi]:
                        _vc = compute_varga_chart(_vk, v_chart.planets, v_chart.ascendant)
                        render_single_varga(_vc)

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
            with st.spinner(t("spinner_indian")):
                _v_chart_sukka = compute_vedic_chart(**_p)
            render_sukkayodo_chart(_v_chart_sukka, after_chart_hook=lambda: _render_ai_button("tab_sukkayodo", _v_chart_sukka, btn_key="sukkayodo"))
            st.subheader(t("sukkayodo_subheader"))
            st.info(t("sukkayodo_info"))
            st.markdown(t("desc_sukkayodo"))
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
            thai_tab_chart, thai_tab_nine, thai_tab_brahma = st.tabs(
                [t("thai_subtab_chart"), t("thai_subtab_nine"), t("thai_subtab_brahma")]
            )
            with thai_tab_chart:
                render_thai_chart(t_chart, after_chart_hook=lambda: _render_ai_button("tab_thai", t_chart, btn_key="thai"))
            with thai_tab_nine:
                nine_grid_result = calculate_thai_nine_grid(
                    birth_date.day, birth_date.month, birth_date.year
                )
                render_nine_grid(nine_grid_result)
                st.markdown("---")
                divination_result = calculate_nine_palace_divination(t_chart)
                render_nine_palace_divination(divination_result)
            with thai_tab_brahma:
                from datetime import date as _date_cls
                _bj_bd = _date_cls(birth_date.year, birth_date.month, birth_date.day)
                _bj_weekday = _bj_bd.weekday()  # 0=Mon … 6=Sun
                _bj_age = None
                _bj_gender = None
                _bj_age_col, _bj_gender_col = st.columns(2)
                with _bj_age_col:
                    _bj_age = st.number_input(
                        "年齡 (Age)", min_value=1, max_value=120,
                        value=max(1, _date_cls.today().year - birth_date.year),
                        key="brahma_jati_age",
                    )
                with _bj_gender_col:
                    _bj_gender = st.selectbox(
                        "性別 (Gender)",
                        options=["male", "female"],
                        format_func=lambda x: "男 Male" if x == "male" else "女 Female",
                        key="brahma_jati_gender",
                    )
                _bj_reading = compute_brahma_jati(
                    ce_year=birth_date.year,
                    month=birth_date.month,
                    weekday=_bj_weekday,
                    age=_bj_age,
                    gender=_bj_gender,
                )
                render_brahma_jati(_bj_reading)
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_thai"))
        render_brahma_jati_browse()

# --- 卡巴拉占星 ---
elif _selected_system == "tab_kabbalistic":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_kabbalistic")):
                k_chart = compute_kabbalistic_chart(**_p)
            render_kabbalistic_chart(k_chart, after_chart_hook=lambda: _render_ai_button("tab_kabbalistic", k_chart, btn_key="kabbalistic"))
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
            arabic_subtab_chart, arabic_subtab_picatrix, arabic_subtab_shams, arabic_subtab_ref, arabic_subtab_ms164 = st.tabs([
                t("arabic_subtab_chart"),
                t("arabic_subtab_picatrix"),
                t("arabic_subtab_shams"),
                t("arabic_subtab_reference"),
                t("arabic_subtab_ms164"),
            ])

            with arabic_subtab_chart:
                with st.spinner(t("spinner_arabic")):
                    a_chart = compute_arabic_chart(**_p)
                render_arabic_chart(a_chart, after_chart_hook=lambda: _render_ai_button("tab_arabic", a_chart, btn_key="arabic"))

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

            with arabic_subtab_ms164:
                render_ms164_browse()

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        arabic_subtab_chart, arabic_subtab_picatrix, arabic_subtab_shams, arabic_subtab_ref, arabic_subtab_ms164 = st.tabs([
            t("arabic_subtab_chart"),
            t("arabic_subtab_picatrix"),
            t("arabic_subtab_shams"),
            t("arabic_subtab_reference"),
            t("arabic_subtab_ms164"),
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

        with arabic_subtab_ms164:
            render_ms164_browse()

# --- 也門占星 (Yemeni) ---
elif _selected_system == "tab_yemeni":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_yemeni")):
                _yemeni_chart = compute_yemeni_chart(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    timezone=_p["timezone"],
                    latitude=_p["latitude"], longitude=_p["longitude"],
                    location_name=location_name,
                )
            _y_tab_mandala, _y_tab_natal, _y_tab_omens = st.tabs([
                t("yemeni_subtab_mandala"),
                t("yemeni_subtab_natal"),
                t("yemeni_subtab_omens"),
            ])
            with _y_tab_mandala:
                _yemeni_svg = build_yemeni_manzil_mandala_svg(
                    _yemeni_chart,
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    tz=input_tz,
                    location=location_name,
                )
                st.markdown(_yemeni_svg, unsafe_allow_html=True)
                st.caption(
                    '<p style="text-align:center; color:#888; font-size:11px;">'
                    'Yemeni Manzil Mandala — 28-mansion disc · '
                    'Rasulid manuscript style · Sidereal zodiac'
                    '</p>',
                    unsafe_allow_html=True,
                )
                _render_ai_button("tab_yemeni", _yemeni_chart, btn_key="yemeni")
            with _y_tab_natal:
                render_yemeni_chart(_yemeni_chart)
            with _y_tab_omens:
                st.subheader("📜 al-Ashraf " + t("yemeni_subtab_omens"))
                for _omen in _yemeni_chart.omens:
                    _omen_icon = "🌟" if _omen.condition == "strong" else "⚠️"
                    st.markdown(
                        f"{_omen_icon} **{_omen.planet}** ({_omen.planet_cn}) — "
                        f"*{_omen.condition.upper()}*: {_omen.text} / {_omen.text_en}"
                    )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_yemeni"))

# --- 瑪雅占星 ---
elif _selected_system == "tab_maya":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_maya")):
                m_chart = compute_maya_chart(**_p)
            render_maya_chart(m_chart, after_chart_hook=lambda: _render_ai_button("tab_maya", m_chart, btn_key="maya"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_maya"))

# --- 阿茲特克占星 ---
elif _selected_system == "tab_aztec":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_aztec")):
                az_chart = compute_aztec_chart(**_p)
            render_aztec_chart(az_chart, after_chart_hook=lambda: _render_ai_button("tab_aztec", az_chart, btn_key="aztec"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_aztec"))

# --- 緬甸占星 (Mahabote) ---
elif _selected_system == "tab_mahabote":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_mahabote")):
                mb_chart = compute_mahabote_chart(**_p)
            render_mahabote_chart(mb_chart, after_chart_hook=lambda: _render_ai_button("tab_mahabote", mb_chart, btn_key="mahabote"))
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
            render_nadi_chart(nadi_chart, after_chart_hook=lambda: _render_ai_button("tab_nadi", nadi_chart, btn_key="nadi"))
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
            render_zurkhai_chart(zk_chart, after_chart_hook=lambda: _render_ai_button("tab_zurkhai", zk_chart, btn_key="zurkhai"))
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_zurkhai"))

# --- 藏傳時輪金剛占星 (Tibetan Kalachakra) ---
elif _selected_system == "tab_tibetan":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            _g = st.session_state["_calc_gender"]
            with st.spinner(t("spinner_tibetan")):
                _tib_chart = compute_tibetan_chart(**_p, gender=_g)
            _t_tab_mandala, _t_tab_natal, _t_tab_mewa, _t_tab_forces, _t_tab_planets = st.tabs([
                t("tibetan_subtab_mandala"),
                t("tibetan_subtab_natal"),
                t("tibetan_subtab_mewa"),
                t("tibetan_subtab_forces"),
                t("tibetan_subtab_planets"),
            ])
            with _t_tab_mandala:
                _tib_svg = build_kalachakra_mandala_svg(
                    _tib_chart,
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    tz=input_tz,
                    location=location_name,
                )
                st.markdown(_tib_svg, unsafe_allow_html=True)
                st.caption(
                    '<p style="text-align:center;color:#888;font-size:11px;">'
                    'Kalachakra Mandala · 時輪金剛曼荼羅 · '
                    'Outer: 12 Animals · Middle: 8 Parkha · Inner: 9 Mewa'
                    '</p>',
                    unsafe_allow_html=True,
                )
                _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_mandala")
            with _t_tab_natal:
                render_tibetan_chart(_tib_chart, after_chart_hook=lambda: _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_natal"))
            with _t_tab_mewa:
                from astro.tibetan import _render_mewa_parkha
                _render_mewa_parkha(_tib_chart)
                _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_mewa")
            with _t_tab_forces:
                from astro.tibetan import _render_five_forces
                _render_five_forces(_tib_chart)
                _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_forces")
            with _t_tab_planets:
                from astro.tibetan import _render_planets
                _render_planets(_tib_chart)
                _render_ai_button("tab_tibetan", _tib_chart, btn_key="tibetan_planets")
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_tibetan"))

# --- 希臘占星 (Hellenistic) ---
elif _selected_system == "tab_hellenistic":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
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
                _render_ai_button("tab_hellenistic", _hellen_chart, btn_key="hellenistic")
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

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_hellenistic"))

# --- 古巴比倫占星 (Babylonian) ---
elif _selected_system == "tab_babylonian":
    if _is_calculated:
        try:
            _p = st.session_state["_calc_params"]
            with st.spinner(t("spinner_babylonian")):
                _bab_chart = compute_babylonian_chart(
                    year=_p["year"], month=_p["month"], day=_p["day"],
                    hour=_p["hour"], minute=_p["minute"],
                    timezone=_p["timezone"],
                    lat=_p["latitude"], lon=_p["longitude"],
                )
            _bab_tab_chart, _bab_tab_natal, _bab_tab_omens = st.tabs([
                t("babylonian_subtab_chart"),
                t("babylonian_subtab_natal"),
                t("babylonian_subtab_omens"),
            ])
            with _bab_tab_chart:
                _bab_svg = build_babylonian_planisphere_svg(
                    _bab_chart,
                    year=birth_date.year,
                    month=birth_date.month,
                    day=birth_date.day,
                    hour=birth_time.hour,
                    minute=birth_time.minute,
                    tz=input_tz,
                    location=location_name,
                )
                st.markdown(_bab_svg, unsafe_allow_html=True)
                st.caption(
                    '<p style="text-align:center; color:#888; font-size:11px;">'
                    'Babylonian Planisphere (K.8538 style) — 8-sector clay disc · '
                    'Sidereal zodiac · MUL.APIN sign names'
                    '</p>',
                    unsafe_allow_html=True,
                )
                _render_ai_button("tab_babylonian", _bab_chart, btn_key="babylonian")
            with _bab_tab_natal:
                render_babylonian_chart(_bab_chart)
            with _bab_tab_omens:
                st.subheader("📜 Enūma Anu Enlil " + t("babylonian_subtab_omens"))
                for _omen in _bab_chart.omens:
                    _omen_icon = "🌟" if _omen.condition == "strong" else "⚠️"
                    st.markdown(
                        f"{_omen_icon} **{_omen.planet}** ({_omen.god_name}) — "
                        f"*{_omen.condition.upper()}*: {_omen.text}"
                    )
        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        st.info(t("info_calc_prompt"))
        st.markdown(t("desc_babylonian"))

# --- 萬化仙禽 (WanHua XianQin) ---
elif _selected_system == "tab_chinstar":

    # ── Lunar date conversion (hidden) ──────────────────────────
    _chinstar_year = birth_date.year
    _chinstar_month = birth_date.month
    _chinstar_day = birth_date.day
    _chinstar_hour = birth_time.hour
    _auto_ok = False

    if _is_calculated:
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
            _auto_ok = True
        except Exception:
            pass

    _cs_gender = "M" if gender == "male" else "F"

    if _auto_ok:
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

            _cs_tab_chart, _cs_tab_xiangtai, _cs_tab_gui_jian = st.tabs([
                t("chinstar_subtab_chart"),
                t("chinstar_subtab_xiangtai"),
                t("chinstar_subtab_gui_jian"),
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

                # 五行色彩 (dark theme)
                _cs_elem_bg = {
                    "木": "rgba(56,142,60,0.15)", "火": "rgba(198,40,40,0.15)",
                    "土": "rgba(245,127,23,0.15)", "金": "rgba(158,158,158,0.15)", "水": "rgba(21,101,192,0.15)",
                }
                _cs_elem_bd = {
                    "木": "rgba(56,142,60,0.4)", "火": "rgba(198,40,40,0.4)",
                    "土": "rgba(245,127,23,0.4)", "金": "rgba(158,158,158,0.4)", "水": "rgba(21,101,192,0.4)",
                }

                def _cs_cell(branch_char: str) -> str:
                    palace = _cs_branch_to_palace.get(branch_char, "")
                    bird   = _cs_palace_bird.get(palace, "")
                    elem   = _cs_qin_elem.get(bird, "")
                    bg     = _cs_elem_bg.get(elem, "rgba(30,27,75,0.4)")
                    bd     = _cs_elem_bd.get(elem, "rgba(167,139,250,0.3)")
                    badge  = ""
                    if branch_char == _cs_ming_br:
                        badge = '<span style="color:#ef4444;font-size:10px;">★命</span> '
                        bd    = "rgba(239,68,68,0.5)"
                        bg    = "rgba(239,68,68,0.1)"
                    elif branch_char == _cs_shen_br:
                        badge = '<span style="color:#a78bfa;font-size:10px;">☆身</span> '
                        bd    = "rgba(167,139,250,0.5)"
                        bg    = "rgba(167,139,250,0.1)"
                    elif branch_char == _cs_tai_br:
                        badge = '<span style="color:#facc15;font-size:10px;">◎胎</span> '
                        bd    = "rgba(250,204,21,0.5)"
                        bg    = "rgba(250,204,21,0.1)"
                    return (
                        f'<td style="width:25%;min-width:70px;height:88px;text-align:center;'
                        f'vertical-align:middle;border:2px solid {bd};'
                        f'background:{bg};padding:4px 2px;border-radius:8px;">'
                        f'<div style="font-size:11px;color:#b0b0d0;font-weight:bold;">'
                        f'{badge}{branch_char}宮</div>'
                        f'<div style="font-size:11px;color:#e0e0ff;margin-top:2px;">{palace}</div>'
                        f'<div style="font-size:14px;color:#a78bfa;font-weight:bold;'
                        f'margin-top:3px;">{bird}</div>'
                        f'</td>'
                    )

                # 中央格（基本資料 + 三主星 + 格局）
                _cs_center_td = (
                    '<td colspan="2" rowspan="2" style="text-align:center;'
                    'vertical-align:middle;border:2px solid rgba(167,139,250,0.3);'
                    'background:rgba(30,27,75,0.6);padding:10px 8px;border-radius:8px;'
                    'line-height:1.6;">'
                    '<div style="font-size:15px;font-weight:bold;color:#a78bfa;'
                    'letter-spacing:2px;">萬化仙禽</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;margin-top:6px;">'
                    f'{bi["year"]}年{bi["month"]}月{bi["day"]}日 {bi["hour"]}時</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;">{bi["gender"]}命 {bi["day_night"]}</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;">{bi["season"]}季 · {bi["san_yuan"]}</div>'
                    '<hr style="margin:6px 0;border-color:rgba(167,139,250,0.2);">'
                    f'<div style="font-size:11px;color:#e0e0ff;"><b>胎星</b>：{s["tai_xing"]}</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;"><b>命星</b>：{s["ming_xing"]}</div>'
                    f'<div style="font-size:11px;color:#e0e0ff;"><b>身星</b>：{s["shen_xing"]}</div>'
                    '<hr style="margin:6px 0;border-color:rgba(167,139,250,0.2);">'
                    f'<div style="font-size:11px;color:#e0e0ff;">'
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
                    '<div style="overflow-x:auto;-webkit-overflow-scrolling:touch;max-width:100%;">'
                    '<table style="border-collapse:separate;border-spacing:4px;'
                    'margin:10px auto;width:100%;table-layout:fixed;font-family:\'Noto Sans TC\',serif;">'
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
                    + "</tr></table></div>"
                )
                st.markdown(_cs_grid, unsafe_allow_html=True)
                _render_ai_button("tab_chinstar", _cs_chart, btn_key="chinstar")
                st.divider()

                # ── 吞啗分析 ──────────────────────────────
                st.markdown(t("chinstar_swallow_analysis_header"))
                _sw = _cs_chart["swallow_analysis"]
                if _sw:
                    _sw_rows = [{"對照": k, "判斷": v} for k, v in _sw.items()]
                    st.dataframe(_sw_rows, width='stretch', hide_index=True)
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
                    st.dataframe(_xt_rows, width='stretch', hide_index=True)

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
                        st.dataframe(_gui_rows, width='stretch', hide_index=True)
                    else:
                        st.info(t("chinstar_no_gui"))

                    st.markdown(t("chinstar_jian_for_star").format(star=_gj_star))
                    _jian = lookup_jian_ge(_gj_star)
                    if _jian:
                        _jian_rows = [{"格局": j["name"], "干支": j["ganzhi"]} for j in _jian]
                        st.dataframe(_jian_rows, width='stretch', hide_index=True)
                    else:
                        st.info(t("chinstar_no_jian"))
                    st.divider()

        except Exception as _e:
            st.error(f"{t('error_tab_compute')}：{_e}")
            st.exception(_e)
    else:
        # Manual input fallback or not calculated
        st.markdown(t("desc_chinstar"))
        if not _is_calculated:
            st.info(t("info_calc_prompt"))
        else:
            st.subheader(t("chinstar_lunar_input_header"))
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
            if st.button(t("calculate_btn"), key="chinstar_calc_btn"):
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

                    _cs_tab_chart, _cs_tab_xiangtai, _cs_tab_gui_jian = st.tabs([
                        t("chinstar_subtab_chart"),
                        t("chinstar_subtab_xiangtai"),
                        t("chinstar_subtab_gui_jian"),
                    ])

                    with _cs_tab_chart:
                        from astro.chinstar.chinstar import BRANCHES as _cs_branches, QIN_ELEMENT as _cs_qin_elem
                        st.code(WanHuaXianQin.format_chart(_cs_chart), language="")
                except Exception as _e:
                    st.error(f"{t('error_tab_compute')}：{_e}")
                    st.exception(_e)

