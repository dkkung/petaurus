# Changelog

## [v0.9.0] - 2026-06-25

### New features

**Asterisk significance labels in `add_pvalue()`**
`add_pvalue()` now accepts `label_style="asterisks"` to render significance as `*` / `**` / `***` / `ns` instead of an exact p-value. Thresholds: `*` p < 0.05, `**` p < 0.01, `***` p < 0.001. The bracket shape parameter has been renamed from `style` to `bracket_style` for clarity.

**`background` parameter in `save()`**
`save()` now accepts `background=["light"]` or `background=["dark"]` to render only one variant instead of both. Defaults to `["light", "dark"]` (no change in behaviour).

### Bug fixes

- **`mark_strip()` errorbars** were incorrectly centered on the median while using SEM (a mean-based statistic). They now correctly center on the mean.
- **`add_multilabel()` docstring** referenced `style="dots"` (invalid); corrected to `style="symbol"`.

### Changes

- Default `mark_circle()` size reduced to `markSize / 5` (was `markSize`).
- Default `mark_point()` size reduced to `markSize / 2` (was `markSize`).

---

## [v0.8.0] - 2026-06-24

### Breaking changes

- `add_grid_labels()` and `add_grid_labels_detached()` are renamed to `add_multilabel()` and `add_multilabel_detached()`.
- `options()` is renamed to `theme()`. Initialise the theme with `ds.theme()`.
- The recommended import alias changes from `import dysonsphere as theme` to `import dysonsphere as ds`.

---

## [v0.7.0] - 2026-06-24

### New features

**`add_grid_labels()` / `add_grid_labels_detached()`** — condition-table annotation layers for placing below strip, violin, and boxplot charts. Each row is a condition label; each column aligns with an x-axis category.

- `style="plusminus"` renders `True`/`False` as `+` / `−`
- `style="symbol"` renders `True` as a filled mark and `False` as an unfilled mark, with a horizontal connecting rule across consecutive `True` runs. The `symbol` parameter accepts any Vega-Lite shape (`"circle"`, `"square"`, `"diamond"`, `"triangle-up"`, etc.)
- `style="text"` renders arbitrary strings or numbers — triggered automatically when group values are non-bool
- `palette` parameter overrides mark colors (pass the result of `theme.palette()`)

**`add_pvalue()`** — consolidated p-value bracket API. Replaces the previous two-function design with a single call supporting multiple pairs, stacked brackets, and manual or computed positions.

**New mark defaults** for `arc`, `errorband`, and `geoshape`.

### Changes

- **Palette rename:** `"rose"` → `"pinks"`. Paired divergent palettes updated.

### Bug fixes

- **Grid label x-axis alignment** — at high PPI, annotation marks were misaligned with x-axis tick positions due to Vega flooring SVG tick transforms to integers. Fixed via SVG post-processing in `theme.save()`.

---

## [v0.6.0] - 2026-06-22

### New features

**Analytic beeswarm offsets**
`add_beeswarm()` now uses an analytic placement algorithm matching the approach used by `geom_beeswarm()` from the R package `ggbeeswarm`. For each point, the exact forbidden x intervals imposed by already-placed neighbours are computed as `px ± √((2·spread)² − dy²)`, and the position closest to 0 outside all intervals is chosen. This produces tighter, more symmetric swarms than the previous grid-search approach.

**Unified `spread` parameter**
`add_jitter()`, `add_beeswarm()`, and `mark_strip()` now share a single `spread` parameter for controlling point spread in pixels. For jitter, `spread` is the Gaussian standard deviation (~68% of points within ±spread). For beeswarm, it is the collision radius (no two point centres closer than 2·spread). When `spread=None`, beeswarm defaults to `√(markSize/π)` from the active theme so point size and collision radius stay in sync automatically.

**Renamed transforms**
`add_jitter_offsets()` and `add_beeswarm_offsets()` have been renamed to `add_jitter()` and `add_beeswarm()`.

**Legend symbol size**
Legend symbols now scale with `fontSize` (`fontSize × 6`) rather than `markSize`, so they remain proportional to the label text regardless of mark size.

**`save()` moved to `export.py`**
`save()` and its SVG helpers (`_fix_tick_alignment`, `_simplify_svg`) have been moved to a new `dysonsphere/export.py` module. The public API is unchanged.

### Bug fixes

**Tick alignment fix for quantitative axes**
The SVG tick alignment pass previously misidentified quantitative x-axis ticks (e.g. on line or area charts) as nominal band-scale ticks, remapping them to wrong positions. A validation step now checks that collected tick positions match expected band-scale floor positions before applying the fix — quantitative and time axes are left untouched.

---

## [v0.5.0] - 2026-06-22

### New features

**`pvalue_layers()` — batch p-value annotations**
A new companion to `pvalue_layer()` that accepts a list of comparisons and returns a combined Altair layer in one call, removing the need to manually loop and stack individual brackets.

**x-axis tick alignment fix for violin and strip charts**
`save()` now includes SVG post-processing that corrects a Vega rendering quirk: Vega floors axis-tick group transforms to integers for screen sharpness, but keeps mark coordinates as floats. At high DPI this causes visible misalignment between ticks and marks.

For bar charts the fix reads bar centers directly from the SVG path data. For all other charts (violin, strip, etc.) band centers are computed analytically from the number of categories and `bandPadding`, then validated against the expected floor positions before being applied — so quantitative and time axes are left untouched.

### Bug fixes

A secondary bug was also fixed: the y-axis tick at the maximum data value renders as `translate(0,0)` in SVG, which the original regex matched as an x-axis tick, inflating the category count by one and producing wrong positions. The fix excludes any tick with a zero translate value.

---

## [v0.4.0] - 2026-06-21

Renamed package from petaurus to dysonsphere. Rebuilt green palettes and all paired diverging palettes using a new multi-hue greens base.

---

## [v0.3.1] - 2026-06-20

Initial beta release of **petaurus** — now available on PyPI.

```sh
pip install petaurus
```

### What's included

- `petaurus.options()` — global Altair theme configuration (fonts, axes, marks, palettes, and more)
- Perceptually uniform palettes built in Oklab, plus ports of matplotlib and cmocean palettes
- `petaurus.palette()` — slice and sample any named palette
- `petaurus.save()` — export light/dark PNG, SVG, and Vega-Lite JSON in one call
- `petaurus.mark_violin()` — violin plot with embedded boxplot
- `petaurus.mark_strip()` — jittered or beeswarm strip plot with optional error bars
- `petaurus.pvalue_layer()` — p-value bracket annotations
- Jitter and beeswarm offset helpers

### Notes

This is a personal project under active development. Breaking changes may occur between minor versions.
