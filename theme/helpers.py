import numpy as np
import polars as pl
import altair as alt

from .colors import colors


def palette_range(
    name: str,
    n: int | None = None,
    start: int = 0,
    stop: int | None = None,
    step: int = 1,
    reverse: bool = False,
) -> list[str]:
    """
    Sample colors from a named palette with control over start, stop, and spacing.

    When ``n`` is provided, evenly samples ``n`` colors between ``start`` and
    ``stop`` (linspace). Otherwise, returns every ``step``-th color from
    ``start`` to ``stop`` — with default ``step=1`` this returns the full slice.

    Parameters
    ----------
    name:
        Key in the ``colors`` dict (e.g. ``"mpl_YlGnBu"``).
    n:
        Number of colors to return (evenly spaced). Takes priority over ``step``.
    start:
        Index of the first color to include. Defaults to 0.
    stop:
        Index of the last color to include (inclusive). Defaults to the last
        index in the palette.
    step:
        Step between color indices. Defaults to 1 (every color).
    reverse:
        If True, reverse the returned list.

    Examples
    --------
    All colors in the palette:

        palette_range("mpl_YlGnBu")

    Last 4 colors:

        palette_range("mpl_YlGnBu", start=5)

    Four evenly-spaced colors across the full palette:

        palette_range("mpl_YlGnBu", n=4)

    Every second color from index 0 to 6 (returns indices 0, 2, 4, 6):

        palette_range("mpl_YlGnBu", stop=6, step=2)

    Four evenly-spaced colors, reversed:

        palette_range("mpl_YlGnBu", n=4, reverse=True)
    """
    palette = colors[name]
    total = len(palette)
    if stop is None:
        stop = total - 1

    if n is not None:
        if n == 1:
            indices = [start]
        else:
            indices = [round(start + i * (stop - start) / (n - 1)) for i in range(n)]
    else:
        indices = list(range(start, stop + 1, step))

    result = [palette[i] for i in indices]
    return result[::-1] if reverse else result


def beeswarm_offsets(
    y_vals,
    height_px: int = 200,
    mark_size: float = 10,
    step: float | None = None,
) -> np.ndarray:
    """
    Compute x offsets (pixels) for a beeswarm plot using collision avoidance.

    Converts y values to pixel space, then places each point at the nearest
    x position (outward from 0) that does not overlap any already-placed point.
    Use the result as an ``xOffset`` column in Altair.

    Parameters
    ----------
    y_vals:
        Array of y values for one group (e.g. one treatment × time combination).
    height_px:
        Chart height in pixels. Should match ``.properties(height=...)``.
    mark_size:
        Altair mark size (area in sq px). Should match the ``size=`` kwarg on
        the mark. Defaults to the theme's ``markSize`` default of 10.
    step:
        x step size (px) between candidate positions. Defaults to the point
        radius derived from ``mark_size``.

    Returns
    -------
    numpy.ndarray
        x offsets in pixels, one per input value, in the same order.

    Examples
    --------
    Compute offsets per group with Polars then plot in Altair::

        df = (
            df
            .with_row_index("__idx")
            .group_by(["Metadata_Treatment", "Metadata_Time"])
            .map_groups(lambda g: g.with_columns(
                pl.Series("beeswarm_x", theme.beeswarm_offsets(
                    g["my_column"].to_numpy(),
                    height_px=200,
                    mark_size=10,
                ))
            ))
            .sort("__idx")
            .drop("__idx")
        )

        alt.Chart(df).mark_circle(size=10).encode(
            x=alt.X("Metadata_Time:O"),
            y=alt.Y("my_column:Q"),
            xOffset=alt.XOffset("beeswarm_x:Q"),
        )
    """
    y_vals = np.asarray(y_vals, dtype=float)
    n = len(y_vals)
    if n == 0:
        return np.array([])

    r = np.sqrt(mark_size / np.pi)
    if step is None:
        step = r

    y_min, y_max = y_vals.min(), y_vals.max()
    y_px = (y_vals - y_min) / max(y_max - y_min, 1e-9) * height_px

    min_dist_sq = (2 * r) ** 2
    order = np.argsort(y_px)
    placed_y = np.empty(n)
    placed_x = np.empty(n)
    offsets = np.zeros(n)
    n_placed = 0

    for idx in order:
        y = y_px[idx]
        nearby = np.abs(placed_y[:n_placed] - y) <= 4 * r
        for k in range(1000):
            for cx in [0.0] if k == 0 else [k * step, -k * step]:
                ny = placed_y[:n_placed][nearby]
                nx = placed_x[:n_placed][nearby]
                if len(ny) == 0 or np.all(
                    (ny - y) ** 2 + (nx - cx) ** 2 >= min_dist_sq
                ):
                    placed_y[n_placed] = y
                    placed_x[n_placed] = cx
                    n_placed += 1
                    offsets[idx] = cx
                    break
            else:
                continue
            break

    return offsets


def add_beeswarm_offsets(
    df: pl.DataFrame,
    y_col: str,
    group_by: list[str],
    height_px: int = 200,
    mark_size: float = 10,
    step: float | None = None,
    out_col: str = "beeswarm_x",
) -> pl.DataFrame:
    """
    Add a beeswarm x-offset column to a Polars DataFrame, computed per group.

    A convenience wrapper around :func:`beeswarm_offsets` that handles the
    ``with_row_index`` / ``map_groups`` / ``sort`` / ``drop`` pattern.

    Parameters
    ----------
    df:
        Input DataFrame.
    y_col:
        Name of the column containing y values.
    group_by:
        Column name(s) that define each beeswarm group (e.g.
        ``["Metadata_Treatment", "Metadata_Time"]``).
    height_px:
        Chart height in pixels.
    mark_size:
        Altair mark size (area in sq px).
    step:
        x step size (px). Defaults to the point radius.
    out_col:
        Name of the output offset column added to the DataFrame.

    Returns
    -------
    polars.DataFrame
        Original DataFrame with an additional ``out_col`` column.

    Examples
    --------
    ::

        df = theme.add_beeswarm_offsets(
            df,
            y_col="percent",
            group_by=["Metadata_Treatment", "Metadata_Time"],
            height_px=200,
            mark_size=10,
        )

        alt.Chart(df).mark_circle(size=10).encode(
            x=alt.X("Metadata_Time:O"),
            y=alt.Y("percent:Q"),
            xOffset=alt.XOffset("beeswarm_x:Q"),
        )
    """
    return (
        df.with_row_index("__beeswarm_idx")
        .group_by(group_by)
        .map_groups(
            lambda g: g.with_columns(
                pl.Series(
                    out_col,
                    beeswarm_offsets(
                        g[y_col].to_numpy(),
                        height_px=height_px,
                        mark_size=mark_size,
                        step=step,
                    ),
                )
            )
        )
        .sort("__beeswarm_idx")
        .drop("__beeswarm_idx")
    )


def _format_pvalue(p: float) -> str:
    if p < 0.001:
        return "p < 0.001"
    elif p < 0.01:
        return "p < 0.01"
    elif p < 0.05:
        return "p < 0.05"
    else:
        return f"p = {p:.2f}"


def pvalue_layer(
    df: pl.DataFrame | None = None,
    x_col: str | None = None,
    y_col: str | None = None,
    group1: str | None = None,
    group2: str | None = None,
    *,
    test: str = "mannwhitneyu",
    pvalue: float | None = None,
    correction: str | None = None,
    n_comparisons: int = 1,
    y: float | None = None,
    y_pad: float = 5,
    tick_height: float = 5,
    style: str = "bracket",
    categories: list | None = None,
    chart_width: int = 400,
    stroke_width: float = 0.5,
    font_size: int = 7,
) -> alt.LayerChart:
    """
    Build an Altair layer with a p-value annotation between two groups.

    Combine with your chart using ``+``:  ``chart + pvalue_layer(...)``.

    Parameters
    ----------
    df:
        Polars DataFrame. Required unless both ``pvalue`` and ``y`` are provided.
    x_col:
        Column name for the grouping variable (x-axis).
    y_col:
        Column name for the value variable (y-axis). Used to extract group
        data for the test and to auto-place the bracket when ``y`` is omitted.
    group1, group2:
        Values in ``x_col`` identifying the two groups to compare.
    test:
        Scipy test to run: ``'mannwhitneyu'``, ``'ttest_ind'``, ``'ttest_rel'``,
        or ``'wilcoxon'``. Ignored when ``pvalue`` is provided.
    pvalue:
        Pre-computed p-value. Skips the statistical test entirely.
    correction:
        Multiple comparison correction: ``'bonferroni'`` or ``None``.
    n_comparisons:
        Total number of comparisons for Bonferroni correction.
    y:
        Y position of the bracket in data units. Defaults to
        ``max(group data) + y_pad``.
    y_pad:
        Padding above the group maximum when ``y`` is auto-placed.
    tick_height:
        Height of the bracket end ticks in data units.
    style:
        ``'bracket'`` (horizontal bar + end ticks) or ``'line'`` (bar only).
    categories:
        Ordered list of all x-axis categories, used to compute the midpoint
        pixel position for the text label. Inferred from ``df`` if not provided
        (sorted alphabetically, matching Vega-Lite's default nominal ordering).
    chart_width:
        Width of the chart in pixels. Used with ``categories`` to compute
        text x position. Should match ``.properties(width=...)``.
    stroke_width:
        Stroke width of bracket lines.
    font_size:
        Font size of the p-value label in points.

    Examples
    --------
    From a DataFrame::

        chart = alt.Chart(df).mark_point().encode(x="group:N", y="value:Q")
        ann = theme.pvalue_layer(
            df, "group", "value", "Control", "Drug A",
            test="mannwhitneyu", y=210,
            categories=["Control", "Drug A", "Drug B"],
            chart_width=300,
        )
        chart + ann

    From a pre-computed p-value::

        _, p = scipy.stats.mannwhitneyu(ctrl, drug_a)
        ann = theme.pvalue_layer(
            group1="Control", group2="Drug A",
            pvalue=p, y=210,
            categories=["Control", "Drug A", "Drug B"],
            chart_width=300,
        )
    """
    from scipy import stats as _stats

    # --- p-value ---
    if pvalue is None:
        if df is None or x_col is None or y_col is None:
            raise ValueError("df, x_col, and y_col are required when pvalue is not provided.")
        a = df.filter(pl.col(x_col) == group1)[y_col].to_numpy()
        b = df.filter(pl.col(x_col) == group2)[y_col].to_numpy()
        _tests = {
            "mannwhitneyu": lambda: _stats.mannwhitneyu(a, b, alternative="two-sided").pvalue,
            "ttest_ind":    lambda: _stats.ttest_ind(a, b).pvalue,
            "ttest_rel":    lambda: _stats.ttest_rel(a, b).pvalue,
            "wilcoxon":     lambda: _stats.wilcoxon(a, b).pvalue,
        }
        if test not in _tests:
            raise ValueError(f"Unknown test {test!r}. Choose from: {list(_tests)}")
        pvalue = _tests[test]()

    if correction == "bonferroni":
        pvalue = min(pvalue * n_comparisons, 1.0)

    label = _format_pvalue(pvalue)

    # --- y position ---
    if y is None:
        if df is None or x_col is None or y_col is None:
            raise ValueError("y is required when df, x_col, and y_col are not provided.")
        y = float(df.filter(pl.col(x_col).is_in([group1, group2]))[y_col].max()) + y_pad

    # --- categories and text x position ---
    if categories is None:
        if df is None or x_col is None:
            raise ValueError("categories is required when df and x_col are not provided.")
        categories = sorted(df[x_col].unique().to_list())

    band_w = chart_width / len(categories)
    g1_idx = categories.index(group1)
    g2_idx = categories.index(group2)
    x_mid_px = ((g1_idx + g2_idx + 1) / 2) * band_w

    # --- layers ---
    _rule_kwargs = {"strokeWidth": stroke_width, "strokeDash": [0, 0]}

    bar = (
        alt.Chart(alt.Data(values=[{"x": group1, "x2": group2, "y": y}]))
        .mark_rule(**_rule_kwargs)
        .encode(
            x=alt.X("x:N"),
            x2="x2:N",
            y=alt.Y("y:Q"),
        )
    )

    text = (
        alt.Chart(alt.Data(values=[{"y": y, "label": label}]))
        .mark_text(align="center", fontSize=font_size, dy=-6)
        .encode(
            x=alt.value(x_mid_px),
            y=alt.Y("y:Q"),
            text="label:N",
        )
    )

    if style == "bracket":
        left_tick = (
            alt.Chart(alt.Data(values=[{"x": group1, "y": y, "y2": y - tick_height}]))
            .mark_rule(**_rule_kwargs)
            .encode(
                x=alt.X("x:N"),
                y=alt.Y("y:Q"),
                y2="y2:Q",
            )
        )
        right_tick = (
            alt.Chart(alt.Data(values=[{"x": group2, "y": y, "y2": y - tick_height}]))
            .mark_rule(**_rule_kwargs)
            .encode(
                x=alt.X("x:N"),
                y=alt.Y("y:Q"),
                y2="y2:Q",
            )
        )
        return alt.layer(bar, left_tick, right_tick, text)

    return alt.layer(bar, text)
