import importlib.util
import sys
import types
from pathlib import Path


def _load_stock_fetcher_module():
    fake_st = types.ModuleType("streamlit")
    fake_st.cache_data = lambda *args, **kwargs: (lambda fn: fn)
    sys.modules["streamlit"] = fake_st

    file_path = (
        Path(__file__).resolve().parents[1]
        / "astro"
        / "qizheng"
        / "financial"
        / "stock_fetcher.py"
    )
    spec = importlib.util.spec_from_file_location("stock_fetcher_under_test", file_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_fetch_stock_info_uses_chart_fallback_when_info_rate_limited(monkeypatch):
    stock_fetcher = _load_stock_fetcher_module()

    class FakeTicker:
        @property
        def info(self):
            raise Exception("Too Many Requests. Rate limited.")

        @property
        def fast_info(self):
            return {}

    fake_yf = types.SimpleNamespace(Ticker=lambda _: FakeTicker())
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    monkeypatch.setattr(
        stock_fetcher,
        "_fetch_chart_quote_fallback",
        lambda _: (
            {
                "symbol": "AAPL",
                "quoteType": "EQUITY",
                "shortName": "Apple Inc.",
                "currentPrice": 210.5,
                "previousClose": 208.0,
                "fiftyTwoWeekHigh": 237.23,
                "fiftyTwoWeekLow": 164.08,
                "currency": "USD",
            },
            "",
        ),
    )

    stock = stock_fetcher.fetch_stock_info("AAPL")
    assert stock.error == ""
    assert stock.current_price == 210.5
    assert stock.prev_close == 208.0
    assert stock.week52_high == 237.23
    assert stock.week52_low == 164.08
    assert stock.currency == "USD"


def test_fetch_stock_info_reports_error_when_primary_and_fallback_fail(monkeypatch):
    stock_fetcher = _load_stock_fetcher_module()

    class FakeTicker:
        @property
        def info(self):
            raise Exception("Too Many Requests. Rate limited.")

        @property
        def fast_info(self):
            return {}

    fake_yf = types.SimpleNamespace(Ticker=lambda _: FakeTicker())
    monkeypatch.setitem(sys.modules, "yfinance", fake_yf)
    monkeypatch.setattr(stock_fetcher, "_fetch_chart_quote_fallback", lambda _: ({}, "fallback failed"))

    stock = stock_fetcher.fetch_stock_info("AAPL")
    assert "Cannot connect to Yahoo Finance" in stock.error
    assert "fallback also failed" in stock.error
