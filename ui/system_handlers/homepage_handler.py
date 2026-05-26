"""Homepage and static-content handlers extracted from app.py."""

from __future__ import annotations

import json
import random
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

_CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
_TEMPLATES_DIR = _CONTENT_DIR / "templates"
_STAR_PARTICLE_COUNT = 60


@lru_cache(maxsize=1)
def _load_homepage_content() -> dict[str, Any]:
    return json.loads((_CONTENT_DIR / "homepage_content.json").read_text(encoding="utf-8"))


@lru_cache(maxsize=8)
def _load_template(name: str) -> str:
    return (_TEMPLATES_DIR / name).read_text(encoding="utf-8")


def build_star_particles_html() -> str:
    """Build CSS-based star particle background HTML."""
    parts: list[str] = []
    for _ in range(_STAR_PARTICLE_COUNT):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        dur = random.uniform(2.5, 6.0)
        delay = random.uniform(0, 5.0)
        opacity = random.uniform(0.3, 0.8)
        size = random.choices([1, 2, 3], weights=[1, 2, 1], k=1)[0]
        color = random.choices(["#EAB308", "#A78BFA", "#E0E0FF"], weights=[3, 1, 1], k=1)[0]
        parts.append(
            f'<div class="particle" style="'
            f"left:{x:.1f}%;top:{y:.1f}%;"
            f"width:{size}px;height:{size}px;"
            f"background:{color};"
            f"--duration:{dur:.1f}s;--delay:{delay:.1f}s;"
            f'--max-opacity:{opacity:.2f};"></div>'
        )
    wrapper = _load_template("star_particles.html")
    return wrapper.format(particles="".join(parts))


def inject_star_particles(st_module) -> None:
    """Inject CSS-based star particle background (cached per session)."""
    if "_star_particles_html" not in st_module.session_state:
        st_module.session_state["_star_particles_html"] = build_star_particles_html()
    st_module.markdown(st_module.session_state["_star_particles_html"], unsafe_allow_html=True)


def render_reference_library(st_module, *, base_dir: Path | None = None) -> None:
    """Render the Arabic astrology reference library sub-tab content."""
    if base_dir is None:
        base_dir = Path(__file__).resolve().parents[2]
    ref_dir = base_dir / "astro" / "reference"
    ref_files = [
        ("astrology_fortune.md", "占星與財富 / Astrology & Fortune"),
        ("astrology_magic.md", "占星魔法 / Astrological Magic"),
        ("astrology_military.md", "軍事占星 / Military Astrology"),
    ]
    for fname, title in ref_files:
        fpath = ref_dir / fname
        if fpath.exists():
            with fpath.open("r", encoding="utf-8") as f:
                content = f.read()
            with st_module.expander(title, expanded=False):
                st_module.markdown(content)


def render_welcome(st_module, *, t_fn: Callable[[str], str]) -> None:
    """Render a welcoming onboarding section for new users."""
    st_module.markdown(
        f'<div class="welcome-hero">'
        f'<h2>{t_fn("welcome_hero_title")}</h2>'
        f'<p>{t_fn("welcome_hero_body")}</p>'
        f"</div>",
        unsafe_allow_html=True,
    )

    steps = [
        ("1️⃣", t_fn("welcome_step1_title"), t_fn("welcome_step1_body")),
        ("2️⃣", t_fn("welcome_step2_title"), t_fn("welcome_step2_body")),
        ("3️⃣", t_fn("welcome_step3_title"), t_fn("welcome_step3_body")),
    ]
    cards_html = '<div class="step-row">'
    for i, (icon, title, body) in enumerate(steps):
        cards_html += (
            f'<div class="step-card">'
            f'<div class="step-num">{i + 1}</div>'
            f"<h4>{icon} {title}</h4>"
            f"<p>{body}</p>"
            f"</div>"
        )
    cards_html += "</div>"
    st_module.markdown(cards_html, unsafe_allow_html=True)
    st_module.info(t_fn("welcome_quick_start"))


def render_homepage(
    st_module,
    *,
    auto_cn_fn: Callable[..., str],
    lang: str,
) -> None:
    """Render the aesthetic homepage landing page."""
    payload = _load_homepage_content()
    categories: list[dict[str, Any]] = payload["categories"]
    total_systems = sum(len(item["systems"]) for item in categories)

    hero = payload["hero"]
    hp_subtitle = auto_cn_fn(
        f"{total_systems} 體系占星排盤平台",
        f"{total_systems}-System Astrology Platform",
    )
    hp_badge = auto_cn_fn(hero["badge_zh"], hero["badge_en"])
    hp_desc = auto_cn_fn(
        hero["desc_zh"].format(total_systems=total_systems),
        hero["desc_en"].format(total_systems=total_systems),
    )
    hp_stat_systems = auto_cn_fn("占星體系 Systems", "Astrology Systems")
    hp_stat_subtabs = auto_cn_fn("子功能分頁 Sub-tabs", "Sub-tabs")
    hp_stat_free = auto_cn_fn("免費開源 Free &amp; Open", "Free &amp; Open Source")
    hp_cta_hint = auto_cn_fn(
        "← 請從左側側邊欄選擇占星體系開始排盤",
        "← Select a system from the left sidebar to begin",
    )
    hp_sec_systems = auto_cn_fn("占星體系總覽", "System Overview")
    hp_sec_features = auto_cn_fn("核心特色", "Key Features")
    hp_cta_title = auto_cn_fn("開始您的星象之旅", "Begin Your Stellar Journey")
    hp_cta_body = auto_cn_fn(
        "在左側側邊欄輸入出生日期、時間與地點，<br/>然後選擇您想探索的占星體系，即可立即排盤。",
        "Enter your birth date, time and location in the left sidebar,<br/>then select the astrology system you'd like to explore — your chart will be generated instantly.",
    )
    hp_cta_tip = auto_cn_fn(
        "💡 初學者推薦從「西洋占星」或「紫微斗數」開始",
        "💡 Beginners are recommended to start with 'Western Astrology' or 'Zi Wei Dou Shu'",
    )

    st_module.markdown(
        _load_template("homepage_hero.html").format(
            badge=hp_badge,
            subtitle=hp_subtitle,
            description=hp_desc,
            total_systems=total_systems,
            stat_systems=hp_stat_systems,
            stat_subtabs=hp_stat_subtabs,
            stat_free=hp_stat_free,
            cta_hint=hp_cta_hint,
        ),
        unsafe_allow_html=True,
    )

    st_module.markdown(f'<div class="hp-section-title">{hp_sec_systems}</div>', unsafe_allow_html=True)
    cat_html = '<div class="hp-cat-grid">'
    for item in categories:
        systems = item["systems"]
        pills = "".join(f'<span class="hp-sys-pill">{s}</span>' for s in systems[:4])
        if len(systems) > 4:
            pills += f'<span class="hp-sys-pill hp-sys-pill-more">+{len(systems) - 4}</span>'
        cat_main = item["title_en"] if lang == "en" else auto_cn_fn(item["title_zh"])
        cat_sub = item["title_zh"] if lang == "en" else item["title_en"]
        cat_html += (
            f'<div class="hp-cat-card" style="--cat-accent:{item["accent"]};--cat-bg:{item["bg"]};--cat-border:{item["border"]};">'
            f'<div class="hp-cat-icon">{item["icon"]}</div>'
            f'<div class="hp-cat-title">{cat_main}</div>'
            f'<div class="hp-cat-en">{cat_sub}</div>'
            f'<div class="hp-cat-pills">{pills}</div>'
            f"</div>"
        )
    cat_html += "</div>"
    st_module.markdown(cat_html, unsafe_allow_html=True)

    st_module.markdown(f'<div class="hp-section-title">{hp_sec_features}</div>', unsafe_allow_html=True)
    feat_html = '<div class="hp-feat-grid">'
    for feature in payload["features"]:
        title = auto_cn_fn(
            feature["title_zh"].format(total_systems=total_systems),
            feature["title_en"].format(total_systems=total_systems),
        )
        desc = auto_cn_fn(
            feature["desc_zh"].format(total_systems=total_systems),
            feature["desc_en"].format(total_systems=total_systems),
        )
        feat_html += (
            f'<div class="hp-feat-card glass-card">'
            f'<div class="hp-feat-icon">{feature["icon"]}</div>'
            f'<div class="hp-feat-title">{title}</div>'
            f'<div class="hp-feat-desc">{desc}</div>'
            f"</div>"
        )
    feat_html += "</div>"
    st_module.markdown(feat_html, unsafe_allow_html=True)

    st_module.markdown(
        _load_template("homepage_cta.html").format(
            cta_title=hp_cta_title,
            cta_body=hp_cta_body,
            cta_tip=hp_cta_tip,
        ),
        unsafe_allow_html=True,
    )
