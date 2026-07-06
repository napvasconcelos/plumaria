# plumaria

Paletas de cores **colorblind-safe** derivadas de plumagens de aves: uma paleta
categórica de 8 cores e três colormaps contínuos (um sequencial, dois
divergentes). Núcleo enxuto (só numpy para acessar cores); matplotlib é opcional,
só para registrar colormaps e ajustar padrões de plotagem.

As cores foram amostradas de fotografias de plumagens (fonte: Vinícius Kohn,
@viniciuskohnpassaros) e ajustadas para permanecerem distinguíveis sob os três
tipos de daltonismo (deuteranopia, protanopia, tritanopia). A paleta categórica
foi selecionada maximizando a distância perceptual mínima (CIE Lab), simulando o
daltonismo pelas matrizes de Machado et al. (2009); o ΔE mínimo (~15) fica na
mesma faixa da paleta Okabe-Ito.

> Extraído de `neurotools.viz` para um pacote autônomo. `neurotools` consome o
> plumaria como submódulo git.

## Instalação

```bash
pip install -e '.[viz]'     # com matplotlib (colormaps + set_defaults)
pip install -e .            # só o acesso às cores (numpy)
```

## Uso

```python
import plumaria

plumaria.categorical(3)      # ['#0A458A', '#F76F24', '#126C7D']
plumaria.register()          # registra os colormaps "aves_*" no matplotlib
plumaria.set_defaults()      # ciclo de cores categórico + cmap padrão

import matplotlib.pyplot as plt
plt.get_cmap("aves_saiazul")           # sequencial
plt.get_cmap("aves_gaturamo")          # divergente
```

`plumaria.palettes` também está disponível (`from plumaria import palettes`).

## Colormaps

| Nome | Tipo |
|---|---|
| `aves_saiazul` | sequencial (mono-matiz) |
| `aves_gaturamo` | divergente |
| `aves_beijaflor` | divergente |

Cada colormap tem a variante invertida `_r` (ex.: `aves_saiazul_r`).

## API

`categorical`, `colormap`, `register`, `set_defaults`, `hex_to_rgb` e os dados
`CATEGORICAL`, `CATEGORICAL_NAMES`, `SEQUENTIAL`, `DIVERGING`, `COLORMAPS`.

## Testes

```bash
pytest
```

## Licença

MIT.
