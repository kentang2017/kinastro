"""
巴厘傳統 Wariga 渲染模組 (Renderer for Balinese Wariga Calendar)

提供文字輸出與基本 SVG 渲染功能，用於展示 Wariga 計算結果。
文字版本輸出完整的 Wariga 資訊；SVG 版本以簡易圖表呈現 Wuku 與 Wewaran 概覽。

古法依據：Lontar Wariga / Dasar Wariga
"""

import math

try:
    import svgwrite
    HAS_SVGWRITE = True
except ImportError:
    HAS_SVGWRITE = False

from .calculator import WarigaResult


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
    status = "✅ 吉日 (Dewasa Ayu)" if d.is_auspicious else "⚠️ 需謹慎 (Dewasa Ala)"
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

    # Waluku (Orion) 參考
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
# SVG 渲染 (SVG Rendering)
# ============================================================

def render_svg(result: WarigaResult, width=600, height=800) -> str:
    """
    將 Wariga 計算結果渲染為簡易 SVG 圖表

    包含：
    - 標題與日期
    - Wuku 資訊方塊
    - Wewaran 列表
    - 吉凶狀態指示

    參數：
        result (WarigaResult): Wariga 計算結果
        width  (int): SVG 寬度（像素）
        height (int): SVG 高度（像素）

    回傳：
        str: SVG 字串

    古法依據：Lontar Wariga / Dasar Wariga
    """
    if not HAS_SVGWRITE:
        return _render_svg_fallback(result, width, height)

    dwg = svgwrite.Drawing(size=(f"{width}px", f"{height}px"))
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height),
                      fill="#FFF8E7", stroke="#8B4513", stroke_width=2))

    y = 30

    # 標題
    dwg.add(dwg.text("巴厘傳統 Wariga 日曆",
                      insert=(width / 2, y),
                      text_anchor="middle",
                      font_size="18px", font_weight="bold",
                      fill="#8B4513"))
    y += 20
    dwg.add(dwg.text("Ala Ayuning Dewasa",
                      insert=(width / 2, y),
                      text_anchor="middle",
                      font_size="14px", fill="#A0522D"))
    y += 30

    # 日期
    date_str = (f"{result.year}年{result.month}月{result.day}日"
                f" {result.hour:02d}:{result.minute:02d}")
    dwg.add(dwg.text(date_str,
                      insert=(width / 2, y),
                      text_anchor="middle",
                      font_size="14px", fill="#333"))
    y += 30

    # Wuku 方塊
    box_w, box_h = 200, 60
    box_x = (width - box_w) / 2
    color = "#2E8B57" if result.dewasa.is_auspicious else "#CD5C5C"
    dwg.add(dwg.rect(insert=(box_x, y), size=(box_w, box_h),
                      rx=8, ry=8, fill=color, fill_opacity=0.15,
                      stroke=color, stroke_width=2))
    dwg.add(dwg.text(f"Wuku {result.wuku.name}",
                      insert=(width / 2, y + 25),
                      text_anchor="middle",
                      font_size="16px", font_weight="bold", fill=color))
    dwg.add(dwg.text(f"Neptu = {result.wuku.neptu}",
                      insert=(width / 2, y + 48),
                      text_anchor="middle",
                      font_size="12px", fill=color))
    y += box_h + 20

    # Pawukon 日序
    dwg.add(dwg.text(f"Pawukon 日序：{result.day_in_pawukon} / 210",
                      insert=(width / 2, y),
                      text_anchor="middle",
                      font_size="12px", fill="#666"))
    y += 25

    # Wewaran 列表
    dwg.add(dwg.text("Wewaran（十類星期）",
                      insert=(30, y),
                      font_size="14px", font_weight="bold", fill="#8B4513"))
    y += 5
    dwg.add(dwg.line(start=(30, y), end=(width - 30, y),
                      stroke="#8B4513", stroke_width=1))
    y += 18

    wara_list = [
        result.eka_wara, result.dwi_wara, result.tri_wara,
        result.catur_wara, result.panca_wara, result.sad_wara,
        result.sapta_wara, result.asta_wara, result.sanga_wara,
        result.dasa_wara,
    ]
    for w in wara_list:
        dwg.add(dwg.text(f"{w.wara_type}",
                          insert=(40, y),
                          font_size="11px", fill="#555"))
        dwg.add(dwg.text(f"{w.name}",
                          insert=(180, y),
                          font_size="11px", font_weight="bold", fill="#333"))
        dwg.add(dwg.text(f"Neptu={w.neptu}",
                          insert=(320, y),
                          font_size="11px", fill="#888"))
        y += 18

    y += 10

    # 分類
    dwg.add(dwg.text("分類",
                      insert=(30, y),
                      font_size="14px", font_weight="bold", fill="#8B4513"))
    y += 5
    dwg.add(dwg.line(start=(30, y), end=(width - 30, y),
                      stroke="#8B4513", stroke_width=1))
    y += 18
    for label, value in [
        ("Ingkel", result.ingkel),
        ("Watek Alit", result.watek_alit),
        ("Watek Madya", result.watek_madya),
        ("Lintang", result.lintang),
    ]:
        dwg.add(dwg.text(f"{label}：",
                          insert=(40, y),
                          font_size="11px", fill="#555"))
        dwg.add(dwg.text(value,
                          insert=(180, y),
                          font_size="11px", font_weight="bold", fill="#333"))
        y += 18

    y += 10

    # 吉凶判斷
    d = result.dewasa
    status_text = "✅ 吉日 (Dewasa Ayu)" if d.is_auspicious else "⚠️ 需謹慎 (Dewasa Ala)"
    status_color = "#2E8B57" if d.is_auspicious else "#CD5C5C"
    dwg.add(dwg.text("吉凶判斷",
                      insert=(30, y),
                      font_size="14px", font_weight="bold", fill="#8B4513"))
    y += 5
    dwg.add(dwg.line(start=(30, y), end=(width - 30, y),
                      stroke="#8B4513", stroke_width=1))
    y += 18
    dwg.add(dwg.text(status_text,
                      insert=(40, y),
                      font_size="13px", font_weight="bold", fill=status_color))
    y += 18
    dwg.add(dwg.text(f"Neptu 總和：{d.neptu_sum}",
                      insert=(40, y),
                      font_size="11px", fill="#555"))
    y += 18
    dwg.add(dwg.text(f"Pancasuda：{d.pancasuda}",
                      insert=(40, y),
                      font_size="11px", fill="#555"))
    y += 15
    dwg.add(dwg.text(f"  — {d.pancasuda_meaning}",
                      insert=(40, y),
                      font_size="10px", fill="#888"))
    y += 20

    # Sasih 與季節
    s = result.sasih
    dwg.add(dwg.text("Sasih 與季節",
                      insert=(30, y),
                      font_size="14px", font_weight="bold", fill="#8B4513"))
    y += 5
    dwg.add(dwg.line(start=(30, y), end=(width - 30, y),
                      stroke="#8B4513", stroke_width=1))
    y += 18
    dwg.add(dwg.text(f"Sasih：{s.sasih_name}（第 {s.sasih_index + 1} 月）",
                      insert=(40, y),
                      font_size="11px", fill="#333"))
    y += 18
    dwg.add(dwg.text(f"季節：{s.season} / {s.season_cn}",
                      insert=(40, y),
                      font_size="11px", fill="#333"))
    y += 18
    dwg.add(dwg.text(f"Ayana：{s.ayana}",
                      insert=(40, y),
                      font_size="11px", fill="#333"))

    return dwg.tostring()


def _render_svg_fallback(result: WarigaResult, width=600, height=800) -> str:
    """
    無 svgwrite 時的手動 SVG 回退方案

    使用純字串拼接產生最基本的 SVG 輸出。

    回傳：
        str: 手動拼接的 SVG 字串
    """
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

    status = "吉日" if result.dewasa.is_auspicious else "需謹慎"
    color = "#2E8B57" if result.dewasa.is_auspicious else "#CD5C5C"
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
# Streamlit 渲染 (可選，當 Streamlit 可用時)
# ============================================================

def render_streamlit(result: WarigaResult):
    """
    使用 Streamlit 元件渲染 Wariga 結果

    若 Streamlit 不可用則略過。

    參數：
        result (WarigaResult): Wariga 計算結果

    古法依據：Lontar Wariga / Dasar Wariga
    """
    try:
        import streamlit as st
    except ImportError:
        return

    st.subheader("🏝️ 巴厘傳統 Wariga 日曆")
    st.caption("古法依據：Lontar Wariga / Dasar Wariga")

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**日期：** {result.year}年{result.month}月{result.day}日"
                 f" {result.hour:02d}:{result.minute:02d}")
        st.write(f"**Pawukon 日序：** {result.day_in_pawukon} / 210")
    with col2:
        st.write(f"**Wuku：** {result.wuku.name}（Neptu = {result.wuku.neptu}）")
        st.write(f"**Sasih：** {result.sasih.sasih_name}")

    # Wewaran 表格
    st.markdown("#### Wewaran（十類星期）")
    header = "| 類型 | 名稱 | Neptu |"
    separator = "|:----:|:----:|:-----:|"
    rows = [header, separator]
    wara_list = [
        result.eka_wara, result.dwi_wara, result.tri_wara,
        result.catur_wara, result.panca_wara, result.sad_wara,
        result.sapta_wara, result.asta_wara, result.sanga_wara,
        result.dasa_wara,
    ]
    for w in wara_list:
        rows.append(f"| {w.wara_type} | {w.name} | {w.neptu} |")
    st.markdown("\n".join(rows))

    # 分類
    st.markdown("#### 分類")
    st.write(f"**Ingkel：** {result.ingkel}")
    st.write(f"**Watek Alit：** {result.watek_alit}")
    st.write(f"**Watek Madya：** {result.watek_madya}")
    st.write(f"**Lintang：** {result.lintang}")

    # 吉凶
    st.markdown("#### Ala Ayuning Dewasa（吉凶判斷）")
    d = result.dewasa
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

    # 季節
    st.markdown("#### Sasih 與季節")
    s = result.sasih
    st.write(f"**Sasih：** {s.sasih_name}（第 {s.sasih_index + 1} 月）")
    st.write(f"**季節：** {s.season} / {s.season_cn}")
    st.write(f"**Ayana：** {s.ayana}")
