import polars as pl
import pytest

from dysonsphere.nonlinear import (
    _derive_exp,
    add_log_ticks,
    add_pow_ticks,
    log_label_expr,
)
from dysonsphere.theme import theme

_SUP = "⁰¹²³⁴⁵⁶⁷⁸⁹"


@pytest.fixture(autouse=True)
def default_theme():
    theme()


@pytest.fixture
def log_df():
    return pl.DataFrame({"v": [1.0, 10.0, 100.0, 1000.0]})


@pytest.fixture
def base_chart(log_df):
    import altair as alt
    return alt.Chart(log_df).mark_point().encode(y="v:Q")


class TestLogLabelExpr:
    def test_returns_string(self):
        assert isinstance(log_label_expr(), str)

    def test_base10_power_contains_base(self):
        expr = log_label_expr(base=10)
        assert "'10'" in expr or "10" in expr

    def test_base2_power_contains_base(self):
        expr = log_label_expr(base=2)
        assert "'2'" in expr or "log(2)" in expr

    def test_superscript_chars_present(self):
        expr = log_label_expr()
        assert any(c in expr for c in _SUP)

    def test_scientific_base10(self):
        expr = log_label_expr(notation="scientific")
        assert "1×10" in expr

    def test_scientific_non_base10_raises(self):
        with pytest.raises(ValueError, match="base=10"):
            log_label_expr(base=2, notation="scientific")

    def test_unknown_notation_raises(self):
        with pytest.raises(ValueError, match="notation"):
            log_label_expr(notation="invalid")

    def test_negative_exponent_marker_present(self):
        expr = log_label_expr()
        assert "⁻" in expr


class TestDeriveExp:
    def test_base10_decade(self):
        df = pl.DataFrame({"v": [1.0, 100.0]})
        lo, hi = _derive_exp(df, "v", base=10)
        assert lo == 0
        assert hi == 2

    def test_base10_single_decade(self):
        df = pl.DataFrame({"v": [10.0, 1000.0]})
        lo, hi = _derive_exp(df, "v", base=10)
        assert lo == 1
        assert hi == 3

    def test_base2(self):
        df = pl.DataFrame({"v": [1.0, 8.0]})
        lo, hi = _derive_exp(df, "v", base=2)
        assert lo == 0
        assert hi == 3


class TestAddLogTicks:
    def test_returns_layer_chart(self, base_chart, log_df):
        import altair as alt
        result = add_log_ticks(base_chart, log_df, "v")
        assert isinstance(result, alt.LayerChart)

    def test_invalid_axis_raises(self, base_chart, log_df):
        with pytest.raises(ValueError, match="axis"):
            add_log_ticks(base_chart, log_df, "v", axis="z")

    def test_missing_field_raises(self, base_chart, log_df):
        with pytest.raises(ValueError, match="field"):
            add_log_ticks(base_chart, log_df)

    def test_both_axis_missing_fields_raises(self, base_chart, log_df):
        with pytest.raises(ValueError, match="xField"):
            add_log_ticks(base_chart, log_df, axis="both")

    def test_x_axis(self, log_df):
        import altair as alt
        chart = alt.Chart(log_df).mark_point().encode(x="v:Q")
        result = add_log_ticks(chart, log_df, "v", axis="x")
        assert isinstance(result, alt.LayerChart)

    def test_exp_override(self, base_chart, log_df):
        import altair as alt
        result = add_log_ticks(base_chart, log_df, "v", expMin=0, expMax=4)
        assert isinstance(result, alt.LayerChart)


class TestAddPowTicks:
    def test_returns_layer_chart(self, base_chart, log_df):
        import altair as alt
        result = add_pow_ticks(base_chart, log_df, "v", majorValues=[0, 1, 4, 9, 16])
        assert isinstance(result, alt.LayerChart)

    def test_invalid_axis_raises(self, base_chart, log_df):
        with pytest.raises(ValueError, match="axis"):
            add_pow_ticks(base_chart, log_df, "v", axis="z", majorValues=[0, 1, 4])

    def test_zero_exponent_raises(self, base_chart, log_df):
        with pytest.raises(ValueError, match="exponent"):
            add_pow_ticks(base_chart, log_df, "v", exponent=0, majorValues=[0, 1, 4])

    def test_missing_major_values_raises(self, base_chart, log_df):
        with pytest.raises(ValueError, match="majorValues"):
            add_pow_ticks(base_chart, log_df, "v")

    def test_single_major_value_raises(self, base_chart, log_df):
        with pytest.raises(ValueError, match="at least two"):
            add_pow_ticks(base_chart, log_df, "v", majorValues=[0])

    def test_missing_field_raises(self, base_chart, log_df):
        with pytest.raises(ValueError, match="field"):
            add_pow_ticks(base_chart, log_df, majorValues=[0, 1, 4])

    def test_both_axis_missing_fields_raises(self, base_chart, log_df):
        with pytest.raises(ValueError, match="xField"):
            add_pow_ticks(base_chart, log_df, axis="both")
