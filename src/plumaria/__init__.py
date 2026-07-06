"""plumaria: paletas de cores colorblind-safe derivadas de plumagens de aves.

Paleta categórica de 8 cores e colormaps contínuos (sequencial e divergentes),
todos seguros para daltonismo. O acesso às cores funciona só com numpy;
registrar colormaps e ajustar rcParams exige o extra ``plumaria[viz]`` (matplotlib).

>>> import plumaria
>>> plumaria.categorical(3)              # 3 primeiras cores da paleta
>>> plumaria.register()                  # registra os colormaps no matplotlib
>>> plumaria.set_defaults()              # ciclo de cores + cmap padrão

O submódulo ``plumaria.palettes`` também está disponível para compatibilidade
(ex.: ``from plumaria import palettes; palettes.categorical()``).
"""

from . import palettes
from .palettes import (
    CATEGORICAL,
    CATEGORICAL_NAMES,
    SEQUENTIAL,
    DIVERGING,
    COLORMAPS,
    hex_to_rgb,
    categorical,
    colormap,
    register,
    set_defaults,
)

__version__ = "0.1.0"

__all__ = [
    "palettes",
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
    "__version__",
]
