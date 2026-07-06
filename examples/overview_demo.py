"""Catálogo "de relance" de todas as paletas Aves (estilo cheatsheet).

Gera uma figura única, uma linha por paleta (categórica + colormaps), com o
swatch normal, as três simulações de daltonismo, o tipo e o código de uso.
É o análogo das folhas de referência de paletas do seaborn — só que com a
simulação de CVD embutida, que é o diferencial do plumaria.

Requer o extra de visualização:  pip install -e '.[viz]'
Rode com:  python examples/overview_demo.py
"""

from plumaria.gallery import render_overview

# cvd=True: mostra normal + protanopia/deuteranopia/tritanopia por paleta.
render_overview(cvd=True, outfile="aves_overview.png")
print("Catálogo salvo em aves_overview.png")

# cvd=False: só os swatches normais, mais compacto.
render_overview(cvd=False, outfile="aves_overview_simples.png")
print("Catálogo simples salvo em aves_overview_simples.png")
