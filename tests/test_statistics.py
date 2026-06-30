import altair as alt
import numpy as np
import polars as pl
import pytest

from dysonsphere.statistics import _format_asterisks, _format_pvalue, add_pvalue
from dysonsphere.theme import theme

CATEGORIES = ["A", "B"]


@pytest.fixture(autouse=True)
def default_theme():
    theme(chartWidth=200, chartHeight=200)


@pytest.fixture
def group_df():
    rng = np.random.default_rng(0)
    return pl.DataFrame(
        {
            "group": CATEGORIES * 15,
            "value": rng.normal(0, 1, 30),
        }
    )


class TestFormatPvalue:
    def test_below_threshold(self):
        assert _format_pvalue(0.0005) == "P < 0.001"

    def test_exactly_threshold(self):
        assert _format_pvalue(0.001) == "P = 0.001"

    def test_above_threshold(self):
        assert _format_pvalue(0.0234) == "P = 0.023"

    def test_custom_decimals(self):
        assert _format_pvalue(0.1, decimals=2) == "P = 0.10"

    def test_p_one(self):
        assert _format_pvalue(1.0) == "P = 1.000"

    def test_p_zero(self):
        assert _format_pvalue(0.0) == "P < 0.001"


class TestFormatAsterisks:
    def test_three_stars(self):
        assert _format_asterisks(0.0005) == "***"

    def test_exactly_0001(self):
        assert _format_asterisks(0.001) == "**"

    def test_two_stars(self):
        assert _format_asterisks(0.005) == "**"

    def test_exactly_001(self):
        assert _format_asterisks(0.01) == "*"

    def test_one_star(self):
        assert _format_asterisks(0.025) == "*"

    def test_exactly_005(self):
        assert _format_asterisks(0.05) == "ns"

    def test_ns(self):
        assert _format_asterisks(0.1) == "ns"

    def test_p_one(self):
        assert _format_asterisks(1.0) == "ns"


class TestAddPvalue:
    def test_returns_layer_chart_with_explicit_pvalue(self, group_df):
        result = add_pvalue(group_df, "group", "value", [("A", "B")], pvalues=[0.01])
        assert isinstance(result, alt.LayerChart)

    def test_returns_layer_chart_running_test(self, group_df):
        result = add_pvalue(group_df, "group", "value", [("A", "B")])
        assert isinstance(result, alt.LayerChart)

    def test_multiple_pairs(self, group_df):
        df = pl.DataFrame(
            {
                "group": ["A"] * 10 + ["B"] * 10 + ["C"] * 10,
                "value": np.random.default_rng(1).normal(0, 1, 30),
            }
        )
        result = add_pvalue(
            df,
            "group",
            "value",
            [("A", "B"), ("B", "C")],
            pvalues=[0.01, 0.05],
        )
        assert isinstance(result, alt.LayerChart)

    def test_asterisk_label_style(self, group_df):
        result = add_pvalue(
            group_df,
            "group",
            "value",
            [("A", "B")],
            pvalues=[0.001],
            labelStyle="asterisks",
        )
        assert isinstance(result, alt.LayerChart)

    def test_unknown_test_raises(self, group_df):
        with pytest.raises(ValueError, match="Unknown test"):
            add_pvalue(group_df, "group", "value", [("A", "B")], test="bogus")
