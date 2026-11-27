# Superfícies e interfaces vistas grão a grão — simulação DEM

Simulação de Elementos Discretos (DEM) 2D que roda no navegador. Cada disco é um grão; em cada contato há uma mola normal, um atrito de Coulomb |Ft| ≤ μ·Fn e uma resistência ao rolamento |M| ≤ μr·R·Fn. No modo Interface, os grãos também são unidos por ligações adesivas que acumulam dano.

## Os quatro ensaios

| Ensaio | O que mostra | Ligação com o livro *Superfícies e interfaces de materiais na Engenharia Civil* |
|---|---|---|
| **Interface** | Duas camadas com faces ásperas unidas por um filme de ligante, cisalhadas sob tensão normal σ (como no ensaio de Leutner). Gera a curva τ × Δx com as zonas I, II e III, e mede kₜ, τ máx e τ residual. | Seção 1.3 (Lei de Goodman, Fig. 1.18) e Capítulo 4 (interface entre camadas); adesão × coesão e efeito da água (Cap. 1.2 e 2) |
| **Efeito parede** | Grãos se acomodando sobre a superfície plana de um agregado e o perfil de porosidade em função da distância. | Capítulo 3 (ZTI, efeito parede, adições finas como a sílica ativa) |
| **Cisalhamento** | Ângulo de atrito do conjunto (φ) gerado pelo atrito entre grãos (μ) e pela resistência ao rolamento. | Atrito e intertravamento em materiais granulares |
| **Coluna** | Talude formado por uma coluna de grãos que desmorona. | Idem |

### Modo Interface — modelo

- Antes do cisalhamento, todo par de grãos que se toca (folga de até 8%) recebe uma **ligação**:
  - entre o filme e as faces das camadas: **adesão** (resistência = "Adesão ligante–agregado");
  - dentro do filme: **coesão** (resistência = "Coesão dentro do ligante").
- Cada ligação tem rigidez normal 600 e tangencial 300 e segue uma **lei bilinear de dano** (zona coesiva em miniatura): elástica até a resistência F, depois perde força linearmente até romper com 12 vezes o deslocamento do pico. O dano só reduz a força de tração e de cisalhamento.
- **Água**: multiplica a adesão por (1 − 0,85·w) e a coesão por (1 − 0,25·w), onde w é a fração de água (0 a 1).
- **Rugosidade**: altura das asperezas aleatórias das faces, em diâmetros de grão.
- A placa de cima aplica σ constante e anda com velocidade 0,05 até Δx = 3 diâmetros.
- **kₜ**: inclinação de τ × Δx até Δx = 0,08. **τ máx**: pico da curva suavizada. **τ residual**: média de Δx = 2,25 a 3. **Zona II**: do pico até τ chegar a 15% do excesso acima do residual.
- **Ruptura adesiva**: fração das ligações rompidas que eram de adesão (face) e não de coesão.
- Rodando ensaios com σ diferentes, o gráfico da direita ajusta as envoltórias de pico e residual: τ = c + σ·tan φ.

### Modo Efeito parede — modelo

- Grãos com diâmetro médio 1 e faixa d_máx/d_mín ajustável caem sob gravidade sobre uma superfície plana e lisa.
- "Finos": fração da área de sólidos em grãos de diâmetro 0,35 (como uma adição fina tipo sílica ativa).
- Porosidade de cada faixa horizontal de 0,05 = 1 − (soma das cordas dos discos que cortam a linha) / largura.
- "Junto ao agregado" = média de 0 a 1 diâmetro; "interior" = média de 3 diâmetros até 1,5 abaixo da superfície livre.
- "Espessura da zona" = distância a partir da qual a média móvel de 1 diâmetro fica a menos de 10% do excesso de porosidade da parede.

## Estrutura

```
index.html                          a simulação (HTML + CSS + JavaScript, sem dependências)
python/DEM_atrito_entre_graos.ipynb caderno do Google Colab que ensina o método passo a passo
python/dem2d.py                     simulador em Python (NumPy + SciPy) do ensaio de cisalhamento
```

## Publicar no GitHub Pages

1. Crie um repositório (por exemplo, `simulacao-dem`).
2. Envie os arquivos desta pasta (**Add file → Upload files**).
3. **Settings → Pages → Deploy from a branch**, branch `main`, pasta `/ (root)` → **Save**.
4. O site fica em `https://SEU-USUARIO.github.io/simulacao-dem/`.

Para abrir no computador sem publicar, basta dar duplo clique no `index.html`.

## Contato entre grãos (todos os modos)

- Discos, densidade 1, unidades adimensionais (diâmetro médio ≈ 1).
- Mola normal linear kn = 2000 com amortecimento (restituição 0,3); mola tangencial kt = kn/2 limitada por μ·Fn; mola de rolamento limitada por μr·Ref·Fn, com memória por contato.
- Integração de Euler semi-implícita, Δt = 0,1·√(m/kn).

## Limites

Modelos 2D com algumas centenas de grãos e unidades adimensionais: servem para entender mecanismos e tendências, não para obter valores de projeto. Cada ensaio oscila alguns por cento conforme o arranjo inicial. Para pesquisa: YADE, LIGGGHTS ou PFC em 3D (DEM), elementos coesivos em programas de elementos finitos (CZM) e dinâmica molecular para a adesão em escala molecular, sempre calibrando com ensaios de laboratório.

## Referências

- Cundall, P. A. & Strack, O. D. L. (1979). A discrete numerical model for granular assemblies. *Géotechnique* 29(1).
- Goodman, R. E.; Taylor, R. L.; Brekke, T. L. (1968). A model for the mechanics of jointed rock. *Journal of the Soil Mechanics and Foundations Division* 94.
- Garboczi, E. J. & Bentz, D. P. (1991). Digital simulation of the aggregate–cement paste interfacial zone in concrete. *Journal of Materials Research* 6.
- O'Sullivan, C. (2011). *Particulate Discrete Element Modelling: A Geomechanics Perspective.* CRC Press.
- Ai, J. et al. (2011). Assessment of rolling resistance models in discrete element simulations. *Powder Technology* 206.
