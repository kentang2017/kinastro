"""
股票資料擷取模組 (Stock Data Fetcher)

使用 yfinance 擷取股票資訊：
- 中英文名稱
- 當前股價、漲跌幅
- 上市日期（IPO date）
- 52 週高低、近期均線
- 支援 .HK / .SS / .SZ / US stocks
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

import streamlit as st


@dataclass
class StockInfo:
    """股票基本資訊"""
    ticker: str                           # 輸入的股票代碼
    normalized_ticker: str                # 規範化後代碼（含交易所後綴）
    name_zh: str = ""                     # 中文名稱（若有）
    name_en: str = ""                     # 英文名稱
    exchange: str = ""                    # 交易所名稱
    currency: str = ""                    # 幣別
    current_price: Optional[float] = None # 當前股價
    prev_close: Optional[float] = None    # 上一收盤價
    price_change: Optional[float] = None  # 漲跌幅（%）
    week52_high: Optional[float] = None   # 52 週最高
    week52_low: Optional[float] = None    # 52 週最低
    ipo_date: Optional[date] = None       # 上市日期
    market_cap: Optional[float] = None    # 市值
    sector: str = ""                      # 行業板塊
    error: str = ""                       # 錯誤訊息（若有）
    raw_info: dict = field(default_factory=dict)  # yfinance raw info


# 常見 A 股/港股中文名稱簡短後綴映射
_EXCHANGE_SUFFIXES = {
    "hk": ".HK",
    "ss": ".SS",
    "sz": ".SZ",
    "us": "",
    "": "",
}

# 常用 A 股交易所代碼識別
_SS_SZ_PATTERN = re.compile(r"^(\d{6})(?:\.(ss|sz))?$", re.IGNORECASE)
_HK_PATTERN    = re.compile(r"^(\d{4,5})(?:\.hk)?$", re.IGNORECASE)


def _normalize_ticker(raw: str) -> str:
    """
    將使用者輸入的股票代碼規範化，自動補全交易所後綴。

    規則：
    - 6 位數字且以 6 開頭 → 上交所 .SS
    - 6 位數字且以 0/3 開頭 → 深交所 .SZ
    - 4~5 位純數字 → 港交所 .HK（補零至 4 位）
    - 其他 → 直接回傳（美股等）
    """
    t = raw.strip().upper()
    # 已包含後綴則直接回傳
    if "." in t:
        return t
    # A 股
    if re.match(r"^\d{6}$", t):
        if t.startswith("6"):
            return f"{t}.SS"
        return f"{t}.SZ"
    # 港股（純數字 4-5 位）
    if re.match(r"^\d{4,5}$", t):
        return f"{t.zfill(4)}.HK"
    return t


def _extract_zh_name(info: dict) -> str:
    """
    嘗試從 yfinance info 中找到中文名稱。
    優先序：displayName → shortName（若含中文字元）→ longName（若含中文字元）
    """
    for key in ("displayName", "shortName", "longName"):
        val = info.get(key, "") or ""
        # 含 CJK 統一漢字則視為中文名稱
        if any("\u4e00" <= c <= "\u9fff" for c in val):
            return val
    return ""


@st.cache_data(ttl=300, show_spinner=False)
def fetch_stock_info(ticker_input: str) -> StockInfo:
    """
    從 yfinance 擷取股票資訊。

    Parameters:
        ticker_input: 使用者輸入的股票代碼（支援 AAPL / 00700 / 700.HK / 600519.SS 等格式）

    Returns:
        StockInfo dataclass；若出錯則 .error 欄位有說明。

    Note:
        使用 @st.cache_data(ttl=300) 快取 5 分鐘，避免頻繁呼叫 Yahoo Finance API。
    """
    try:
        import yfinance as yf  # lazy import
    except ImportError:
        return StockInfo(
            ticker=ticker_input,
            normalized_ticker=ticker_input,
            error="yfinance 未安裝 / yfinance not installed. Run: pip install yfinance",
        )

    normalized = _normalize_ticker(ticker_input)

    try:
        tkr = yf.Ticker(normalized)
        info = tkr.info or {}
    except Exception as exc:
        return StockInfo(
            ticker=ticker_input,
            normalized_ticker=normalized,
            error=f"無法連接 Yahoo Finance / Cannot connect to Yahoo Finance: {exc}",
        )

    # 檢查是否取得有效資訊
    if not info or info.get("trailingPegRatio") is None and not info.get("shortName"):
        # 有些股票只有 quoteType 但沒有詳細資訊
        if not info.get("quoteType") and not info.get("symbol"):
            return StockInfo(
                ticker=ticker_input,
                normalized_ticker=normalized,
                error=(
                    f"找不到股票代碼 '{normalized}' 的資訊。"
                    f"請確認代碼格式（如 700.HK / AAPL / 600519.SS）。"
                    f" / Cannot find stock '{normalized}'. "
                    f"Please check the ticker format (e.g. 700.HK / AAPL / 600519.SS)."
                ),
            )

    # ── 名稱 ─────────────────────────────────────────────
    name_zh = _extract_zh_name(info)
    name_en = info.get("longName") or info.get("shortName") or normalized

    # ── 股價 ─────────────────────────────────────────────
    current_price = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("navPrice")
    )
    prev_close = info.get("previousClose") or info.get("regularMarketPreviousClose")
    price_change: Optional[float] = None
    if current_price and prev_close and prev_close != 0:
        price_change = (current_price - prev_close) / prev_close * 100.0

    week52_high = info.get("fiftyTwoWeekHigh")
    week52_low  = info.get("fiftyTwoWeekLow")

    # ── 上市日期 ─────────────────────────────────────────
    ipo_date: Optional[date] = None
    # yfinance 提供 ipoExpectedDate（即將上市）或 firstTradeDateEpochUtc
    raw_ipo = info.get("ipoExpectedDate")
    if raw_ipo:
        try:
            ipo_date = datetime.strptime(raw_ipo, "%Y-%m-%d").date()
        except Exception:
            pass

    if ipo_date is None:
        first_epoch = info.get("firstTradeDateEpochUtc")
        if first_epoch:
            try:
                ipo_date = datetime.utcfromtimestamp(first_epoch).date()
            except Exception:
                pass

    # 備用：從歷史資料取第一筆交易日
    if ipo_date is None:
        try:
            hist = tkr.history(period="max", auto_adjust=True)
            if not hist.empty:
                idx = hist.index[0]
                if hasattr(idx, "date"):
                    ipo_date = idx.date()
                else:
                    ipo_date = idx.to_pydatetime().date()
        except Exception:
            pass

    return StockInfo(
        ticker=ticker_input,
        normalized_ticker=normalized,
        name_zh=name_zh,
        name_en=name_en,
        exchange=info.get("exchange", "") or info.get("fullExchangeName", ""),
        currency=info.get("currency", ""),
        current_price=current_price,
        prev_close=prev_close,
        price_change=price_change,
        week52_high=week52_high,
        week52_low=week52_low,
        ipo_date=ipo_date,
        market_cap=info.get("marketCap"),
        sector=info.get("sector") or info.get("industry") or "",
        raw_info=info,
    )


def get_display_name(stock: StockInfo) -> str:
    """回傳優先使用中文的顯示名稱"""
    if stock.name_zh:
        return f"{stock.name_zh} ({stock.name_en})" if stock.name_en else stock.name_zh
    return stock.name_en or stock.normalized_ticker


def get_price_ratio(stock: StockInfo) -> Optional[float]:
    """
    計算當前股價在 52 週高低範圍中的百分比位置（0~100%）。
    類似命宮強弱度：0-20% 弱宮，80-100% 旺相。

    Returns None if data is insufficient.
    """
    if (
        stock.current_price is not None
        and stock.week52_high is not None
        and stock.week52_low is not None
        and stock.week52_high != stock.week52_low
    ):
        ratio = (stock.current_price - stock.week52_low) / (stock.week52_high - stock.week52_low)
        return max(0.0, min(1.0, ratio)) * 100.0
    return None


def get_strength_label(ratio: Optional[float]) -> tuple[str, str, str]:
    """
    根據股價比例返回七政四餘強弱判斷標籤。

    Returns:
        (label_zh, label_en, color_hex)
    """
    if ratio is None:
        return "資料不足", "Insufficient Data", "#9090b8"
    if ratio >= 80:
        return "旺相（強勢）", "Wang Xiang — Strong", "#FFD700"
    if ratio >= 60:
        return "得令（偏強）", "De Ling — Above Average", "#86efac"
    if ratio >= 40:
        return "中和（平穩）", "Zhong He — Neutral", "#60a5fa"
    if ratio >= 20:
        return "失令（偏弱）", "Shi Ling — Below Average", "#fb923c"
    return "休囚（弱宮）", "Xiu Qiu — Weak", "#f87171"
