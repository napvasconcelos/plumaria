"""Simulação de daltonismo (CVD) e separabilidade perceptual — o núcleo
accessibility-first do plumaria.

Contrasta a paleta categórica "Aves" (curada para permanecer separável sob
daltonismo) com uma paleta vermelho/verde ingênua, que colapsa sob
deuteranopia. Imprime o ΔE mínimo par-a-par em cada condição.

Não precisa de matplotlib — só numpy + colorspacious (extra plumaria[viz]).
Rode com:  python examples/cvd_demo.py
"""

from plumaria import cvd
from plumaria.palettes import CATEGORICAL


def print_report(nome, hex_colors):
    report = cvd.separability_report(hex_colors)
    flag = "✓ segura" if report["safe"] else "⚠ risco"
    print(f"\n{nome}  [{flag}]  ({len(hex_colors)} cores)")
    print(f"  normal        ΔE mín = {report['normal']:5.1f}")
    for cvd_type in cvd.CVD_TYPES:
        print(f"  {cvd_type:<13} ΔE mín = {report[cvd_type]:5.1f}")
    cond, de = report["worst"]
    print(f"  pior caso: {cond} (ΔE {de:.1f}); limiar de confusão = {cvd.JND_THRESHOLD}")


# Paleta curada do pacote: separável em todas as condições.
print_report("Categórica Aves", CATEGORICAL)

# Paleta ingênua vermelho/verde: alto contraste na visão normal, mas as duas
# cores colapsam sob deuteranopia/protanopia.
print_report("Vermelho x Verde (ingênua)", ["#D7191C", "#1A9641"])

# Inspecionando uma cor sob daltonismo: o verde vira um tom amarelado.
verde = [(0.10, 0.59, 0.25)]  # RGB [0,1]
print("\nVerde #1A9641 sob deuteranopia (severity=100):")
print("  ", cvd.simulate_cvd(verde, "deuteranomaly").round(3).tolist())
