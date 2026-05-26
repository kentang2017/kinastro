import pytest

from astro.tieban import tieban_browser
from astro.tieban.tieban_browser import (
    _paginate_items,
    _slice_page,
    render_palace_verses_paginated,
)


def test_slice_page_returns_requested_window():
    items = list(range(1, 121))

    assert _slice_page(items, page=2, page_size=50) == list(range(51, 101))


def test_slice_page_clamps_out_of_range_page():
    items = list(range(1, 76))

    assert _slice_page(items, page=99, page_size=50) == list(range(51, 76))


def test_slice_page_rejects_non_positive_page_size():
    with pytest.raises(ValueError, match="page_size"):
        _slice_page([1, 2, 3], page=1, page_size=0)


def test_paginate_items_returns_full_list_when_single_page():
    items, total_pages, page = _paginate_items([1, 2, 3], page_size=50, key_prefix="single")

    assert items == [1, 2, 3]
    assert total_pages == 1
    assert page == 1


def test_paginate_items_uses_selected_page(monkeypatch):
    monkeypatch.setattr(tieban_browser.st, "selectbox", lambda *args, **kwargs: 2)

    items, total_pages, page = _paginate_items(
        list(range(1, 121)),
        page_size=50,
        key_prefix="multi",
    )

    assert items == list(range(51, 101))
    assert total_pages == 3
    assert page == 2


def test_render_palace_verses_paginated_renders_selected_page(monkeypatch):
    monkeypatch.setattr(tieban_browser.st, "selectbox", lambda *args, **kwargs: 2)
    markdown_calls = []
    caption_calls = []
    monkeypatch.setattr(
        tieban_browser.st,
        "markdown",
        lambda text, **kwargs: markdown_calls.append(text),
    )
    monkeypatch.setattr(tieban_browser.st, "caption", lambda text: caption_calls.append(text))

    palace_verses = {
        palace: {"verse": f"{palace}條文", "branch": "子", "category": "綜合"}
        for palace in [
            "命宮", "兄弟宮", "夫妻宮", "子女宮", "財帛宮", "疾厄宮",
            "遷移宮", "交友宮", "官祿宮", "田宅宮", "福德宮", "父母宮",
        ]
    }

    render_palace_verses_paginated(
        palace_verses,
        language="zh",
        page_size=4,
        key_prefix="test_palace_page",
    )

    assert markdown_calls
    html = markdown_calls[-1]
    assert "財帛宮" in html
    assert "疾厄宮" in html
    assert "遷移宮" in html
    assert "交友宮" in html
    assert "命宮" not in html
    assert caption_calls[-1] == "第 2/3 頁，共 12 條"


def test_render_palace_verses_paginated_english_fallback(monkeypatch):
    markdown_calls = []
    monkeypatch.setattr(
        tieban_browser.st,
        "markdown",
        lambda text, **kwargs: markdown_calls.append(text),
    )
    monkeypatch.setattr(tieban_browser.st, "caption", lambda text: None)

    render_palace_verses_paginated(
        {"命宮": {"branch": "子"}},
        language="en",
        page_size=12,
        key_prefix="test_palace_en",
    )

    html = markdown_calls[-1]
    assert "Life" in html
    assert "No verse yet" in html
