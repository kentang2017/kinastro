# astro/chinstar package

from astro.chinstar.chinstar import WanHuaXianQin  # noqa: F401


def compute_chinstar_chart(
    year: int,
    month: int,
    day: int,
    hour: int,
    gender: str = "M",
) -> dict:
    """Compute ChinStar (WanHua XianQin) chart.

    Args:
        year: Lunar year
        month: Lunar month (1-12)
        day: Lunar day (1-30)
        hour: 24-hour format (0-23)
        gender: "M" for male, "F" for female

    Returns:
        Dict containing chart data
    """
    calculator = WanHuaXianQin()
    return calculator.build_chart(year, month, day, hour, gender)


from astro.chinstar.renderer import render_chinstar_chart  # noqa: F401
