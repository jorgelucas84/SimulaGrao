"""
Gera o data.json usado pelo mapa (index.html) a partir do TIF de Köppen-Geiger.

Entradas (baixe e coloque na pasta "entrada/"):
  - koppen_geiger_climatezones_1991_2020_1km.tif   (Beck et al. 2023, https://www.gloh2o.org/koppen/)
  - ne_10m_admin_0_countries.shp (+ .dbf .shx .prj) (Natural Earth 10m, https://www.naturalearthdata.com/)
  - ne_10m_admin_1_states_provinces.shp (+ .dbf .shx .prj) (Natural Earth 10m, estados)

Instalação:
  pip install numpy pandas rasterio pyshp pillow scipy

Uso:
  python scripts/gerar_dados.py
Saída:
  data.json (na raiz do projeto)
"""
import base64, io, json, os
import numpy as np
import rasterio, shapefile
from rasterio.features import rasterize
from rasterio.transform import from_origin
from rasterio.windows import Window, from_bounds
from PIL import Image

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TIF = os.path.join(RAIZ, "entrada", "koppen_geiger_climatezones_1991_2020_1km.tif")
SHP = os.path.join(RAIZ, "entrada", "ne_10m_admin_0_countries.shp")
SHP_ESTADOS = os.path.join(RAIZ, "entrada", "ne_10m_admin_1_states_provinces.shp")   # divisas dos estados
SAIDA = os.path.join(RAIZ, "data.json")

# Cores oficiais da legenda do TIF (classes 1 a 30)
CORES = [[0,0,255],[0,120,255],[70,170,250],[255,0,0],[255,150,150],[245,165,0],[255,220,100],
         [255,255,0],[200,200,0],[150,150,0],[150,255,150],[100,200,100],[50,150,50],[200,255,80],
         [100,255,80],[50,200,0],[255,0,255],[200,0,200],[150,50,150],[150,100,150],[170,175,255],
         [90,120,220],[75,80,180],[50,0,135],[0,255,255],[55,200,255],[0,125,125],[0,70,95],
         [178,178,178],[102,102,102]]
# Continente de cada país (abas do site). Países entre dois continentes aparecem nos dois.
CONTINENTES = {"Asia": "asia", "Africa": "africa", "Europe": "europa", "North America": "america-do-norte",
               "Oceania": "oceania", "South America": "america-do-sul", "Antarctica": "antartida"}
ILHAS = {"ATF": "antartida", "SYC": "africa", "HMD": "oceania", "SHN": "africa", "MUS": "africa",
         "IOT": "asia", "MDV": "asia", "SGS": "america-do-sul", "CLP": "america-do-norte"}   # "Seven seas" no Natural Earth
# A Rússia é dividida nos Montes Urais (aprox. 60° E): a oeste = Europa, a leste (e além de 180°) = Ásia.
URAIS_LON = 60.0
R_TERRA = 6371.0088   # raio médio da Terra (km)
FATOR = 12            # 12 x 12 pixels de 1/120° = células de 0,1° no mapa


def main():
    src = rasterio.open(TIF)
    T, W, H, res = src.transform, src.width, src.height, src.transform.a

    r = shapefile.Reader(SHP, encoding="utf-8")
    campos = [f[0] for f in r.fields[1:]]
    regs = [dict(zip(campos, x)) for x in r.records()]
    formas = [(s.__geo_interface__, i + 1) for i, s in enumerate(r.shapes())]
    i_rus = next(i + 1 for i, g in enumerate(regs) if g["ADM0_A3"] == "RUS")
    i_rus_asia = len(regs) + 1          # id extra para a parte asiática da Rússia
    N = len(regs) + 2

    def dividir_russia(pais, transf, largura):
        lon = transf.c + (np.arange(largura) + 0.5) * transf.a
        leste = (lon >= URAIS_LON) | (lon < -150)
        pais[(pais == i_rus) & leste[None, :]] = i_rus_asia
        return pais

    # 1) Área exata (km²) de cada clima em cada país, na resolução original de 1 km
    area = np.zeros((N, 31))
    dl = np.deg2rad(res)
    for y0 in range(0, H, 1080):
        h = min(1080, H - y0)
        jan = Window(0, y0, W, h)
        kg = src.read(1, window=jan)
        pais = rasterize(formas, out_shape=(h, W), transform=src.window_transform(jan), fill=0, dtype="int16")
        pais = dividir_russia(pais, src.window_transform(jan), W)
        topo = T.f + (y0 + np.arange(h)) * T.e
        a_px = R_TERRA**2 * dl * (np.sin(np.deg2rad(topo)) - np.sin(np.deg2rad(topo + T.e)))  # km² por pixel
        m = (kg >= 1) & (kg <= 30)
        np.add.at(area, (pais[m], kg[m]), np.broadcast_to(a_px[:, None], (h, W))[m])
        print(f"linhas {y0}–{y0 + h} de {H}")

    # 2) Mapa reduzido a 0,1°: clima predominante em cada bloco de 12 x 12 pixels
    w2, h2 = W // FATOR, H // FATOR
    classe = np.zeros((h2, w2), np.uint8)
    for y in range(0, h2, 90):
        hh = min(90, h2 - y)
        a = src.read(1, window=Window(0, y * FATOR, W, hh * FATOR))
        a = a.reshape(hh, FATOR, w2, FATOR).transpose(0, 2, 1, 3).reshape(hh, w2, FATOR * FATOR)
        cont = np.stack([(a == k).sum(-1) for k in range(31)], -1)
        terra = cont[..., 1:].sum(-1)
        classe[y:y + hh] = np.where(terra * 2 >= FATOR * FATOR, cont[..., 1:].argmax(-1) + 1, 0)
    t2 = from_origin(-180, 90, 360 / w2, 180 / h2)
    id_pais = rasterize(formas, out_shape=(h2, w2), transform=t2, fill=0, dtype="uint16")
    id_pais = dividir_russia(id_pais, t2, w2)

    def png(arr, modo):
        b = io.BytesIO()
        Image.fromarray(arr, modo).save(b, "PNG", optimize=True)
        return base64.b64encode(b.getvalue()).decode()

    # 2b) Estados do Brasil: área por clima (1 km) e id do estado no mapa de 0,1°
    re_ = shapefile.Reader(SHP_ESTADOS, encoding="utf-8")
    ce = [f[0] for f in re_.fields[1:]]
    est = sorted([(dict(zip(ce, r_)), s_) for r_, s_ in zip(re_.records(), re_.shapes())
                  if dict(zip(ce, r_))["adm0_a3"] == "BRA"], key=lambda t_: t_[0]["name"])
    formas_e = [(s_.__geo_interface__, i + 1) for i, (_, s_) in enumerate(est)]
    jan = from_bounds(-75, -35, -28, 6, T).round_offsets().round_lengths()
    kg = src.read(1, window=jan); te = src.window_transform(jan)
    ide = rasterize(formas_e, out_shape=kg.shape, transform=te, fill=0, dtype="uint8")
    topo = te.f + np.arange(kg.shape[0]) * te.e
    a_px = R_TERRA**2 * dl * (np.sin(np.deg2rad(topo)) - np.sin(np.deg2rad(topo + te.e)))
    area_e = np.zeros((len(est) + 1, 31)); m = (kg >= 1) & (kg <= 30)
    np.add.at(area_e, (ide[m], kg[m]), np.broadcast_to(a_px[:, None], kg.shape)[m])
    estados = [{"n": d_["name"], "uf": d_["postal"],
                "a": [round(float(x), 1) for x in area_e[i + 1, 1:]],
                "p": [round(float(x), 2) for x in 100 * area_e[i + 1, 1:] / area_e[i + 1, 1:].sum()]}
               for i, (d_, _) in enumerate(est)]
    id_est = rasterize(formas_e, out_shape=(h2, w2), transform=t2, fill=0, dtype="uint8")
    i_bra = next(i + 1 for i, g in enumerate(regs) if g["ADM0_A3"] == "BRA")
    id_est[id_pais != i_bra] = 0
    falta = (id_pais == i_bra) & (id_est == 0)            # litoral: usa o estado mais próximo
    if falta.any():
        from scipy import ndimage
        iy, ix = ndimage.distance_transform_edt(id_est == 0, return_distances=False, return_indices=True)
        id_est[falta] = id_est[iy[falta], ix[falta]]

    rgb = np.zeros((h2, w2, 3), np.uint8)
    rgb[..., 0], rgb[..., 1] = id_pais >> 8, id_pais & 255   # id do país codificado em R e G
    rgb[..., 2] = id_est                                     # id do estado (Brasil) em B

    # 3) Semelhança com o Brasil = 100 − ½·Σ|%país − %Brasil| sobre os 30 climas
    pct = {i: 100 * area[i, 1:] / area[i, 1:].sum() for i in range(1, N) if area[i, 1:].sum() > 0}
    bra = next(i for i in pct if regs[i - 1]["ADM0_A3"] == "BRA")
    paises = {}
    for i, p in pct.items():
        g = regs[i_rus - 1] if i == i_rus_asia else regs[i - 1]
        nome = g.get("NAME_PT") or g["NAME"]
        if i == i_rus: nome += " (parte europeia)"
        if i == i_rus_asia: nome += " (parte asiática)"
        paises[i] = {
            "n": nome,
            "iso": g["ADM0_A3"],
            "s": round(float(100 - 0.5 * np.abs(p - pct[bra]).sum()), 1),
            "p": [round(float(x), 2) for x in p],
            "a": [round(float(x), 1) for x in area[i, 1:]],
            "c": ["asia"] if i == i_rus_asia else [ILHAS.get(g["ADM0_A3"]) or CONTINENTES[g["CONTINENT"]]],
        }

    json.dump({"W": w2, "H": h2, "cls": png(classe, "L"), "cid": png(rgb, "RGB"), "countries": paises,
               "colors": CORES, "states": estados, "world": [round(float(x), 1) for x in area[:, 1:].sum(0)]},
              open(SAIDA, "w"), ensure_ascii=False)
    print("Pronto:", SAIDA, f"({len(paises)} países)")


if __name__ == "__main__":
    main()
