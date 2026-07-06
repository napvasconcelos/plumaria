"""Galeria "Aves": renderiza cards de paleta (foto + swatch + painel CVD).

Mostra o que diferencia o plumaria dos pacotes em R: cada card traz, além do
swatch e da proveniência, um painel de simulação de daltonismo e o relatório
de separabilidade perceptual (ΔE mínimo par-a-par).

Requer o extra de visualização:  pip install -e '.[viz]'
Rode com:  python examples/gallery_demo.py
"""

from plumaria.gallery import SAI_AZUL, BirdPalette, render_card

# (1) Card da ave de exemplo que acompanha o pacote (Saí-azul).
render_card(SAI_AZUL, outfile="card_sai_azul.png")
print("Card salvo em card_sai_azul.png")

# (2) Construindo a sua própria paleta: basta um BirdPalette. As cores abaixo
# vêm da paleta categórica curada do pacote (todas colorblind-safe).
saira = BirdPalette(
    slug="saira_sete_cores",
    common_name_pt="Saíra-sete-cores",
    indigenous_name=None,
    scientific_name="Tangara seledon",
    region="Mata Atlântica (Brasil, Paraguai, Argentina)",
    hex_colors=["#126C7D", "#1AA6BE", "#EFBE30", "#F76F24", "#32253B"],
    palette_type="qualitative",
    photographer="ilustrativo",
    license="—",
)
render_card(saira, outfile="card_saira_sete_cores.png")
print("Card salvo em card_saira_sete_cores.png")
