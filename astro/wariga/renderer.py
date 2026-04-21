"""
巴厘傳統 Wariga 渲染模組 (Renderer for Balinese Wariga Calendar)

提供三種渲染方式：
1. 古典 Lontar 圖形模式（Palalintangan 風格 HTML/CSS+SVG）— 優先推薦
2. 現代清晰表格模式（作為備用）
3. 純文字輸出模式（用於非 UI 環境）

所有視覺設計嚴格模擬棕櫚葉（Lontar）手稿風格：
- 米黃/淡棕色調（仿羊皮紙/棕櫚葉）
- 細線邊框、仿古分欄排版
- 傳統巴厘式方格矩陣（Palalintangan 結構）
- 每項輸出附「古法依據」標註

古法依據：Lontar Wariga / Dasar Wariga / Palalintangan
"""

import math

try:
    import svgwrite
    HAS_SVGWRITE = True
except ImportError:
    HAS_SVGWRITE = False

from .calculator import WarigaResult
from .constants import WUKU_TABLE, WUKU_ATTRIBUTES


# ============================================================
# 色彩主題 — 仿古 Lontar 棕櫚葉手稿風格
# ============================================================
_LONTAR_BG        = "#F5E6C8"   # 棕櫚葉米黃底色
_LONTAR_BORDER    = "#8B4513"   # 深棕邊框（風化棕櫚）
_LONTAR_HEADER    = "#5C2E00"   # 深棕標題文字
_LONTAR_TEXT      = "#3D1C02"   # 主文字（焦棕）
_LONTAR_SUBTLE    = "#7A5230"   # 次要文字
_LONTAR_ACCENT    = "#C9980A"   # 金黃強調色（Prada/金粉）
_LONTAR_AYU       = "#2E6B3B"   # 吉日綠
_LONTAR_ALA       = "#8B1A1A"   # 凶日紅
_LONTAR_NEUTRAL   = "#6B5A2D"   # 中性棕
_LONTAR_CELL_ODD  = "#EDD9A3"   # 表格奇數行
_LONTAR_CELL_EVEN = "#F5E6C8"   # 表格偶數行
_LONTAR_HIGHLIGHT = "#FFD700"   # 當前格高亮（金色）


# ============================================================
# 輔助函數 (Helpers)
# ============================================================

def _format_dewasa_status(is_auspicious: bool):
    """
    根據吉凶狀態回傳格式化文字與顏色

    回傳：
        tuple: (status_text, color)
    """
    if is_auspicious:
        return "✅ 吉日 (Dewasa Ayu)", _LONTAR_AYU
    return "⚠️ 需謹慎 (Dewasa Ala)", _LONTAR_ALA


def _moon_phase_emoji(phase_deg: float) -> str:
    """依月相角度回傳對應月相符號"""
    if phase_deg < 22.5:
        return "🌑"
    elif phase_deg < 67.5:
        return "🌒"
    elif phase_deg < 112.5:
        return "🌓"
    elif phase_deg < 157.5:
        return "🌔"
    elif phase_deg < 202.5:
        return "🌕"
    elif phase_deg < 247.5:
        return "🌖"
    elif phase_deg < 292.5:
        return "🌗"
    elif phase_deg < 337.5:
        return "🌘"
    return "🌑"


def _wuku_color(wuku_index: int) -> str:
    """取得 Wuku 傳統顏色"""
    if wuku_index < len(WUKU_ATTRIBUTES):
        return WUKU_ATTRIBUTES[wuku_index][2]
    return "#CCAA66"


def _escape_html(text: str) -> str:
    """HTML 轉義"""
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))


def _ayana_main(ayana: str) -> str:
    """提取 Ayana 主要名稱（括號前部分）"""
    return ayana.split("（")[0]


def _ayana_sub(ayana: str) -> str:
    """提取 Ayana 括號內說明（若有），否則回傳空字串"""
    parts = ayana.split("（", 1)
    if len(parts) < 2:
        return ""
    return parts[1].rstrip("）")


# ============================================================
# Palalintangan 風格 HTML/CSS+SVG 渲染
# 嚴格依照傳統巴厘 Palalintangan 排版結構
# ============================================================

def render_palalintangan_html(result: WarigaResult) -> str:
    """
    生成 Palalintangan 風格的完整 HTML/CSS 排盤

    視覺結構模擬傳統巴厘 Palalintangan（占星圖）：
    - 頂部：日期與核心資訊橫幅
    - 中央：Wuku 網格矩陣（30格，當前週高亮）
    - 右側：Wewaran 十類星期列表
    - 底部：Sasih、季節、Dauh 時辰與吉凶判斷

    古法依據：Lontar Palalintangan 傳統排版規則

    參數：
        result (WarigaResult): Wariga 計算完整結果

    回傳：
        str: 完整 HTML 字串
    """
    r = result
    d = r.dewasa
    s = r.sasih
    moon_emoji = _moon_phase_emoji(r.penanggal.moon_phase_deg)
    status_text, status_color = _format_dewasa_status(d.is_auspicious)
    penanggal_label = "Penanggal" if r.penanggal.is_penanggal else "Panglong"

    # ── CSS ──────────────────────────────────────────────────
    css = f"""
<style>
  .wariga-lontar {{
    font-family: 'Georgia', 'Palatino Linotype', serif;
    background: {_LONTAR_BG};
    border: 3px double {_LONTAR_BORDER};
    border-radius: 4px;
    padding: 16px;
    color: {_LONTAR_TEXT};
    max-width: 860px;
    margin: 0 auto;
  }}
  .wariga-lontar * {{ box-sizing: border-box; }}

  /* ── 頂部橫幅 ── */
  .wl-header {{
    text-align: center;
    border-bottom: 2px solid {_LONTAR_BORDER};
    padding-bottom: 10px;
    margin-bottom: 12px;
  }}
  .wl-title {{
    font-size: 1.35em;
    font-weight: bold;
    color: {_LONTAR_HEADER};
    letter-spacing: 0.05em;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.15);
  }}
  .wl-subtitle {{
    font-size: 0.78em;
    color: {_LONTAR_SUBTLE};
    font-style: italic;
    margin-top: 2px;
  }}
  .wl-date-box {{
    display: inline-block;
    border: 1.5px solid {_LONTAR_ACCENT};
    border-radius: 3px;
    padding: 5px 18px;
    margin: 6px auto;
    background: rgba(201,152,10,0.08);
    font-size: 1.0em;
    color: {_LONTAR_HEADER};
    font-weight: bold;
    letter-spacing: 0.03em;
  }}

  /* ── 雙欄主體 ── */
  .wl-body {{
    display: flex;
    gap: 14px;
    flex-wrap: wrap;
  }}
  .wl-left {{ flex: 1 1 380px; }}
  .wl-right {{ flex: 1 1 240px; }}

  /* ── 分節標題 ── */
  .wl-section-title {{
    font-size: 0.82em;
    font-weight: bold;
    color: {_LONTAR_ACCENT};
    text-transform: uppercase;
    letter-spacing: 0.08em;
    border-bottom: 1px solid {_LONTAR_BORDER};
    padding-bottom: 2px;
    margin: 10px 0 5px;
  }}
  .wl-lontar-note {{
    font-size: 0.68em;
    color: {_LONTAR_SUBTLE};
    font-style: italic;
    margin-bottom: 4px;
  }}

  /* ── Wuku 網格矩陣 ── */
  .wl-wuku-grid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 2px;
    margin-bottom: 10px;
  }}
  .wl-wuku-cell {{
    border: 1px solid {_LONTAR_BORDER};
    border-radius: 2px;
    padding: 2px 1px;
    text-align: center;
    font-size: 0.6em;
    background: {_LONTAR_CELL_EVEN};
    color: {_LONTAR_TEXT};
    line-height: 1.3;
    cursor: default;
    transition: background 0.15s;
  }}
  .wl-wuku-cell.current {{
    background: {_LONTAR_HIGHLIGHT};
    border: 2px solid {_LONTAR_BORDER};
    font-weight: bold;
    box-shadow: 0 0 4px rgba(201,152,10,0.5);
    color: {_LONTAR_HEADER};
    transform: scale(1.05);
    z-index: 1;
  }}
  .wl-wuku-cell .wc-num {{
    display: block;
    font-size: 0.8em;
    color: {_LONTAR_SUBTLE};
  }}
  .wl-wuku-cell .wc-name {{
    display: block;
    font-weight: bold;
    word-break: break-word;
    hyphens: auto;
  }}
  .wl-wuku-cell .wc-neptu {{
    display: block;
    font-size: 0.75em;
    color: {_LONTAR_ACCENT};
  }}

  /* ── Wewaran 表格 ── */
  .wl-wara-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.78em;
  }}
  .wl-wara-table th {{
    background: {_LONTAR_BORDER};
    color: #F5E6C8;
    padding: 3px 5px;
    text-align: center;
    font-weight: bold;
    font-size: 0.85em;
  }}
  .wl-wara-table td {{
    padding: 3px 5px;
    border-bottom: 1px solid rgba(139,69,19,0.25);
    vertical-align: middle;
  }}
  .wl-wara-table tr:nth-child(odd) td {{ background: {_LONTAR_CELL_ODD}; }}
  .wl-wara-table tr:nth-child(even) td {{ background: {_LONTAR_CELL_EVEN}; }}
  .wl-wara-type {{ color: {_LONTAR_SUBTLE}; }}
  .wl-wara-name {{ font-weight: bold; color: {_LONTAR_HEADER}; }}
  .wl-wara-neptu {{
    text-align: center;
    color: {_LONTAR_ACCENT};
    font-family: monospace;
  }}

  /* ── 吉凶橫幅 ── */
  .wl-dewasa-banner {{
    border: 2px solid;
    border-radius: 3px;
    padding: 7px 12px;
    margin: 8px 0;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .wl-dewasa-ayu {{
    border-color: {_LONTAR_AYU};
    background: rgba(46,107,59,0.07);
  }}
  .wl-dewasa-ala {{
    border-color: {_LONTAR_ALA};
    background: rgba(139,26,26,0.07);
  }}
  .wl-dewasa-status {{
    font-size: 1.05em;
    font-weight: bold;
  }}
  .wl-dewasa-tags {{
    margin-top: 6px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }}
  .wl-tag {{
    display: inline-block;
    padding: 1px 7px;
    border-radius: 10px;
    font-size: 0.72em;
    font-weight: bold;
    letter-spacing: 0.02em;
  }}
  .wl-tag-ayu {{ background: {_LONTAR_AYU}; color: #fff; }}
  .wl-tag-ala {{ background: {_LONTAR_ALA}; color: #fff; }}
  .wl-tag-note {{ background: {_LONTAR_SUBTLE}; color: #fff; }}

  /* ── 資訊卡片列 ── */
  .wl-info-row {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin: 5px 0;
  }}
  .wl-info-card {{
    border: 1.5px solid {_LONTAR_BORDER};
    border-radius: 3px;
    padding: 5px 9px;
    background: {_LONTAR_CELL_ODD};
    min-width: 80px;
    flex: 1 1 80px;
    text-align: center;
  }}
  .wl-info-card .ic-label {{
    font-size: 0.65em;
    color: {_LONTAR_SUBTLE};
    text-transform: uppercase;
    letter-spacing: 0.06em;
    display: block;
  }}
  .wl-info-card .ic-value {{
    font-size: 0.88em;
    font-weight: bold;
    color: {_LONTAR_HEADER};
    display: block;
    margin-top: 1px;
  }}
  .wl-info-card .ic-sub {{
    font-size: 0.68em;
    color: {_LONTAR_SUBTLE};
    display: block;
  }}

  /* ── 月相圓 ── */
  .wl-moon-row {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 5px 0;
  }}
  .wl-moon-emoji {{ font-size: 1.6em; line-height: 1; }}
  .wl-moon-info {{ font-size: 0.82em; }}

  /* ── Pawukon 進度條 ── */
  .wl-progress-bar {{
    background: rgba(139,69,19,0.18);
    border: 1px solid {_LONTAR_BORDER};
    border-radius: 2px;
    height: 10px;
    margin: 3px 0 6px;
    overflow: hidden;
  }}
  .wl-progress-fill {{
    height: 100%;
    background: linear-gradient(90deg, {_LONTAR_ACCENT}, {_LONTAR_BORDER});
    transition: width 0.4s;
  }}
  .wl-progress-label {{
    font-size: 0.68em;
    color: {_LONTAR_SUBTLE};
  }}

  /* ── 底部頁腳 ── */
  .wl-footer {{
    margin-top: 12px;
    padding-top: 8px;
    border-top: 1px dashed {_LONTAR_BORDER};
    font-size: 0.68em;
    color: {_LONTAR_SUBTLE};
    text-align: center;
    font-style: italic;
  }}

  /* ── Dauh 時辰表 ── */
  .wl-dauh-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin: 5px 0;
  }}
  .wl-dauh-card {{
    border: 1.5px solid {_LONTAR_BORDER};
    border-radius: 3px;
    padding: 5px 8px;
    background: {_LONTAR_CELL_ODD};
    font-size: 0.78em;
  }}
  .wl-dauh-card .dc-title {{
    font-weight: bold;
    color: {_LONTAR_HEADER};
    font-size: 0.9em;
  }}
  .wl-dauh-card .dc-deity {{
    color: {_LONTAR_SUBTLE};
    font-size: 0.85em;
  }}
  .wl-dauh-ayu {{ border-color: {_LONTAR_AYU}; }}
  .wl-dauh-ala {{ border-color: {_LONTAR_ALA}; }}

  /* ── 裝飾線 ── */
  .wl-ornament {{
    text-align: center;
    color: {_LONTAR_ACCENT};
    font-size: 0.9em;
    letter-spacing: 0.3em;
    margin: 4px 0;
    opacity: 0.65;
  }}
</style>
"""

    # ── 30 Wuku 網格矩陣 HTML ──────────────────────────────
    wuku_cells = []
    day_in_wuku = (r.day_in_pawukon % 7) + 1  # 只用於當前 Wuku 標示
    for i, (name, neptu) in enumerate(WUKU_TABLE):
        is_current = (i == r.wuku.index)
        cell_class = "wl-wuku-cell current" if is_current else "wl-wuku-cell"
        day_label = f"（第{day_in_wuku}天）" if is_current else ""
        wuku_cells.append(
            f'<div class="{cell_class}" title="Wuku {name}，Neptu={neptu}">'
            f'<span class="wc-num">W{i+1:02d}</span>'
            f'<span class="wc-name">{_escape_html(name)}</span>'
            f'<span class="wc-neptu">{neptu}{day_label}</span>'
            f'</div>'
        )
    wuku_grid_html = '<div class="wl-wuku-grid">' + "".join(wuku_cells) + '</div>'

    # ── Wewaran 表格 HTML ─────────────────────────────────
    wara_list = [
        r.eka_wara, r.dwi_wara, r.tri_wara,
        r.catur_wara, r.panca_wara, r.sad_wara,
        r.sapta_wara, r.asta_wara, r.sanga_wara,
        r.dasa_wara,
    ]
    wara_rows = ""
    for w in wara_list:
        wara_rows += (
            f'<tr>'
            f'<td class="wl-wara-type">{_escape_html(w.wara_type)}</td>'
            f'<td class="wl-wara-name">{_escape_html(w.name)}</td>'
            f'<td class="wl-wara-neptu">{w.neptu}</td>'
            f'</tr>'
        )
    wara_table_html = f"""
<table class="wl-wara-table">
  <thead>
    <tr><th>Wara 類型</th><th>名稱</th><th>Neptu</th></tr>
  </thead>
  <tbody>{wara_rows}</tbody>
</table>
"""

    # ── 吉凶橫幅 HTML ─────────────────────────────────────
    banner_class = "wl-dewasa-ayu" if d.is_auspicious else "wl-dewasa-ala"
    dewasa_html = f"""
<div class="wl-dewasa-banner {banner_class}">
  <span class="wl-dewasa-status" style="color:{status_color};">
    {_escape_html(status_text)}
  </span>
  <span style="font-size:0.8em;color:{_LONTAR_SUBTLE};">
    Neptu 總和：{d.neptu_sum}
  </span>
</div>
"""
    if d.auspicious_labels or d.inauspicious_labels:
        tags_html = '<div class="wl-dewasa-tags">'
        for lbl in d.auspicious_labels:
            tags_html += f'<span class="wl-tag wl-tag-ayu">✅ {_escape_html(lbl)}</span>'
        for lbl in d.inauspicious_labels:
            tags_html += f'<span class="wl-tag wl-tag-ala">⚠️ {_escape_html(lbl)}</span>'
        for note in d.notes:
            tags_html += f'<span class="wl-tag wl-tag-note">📝 {_escape_html(note)}</span>'
        tags_html += '</div>'
        dewasa_html += tags_html

    # ── Pancasuda 卡片 ────────────────────────────────────
    pancasuda_html = f"""
<div class="wl-info-row">
  <div class="wl-info-card">
    <span class="ic-label">Pancasuda</span>
    <span class="ic-value">{_escape_html(d.pancasuda)}</span>
    <span class="ic-sub">{_escape_html(d.pancasuda_meaning)}</span>
  </div>
  <div class="wl-info-card">
    <span class="ic-label">Ingkel</span>
    <span class="ic-value">{_escape_html(r.ingkel)}</span>
    <span class="ic-sub">動物分類</span>
  </div>
  <div class="wl-info-card">
    <span class="ic-label">Lintang</span>
    <span class="ic-value">{_escape_html(r.lintang)}</span>
    <span class="ic-sub">星宿</span>
  </div>
</div>
<div class="wl-info-row">
  <div class="wl-info-card">
    <span class="ic-label">Watek Alit</span>
    <span class="ic-value">{_escape_html(r.watek_alit)}</span>
    <span class="ic-sub">小性情</span>
  </div>
  <div class="wl-info-card">
    <span class="ic-label">Watek Madya</span>
    <span class="ic-value">{_escape_html(r.watek_madya)}</span>
    <span class="ic-sub">中性情</span>
  </div>
</div>
"""

    # ── 月相資訊 ─────────────────────────────────────────
    penanggal_special = f" ✨ <b>{_escape_html(r.penanggal.special)}</b>" if r.penanggal.special else ""
    moon_html = f"""
<div class="wl-moon-row">
  <span class="wl-moon-emoji">{moon_emoji}</span>
  <div class="wl-moon-info">
    <b>{_escape_html(penanggal_label)} {r.penanggal.day_number}</b> —
    {_escape_html(r.penanggal.name)}{penanggal_special}<br>
    <span style="color:{_LONTAR_SUBTLE};">
      Neptu: {r.penanggal.neptu} ／ 月相角: {r.penanggal.moon_phase_deg:.1f}°
    </span>
  </div>
</div>
"""

    # ── Sasih 與季節 ──────────────────────────────────────
    season_icon = "☀️" if "Lahru" in s.season else "🌧️"
    ayana_icon = "⬆️" if "Uttara" in s.ayana else "⬇️"
    sasih_html = f"""
<div class="wl-info-row">
  <div class="wl-info-card">
    <span class="ic-label">Sasih（月份）</span>
    <span class="ic-value">{_escape_html(s.sasih_name)}</span>
    <span class="ic-sub">第 {s.sasih_index + 1} 月</span>
  </div>
  <div class="wl-info-card">
    <span class="ic-label">{season_icon} 季節</span>
    <span class="ic-value">{_escape_html(s.season_cn)}</span>
    <span class="ic-sub">{_escape_html(s.season)}</span>
  </div>
  <div class="wl-info-card">
    <span class="ic-label">{ayana_icon} Ayana</span>
    <span class="ic-value">{_escape_html(_ayana_main(s.ayana))}</span>
    <span class="ic-sub">{_escape_html(_ayana_sub(s.ayana))}</span>
  </div>
</div>
"""

    # ── Dauh 時辰 ─────────────────────────────────────────
    pd = r.panca_dauh
    ad = r.asta_dauh
    pd_class = "wl-dauh-ayu" if pd.quality == "吉" else ("wl-dauh-ala" if pd.quality == "凶" else "")
    ad_class = "wl-dauh-ayu" if ad.quality == "吉" else ("wl-dauh-ala" if ad.quality == "凶" else "")
    dauh_html = f"""
<div class="wl-dauh-grid">
  <div class="wl-dauh-card {pd_class}">
    <div class="dc-title">🕐 Panca Dauh：{_escape_html(pd.name)}</div>
    <div class="dc-deity">{_escape_html(pd.deity)}</div>
    <div style="font-size:0.8em;color:{'#2E6B3B' if pd.quality=='吉' else '#8B1A1A' if pd.quality=='凶' else _LONTAR_SUBTLE};">
      {_escape_html(pd.quality)} — {_escape_html(pd.direction)}
    </div>
  </div>
  <div class="wl-dauh-card {ad_class}">
    <div class="dc-title">🧭 Asta Dauh：{_escape_html(ad.name)}</div>
    <div class="dc-deity">{_escape_html(ad.direction)}</div>
    <div style="font-size:0.8em;color:{'#2E6B3B' if ad.quality=='吉' else '#8B1A1A' if ad.quality=='凶' else _LONTAR_SUBTLE};">
      {_escape_html(ad.quality)} — {_escape_html(ad.deity)}
    </div>
  </div>
</div>
"""

    # ── Pawukon 進度條 ────────────────────────────────────
    pct = (r.day_in_pawukon / 210) * 100
    progress_html = f"""
<div class="wl-progress-label">
  Pawukon 週期進度：第 {r.day_in_pawukon} 天 / 210（{pct:.1f}%）
</div>
<div class="wl-progress-bar">
  <div class="wl-progress-fill" style="width:{pct:.1f}%;"></div>
</div>
"""

    # ── 天文參考 ──────────────────────────────────────────
    astro_html = f"""
<div class="wl-info-row">
  <div class="wl-info-card">
    <span class="ic-label">☀️ 太陽黃經</span>
    <span class="ic-value">{r.sun_longitude:.2f}°</span>
    <span class="ic-sub">Ecliptic Longitude</span>
  </div>
  <div class="wl-info-card">
    <span class="ic-label">{moon_emoji} 月亮黃經</span>
    <span class="ic-value">{r.moon_longitude:.2f}°</span>
    <span class="ic-sub">Ecliptic Longitude</span>
  </div>
  <div class="wl-info-card">
    <span class="ic-label">📐 儒略日</span>
    <span class="ic-value">{r.julian_day:.1f}</span>
    <span class="ic-sub">Julian Day</span>
  </div>
</div>
"""

    # ── 組合完整 HTML ─────────────────────────────────────
    html = f"""
{css}
<div class="wariga-lontar">

  <!-- 頂部橫幅 -->
  <div class="wl-header">
    <div class="wl-title">🏝️ 巴厘傳統 Wariga 排盤 — Ala Ayuning Dewasa</div>
    <div class="wl-subtitle">嚴格依照 Lontar Wariga Dewasa、Wariga Gemet 與 Palalintangan 古典規則</div>
    <div class="wl-date-box">
      {r.year}年{r.month}月{r.day}日 {r.hour:02d}:{r.minute:02d}
      &nbsp;·&nbsp; 巴厘島（{r.latitude:.3f}°N, {r.longitude:.3f}°E）
    </div>
  </div>

  <div class="wl-ornament">✦ ✧ ✦ ✧ ✦</div>

  <div class="wl-body">

    <!-- 左欄 -->
    <div class="wl-left">

      <!-- Wuku 方格矩陣 -->
      <div class="wl-section-title">Pawukon — 30 Wuku 週期矩陣</div>
      <div class="wl-lontar-note">依 Lontar Wariga：210 天 = 30 Wuku × 7 天；當前 Wuku 以金色高亮顯示</div>
      {wuku_grid_html}
      {progress_html}

      <!-- 吉凶判斷 -->
      <div class="wl-section-title">Ala Ayuning Dewasa — 吉凶判斷</div>
      <div class="wl-lontar-note">依 Lontar Wariga Dewasa：Wewāran alah dening Wuku，Wuku alah dening Penanggal/Panglong</div>
      {dewasa_html}
      {pancasuda_html}

      <!-- Sasih 與季節 -->
      <div class="wl-section-title">Sasih 月份 · 季節 · Ayana</div>
      <div class="wl-lontar-note">依 Lontar Wariga：Penanggal/Panglong alah dening Śaśih</div>
      {sasih_html}

      <!-- 月相 -->
      <div class="wl-section-title">月相日 — Penanggal / Panglong</div>
      <div class="wl-lontar-note">依 Lontar Wariga：月盈(Penanggal 1-15)→滿月(Purnama)→月虧(Panglong 1-15)→新月(Tilem)</div>
      {moon_html}

      <!-- 天文參考 -->
      <div class="wl-section-title">天文參考（pyswisseph，僅供校驗）</div>
      {astro_html}

    </div>

    <!-- 右欄 -->
    <div class="wl-right">

      <!-- 核心 Wuku 資訊 -->
      <div class="wl-section-title">當前 Wuku</div>
      <div class="wl-lontar-note">依 Lontar Wariga：Wuku 主宰本日根本性格</div>
      <div class="wl-info-row">
        <div class="wl-info-card" style="border-color:{_LONTAR_ACCENT};background:rgba(201,152,10,0.1);">
          <span class="ic-label">Wuku 名稱</span>
          <span class="ic-value" style="font-size:1.05em;color:{_LONTAR_HEADER};">
            {_escape_html(r.wuku.name)}
          </span>
          <span class="ic-sub">第 {r.wuku.index + 1} Wuku</span>
        </div>
        <div class="wl-info-card">
          <span class="ic-label">Neptu</span>
          <span class="ic-value">{r.wuku.neptu}</span>
          <span class="ic-sub">Wuku 能量值</span>
        </div>
      </div>

      <!-- Wewaran 十類星期 -->
      <div class="wl-section-title">Wewaran — 十類星期</div>
      <div class="wl-lontar-note">依 Lontar Wariga：Eka~Dasa Wara 完整 Neptu/Urip 系統</div>
      {wara_table_html}

      <!-- Dauh 時辰 -->
      <div class="wl-section-title">時辰 — Panca & Asta Dauh</div>
      <div class="wl-lontar-note">依 Lontar Wariga Gemet：精確到小時的傳統時辰劃分</div>
      {dauh_html}

    </div>

  </div><!-- end .wl-body -->

  <div class="wl-ornament">✦ ✧ ✦ ✧ ✦</div>

  <div class="wl-footer">
    嚴格依照 Lontar Wariga、Dasar Wariga 與 Palalintangan 古法 · 堅守古法、忠實還原傳統
  </div>

</div><!-- end .wariga-lontar -->
"""
    return html


# ============================================================
# 現代清晰表格模式
# ============================================================

def render_modern_table(result: WarigaResult) -> str:
    """
    生成現代清晰表格風格的 HTML

    作為古典 Palalintangan 模式的備用，
    以標準 HTML 表格呈現所有 Wariga 資訊。

    回傳：
        str: 現代表格 HTML
    """
    r = result
    d = r.dewasa
    s = r.sasih
    moon_emoji = _moon_phase_emoji(r.penanggal.moon_phase_deg)
    status_text, status_color = _format_dewasa_status(d.is_auspicious)
    penanggal_label = "Penanggal" if r.penanggal.is_penanggal else "Panglong"

    wara_list = [
        r.eka_wara, r.dwi_wara, r.tri_wara,
        r.catur_wara, r.panca_wara, r.sad_wara,
        r.sapta_wara, r.asta_wara, r.sanga_wara,
        r.dasa_wara,
    ]
    wara_rows = ""
    for w in wara_list:
        wara_rows += (
            f"<tr><td>{_escape_html(w.wara_type)}</td>"
            f"<td><b>{_escape_html(w.name)}</b></td>"
            f"<td style='text-align:center'>{w.neptu}</td></tr>"
        )

    ayu_tags = "".join(
        f"<span style='color:green;margin-right:6px'>✅ {_escape_html(l)}</span>"
        for l in d.auspicious_labels
    )
    ala_tags = "".join(
        f"<span style='color:red;margin-right:6px'>⚠️ {_escape_html(l)}</span>"
        for l in d.inauspicious_labels
    )

    penanggal_special = f" ✨ <b>{_escape_html(r.penanggal.special)}</b>" if r.penanggal.special else ""

    html = f"""
<style>
.wt-table {{border-collapse:collapse;width:100%;font-size:0.9em;}}
.wt-table th {{background:#444;color:#fff;padding:4px 8px;}}
.wt-table td {{padding:3px 8px;border-bottom:1px solid #ddd;}}
.wt-table tr:nth-child(odd) td {{background:#f9f9f9;}}
.wt-section {{margin:12px 0 4px;font-weight:bold;font-size:1em;border-left:4px solid #888;padding-left:8px;}}
</style>
<div style="font-family:sans-serif;max-width:700px;">
  <h3>🏝️ Wariga 排盤 — {r.year}年{r.month}月{r.day}日 {r.hour:02d}:{r.minute:02d}</h3>
  <p style="color:#666;font-size:0.85em;">古法依據：Lontar Wariga / Dasar Wariga</p>

  <div class="wt-section">Wuku</div>
  <p>
    <b>{_escape_html(r.wuku.name)}</b>（第 {r.wuku.index + 1} Wuku）
    Neptu = {r.wuku.neptu}<br>
    Pawukon 日序：{r.day_in_pawukon} / 210
  </p>

  <div class="wt-section">Wewaran — 十類星期</div>
  <table class="wt-table">
    <thead><tr><th>Wara 類型</th><th>名稱</th><th>Neptu</th></tr></thead>
    <tbody>{wara_rows}</tbody>
  </table>

  <div class="wt-section">分類</div>
  <p>
    Ingkel: <b>{_escape_html(r.ingkel)}</b> ／
    Watek Alit: <b>{_escape_html(r.watek_alit)}</b> ／
    Watek Madya: <b>{_escape_html(r.watek_madya)}</b> ／
    Lintang: <b>{_escape_html(r.lintang)}</b>
  </p>

  <div class="wt-section">Ala Ayuning Dewasa — 吉凶</div>
  <p style="color:{status_color};font-size:1.05em;font-weight:bold;">{_escape_html(status_text)}</p>
  <p>
    Neptu 總和：{d.neptu_sum}
    ／ Pancasuda：<b>{_escape_html(d.pancasuda)}</b> — {_escape_html(d.pancasuda_meaning)}
  </p>
  <p>{ayu_tags}{ala_tags}</p>

  <div class="wt-section">Sasih 月份 · 季節 · 時辰</div>
  <p>
    Sasih: <b>{_escape_html(s.sasih_name)}</b>（第 {s.sasih_index + 1} 月）
    ／ 季節: {_escape_html(s.season)} / {_escape_html(s.season_cn)}
    ／ Ayana: {_escape_html(s.ayana)}<br>
    {moon_emoji} <b>{_escape_html(penanggal_label)} {r.penanggal.day_number}</b> —
    {_escape_html(r.penanggal.name)}{penanggal_special}<br>
    🕐 Panca Dauh: <b>{_escape_html(r.panca_dauh.name)}</b> （{_escape_html(r.panca_dauh.quality)}）
    ／ 🧭 Asta Dauh: <b>{_escape_html(r.asta_dauh.name)}</b> （{_escape_html(r.asta_dauh.quality)}）
  </p>
</div>
"""
    return html


# ============================================================
# 文字渲染 (Text Rendering)
# ============================================================

def render_text(result: WarigaResult) -> str:
    """
    將 Wariga 計算結果渲染為純文字格式

    參數：
        result (WarigaResult): Wariga 計算結果

    回傳：
        str: 格式化的純文字輸出

    古法依據：Lontar Wariga / Dasar Wariga
    """
    lines = []
    lines.append("=" * 60)
    lines.append("  巴厘傳統 Wariga 日曆 — Ala Ayuning Dewasa")
    lines.append("  古法依據：Lontar Wariga / Dasar Wariga")
    lines.append("=" * 60)
    lines.append("")

    # 基本日期資訊
    lines.append(f"  日期：{result.year}年{result.month}月{result.day}日"
                 f"  {result.hour:02d}:{result.minute:02d}")
    lines.append(f"  座標：{result.latitude:.4f}°N, {result.longitude:.4f}°E")
    lines.append(f"  儒略日：{result.julian_day:.4f}")
    lines.append("")

    # Pawukon 資訊
    lines.append("─" * 60)
    lines.append("  【Pawukon 210天週期】")
    lines.append("─" * 60)
    lines.append(f"  Pawukon 日序：第 {result.day_in_pawukon} 天 / 210")
    lines.append(f"  Wuku：{result.wuku.name}（Neptu = {result.wuku.neptu}）")
    lines.append("")

    # 所有 Wara
    lines.append("─" * 60)
    lines.append("  【Wewaran（十類星期）】")
    lines.append("─" * 60)
    wara_list = [
        result.eka_wara, result.dwi_wara, result.tri_wara,
        result.catur_wara, result.panca_wara, result.sad_wara,
        result.sapta_wara, result.asta_wara, result.sanga_wara,
        result.dasa_wara,
    ]
    for w in wara_list:
        lines.append(f"  {w.wara_type:<16s}：{w.name:<16s}（Neptu = {w.neptu}）")
    lines.append("")

    # 分類
    lines.append("─" * 60)
    lines.append("  【分類 (Ingkel / Watek / Lintang)】")
    lines.append("─" * 60)
    lines.append(f"  Ingkel（動物分類）：{result.ingkel}")
    lines.append(f"  Watek Alit：{result.watek_alit}")
    lines.append(f"  Watek Madya：{result.watek_madya}")
    lines.append(f"  Lintang（星宿）：{result.lintang}")
    lines.append("")

    # 吉凶判斷
    lines.append("─" * 60)
    lines.append("  【Ala Ayuning Dewasa（吉凶判斷）】")
    lines.append("─" * 60)
    d = result.dewasa
    status, _ = _format_dewasa_status(d.is_auspicious)
    lines.append(f"  總體判斷：{status}")
    lines.append(f"  Neptu 總和（Panca + Sapta）：{d.neptu_sum}")
    lines.append(f"  Pancasuda：{d.pancasuda} — {d.pancasuda_meaning}")

    if d.auspicious_labels:
        lines.append("  吉日標記：")
        for label in d.auspicious_labels:
            lines.append(f"    ✅ {label}")
    if d.inauspicious_labels:
        lines.append("  凶日標記：")
        for label in d.inauspicious_labels:
            lines.append(f"    ⚠️ {label}")
    if d.notes:
        lines.append("  備註：")
        for note in d.notes:
            lines.append(f"    📝 {note}")
    lines.append("")

    # 月相日
    penanggal_label = "Penanggal" if result.penanggal.is_penanggal else "Panglong"
    moon_emoji = _moon_phase_emoji(result.penanggal.moon_phase_deg)
    lines.append("─" * 60)
    lines.append("  【月相日（Penanggal / Panglong）】")
    lines.append("─" * 60)
    lines.append(f"  {moon_emoji} {penanggal_label} {result.penanggal.day_number}：{result.penanggal.name}")
    lines.append(f"  月相角度：{result.penanggal.moon_phase_deg:.1f}°  Neptu：{result.penanggal.neptu}")
    if result.penanggal.special:
        lines.append(f"  ✨ 特殊聖日：{result.penanggal.special}")
    lines.append("")

    # 時辰
    lines.append("─" * 60)
    lines.append("  【時辰（Dauh）】")
    lines.append("─" * 60)
    pd = result.panca_dauh
    ad = result.asta_dauh
    lines.append(f"  Panca Dauh：{pd.name}（{pd.quality}）— {pd.deity}")
    lines.append(f"  Asta Dauh：{ad.name}（{ad.quality}）— 方位：{ad.direction}")
    lines.append("")

    # Sasih 與季節
    lines.append("─" * 60)
    lines.append("  【Sasih（月份）與季節】")
    lines.append("─" * 60)
    s = result.sasih
    lines.append(f"  Sasih：{s.sasih_name}（第 {s.sasih_index + 1} 月）")
    lines.append(f"  季節：{s.season} / {s.season_cn}")
    lines.append(f"  Ayana：{s.ayana}")
    lines.append("")

    # 天文參考
    lines.append("─" * 60)
    lines.append("  【天文參考（pyswisseph 計算，僅供參考）】")
    lines.append("─" * 60)
    lines.append(f"  太陽黃經：{result.sun_longitude:.2f}°")
    lines.append(f"  月亮黃經：{result.moon_longitude:.2f}°")
    waluku_note = _get_waluku_note(result.sasih.sasih_index)
    if waluku_note:
        lines.append(f"  Waluku (Orion) 參考：{waluku_note}")
    lines.append("")
    lines.append("=" * 60)

    return "\n".join(lines)


def _get_waluku_note(sasih_index: int) -> str:
    """
    根據 Sasih 提供 Waluku (Orion/犁星) 星座出現的季節參考

    傳統上 Waluku 星座在 Sasih Kasa~Katiga（乾季初期）最為明亮可見，
    用於驗證季節與耕作時機。

    古法依據：Lontar Wariga — Waluku 星座觀測

    回傳：
        str: Waluku 參考說明
    """
    notes = {
        0: "Waluku（犁星/Orion）於東方升起，乾季開始，宜備耕",
        1: "Waluku 在天空高處，乾季持續，宜播種",
        2: "Waluku 西沉，乾季後期，宜照料作物",
        3: "Waluku 不可見，乾季深期",
        4: "Waluku 隱沒期",
        5: "Waluku 隱沒期末，即將再現",
        6: "Waluku 黎明前東方隱現，雨季開始",
        7: "Waluku 晨見，雨季持續",
        8: "Waluku 漸高，雨季中期",
        9: "Waluku 天頂附近，雨季後期",
        10: "Waluku 西斜，雨季將盡",
        11: "Waluku 將沒，過渡至乾季",
    }
    return notes.get(sasih_index, "")


# ============================================================
# SVG 渲染 (SVG Rendering) — 保留舊版相容性
# ============================================================

def render_svg(result: WarigaResult, width=600, height=800) -> str:
    """
    將 Wariga 計算結果渲染為簡易 SVG 圖表（舊版相容性）

    建議改用 render_palalintangan_html() 獲得更完整的視覺效果。

    參數：
        result (WarigaResult): Wariga 計算結果
        width  (int): SVG 寬度（像素）
        height (int): SVG 高度（像素）

    回傳：
        str: SVG 字串

    古法依據：Lontar Wariga / Dasar Wariga
    """
    return _render_svg_fallback(result, width, height)


def _render_svg_fallback(result: WarigaResult, width=600, height=800) -> str:
    """手動 SVG 回退方案"""
    lines = []
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'width="{width}" height="{height}">')
    lines.append(f'<rect width="{width}" height="{height}" '
                 f'fill="#FFF8E7" stroke="#8B4513" stroke-width="2"/>')

    y = 40
    lines.append(f'<text x="{width // 2}" y="{y}" text-anchor="middle" '
                 f'font-size="18" font-weight="bold" fill="#8B4513">'
                 f'巴厘傳統 Wariga 日曆</text>')
    y += 30

    date_str = (f"{result.year}年{result.month}月{result.day}日"
                f" {result.hour:02d}:{result.minute:02d}")
    lines.append(f'<text x="{width // 2}" y="{y}" text-anchor="middle" '
                 f'font-size="14" fill="#333">{date_str}</text>')
    y += 30

    lines.append(f'<text x="{width // 2}" y="{y}" text-anchor="middle" '
                 f'font-size="16" font-weight="bold" fill="#2E8B57">'
                 f'Wuku {result.wuku.name} (Neptu={result.wuku.neptu})</text>')
    y += 25

    status, color = _format_dewasa_status(result.dewasa.is_auspicious)
    lines.append(f'<text x="{width // 2}" y="{y}" text-anchor="middle" '
                 f'font-size="14" fill="{color}">{status}</text>')
    y += 30

    wara_list = [
        result.eka_wara, result.dwi_wara, result.tri_wara,
        result.catur_wara, result.panca_wara, result.sad_wara,
        result.sapta_wara, result.asta_wara, result.sanga_wara,
        result.dasa_wara,
    ]
    for w in wara_list:
        lines.append(f'<text x="40" y="{y}" font-size="11" fill="#555">'
                     f'{w.wara_type}: {w.name} (Neptu={w.neptu})</text>')
        y += 18

    lines.append('</svg>')
    return "\n".join(lines)


# ============================================================
# Streamlit 渲染主入口 — 支援古風/現代雙模式切換
# ============================================================

def render_streamlit(result: WarigaResult):
    """
    使用 Streamlit 元件渲染 Wariga 結果（雙模式）

    提供：
    1. 古典 Lontar 圖形模式（Palalintangan 風格）
    2. 現代清晰表格模式

    參數：
        result (WarigaResult): Wariga 計算結果

    古法依據：Lontar Wariga / Dasar Wariga / Palalintangan
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("🏝️ 巴厘傳統 Wariga 排盤")
    st.caption("嚴格依照 Lontar Wariga Dewasa、Wariga Gemet 與 Palalintangan 古典規則")

    # 模式切換按鈕
    col_mode1, col_mode2, col_spacer = st.columns([1, 1, 4])
    with col_mode1:
        classic_btn = st.button(
            "📜 古典 Lontar 模式",
            key="wariga_classic_mode",
            help="仿古棕櫚葉手稿風格，Palalintangan 方格矩陣視覺",
            width="stretch",
        )
    with col_mode2:
        modern_btn = st.button(
            "📊 現代表格模式",
            key="wariga_modern_mode",
            help="清晰現代表格佈局，快速查閱",
            width="stretch",
        )

    # 初始化模式狀態
    if "wariga_display_mode" not in st.session_state:
        st.session_state["wariga_display_mode"] = "classic"
    if classic_btn:
        st.session_state["wariga_display_mode"] = "classic"
    if modern_btn:
        st.session_state["wariga_display_mode"] = "modern"

    mode = st.session_state.get("wariga_display_mode", "classic")

    if mode == "classic":
        html = render_palalintangan_html(result)
        st.components.v1.html(html, height=1100, scrolling=True)
    else:
        # 現代模式：使用 Streamlit 原生元件 + HTML
        _render_modern_streamlit(result, st)


def _render_modern_streamlit(result: WarigaResult, st):
    """
    現代表格模式 — 使用 Streamlit 原生元件渲染

    保留原有結構並加入新的 Dauh 和 Penanggal 資訊。
    古法依據：Lontar Wariga / Dasar Wariga
    """
    r = result
    d = r.dewasa
    s = r.sasih
    moon_emoji = _moon_phase_emoji(r.penanggal.moon_phase_deg)
    penanggal_label = "Penanggal（月盈）" if r.penanggal.is_penanggal else "Panglong（月虧）"

    # 頂部摘要
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Pawukon 日序：** {r.day_in_pawukon} / 210")
        st.write(f"**Wuku：** {r.wuku.name}（Neptu={r.wuku.neptu}）")
    with col2:
        st.write(f"**Sasih：** {s.sasih_name}（第 {s.sasih_index+1} 月）")
        st.write(f"**季節：** {s.season_cn} / {s.ayana.split('（')[0]}")
    with col3:
        st.write(f"**{moon_emoji} 月相日：** {r.penanggal.day_number} — {r.penanggal.name}")
        if r.penanggal.special:
            st.success(f"✨ {r.penanggal.special}")

    st.markdown("---")

    # Wewaran 表格
    st.markdown("#### 🗓️ Wewaran（十類星期）")
    st.caption("古法依據：Lontar Wariga — Eka~Dasa Wara 完整 Neptu/Urip 系統")
    wara_list = [
        r.eka_wara, r.dwi_wara, r.tri_wara,
        r.catur_wara, r.panca_wara, r.sad_wara,
        r.sapta_wara, r.asta_wara, r.sanga_wara,
        r.dasa_wara,
    ]
    header = "| Wara 類型 | 名稱 | Neptu |"
    sep = "|:----:|:----:|:-----:|"
    rows = [header, sep]
    for w in wara_list:
        rows.append(f"| {w.wara_type} | **{w.name}** | {w.neptu} |")
    st.markdown("\n".join(rows))

    # 分類 + 時辰
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🦁 分類（Ingkel / Watek / Lintang）")
        st.caption("古法依據：Lontar Wariga — 動物分類與星宿")
        st.write(f"**Ingkel：** {r.ingkel}")
        st.write(f"**Watek Alit：** {r.watek_alit}")
        st.write(f"**Watek Madya：** {r.watek_madya}")
        st.write(f"**Lintang：** {r.lintang}")
    with col_b:
        st.markdown("#### 🕐 時辰（Panca & Asta Dauh）")
        st.caption("古法依據：Lontar Wariga Gemet — 精確到小時的時辰劃分")
        pd = r.panca_dauh
        ad = r.asta_dauh
        pd_color = "🟢" if pd.quality == "吉" else ("🔴" if pd.quality == "凶" else "⚪")
        ad_color = "🟢" if ad.quality == "吉" else ("🔴" if ad.quality == "凶" else "⚪")
        st.write(f"**Panca Dauh：** {pd_color} {pd.name}（{pd.quality}）")
        st.write(f"  {pd.deity} — {pd.direction}")
        st.write(f"**Asta Dauh：** {ad_color} {ad.name}（{ad.quality}）")
        st.write(f"  方位：{ad.direction}")

    # 吉凶判斷
    st.markdown("#### ⚖️ Ala Ayuning Dewasa（吉凶判斷）")
    st.caption("古法依據：Lontar Wariga Dewasa — Wewāran alah dening Wuku")
    if d.is_auspicious:
        st.success(f"✅ 吉日 (Dewasa Ayu) — Neptu 總和 = {d.neptu_sum}")
    else:
        st.warning(f"⚠️ 需謹慎 (Dewasa Ala) — Neptu 總和 = {d.neptu_sum}")
    st.write(f"**Pancasuda：** {d.pancasuda} — {d.pancasuda_meaning}")

    if d.auspicious_labels:
        for label in d.auspicious_labels:
            st.write(f"  ✅ {label}")
    if d.inauspicious_labels:
        for label in d.inauspicious_labels:
            st.write(f"  ⚠️ {label}")
    if d.notes:
        for note in d.notes:
            st.info(f"📝 {note}")
