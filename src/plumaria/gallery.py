"""Galeria: renderiza um "card" matplotlib por paleta de ave.

Replica o layout dos cards do pacote ``Manu`` (swatch + foto da ave +
metadados) e acrescenta o que só o plumaria faz: um painel de simulação de
daltonismo (CVD) do swatch e um relatório de separabilidade perceptual
(ΔE mínimo par-a-par), além de um bloco de proveniência da foto.

matplotlib é opcional (extra ``plumaria[viz]``). O modelo de dados
:class:`BirdPalette` funciona só com numpy; :func:`render_card` exige
matplotlib.

Rode ``python -m plumaria.gallery`` para renderizar o card de exemplo
(Saí-azul) em disco.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Literal, Optional

import numpy as np

from .cvd import CVD_TYPES, separability_report, simulate_cvd
from .palettes import COLORMAPS, SEQUENTIAL, CATEGORICAL, colormap, hex_to_rgb

PaletteType = Literal["qualitative", "sequential", "diverging"]

# Rótulos curtos das linhas do painel de CVD, na ordem de CVD_TYPES.
_CVD_LABELS = {
    "protanomaly": "Protanopia",
    "deuteranomaly": "Deuteranopia",
    "tritanomaly": "Tritanopia",
}

__all__ = ["BirdPalette", "render_card", "render_overview"]


@dataclass
class BirdPalette:
    """Uma paleta derivada da plumagem de uma ave, com proveniência.

    Os campos de proveniência (foto, fotógrafo, licença, fonte) são opcionais
    mas fortemente encorajados: a atribuição é parte do contrato de uso das
    fotos que dão origem às cores.
    """

    slug: str
    common_name_pt: str
    indigenous_name: Optional[str]
    scientific_name: str
    region: str
    hex_colors: List[str]
    palette_type: PaletteType
    photo_path: Optional[str] = None
    photographer: Optional[str] = None
    license: Optional[str] = None
    source_url: Optional[str] = None

    def __post_init__(self):
        if not self.slug or self.slug != self.slug.lower() or any(
            ch.isspace() for ch in self.slug
        ):
            raise ValueError(
                f"slug inválido: {self.slug!r} (use minúsculas, sem espaços)."
            )
        if len(self.hex_colors) < 2:
            raise ValueError("hex_colors precisa de >= 2 cores.")
        # Valida cada cor reutilizando o parser hex canônico (levanta se inválida).
        for color in self.hex_colors:
            hex_to_rgb(color)
        valid_types = ("qualitative", "sequential", "diverging")
        if self.palette_type not in valid_types:
            raise ValueError(
                f"palette_type inválido: {self.palette_type!r}. Use {valid_types}."
            )

    @property
    def rgb(self) -> np.ndarray:
        """Cores da paleta como array float ``(N, 3)`` em [0, 1]."""
        return np.array([hex_to_rgb(c) for c in self.hex_colors], dtype=float)


def _draw_swatch(ax, rgb_rows, col_labels=None, row_labels=None):
    """Desenha uma grade de cores ``(rows, cols, 3)`` num Axes.

    ``rgb_rows`` de forma ``(N, 3)`` é tratado como uma única linha.
    """
    rgb_rows = np.asarray(rgb_rows, dtype=float)
    if rgb_rows.ndim == 2:  # (N, 3) -> (1, N, 3)
        rgb_rows = rgb_rows[None, :, :]
    n_rows, n_cols = rgb_rows.shape[:2]
    ax.imshow(rgb_rows, aspect="auto", interpolation="nearest")
    # Linhas de grade finas separando os patches.
    ax.set_xticks(np.arange(-0.5, n_cols, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, n_rows, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.5)
    ax.tick_params(which="both", length=0)
    if col_labels is not None:
        ax.set_xticks(range(n_cols))
        ax.set_xticklabels(col_labels, fontsize=7, family="monospace")
    else:
        ax.set_xticks([])
    if row_labels is not None:
        ax.set_yticks(range(n_rows))
        ax.set_yticklabels(row_labels, fontsize=8)
    else:
        ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def _draw_photo(ax, palette):
    """Desenha a foto da ave, ou um placeholder se não houver arquivo."""
    import matplotlib.pyplot as plt

    ax.set_xticks([])
    ax.set_yticks([])
    path = palette.photo_path
    if path and os.path.exists(path):
        ax.imshow(plt.imread(path), aspect="equal")
    else:
        # Placeholder — mantém o card funcional end-to-end sem foto cabeada.
        ax.imshow(np.full((10, 10, 3), 0.92), aspect="equal")
        ax.text(
            0.5, 0.5, "sem foto", transform=ax.transAxes,
            ha="center", va="center", fontsize=13, color="#999999",
        )
    for spine in ax.spines.values():
        spine.set_color("#cccccc")


def _header_text(palette):
    """Monta o cabeçalho: nome comum, científico, indígena e região."""
    lines = [palette.common_name_pt]
    subtitle = palette.scientific_name
    if palette.indigenous_name:
        subtitle = f"{subtitle}  ·  “{palette.indigenous_name}”"
    lines.append(subtitle)
    lines.append(palette.region)
    return lines


def _report_lines(palette):
    """Linhas do relatório de separabilidade perceptual (ΔE)."""
    report = separability_report(palette.hex_colors)
    flag = "✓ segura" if report["safe"] else "⚠ risco"
    lines = [
        f"Separabilidade perceptual — ΔE mín. par-a-par (CAM02-UCS)   [{flag}]",
        f"   normal        {report['normal']:5.1f}",
    ]
    for cvd_type in CVD_TYPES:
        lines.append(f"   {_CVD_LABELS[cvd_type]:<13} {report[cvd_type]:5.1f}")
    worst_cond, worst_de = report["worst"]
    worst_name = _CVD_LABELS.get(worst_cond, worst_cond)
    lines.append(f"   pior caso: {worst_name} (ΔE {worst_de:.1f})")
    return lines


def _provenance_lines(palette):
    """Bloco de proveniência da foto e da fonte das cores."""
    parts = []
    if palette.photographer:
        parts.append(f"Foto: {palette.photographer}")
    if palette.license:
        parts.append(f"Licença: {palette.license}")
    lines = ["   ".join(parts)] if parts else []
    if palette.source_url:
        lines.append(palette.source_url)
    if not lines:
        lines = ["proveniência não informada"]
    return lines


def render_card(palette, outfile=None, dpi=150):
    """Renderiza o card da paleta e retorna a ``Figure`` matplotlib.

    Layout (de cima para baixo): cabeçalho com os nomes, foto da ave, swatch
    da paleta com os hex, painel de simulação CVD do swatch, relatório de
    separabilidade perceptual e bloco de proveniência.

    Se ``outfile`` for dado, salva a figura nesse caminho.
    """
    import matplotlib

    matplotlib.use("Agg", force=False)
    import matplotlib.pyplot as plt

    rgb = palette.rgb
    hex_labels = [c.upper() for c in palette.hex_colors]
    cvd_stack = np.stack([simulate_cvd(rgb, t) for t in CVD_TYPES])  # (3, N, 3)
    cvd_row_labels = [_CVD_LABELS[t] for t in CVD_TYPES]

    fig = plt.figure(figsize=(7.2, 9.6), dpi=dpi)
    fig.patch.set_facecolor("white")
    gs = fig.add_gridspec(
        nrows=6,
        ncols=1,
        height_ratios=[0.9, 3.2, 0.8, 1.4, 1.9, 0.9],
        hspace=0.55,
        left=0.11, right=0.95, top=0.95, bottom=0.04,
    )

    # (0) Cabeçalho.
    ax_head = fig.add_subplot(gs[0])
    ax_head.axis("off")
    head = _header_text(palette)
    ax_head.text(0, 0.85, head[0], fontsize=20, fontweight="bold", va="top")
    ax_head.text(0, 0.42, head[1], fontsize=11, fontstyle="italic",
                 color="#333333", va="top")
    ax_head.text(0, 0.08, head[2], fontsize=9, color="#666666", va="top")

    # (1) Foto da ave.
    ax_photo = fig.add_subplot(gs[1])
    _draw_photo(ax_photo, palette)

    # (2) Swatch da paleta (visão normal), com hex.
    ax_swatch = fig.add_subplot(gs[2])
    _draw_swatch(ax_swatch, rgb, col_labels=hex_labels)
    ax_swatch.set_title(
        f"Paleta ({palette.palette_type}) — {len(palette.hex_colors)} cores",
        fontsize=9, loc="left", pad=6,
    )

    # (3) Painel de simulação CVD.
    ax_cvd = fig.add_subplot(gs[3])
    _draw_swatch(ax_cvd, cvd_stack, row_labels=cvd_row_labels)
    ax_cvd.set_title("Simulação de daltonismo (CVD)", fontsize=9, loc="left", pad=6)

    # (4) Relatório de separabilidade perceptual.
    ax_report = fig.add_subplot(gs[4])
    ax_report.axis("off")
    ax_report.text(
        0, 1.0, "\n".join(_report_lines(palette)),
        family="monospace", fontsize=8.5, va="top", linespacing=1.5,
    )

    # (5) Proveniência.
    ax_prov = fig.add_subplot(gs[5])
    ax_prov.axis("off")
    ax_prov.text(
        0, 1.0, "\n".join(_provenance_lines(palette)),
        fontsize=8, color="#555555", va="top", linespacing=1.5,
    )

    if outfile:
        fig.savefig(outfile, dpi=dpi, facecolor=fig.get_facecolor())
    return fig


def _cmap_rgb(name, n):
    """Amostra um colormap "aves_*" em ``n`` pontos -> array ``(n, 3)`` em [0,1]."""
    cmap = colormap(name, n=n)
    return cmap(np.linspace(0.0, 1.0, n))[:, :3]


def _overview_entries(n_continuous):
    """Monta as linhas do catálogo: (título, tipo, código, rgb, hex_ou_None).

    ``hex_labels`` só é preenchido para a paleta categórica (discreta); os
    colormaps contínuos entram como faixa amostrada, sem rótulos por cor.
    """
    entries = [(
        "aves_categorical", "qualitative", "plumaria.categorical()",
        np.array([hex_to_rgb(c) for c in CATEGORICAL], dtype=float),
        [c.upper() for c in CATEGORICAL],
    )]
    for name in COLORMAPS:
        kind = "sequential" if name in SEQUENTIAL else "diverging"
        entries.append((
            name, kind, f'cmap="{name}"', _cmap_rgb(name, n_continuous), None,
        ))
    return entries


def render_overview(cvd=True, outfile=None, dpi=150, n_continuous=48):
    """Catálogo "de relance" de todas as paletas Aves, uma por linha.

    No espírito das folhas de referência do seaborn, mas com o diferencial do
    plumaria: se ``cvd`` (padrão), cada paleta aparece como o swatch normal
    seguido das três simulações de daltonismo empilhadas. Cada bloco traz o
    nome, o tipo e o snippet de código para usar a paleta; a categórica ainda
    exibe o flag de separabilidade perceptual.

    Retorna a ``Figure``; se ``outfile`` for dado, também salva em disco.
    Requer matplotlib.
    """
    import matplotlib

    matplotlib.use("Agg", force=False)
    import matplotlib.pyplot as plt

    entries = _overview_entries(n_continuous)
    row_labels = (
        ["normal"] + [_CVD_LABELS[t] for t in CVD_TYPES] if cvd else None
    )

    n = len(entries)
    fig = plt.figure(figsize=(9.0, 2.2 * n + 0.4), dpi=dpi)
    fig.patch.set_facecolor("white")
    fig.suptitle(
        "plumaria — paletas Aves (swatch + simulação de daltonismo)",
        fontsize=13, fontweight="bold", x=0.11, ha="left", y=0.985,
    )
    gs = fig.add_gridspec(
        nrows=n, ncols=1, hspace=1.0,
        left=0.14, right=0.97, top=0.93, bottom=0.03,
    )

    for i, (title, kind, code, rgb, hex_labels) in enumerate(entries):
        ax = fig.add_subplot(gs[i])
        if cvd:
            stack = np.stack([rgb] + [simulate_cvd(rgb, t) for t in CVD_TYPES])
            _draw_swatch(ax, stack, col_labels=hex_labels, row_labels=row_labels)
        else:
            _draw_swatch(ax, rgb, col_labels=hex_labels)

        header = f"{title}   ·   {kind}     {code}"
        if kind == "qualitative":
            report = separability_report([c for c in CATEGORICAL])
            flag = "✓ segura" if report["safe"] else "⚠ risco"
            worst_de = report["worst"][1]
            header += f"     [ΔE mín. {worst_de:.1f} · {flag}]"
        ax.set_title(header, fontsize=9, loc="left", pad=6)

    if outfile:
        fig.savefig(outfile, dpi=dpi, facecolor=fig.get_facecolor())
    return fig


# --------------------------------------------------------------------------- #
# Ave de exemplo cabeada — Saí-azul (Dacnis cayana), macho.
# Cores amostradas da plumagem turquesa/azul com máscara escura e bico.
# --------------------------------------------------------------------------- #
SAI_AZUL = BirdPalette(
    slug="sai_azul",
    common_name_pt="Saí-azul",
    indigenous_name="Saí",
    scientific_name="Dacnis cayana",
    region="Neotrópico (Mata Atlântica e Amazônia)",
    hex_colors=["#126C7D", "#1AA6BE", "#6DBBD5", "#12303A", "#EFBE30"],
    palette_type="qualitative",
    photo_path=None,  # sem foto cabeada: cai no placeholder
    photographer="Vinícius Kohn",
    license="CC BY-NC 2.0",
    source_url="https://www.instagram.com/viniciuskohnpassaros",
)


def main():
    """Renderiza o card de exemplo em disco e imprime o caminho."""
    outfile = os.path.abspath(f"plumaria_card_{SAI_AZUL.slug}.png")
    render_card(SAI_AZUL, outfile=outfile)
    print(f"Card renderizado em: {outfile}")
    return outfile


if __name__ == "__main__":
    main()
