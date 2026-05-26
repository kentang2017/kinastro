import pytest

from astro.tieban.tieban_browser import _slice_page


def test_slice_page_returns_requested_window():
    items = list(range(1, 121))

    assert _slice_page(items, page=2, page_size=50) == list(range(51, 101))


def test_slice_page_clamps_out_of_range_page():
    items = list(range(1, 76))

    assert _slice_page(items, page=99, page_size=50) == list(range(51, 76))


def test_slice_page_rejects_non_positive_page_size():
    with pytest.raises(ValueError, match="page_size"):
        _slice_page([1, 2, 3], page=1, page_size=0)
