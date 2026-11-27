# Como o contato entre os grãos cria o atrito do solo — simulação DEM

Simulação de Elementos Discretos (DEM) 2D que roda no navegador. Cada disco é um grão; em cada contato há uma mola normal, um atrito de Coulomb |Ft| ≤ μ·Fn e uma resistência ao rolamento |M| ≤ μr·R·Fn. O ângulo de atrito do solo (φ) **não é dado de entrada**: ele surge do ensaio.

## O que a página faz

- **Ensaio de cisalhamento**: camada de grãos entre um fundo rugoso e uma placa com tensão normal σ constante; a placa anda e mede-se τ/σ → tan φ.
- **Coluna que desmorona**: grãos atrás de uma comporta, sob gravidade; ao abrir, a coluna forma um talude.
- Controles para μ (atrito entre grãos), μr (resistência ao rolamento), σ, velocidade do ensaio e da animação.
- Cadeias de força, cor por velocidade, faixas ou rotação.
- Gráficos ao vivo (τ/σ × deformação e φ × μ) e diário de ensaios.

## Estrutura

```
index.html                          a simulação (HTML + CSS + JavaScript, sem dependências)
python/DEM_atrito_entre_graos.ipynb caderno do Google Colab que ensina o método passo a passo
python/dem2d.py                     o mesmo simulador em Python (NumPy + SciPy)
```

## Publicar no GitHub Pages

1. Crie um repositório (por exemplo, `simulacao-dem`).
2. Envie os arquivos desta pasta (**Add file → Upload files**).
3. **Settings → Pages → Deploy from a branch**, branch `main`, pasta `/ (root)` → **Save**.
4. O site fica em `https://SEU-USUARIO.github.io/simulacao-dem/`.

Para abrir no computador sem publicar, basta dar duplo clique no `index.html` (esta página não carrega arquivos externos).

## Modelo

- Discos com diâmetro entre 0,8 e 1,2; densidade 1; unidades adimensionais.
- Contato: mola normal linear kn = 2000 com amortecimento (restituição 0,3); mola tangencial kt = kn/2 limitada por μ·Fn; mola de rolamento limitada por μr·Ref·Fn, com memória por contato.
- Integração de Euler semi-implícita, Δt = 0,1·√(m/kn).
- Cisalhamento: caixa periódica na horizontal, sem gravidade, número inercial I = γ̇·d/√(σ/ρ).
- φ = arctan(média de τ/σ para γ > 0,5).

## Limites

Modelo 2D com ~430 grãos: serve para entender o mecanismo, não para projeto. Cada ensaio oscila uns ±2°. Para pesquisa, use YADE, LIGGGHTS ou PFC em 3D, calibrando os parâmetros com ensaios de laboratório.

## Referências

- Cundall, P. A. & Strack, O. D. L. (1979). A discrete numerical model for granular assemblies. *Géotechnique* 29(1).
- O'Sullivan, C. (2011). *Particulate Discrete Element Modelling: A Geomechanics Perspective.* CRC Press.
- GDR MiDi (2004). On dense granular flows. *European Physical Journal E* 14.
- Ai, J. et al. (2011). Assessment of rolling resistance models in discrete element simulations. *Powder Technology* 206.
