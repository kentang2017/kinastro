"""Legacy compatibility bridge for refactored system handlers."""

from __future__ import annotations

import importlib
from collections.abc import Iterator, Mapping
from datetime import datetime as datetime, time as time
from typing import Any

import streamlit as st

_mode = None
x = None


def _get_attr(module_name: str, attr_name: str):
    return getattr(importlib.import_module(module_name), attr_name)


def _call(module_name: str, attr_name: str, *args, **kwargs):
    return _get_attr(module_name, attr_name)(*args, **kwargs)


class _LazyAttr:
    def __init__(self, module_name: str, attr_name: str) -> None:
        self.module_name = module_name
        self.attr_name = attr_name

    def _value(self):
        return _get_attr(self.module_name, self.attr_name)

    def __getattr__(self, name: str):
        return getattr(self._value(), name)

    def __call__(self, *args, **kwargs):
        return self._value()(*args, **kwargs)

    def __getitem__(self, key):
        return self._value()[key]

    def __iter__(self):
        return iter(self._value())

    def __len__(self):
        return len(self._value())

    def __contains__(self, item):
        return item in self._value()

    def __bool__(self):
        return bool(self._value())

    def __eq__(self, other):
        return self._value() == other

    def __str__(self) -> str:
        return str(self._value())

    def __repr__(self) -> str:
        return repr(self._value())

    def get(self, *args, **kwargs):
        return self._value().get(*args, **kwargs)

    def keys(self):
        return self._value().keys()

    def items(self):
        return self._value().items()

    def values(self):
        return self._value().values()


ACG_PLANETS = _LazyAttr("astro.astrocartography", "ACG_PLANETS")
ACG_LINE_COLORS = _LazyAttr("astro.astrocartography", "LINE_COLORS")
ACG_PLANET_COLORS = _LazyAttr("astro.astrocartography", "PLANET_COLORS")
ASTEROID_GROUPS = _LazyAttr("astro.western.asteroids", "ASTEROID_GROUPS")
PLANET_GLYPHS = _LazyAttr("astro.astrocartography", "PLANET_GLYPHS")
PtolPlanet = _LazyAttr("astro.western.ptolemy_dignities", "Planet")
SIGN_NAMES = _LazyAttr("astro.western.ptolemy_dignities", "SIGN_NAMES")
STAR_CATALOG_ALL = _LazyAttr("astro.western.fixed_stars", "STAR_CATALOG_ALL")
VARGA_INFO = _LazyAttr("astro.vedic.varga", "VARGA_INFO")
VARGA_KEYS = _LazyAttr("astro.vedic.varga", "VARGA_KEYS")


class _GanzhiProxy(Mapping[str, Any]):
    def _data(self) -> dict[str, Any]:
        params = st.session_state.get("_calc_params") or {}
        required = ("year", "month", "day", "hour", "minute")
        if not all(key in params for key in required):
            return {}
        tieban_cls = _get_attr("astro.tieban", "TieBanShenShu")
        calc = tieban_cls()
        return calc.calculate_ganzhi(
            datetime(
                params["year"],
                params["month"],
                params["day"],
                params["hour"],
                params.get("minute", 0),
            )
        )

    def __getitem__(self, key: str) -> Any:
        return self._data()[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._data())

    def __len__(self) -> int:
        return len(self._data())



ganzhi = _GanzhiProxy()


def _system_cache_key(*args, **kwargs):
    return _call("core.cached_computations", "_system_cache_key", *args, **kwargs)


def auto_cn(*args, **kwargs):
    return _call("astro.i18n", "auto_cn", *args, **kwargs)


def compute_astrocartography(*args, **kwargs):
    return _call("astro.astrocartography", "compute_astrocartography", *args, **kwargs)


def compute_astrocartography_transit(*args, **kwargs):
    return _call("astro.astrocartography", "compute_astrocartography_transit", *args, **kwargs)


def dignity_to_chinese(*args, **kwargs):
    return _call("astro.western.ptolemy_dignities", "dignity_to_chinese", *args, **kwargs)


def find_conjunctions(*args, **kwargs):
    return _call("astro.western.fixed_stars", "find_conjunctions", *args, **kwargs)


def format_acg_for_prompt(*args, **kwargs):
    return _call("astro.astrocartography", "format_acg_for_prompt", *args, **kwargs)


def generate_natal_summary(*args, **kwargs):
    return _call("astro.natal_summary", "generate_natal_summary", *args, **kwargs)


def get_asteroid_aspects(*args, **kwargs):
    return _call("astro.western.advanced_bodies", "get_asteroid_aspects", *args, **kwargs)


def get_dasha_reading(*args, **kwargs):
    return _call("astro.interpretations", "get_dasha_reading", *args, **kwargs)


def get_lang(*args, **kwargs):
    return _call("astro.i18n", "get_lang", *args, **kwargs)


def get_qizheng_dasha_reading(*args, **kwargs):
    return _call("astro.interpretations", "get_qizheng_dasha_reading", *args, **kwargs)


def get_yogini_reading(*args, **kwargs):
    return _call("astro.interpretations", "get_yogini_reading", *args, **kwargs)


# Chinese systems

def build_twelve_ci_svg(*args, **kwargs):
    return _call("astro.twelve_ci", "build_twelve_ci_svg", *args, **kwargs)


def compute_bazi_chart(*args, **kwargs):
    return _call("astro.bazi.calculator", "compute_bazi", *args, **kwargs)


def compute_damo_chart(*args, **kwargs):
    return _call("astro.damo.calculator", "compute_damo_chart", *args, **kwargs)


def compute_diqiyijue_chart(*args, **kwargs):
    return _call("astro.diqiyijue.calculator", "compute_diqiyijue_chart", *args, **kwargs)


def compute_liuren_chart(*args, **kwargs):
    return _call("astro.sanshi.liuren", "compute_liuren_chart", *args, **kwargs)


def compute_lunming(*args, **kwargs):
    return _call("astro.sanshi.liuren", "compute_lunming", *args, **kwargs)


def compute_twelve_ci_chart(*args, **kwargs):
    return _call("astro.twelve_ci", "compute_twelve_ci_chart", *args, **kwargs)


def compute_wuyunliuqi(*args, **kwargs):
    return _call("astro.wuyunliuqi.calculator", "compute_wuyunliuqi", *args, **kwargs)


def render_aspect_summary(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_aspect_summary", *args, **kwargs)


def render_bazi(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_bazi", *args, **kwargs)


def render_bazi_chart(*args, **kwargs):
    return _call("astro.bazi.renderer", "render_streamlit", *args, **kwargs)


def render_beiji_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int = 0,
    gender: str = "男",
) -> None:
    result = _call(
        "astro.beiji.calculator",
        "compute_beiji",
        year=year,
        month=month,
        day=day,
        hour=hour,
        minute=minute,
        gender=gender,
    )
    _call("astro.beiji.renderer", "render_beiji_chart", result)


def render_cetian_ziwei_chart(*args, **kwargs):
    return _call("astro.cetian_ziwei", "render_cetian_ziwei_chart", *args, **kwargs)


def render_chart_info(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_chart_info", *args, **kwargs)


def render_chunzi_chart() -> None:
    _call("astro.chunzi", "render_streamlit")


def render_damo_chart(*args, **kwargs):
    return _call("astro.damo.renderer", "render_damo_chart", *args, **kwargs)


def render_dasha(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_dasha", *args, **kwargs)


def render_diqiyijue_chart(*args, **kwargs):
    return _call("astro.diqiyijue.renderer", "render_diqiyijue_chart", *args, **kwargs)


def render_electional_tool(*args, **kwargs):
    return _call("astro.qizheng.qizheng_electional", "render_electional_tool", *args, **kwargs)


def render_financial_tab(*args, **kwargs):
    return _call("astro.qizheng.qizheng_financial", "render_financial_tab", *args, **kwargs)


def render_full_chart(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_full_chart", *args, **kwargs)


def render_house_table(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_house_table", *args, **kwargs)


def render_kaiyuan_chart() -> None:
    _call("astro.kaiyuan.renderer", "render_streamlit")


def render_liuren_chart(*args, **kwargs):
    return _call("astro.sanshi.liuren", "render_liuren_chart", *args, **kwargs)


def render_lunming_report(*args, **kwargs):
    return _call("astro.sanshi.liuren", "render_lunming_report", *args, **kwargs)


def render_mansion_text_panel(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_mansion_text_panel", *args, **kwargs)


def render_ming_gong_interpretations(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_ming_gong_interpretations", *args, **kwargs)


def render_nanji_chart(*args, **kwargs):
    return _call("astro.nanji", "render_streamlit", *args, **kwargs)


def render_planet_table(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_planet_table", *args, **kwargs)


def render_qigua_ui(*args, **kwargs):
    return _call("astro.chinese.taixuan.taixuan_renderer", "render_qigua_ui", *args, **kwargs)


def render_shensha(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_shensha", *args, **kwargs)


def render_taixuan_chart(*args, **kwargs):
    return _call("astro.chinese.taixuan.taixuan_renderer", "render_taixuan_chart", *args, **kwargs)


def render_taixuan_intro(*args, **kwargs):
    return _call("astro.chinese.taixuan.taixuan_renderer", "render_taixuan_intro", *args, **kwargs)


def render_transit_comparison(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_transit_comparison", *args, **kwargs)


def render_twelve_ci_chart(*args, **kwargs):
    return _call("astro.twelve_ci", "render_twelve_ci_chart", *args, **kwargs)


def render_wuyunliuqi_chart(*args, **kwargs):
    return _call("astro.wuyunliuqi.renderer", "render_streamlit", *args, **kwargs)


def render_wuyunliuqi_intro(*args, **kwargs):
    return _call("astro.wuyunliuqi.renderer", "render_wuyunliuqi_intro", *args, **kwargs)


def render_zhangguo(*args, **kwargs):
    return _call("astro.qizheng.chart_renderer", "render_zhangguo", *args, **kwargs)


# Western systems

def _fludd_config_from_dict(*args, **kwargs):
    return _call("astro.fludd_rota", "config_from_dict", *args, **kwargs)


def _render_global_ai_chat(*args, **kwargs):
    return _call("ui.ai_chat", "render_global_ai_chat", *args, **kwargs)


def build_babylonian_planisphere_svg(*args, **kwargs):
    return _call("astro.babylonian", "build_babylonian_planisphere_svg", *args, **kwargs)


def build_greek_horoscope_svg(*args, **kwargs):
    return _call("astro.western.hellenistic", "build_greek_horoscope_svg", *args, **kwargs)


def compute_babylonian_chart(*args, **kwargs):
    return _call("astro.babylonian", "compute_babylonian_chart", *args, **kwargs)


def compute_cosmobiology_chart(*args, **kwargs):
    return _call("astro.cosmobiology.calculator", "compute_cosmobiology_chart", *args, **kwargs)


def compute_esoteric_chart(*args, **kwargs):
    return _call("astro.esoteric.calculator", "compute_esoteric_chart", *args, **kwargs)


def compute_hellenistic_chart(*args, **kwargs):
    return _call("astro.western.hellenistic", "compute_hellenistic_chart", *args, **kwargs)


def compute_hellenistic_extended(*args, **kwargs):
    return _call("astro.western.hellenistic", "compute_hellenistic_extended", *args, **kwargs)


def compute_human_design_chart(*args, **kwargs):
    return _call("astro.human_design.calculator", "compute_human_design_chart", *args, **kwargs)


def compute_multi_harmonic(*args, **kwargs):
    return _call("astro.harmonic.calculator", "compute_multi_harmonic", *args, **kwargs)


def compute_primary_directions(*args, **kwargs):
    return _call("astro.primary_directions.calculator", "compute_primary_directions", *args, **kwargs)


def compute_uranian_chart(*args, **kwargs):
    return _call("astro.western.uranian", "compute_uranian_chart", *args, **kwargs)


def compute_western_chart(*args, **kwargs):
    return _call("astro.western.western", "compute_western_chart", *args, **kwargs)


def render_alchemical_tab(*args, **kwargs):
    return _call("frontend.alchemical_renderer", "render_alchemical_tab", *args, **kwargs)


def render_annual_profections(*args, **kwargs):
    return _call("frontend.hellenistic_enhanced_renderer", "render_annual_profections", *args, **kwargs)


def render_babylonian_chart(*args, **kwargs):
    return _call("astro.babylonian", "render_babylonian_chart", *args, **kwargs)


def render_cosmobiology(*args, **kwargs):
    return _call("astro.cosmobiology.renderer", "render_cosmobiology", *args, **kwargs)


def render_draconic_chart(*args, **kwargs):
    return _call("astro.western.draconic", "render_draconic_chart", *args, **kwargs)


def render_electional_chart(*args, **kwargs):
    return _call("astro.electional", "render_streamlit", *args, **kwargs)


def render_esoteric_chart(*args, **kwargs):
    return _call("astro.esoteric", "render_streamlit", *args, **kwargs)


def render_extended_lots(*args, **kwargs):
    return _call("astro.western.hellenistic", "render_extended_lots", *args, **kwargs)


def render_fludd_rota(*args, **kwargs):
    return _call("frontend.fludd_rota_renderer", "render_fludd_rota", *args, **kwargs)


def render_harmonic(*args, **kwargs):
    return _call("astro.harmonic.renderer", "render_harmonic", *args, **kwargs)


def render_harmonic_chart(*args, **kwargs):
    return _call("astro.western.harmonic", "render_harmonic_chart", *args, **kwargs)


def render_hellenistic_chart(*args, **kwargs):
    return _call("astro.western.hellenistic", "render_hellenistic_chart", *args, **kwargs)


def render_human_design_chart(*args, **kwargs):
    return _call("astro.human_design", "render_streamlit", *args, **kwargs)


def render_mundane_chart(*args, **kwargs):
    return _call("astro.mundane", "render_streamlit", *args, **kwargs)


def render_predictive_suite(*args, **kwargs):
    return _call("astro.western.predictive_ui", "render_predictive_suite", *args, **kwargs)


def render_primary_directions(*args, **kwargs):
    return _call("astro.primary_directions.renderer", "render_primary_directions", *args, **kwargs)


def render_rectification_page(*args, **kwargs):
    return _call("astro.rectification.renderer", "render_streamlit", *args, **kwargs)


def render_trutine_chart(*args, **kwargs):
    return _call("astro.trutine_of_hermes", "render_streamlit", *args, **kwargs)


def render_uranian_chart(*args, **kwargs):
    return _call("astro.western.uranian", "render_uranian_chart", *args, **kwargs)


def render_valens_combinations(*args, **kwargs):
    return _call("astro.western.hellenistic", "render_valens_combinations", *args, **kwargs)


def render_western_chart(*args, **kwargs):
    return _call("astro.western.western", "render_western_chart", *args, **kwargs)


def render_wiki(*args, **kwargs):
    return _call("wiki_renderer", "render_wiki", *args, **kwargs)


def render_zodiacal_releasing(*args, **kwargs):
    return _call("frontend.hellenistic_enhanced_renderer", "render_zodiacal_releasing", *args, **kwargs)


# Asian systems

def build_kalachakra_mandala_svg(*args, **kwargs):
    return _call("astro.tibetan", "build_kalachakra_mandala_svg", *args, **kwargs)


def calculate_nine_palace_divination(*args, **kwargs):
    return _call("astro.thai", "calculate_nine_palace_divination", *args, **kwargs)


def calculate_thai_nine_grid(*args, **kwargs):
    return _call("astro.thai", "calculate_thai_nine_grid", *args, **kwargs)


def compute_brahma_jati(*args, **kwargs):
    return _call("astro.brahma_jati", "compute_brahma_jati", *args, **kwargs)


def compute_celtic_tree_chart(*args, **kwargs):
    return _call("astro.celtic.celtic_tree_graves", "compute_celtic_tree_chart", *args, **kwargs)


def compute_lao_chart(*args, **kwargs):
    return _call("astro.laos.calculator", "compute_lao_chart", *args, **kwargs)


def compute_lifetime_hexagram(*args, **kwargs):
    return _call("astro.liuyao_lifetime.calculator", "compute_lifetime_hexagram", *args, **kwargs)


def compute_mahabote_chart(*args, **kwargs):
    return _call("astro.mahabote", "compute_mahabote_chart", *args, **kwargs)


def compute_nine_star_ki_chart(*args, **kwargs):
    return _call("astro.nine_star_ki", "compute_nine_star_ki_chart", *args, **kwargs)


def compute_polynesian_chart(*args, **kwargs):
    return _call("astro.polynesian_hawaiian.calculator", "compute_polynesian_chart", *args, **kwargs)


def compute_tibetan_chart(*args, **kwargs):
    return _call("astro.tibetan", "compute_tibetan_chart", *args, **kwargs)


def compute_wariga(*args, **kwargs):
    return _call("astro.wariga.calculator", "compute_wariga", *args, **kwargs)


def compute_weton(*args, **kwargs):
    return _call("astro.jawa_weton.calculator", "compute_weton", *args, **kwargs)


def compute_zurkhai_chart(*args, **kwargs):
    return _call("astro.zurkhai", "compute_zurkhai_chart", *args, **kwargs)


def render_bintang_duabelas_chart(*args, **kwargs):
    return _call("astro.bintang_duabelas", "render_streamlit", *args, **kwargs)


def render_brahma_jati(*args, **kwargs):
    return _call("astro.brahma_jati", "render_brahma_jati", *args, **kwargs)


def render_brahma_jati_browse(*args, **kwargs):
    return _call("astro.brahma_jati", "render_brahma_jati_browse", *args, **kwargs)


def render_byzantine_astrology_chart(*args, **kwargs):
    return _call("astro.byzantine_astrology", "render_streamlit", *args, **kwargs)


def render_celtic_tree_chart(*args, **kwargs):
    return _call("astro.celtic.celtic_tree_graves", "render_celtic_tree_chart", *args, **kwargs)


def render_jawa_weton_chart(*args, **kwargs):
    return _call("astro.jawa_weton.renderer", "render_streamlit", *args, **kwargs)


def render_kinketika_chart(*args, **kwargs):
    return _call("astro.kinketika", "render_streamlit", *args, **kwargs)


def render_lao_horasat(*args, **kwargs):
    return _call("astro.laos.renderer", "render_lao_horasat", *args, **kwargs)


def render_liuyao_lifetime_chart(*args, **kwargs):
    return _call("astro.liuyao_lifetime.renderer", "render_streamlit", *args, **kwargs)


def render_mahabote_chart(*args, **kwargs):
    return _call("astro.mahabote", "render_mahabote_chart", *args, **kwargs)


def render_nine_grid(*args, **kwargs):
    return _call("astro.thai", "render_nine_grid", *args, **kwargs)


def render_nine_palace_divination(*args, **kwargs):
    return _call("astro.thai", "render_nine_palace_divination", *args, **kwargs)


def render_nine_star_ki_chart(*args, **kwargs):
    return _call("astro.nine_star_ki", "render_nine_star_ki_chart", *args, **kwargs)


def render_polynesian_chart_ui(*args, **kwargs):
    return _call("astro.polynesian_hawaiian", "render_streamlit", *args, **kwargs)


def render_thai_chart(*args, **kwargs):
    return _call("astro.thai", "render_thai_chart", *args, **kwargs)


def render_tibetan_chart(*args, **kwargs):
    return _call("astro.tibetan", "render_tibetan_chart", *args, **kwargs)


def render_wariga_chart(*args, **kwargs):
    return _call("astro.wariga.renderer", "render_streamlit", *args, **kwargs)


def render_zurkhai_chart(*args, **kwargs):
    return _call("astro.zurkhai", "render_zurkhai_chart", *args, **kwargs)


# Middle Eastern systems

def _compute_geomancy_chart(*args, **kwargs):
    return _call("astro.astronomical_geomancy", "compute_geomancy_chart", *args, **kwargs)


def _render_geomancy_input(*args, **kwargs):
    return _call("astro.astronomical_geomancy", "render_input_panel", *args, **kwargs)


def _render_geomancy_ui(*args, **kwargs):
    return _call("astro.astronomical_geomancy", "render_streamlit", *args, **kwargs)


def _render_reference_library() -> None:
    st.markdown("### 📚 Reference Library")
    render_picatrix_browse()
    st.divider()
    render_shams_browse()
    st.divider()
    render_ms164_browse()


def analyze_bahre_hasab_date(*args, **kwargs):
    return _call("astro.bahre_hasab.engine", "analyze_bahre_hasab_date", *args, **kwargs)


def build_yemeni_manzil_mandala_svg(*args, **kwargs):
    return _call("astro.yemeni", "build_yemeni_manzil_mandala_svg", *args, **kwargs)


def compute_albiruni_lots(*args, **kwargs):
    return _call("astro.arabic_lots", "compute_albiruni_lots", *args, **kwargs)


def compute_amazigh_chart(*args, **kwargs):
    return _call("astro.amazigh.amazigh", "compute_amazigh_chart", *args, **kwargs)


def compute_arabic_chart(*args, **kwargs):
    return _call("astro.arabic.arabic", "compute_arabic_chart", *args, **kwargs)


def compute_dogon_sirius_chart(*args, **kwargs):
    return _call("astro.dogon", "compute_dogon_sirius_chart", *args, **kwargs)


def compute_kabbalistic_chart(*args, **kwargs):
    return _call("astro.kabbalistic", "compute_kabbalistic_chart", *args, **kwargs)


def compute_moon_longitude(*args, **kwargs):
    return _call("astro.arabic.picatrix_mansions", "compute_moon_longitude", *args, **kwargs)


def compute_yemeni_chart(*args, **kwargs):
    return _call("astro.yemeni", "compute_yemeni_chart", *args, **kwargs)


def render_amazigh_chart(*args, **kwargs):
    return _call("astro.amazigh.amazigh", "render_amazigh_chart", *args, **kwargs)


def render_amazigh_sky_svg(*args, **kwargs):
    return _call("astro.amazigh.amazigh", "render_amazigh_sky_svg", *args, **kwargs)


def render_arabic_chart(*args, **kwargs):
    return _call("astro.arabic.arabic", "render_arabic_chart", *args, **kwargs)


def render_arabic_lots_dashboard(*args, **kwargs):
    return _call("frontend.arabic_lots_dashboard", "render_arabic_lots_dashboard", *args, **kwargs)


def render_bahre_hasab_tab(*args, **kwargs):
    return _call("frontend.bahre_hasab_renderer", "render_bahre_hasab_tab", *args, **kwargs)


def render_deep_sassanian_chart(*args, **kwargs):
    return _call("astro.persian", "render_deep_streamlit", *args, **kwargs)


def render_dogon_sirius_chart(*args, **kwargs):
    return _call("astro.dogon", "render_dogon_sirius_chart", *args, **kwargs)


def render_european_geomancy(*args, **kwargs):
    return _call("frontend.european_geomancy_renderer", "render_european_geomancy", *args, **kwargs)


def render_kabbalistic_chart(*args, **kwargs):
    return _call("astro.kabbalistic", "render_kabbalistic_chart", *args, **kwargs)


def render_mansion_lookup(*args, **kwargs):
    return _call("astro.arabic.picatrix_mansions", "render_mansion_lookup", *args, **kwargs)


def render_mazzalot_chart(*args, **kwargs):
    return _call("astro.jewish_mazzalot", "render_mazzalot_chart", *args, **kwargs)


def render_ms164_browse(*args, **kwargs):
    return _call("astro.arabic.ms164_browser", "render_ms164_browse", *args, **kwargs)


def render_picatrix_behenian(*args, **kwargs):
    return _call("astro.picatrix_behenian", "render_streamlit", *args, **kwargs)


def render_picatrix_browse(*args, **kwargs):
    return _call("astro.arabic.picatrix_mansions", "render_picatrix_browse", *args, **kwargs)


def render_picatrix_invocations(*args, **kwargs):
    return _call("astro.arabic.picatrix_invocations", "render_picatrix_invocations", *args, **kwargs)


def render_planetary_hours_tool(*args, **kwargs):
    return _call("astro.arabic.picatrix_mansions", "render_planetary_hours_tool", *args, **kwargs)


def render_shams_browse(*args, **kwargs):
    return _call("astro.arabic.shams_maarif", "render_shams_browse", *args, **kwargs)


def render_shams_chart(*args, **kwargs):
    return _call("astro.arabic.shams_maarif", "render_shams_chart", *args, **kwargs)


def render_talisman_generator(*args, **kwargs):
    return _call("astro.arabic.picatrix_mansions", "render_talisman_generator", *args, **kwargs)


def render_yemeni_chart(*args, **kwargs):
    return _call("astro.yemeni", "render_yemeni_chart", *args, **kwargs)


# Ancient systems

def _compute_andean_chart_fn(*args, **kwargs):
    return _call("astro.andean", "compute_andean_chart", *args, **kwargs)


def _compute_armenian_chart_fn(*args, **kwargs):
    return _call("astro.systems.obscure.armenian", "compute_armenian_chart", *args, **kwargs)


def _compute_etruscan_chart_fn(*args, **kwargs):
    return _call("astro.etruscan", "compute_etruscan_chart", *args, **kwargs)


def compute_aztec_chart(*args, **kwargs):
    return _call("astro.aztec", "compute_aztec_chart", *args, **kwargs)


def compute_decan_chart(*args, **kwargs):
    return _call("astro.egyptian.decans", "compute_decan_chart", *args, **kwargs)


def compute_maya_chart(*args, **kwargs):
    return _call("astro.maya", "compute_maya_chart", *args, **kwargs)


def compute_sumerian_chart(*args, **kwargs):
    return _call("astro.sumerian.calculator", "compute_sumerian_chart", *args, **kwargs)


def render_andean_chart_ui(*args, **kwargs):
    return _call("astro.andean", "render_streamlit", *args, **kwargs)


def render_armenian_chart_ui(*args, **kwargs):
    return _call("astro.systems.obscure.armenian", "render_streamlit", *args, **kwargs)


def render_aztec_chart(*args, **kwargs):
    return _call("astro.aztec", "render_aztec_chart", *args, **kwargs)


def render_decan_browse(*args, **kwargs):
    return _call("astro.egyptian.decans", "render_decan_browse", *args, **kwargs)


def render_decan_chart(*args, **kwargs):
    return _call("astro.egyptian.decans", "render_decan_chart", *args, **kwargs)


def render_etruscan_chart_ui(*args, **kwargs):
    return _call("astro.etruscan", "render_streamlit", *args, **kwargs)


def render_maya_chart(*args, **kwargs):
    return _call("astro.maya", "render_maya_chart", *args, **kwargs)


def render_sumerian_chart(*args, **kwargs):
    return _call("astro.sumerian.renderer", "render_streamlit", *args, **kwargs)


# Sanshi / specialty systems

def compute_medical_chart(*args, **kwargs):
    return _call("astro.medical_astrology.calculator", "compute_medical_chart", *args, **kwargs)


def compute_qimen_luming(*args, **kwargs):
    return _call("astro.sanshi.qimen_luming", "compute_qimen_luming", *args, **kwargs)


def compute_shanghan_qianfa(*args, **kwargs):
    return _call("astro.shanghan_qianfa.calculator", "compute_shanghan_qianfa", *args, **kwargs)


def compute_taiyi_chart(*args, **kwargs):
    return _call("astro.sanshi.taiyi", "compute_taiyi_chart", *args, **kwargs)


def render_horary_chart(*args, **kwargs):
    return _call("astro.horary.renderer", "render_streamlit", *args, **kwargs)


def render_medical_astrology_chart(*args, **kwargs):
    return _call("astro.medical_astrology.renderer", "render_streamlit", *args, **kwargs)


def render_qimen_luming(*args, **kwargs):
    return _call("astro.sanshi.qimen_luming", "render_qimen_luming", *args, **kwargs)


def render_shanghan_qianfa_chart(*args, **kwargs):
    return _call("astro.shanghan_qianfa.renderer", "render_streamlit", *args, **kwargs)


def render_sports_astrology_chart(*args, **kwargs):
    return _call("astro.sports", "render_streamlit", *args, **kwargs)


def render_taiyi_chart(*args, **kwargs):
    return _call("astro.sanshi.taiyi", "render_taiyi_chart", *args, **kwargs)


# Vedic systems

def compute_jaimini_chart(*args, **kwargs):
    return _call("astro.jaimini", "compute_jaimini_chart", *args, **kwargs)


def compute_lal_kitab_chart(*args, **kwargs):
    return _call("astro.lal_kitab", "compute_lal_kitab_chart", *args, **kwargs)


def compute_nadi_chart(*args, **kwargs):
    return _call("astro.vedic.nadi", "compute_nadi_chart", *args, **kwargs)


def compute_vedic_chart(*args, **kwargs):
    return _call("astro.vedic.indian", "compute_vedic_chart", *args, **kwargs)


def render_jaimini_chart(*args, **kwargs):
    return _call("astro.jaimini", "render_jaimini_chart", *args, **kwargs)


def render_jaimini_dasha(*args, **kwargs):
    return _call("astro.jaimini", "render_jaimini_dasha", *args, **kwargs)


def render_lal_kitab_1952_page(*args, **kwargs):
    return _call("astro.lal_kitab", "render_lal_kitab_1952_page", *args, **kwargs)


def render_nadi_chart(*args, **kwargs):
    return _call("astro.vedic.nadi", "render_nadi_chart", *args, **kwargs)


def render_single_varga(*args, **kwargs):
    return _call("astro.vedic.varga", "render_single_varga", *args, **kwargs)


def render_sukkayodo_chart(*args, **kwargs):
    return _call("astro.sukkayodo", "render_sukkayodo_chart", *args, **kwargs)


def render_vedic_chart(*args, **kwargs):
    return _call("astro.vedic.indian", "render_vedic_chart", *args, **kwargs)


def render_vedic_financial_tab(*args, **kwargs):
    return _call("astro.vedic.financial", "render_vedic_financial_tab", *args, **kwargs)
