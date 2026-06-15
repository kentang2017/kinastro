"""Render a simplified Liu Ren board PNG for PDF embedding."""

from __future__ import annotations

from io import BytesIO
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # pragma: no cover
    Image = None
    ImageDraw = None
    ImageFont = None

BOARD_GRID: list[list[str | None]] = [
    ["巳", "午", "未", "申"],
    ["辰", None, None, "酉"],
    ["卯", None, None, "戌"],
    ["寅", "丑", "子", "亥"],
]


def _load_font(size: int):
    if ImageFont is None:
        raise RuntimeError("Pillow is required to render Liu Ren board images.")
    for name in ("msyh.ttc", "NotoSansCJKtc-Regular.otf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_liuren_board_png(
    chart: dict[str, Any],
    *,
    benming_zhi: str = "",
    width: int = 1200,
    height: int = 1200,
) -> bytes:
    """Draw a 4×4 Liu Ren square board with tian/jiang labels."""
    if Image is None or ImageDraw is None:
        raise RuntimeError("Pillow is required to render Liu Ren board images.")

    di_to_tian = chart.get("地轉天盤", {})
    di_to_jiang = chart.get("地轉天將", {})
    san_chuan = chart.get("三傳", {})
    day_gz = chart.get("_day_gz", chart.get("日期", "")[:2])

    image = Image.new("RGB", (width, height), "#1a1a2e")
    draw = ImageDraw.Draw(image)
    title_font = _load_font(42)
    cell_font = _load_font(24)
    small_font = _load_font(18)

    margin = 48
    top = 120
    cell_w = (width - margin * 2) // 4
    cell_h = (height - top - margin) // 4

    draw.rounded_rectangle((margin, 20, width - margin, 90), radius=16, fill="#2d2d44")
    draw.text((margin + 20, 36), f"大六壬 SR 課式  {day_gz}", fill="#f5d76e", font=title_font)

    center = (
        margin + cell_w,
        top + cell_h,
        margin + cell_w * 3,
        top + cell_h * 3,
    )
    draw.rounded_rectangle(center, radius=20, fill="#252538", outline="#666", width=2)
    y = center[1] + 24
    for label in ("初傳", "中傳", "末傳"):
        vals = san_chuan.get(label, [])
        text = f"{label}: {vals[0] if vals else '—'} {vals[1] if len(vals) > 1 else ''}"
        draw.text((center[0] + 24, y), text, fill="#ddd", font=cell_font)
        y += 42
    if benming_zhi:
        draw.text((center[0] + 24, center[3] - 48), f"本命支 {benming_zhi}", fill="#9e9e9e", font=small_font)

    for row in range(4):
        for col in range(4):
            branch = BOARD_GRID[row][col]
            if not branch:
                continue
            x1 = margin + col * cell_w + 4
            y1 = top + row * cell_h + 4
            x2 = x1 + cell_w - 8
            y2 = y1 + cell_h - 8
            draw.rounded_rectangle((x1, y1, x2, y2), radius=12, fill="#2a2a3d", outline="#555", width=2)
            tian = di_to_tian.get(branch, "")
            jiang = di_to_jiang.get(branch, "")
            draw.text((x1 + 12, y1 + 10), branch, fill="#f5d76e", font=cell_font)
            draw.text((x1 + 12, y1 + 42), f"天{tian}", fill="#81d4fa", font=small_font)
            draw.text((x1 + 12, y1 + 68), jiang, fill="#ef9a9a", font=small_font)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()