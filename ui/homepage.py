"""Homepage landing page for KinAstro.

Provides the ``render_homepage()`` function that displays the aesthetic
landing page when no astrology system has been selected yet.
"""

from __future__ import annotations

import textwrap

import streamlit as st

from astro.i18n import auto_cn


def render_homepage() -> None:
    """Render the aesthetic homepage landing page."""
    _lang = st.session_state.get("lang", "zh")

    _categories = [
        ("☯️", "三式神機", "San Shi Divination",
         ["大六壬", "太乙神數", "奇門祿命"],
         "#C9A84C", "rgba(201,168,76,0.12)", "rgba(201,168,76,0.28)"),
        ("🏮", "中式占星", "Chinese Systems",
         ["紫微斗數", "七政四餘", "萬化仙禽", "十二星次", "策天飛星", "達摩一掌經", "鐵板神數", "邵子神數", "皇極經世",
          "鬼谷分定經", "滌器遺訣", "太玄數占星", "開元占經", "五運六氣", "六爻終身卦", "北極神數", "南極神數", "子平八字", "蠢子數"],
         "#C9A84C", "rgba(201,168,76,0.10)", "rgba(201,168,76,0.22)"),
        ("🏛️", "西洋占星", "Western Astrology",
         ["西洋占星", "薩比安符號", "希臘化占星", "星移地圖", "天王星漢堡", "宇宙生物學", "和諧占星",
          "古典主限推運", "凱爾特樹", "出生時間校正", "赫密士前世盤", "靈性占星", "拜占庭占星", "人間圖", "世俗占星", "弗拉德命運輪盤", "煉金占星"],
         "#7B9ED9", "rgba(123,158,217,0.1)", "rgba(123,158,217,0.22)"),
        ("🪷", "印度占星", "Vedic Jyotish",
         ["Jyotish", "紅皮書 Lal Kitab", "納迪占星", "Jaimini", "KP 占星", "吠陀風水"],
         "#FF9933", "rgba(255,153,51,0.1)", "rgba(255,153,51,0.22)"),
        ("🌏", "亞洲體系", "Asian Systems",
         ["土亭數", "宿曜道", "泰國占星", "老撾占星", "緬甸 Mahabote", "峇里 Wariga", "爪哇 Weton", "馬來伊斯蘭占星（十二星）", "馬來七星五刻占卜", "祖爾海", "藏傳時輪金剛",
             "九星氣學", "高棉占星", "波利尼西亞"],
            "#E0A526", "rgba(224,165,38,0.1)", "rgba(224,165,38,0.22)"),
        ("🕌", "中東體系", "Middle East Systems",
         ["卡巴拉", "猶太占星", "薩珊波斯", "薩珊波斯進階版", "阿拉伯占星", "也門占星", "Picatrix 占星魔法", "柏柏爾占星", "地占占星"],
           "#3AB09E", "rgba(58,176,158,0.1)", "rgba(58,176,158,0.22)"),
        ("🌍", "非洲體系", "African Systems",
         ["衣索比亞 Bahre Hasab", "多貢天狼星宇宙學"],
         "#B07D42", "rgba(176,125,66,0.1)", "rgba(176,125,66,0.22)"),
        ("🜁", "隱祕與原民傳統", "Obscure & Indigenous",
         ["亞美尼亞占星"],
         "#A06C3B", "rgba(160,108,59,0.1)", "rgba(160,108,59,0.22)"),
        ("🏺", "古代文明", "Ancient Civilizations",
         ["瑪雅占星", "印加／安地斯占星", "阿茲特克", "古埃及十度", "巴比倫占星", "蘇美/美索不達米亞", "伊特魯里亞占星"],
         "#D4A04A", "rgba(212,160,74,0.1)", "rgba(212,160,74,0.22)"),
        ("⚕️", "醫占", "Medical Astrology",
         ["醫學占星", "傷寒鈐法"],
         "#2ECC71", "rgba(46,204,113,0.1)", "rgba(46,204,113,0.22)"),
        ("📜", "傳統卜卦占星", "Traditional Horary",
         ["傳統卜卦占星", "運動占星", "擇日占星", "歐洲地占"],
           "#7B4EBE", "rgba(123,78,190,0.1)", "rgba(123,78,190,0.25)"),
    ]
    _total_systems = sum(len(systems) for _, _, _, systems, *_ in _categories)

    _hp_subtitle = auto_cn(
        f"{_total_systems} 體系占星排盤平台",
        f"{_total_systems}-System Astrology Platform",
    )
    _hp_badge = auto_cn(
        "線上免費使用 · Open Source · MIT License",
        "Free Online · Open Source · MIT License",
    )
    _hp_desc = auto_cn(
        f'從七政四餘到西洋占星、從紫微斗數到印度 Jyotish、<br/>'
        f'從三式（六壬、太乙、奇門）到 Astrocartography、凱爾特樹木曆、太玄數占星、<br/>'
        f'紅皮書 Lal Kitab、薩珊波斯占星、<strong style="color:#A78BFA;">皇極經世（Huangji Jingshi）</strong>、<strong style="color:#A78BFA;">馬來伊斯蘭占星（Bintang Duabelas）</strong>、<strong style="color:#A78BFA;">馬來七星五刻占卜（Kinketika）</strong>、<strong style="color:#A78BFA;">柏柏爾占星</strong>、<strong style="color:#A78BFA;">衣索比亞 Bahre Hasab</strong>、瑪雅曆法到巴比倫星表、<strong style="color:#A78BFA;">世俗占星</strong>、<strong style="color:#A78BFA;">拜占庭占星</strong>、醫學占星、傷寒鈐法、<br/>'
        f'傳統卜卦占星、<strong style="color:#A78BFA;">運動占星（Sports Astrology）</strong>、擇日占星、蠢子數、<strong style="color:#A78BFA;">亞美尼亞占星</strong>、<strong style="color:#A78BFA;">地占占星</strong>、<strong style="color:#A78BFA;">伊特魯里亞占星</strong>、<strong style="color:#A78BFA;">煉金占星</strong>——堅占星將<strong style="color:#EAB308;font-weight:600;">全球 {_total_systems} 種占星體系</strong>融合為一，讓千年星學智慧觸手可及。',
        f'From Seven Luminaries to Western Astrology, from Zi Wei Dou Shu to Indian Jyotish,<br/>'
        f'from San Shi (Liu Ren, Tai Yi, Qi Men) to Astrocartography, Celtic Tree Calendar, Tai Xuan Shu,<br/>'
        f'Lal Kitab, Sassanid Persian Astrology, <strong style="color:#A78BFA;">Huangji Jingshi</strong>, <strong style="color:#A78BFA;">Malay Islamic Astrology (Bintang Duabelas)</strong>, <strong style="color:#A78BFA;">Malay Time Divination (Kinketika)</strong>, <strong style="color:#A78BFA;">Berber Astrology</strong>, <strong style="color:#A78BFA;">Ethiopian Bahre Hasab</strong>, Mayan Calendar to Babylonian Star Catalogue, <strong style="color:#A78BFA;">Mundane Astrology</strong>, <strong style="color:#A78BFA;">Byzantine Astrology</strong>, Medical Astrology, Shang Han Method,<br/>'
        f'Traditional Horary, <strong style="color:#A78BFA;">Sports Astrology (Frawley)</strong>, Electional Astrology, Chun Zi Shu, <strong style="color:#A78BFA;">Armenian Astrology</strong>, <strong style="color:#A78BFA;">Geomantic Astrology</strong>, <strong style="color:#A78BFA;">Etruscan Astrology</strong>, <strong style="color:#A78BFA;">Alchemical Astrology</strong> — KinAstro unifies <strong style="color:#EAB308;font-weight:600;">{_total_systems} astrology systems</strong> worldwide, bringing millennia of stellar wisdom to your fingertips.',
    )
    _hp_stat_systems = auto_cn("占星體系 Systems", "Astrology Systems")
    _hp_stat_subtabs = auto_cn("子功能分頁 Sub-tabs", "Sub-tabs")
    _hp_stat_free = auto_cn("免費開源 Free &amp; Open", "Free &amp; Open Source")
    _hp_cta_hint = auto_cn(
        "← 請從左側側邊欄選擇占星體系開始排盤",
        "← Select a system from the left sidebar to begin",
    )
    _hp_sec_systems = auto_cn("占星體系總覽", "System Overview")
    _hp_sec_features = auto_cn("核心特色", "Key Features")
    _hp_cta_title = auto_cn("開始您的星象之旅", "Begin Your Stellar Journey")
    _hp_cta_body = auto_cn(
        "在左側側邊欄輸入出生日期、時間與地點，<br/>"
        "然後選擇您想探索的占星體系，即可立即排盤。",
        "Enter your birth date, time and location in the left sidebar,<br/>"
        "then select the astrology system you'd like to explore — your chart will be generated instantly.",
    )
    _hp_cta_tip = auto_cn(
        "💡 初學者推薦從「西洋占星」或「紫微斗數」開始",
        "💡 Beginners are recommended to start with 'Western Astrology' or 'Zi Wei Dou Shu'",
    )

    st.markdown(textwrap.dedent(f"""
    <div class="hp-hero">
      <div class="hp-constellation">
        <svg width="100%" height="100%" viewBox="0 0 900 420"
             preserveAspectRatio="xMidYMid slice" aria-hidden="true"
             style="position:absolute;inset:0;width:100%;height:100%;">
          <circle cx="80"  cy="60"  r="1.8" fill="#EAB308" opacity="0.75"/>
          <circle cx="140" cy="110" r="1.2" fill="#A78BFA" opacity="0.6"/>
          <circle cx="210" cy="45"  r="2.2" fill="#EAB308" opacity="0.8"/>
          <circle cx="270" cy="140" r="1.0" fill="#E0E0FF" opacity="0.5"/>
          <circle cx="340" cy="80"  r="1.8" fill="#A78BFA" opacity="0.7"/>
          <circle cx="400" cy="165" r="1.4" fill="#EAB308" opacity="0.65"/>
          <circle cx="460" cy="55"  r="2.6" fill="#EAB308" opacity="0.85"/>
          <circle cx="530" cy="130" r="1.0" fill="#E0E0FF" opacity="0.5"/>
          <circle cx="590" cy="85"  r="1.8" fill="#A78BFA" opacity="0.7"/>
          <circle cx="660" cy="40"  r="1.4" fill="#EAB308" opacity="0.6"/>
          <circle cx="720" cy="150" r="2.2" fill="#A78BFA" opacity="0.75"/>
          <circle cx="790" cy="70"  r="1.2" fill="#E0E0FF" opacity="0.55"/>
          <circle cx="840" cy="120" r="1.8" fill="#EAB308" opacity="0.7"/>
          <circle cx="50"  cy="200" r="1.0" fill="#A78BFA" opacity="0.4"/>
          <circle cx="180" cy="280" r="1.4" fill="#EAB308" opacity="0.5"/>
          <circle cx="320" cy="310" r="1.0" fill="#E0E0FF" opacity="0.35"/>
          <circle cx="500" cy="290" r="1.6" fill="#A78BFA" opacity="0.5"/>
          <circle cx="700" cy="270" r="1.2" fill="#EAB308" opacity="0.45"/>
          <circle cx="860" cy="250" r="1.0" fill="#E0E0FF" opacity="0.4"/>
          <line x1="80"  y1="60"  x2="140" y2="110" stroke="#A78BFA" stroke-width="0.5" opacity="0.35"/>
          <line x1="140" y1="110" x2="210" y2="45"  stroke="#A78BFA" stroke-width="0.5" opacity="0.35"/>
          <line x1="340" y1="80"  x2="400" y2="165" stroke="#EAB308" stroke-width="0.5" opacity="0.3"/>
          <line x1="460" y1="55"  x2="530" y2="130" stroke="#A78BFA" stroke-width="0.5" opacity="0.35"/>
          <line x1="590" y1="85"  x2="660" y2="40"  stroke="#EAB308" stroke-width="0.5" opacity="0.3"/>
          <line x1="720" y1="150" x2="790" y2="70"  stroke="#A78BFA" stroke-width="0.5" opacity="0.35"/>
          <line x1="790" y1="70"  x2="840" y2="120" stroke="#A78BFA" stroke-width="0.5" opacity="0.3"/>
          <circle cx="450" cy="210" r="130" fill="none" stroke="rgba(167,139,250,0.08)" stroke-width="1"/>
          <circle cx="450" cy="210" r="105" fill="none" stroke="rgba(234,179,8,0.06)"   stroke-width="1" stroke-dasharray="5,8"/>
          <circle cx="450" cy="210" r="78"  fill="none" stroke="rgba(167,139,250,0.05)" stroke-width="1"/>
          <line x1="450" y1="80"  x2="450" y2="340" stroke="rgba(167,139,250,0.06)" stroke-width="0.6"/>
          <line x1="320" y1="210" x2="580" y2="210" stroke="rgba(167,139,250,0.06)" stroke-width="0.6"/>
          <line x1="337" y1="127" x2="563" y2="293" stroke="rgba(167,139,250,0.05)" stroke-width="0.5"/>
          <line x1="563" y1="127" x2="337" y2="293" stroke="rgba(167,139,250,0.05)" stroke-width="0.5"/>
          <line x1="370" y1="98"  x2="530" y2="322" stroke="rgba(167,139,250,0.04)" stroke-width="0.5"/>
          <line x1="530" y1="98"  x2="370" y2="322" stroke="rgba(167,139,250,0.04)" stroke-width="0.5"/>
          <text x="450" y="218" text-anchor="middle" font-size="22"
                fill="rgba(234,179,8,0.2)" font-family="serif">&#9789;</text>
        </svg>
      </div>
      <div class="hp-hero-content">
        <div class="hp-badge">
          <span class="hp-badge-dot"></span>
          <span>{_hp_badge}</span>
        </div>
        <h1 class="hp-title">
          <span class="hp-title-line1">堅占星</span>
          <span class="hp-title-line2">KinAstro</span>
          <span class="hp-title-sub">{_hp_subtitle}</span>
        </h1>
         <p class="hp-desc">
           {_hp_desc}
         </p>
        <div class="hp-stats">
          <div class="hp-stat">
            <div class="hp-stat-num">{_total_systems}</div>
            <div class="hp-stat-label">{_hp_stat_systems}</div>
          </div>
          <div class="hp-stat-sep">✦</div>
          <div class="hp-stat">
            <div class="hp-stat-num">95<span style="font-size:1.1rem">+</span></div>
            <div class="hp-stat-label">{_hp_stat_subtabs}</div>
          </div>
          <div class="hp-stat-sep">✦</div>
          <div class="hp-stat">
            <div class="hp-stat-num">100<span style="font-size:1.1rem">%</span></div>
            <div class="hp-stat-label">{_hp_stat_free}</div>
          </div>
        </div>
        <div class="hp-cta-hint">{_hp_cta_hint}</div>
      </div>
    </div>
    """), unsafe_allow_html=True)

    st.markdown(f'<div class="hp-section-title">{_hp_sec_systems}</div>', unsafe_allow_html=True)

    _cat_html = '<div class="hp-cat-grid">'
    for icon, title_zh, title_en, systems, accent, bg, border_col in _categories:
        _pills = "".join(f'<span class="hp-sys-pill">{s}</span>' for s in systems[:4])
        if len(systems) > 4:
            _pills += f'<span class="hp-sys-pill hp-sys-pill-more">+{len(systems) - 4}</span>'
        _cat_main = title_en if _lang == "en" else auto_cn(title_zh)
        _cat_sub = title_zh if _lang == "en" else title_en
        _cat_html += (
            f'<div class="hp-cat-card" style="'
            f'--cat-accent:{accent};--cat-bg:{bg};--cat-border:{border_col};">'
            f'<div class="hp-cat-icon">{icon}</div>'
            f'<div class="hp-cat-title">{_cat_main}</div>'
            f'<div class="hp-cat-en">{_cat_sub}</div>'
            f'<div class="hp-cat-pills">{_pills}</div>'
            f'</div>'
        )
    _cat_html += '</div>'
    st.markdown(_cat_html, unsafe_allow_html=True)

    st.markdown(f'<div class="hp-section-title">{_hp_sec_features}</div>', unsafe_allow_html=True)

    _features = [
        ("🔮",
         auto_cn(f"{_total_systems} 體系合一", f"{_total_systems} Systems in One"),
         auto_cn(f"在同一介面中切換中國、西洋、印度、阿拉伯、瑪雅等全球 {_total_systems} 種占星體系",
                 f"Switch between {_total_systems} global astrology traditions — Chinese, Western, Indian, Arabic, Mayan and more — all in a single interface")),
        ("🪐",
         auto_cn("精密天文計算", "Precision Astronomy"),
         auto_cn("使用瑞士星曆表 (Swiss Ephemeris) pyswisseph 進行高精度天文運算",
                 "High-precision astronomical calculations powered by Swiss Ephemeris (pyswisseph)")),
        ("🤖",
         auto_cn("AI 智慧分析", "AI-Powered Analysis"),
         auto_cn("整合 Cerebras / OpenAI，提供專業命理解讀，支援中英雙語互動問答",
                 "Integrated with Cerebras / OpenAI for professional chart readings with bilingual Q&A")),
        ("📊",
         auto_cn("精美 SVG 圖表", "Beautiful SVG Charts"),
         auto_cn("純 SVG 渲染，清晰美觀，支援響應式設計，手機平板完美顯示",
                 "Pure SVG rendering — crisp, responsive, and perfect on mobile and tablet")),
        ("🌍",
         auto_cn("三語介面", "Trilingual Interface"),
         auto_cn("繁體中文、簡體中文、English 即時切換，無需重新載入",
                 "Switch instantly between Traditional Chinese, Simplified Chinese, and English — no reload required")),
        ("🆓",
         auto_cn("完全免費開源", "Free & Open Source"),
         auto_cn("MIT License，永久免費，無任何隱藏費用，歡迎 Fork 與貢獻",
                 "MIT License — free forever, no hidden fees. Fork and contribute welcome")),
    ]

    _feat_html = '<div class="hp-feat-grid">'
    for icon, title, desc in _features:
        _feat_html += (
            f'<div class="hp-feat-card glass-card">'
            f'<div class="hp-feat-icon">{icon}</div>'
            f'<div class="hp-feat-title">{title}</div>'
            f'<div class="hp-feat-desc">{desc}</div>'
            f'</div>'
        )
    _feat_html += '</div>'
    st.markdown(_feat_html, unsafe_allow_html=True)

    st.markdown(textwrap.dedent(f"""
    <div class="hp-cta-box">
      <div class="hp-cta-stars">✦ ✧ ✦ ✧ ✦</div>
      <h3 class="hp-cta-title">{_hp_cta_title}</h3>
      <p class="hp-cta-body">
        {_hp_cta_body}
      </p>
      <div class="hp-cta-tips">
        <span class="hp-tip">{_hp_cta_tip}</span>
      </div>
    </div>
    """), unsafe_allow_html=True)
