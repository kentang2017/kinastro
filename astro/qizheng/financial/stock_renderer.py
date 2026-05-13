"""
股票靈運占星儀渲染模組 (Stock Fortune Astrology UI Renderer)

Streamlit UI，包含：
- 股票代碼輸入與資訊卡
- 上市出生盤行星列表
- 流日流時吉凶時間軸
- 股價強弱度視覺化（七政四餘傳統語）
- AI 解讀整合
"""

from __future__ import annotations

import math
from datetime import date, datetime, timezone as tz_cls, timedelta
from typing import Optional

import streamlit as st


# Maximum length for bad-planets display string
_MAX_BAD_PLANETS_STR_LEN = 60

# Forecast tuning constants (Gann-style golden ratio projection)
_MIN_RANGE_PCT_OF_PRICE = 0.05
_MIN_PRICE_FLOOR = 0.01
_SCORE_BOOST_DIVISOR = 60.0
_MAX_SCORE_BOOST = 0.2
_RATIO_CENTER = 50.0
_RATIO_BIAS_DIVISOR = 100.0
_RATIO_BIAS_WEIGHT = 0.6
_MIN_TREND_FACTOR = 0.65
_MAX_TREND_FACTOR = 1.65
_BEARISH_RATIO_STRONG = 35.0
_BEARISH_RATIO_MILD = 45.0
_BEARISH_SCORE_THRESHOLD = -4
_GOLDEN_RATIO_STEPS = (0.236, 0.382, 0.618, 1.0, 1.618)
_FORECAST_HORIZONS = ("1個月", "3個月", "6個月", "1年", "3年以上")
_BULLISH_FORECAST_COLORS = ("#60a5fa", "#38bdf8", "#86efac", "#facc15", "#FFD700")
_BEARISH_FORECAST_COLORS = ("#fb923c", "#f87171", "#f87171", "#fb7185", "#f87171")


# ============================================================
# 主要渲染入口
# ============================================================

def render_stock_fortune_tab(input_tz: float = 8.0):
    """
    渲染「股票靈運占星儀」分頁。

    Parameters:
        input_tz: 預設時區（從外層上下文傳入）
    """
    import plotly.graph_objects as go

    from .stock_fetcher import fetch_stock_info, get_display_name, get_price_ratio, get_strength_label
    from .stock_calculator import compute_stock_chart, compute_daily_fortune

    # ── 頁眉 ─────────────────────────────────────────────
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, rgba(180,120,0,0.18), rgba(60,30,10,0.35));
            border: 1px solid rgba(255,200,50,0.3);
            border-radius: 14px;
            padding: 16px 20px;
            margin-bottom: 18px;
        ">
        <span style="font-size:1.15em;font-weight:700;color:#FFD700;">
        📈 股票靈運占星儀 / Stock Fortune Astrologer
        </span><br/>
        <span style="color:#d4b860;font-size:0.92em;">
        以七政四餘星曜之力，洞察股票靈運。以上市日為「出生盤」，結合流日流時吉凶，判斷股票強弱。<br/>
        Using the Seven Governors &amp; Four Remainders, read the spirit fortune of any stock.
        IPO date as birth chart · Daily &amp; hourly auspice · Price strength analysis.
        </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Sidebar-style 輸入區（放在頁面上方兩欄）───────────
    col_input, col_info = st.columns([1, 2], gap="medium")

    with col_input:
        st.markdown("#### 🔍 股票查詢 / Stock Query")

        ticker_input = st.text_input(
            "股票代碼 / Ticker",
            value=st.session_state.get("_stock_ticker", ""),
            placeholder="如 700.HK / AAPL / 600519.SS / 000333.SZ",
            key="_stock_ticker_input",
            help="港股：700 或 700.HK；美股：AAPL；上交所：600519.SS；深交所：000333.SZ",
        )

        fetch_btn = st.button("📡 擷取股票資訊 / Fetch Stock Info", key="_stock_fetch_btn",
                               width="stretch")

        if fetch_btn and ticker_input.strip():
            st.session_state["_stock_ticker"] = ticker_input.strip()
            st.session_state.pop("_stock_info", None)   # 清除舊快取

        # 自動觸發：若 session 中有 ticker 但無 info
        active_ticker = st.session_state.get("_stock_ticker", "").strip()
        if active_ticker and "_stock_info" not in st.session_state:
            with st.spinner(f"擷取 {active_ticker} 中… / Fetching {active_ticker}…"):
                stock = fetch_stock_info(active_ticker)
                st.session_state["_stock_info"] = stock

        stock = st.session_state.get("_stock_info")
        if stock and not stock.error:
            current_ipo_ticker = (stock.normalized_ticker or active_ticker).strip().upper()
            last_ipo_ticker = st.session_state.get("_stock_ipo_source_ticker", "")
            if current_ipo_ticker and current_ipo_ticker != last_ipo_ticker:
                st.session_state["_stock_ipo_date"] = stock.ipo_date or date(2000, 1, 1)
                st.session_state["_stock_ipo_source_ticker"] = current_ipo_ticker

        if stock and stock.error:
            st.error(f"⚠️ {stock.error}")
            stock = None

    # ── 股票資訊卡 ────────────────────────────────────────
    with col_info:
        if stock and not stock.error:
            _render_stock_card(stock)

    if not stock or stock.error:
        st.info(
            "請輸入股票代碼並點擊「擷取股票資訊」。\n"
            "/ Please enter a ticker and click 'Fetch Stock Info'."
        )
        _render_ticker_examples()
        return

    # ── IPO 日期/時間選擇 ─────────────────────────────────
    st.divider()
    st.markdown("#### 🗓 上市出生盤 / IPO Birth Chart")

    col_d, col_t, col_tz2 = st.columns(3)
    with col_d:
        default_ipo = stock.ipo_date or date(2000, 1, 1)
        ipo_date = st.date_input(
            "上市日期 / IPO Date",
            value=default_ipo,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            key="_stock_ipo_date",
        )
    with col_t:
        ipo_time = st.time_input(
            "上市時間 / IPO Time（預設 09:30）",
            value=datetime.strptime("09:30", "%H:%M").time(),
            step=60,
            key="_stock_ipo_time",
        )
    with col_tz2:
        ipo_tz = st.number_input(
            "時區 / Timezone",
            value=float(input_tz),
            format="%.1f",
            min_value=-12.0, max_value=14.0, step=0.5,
            key="_stock_ipo_tz",
        )

    st.caption(
        "💡 若 yfinance 已自動偵測上市日期，已預填於上方。"
        " / IPO date auto-filled from yfinance when available."
    )

    # ── 流日流時選擇 ──────────────────────────────────────
    st.divider()
    st.markdown("#### ⏰ 流日流時查詢 / Daily & Hourly Transit")

    col_qd, col_qh = st.columns(2)
    with col_qd:
        query_date = st.date_input(
            "查詢日期 / Query Date",
            value=date.today(),
            key="_stock_query_date",
        )
    with col_qh:
        query_hour = st.slider(
            "查詢時辰（24小時）/ Query Hour (24h)",
            min_value=0, max_value=23,
            value=datetime.now().hour,
            key="_stock_query_hour",
            help="選擇要查詢的時辰（整點）/ Select hour to query",
        )
        st.caption(f"已選：{query_hour:02d}:00 — {query_hour:02d}:59")

    # ── 計算 ──────────────────────────────────────────────
    with st.spinner("🔮 計算股票靈運… / Computing stock fortune…"):
        try:
            stock_data = compute_stock_chart(
                ipo_year=ipo_date.year, ipo_month=ipo_date.month, ipo_day=ipo_date.day,
                ipo_hour=ipo_time.hour, ipo_minute=ipo_time.minute,
                timezone=float(ipo_tz),
                current_price=stock.current_price,
                week52_high=stock.week52_high,
                week52_low=stock.week52_low,
                query_year=query_date.year, query_month=query_date.month,
                query_day=query_date.day,
                query_hour=query_hour,
            )
        except Exception as exc:
            st.error(f"計算錯誤 / Computation error: {exc}")
            st.exception(exc)
            return

    # ── 結果分頁 ──────────────────────────────────────────
    tab_ipo, tab_daily, tab_strength, tab_wuxing, tab_ai = st.tabs([
        "🌠 上市出生盤 / IPO Chart",
        "📅 流日流時吉凶 / Daily Fortune",
        "💹 股價強弱度 / Price Strength",
        "🀄 名學五行 / Name Wuxing",
        "🤖 AI 靈運解讀 / AI Reading",
    ])

    with tab_ipo:
        _render_ipo_planets(stock_data, stock, go)

    with tab_daily:
        _render_daily_fortune(stock_data, go, query_date, query_hour)

    with tab_strength:
        _render_price_strength(stock, stock_data, go)

    with tab_wuxing:
        _render_name_wuxing(stock)

    with tab_ai:
        _render_ai_reading(stock, stock_data, input_tz)


# ============================================================
# 子渲染函數
# ============================================================

def _render_stock_card(stock):
    """渲染股票資訊卡（中英名稱、即時股價、漲跌幅）"""
    from .stock_fetcher import get_display_name

    price_str = f"{stock.current_price:.2f}" if stock.current_price else "—"
    currency = stock.currency or ""

    # 中文名稱行：優先顯示中文名，再顯示英文名
    zh_name_html = ""
    if stock.name_zh:
        zh_name_html = (
            f'<div style="font-size:1.15em;font-weight:700;color:#FFD700;margin-bottom:2px;">'
            f'{stock.name_zh}'
            f'</div>'
        )
        en_name_html = (
            f'<div style="font-size:0.82em;color:#d4b860;margin-bottom:2px;">'
            f'{stock.name_en}</div>'
        ) if stock.name_en else ""
    else:
        display_name = get_display_name(stock)
        zh_name_html = (
            f'<div style="font-size:1.15em;font-weight:700;color:#FFD700;margin-bottom:2px;">'
            f'{display_name}'
            f'</div>'
        )
        en_name_html = ""

    if stock.price_change is not None:
        change_color = "#86efac" if stock.price_change >= 0 else "#f87171"
        change_icon = "▲" if stock.price_change >= 0 else "▼"
        change_str = f"{change_icon} {abs(stock.price_change):.2f}%"
    else:
        change_color, change_str = "#9090b8", "—"

    mktcap_str = ""
    if stock.market_cap:
        mc = stock.market_cap
        if mc >= 1e12:
            mktcap_str = f"{mc/1e12:.2f}T {currency}"
        elif mc >= 1e9:
            mktcap_str = f"{mc/1e9:.2f}B {currency}"
        elif mc >= 1e6:
            mktcap_str = f"{mc/1e6:.2f}M {currency}"

    w52h_str = f"{stock.week52_high:.2f}" if stock.week52_high is not None else "—"
    w52l_str = f"{stock.week52_low:.2f}" if stock.week52_low is not None else "—"

    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg,rgba(40,25,5,0.65),rgba(80,50,10,0.45));
            border: 1px solid rgba(255,200,50,0.35);
            border-radius: 14px;
            padding: 16px 20px;
        ">
        {zh_name_html}
        {en_name_html}
        <div style="color:#d4b860;font-size:0.82em;margin-bottom:10px;">
            {stock.normalized_ticker}
            {"&nbsp;|&nbsp;" + stock.exchange if stock.exchange else ""}
            {"&nbsp;|&nbsp;" + stock.sector if stock.sector else ""}
        </div>
        <div style="font-size:1.6em;font-weight:700;color:#fff;margin-bottom:2px;">
            {price_str} <span style="font-size:0.55em;color:#b0b8d8;">{currency}</span>
            &nbsp;<span style="font-size:0.6em;color:{change_color};">{change_str}</span>
        </div>
        <div style="font-size:0.82em;color:#9090b8;margin-top:6px;">
            52W H: <span style="color:#86efac;">{w52h_str}</span>
            &nbsp;|&nbsp;
            52W L: <span style="color:#f87171;">{w52l_str}</span>
            {"&nbsp;|&nbsp;市值 " + mktcap_str if mktcap_str else ""}
        </div>
        {"<div style='font-size:0.82em;color:#d4b860;margin-top:4px;'>上市日 IPO: " + str(stock.ipo_date) + "</div>" if stock.ipo_date else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_ticker_examples():
    """顯示股票代碼範例說明"""
    st.markdown(
        """
        <div style="
            background:rgba(30,20,60,0.4);border:1px solid rgba(180,140,255,0.2);
            border-radius:10px;padding:12px 16px;margin-top:12px;
        ">
        <strong style="color:#c8aaff;">📋 支援格式 / Supported Formats</strong><br/>
        <ul style="color:#b0b8d8;font-size:0.88em;margin:6px 0 0 0;padding-left:18px;">
          <li>🇺🇸 美股：<code>AAPL</code>, <code>TSLA</code>, <code>NVDA</code></li>
          <li>🇭🇰 港股：<code>700</code> 或 <code>700.HK</code>（騰訊）</li>
          <li>🇨🇳 滬市：<code>600519</code> 或 <code>600519.SS</code>（貴州茅台）</li>
          <li>🇨🇳 深市：<code>000333</code> 或 <code>000333.SZ</code>（美的集團）</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_ipo_planets(stock_data, stock, go):
    """渲染上市出生盤行星位置"""
    from .stock_fetcher import get_display_name

    name = get_display_name(stock)
    st.subheader(f"🌠 {name} 上市出生盤 / IPO Birth Chart")
    st.caption(
        "以股票上市日期+時間作為「出生時刻」排盤，"
        "揭示該股票的先天七政四餘靈運格局。"
        " / IPO date/time as birth moment for the Seven Governors chart."
    )

    planets = stock_data.ipo_planets
    if not planets:
        st.warning("無法計算出生盤，請確認上市日期。 / Cannot compute chart. Check the IPO date.")
        return

    # 行星位置表
    rows = []
    for p in planets:
        rows.append({
            "星曜 Planet": f"{p.name}{' ℞' if p.retrograde else ''}",
            "黃經 Lon": f"{p.longitude:.2f}°",
            "星次（中）Sign": p.sign_chinese,
            "Sign (EN)": p.sign_western,
            "宿度 Deg": f"{p.sign_degree:.1f}°",
            "五行": p.element,
        })

    import pandas as pd
    df = pd.DataFrame(rows)

    # 以 Plotly Table 渲染，帶金墨色系
    fill_colors = []
    text_colors = []
    for p in planets:
        if p.name in ("木星", "太陽", "金星", "紫氣"):
            fill_colors.append("rgba(180,120,0,0.18)")
            text_colors.append("#FFD700")
        elif p.name in ("火星", "土星", "計都", "月孛"):
            fill_colors.append("rgba(180,30,30,0.15)")
            text_colors.append("#fca5a5")
        else:
            fill_colors.append("rgba(20,10,60,0.25)")
            text_colors.append("#d4c8ff")

    fig = go.Figure(go.Table(
        header=dict(
            values=list(df.columns),
            fill_color="rgba(120,80,0,0.5)",
            font=dict(color="#FFD700", size=12),
            align="left",
            line_color="rgba(255,200,50,0.3)",
        ),
        cells=dict(
            values=[df[c].tolist() for c in df.columns],
            fill_color=[
                fill_colors,                                          # first column: planet-colored
            ] + [
                ["rgba(20,10,60,0.25)"] * len(planets)               # remaining columns: uniform
                for _ in range(len(df.columns) - 1)
            ],
            font=dict(color="#d4c8ff", size=11),
            align="left",
            line_color="rgba(255,200,50,0.15)",
        ),
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        height=min(80 + len(planets) * 28, 450),
    )
    st.plotly_chart(fig, width="stretch")

    # 七政四餘輪形分佈圖（360° 黃道圓圈散點）
    _render_zodiac_wheel(planets, go, title=f"{name} 上市盤 / IPO Chart")


def _render_zodiac_wheel(planets, go, title: str = ""):
    """渲染黃道輪形行星分佈圖"""
    # 12 星次分隔線（每 30°）
    angles_deg = [p.longitude for p in planets]
    labels = [f"{p.name}<br>{p.sign_chinese}<br>{p.longitude:.1f}°" for p in planets]
    colors = []
    for p in planets:
        if p.name in ("木星", "紫氣", "太陽"):
            colors.append("#FFD700")
        elif p.name in ("火星", "計都", "月孛"):
            colors.append("#f87171")
        elif p.name in ("土星",):
            colors.append("#94a3b8")
        elif p.name in ("羅睺",):
            colors.append("#c084fc")
        else:
            colors.append("#60a5fa")

    fig = go.Figure()

    # 黃道 12 宮分隔線
    _ZH_SIGNS = ["白羊", "金牛", "雙子", "巨蟹", "獅子", "處女",
                 "天秤", "天蠍", "射手", "摩羯", "水瓶", "雙魚"]
    for i in range(12):
        ang = i * 30
        fig.add_shape(
            type="line",
            x0=0, y0=0,
            x1=1.05 * math.cos(math.radians(90 - ang)),
            y1=1.05 * math.sin(math.radians(90 - ang)),
            line=dict(color="rgba(255,200,50,0.2)", width=1),
        )
        mid_ang = ang + 15
        mx = 0.82 * math.cos(math.radians(90 - mid_ang))
        my = 0.82 * math.sin(math.radians(90 - mid_ang))
        fig.add_annotation(
            x=mx, y=my, text=_ZH_SIGNS[i],
            showarrow=False,
            font=dict(size=8, color="rgba(255,200,50,0.5)"),
        )

    # 外圈
    theta_list = [90 - a for a in angles_deg]
    x_pts = [0.68 * math.cos(math.radians(t)) for t in theta_list]
    y_pts = [0.68 * math.sin(math.radians(t)) for t in theta_list]

    fig.add_trace(go.Scatter(
        x=x_pts, y=y_pts,
        mode="markers+text",
        marker=dict(size=14, color=colors,
                    line=dict(width=1.5, color="rgba(255,200,50,0.6)")),
        text=[p.name for p in planets],
        textposition="top center",
        hovertext=labels,
        hoverinfo="text",
        textfont=dict(size=9, color="#FFD700"),
    ))

    fig.update_layout(
        height=380,
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,10,60,0.4)",
        title=dict(text=title, font=dict(color="#FFD700", size=13)),
        xaxis=dict(showticklabels=False, showgrid=False, zeroline=False, range=[-1.15, 1.15]),
        yaxis=dict(showticklabels=False, showgrid=False, zeroline=False,
                   scaleanchor="x", range=[-1.15, 1.15]),
        shapes=[dict(
            type="circle",
            xref="x", yref="y",
            x0=-1, y0=-1, x1=1, y1=1,
            line=dict(color="rgba(255,200,50,0.25)", width=1),
        )],
    )
    st.plotly_chart(fig, width="stretch")


def _render_daily_fortune(stock_data, go, query_date: date, query_hour: int):
    """渲染流日流時吉凶分頁"""
    from .stock_calculator import DailyFortuneData

    df_data: DailyFortuneData = stock_data.daily_fortune
    if not df_data:
        st.warning("流日流時資料不可用。 / Daily fortune data unavailable.")
        return

    st.subheader(f"📅 {query_date} {query_hour:02d}:00 流日流時吉凶")

    # 總覽卡
    score = df_data.total_score
    if score >= 8:
        card_color, level_icon = "rgba(255,200,50,0.2)", "🌟"
    elif score >= 4:
        card_color, level_icon = "rgba(134,239,172,0.15)", "✅"
    elif score >= 0:
        card_color, level_icon = "rgba(96,165,250,0.12)", "🔵"
    elif score >= -4:
        card_color, level_icon = "rgba(251,146,60,0.15)", "⚠️"
    else:
        card_color, level_icon = "rgba(248,113,113,0.15)", "🔴"

    st.markdown(
        f"""
        <div style="
            background:{card_color};
            border:1px solid rgba(255,200,50,0.25);
            border-radius:12px;padding:14px 18px;margin-bottom:14px;
        ">
        {level_icon} <strong style="color:#FFD700;font-size:1.05em;">
        流時吉凶總評 / Overall Daily Fortune Score: {score:+d}</strong><br/>
        <span style="color:#d4b860;font-size:0.93em;">{df_data.overall_zh}</span><br/>
        <span style="color:#9090a8;font-size:0.84em;">{df_data.overall_en}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 星曜明細橫條圖
    names = [e.planet for e in df_data.entries]
    scores = [e.score for e in df_data.entries]
    bar_colors = [e.color for e in df_data.entries]
    hover_texts = [
        f"<b>{e.planet}</b> {e.sign_zh} {e.longitude:.1f}°"
        f"{'℞' if e.retrograde else ''}<br>{e.judgment_zh}<br>{e.judgment_en}"
        for e in df_data.entries
    ]

    fig = go.Figure(go.Bar(
        y=names[::-1],
        x=scores[::-1],
        orientation="h",
        marker_color=bar_colors[::-1],
        marker_line_color="rgba(255,200,50,0.3)",
        marker_line_width=1,
        hovertext=hover_texts[::-1],
        hoverinfo="text",
    ))
    fig.add_vline(x=0, line_color="rgba(255,200,50,0.4)", line_width=1.5)
    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,10,60,0.4)",
        title=dict(text="各星曜吉凶分數 / Per-Planet Fortune Score", font=dict(color="#FFD700", size=12)),
        xaxis=dict(title="Score", color="#9090b8", gridcolor="rgba(255,200,50,0.1)",
                   zeroline=False),
        yaxis=dict(color="#d4b860", gridcolor="rgba(255,200,50,0.05)"),
        font=dict(color="#d4c8ff"),
    )
    st.plotly_chart(fig, width="stretch")

    # 星曜斷語卡片
    st.markdown("**⭐ 各星曜流時斷語 / Per-Planet Judgment**")
    cols = st.columns(2)
    for i, entry in enumerate(df_data.entries):
        retro_sym = " ℞" if entry.retrograde else ""
        icon = "🟢" if entry.score >= 2 else ("🟡" if entry.score >= 0 else "🔴")
        with cols[i % 2]:
            st.markdown(
                f"""<div style="
                    background:rgba(20,12,5,0.5);
                    border-left:3px solid {entry.color};
                    border-radius:0 8px 8px 0;
                    padding:7px 12px;margin:4px 0;
                ">
                {icon} <strong style="color:{entry.color};">{entry.planet}{retro_sym}</strong>
                &nbsp;<span style="color:#9090a8;font-size:0.82em;">{entry.sign_zh} {entry.longitude:.1f}°</span><br/>
                <span style="color:#d4b860;font-size:0.85em;">{entry.judgment_zh}</span>
                </div>""",
                unsafe_allow_html=True,
            )

    # 24小時吉凶時間軸（掃描今日每小時）
    st.divider()
    st.markdown("**🕐 今日 24 小時吉凶走勢 / Today's Hourly Fortune Timeline**")
    _render_hourly_timeline(go, query_date, df_data.timezone)


def _render_hourly_timeline(go, query_date: date, timezone: float):
    """渲染今日 24 小時各時辰吉凶折線圖"""
    from .stock_calculator import compute_daily_fortune

    hours = list(range(24))
    scores = []
    for h in hours:
        try:
            fd = compute_daily_fortune(
                query_year=query_date.year, query_month=query_date.month,
                query_day=query_date.day, query_hour=h, timezone=timezone,
            )
            scores.append(fd.total_score)
        except Exception:
            scores.append(0)

    bar_colors = [
        "#FFD700" if s >= 8 else
        "#86efac" if s >= 4 else
        "#60a5fa" if s >= 0 else
        "#fb923c" if s >= -4 else
        "#f87171"
        for s in scores
    ]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"{h:02d}:00" for h in hours],
        y=scores,
        marker_color=bar_colors,
        marker_line_color="rgba(255,200,50,0.2)",
        marker_line_width=1,
        hovertemplate="%{x}<br>吉凶分：%{y:+d}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="rgba(255,200,50,0.3)", line_width=1.2)

    fig.update_layout(
        height=200,
        margin=dict(l=10, r=10, t=30, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,10,60,0.4)",
        title=dict(text=f"{query_date} 逐時吉凶 / Hourly Fortune", font=dict(color="#FFD700", size=11)),
        xaxis=dict(color="#9090b8", gridcolor="rgba(255,200,50,0.08)", tickfont=dict(size=9)),
        yaxis=dict(title="Score", color="#9090b8", gridcolor="rgba(255,200,50,0.08)"),
        font=dict(color="#d4c8ff"),
    )
    st.plotly_chart(fig, width="stretch")


def _render_price_strength(stock, stock_data, go):
    """渲染股價比例強弱度分頁"""
    from .stock_fetcher import get_display_name

    name = get_display_name(stock)
    ratio = stock_data.price_ratio
    label_zh = stock_data.strength_label_zh
    label_en = stock_data.strength_label_en
    color = stock_data.strength_color

    st.subheader(f"💹 {name} 股價強弱度 / Price Strength Indicator")

    if ratio is None:
        st.warning(
            "股價強弱度計算需要 52 週高低點資料，目前資料不足。"
            " / Price strength requires 52-week high/low data, which is currently unavailable."
        )
    else:
        # 進度條 / 滑動量尺
        _render_strength_gauge(ratio, label_zh, label_en, color, go)

        # 對應七政四餘解讀
        _render_strength_interpretation(ratio, label_zh, stock)

    # 股價預測視覺化
    if stock.current_price and stock.week52_high and stock.week52_low:
        _render_price_forecast(stock, stock_data, go)


def _render_strength_gauge(ratio: float, label_zh: str, label_en: str, color: str, go):
    """渲染股價強弱度儀表盤"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=ratio,
        number={"suffix": "%", "font": {"color": color, "size": 32}},
        title={"text": f"52週強弱度 / 52-Week Strength<br><span style='font-size:0.85em;color:{color};'>{label_zh} · {label_en}</span>",
               "font": {"color": "#FFD700", "size": 12}},
        gauge={
            "axis": {"range": [0, 100], "tickfont": {"color": "#9090b8"},
                     "tickvals": [0, 20, 40, 60, 80, 100]},
            "bar": {"color": color},
            "bgcolor": "rgba(20,10,5,0.4)",
            "bordercolor": "rgba(255,200,50,0.3)",
            "steps": [
                {"range": [0, 20],  "color": "rgba(248,113,113,0.18)"},
                {"range": [20, 40], "color": "rgba(251,146,60,0.15)"},
                {"range": [40, 60], "color": "rgba(96,165,250,0.12)"},
                {"range": [60, 80], "color": "rgba(134,239,172,0.15)"},
                {"range": [80, 100],"color": "rgba(255,200,50,0.18)"},
            ],
            "threshold": {
                "line": {"color": "#FFD700", "width": 2},
                "thickness": 0.75, "value": ratio,
            },
        },
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=60, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "#d4c8ff"},
    )
    st.plotly_chart(fig, width="stretch")

    # 五區間說明
    st.markdown(
        """
        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:4px;">
        <span style="background:rgba(248,113,113,0.25);border-radius:6px;padding:3px 10px;color:#f87171;font-size:0.82em;">0–20% 休囚（弱宮）</span>
        <span style="background:rgba(251,146,60,0.25);border-radius:6px;padding:3px 10px;color:#fb923c;font-size:0.82em;">20–40% 失令（偏弱）</span>
        <span style="background:rgba(96,165,250,0.20);border-radius:6px;padding:3px 10px;color:#60a5fa;font-size:0.82em;">40–60% 中和（平穩）</span>
        <span style="background:rgba(134,239,172,0.20);border-radius:6px;padding:3px 10px;color:#86efac;font-size:0.82em;">60–80% 得令（偏強）</span>
        <span style="background:rgba(255,200,50,0.20);border-radius:6px;padding:3px 10px;color:#FFD700;font-size:0.82em;">80–100% 旺相（強勢）</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_strength_interpretation(ratio: float, label_zh: str, stock):
    """根據股價強弱度給出七政四餘語調的操作建議"""
    from .stock_fetcher import get_display_name

    name = get_display_name(stock)
    st.divider()
    st.markdown("**📖 七政四餘強弱解讀 / Strength Interpretation**")

    if ratio >= 80:
        interp_zh = (
            f"《旺相格》{name} 當前價位處於 {ratio:.0f}% 強勢區。"
            "七政諸星廟旺，財氣充盈，適合持股待漲或短線追高。"
            "惟需防木星過旺轉折，宜設停利保護利潤。"
        )
        interp_en = (
            f"{name} sits at {ratio:.0f}% of its 52-week range — Wang Xiang (Full Strength). "
            "Planetary energy is at peak; hold or trail-stop for further gains. "
            "Watch for Jupiter peak reversal — protect profits with trailing stops."
        )
        short_line = "宜持股/短線追高，嚴設停利"
        medium_line = "趨勢向上，可分批持有"
        long_line = "旺相期，適合中長線持有"
        risk = "防強弩之末，注意逆轉訊號"
    elif ratio >= 60:
        interp_zh = (
            f"《得令格》{name} 處於 {ratio:.0f}% 偏強區。"
            "財星得令，動能充足，多頭趨勢未盡。"
            "適合逢回短線進場，中線持有。"
        )
        interp_en = (
            f"{name} at {ratio:.0f}% — De Ling (Above Average Strength). "
            "Wealth stars empowered, upward momentum intact. "
            "Buy dips for short-term; hold medium-term."
        )
        short_line = "逢回買進，動能仍在"
        medium_line = "中線多頭，分批建倉"
        long_line = "偏多格，適合長線配置"
        risk = "留意回測支撐，防短線震盪"
    elif ratio >= 40:
        interp_zh = (
            f"《中和格》{name} 處於 {ratio:.0f}% 中性區。"
            "七政星力平衡，多空拉鋸，宜觀望或小量布局。"
            "等待明確突破訊號再行動。"
        )
        interp_en = (
            f"{name} at {ratio:.0f}% — Zhong He (Neutral). "
            "Planetary energy balanced; bulls and bears in equilibrium. "
            "Wait for a clear breakout before acting."
        )
        short_line = "觀望為主，等待突破"
        medium_line = "中線中性，需等趨勢明確"
        long_line = "不宜重倉，小量試探"
        risk = "方向未明，防假突破"
    elif ratio >= 20:
        interp_zh = (
            f"《失令格》{name} 位於 {ratio:.0f}% 偏弱區。"
            "財星失令，下行壓力明顯。"
            "宜減持或空倉等待，不宜逆勢進場。"
        )
        interp_en = (
            f"{name} at {ratio:.0f}% — Shi Ling (Below Average). "
            "Wealth star in detriment; downward pressure dominant. "
            "Reduce exposure or stay sidelined."
        )
        short_line = "不宜進場，防止抄底失敗"
        medium_line = "中線偏空，宜等落底訊號"
        long_line = "長線需等回升確認"
        risk = "防止持續下跌，嚴設停損"
    else:
        interp_zh = (
            f"《休囚格》{name} 僅位於 {ratio:.0f}% 弱宮區。"
            "諸星皆弱，財氣散盡，宜空倉觀望。"
            "等待月孛散去、紫氣回歸後，再考慮布局。"
        )
        interp_en = (
            f"{name} at {ratio:.0f}% — Xiu Qiu (Weak Zone). "
            "Planetary energies depleted; avoid new positions. "
            "Wait for reversal confirmation before re-entering."
        )
        short_line = "嚴禁進場，空倉等待"
        medium_line = "中線看空，等底部確認"
        long_line = "長線需待市場企穩"
        risk = "大幅下跌風險高，出清保本"

    st.markdown(
        f"""
        <div style="
            background:linear-gradient(135deg,rgba(40,25,5,0.6),rgba(60,35,5,0.4));
            border:1px solid rgba(255,200,50,0.3);border-radius:12px;
            padding:16px 20px;margin-bottom:12px;
        ">
        <div style="color:#d4b860;font-size:0.94em;margin-bottom:10px;">{interp_zh}</div>
        <div style="color:#8090a8;font-size:0.84em;margin-bottom:12px;">{interp_en}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <span style="background:rgba(96,165,250,0.18);border-radius:6px;padding:4px 12px;
            color:#60a5fa;font-size:0.85em;">📊 短線：{short_line}</span>
          <span style="background:rgba(134,239,172,0.15);border-radius:6px;padding:4px 12px;
            color:#86efac;font-size:0.85em;">📈 中線：{medium_line}</span>
          <span style="background:rgba(255,200,50,0.15);border-radius:6px;padding:4px 12px;
            color:#FFD700;font-size:0.85em;">🏆 長線：{long_line}</span>
          <span style="background:rgba(248,113,113,0.15);border-radius:6px;padding:4px 12px;
            color:#f87171;font-size:0.85em;">⚠️ 風險：{risk}</span>
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_price_forecast(stock, stock_data, go):
    """渲染黃金分割 × 七政四餘股價預測視覺圖"""
    from .stock_fetcher import get_display_name

    st.divider()
    st.markdown("**🔮 股價預測 / Price Forecast**")

    low = stock.week52_low
    high = stock.week52_high
    current = stock.current_price
    display_name = get_display_name(stock)
    ratio = stock_data.price_ratio if stock_data.price_ratio is not None else 50.0
    total_score = stock_data.daily_fortune.total_score if stock_data.daily_fortune else 0
    price_range = max(high - low, max(current * _MIN_RANGE_PCT_OF_PRICE, _MIN_PRICE_FLOOR))

    score_boost = max(-_MAX_SCORE_BOOST, min(_MAX_SCORE_BOOST, total_score / _SCORE_BOOST_DIVISOR))
    ratio_bias = ((ratio - _RATIO_CENTER) / _RATIO_BIAS_DIVISOR) * _RATIO_BIAS_WEIGHT
    trend_factor = 1.0 + score_boost + ratio_bias
    trend_factor = max(_MIN_TREND_FACTOR, min(_MAX_TREND_FACTOR, trend_factor))

    golden_steps = _GOLDEN_RATIO_STEPS
    direction = 1.0
    if ratio < _BEARISH_RATIO_STRONG and total_score < 0:
        direction = -1.0
    elif ratio < _BEARISH_RATIO_MILD and total_score <= _BEARISH_SCORE_THRESHOLD:
        direction = -1.0

    targets = []
    for step, horizon in zip(golden_steps, _FORECAST_HORIZONS):
        move = price_range * step * trend_factor * direction
        target_price = max(_MIN_PRICE_FLOOR, current + move)
        targets.append({"horizon": horizon, "step": step, "price": target_price})

    st.markdown(
        f"""
        <div style="
            background: radial-gradient(circle at top right, rgba(255,215,0,0.18), rgba(40,10,75,0.35) 45%, rgba(10,20,60,0.45));
            border:1px solid rgba(255,215,0,0.35);
            border-radius:14px;
            padding:14px 16px;
            margin:6px 0 14px 0;
        ">
            <div style="font-weight:700;color:#FFD700;font-size:0.97em;">
                江恩占星學派 · 黃金分割比率 × 七政四餘
            </div>
            <div style="color:#d6c8ff;font-size:0.86em;margin-top:5px;">
                {display_name} 以現價 <span style="color:#FFD700;">{current:.2f}</span> 為基準，
                結合 52 週振幅與流時星曜分數（{total_score:+d}）推演未來目標價。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(5, gap="small")
    card_colors = [
        "rgba(96,165,250,0.18)",
        "rgba(56,189,248,0.18)",
        "rgba(134,239,172,0.18)",
        "rgba(250,204,21,0.18)",
        "rgba(255,215,0,0.24)",
    ]
    for idx, target in enumerate(targets):
        delta_pct = ((target["price"] - current) / current * 100.0) if current else 0.0
        with cols[idx]:
            st.markdown(
                f"""
                <div style="
                    background:{card_colors[idx]};
                    border:1px solid rgba(255,215,0,0.28);
                    border-radius:12px;
                    padding:10px 10px 9px 10px;
                    min-height:106px;
                ">
                    <div style="font-size:0.78em;color:#d8cff8;">{target["horizon"]} 目標價</div>
                    <div style="font-size:1.06em;font-weight:700;color:#FFD700;margin:4px 0 3px 0;">
                        {target["price"]:.2f}
                    </div>
                    <div style="font-size:0.78em;color:{'#86efac' if delta_pct >= 0 else '#f87171'};">
                        {delta_pct:+.2f}% vs 現價
                    </div>
                    <div style="font-size:0.72em;color:#a8b4d8;margin-top:4px;">
                        φ {target["step"]:.3f}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    fig = go.Figure()
    x_points = ["現價"] + list(_FORECAST_HORIZONS)
    y_points = [current] + [t["price"] for t in targets]
    line_color = "#FFD700" if direction > 0 else "#f87171"
    marker_tail = _BULLISH_FORECAST_COLORS if direction > 0 else _BEARISH_FORECAST_COLORS
    marker_color = ["#FFD700", *list(marker_tail[:len(targets)])]

    fig.add_trace(go.Scatter(
        x=x_points,
        y=y_points,
        mode="lines+markers+text",
        line=dict(color=line_color, width=3),
        marker=dict(size=8, color=marker_color, line=dict(color="rgba(255,255,255,0.4)", width=1)),
        text=[f"{p:.2f}" for p in y_points],
        textposition="top center",
        textfont=dict(color="#d4c8ff", size=10),
        hovertemplate="%{x}<br>預測價: %{y:.2f}<extra></extra>",
    ))

    fig.add_hline(
        y=current,
        line_color="rgba(255,215,0,0.5)",
        line_dash="dot",
        annotation_text=f"現價 {current:.2f}",
        annotation_font_color="#FFD700",
    )

    fig.update_layout(
        height=315,
        margin=dict(l=16, r=16, t=36, b=24),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(12,10,34,0.52)",
        xaxis=dict(color="#a8b4d8", gridcolor="rgba(255,200,50,0.08)"),
        yaxis=dict(color="#a8b4d8", gridcolor="rgba(255,200,50,0.08)", title=stock.currency or "Price"),
        title=dict(text="黃金分割時間軸目標價 / Golden Ratio Target Curve", font=dict(color="#FFD700", size=12)),
        font=dict(color="#d4c8ff"),
    )
    st.plotly_chart(fig, width="stretch")


def _render_ai_reading(stock, stock_data, input_tz: float):
    """渲染 AI 七政四餘語調解讀"""
    from .stock_fetcher import get_display_name

    name = get_display_name(stock)
    st.subheader(f"🤖 {name} AI 靈運解讀 / AI Reading")

    # 構建 AI prompt context
    df = stock_data.daily_fortune
    ratio_str = f"{stock_data.price_ratio:.0f}%" if stock_data.price_ratio is not None else "不詳"

    top_planets = sorted(df.entries if df else [], key=lambda e: e.score, reverse=True)
    top3_good = ", ".join(f"{e.planet}（{e.score:+d}）" for e in top_planets[:3] if e.score > 0)
    top3_bad  = ", ".join(f"{e.planet}（{e.score:+d}）" for e in reversed(top_planets) if e.score < 0)
    top3_bad  = top3_bad[:_MAX_BAD_PLANETS_STR_LEN]  # cap display length

    prompt_snippet = (
        f"股票：{name}（{stock.normalized_ticker}）\n"
        f"上市日期：{stock.ipo_date}\n"
        f"當前股價：{stock.current_price} {stock.currency}，"
        f"漲跌：{stock.price_change:+.2f}%\n"
        f"52週強弱度：{ratio_str}（{stock_data.strength_label_zh}）\n"
        f"今日流時吉凶總分：{df.total_score if df else 'N/A'}\n"
        f"今日主要吉星：{top3_good or '無'}\n"
        f"今日主要凶星：{top3_bad or '無'}\n"
        f"流時概覽：{stock_data.transit_summary_zh}"
    )

    st.info(
        "💡 點擊頁面底部 **AI 助理** 按鈕，取得七政四餘語調的股票靈運解讀。\n"
        "/ Click the **AI Assistant** button at the bottom for a Seven Governors–style stock fortune reading.",
        icon="🤖",
    )

    # 推送給全域 AI chat
    try:
        st.session_state["_global_chat_system"] = "tab_stock_fortune"
        st.session_state["_global_chat_chart"] = {
            "module": "stock_fortune",
            "stock_name": name,
            "ticker": stock.normalized_ticker,
            "ipo_date": str(stock.ipo_date),
            "current_price": stock.current_price,
            "price_change_pct": stock.price_change,
            "price_ratio_pct": stock_data.price_ratio,
            "strength_zh": stock_data.strength_label_zh,
            "daily_score": df.total_score if df else 0,
            "daily_overall_zh": df.overall_zh if df else "",
            "good_planets": top3_good,
            "bad_planets": top3_bad,
            "ai_role_zh": (
                "你是精通七政四餘的明清星曜大師，擅長以古語斷語解讀股票靈運，"
                "結合傳統財星理論與現代市場分析，給出短中長線建議"
            ),
            "ai_role_en": (
                "You are a master of the Seven Governors & Four Remainders (Qi Zheng Si Yu), "
                "skilled at reading stock fortune through classical Chinese astrology, "
                "blending traditional wealth-star theory with modern market insights."
            ),
        }
        st.session_state["_global_chat_page_content"] = prompt_snippet
    except Exception:
        pass

    # 顯示 prompt 預覽（供用戶參考）
    with st.expander("🔍 AI 分析上下文預覽 / AI Context Preview"):
        st.code(prompt_snippet, language="text")


# ============================================================
# 名學五行分析
# ============================================================

def _wuxing_bar(dist: dict, total: int, title: str):
    """渲染五行比重橫條圖（純 HTML/CSS，無需 plotly）"""
    import streamlit as st
    from .name_wuxing import WUXING_ELEMENTS, WUXING_COLORS

    bars_html = ""
    for el in WUXING_ELEMENTS:
        count = dist.get(el, 0)
        pct = (count / total * 100) if total > 0 else 0
        color = WUXING_COLORS[el]
        bars_html += (
            f'<div style="display:flex;align-items:center;margin:4px 0;">'
            f'<span style="width:28px;color:{color};font-weight:700;font-size:0.95em;">{el}</span>'
            f'<div style="flex:1;background:rgba(255,255,255,0.06);border-radius:6px;height:14px;margin:0 8px;">'
            f'<div style="width:{pct:.1f}%;background:{color};border-radius:6px;height:100%;'
            f'transition:width 0.4s;"></div></div>'
            f'<span style="color:{color};font-size:0.85em;min-width:60px;">'
            f'{count}次 {pct:.0f}%</span>'
            f'</div>'
        )

    st.markdown(
        f'<div style="background:rgba(20,12,40,0.5);border:1px solid rgba(255,200,50,0.2);'
        f'border-radius:10px;padding:12px 16px;margin-bottom:10px;">'
        f'<div style="color:#d4b860;font-weight:600;margin-bottom:8px;">{title}</div>'
        f'{bars_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def _render_name_wuxing(stock):
    """
    渲染「名學五行分析」分頁：
    - 公司中文名稱各字筆劃 → 五行比重
    - 股票代碼數字 → 五行比重
    - 若 session 有出生日期，計算命主八字五行並對比
    """
    from .name_wuxing import (
        analyze_name_wuxing,
        analyze_ticker_wuxing,
        get_bazi_wuxing,
        compare_wuxing,
        WUXING_COLORS,
        WUXING_ELEMENTS,
    )
    from .stock_fetcher import get_display_name

    st.subheader("🀄 名學五行分析 / Name & Ticker Wuxing Analysis")
    st.caption(
        "依「姓名學」五行理論，分析上市公司名稱漢字筆劃五行與股票代碼數字五行，"
        "並與命主八字五行對比，判斷是否相生相和或相剋。\n"
        "/ Using Chinese name numerology, analyse the Five Elements of the company name "
        "characters and stock ticker digits, then compare with your BaZi birth chart elements."
    )

    ticker = stock.normalized_ticker
    name_zh = stock.name_zh or ""

    # ── 公司中文名稱五行 ──────────────────────────────
    st.markdown("---")
    st.markdown("**📝 公司名稱五行 / Company Name Wuxing**")

    if name_zh:
        name_result = analyze_name_wuxing(name_zh)
        total_name = name_result["total"] or 1

        # 字符明細卡片
        chars_html = ""
        for cd in name_result["chars"]:
            color = WUXING_COLORS[cd["wuxing"]]
            stroke_label = str(cd["strokes"]) if cd["strokes"] is not None else "?"
            chars_html += (
                f'<span style="display:inline-block;text-align:center;'
                f'background:rgba(0,0,0,0.3);border:1px solid {color}33;'
                f'border-radius:8px;padding:6px 12px;margin:4px;">'
                f'<span style="font-size:1.5em;color:{color};">{cd["char"]}</span><br/>'
                f'<span style="font-size:0.72em;color:{color};">{stroke_label}劃·{cd["wuxing"]}</span>'
                f'</span>'
            )

        st.markdown(
            f'<div style="background:rgba(20,12,40,0.5);border:1px solid rgba(255,200,50,0.2);'
            f'border-radius:10px;padding:12px 16px;margin-bottom:10px;">'
            f'<div style="color:#FFD700;font-weight:600;margin-bottom:8px;">{name_zh}</div>'
            f'{chars_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

        if name_result["unknown_chars"]:
            st.caption(f"⚠️ 以下字符無筆劃資料，預設為「土」: {'、'.join(name_result['unknown_chars'])}")

        _wuxing_bar(name_result["distribution"], total_name,
                    f"{name_zh} 名稱五行比重")
    else:
        st.info(
            "此股票暫無中文公司名稱資料（yfinance 未返回中文名）。\n"
            "/ No Chinese company name available from yfinance for this ticker."
        )

    # ── 股票代碼數字五行 ──────────────────────────────
    st.markdown("---")
    st.markdown("**🔢 股票代碼數字五行 / Ticker Digit Wuxing**")

    ticker_result = analyze_ticker_wuxing(ticker)
    total_ticker = ticker_result["total"] or 1

    if ticker_result["digits"]:
        digits_html = ""
        for dd in ticker_result["digits"]:
            color = WUXING_COLORS[dd["wuxing"]]
            digits_html += (
                f'<span style="display:inline-block;text-align:center;'
                f'background:rgba(0,0,0,0.3);border:1px solid {color}33;'
                f'border-radius:8px;padding:6px 14px;margin:4px;">'
                f'<span style="font-size:1.5em;color:{color};">{dd["digit"]}</span><br/>'
                f'<span style="font-size:0.72em;color:{color};">{dd["wuxing"]}</span>'
                f'</span>'
            )

        st.markdown(
            f'<div style="background:rgba(20,12,40,0.5);border:1px solid rgba(255,200,50,0.2);'
            f'border-radius:10px;padding:12px 16px;margin-bottom:10px;">'
            f'<div style="color:#FFD700;font-weight:600;margin-bottom:8px;">{ticker}</div>'
            f'{digits_html}'
            f'</div>',
            unsafe_allow_html=True,
        )

        _wuxing_bar(ticker_result["distribution"], total_ticker,
                    f"{ticker} 代碼數字五行比重")
    else:
        st.info("股票代碼中無數字，無法分析五行。/ No digits found in ticker.")

    # ── 命主八字五行（若有出生日期）────────────────────
    st.markdown("---")
    st.markdown("**🎂 命主八字五行 / Your BaZi Wuxing (from Sidebar Birth Date)**")

    birth_date = st.session_state.get("birth_date_input")
    confirmed_params = st.session_state.get("_confirmed_params")

    bazi_year, bazi_month, bazi_day = None, None, None
    if confirmed_params and confirmed_params.get("year"):
        bazi_year = confirmed_params["year"]
        bazi_month = confirmed_params["month"]
        bazi_day = confirmed_params["day"]
    elif birth_date is not None:
        try:
            bazi_year = birth_date.year
            bazi_month = birth_date.month
            bazi_day = birth_date.day
        except AttributeError:
            pass

    if bazi_year is None:
        st.info(
            "請在左側邊欄輸入您的出生日期，即可比較命主八字五行與股票五行的相生相剋。\n"
            "/ Enter your birth date in the sidebar to compare your BaZi elements "
            "with the stock's Five Elements."
        )
        return

    bazi_result = get_bazi_wuxing(bazi_year, bazi_month, bazi_day)

    if not bazi_result["available"]:
        st.warning(
            f"無法計算八字五行（{bazi_result['error']}）。\n"
            "/ Cannot compute BaZi elements."
        )
        return

    # 八字四柱展示
    from datetime import date as date_cls
    birth_str = f"{bazi_year}-{bazi_month:02d}-{bazi_day:02d}"
    pillars_html = ""
    for p in bazi_result["pillars"]:
        ws_color = WUXING_COLORS[p["wuxing_stem"]]
        wb_color = WUXING_COLORS[p["wuxing_branch"]]
        pillars_html += (
            f'<span style="display:inline-block;text-align:center;'
            f'background:rgba(0,0,0,0.3);border:1px solid rgba(255,200,50,0.2);'
            f'border-radius:8px;padding:8px 14px;margin:4px;">'
            f'<span style="font-size:0.72em;color:#9090b8;">{p["label"]}</span><br/>'
            f'<span style="font-size:1.4em;color:{ws_color};">{p["stem"]}</span>'
            f'<span style="font-size:1.4em;color:{wb_color};">{p["branch"]}</span><br/>'
            f'<span style="font-size:0.72em;color:{ws_color};">{p["wuxing_stem"]}</span>'
            f'<span style="font-size:0.72em;color:#9090b8;">·</span>'
            f'<span style="font-size:0.72em;color:{wb_color};">{p["wuxing_branch"]}</span>'
            f'</span>'
        )

    st.markdown(
        f'<div style="background:rgba(20,12,40,0.5);border:1px solid rgba(255,200,50,0.2);'
        f'border-radius:10px;padding:12px 16px;margin-bottom:10px;">'
        f'<div style="color:#FFD700;font-weight:600;margin-bottom:8px;">'
        f'命主出生日期 {birth_str} 三柱八字</div>'
        f'{pillars_html}'
        f'</div>',
        unsafe_allow_html=True,
    )

    _wuxing_bar(bazi_result["distribution"], sum(bazi_result["distribution"].values()) or 1,
                "命主三柱六字五行比重（年月日）")

    # ── 對比分析 ──────────────────────────────────────
    st.markdown("---")
    st.markdown("**⚖️ 命主 × 股票 五行對比 / BaZi vs. Stock Wuxing Compatibility**")

    comparisons = []
    if name_zh and name_result["total"] > 0:
        comparisons.append(
            (name_result["distribution"], f"公司名稱「{name_zh}」")
        )
    if ticker_result["total"] > 0:
        comparisons.append(
            (ticker_result["distribution"], f"股票代碼「{ticker}」數字")
        )

    for dist_b, label_b in comparisons:
        cmp = compare_wuxing(
            bazi_result["distribution"], "命主",
            dist_b, label_b,
        )

        score_icon = {2: "🌟", 1: "✅", 0: "🔵", -1: "⚠️", -2: "🔴"}.get(cmp["score"], "🔵")
        st.markdown(
            f"""
            <div style="
                background:rgba(20,12,40,0.55);
                border-left:4px solid {cmp['color']};
                border-radius:0 10px 10px 0;
                padding:12px 16px;
                margin-bottom:10px;
            ">
            <div style="font-weight:700;color:{cmp['color']};font-size:1.0em;">
                {score_icon} {cmp['relationship']} &nbsp;
                <span style="font-size:0.85em;color:#9090b8;">({cmp['relationship_en']})</span>
            </div>
            <div style="font-size:0.78em;color:#9090b8;margin:2px 0 8px 0;">
                命主主元素：<span style="color:{cmp['color']};">{cmp['dominant_a']}</span>
                &nbsp;⟷&nbsp;
                {label_b}主元素：<span style="color:{cmp['color']};">{cmp['dominant_b']}</span>
            </div>
            <div style="color:#d4b860;font-size:0.91em;margin-bottom:6px;">{cmp['summary_zh']}</div>
            <div style="color:#8090a8;font-size:0.82em;">{cmp['summary_en']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "⚠️ 名學五行分析僅供參考，不構成投資建議。"
        " / Name Wuxing analysis is for reference only and does not constitute investment advice."
    )
