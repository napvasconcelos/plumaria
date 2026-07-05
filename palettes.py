"""Paletas de cores "Aves": categórica colorblind-safe e colormaps contínuos.

As cores foram amostradas de fotografias de plumagens de aves
(fonte: Vinícius Kohn, @viniciuskohnpassaros) e ajustadas para permanecerem
distinguíveis sob os três tipos de daltonismo (deuteranopia, protanopia,
tritanopia). A seleção da paleta categórica foi feita maximizando a distância
perceptual mínima (CIE Lab) entre pares de cores, simulando o daltonismo pelas
matrizes de Machado et al. (2009); o ΔE mínimo resultante fica ~15, na mesma
faixa da paleta Okabe-Ito.

Uso rápido
----------
>>> from neurotools.viz import palettes
>>> palettes.categorical(3)
['#0A458A', '#F76F24', '#126C7D']
>>> palettes.register()          # registra colormaps no matplotlib
>>> import matplotlib.pyplot as plt
>>> plt.get_cmap("aves_saiazul")            # doctest: +SKIP
>>> palettes.set_defaults()                 # ciclo de cores + cmap padrão

matplotlib é opcional: `categorical`, `hex_to_rgb` e os dados de cores funcionam
só com numpy; `colormap`, `register` e `set_defaults` exigem matplotlib
(instale com o extra ``neurotools[viz]``).
"""

from __future__ import annotations

import numpy as np

# Paleta categórica (qualitativa), na ordem de uso. Cada cor vem de uma ave.
CATEGORICAL = [
    "#0A458A",  # Surucuá        (azul escuro)
    "#F76F24",  # Tangará        (laranja)
    "#126C7D",  # Saí-azul       (teal)
    "#EFBE30",  # Gaturamo       (amarelo)
    "#32253B",  # Gaturamo       (roxo/quase-preto)
    "#965F3B",  # Ferrugem       (marrom)
    "#1AA6BE",  # Beija-flor     (turquesa)
    "#BB9066",  # Fulvo          (bege)
]

# Rótulo (ave) de cada cor da paleta categórica, na mesma ordem.
CATEGORICAL_NAMES = [
    "Surucuá",
    "Tangará",
    "Saí-azul",
    "Gaturamo (amarelo)",
    "Gaturamo (roxo)",
    "Ferrugem",
    "Beija-flor",
    "Fulvo",
]

# Colormaps contínuos, como âncoras (claro -> escuro / extremo -> extremo).
# Sequencial: mono-matiz, intrinsecamente seguro para daltonismo.
# Divergente: dois matizes com ponto neutro claro no centro.
SEQUENTIAL = {
    "aves_saiazul": ["#0D4B4C", "#126C7D", "#218AA5", "#46A0BE", "#6DBBD5"],
}
DIVERGING = {
    "aves_gaturamo": [
        "#32253B", "#5E5476", "#A9A0BC", "#ECE7DA", "#E7C87F", "#D3A231", "#8A6B10",
    ],
    "aves_beijaflor": [
        "#1AA6BE", "#69B9C4", "#B7CFCF", "#ECE7DA", "#E29FB6", "#C74C86", "#941059",
    ],
}

# Todos os colormaps por nome -> lista de âncoras.
COLORMAPS = {**SEQUENTIAL, **DIVERGING}

__all__ = [
    "CATEGORICAL",
    "CATEGORICAL_NAMES",
    "SEQUENTIAL",
    "DIVERGING",
    "COLORMAPS",
    "hex_to_rgb",
    "categorical",
    "colormap",
    "register",
    "set_defaults",
]


def hex_to_rgb(color: str) -> tuple:
    """Converte '#RRGGBB' em tupla (r, g, b) normalizada em [0, 1]."""
    h = color.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"Cor hex inválida: {color!r} (esperado '#RRGGBB').")
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def categorical(n: int | None = None) -> list:
    """Retorna a paleta categórica como lista de cores hex.

    Com `n` omitido, devolve as 8 cores. Com `n <= 8`, devolve as `n`
    primeiras (ordenadas por distinguibilidade). Com `n > 8`, cicla a paleta.
    """
    if n is None:
        return list(CATEGORICAL)
    if n < 0:
        raise ValueError("n deve ser não-negativo.")
    if n <= len(CATEGORICAL):
        return CATEGORICAL[:n]
    return [CATEGORICAL[i % len(CATEGORICAL)] for i in range(n)]


def colormap(name: str, n: int = 256):
    """Constrói um `LinearSegmentedColormap` a partir das âncoras de `name`.

    `name` deve estar em `COLORMAPS`. Requer matplotlib.
    """
    if name not in COLORMAPS:
        raise KeyError(
            f"Colormap {name!r} desconhecido. Disponíveis: {sorted(COLORMAPS)}."
        )
    from matplotlib.colors import LinearSegmentedColormap

    anchors = [hex_to_rgb(c) for c in COLORMAPS[name]]
    return LinearSegmentedColormap.from_list(name, anchors, N=n)


def register(n: int = 256) -> list:
    """Registra todos os colormaps "aves_*" no matplotlib (com variante `_r`).

    Idempotente: re-registrar sobrescreve. Retorna os nomes registrados.
    Requer matplotlib.
    """
    import warnings

    import matplotlib as mpl

    if hasattr(mpl, "colormaps"):  # matplotlib >= 3.6

        def reg(cmap, name):
            mpl.colormaps.register(cmap, name=name, force=True)

    else:  # matplotlib < 3.6

        def reg(cmap, name):
            mpl.cm.register_cmap(name=name, cmap=cmap)

    registered = []
    with warnings.catch_warnings():
        # Re-registrar é intencional (idempotente): silencia o aviso de overwrite.
        warnings.filterwarnings("ignore", message="Overwriting the cmap")
        for name in COLORMAPS:
            cmap = colormap(name, n=n)
            reg(cmap, name)
            reg(cmap.reversed(), name + "_r")
            registered += [name, name + "_r"]
    return registered


def set_defaults(cmap: str = "aves_saiazul", categorical_cycle: bool = True) -> None:
    """Define padrões de plotagem no matplotlib rcParams.

    - Registra os colormaps "aves_*" (idempotente).
    - `image.cmap` = `cmap` (padrão: sequencial Saí-azul).
    - Se `categorical_cycle`, define o ciclo de cores dos eixos como a paleta
      categórica Aves.

    Requer matplotlib.
    """
    import matplotlib as mpl
    from cycler import cycler

    register()
    mpl.rcParams["image.cmap"] = cmap
    if categorical_cycle:
        mpl.rcParams["axes.prop_cycle"] = cycler(color=CATEGORICAL)
