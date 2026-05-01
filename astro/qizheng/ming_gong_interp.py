"""
命宮特徵解讀模組 (Life Palace Interpretation Module)

從七政.txt中提取命宮相關文字描述，包括：
1. 立命X宮  — 依命宮地支的推命文字
2. X入本命宮 — 各星曜入命宮的文字描述
"""

import os
import streamlit as st

_TXT_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "..", "七政.txt")
)

_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# Planet display name → lookup prefix for "X入本命宮："
_PLANET_TO_KEY = {
    "太陽": "日",
    "太陰": "月",
    "木星": "木",
    "火星": "火",
    "土星": "土",
    "金星": "金",
    "水星": "水",
    "紫氣": "紫",
    "月孛": "孛",
    "羅睺": "羅",
    "計都": "計",
}

# Lines that mark the start of a non-命宮 palace section within each planet block
_PALACE_MARKERS = {"財帛宮", "兄弟宮", "田宅宮", "男女宮", "奴僕宮",
                   "夫妻宮", "疾厄宮", "遷移宮", "官祿宮", "福德宮", "相貌宮"}


@st.cache_data(show_spinner=False)
def _load_texts() -> tuple:
    """Parse 七政.txt and return (li_ming_dict, planet_dict).

    li_ming_dict  : branch_char → interpretation text (立命X宮 sections)
    planet_dict   : planet_key  → interpretation text (X入本命宮 sections)
    """
    try:
        with open(_TXT_PATH, encoding="utf-8") as fh:
            lines = fh.readlines()
    except FileNotFoundError:
        return {}, {}

    # ── 1. Extract 立命X宮 sections ──────────────────────────────────────────
    # Locate the starting line for each branch.
    li_ming_starts: dict[str, int] = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Pattern: "立命X宮：" where X is one earthly-branch character
        if (
            stripped.startswith("立命")
            and stripped.endswith("：")
            and len(stripped) == 5
        ):
            branch_char = stripped[2]
            if branch_char in _BRANCHES:
                li_ming_starts[branch_char] = i

    sorted_starts = sorted(li_ming_starts.items(), key=lambda kv: kv[1])

    li_ming: dict[str, str] = {}
    for idx, (branch_char, start_idx) in enumerate(sorted_starts):
        # End just before the next 立命X宮 entry (or the section separator)
        if idx + 1 < len(sorted_starts):
            end_idx = sorted_starts[idx + 1][1]
        else:
            end_idx = start_idx + 200  # generous fallback
            for j in range(start_idx + 1, min(start_idx + 300, len(lines))):
                if "十二宮論凶吉" in lines[j]:
                    end_idx = j
                    break

        paragraphs = []
        for j in range(start_idx + 1, end_idx):
            text = lines[j].strip()
            if text:
                paragraphs.append(text)

        li_ming[branch_char] = "\n\n".join(paragraphs)

    # ── 2. Extract X入本命宮 sections ────────────────────────────────────────
    planet_keys = list(_PLANET_TO_KEY.values())

    planet_starts: dict[str, int] = {}
    for i, line in enumerate(lines):
        stripped = line.strip()
        for key in planet_keys:
            if stripped.startswith(f"{key}入本命宮："):
                planet_starts[key] = i
                break

    planet_in_ming: dict[str, str] = {}
    for key, start_idx in planet_starts.items():
        collected = []
        for j in range(start_idx, min(start_idx + 30, len(lines))):
            raw = lines[j]
            stripped = raw.strip()

            # Stop at the first non-命宮 palace heading (財帛宮：…, etc.)
            if j > start_idx:
                for marker in _PALACE_MARKERS:
                    if marker in stripped and "：" in stripped:
                        break
                else:
                    if stripped:
                        collected.append(stripped)
                    continue
                break  # palace marker found — stop

            # First line: always include
            if stripped:
                collected.append(stripped)

        planet_in_ming[key] = "\n".join(collected)

    return li_ming, planet_in_ming


def get_li_ming_text(branch_char: str) -> str:
    """Return the 立命X宮 interpretation for the given earthly-branch character."""
    li_ming, _ = _load_texts()
    return li_ming.get(branch_char, "")


def get_planet_in_ming_text(planet_name: str) -> str:
    """Return the X入本命宮 interpretation for the given planet display name."""
    _, planet_in_ming = _load_texts()
    key = _PLANET_TO_KEY.get(planet_name)
    if not key:
        return ""
    return planet_in_ming.get(key, "")
