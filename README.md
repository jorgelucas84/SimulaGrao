# Climas de Köppen-Geiger — o Brasil comparado com o mundo

Mapa interativo dos 30 climas de Köppen-Geiger (1991–2020), com:

- seletor de clima (mostra só o clima escolhido, na cor original);
- modo **★ Semelhantes ao Brasil** (só os climas que existem no Brasil);
- vista **Semelhança com o Brasil** (cada país colorido pela sua nota);
- zoom em qualquer país (roda do mouse, + / −, arrastar, duplo clique ou lista de países);
- tabela com os países que têm o clima escolhido (% do território, km² e % do total mundial);
- botão **Analisar somente o Brasil (estados)**: mapa do Brasil com as divisas dos 27 estados e, na parte de baixo, a % de cada clima estado por estado (por região, de A a Z ou pelo clima selecionado);
- **Comparar dois climas**: escolha dois dos 30 climas e veja um texto com as diferenças (grupo, chuva, temperatura, paisagem), um quadro lado a lado, os países que têm os dois e um botão para mostrar só os dois no mapa;
- seção com os critérios de cada clima do Brasil (variáveis, limites e equações de Köppen-Geiger);
- caixinhas para escolher as regiões (Brasil, América do Sul, América do Norte e Central, Europa, África, Ásia, Oceania, Antártida), em qualquer combinação; o link guarda a escolha (por exemplo `#brasil+europa`).

## Simulação DEM (simulacao.html)

Página separada, ligada pelo topo do mapa: um simulador de Elementos Discretos 2D em JavaScript que roda no navegador.
Mostra como o atrito entre grãos (μ) e a resistência ao rolamento (μ_r) geram o ângulo de atrito do solo (φ)
num ensaio de cisalhamento virtual e numa coluna que desmorona, com cadeias de força, gráfico τ/σ ao vivo e diário de ensaios.
A pasta `dem/` traz o caderno do Google Colab (`DEM_atrito_entre_graos.ipynb`) e o simulador em Python (`dem2d.py`).

## Estrutura

```
index.html              mapa dos climas (HTML + CSS + JavaScript, sem dependências)
simulacao.html          simulação DEM do atrito entre grãos
dem/                    caderno do Colab e simulador em Python
data.json               dados do mapa (gerados pelo script)
planilhas/              planilhas Excel com os resultados completos
scripts/gerar_dados.py  gera o data.json a partir do TIF
```

## Publicar no GitHub Pages

1. Crie um repositório no GitHub (por exemplo, `climas-koppen`).
2. Envie os arquivos desta pasta (botão **Add file → Upload files**, ou `git push`).
3. Vá em **Settings → Pages**, escolha **Deploy from a branch**, branch `main`, pasta `/ (root)` e clique em **Save**.
4. Em um ou dois minutos o site fica em `https://SEU-USUARIO.github.io/climas-koppen/`.

## Ver no seu computador

O `index.html` carrega o `data.json` com `fetch`, então ele não abre com duplo clique: precisa de um servidor local.

```
python -m http.server 8000
```

Depois abra `http://localhost:8000`.

## Gerar os dados de novo

1. Crie a pasta `entrada/` e coloque nela:
   - `koppen_geiger_climatezones_1991_2020_1km.tif` — Beck et al. (2023), https://www.gloh2o.org/koppen/
   - `ne_10m_admin_0_countries.shp` e os arquivos `.dbf`, `.shx` e `.prj` — Natural Earth 10m, https://www.naturalearthdata.com/
   - `ne_10m_admin_1_states_provinces.shp` e os arquivos `.dbf`, `.shx` e `.prj` — Natural Earth 10m (estados)
2. Instale as bibliotecas e rode o script:

```
pip install numpy pandas rasterio pyshp pillow scipy
python scripts/gerar_dados.py
```

A pasta `entrada/` está no `.gitignore`, porque os arquivos são grandes.

## Método

- **Áreas:** Áreas calculadas a partir do mapa Köppen-Geiger 1991–2020 de 1 km (Beck et al., 2023), somando a área real de cada pixel dentro das fronteiras do Natural Earth 10m. Representam a área de terra com clima classificado e não incluem grandes lagos.
- **Estados:** divisas do Natural Earth 10m (admin 1); a soma dos 27 estados é igual à área do Brasil.

- **Área:** cada pixel do TIF (1/120°) entra com a sua área real na esfera, `R² · Δλ · (sen φ₁ − sen φ₂)` com R = 6371 km. Contar pixels sem esse ajuste exagera os climas perto dos polos.
- **% do território:** área de cada clima dividida pela área total do país.
- **Semelhança com o Brasil:** `100 − ½ · Σ |%país − %Brasil|` sobre os 30 climas, que é o mesmo que somar a parcela em comum de cada clima. 100 = distribuição idêntica, 0 = nenhum clima em comum.
- **Mapa:** reduzido a 0,1° (blocos de 12 × 12 pixels, clima predominante) para carregar rápido. As porcentagens e áreas são calculadas na resolução original de 1 km.

- **Continentes:** campo `CONTINENT` do Natural Earth, com uma exceção: a Rússia é dividida nos Montes Urais (aprox. 60° E) em "parte europeia" (Europa) e "parte asiática" (Ásia). Turquia, Cazaquistão, Cáucaso e Chipre ficam na Ásia; o Egito na África. A França inclui a Guiana Francesa.

## Fontes

- Beck, H. E. et al. (2023). *High-resolution (1 km) Köppen-Geiger maps for 1901–2099 based on constrained CMIP6 projections.* Scientific Data 10, 724.
- Natural Earth — Admin 0 Countries, 1:10m (domínio público).
