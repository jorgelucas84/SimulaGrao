"""
dem2d.py — simulador de Elementos Discretos (DEM) 2D, didático, em Python + NumPy + SciPy.

Grãos = discos. Em cada contato entre dois grãos:
  * força normal ......... mola linear (kn) + amortecedor  -> os grãos se empurram
  * força tangencial ..... mola (kt) limitada por Coulomb   -> ATRITO ENTRE GRÃOS:  |Ft| <= mu * Fn
  * momento de rolamento . mola limitada                    -> imita grãos angulosos: |M| <= mu_r * R * Fn

Unidades adimensionais: diâmetro médio ~ 1, densidade = 1.
Recursos: gravidade, chão e paredes laterais opcionais, caixa periódica em x,
grãos fixos (fundo rugoso) e uma "placa" de grãos que se move junta (ensaio de cisalhamento).
"""
import numpy as np
from scipy.spatial import cKDTree


class DEM2D:
    def __init__(self, raios, x, y, mu=0.5, mu_r=0.0, kn=2.0e3, kt_kn=0.5, restituicao=0.3,
                 g=1.0, chao=True, parede_esq=None, parede_dir=None, periodo_x=None,
                 fixo=None, placa=None):
        self.N = len(raios)
        self.r = np.asarray(raios, float)
        self.m = np.pi * self.r**2                      # massa (densidade 1)
        self.I = 0.5 * self.m * self.r**2               # momento de inércia do disco
        self.pos = np.column_stack([x, y]).astype(float)
        self.vel = np.zeros((self.N, 2))
        self.w = np.zeros(self.N)                       # rotação
        self.mu, self.mu_r = mu, mu_r
        self.kn, self.kt = kn, kt_kn * kn
        self.g, self.chao = g, chao
        self.parede_esq, self.parede_dir = parede_esq, parede_dir   # posição x ou None
        self.Lx = periodo_x                             # caixa periódica em x (None = não)
        self.fixo = np.zeros(self.N, bool) if fixo is None else np.asarray(fixo, bool)
        self.placa = np.zeros(self.N, bool) if placa is None else np.asarray(placa, bool)
        e = restituicao
        self.zeta = -np.log(e) / np.sqrt(np.pi**2 + np.log(e)**2)   # amortecimento a partir de e
        livres = ~(self.fixo | self.placa)
        self.dt = 0.1 * np.sqrt(self.m[livres].min() / kn)        # passo de tempo estável
        self.t = 0.0
        # memória das molas de cada contato (chave do par -> deslocamento acumulado)
        self.chaves = np.zeros(0, np.int64)
        self.xi = np.zeros(0)
        self.th = np.zeros(0)
        # placa (ensaio de cisalhamento): velocidade horizontal imposta e pressão vertical
        self.V_placa, self.P_placa, self.vy_placa = 0.0, 0.0, 0.0
        self.F_placa = np.zeros(2)                      # força dos grãos sobre a placa

    # ------------------------------------------------------------------ 1) contatos
    def contatos(self):
        N, p, r = self.N, self.pos, self.r
        if self.Lx is None:
            arvore = cKDTree(p)
        else:
            q = p.copy(); q[:, 0] %= self.Lx
            q[:, 1] -= p[:, 1].min() - 1
            arvore = cKDTree(q, boxsize=[self.Lx, 10 * (q[:, 1].max() + 10)])
        pares = arvore.query_pairs(2 * r.max(), output_type="ndarray")
        i, j = pares[:, 0], pares[:, 1]
        d = p[j] - p[i]
        if self.Lx is not None:                         # imagem mais próxima (caixa periódica)
            d[:, 0] -= self.Lx * np.round(d[:, 0] / self.Lx)
        dist = np.hypot(d[:, 0], d[:, 1])
        ov = r[i] + r[j] - dist                         # sobreposição
        rigido = self.fixo | self.placa
        ok = (ov > 0) & ~(rigido[i] & rigido[j])
        i, j, d, dist, ov = i[ok], j[ok], d[ok], dist[ok], ov[ok]
        n = d / dist[:, None]                           # normal unitária de i para j
        listas = [(i, j, n, ov, r[j])]
        # paredes = "grãos" de índice N (chão), N+1 (esquerda), N+2 (direita)
        paredes = []
        if self.chao:
            paredes.append((N, p[:, 1] < r, (0.0, -1.0), r - p[:, 1]))
        if self.parede_esq is not None:
            paredes.append((N + 1, p[:, 0] < self.parede_esq + r, (-1.0, 0.0), r - (p[:, 0] - self.parede_esq)))
        if self.parede_dir is not None:
            paredes.append((N + 2, p[:, 0] > self.parede_dir - r, (1.0, 0.0), r - (self.parede_dir - p[:, 0])))
        for idw, sel, nn, ovw in paredes:
            k = np.nonzero(sel & ~rigido)[0]
            listas.append((k, np.full(len(k), idw), np.tile(nn, (len(k), 1)), ovw[k], np.zeros(len(k))))
        return [np.concatenate(a) for a in zip(*listas)]

    # ------------------------------------------------------------------ 2) forças + 3) movimento
    def passo(self):
        N, dt = self.N, self.dt
        I, J, n, ov, rJ = self.contatos()
        t = np.column_stack([-n[:, 1], n[:, 0]])        # direção tangencial
        parede = J >= N
        Jp = np.where(parede, 0, J)
        vJ = np.where(parede[:, None], 0.0, self.vel[Jp])
        wJ = np.where(parede, 0.0, self.w[Jp])
        mJ = np.where(parede, np.inf, self.m[Jp])
        m_ef = 1.0 / (1.0 / self.m[I] + 1.0 / mJ)
        rI = self.r[I]

        dv = self.vel[I] - vJ
        vn = np.einsum("ij,ij->i", dv, n)                # > 0: grãos se aproximando
        vt = np.einsum("ij,ij->i", dv, t) + self.w[I] * rI + wJ * rJ   # deslizamento no ponto de contato

        # (a) NORMAL: mola + amortecedor; nunca puxa (Fn >= 0)
        Fn = np.maximum(self.kn * ov + 2 * self.zeta * np.sqrt(m_ef * self.kn) * vn, 0.0)

        # recuperar a memória das molas dos contatos que já existiam
        chave = I.astype(np.int64) * (N + 3) + J
        xi = np.zeros(len(I)); th = np.zeros(len(I))
        if len(self.chaves):
            k = np.minimum(np.searchsorted(self.chaves, chave), len(self.chaves) - 1)
            achou = self.chaves[k] == chave
            xi[achou] = self.xi[k[achou]]; th[achou] = self.th[k[achou]]

        # (b) TANGENCIAL: mola limitada pelo atrito de Coulomb |Ft| <= mu*Fn
        xi = xi + vt * dt
        Ft = -self.kt * xi
        limite = self.mu * Fn
        desliza = np.abs(Ft) > limite
        Ft[desliza] = np.sign(Ft[desliza]) * limite[desliza]
        xi[desliza] = -Ft[desliza] / self.kt             # o contato escorrega

        # (c) ROLAMENTO: momento limitado |M| <= mu_r*R*Fn
        R_ef = np.where(parede, rI, rI * rJ / np.maximum(rI + rJ, 1e-12))
        kr = self.kt * R_ef**2
        th = th + (self.w[I] - wJ) * dt
        M = -kr * th
        limr = self.mu_r * R_ef * Fn
        rola = np.abs(M) > limr
        M[rola] = np.sign(M[rola]) * limr[rola]
        th[rola] = -M[rola] / np.maximum(kr[rola], 1e-12)

        o = np.argsort(chave)
        self.chaves, self.xi, self.th = chave[o], xi[o], th[o]

        # somar forças e momentos (ação e reação)
        F = -Fn[:, None] * n + Ft[:, None] * t
        Ftot = np.zeros((N, 2)); Ttot = np.zeros(N)
        np.add.at(Ftot, I, F); np.add.at(Ttot, I, rI * Ft + M)
        g = ~parede
        np.add.at(Ftot, J[g], -F[g]); np.add.at(Ttot, J[g], rJ[g] * Ft[g] - M[g])
        Ftot[:, 1] -= self.m * self.g                    # gravidade

        # integrar (Euler semi-implícito)
        self.vel += Ftot / self.m[:, None] * dt
        self.w += Ttot / self.I * dt
        self.vel[self.fixo] = 0.0; self.w[self.fixo] = 0.0
        if self.placa.any():                             # a placa anda como um corpo rígido
            self.F_placa = Ftot[self.placa].sum(0)
            Mp = self.m[self.placa].sum()
            amort = 2 * np.sqrt(Mp * self.kn * self.placa.sum())   # evita oscilação da placa
            self.vy_placa += (self.F_placa[1] - self.P_placa - amort * self.vy_placa) / Mp * dt
            self.vel[self.placa] = (self.V_placa, self.vy_placa); self.w[self.placa] = 0.0
        self.pos += self.vel * dt
        self.t += dt

    # ------------------------------------------------------------------ utilidades
    def energia_cinetica_media(self):
        L = ~(self.fixo | self.placa)
        return (0.5 * np.sum(self.m[L] * np.sum(self.vel[L]**2, 1)) + 0.5 * np.sum(self.I[L] * self.w[L]**2)) / L.sum()

    def rodar(self, tempo, parar_quando_parado=False, ek_min=1e-4, a_cada=500, ao_registrar=None):
        for k in range(int(tempo / self.dt)):
            self.passo()
            if k % a_cada == 0:
                if ao_registrar is not None:
                    ao_registrar(self)
                if parar_quando_parado and k > 4 * a_cada and self.energia_cinetica_media() < ek_min:
                    break
        return self


# ====================================================================== montagens prontas
def caixa_cisalhamento(Lx=24, n_camadas=16, seed=0):
    """Camada de grãos entre um fundo rugoso fixo e uma placa rugosa no topo; periódica em x."""
    rng = np.random.default_rng(seed)
    dr = 0.5                                             # grãos da rugosidade: diâmetro 0,5
    xr = np.arange(0.25, Lx, dr)
    nx = int(Lx / 1.1)
    xs, ys = np.meshgrid((np.arange(nx) + 0.5) * Lx / nx, 1.0 + np.arange(n_camadas) * 1.15)
    r = rng.uniform(0.4, 0.6, xs.size)                  # diâmetros entre 0,8 e 1,2
    topo = ys.max() + 1.0
    raios = np.concatenate([np.full(xr.size, dr / 2), r, np.full(xr.size, dr / 2)])
    X = np.concatenate([xr, xs.ravel() + rng.uniform(-0.05, 0.05, xs.size), xr])
    Y = np.concatenate([np.full(xr.size, 0.0), ys.ravel(), np.full(xr.size, topo)])
    fixo = np.r_[np.ones(xr.size, bool), np.zeros(xs.size + xr.size, bool)]
    placa = np.r_[np.zeros(xr.size + xs.size, bool), np.ones(xr.size, bool)]
    return raios, X, Y, fixo, placa


def ensaio_cisalhamento(mu, mu_r=0.0, sigma=10.0, Lx=24, n_camadas=16, I_inercial=0.005,
                        deformacao=2.0, seed=0, registrar=None):
    """Cisalhamento plano com tensão normal constante.
    Devolve a simulação e um histórico com colunas: tempo, deformação, tau/sigma, espessura."""
    raios, X, Y, fixo, placa = caixa_cisalhamento(Lx, n_camadas, seed)
    s = DEM2D(raios, X, Y, mu=mu, mu_r=mu_r, g=0.0, chao=False, periodo_x=Lx, fixo=fixo, placa=placa)
    s.P_placa = sigma * Lx                               # força normal total sobre a placa
    # 1) adensar: a placa desce sob a tensão normal, sem cisalhar
    s.rodar(30)
    H = s.pos[placa, 1].mean() - s.pos[fixo, 1].mean()
    # 2) cisalhar: placa anda com velocidade V.  Número inercial I = (V/H)*d / sqrt(sigma/densidade)
    s.V_placa = I_inercial * np.sqrt(sigma) * H
    hist = []
    t0 = s.t
    def reg(sim):
        Hs = sim.pos[placa, 1].mean() - sim.pos[fixo, 1].mean()
        hist.append((sim.t - t0, sim.V_placa * (sim.t - t0) / Hs, -sim.F_placa[0] / sim.P_placa, Hs))
        if registrar:
            registrar(sim)
    s.rodar(deformacao * H / s.V_placa, ao_registrar=reg, a_cada=200)
    return s, np.array(hist)
