"""Gera a galeria HTML de paletas (docs/index.html) a partir do pacote.

As cores simuladas sob daltonismo e o relatório de ΔE são computados aqui,
com o próprio plumaria (colorspacious), e injetados numa página estática
autossuficiente — pronta para servir via GitHub Pages. Rode este script
sempre que as paletas mudarem, para docs/ não desatualizar.

Requer:  pip install -e '.[viz]'
Rode:    python examples/build_gallery_html.py
"""

import json
import os

import numpy as np

from plumaria import cvd
from plumaria.palettes import (
    CATEGORICAL,
    CATEGORICAL_NAMES,
    COLORMAPS,
    SEQUENTIAL,
    colormap,
    hex_to_rgb,
)

CVD_ORDER = cvd.CVD_TYPES  # protanomaly, deuteranomaly, tritanomaly
N_CONTINUOUS = 14          # amostras exibidas por colormap contínuo


def _to_hex(rgb):
    rgb = np.clip(np.asarray(rgb, dtype=float), 0.0, 1.0)
    return ["#%02X%02X%02X" % tuple(int(round(c * 255)) for c in row) for row in rgb]


def _cmap_rgb(name, n):
    return colormap(name, n=n)(np.linspace(0.0, 1.0, n))[:, :3]


def build_data():
    """Estrutura de dados consumida pela página (mesmo shape do <script> JSON)."""
    palettes = []

    # Paleta categórica: discreta, com rótulos por ave e relatório de ΔE.
    rgb = np.array([hex_to_rgb(c) for c in CATEGORICAL], dtype=float)
    rep = cvd.separability_report(CATEGORICAL)
    palettes.append({
        "name": "aves_categorical",
        "kind": "qualitative",
        "code": "import plumaria\nplumaria.categorical()   # -> lista de 8 hex",
        "labels": list(CATEGORICAL_NAMES),
        "normal": _to_hex(rgb),
        "cvd": {t: _to_hex(cvd.simulate_cvd(rgb, t)) for t in CVD_ORDER},
        "report": {
            "normal": round(rep["normal"], 1),
            **{t: round(rep[t], 1) for t in CVD_ORDER},
            "worst": [rep["worst"][0], round(rep["worst"][1], 1)],
            "safe": rep["safe"],
        },
    })

    # Colormaps contínuos: faixa amostrada, sem rótulos por cor.
    for name in COLORMAPS:
        kind = "sequential" if name in SEQUENTIAL else "diverging"
        rgb = _cmap_rgb(name, N_CONTINUOUS)
        palettes.append({
            "name": name,
            "kind": kind,
            "code": (
                "import plumaria, matplotlib.pyplot as plt\n"
                "plumaria.register()\n"
                f'plt.imshow(data, cmap="{name}")'
            ),
            "labels": None,
            "normal": _to_hex(rgb),
            "cvd": {t: _to_hex(cvd.simulate_cvd(rgb, t)) for t in CVD_ORDER},
            "report": None,
        })

    return {"jnd": cvd.JND_THRESHOLD, "palettes": palettes}


def main():
    data = build_data()
    payload = json.dumps(data, ensure_ascii=False, indent=1)
    html = TEMPLATE.replace("__PALETTE_DATA__", payload)

    out = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "docs", "index.html"))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Galeria gerada em: {out}")
    return out


# --------------------------------------------------------------------------- #
# Template da página. `__PALETTE_DATA__` é substituído pelo JSON computado.
# String crua (r'''...''') para preservar as \b dos regexes do JavaScript.
# --------------------------------------------------------------------------- #
TEMPLATE = r'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>plumaria — galeria de paletas Aves</title>
<style>
  :root {
    --ground: #F5F6F4;
    --surface: #FFFFFF;
    --ink: #12303A;
    --muted: #5A6B70;
    --accent: #126C7D;
    --safe: #1F7A5A;
    --warn: #B26A00;
    --hairline: #DDE2DF;
    --serif: "Iowan Old Style", "Palatino Linotype", Palatino, "Book Antiqua", Georgia, serif;
    --sans: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
    --maxw: 940px;
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; }

  .page {
    background: var(--ground);
    color: var(--ink);
    font-family: var(--sans);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
    padding: clamp(1.25rem, 4vw, 3rem) clamp(1rem, 4vw, 2rem) 4rem;
  }

  .wrap { max-width: var(--maxw); margin: 0 auto; }

  .masthead { border-bottom: 1px solid var(--hairline); padding-bottom: 1.75rem; margin-bottom: 2.25rem; }
  .wordmark {
    font-family: var(--serif); font-weight: 600;
    font-size: clamp(2rem, 6vw, 2.9rem); letter-spacing: -0.01em;
    margin: 0 0 0.35rem; text-wrap: balance;
  }
  .wordmark .feather { color: var(--accent); }
  .thesis { max-width: 60ch; color: var(--muted); font-size: 1.02rem; margin: 0 0 1.4rem; text-wrap: pretty; }
  .thesis strong { color: var(--ink); font-weight: 600; }

  .legend { display: flex; flex-wrap: wrap; gap: 0.5rem 1.4rem; align-items: center; }
  .legend .cap { font-family: var(--mono); font-size: 0.68rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }
  .legend ul { display: flex; flex-wrap: wrap; gap: 0.35rem 0.9rem; list-style: none; margin: 0; padding: 0; }
  .legend li { font-size: 0.82rem; color: var(--ink); display: flex; align-items: center; gap: 0.4rem; }
  .legend .swatch-dot { width: 0.8rem; height: 0.8rem; border-radius: 2px; border: 1px solid rgba(0,0,0,.12); }

  .grid { display: flex; flex-direction: column; gap: 1.5rem; }

  .card { background: var(--surface); border: 1px solid var(--hairline); border-radius: 10px; padding: 1.4rem 1.5rem 1.5rem; }

  .card-head { display: flex; flex-wrap: wrap; align-items: baseline; gap: 0.6rem 0.9rem; margin-bottom: 1.05rem; }
  .pal-name { font-family: var(--mono); font-size: 1.28rem; font-weight: 600; color: var(--ink); margin: 0; letter-spacing: -0.01em; }
  .chip {
    font-family: var(--mono); font-size: 0.66rem; letter-spacing: 0.06em; text-transform: uppercase;
    padding: 0.2rem 0.55rem; border-radius: 999px; border: 1px solid var(--hairline);
    color: var(--muted); background: var(--ground); white-space: nowrap;
  }
  .chip.kind { color: var(--accent); border-color: color-mix(in srgb, var(--accent) 30%, var(--hairline)); }
  .chip.verdict { font-weight: 600; }
  .chip.verdict.safe { color: var(--safe); border-color: color-mix(in srgb, var(--safe) 40%, var(--hairline)); background: color-mix(in srgb, var(--safe) 8%, var(--surface)); }
  .chip.verdict.warn { color: var(--warn); border-color: color-mix(in srgb, var(--warn) 40%, var(--hairline)); background: color-mix(in srgb, var(--warn) 8%, var(--surface)); }

  .swatch { display: flex; border-radius: 6px; overflow: hidden; border: 1px solid var(--hairline); }
  .swatch.discrete .cell { flex: 1; }
  .cell { position: relative; height: 74px; display: flex; align-items: flex-end; justify-content: center; }
  .cell .hex {
    font-family: var(--mono); font-size: 0.68rem; padding: 0.25rem 0; width: 100%; text-align: center;
    background: rgba(255,255,255,0.82); color: #1a1a1a; letter-spacing: 0.02em;
    opacity: 0; transform: translateY(100%); transition: opacity .16s ease, transform .16s ease;
  }
  .cell:hover .hex, .cell:focus-visible .hex { opacity: 1; transform: translateY(0); }
  .cell .name {
    position: absolute; top: 0.4rem; left: 0; right: 0; text-align: center;
    font-size: 0.66rem; color: rgba(255,255,255,0.92); text-shadow: 0 1px 2px rgba(0,0,0,.45);
    padding: 0 0.2rem; opacity: 0; transition: opacity .16s ease; pointer-events: none;
  }
  .cell:hover .name, .cell:focus-visible .name { opacity: 1; }
  .swatch.gradient { height: 74px; display: block; }

  .hex-row { display: flex; margin-top: 0.4rem; }
  .hex-row span { flex: 1; text-align: center; font-family: var(--mono); font-size: 0.66rem; color: var(--muted); letter-spacing: 0.01em; }

  .cvd { margin-top: 1.25rem; }
  .cvd-title { font-family: var(--mono); font-size: 0.68rem; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); margin: 0 0 0.6rem; display: flex; align-items: center; gap: 0.5rem; }
  .cvd-title::after { content: ""; flex: 1; height: 1px; background: var(--hairline); }
  .cvd-row { display: grid; grid-template-columns: 116px 1fr; align-items: center; gap: 0.75rem; margin-bottom: 0.4rem; }
  .cvd-row .rl { font-family: var(--mono); font-size: 0.72rem; color: var(--ink); text-align: right; }
  .cvd-bar { display: flex; height: 26px; border-radius: 4px; overflow: hidden; border: 1px solid var(--hairline); }
  .cvd-bar .c { flex: 1; }
  .cvd-bar.gradient { display: block; }

  .stats { margin-top: 1.2rem; display: flex; flex-wrap: wrap; gap: 0.5rem; align-items: stretch; }
  .stat { border: 1px solid var(--hairline); border-radius: 6px; padding: 0.45rem 0.7rem; background: var(--ground); min-width: 92px; display: flex; flex-direction: column; gap: 0.1rem; }
  .stat .k { font-family: var(--mono); font-size: 0.62rem; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); }
  .stat .v { font-family: var(--mono); font-size: 1.05rem; font-weight: 600; font-variant-numeric: tabular-nums; color: var(--ink); }
  .stat.worst { border-color: color-mix(in srgb, var(--warn) 45%, var(--hairline)); }
  .stat.worst .v { color: var(--warn); }
  .stats .note { align-self: center; font-size: 0.8rem; color: var(--muted); max-width: 28ch; }

  .code { position: relative; margin-top: 1.25rem; background: var(--ink); border-radius: 8px; padding: 0.85rem 1rem; overflow-x: auto; }
  .code pre { margin: 0; font-family: var(--mono); font-size: 0.8rem; line-height: 1.6; color: #DCE6E4; white-space: pre; }
  .code .tok-kw { color: #7FD1C4; }
  .code .tok-str { color: #E7C87F; }
  .code .tok-com { color: #6E8A86; font-style: italic; }
  .copy {
    position: absolute; top: 0.55rem; right: 0.55rem; font-family: var(--mono); font-size: 0.66rem;
    letter-spacing: 0.05em; text-transform: uppercase; color: #9FB8B4;
    background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.16); border-radius: 5px;
    padding: 0.25rem 0.55rem; cursor: pointer; transition: background .15s ease, color .15s ease;
  }
  .copy:hover { background: rgba(255,255,255,0.16); color: #fff; }
  .copy.done { color: #8BD6B4; border-color: rgba(139,214,180,.4); }

  footer { margin-top: 2.5rem; padding-top: 1.5rem; border-top: 1px solid var(--hairline); color: var(--muted); font-size: 0.82rem; }
  footer .mono { font-family: var(--mono); }

  :focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 3px; }

  @media (max-width: 560px) {
    .cvd-row { grid-template-columns: 88px 1fr; gap: 0.5rem; }
    .cvd-row .rl { font-size: 0.66rem; }
    .hex-row { display: none; }
  }
  @media (prefers-reduced-motion: reduce) { * { transition: none !important; } }
</style>
</head>
<body>
<div class="page">
  <div class="wrap">
    <header class="masthead">
      <h1 class="wordmark"><span class="feather">plumaria</span> · galeria de paletas Aves</h1>
      <p class="thesis">
        Paletas de cores derivadas da plumagem de aves neotropicais, para Python.
        O diferencial: cada paleta é exibida <strong>sob simulação de deficiência de
        visão de cores (CVD)</strong> e vem com o ΔE mínimo par-a-par que mede a
        separação entre categorias — uma validação de acessibilidade que os pacotes
        equivalentes em R (feathers, Manu, tanagR) não fazem no próprio pacote.
      </p>
      <div class="legend">
        <span class="cap">cada paleta, sob</span>
        <ul>
          <li><span class="swatch-dot" style="background:#126C7D"></span>Visão normal</li>
          <li><span class="swatch-dot" style="background:#60687E"></span>Protanopia</li>
          <li><span class="swatch-dot" style="background:#525E7D"></span>Deuteranopia</li>
          <li><span class="swatch-dot" style="background:#007271"></span>Tritanopia</li>
        </ul>
      </div>
    </header>

    <main class="grid" id="grid"></main>

    <footer>
      Cores amostradas de fotografias de plumagens (Vinícius Kohn). Simulação CVD pelo
      modelo de Machado, Oliveira &amp; Fernandes (2009) via colorspacious; distâncias
      perceptuais (ΔE) euclidianas em CAM02-UCS. Gerado a partir do pacote
      <span class="mono">plumaria</span> por <span class="mono">examples/build_gallery_html.py</span>.
    </footer>
  </div>
</div>

<script id="palette-data" type="application/json">
__PALETTE_DATA__
</script>

<script>
  (function () {
    var DATA = JSON.parse(document.getElementById("palette-data").textContent);
    var CVD_LABELS = { protanomaly: "Protanopia", deuteranomaly: "Deuteranopia", tritanomaly: "Tritanopia" };
    var CVD_ORDER = ["protanomaly", "deuteranomaly", "tritanomaly"];

    function el(tag, cls, html) {
      var n = document.createElement(tag);
      if (cls) n.className = cls;
      if (html != null) n.innerHTML = html;
      return n;
    }
    function esc(s) { return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }
    function gradient(colors) { return "linear-gradient(90deg," + colors.join(",") + ")"; }

    function discreteBar(colors, cls) {
      var bar = el("div", cls);
      colors.forEach(function (c) { var cell = el("div", "c"); cell.style.background = c; bar.appendChild(cell); });
      return bar;
    }

    function highlight(code) {
      return code.split("\n").map(function (line) {
        var idx = line.indexOf("#");
        var codePart = idx >= 0 ? line.slice(0, idx) : line;
        var comPart = idx >= 0 ? line.slice(idx) : "";
        codePart = esc(codePart)
          .replace(/\b(import|as|from)\b/g, '<span class="tok-kw">$1</span>')
          .replace(/("[^"]*?")/g, '<span class="tok-str">$1</span>');
        if (comPart) comPart = '<span class="tok-com">' + esc(comPart) + "</span>";
        return codePart + comPart;
      }).join("\n");
    }

    function renderCard(p) {
      var card = el("section", "card");

      var head = el("div", "card-head");
      head.appendChild(el("h2", "pal-name", p.name));
      head.appendChild(el("span", "chip kind", p.kind));
      if (p.report) {
        head.appendChild(el("span", "chip verdict " + (p.report.safe ? "safe" : "warn"),
          (p.report.safe ? "✓ segura" : "⚠ risco") + " · ΔE mín " + p.report.worst[1].toFixed(1)));
      }
      card.appendChild(head);

      if (p.labels) {
        var sw = el("div", "swatch discrete");
        p.normal.forEach(function (c, i) {
          var cell = el("div", "cell");
          cell.style.background = c;
          cell.setAttribute("tabindex", "0");
          cell.setAttribute("aria-label", p.labels[i] + " " + c);
          cell.appendChild(el("span", "name", esc(p.labels[i])));
          cell.appendChild(el("span", "hex", c));
          sw.appendChild(cell);
        });
        card.appendChild(sw);
        var hr = el("div", "hex-row");
        p.normal.forEach(function (c) { hr.appendChild(el("span", null, c)); });
        card.appendChild(hr);
      } else {
        var g = el("div", "swatch gradient");
        g.style.background = gradient(p.normal);
        card.appendChild(g);
      }

      var cvd = el("div", "cvd");
      cvd.appendChild(el("p", "cvd-title", "Simulação de daltonismo"));
      CVD_ORDER.forEach(function (t) {
        var row = el("div", "cvd-row");
        row.appendChild(el("span", "rl", CVD_LABELS[t]));
        if (p.labels) {
          row.appendChild(discreteBar(p.cvd[t], "cvd-bar"));
        } else {
          var bar = el("div", "cvd-bar gradient");
          bar.style.background = gradient(p.cvd[t]);
          row.appendChild(bar);
        }
        cvd.appendChild(row);
      });
      card.appendChild(cvd);

      if (p.report) {
        var stats = el("div", "stats");
        var conds = [["normal", "normal"]].concat(CVD_ORDER.map(function (t) { return [t, CVD_LABELS[t]]; }));
        conds.forEach(function (pair) {
          var s = el("div", "stat" + (pair[0] === p.report.worst[0] ? " worst" : ""));
          s.appendChild(el("span", "k", pair[1]));
          s.appendChild(el("span", "v", p.report[pair[0]].toFixed(1)));
          stats.appendChild(s);
        });
        stats.appendChild(el("span", "note",
          "ΔE mín. par-a-par (CAM02-UCS). Limiar de confusão ≈ " + DATA.jnd.toFixed(0) +
          "; todos os casos ficam acima."));
        card.appendChild(stats);
      }

      var code = el("div", "code");
      var btn = el("button", "copy", "copiar");
      btn.type = "button";
      btn.addEventListener("click", function () {
        navigator.clipboard.writeText(p.code).then(function () {
          btn.textContent = "copiado"; btn.classList.add("done");
          setTimeout(function () { btn.textContent = "copiar"; btn.classList.remove("done"); }, 1400);
        });
      });
      code.appendChild(btn);
      code.appendChild(el("pre", null, highlight(p.code)));
      card.appendChild(code);

      return card;
    }

    var grid = document.getElementById("grid");
    DATA.palettes.forEach(function (p) { grid.appendChild(renderCard(p)); });
  })();
</script>
</body>
</html>
'''


if __name__ == "__main__":
    main()
