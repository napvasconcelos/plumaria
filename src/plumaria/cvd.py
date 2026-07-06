"""Simulação de daltonismo (CVD) e métricas de separabilidade perceptual.

Este é o núcleo *accessibility-first* do plumaria: nenhum concorrente em R
(``feathers``, ``Manu``, ``tanagR``) simula deficiência de visão de cores
(CVD) dentro do próprio pacote. Aqui a simulação e as métricas de ΔE ficam a
um ``import`` de distância e alimentam o painel de CVD e o relatório de
separabilidade da galeria.

Sem dependência de matplotlib: só ``numpy`` + ``colorspacious`` (extra
``plumaria[viz]``). A simulação usa o espaço ``"sRGB1+CVD"`` do colorspacious
(modelo de Machado, Oliveira & Fernandes, 2009); as distâncias perceptuais
(ΔE) são euclidianas no espaço CAM02-UCS, onde a distância euclidiana
aproxima uma diferença perceptual uniforme.

>>> from plumaria import cvd
>>> cvd.min_pairwise_delta_e(["#0A458A", "#F76F24", "#126C7D"])          # doctest: +SKIP
>>> cvd.min_pairwise_delta_e(["#0A458A", "#F76F24"], "deuteranomaly")    # doctest: +SKIP
"""

from __future__ import annotations

import numpy as np
from colorspacious import cspace_convert

from .palettes import hex_to_rgb

# Tipos de daltonismo suportados pelo modelo "sRGB1+CVD" do colorspacious.
CVD_TYPES = ("protanomaly", "deuteranomaly", "tritanomaly")

# ΔE (CAM02-UCS) abaixo do qual duas cores tendem a se confundir. Heurística
# na faixa citada na literatura de paletas seguras; a paleta categórica Aves
# mira ΔE mínimo ~15, folgado acima deste piso.
JND_THRESHOLD = 10.0

__all__ = [
    "CVD_TYPES",
    "JND_THRESHOLD",
    "simulate_cvd",
    "delta_e_matrix",
    "min_pairwise_delta_e",
    "separability_report",
]


def simulate_cvd(rgb, cvd_type, severity=100):
    """Simula daltonismo sobre cores RGB float em [0, 1].

    Parâmetros
    ----------
    rgb : array-like
        Forma ``(3,)`` ou ``(N, 3)``, valores em [0, 1].
    cvd_type : str
        Um de :data:`CVD_TYPES`.
    severity : float
        0 (visão normal) a 100 (dicromacia completa).

    Retorna array float no mesmo shape da entrada, clipado em [0, 1] — a
    simulação pode projetar cores para fora do gamut sRGB.
    """
    if cvd_type not in CVD_TYPES:
        raise ValueError(f"cvd_type inválido: {cvd_type!r}. Use um de {CVD_TYPES}.")
    if not 0 <= severity <= 100:
        raise ValueError(f"severity deve estar em [0, 100], recebido {severity!r}.")
    arr = np.asarray(rgb, dtype=float)
    cvd_space = {"name": "sRGB1+CVD", "cvd_type": cvd_type, "severity": severity}
    out = cspace_convert(arr, cvd_space, "sRGB1")
    return np.clip(out, 0.0, 1.0)


def _palette_to_ucs(hex_colors, cvd_type=None):
    """Converte uma paleta hex para coordenadas CAM02-UCS ``(N, 3)``.

    Se ``cvd_type`` for dado, simula o daltonismo (severity=100) antes de
    converter, revelando como as cores colapsam sob aquela deficiência.
    """
    if len(hex_colors) < 2:
        raise ValueError("A paleta precisa de >= 2 cores para medir separabilidade.")
    rgb = np.array([hex_to_rgb(c) for c in hex_colors], dtype=float)
    if cvd_type is not None:
        rgb = simulate_cvd(rgb, cvd_type, severity=100)
    return cspace_convert(rgb, "sRGB1", "CAM02-UCS")


def delta_e_matrix(hex_colors, cvd_type=None):
    """Matriz ``(N, N)`` de distâncias perceptuais ΔE (CAM02-UCS) par-a-par.

    Simétrica, com diagonal nula. Se ``cvd_type`` for dado, mede sob aquela
    deficiência de visão de cores.
    """
    ucs = _palette_to_ucs(hex_colors, cvd_type=cvd_type)
    diff = ucs[:, None, :] - ucs[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=-1))


def min_pairwise_delta_e(hex_colors, cvd_type=None):
    """Menor ΔE entre qualquer par distinto de cores (pior caso de confusão).

    É a métrica-chave de uma paleta qualitativa: quanto maior, mais robusta a
    separação entre categorias.
    """
    matrix = delta_e_matrix(hex_colors, cvd_type=cvd_type)
    iu = np.triu_indices(matrix.shape[0], k=1)
    return float(matrix[iu].min())


def separability_report(hex_colors):
    """Relatório de separabilidade perceptual da paleta.

    Retorna um ``dict`` com o ΔE mínimo par-a-par sob visão normal e sob cada
    tipo de daltonismo, mais o pior caso e um flag de segurança::

        {
            "normal": float,
            "protanomaly": float,
            "deuteranomaly": float,
            "tritanomaly": float,
            "worst": (str, float),   # (condição, ΔE) de menor separação
            "safe": bool,            # pior caso >= JND_THRESHOLD
        }
    """
    report = {"normal": min_pairwise_delta_e(hex_colors)}
    for cvd_type in CVD_TYPES:
        report[cvd_type] = min_pairwise_delta_e(hex_colors, cvd_type=cvd_type)
    conditions = ("normal",) + CVD_TYPES
    worst = min(conditions, key=lambda cond: report[cond])
    report["worst"] = (worst, report[worst])
    report["safe"] = report[worst] >= JND_THRESHOLD
    return report
