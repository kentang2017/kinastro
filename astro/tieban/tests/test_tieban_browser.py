import pytest

from astro.tieban import tieban_browser
from astro.tieban.tieban_browser import _paginate_items, _slice_page


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
