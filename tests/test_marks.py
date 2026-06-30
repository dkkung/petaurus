import altair as alt
import numpy as np
import polars as pl
import pytest

from dysonsphere.marks import mark_strip, mark_violin
from dysonsphere.theme import theme

CATEGORIES = ["A", "B", "C"]


@pytest.fixture(autouse=True)
def default_theme():
    theme(chartWidth=200, chartHeight=200)


@pytest.fixture
def group_df():
    rng = np.random.default_rng(0)
    n = 15
    return pl.DataFrame({
        "group": CATEGORIES * n,
        "value": rng.normal(0, 1, len(CATEGORIES) * n),
    })


class TestMarkViolin:
    def test_returns_layer_chart(self, group_df):
        result = mark_violin(group_df, xCol="group", yCol="value", categories=CATEGORIES)
        assert isinstance(result, alt.LayerChart)

    def test_custom_palette_list(self, group_df):
        result = mark_violin(
            group_df, xCol="group", yCol="value", categories=CATEGORIES,
            palette=["#FF0000", "#00FF00", "#0000FF"],
        )
        assert isinstance(result, alt.LayerChart)

    def test_y_title_default_is_col_name(self, group_df):
        result = mark_violin(group_df, xCol="group", yCol="value", categories=CATEGORIES)
        spec = result.to_dict()
        layer_specs = spec.get("layer", [])
        y_titles = [
            layer.get("encoding", {}).get("y", {}).get("title")
            for layer in layer_specs
            if layer.get("encoding", {}).get("y", {}).get("title") is not None
        ]
        assert any(t == "value" for t in y_titles)

    def test_y_title_none_suppresses(self, group_df):
        result = mark_violin(
            group_df, xCol="group", yCol="value", categories=CATEGORIES, yTitle=None
        )
        spec = result.to_dict()
        for layer in spec.get("layer", []):
            y_enc = layer.get("encoding", {}).get("y", {})
            assert y_enc.get("title") is None or "title" not in y_enc

    def test_violin_x_uses_absolute_quantitative(self, group_df):
        # Violin line mark encodes x:Q with axis=None - absolute pixel coordinates,
        # not xOffset - so hconcat with mark_strip never squishes the violin.
        result = mark_violin(group_df, xCol="group", yCol="value", categories=CATEGORIES)
        spec = result.to_dict()
        violin_layer = next(
            l for l in spec["layer"]
            if isinstance(l.get("mark"), dict) and l["mark"].get("type") == "line"
        )
        x_enc = violin_layer["encoding"]["x"]
        assert x_enc["type"] == "quantitative"
        # axis=None serialises as null in to_dict()
        assert x_enc.get("axis") is None
        chart_width = alt.theme.options.get("chartWidth", 200)
        assert x_enc["scale"]["domain"] == [0, chart_width]

    def test_violin_no_xoffset_in_any_layer(self, group_df):
        # No layer uses xOffset - Vega-Lite won't merge xOffset scales across hconcat panels.
        result = mark_violin(group_df, xCol="group", yCol="value", categories=CATEGORIES)
        spec = result.to_dict()
        for layer in spec["layer"]:
            assert "xOffset" not in layer.get("encoding", {})


class TestMarkStrip:
    def test_returns_layer_chart(self, group_df):
        result = mark_strip(group_df, xCol="group", yCol="value", categories=CATEGORIES)
        assert isinstance(result, alt.LayerChart)

    def test_errorbars_disabled(self, group_df):
        result = mark_strip(
            group_df, xCol="group", yCol="value", categories=CATEGORIES, errorbars=False
        )
        assert isinstance(result, alt.LayerChart)

    def test_beeswarm_scatter(self, group_df):
        result = mark_strip(
            group_df, xCol="group", yCol="value", categories=CATEGORIES, scatter="beeswarm"
        )
        assert isinstance(result, alt.LayerChart)

    def test_invalid_scatter_raises(self, group_df):
        with pytest.raises(ValueError, match="scatter"):
            mark_strip(
                group_df, xCol="group", yCol="value", categories=CATEGORIES, scatter="invalid"
            )
