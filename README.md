# Superfícies e interfaces vistas grão a grão — simulação DEM

Simulação de Elementos Discretos (DEM) 2D que roda no navegador. Cada disco é um grão; em cada contato há uma mola normal, um atrito de Coulomb |Ft| ≤ μ·Fn e uma resistência ao rolamento |M| ≤ μr·R·Fn. No modo Interface, os grãos também são unidos por ligações adesivas que acumulam dano.

## Os cinco ensaios

| Ensaio | O que mostra | Ligação com o livro *Superfícies e interfaces de materiais na Engenharia Civil* |
|---|---|---|
| **Seus ensaios (ANPET 2026)** | As 18 curvas τ × deslocamento horizontal do artigo "Desenvolvimento de um ensaio para análise da aderência de interface entre camadas" (Solo 1 A-4 e Solo 2 A-2-4; interfaces I1 solo-solo, I2 com ETS e I3 com EAI; σ = 50, 100 e 200 kPa), as envoltórias de ruptura e, ao lado, a simulação DEM calibrada para cada interface. | Capítulo 4 (aderência entre camadas) e Lei de Goodman |
| **Interface** | Duas placas (lisas ou ásperas) unidas por um filme de espessura ajustável, cisalhadas sob tensão normal σ (como no ensaio de Leutner) ou tracionadas (arrancamento). Gera a curva τ × Δx com as zonas I, II e III, e mede kₜ, τ máx e τ residual. | Seção 1.3 (Lei de Goodman, Fig. 1.18) e Capítulo 4 (interface entre camadas); adesão × coesão e efeito da água (Cap. 1.2 e 2) |
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
- **Espessura do filme**: de 1 a 6 camadas de grãos entre as placas. Com rugosidade 0 e 1–2 camadas, o ensaio representa **duas placas com um filme fino de adesivo** (junta adesiva).
- **Tipo de carga**:
  - *Cisalhamento (Leutner)*: a placa de cima aplica σ constante e anda para o lado com velocidade 0,05 até Δx = 3 diâmetros.
  - *Tração (arrancamento)*: o filme se acomoda sob σ = 10, é descarregado para 0,2 e então a placa de cima é puxada para cima com velocidade 0,02 até Δy = 2 diâmetros. A tensão medida é a força vertical por largura. Não há Zona III de atrito: depois que as ligações rompem, a tensão vai a zero.
- **kₜ** (ou **kₙ** na tração): inclinação inicial da curva, até 2,7% do deslocamento final. **τ máx**: pico da curva suavizada. **τ residual**: média do último quarto do deslocamento. **Zona II**: do pico até τ chegar a 15% do excesso acima do residual.
- **Ruptura adesiva**: fração das ligações rompidas que eram de adesão (face) e não de coesão.
- Cisalhamento com σ diferentes: o gráfico da direita ajusta as envoltórias de pico e residual, τ = c + σ·tan φ. Tração com espessuras diferentes: o gráfico mostra σ máx × número de camadas.

### Modo Seus ensaios (ANPET 2026) — calibração

- Dados: planilha `ANPET_25-06-26.xlsx`, embutidos na página (deslocamento horizontal em mm, τ em kPa e, no Solo 1, deslocamento vertical).
- Envoltória do ensaio: reta pelos τ máximos das 3 tensões (reproduz c e φ do artigo).
- Escalas do modelo: σ_modelo = σ/10 kPa; τ (kPa) = 10·τ_modelo; 1 diâmetro de grão = 3 mm.
- Resistência simulada: média do patamar entre 4,5 e 9 mm equivalentes (nos ensaios, o τ máximo ocorre nesse patamar).
- Parâmetros encontrados por busca em grade, com média de 3 arranjos de grãos por tensão:

| Interface | μ | μr | rugosidade | ligações | Simulação (c, φ) | Ensaio Solo 1 (c, φ) | Ensaio Solo 2 (c, φ) |
|---|---|---|---|---|---|---|---|
| I1 solo-solo | 0,6 | 0,2 | 1,0 | nenhuma | 16 kPa, 40,4° | 16 kPa, 41,8° | 19 kPa, 41,6° |
| I2 ETS (filme lubrificante) | 0,3 | 0,2 | 1,5 | nenhuma | 2 kPa, 28,6° | −16 (≈0) kPa, 34,4° | 1 kPa, 28,0° |
| I3 EAI, Solo 1 | 0,6 | 0,2 | 1,0 | F = 5, dúcteis (ruptura com 150× o deslocamento do pico) | 37 kPa, 31,7° | 43 kPa, 34,5° | — |
| I3 EAI, Solo 2 | igual ao I1 | | | | 16 kPa, 40,4° | — | 21 kPa, 42,2° |

- Limites: reproduz a envoltória, não a curva inteira (a simulação sobe mais rápido); cada ensaio simulado oscila cerca de ±15 kPa; a dilatância medida (deslocamento vertical) ainda não é comparada.

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
