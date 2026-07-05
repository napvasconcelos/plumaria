"""Visualização: paletas de cores colorblind-safe derivadas de plumagens de aves.

O módulo `palettes` funciona só com numpy para acessar as cores; registrar
colormaps e ajustar rcParams do matplotlib exige o extra ``neurotools[viz]``.
"""

from . import palettes

__all__ = ["palettes"]
