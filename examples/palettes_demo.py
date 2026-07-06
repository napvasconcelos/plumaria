"""Paletas "Aves" colorblind-safe: ciclo categórico e colormaps.

Requer o extra de visualização:  pip install -e '.[viz]'
Rode com:  python examples/palettes_demo.py
"""

import numpy as np
import matplotlib.pyplot as plt

from plumaria import palettes

# Registra os colormaps "aves_*" e usa a paleta categórica como padrão.
palettes.set_defaults()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

# --- Ciclo categórico: uma linha por "grupo" ----------------------------
t = np.linspace(0, 2 * np.pi, 200)
for i in range(len(palettes.CATEGORICAL)):
    ax1.plot(t, np.sin(t + i * np.pi / 8) + i, lw=2)
ax1.set_title("Paleta categórica (Aves)")
ax1.set_yticks([])

# --- Colormap sequencial em um heatmap ----------------------------------
grid = np.add.outer(np.linspace(0, 1, 50), np.linspace(0, 1, 50))
im = ax2.imshow(grid, cmap="aves_saiazul")
ax2.set_title("Colormap sequencial: aves_saiazul")
ax2.set_xticks([])
ax2.set_yticks([])
fig.colorbar(im, ax=ax2, fraction=0.046)

fig.tight_layout()
out = "aves_palettes_demo.png"
fig.savefig(out, dpi=120)
print(f"Figura salva em {out}")
print("Colormaps registrados:", palettes.register())
