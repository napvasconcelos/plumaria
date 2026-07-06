import pytest

from plumaria import palettes


def test_categorical_default_returns_eight_hex():
    cols = palettes.categorical()
    assert len(cols) == 8
    assert cols[0] == "#0A458A"
    assert all(c.startswith("#") and len(c) == 7 for c in cols)


def test_categorical_truncates_and_cycles():
    assert palettes.categorical(3) == palettes.CATEGORICAL[:3]
    twelve = palettes.categorical(12)
    assert len(twelve) == 12
    assert twelve[8] == palettes.CATEGORICAL[0]  # cicla após 8


def test_categorical_negative_raises():
    with pytest.raises(ValueError):
        palettes.categorical(-1)


def test_hex_to_rgb_bounds_and_values():
    assert palettes.hex_to_rgb("#000000") == (0.0, 0.0, 0.0)
    assert palettes.hex_to_rgb("#FFFFFF") == (1.0, 1.0, 1.0)
    r, g, b = palettes.hex_to_rgb("#0A458A")
    assert (round(r, 3), round(g, 3), round(b, 3)) == (0.039, 0.271, 0.541)


def test_hex_to_rgb_invalid_raises():
    with pytest.raises(ValueError):
        palettes.hex_to_rgb("#123")


def test_colormaps_have_expected_names():
    assert "aves_saiazul" in palettes.SEQUENTIAL
    assert set(palettes.COLORMAPS) == {"aves_saiazul", "aves_gaturamo", "aves_beijaflor"}


def test_colormap_unknown_name_raises():
    pytest.importorskip("matplotlib")
    with pytest.raises(KeyError):
        palettes.colormap("nao_existe")


def test_colormap_builds_with_requested_size():
    pytest.importorskip("matplotlib")
    from matplotlib.colors import LinearSegmentedColormap

    cmap = palettes.colormap("aves_saiazul", n=64)
    assert isinstance(cmap, LinearSegmentedColormap)
    assert cmap.N == 64


def test_register_makes_cmaps_retrievable():
    pytest.importorskip("matplotlib")
    import matplotlib.pyplot as plt

    names = palettes.register()
    assert "aves_saiazul" in names and "aves_saiazul_r" in names
    assert plt.get_cmap("aves_gaturamo") is not None
    palettes.register()  # idempotente: não deve levantar


def test_set_defaults_applies_cycle_and_cmap():
    pytest.importorskip("matplotlib")
    import matplotlib as mpl

    palettes.set_defaults()
    assert mpl.rcParams["image.cmap"] == "aves_saiazul"
    cycle_colors = mpl.rcParams["axes.prop_cycle"].by_key()["color"]
    assert cycle_colors == palettes.CATEGORICAL


def test_top_level_reexports():
    # A API principal também é acessível direto em `plumaria`.
    import plumaria

    assert plumaria.categorical(2) == palettes.categorical(2)
    assert plumaria.CATEGORICAL == palettes.CATEGORICAL
