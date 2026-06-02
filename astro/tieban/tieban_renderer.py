"""
astro/tieban/tieban_renderer.py — 鐵板神數 SVG 渲染器

Tie Ban Shen Shu SVG Renderer
"""


def render_tieban_chart_svg(result, language: str = "zh") -> str:
    """
    Render Tie Ban Shen Shu chart as an interactive SVG.

    Parameters
    ----------
    result : TieBanResult
        The calculated result from TieBanShenShu.calculate()
    language : str
        "zh" for Chinese, "en" for English

    Returns
    -------
    str
        SVG string for embedding in Streamlit via st.components.v1.html()
    """
    # Import here to avoid circular imports
    from astro.tieban.tieban_calculator import TieBanResult, Ganzhi

    # Build SVG components
    svg_parts = [
        '<svg viewBox="0 0 600 700" xmlns="http://www.w3.org/2000/svg" '
        'style="max-width:560px;width:100%;display:block;margin:auto;'
        'border-radius:14px;background:#090f1f;font-family:Segoe UI,Microsoft YaHei,sans-serif">',
        '<defs>',
        '<style>',
        '.title { font: bold 18px/1.4 "Segoe UI","Microsoft YaHei",sans-serif; fill: #f0e68c; }',
        '.subtitle { font: 14px/1.4 "Segoe UI","Microsoft YaHei",sans-serif; fill: #ddd; }',
        '.label { font: 12px "Segoe UI","Microsoft YaHei",sans-serif; fill: #888; }',
        '.value { font: 14px "Segoe UI","Microsoft YaHei",sans-serif; fill: #fff; }',
        '.verse { font: 13px/1.5 "Segoe UI","Microsoft YaHei",sans-serif; fill: #ccc; }',
        '.box { fill: #1e2a4a; stroke: #5a6b9b; stroke-width: 1; }',
        '.border { fill: none; stroke: #3a4b7b; stroke-width: 1; }',
        '.line { stroke: #5a6b9b; stroke-width: 1; }',
        '</style>',
        '</defs>',
        '<rect x="20" y="20" width="560" height="660" rx="12" class="box"/>',
        '<rect x="25" y="25" width="550" height="650" rx="10" class="border"/>',
    ]

    # Title
    title_zh = "鐵板神數推算結果"
    title_en = "Tie Ban Shen Shu Result"
    svg_parts.append(
        f'<text x="300" y="55" text-anchor="middle" class="title">'
        f"{title_zh if language == 'zh' else title_en}</text>"
    )

    y = 85

    # Basic info block
    svg_parts.extend([
        '<g transform="translate(40,90)">',
        '<rect x="0" y="0" width="520" height="120" rx="6" class="border"/>',
    ])

    # Birth info
    bd = result.birth_data
    gz = bd.year_gz
    birth_text_zh = f"出生：{bd.birth_dt.strftime('%Y-%m-%d %H:%M')}（{gz}年 {bd.month_gz}月 {bd.day_gz}日 {bd.hour_gz}日）"
    birth_text_en = f"Birth: {bd.birth_dt.strftime('%Y-%m-%d %H:%M')} ({gz} Year, {bd.month_gz} Month, {bd.day_gz} Day, {bd.hour_gz} Hour)"

    svg_parts.append(
        f'<text x="20" y="25" class="label">'
        f"{birth_text_zh if language == 'zh' else birth_text_en}</text>"
    )

    # Palace info
    svg_parts.append(
        f'<text x="20" y="48" class="value">'
        f"命宮：{result.ming_palace} · 身宮：{result.shen_palace}</text>"
    )

    # Five Elements
    if result.wuxing_ju:
        svg_parts.append(
            f'<text x="20" y="70" class="value">五行局：{result.wuxing_ju}</text>'
        )

    # Verse number
    if result.tieban_number:
        svg_parts.append(
            f'<text x="20" y="92" class="value">神數號碼：{result.tieban_number}</text>'
        )

    svg_parts.append("</g>")

    # Verse text (main content)
    y += 140
    svg_parts.extend([
        f'<g transform="translate(40,{y})">',
        '<rect x="0" y="0" width="520" height="200" rx="6" class="border"/>',
    ])

    if result.verse:
        # Wrap text (simplified - just truncate for now)
        verse_text = result.verse[:150] + "..." if len(result.verse) > 150 else result.verse
        svg_parts.extend([
            f'<text x="20" y="25" class="label">{language == "zh" and "條文" or "Verse"}:</text>',
            f'<text x="20" y="45" class="verse">{verse_text}</text>',
        ])
    else:
        svg_parts.append(
            f'<text x="20" y="25" class="label">'
            f"{language == 'zh' and '無條文數據' or 'No verse data'}</text>"
        )

    svg_parts.append("</g>")

    # Palaces grid (12 palaces)
    y += 240
    svg_parts.extend([
        f'<g transform="translate(40,{y})">',
        '<rect x="0" y="0" width="520" height="160" rx="6" class="border"/>',
        '<text x="20" y="25" class="label">'
        f"{language == 'zh' and '十二宮條文' or 'Palaces'}:</text>",
    ])

    # Draw 12 palaces in 3 rows of 4 (fit within 520px content area)
    palace_labels_zh = ["命", "兄弟", "夫妻", "子女", "財帛", "疾病", "奴僕", "配偶", "田宅", "官祿", "遷流", "財庫"]
    palace_labels_en = ["Ming", "Siblings", "Spouse", "Children", "Wealth", "Health", "Servants", "Spouse", "Property", "Career", "Migration", "Treasure"]

    labels = palace_labels_zh if language == 'zh' else palace_labels_en
    palaces = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
    palace_names = ["寅宫", "卯宫", "辰宫", "巳宫", "午宫", "未宫", "申宫", "酉宫", "戌宫", "亥宫", "子宫", "丑宫"]
    palace_names_en = ["Yin", "Mao", "Chen", "Si", "Wu", "Wei", "Shen", "You", "Xu", "Hai", "Zi", "Chou"]

    for i, p in enumerate(palaces):
        row = i // 4
        col = i % 4
        x = 20 + col * 125
        y_offset = 42 + row * 40

        # Palace box
        svg_parts.append(
            f'<rect x="{x}" y="{y_offset}" width="52" height="24" rx="3" '
            f'stroke="#6a7b9b" fill="#1e2a4a" stroke-width="1"/>'
        )

        # Palace letter
        svg_parts.append(
            f'<text x="{x + 26}" y="{y_offset + 17}" text-anchor="middle" '
            f'class="value">{p}</text>'
        )

        # Label
        label = labels[i] if i < len(labels) else p
        svg_parts.append(
            f'<text x="{x + 26}" y="{y_offset + 36}" text-anchor="middle" class="label" font-size="10">{label}</text>'
        )

        # Verse (if available)
        if result.palace_verses and i < 12:
            pkey = palace_names[i] if language == 'zh' else palace_names_en[i]
            if pkey in result.palace_verses:
                v = result.palace_verses[pkey]
                verse_raw = v.get("verse", "")
                verse_text = (verse_raw[:8] + "…") if len(verse_raw) > 8 else verse_raw
                if verse_text:
                    svg_parts.append(
                        f'<text x="{x + 26}" y="{y_offset + 48}" text-anchor="middle" class="verse" font-size="9">{verse_text}</text>'
                    )

    svg_parts.append("</g>")

    # Footer
    y += 200
    svg_parts.extend([
        f'<g transform="translate(40,{y})">',
        '<rect x="0" y="0" width="520" height="40" rx="6" class="border"/>',
        f'<text x="260" y="25" text-anchor="middle" class="subtitle" fill="#6a7b9b">',
        f"{language == 'zh' and '生成時間：' or 'Generated: '}"
        f"{result.birth_data.birth_dt.strftime('%Y-%m-%d %H:%M:%S')}",
        '</text>',
        "</g>",
    ])

    svg_parts.append("</svg>")
    return "".join(svg_parts)


# Re-export for convenience
__all__ = ["render_tieban_chart_svg"]
