"""
tools/gerar_sprites.py - gera a ARTE ANIMADA dos inimigos e bosses do Modo Infinito.

    python tools/gerar_sprites.py            -> grava os PNGs animados em assets/images/enemies e /bosses (NÃO sobrescreve arquivos que já existem; use --forcar)
    python tools/gerar_sprites.py --sheet    -> também grava tools/sprites_preview.png (folha de conferência)

Estilo: o mesmo dos retratos do jogo (ui/portraits.py): formas planas com contorno escuro, fundo transparente
(o jogo desenha a moldura escura em volta). A cor principal de cada criatura vem do campo "color" do JSON,
então a borda do HUD e a arte combinam. Cada arquivo é um PNG animado (APNG) de 4 quadros, que o
ui/gif_loader.py já sabe ler. Para usar a SUA arte no lugar, basta colocar um .gif com o mesmo nome:
o jogo procura .gif antes de .png.

Para mudar um desenho, edite a receita da criatura em SPRITES (no fim do arquivo) e rode de novo.
"""
import json
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = 192                 # tamanho final de cada quadro
SS = 3                  # super-amostragem (suaviza as bordas)
N = W * SS
U = N / 100.0           # o desenho é pensado numa grade de 100 x 100
FRAMES = 4
BOB = (0.0, -1.2, -2.2, -1.2)             # balanço vertical de cada quadro
FRAME_MS = 170


def sh(c, d):
    """Clareia (d > 0) ou escurece (d < 0) uma cor."""
    return tuple(max(0, min(255, v + d)) for v in c[:3])


def mix(c1, c2, k):
    return tuple(int(a + (b - a) * k) for a, b in zip(c1[:3], c2[:3]))


def rgba(c, a=255):
    return (int(c[0]), int(c[1]), int(c[2]), a)


class Art:
    """Pincel: tudo é desenhado em coordenadas 0..100 (centro em 50,50)."""

    def __init__(self, scale=1.0, t=0, dy=0.0):
        self.im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.im)
        self.s, self.t, self.dy = scale, t, dy

    # ---- coordenadas ----
    def p(self, x, y):
        return ((50 + (x - 50) * self.s) * U, (50 + (y + self.dy - 50) * self.s) * U)

    def lw(self, w):
        return max(1, int(round(w * U * self.s)))

    # ---- formas ----
    def poly(self, pts, fill, ol=True, w=1.0, alpha=255):
        P = [self.p(*q) for q in pts]
        self.d.polygon(P, fill=rgba(fill, alpha))
        if ol:
            self.d.line(P + [P[0]], fill=rgba(sh(fill, -80), alpha), width=self.lw(w), joint="curve")

    def ell(self, cx, cy, rx, ry, fill, ol=True, w=1.0, shine=False, alpha=255):
        x0, y0 = self.p(cx - rx, cy - ry)
        x1, y1 = self.p(cx + rx, cy + ry)
        self.d.ellipse([x0, y0, x1, y1], fill=rgba(fill, alpha),
                       outline=rgba(sh(fill, -80), alpha) if ol else None, width=self.lw(w))
        if shine:
            self.ell(cx - rx * 0.35, cy - ry * 0.4, rx * 0.35, ry * 0.25, sh(fill, 60), ol=False, alpha=alpha)

    def rect(self, x0, y0, x1, y1, fill, r=1.5, ol=True, w=1.0):
        a, b = self.p(x0, y0), self.p(x1, y1)
        self.d.rounded_rectangle([a[0], a[1], b[0], b[1]], radius=int(r * U * self.s), fill=rgba(fill),
                                 outline=rgba(sh(fill, -80)) if ol else None, width=self.lw(w))

    def line(self, a, b, w, fill):
        A, B = self.p(*a), self.p(*b)
        self.d.line([A, B], fill=rgba(fill), width=self.lw(w))
        r = self.lw(w) / 2
        for q in (A, B):
            self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=rgba(fill))

    def curve(self, pts, w, fill, ol=False):
        """Linha grossa passando por vários pontos (pescoços, caudas, tentáculos)."""
        P = [self.p(*q) for q in pts]
        if ol:
            self.d.line(P, fill=rgba(sh(fill, -80)), width=self.lw(w + 1.6), joint="curve")
            r = self.lw(w + 1.6) / 2
            for q in (P[0], P[-1]):
                self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=rgba(sh(fill, -80)))
        self.d.line(P, fill=rgba(fill), width=self.lw(w), joint="curve")
        r = self.lw(w) / 2
        for q in (P[0], P[-1]):
            self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=rgba(fill))

    def taper(self, pts, w0, w1, fill, ol=True):
        """Tentáculo/cauda que afina: círculos de raio decrescente ao longo dos pontos."""
        steps = []
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            for i in range(8):
                k = i / 8
                steps.append((x0 + (x1 - x0) * k, y0 + (y1 - y0) * k))
        steps.append(pts[-1])
        for pass_color, grow in ((sh(fill, -80), 0.8), (fill, 0.0)) if ol else ((fill, 0.0),):
            for i, (x, y) in enumerate(steps):
                w = w0 + (w1 - w0) * i / max(1, len(steps) - 1) + grow
                self.ell(x, y, w / 2, w / 2, pass_color, ol=False)

    def glow(self, cx, cy, r, color, strength=0.6):
        """Brilho suave (aura, olhos, magia)."""
        layer = Image.new("RGBA", (N, N), (0, 0, 0, 0))
        x, y = self.p(cx, cy)
        rr = r * U * self.s
        ImageDraw.Draw(layer).ellipse([x - rr, y - rr, x + rr, y + rr], fill=rgba(color, int(255 * strength)))
        layer = layer.filter(ImageFilter.GaussianBlur(rr * 0.55))
        self.im.alpha_composite(layer)
        self.d = ImageDraw.Draw(self.im)

    def sparkle(self, cx, cy, r, color):
        self.poly([(cx, cy - r), (cx + r * 0.3, cy - r * 0.3), (cx + r, cy), (cx + r * 0.3, cy + r * 0.3),
                   (cx, cy + r), (cx - r * 0.3, cy + r * 0.3), (cx - r, cy), (cx - r * 0.3, cy - r * 0.3)],
                  color, ol=False)

    def eyes(self, x, y, gap, r, color, slit=False, angry=False):
        for side in (-1, 1):
            ex = x + side * gap
            self.glow(ex, y, r * 2.2, color, 0.35)
            self.ell(ex, y, r, r * (1.1 if slit else 1.0), color, ol=False)
            self.ell(ex, y, r * (0.28 if slit else 0.45), r * (0.95 if slit else 0.45), (20, 10, 20), ol=False)
            if angry:                                    # sobrancelha brava
                self.line((ex - side * r * 0.2, y - r * 1.5), (ex + side * r * 1.8, y - r * 0.4 - 0.4), 0.9, (25, 15, 25))


# ======================================================================
# PEÇAS REUTILIZÁVEIS (cabeças, armas, asas, auras)
# ======================================================================
def _skull(a, x, y, r, bone=(232, 226, 205), eye=(120, 255, 170), crown=None):
    a.ell(x, y - r * 0.1, r, r * 0.95, bone, shine=True)
    a.rect(x - r * 0.55, y + r * 0.5, x + r * 0.55, y + r * 1.15, sh(bone, -12), r=1.0)          # mandíbula
    for i in range(-2, 3):
        a.line((x + i * r * 0.22, y + r * 0.62), (x + i * r * 0.22, y + r * 1.08), 0.5, sh(bone, -90))
    for side in (-1, 1):
        a.ell(x + side * r * 0.42, y - r * 0.05, r * 0.28, r * 0.32, (25, 20, 30), ol=False)
        a.glow(x + side * r * 0.42, y - r * 0.05, r * 0.6, eye, 0.5)
        a.ell(x + side * r * 0.42, y - r * 0.05, r * 0.12, r * 0.14, eye, ol=False)
    a.poly([(x - r * 0.1, y + r * 0.28), (x + r * 0.1, y + r * 0.28), (x, y + r * 0.5)], (30, 24, 34), ol=False)
    if crown:
        for i in range(-2, 3):
            h = r * (0.75 if i % 2 == 0 else 0.5)
            a.poly([(x + i * r * 0.4 - r * 0.18, y - r * 0.8), (x + i * r * 0.4, y - r * 0.8 - h),
                    (x + i * r * 0.4 + r * 0.18, y - r * 0.8)], crown)
        a.rect(x - r * 0.95, y - r * 0.95, x + r * 0.95, y - r * 0.72, sh(crown, -25), r=0.8)


def _head(a, kind, x, y, r, skin, c, c2, eye):
    """Cabeças: human, skull, crown (caveira coroada), hood, helm, horned (elmo com chifres), bull, wolf,
    beak (máscara de peste), demon, snakes, witch."""
    bone = (232, 226, 205)
    if kind in ("skull", "crown"):
        _skull(a, x, y, r, bone, eye, crown=c2 if kind == "crown" else None)
        return
    if kind == "hood":
        a.poly([(x - r * 1.15, y + r * 1.25), (x - r * 0.95, y - r * 0.3), (x - r * 0.2, y - r * 1.35), (x + r * 0.2, y - r * 1.35),
                (x + r * 0.95, y - r * 0.3), (x + r * 1.15, y + r * 1.25), (x, y + r * 0.9)], c)
        a.ell(x, y + r * 0.1, r * 0.72, r * 0.78, (18, 14, 26), ol=False)
        a.eyes(x, y + r * 0.05, r * 0.3, r * 0.13, eye)
        return
    if kind == "bull":
        a.poly([(x - r * 0.9, y - r * 0.4), (x - r * 1.9, y - r * 0.95), (x - r * 1.55, y - r * 0.2), (x - r * 0.7, y + r * 0.1)], (240, 235, 215))
        a.poly([(x + r * 0.9, y - r * 0.4), (x + r * 1.9, y - r * 0.95), (x + r * 1.55, y - r * 0.2), (x + r * 0.7, y + r * 0.1)], (240, 235, 215))
        a.ell(x, y, r, r * 1.05, skin, shine=True)
        a.ell(x, y + r * 0.55, r * 0.6, r * 0.42, sh(skin, 35))                     # focinho
        a.ell(x - r * 0.2, y + r * 0.5, r * 0.09, r * 0.1, (40, 25, 25), ol=False)
        a.ell(x + r * 0.2, y + r * 0.5, r * 0.09, r * 0.1, (40, 25, 25), ol=False)
        a.curve([(x - r * 0.3, y + r * 0.8), (x, y + r * 0.95), (x + r * 0.3, y + r * 0.8)], 0.7, (220, 200, 90))   # argola
        a.eyes(x, y - r * 0.15, r * 0.42, r * 0.13, (255, 90, 60), angry=True)
        return
    if kind == "wolf":
        for side in (-1, 1):
            a.poly([(x + side * r * 0.35, y - r * 0.6), (x + side * r * 1.0, y - r * 1.5), (x + side * r * 1.15, y - r * 0.4)], skin)
        a.ell(x, y, r * 1.05, r, skin, shine=True)
        a.poly([(x - r * 0.45, y + r * 0.1), (x + r * 0.45, y + r * 0.1), (x + r * 0.35, y + r * 1.05), (x - r * 0.35, y + r * 1.05)], sh(skin, 25))
        a.ell(x, y + r * 0.2, r * 0.17, r * 0.12, (30, 20, 25), ol=False)
        for side in (-1, 1):
            a.poly([(x + side * r * 0.2, y + r * 0.85), (x + side * r * 0.35, y + r * 0.85), (x + side * r * 0.27, y + r * 1.2)], (245, 245, 235), ol=False)
        a.eyes(x, y - r * 0.2, r * 0.42, r * 0.14, eye, slit=True, angry=True)
        return
    if kind == "beak":
        a.poly([(x - r * 1.4, y - r * 0.55), (x + r * 1.4, y - r * 0.55), (x + r * 0.8, y - r * 0.8), (x + r * 0.5, y - r * 1.5),
                (x - r * 0.5, y - r * 1.5), (x - r * 0.8, y - r * 0.8)], sh(c, -50))                  # chapéu
        a.ell(x, y, r * 0.95, r, (200, 195, 175), shine=True)
        a.poly([(x - r * 0.28, y + r * 0.1), (x + r * 0.28, y + r * 0.1), (x + r * 0.06, y + r * 1.75), (x - r * 0.06, y + r * 1.5)], (190, 180, 150))   # bico
        for side in (-1, 1):
            a.ell(x + side * r * 0.42, y - r * 0.15, r * 0.3, r * 0.3, (35, 40, 35))
            a.ell(x + side * r * 0.42, y - r * 0.15, r * 0.17, r * 0.17, eye, ol=False)
        return
    if kind == "demon":
        a.poly([(x - r * 0.7, y - r * 0.5), (x - r * 1.5, y - r * 1.9), (x - r * 0.2, y - r * 0.9)], (60, 30, 30))
        a.poly([(x + r * 0.7, y - r * 0.5), (x + r * 1.5, y - r * 1.9), (x + r * 0.2, y - r * 0.9)], (60, 30, 30))
        a.ell(x, y, r, r * 1.02, skin, shine=True)
        a.eyes(x, y - r * 0.1, r * 0.42, r * 0.17, (255, 230, 70), slit=True, angry=True)
        a.poly([(x - r * 0.55, y + r * 0.45), (x + r * 0.55, y + r * 0.45), (x + r * 0.4, y + r * 0.8), (x - r * 0.4, y + r * 0.8)], (35, 10, 20))
        for i in range(-2, 3):
            a.poly([(x + i * r * 0.2 - r * 0.07, y + r * 0.47), (x + i * r * 0.2 + r * 0.07, y + r * 0.47), (x + i * r * 0.2, y + r * 0.7)], (245, 240, 230), ol=False)
        return
    if kind == "snakes":
        for i, ang in enumerate((-2.6, -2.1, -1.57, -1.05, -0.5)):
            sx, sy = x + math.cos(ang) * r * 0.9, y + math.sin(ang) * r * 0.9
            wob = math.sin(a.t * 1.57 + i) * 1.2
            a.curve([(sx, sy), (sx + math.cos(ang) * r * 0.7 + wob, sy + math.sin(ang) * r * 0.6),
                     (sx + math.cos(ang) * r * 1.3 - wob, sy + math.sin(ang) * r * 1.1 - r * 0.2)], 1.8, (80, 160, 90), ol=True)
            a.ell(sx + math.cos(ang) * r * 1.3 - wob, sy + math.sin(ang) * r * 1.1 - r * 0.3, 1.5, 1.2, (110, 190, 110))
        a.ell(x, y, r * 0.95, r, skin, shine=True)
        a.eyes(x, y - r * 0.05, r * 0.4, r * 0.15, (240, 230, 80), slit=True)
        a.line((x - r * 0.3, y + r * 0.55), (x + r * 0.3, y + r * 0.55), 0.7, (90, 40, 50))
        return
    if kind == "witch":
        for i, k in enumerate((-1.0, -0.5, 0.0, 0.5, 1.0)):                                # cabelo em chamas
            fl = math.sin(a.t * 1.57 + i) * 1.2
            a.poly([(x + k * r * 0.9 - r * 0.25, y - r * 0.2), (x + k * r * 1.3 + fl, y - r * 1.2 - abs(k) * r * 0.2),
                    (x + k * r * 0.9 + r * 0.25, y - r * 0.2)], (255, 140 + i * 20, 40), ol=False)
        a.ell(x, y, r * 0.95, r, skin, shine=True)
        a.poly([(x - r * 1.5, y - r * 0.55), (x + r * 1.5, y - r * 0.55), (x + r * 0.7, y - r * 0.75), (x + r * 0.15, y - r * 2.3),
                (x - r * 0.55, y - r * 0.75)], sh(c, -45))                                    # chapéu
        a.rect(x - r * 0.75, y - r * 0.85, x + r * 0.75, y - r * 0.6, (240, 170, 60), r=0.5)
        a.eyes(x, y + r * 0.05, r * 0.38, r * 0.13, (255, 240, 120))
        return
    if kind == "helm" or kind == "horned":
        if kind == "horned":
            for side in (-1, 1):
                a.poly([(x + side * r * 0.85, y - r * 0.5), (x + side * r * 1.9, y - r * 1.5), (x + side * r * 1.3, y - r * 0.1)], (230, 225, 205))
        a.ell(x, y, r * 1.0, r * 1.05, (150, 155, 170), shine=True)
        a.rect(x - r * 0.15, y - r * 1.0, x + r * 0.15, y + r * 0.5, (120, 125, 140), r=0.5)       # crista central
        a.rect(x - r * 0.85, y - r * 0.05, x + r * 0.85, y + r * 0.35, (25, 22, 32), r=0.8)       # viseira
        a.glow(x, y + r * 0.15, r * 0.9, eye, 0.4)
        a.line((x - r * 0.6, y + r * 0.15), (x - r * 0.15, y + r * 0.15), 1.1, eye)
        a.line((x + r * 0.15, y + r * 0.15), (x + r * 0.6, y + r * 0.15), 1.1, eye)
        return
    # human
    a.ell(x, y, r, r * 1.05, skin, shine=True)
    a.ell(x, y - r * 0.55, r * 0.95, r * 0.5, sh(c2, -20))
    a.eyes(x, y, r * 0.38, r * 0.12, (30, 25, 35))


def _weapon(a, kind, wc, c2):
    t = a.t
    if kind in (None, "none"):
        return
    if kind == "staff":
        a.line((84, 92), (84, 30), 2.2, (130, 90, 55))
        a.glow(84, 26, 11, c2, 0.5 + 0.1 * (t % 2))
        a.ell(84, 26, 5, 5, mix(c2, (255, 255, 255), 0.35), shine=True)
        a.poly([(78, 28), (84, 17), (90, 28)], sh(wc, -20), ol=False)
    elif kind == "sword":
        a.poly([(83, 88), (86, 88), (87, 42), (84.5, 34), (82, 42)], (225, 228, 238))
        a.line((84.5, 40), (84.5, 80), 0.6, (170, 175, 190))
        a.rect(77, 86, 92, 90, (150, 110, 60), r=1.2)
        a.rect(82.5, 90, 86.5, 97, (110, 70, 45), r=1.0)
    elif kind == "greatsword":
        a.poly([(82, 90), (88, 90), (90, 24), (85, 12), (80, 24)], (210, 215, 232))
        a.line((85, 20), (85, 84), 0.8, (150, 155, 175))
        a.glow(85, 52, 14, c2, 0.28)
        a.rect(75, 88, 95, 93, (110, 90, 70), r=1.2)
        a.rect(83, 93, 87, 99, (90, 60, 40), r=1.0)
    elif kind == "axe":
        a.line((82, 94), (82, 38), 2.2, (120, 80, 50))
        a.poly([(82, 36), (96, 30), (98, 52), (82, 50)], (190, 195, 210))
        a.poly([(82, 36), (74, 32), (74, 48), (82, 50)], (160, 165, 180))
    elif kind == "bow":
        a.curve([(78, 28), (92, 50), (78, 74)], 2.2, (140, 95, 55), ol=True)
        a.line((78, 28), (78, 74), 0.4, (235, 235, 235))
        a.line((60, 51), (90, 51), 0.9, (210, 210, 220))
        a.poly([(90, 48.5), (96, 51), (90, 53.5)], (225, 225, 235), ol=False)
    elif kind == "dagger":
        for side in (-1, 1):
            bx = 50 + side * 38
            a.poly([(bx - 1.5, 76), (bx + 1.5, 76), (bx + 0.5, 56), (bx - 0.5, 56)], (225, 228, 240))
            a.rect(bx - 3, 76, bx + 3, 78.5, (90, 60, 50), r=0.8)
            a.rect(bx - 1.2, 78.5, bx + 1.2, 84, (70, 45, 40), r=0.6)
    elif kind == "scythe":
        a.line((82, 96), (82, 14), 2.0, (95, 70, 50))
        a.curve([(82, 14), (62, 12), (44, 26), (38, 40)], 2.8, (205, 210, 225), ol=True)
        a.poly([(38, 40), (44, 32), (47, 40)], (230, 235, 245), ol=False)
    elif kind == "trident":
        a.line((84, 98), (84, 20), 2.0, (90, 70, 60))
        a.curve([(75, 34), (75, 22), (84, 14), (93, 22), (93, 34)], 1.8, (220, 215, 205), ol=True)
        a.line((84, 14), (84, 24), 1.8, (220, 215, 205))
        a.glow(84, 20, 9, c2, 0.4)
    elif kind == "lantern":
        a.line((84, 92), (84, 36), 1.8, (95, 75, 55))
        a.rect(78, 32, 90, 46, (60, 55, 50), r=1.5)
        a.rect(80, 34, 88, 44, (170, 255, 150), r=1.0, ol=False)
        a.glow(84, 39, 12, (170, 255, 150), 0.55)
    elif kind == "chain":
        a.curve([(80, 60), (88, 72), (84, 86)], 1.3, (150, 155, 170), ol=True)
        a.ell(84, 90, 8, 8, (110, 115, 130), shine=True)
        for i in range(-2, 3):
            a.poly([(84 + i * 3 - 1, 83), (84 + i * 3, 79), (84 + i * 3 + 1, 83)], (170, 175, 190), ol=False)


def _wings(a, kind, color, cx, cy, span=1.0, up=0.0):
    """Asas atrás do corpo. kind: bat (membrana), feather (penas), dragon (membrana grande), flame."""
    flap = (0, 5, 10, 5)[a.t]
    for side in (-1, 1):
        tip = (cx + side * 44 * span, cy - 22 * span - flap + up)
        if kind in ("bat", "dragon"):
            pts = [(cx + side * 6, cy - 4), tip, (cx + side * 40 * span, cy + 6), (cx + side * 32 * span, cy + 1),
                   (cx + side * 27 * span, cy + 16), (cx + side * 18 * span, cy + 9), (cx + side * 12 * span, cy + 20), (cx + side * 4, cy + 12)]
            a.poly(pts, color)
            for q in ((cx + side * 40 * span, cy + 6), (cx + side * 27 * span, cy + 16), (cx + side * 12 * span, cy + 20)):
                a.line((cx + side * 6, cy - 4), q, 0.8, sh(color, -70))
            a.line((cx + side * 6, cy - 4), tip, 1.4, sh(color, -50))
        elif kind == "feather":
            for i in range(6):
                k = i / 5
                end = (cx + side * (46 - i * 4) * span, cy - 20 * span * (1 - k) + 14 * k - flap * (1 - k))
                a.poly([(cx + side * 6, cy - 2 + i), (end[0], end[1] - 4), (end[0] + side * 3, end[1] + 6), (cx + side * 8, cy + 6 + i)],
                       sh(color, 12 - i * 8))
        elif kind == "flame":
            for lay, (col, sc) in enumerate(((color, 1.0), (mix(color, (255, 200, 60), 0.5), 0.78), ((255, 235, 120), 0.52))):
                pts = [(cx + side * 5, cy), (cx + side * 46 * span * sc, cy - 26 * span * sc - flap), (cx + side * 40 * span * sc, cy - 4),
                       (cx + side * 46 * span * sc, cy + 8), (cx + side * 30 * span * sc, cy + 10), (cx + side * 22 * span * sc, cy + 22 * sc), (cx + side * 8, cy + 10)]
                a.poly(pts, col, ol=(lay == 0))


def aura(a, color, strength=0.55, r=46):
    """Brilho atrás da criatura (Super Bosses brilham mais)."""
    pulse = 0.78 + 0.22 * math.sin(a.t * math.pi / 2)
    save, a.dy = a.dy, 0.0
    a.glow(50, 52, r * pulse, color, strength)
    a.dy = save


def runes(a, color, r=40, count=6):
    """Runas/losangos que giram em volta do Super Boss."""
    save, a.dy = a.dy, 0.0
    for i in range(count):
        ang = (i / count + a.t / (count * 4.0)) * 2 * math.pi
        x, y = 50 + math.cos(ang) * r, 54 + math.sin(ang) * r * 0.55
        a.glow(x, y, 4.5, color, 0.6)
        a.sparkle(x, y, 2.8, mix(color, (255, 255, 255), 0.5))
    a.dy = save


def ground_shadow(a, rx=30):
    save, a.dy = a.dy, 0.0
    a.ell(50, 93, rx, 4.2, (0, 0, 0), ol=False, alpha=90)
    a.dy = save


# ======================================================================
# PLANOS DE CORPO
# ======================================================================
def humanoid(a, c, c2, eye, head="human", weapon=None, wc=(205, 210, 225), robe=False, cape=None, wings=None,
             wing_c=None, bulk=1.0, hunch=0.0, skin=(235, 200, 160), plate=False, extras=(), accent=None):
    accent = accent or c2
    if cape:
        a.poly([(30, 42), (70, 42), (86, 94), (14, 94)], cape)
        a.line((22, 90), (78, 90), 0.8, sh(cape, 35))
    if wings:
        _wings(a, wings, wing_c or sh(c, -25), 50, 48, 1.0)
    bw = 17 * bulk
    if robe:
        a.poly([(50 - bw, 48), (50 + bw, 48), (50 + bw + 9, 93), (50 - bw - 9, 93)], c)
        a.poly([(50 - bw - 9, 93), (50 + bw + 9, 93), (50 + bw + 8, 88), (50 - bw - 8, 88)], c2, ol=False)
        a.line((50, 52), (50, 92), 0.7, sh(c, -45))
    else:
        for side in (-1, 1):
            a.rect(50 + side * bw * 0.45 - 5, 72, 50 + side * bw * 0.45 + 5, 93, sh(c, -35), r=2)
            a.rect(50 + side * bw * 0.45 - 6, 88, 50 + side * bw * 0.45 + 6, 94, (60, 50, 50), r=1.5)
        a.rect(50 - bw, 46, 50 + bw, 78, sh(c, -5) if not plate else (140, 145, 160), r=5)
    if plate:
        a.rect(50 - bw + 2, 48, 50 + bw - 2, 76, (150, 155, 170), r=4)
        a.line((50, 48), (50, 76), 1.0, (95, 100, 115))
        for y in (56, 64, 72):
            a.line((50 - bw + 5, y), (50 + bw - 5, y), 0.7, (100, 105, 120))
        for side in (-1, 1):
            a.ell(50 + side * (bw + 1), 49, 9, 6.5, (165, 170, 186), shine=True)
            for k in (-1, 1):
                a.poly([(50 + side * (bw + 1) + k * 3 - 1.5, 45), (50 + side * (bw + 1) + k * 3, 39), (50 + side * (bw + 1) + k * 3 + 1.5, 45)], (190, 195, 210), ol=False)
    else:
        a.rect(50 - bw, 66, 50 + bw, 70, c2, r=1.0)                                    # cinto
        a.rect(47, 65, 53, 71, (235, 200, 80), r=1.0)
        a.poly([(50 - bw, 46), (50 + bw, 46), (50 + bw * 0.55, 54), (50 - bw * 0.55, 54)], c2, ol=False)
    for side in (-1, 1):                                                                 # braços
        sx = 50 + side * (bw + 2)
        a.curve([(sx, 52), (sx + side * 3, 64), (sx + side * 2, 74)], 5.5, sh(c, 5) if not plate else (150, 155, 170), ol=True)
        a.ell(sx + side * 2, 76, 3.4, 3.4, skin if "gauntlet" not in extras else (170, 175, 190))
    hy = 30 + hunch
    a.ell(50, hy + 15, 5, 5, sh(skin, -30), ol=False)                                    # pescoço
    _head(a, head, 50, hy, 15, skin, c, accent, eye)
    _weapon(a, weapon, wc, accent)
    if "belt_skulls" in extras:
        for x in (38, 62):
            _skull(a, x, 72, 3.2, eye=eye)
    if "chains" in extras:
        a.curve([(34, 52), (30, 66), (38, 80), (50, 74)], 1.1, (150, 155, 170), ol=True)
        a.curve([(66, 52), (70, 66), (62, 80), (50, 74)], 1.1, (150, 155, 170), ol=True)
    if "talons" in extras:
        for side in (-1, 1):
            for k in (-1, 0, 1):
                a.poly([(50 + side * 8 + k * 3 - 1.2, 93), (50 + side * 8 + k * 3 + 1.2, 93), (50 + side * 8 + k * 3, 98)], (230, 200, 90), ol=False)
    if "tail" in extras:
        a.curve([(58, 86), (76, 94), (86, 84), (88, 74)], 2.2, sh(c, -20), ol=True)
        a.poly([(84, 76), (88, 68), (92, 76)], accent, ol=False)
    if "wisps" in extras:
        for i in range(3):
            wx = 22 + i * 28 + math.sin(a.t * 1.57 + i) * 2
            a.glow(wx, 88 - (a.t + i) % 3 * 3, 6, eye, 0.35)
    if "mist" in extras:
        for i in range(4):
            a.ell(24 + i * 17, 90 - math.sin(a.t * 1.57 + i) * 1.5, 11, 4, (130, 220, 120), ol=False, alpha=110)
    if "flames" in extras:
        for i in range(5):
            fx = 30 + i * 10
            a.poly([(fx - 3, 92), (fx + math.sin(a.t * 1.57 + i) * 2, 80 - i % 2 * 5), (fx + 3, 92)], (255, 150 + i * 14, 40), ol=False)
    if "souls" in extras:
        for i in range(3):
            sx, sy = 16 + i * 34, 30 + ((a.t + i) % 4) * -2 + i * 6
            a.ell(sx, sy, 4.5, 5.5, (190, 255, 230), ol=False, alpha=150)
            a.poly([(sx - 4.5, sy + 3), (sx + 4.5, sy + 3), (sx + 2, sy + 11), (sx, sy + 8), (sx - 2, sy + 11)], (190, 255, 230), ol=False, alpha=150)
            a.ell(sx - 1.6, sy - 0.5, 0.9, 1.2, (20, 40, 50), ol=False)
            a.ell(sx + 1.6, sy - 0.5, 0.9, 1.2, (20, 40, 50), ol=False)
    if "shadow" in extras:
        for i, ang in enumerate((-0.9, -0.3, 0.3, 0.9)):
            a.taper([(50 + math.sin(ang) * 10, 88), (50 + math.sin(ang) * 30, 92 + math.sin(a.t * 1.57 + i) * 2), (50 + math.sin(ang) * 42, 82)],
                    5, 1, sh(c, -30), ol=False)
    if "stars" in extras:
        for i in range(7):
            sx, sy = 22 + (i * 37) % 56, 52 + (i * 23) % 40
            a.sparkle(sx, sy, 1.6 + (i + a.t) % 2, (230, 220, 255))


def bat(a, c, wc, eye):
    flap = (0, 5, 10, 5)[a.t]
    for side in (-1, 1):
        pts = [(50 + side * 7, 50), (50 + side * 46, 24 - flap), (50 + side * 41, 46), (50 + side * 33, 40), (50 + side * 27, 58),
               (50 + side * 18, 50), (50 + side * 12, 62), (50 + side * 6, 58)]
        a.poly(pts, wc)
        for q in ((50 + side * 41, 46), (50 + side * 27, 58), (50 + side * 12, 62)):
            a.line((50 + side * 7, 50), q, 0.8, sh(wc, -70))
        a.line((50 + side * 7, 50), (50 + side * 46, 24 - flap), 1.4, sh(wc, -45))
    for side in (-1, 1):
        a.poly([(50 + side * 5, 38), (50 + side * 13, 22), (50 + side * 12, 40)], c)
    a.ell(50, 62, 12, 16, c, shine=True)
    a.ell(50, 66, 7, 10, sh(c, 35), ol=False)
    a.ell(50, 42, 11, 10, c, shine=True)
    a.eyes(50, 40, 5, 2.2, eye, angry=True)
    for side in (-1, 1):
        a.poly([(50 + side * 3.2, 47), (50 + side * 5.2, 47), (50 + side * 4.2, 53)], (250, 250, 240), ol=False)
    a.ell(50, 46.5, 2.2, 1.2, (40, 20, 30), ol=False)
    for side in (-1, 1):
        a.poly([(50 + side * 5, 76), (50 + side * 9, 90), (50 + side * 2, 80)], sh(c, -20))


def slime(a, c, eye, acid=False):
    pts = []
    for i in range(0, 181, 6):
        r = math.radians(180 + i)
        pts.append((50 + 34 * math.cos(r), 84 + 38 * math.sin(r) * (1 + 0.04 * math.sin(a.t * 1.57))))
    pts += [(84, 90), (70, 92), (62, 88), (50, 93), (36, 89), (26, 92), (16, 90)]
    a.poly(pts, c, alpha=235)
    a.ell(36, 56, 8, 5, sh(c, 70), ol=False, alpha=190)
    a.ell(60, 78, 14, 6, sh(c, -30), ol=False, alpha=120)
    for bx, by, br in ((62, 66, 3.2), (70, 74, 2.2), (32, 74, 2.6), (54, 58, 1.8)):
        a.ell(bx, by + math.sin(a.t * 1.57 + bx) * 1.2, br, br, sh(c, 50), alpha=170)
    for side in (-1, 1):
        a.ell(50 + side * 11, 66, 7.5, 8.5, (250, 250, 245), w=0.9)
        a.ell(50 + side * 11 - side * 1, 67, 3.4, 4.2, (20, 25, 20), ol=False)
        a.ell(50 + side * 11 - side * 2, 65, 1.2, 1.2, (255, 255, 255), ol=False)
    a.curve([(40, 80), (46, 84), (54, 84), (60, 80)], 1.3, sh(c, -90))
    if acid:
        a.ell(26, 88, 3, 5, c, alpha=240)
        a.poly([(24, 92), (28, 92), (26, 99)], c, ol=False)
        a.sparkle(76, 40, 3, (210, 255, 150))
        a.sparkle(24, 46, 2.4, (210, 255, 150))


def wolf(a, c, eye, pelt2=None):
    pelt2 = pelt2 or sh(c, 30)
    a.curve([(26, 62), (14, 52), (10, 36)], 6, sh(c, -15), ol=True)
    for x in (30, 40, 60, 70):
        a.rect(x - 3, 70, x + 3.5, 92, sh(c, -25) if x in (30, 60) else sh(c, -10), r=2)
        a.poly([(x - 3.5, 92), (x + 4, 92), (x + 5, 97), (x - 4, 97)], (50, 45, 50))
    a.ell(46, 62, 28, 15, c, shine=True)
    a.ell(48, 70, 22, 7, pelt2, ol=False)
    for i in range(7):
        a.poly([(28 + i * 7 - 3, 50 + (i % 2)), (28 + i * 7, 41 - (i == 3) * 3), (28 + i * 7 + 3, 50)], sh(c, -25), ol=False)
    a.poly([(66, 48), (84, 42), (94, 56), (84, 70), (66, 66)], c)
    a.poly([(66, 48), (72, 36), (76, 46)], sh(c, -25))
    a.poly([(76, 46), (82, 35), (84, 45)], sh(c, -25))
    a.poly([(82, 54), (98, 58), (86, 66)], pelt2)
    a.ell(96, 58, 1.8, 1.6, (30, 20, 25), ol=False)
    a.poly([(86, 62), (94, 66), (88, 70)], (245, 245, 235), ol=False)
    a.glow(79, 51, 4, eye, 0.5)
    a.ell(79, 51, 2.4, 1.8, eye, ol=False)
    a.line((74, 47), (83, 50), 0.9, (25, 15, 20))


def mushroom(a, c, eye):
    a.rect(38, 52, 62, 90, (235, 225, 195), r=7)
    a.ell(50, 86, 15, 6, (235, 225, 195))
    a.ell(50, 46, 38, 23, sh(c, -20), ol=False)
    a.poly([(12, 46), (88, 46), (82, 54), (18, 54)], (80, 55, 70))
    for k in range(7):
        a.line((18 + k * 10.7, 48), (21 + k * 9.7, 54), 0.5, (50, 35, 50))
    a.ell(50, 40, 38, 24, c, shine=True)
    for sx, sy, r in ((30, 36, 5), (52, 28, 6), (70, 40, 4.5), (42, 46, 3.2), (62, 50, 3)):
        a.ell(sx, sy, r, r * 0.8, (255, 235, 245), ol=False)
    for side in (-1, 1):
        a.ell(50 + side * 7, 68, 4.2, 5.2, (255, 255, 255), w=0.8)
        a.ell(50 + side * 7, 69, 2, 2.6, (25, 20, 30), ol=False)
    a.curve([(43, 78), (50, 82), (57, 78)], 1.0, (90, 50, 60))
    for i in range(5):
        k = (a.t * 5 + i * 11) % 24
        a.ell(20 + i * 15, 30 - k * 0.6, 1.8, 1.8, (230, 255, 160), ol=False, alpha=int(220 - k * 7))


def imp(a, c, eye):
    flap = (0, 4, 8, 4)[a.t]
    for side in (-1, 1):
        a.poly([(50 + side * 6, 56), (50 + side * 36, 36 - flap), (50 + side * 30, 56), (50 + side * 18, 52), (50 + side * 14, 66)], sh(c, -40))
    a.curve([(56, 82), (74, 92), (88, 80), (84, 66)], 2.2, c, ol=True)
    a.poly([(79, 66), (85, 56), (91, 66)], (255, 120, 40), ol=True)
    for side in (-1, 1):
        a.rect(50 + side * 6 - 4, 78, 50 + side * 6 + 4, 92, sh(c, -20), r=2)
    a.ell(50, 64, 15, 17, c, shine=True)
    a.ell(50, 68, 9, 11, sh(c, 40), ol=False)
    for side in (-1, 1):
        a.curve([(50 + side * 14, 58), (50 + side * 24, 66), (50 + side * 24, 76)], 4.5, c, ol=True)
    a.glow(26, 80, 11, (255, 140, 40), 0.7)
    a.ell(26, 80, 6.5, 6.5, (255, 190, 60), ol=False)
    a.ell(26, 80, 3.4, 3.4, (255, 245, 170), ol=False)
    for i, k in enumerate((-8, -3, 2, 7)):
        a.poly([(50 + k - 2.5, 34), (50 + k + math.sin(a.t * 1.57 + i) * 1.2, 20 - (i % 2) * 5), (50 + k + 2.5, 34)], (255, 130 + i * 25, 40), ol=False)
    for side in (-1, 1):
        a.poly([(50 + side * 7, 32), (50 + side * 16, 16), (50 + side * 13, 34)], (70, 30, 30))
    a.ell(50, 42, 13, 12, c, shine=True)
    a.eyes(50, 40, 5.5, 2.4, (255, 235, 70), slit=True, angry=True)
    a.poly([(42, 47), (58, 47), (54, 52), (46, 52)], (40, 12, 20), ol=False)
    for x in (45.5, 54.5):
        a.poly([(x - 1, 47), (x + 1, 47), (x, 50)], (250, 250, 240), ol=False)


def ghost(a, c, mouth=0.0, hair=False, armor=False, eye=(190, 230, 255)):
    wav = [math.sin(a.t * 1.57 + i * 1.4) * 2.2 for i in range(6)]
    pts = [(28, 48), (34, 30), (50, 22), (66, 30), (72, 48), (76, 94 + wav[0]), (66, 86 + wav[1]), (58, 96 + wav[2]), (50, 86 + wav[3]),
           (42, 96 + wav[4]), (34, 86 + wav[5]), (24, 94 + wav[0])]
    if hair:
        for i in range(7):
            x0 = 32 + i * 6
            a.curve([(x0, 30), (x0 - 6 + math.sin(a.t * 1.57 + i) * 2, 52), (x0 - 12, 80 + wav[i % 6])], 2.6, sh(c, 40), ol=False)
    a.poly(pts, c, alpha=225)
    a.ell(50, 58, 14, 22, sh(c, 35), ol=False, alpha=150)
    for side in (-1, 1):
        a.curve([(50 + side * 22, 50), (50 + side * 30, 62 - mouth * 4), (50 + side * 28, 72 - mouth * 6)], 6, sh(c, 12), ol=True)
        for k in (-1, 0, 1):
            a.line((50 + side * 28 + k * 1.8, 72 - mouth * 6), (50 + side * 28 + k * 2.4, 78 - mouth * 6), 0.9, sh(c, 12))
    a.ell(50, 42, 15, 16, sh(c, 45), shine=True, alpha=240)
    for side in (-1, 1):
        a.ell(50 + side * 6, 38, 4.4, 6, (15, 20, 40), ol=False)
        a.glow(50 + side * 6, 39, 4, eye, 0.5)
        a.ell(50 + side * 6, 39, 1.6, 2.2, eye, ol=False)
    a.ell(50, 52, 4.2 + mouth * 2, 5 + mouth * 4, (15, 20, 40), ol=False)
    if armor:
        a.ell(50, 38, 16, 17, (150, 160, 190))
        a.rect(34, 36, 66, 42, (25, 25, 45), r=1.5)
        a.line((38, 39), (47, 39), 1.2, eye)
        a.line((53, 39), (62, 39), 1.2, eye)
        a.poly([(50, 16), (54, 24), (46, 24)], (230, 235, 255))
        a.poly([(30, 54), (70, 54), (66, 68), (34, 68)], (150, 160, 190))
        a.poly([(14, 52), (30, 52), (30, 76), (22, 84), (14, 76)], (110, 125, 170))
        a.line((22, 56), (22, 78), 0.8, (190, 200, 230))
        a.poly([(80, 88), (84, 88), (85, 36), (82, 28), (79, 36)], (225, 232, 250))
        a.rect(74, 86, 90, 90, (120, 130, 175), r=1)


def scorpion(a, c, eye):
    for i in range(3):
        for side in (-1, 1):
            y = 62 + i * 6
            a.curve([(50 + side * 12, y), (50 + side * 28, y - 6 + i), (50 + side * 36, y + 14 + i * 3)], 2.0, sh(c, -30), ol=True)
    for side in (-1, 1):
        a.curve([(50 + side * 8, 56), (50 + side * 26, 44), (50 + side * 32, 34)], 4.2, sh(c, 5), ol=True)
        a.poly([(50 + side * 28, 32), (50 + side * 42, 24), (50 + side * 38, 36), (50 + side * 44, 42), (50 + side * 30, 42)], c)
    a.ell(50, 78, 17, 11, sh(c, -10), shine=True)
    a.ell(50, 66, 14, 10, c, shine=True)
    a.ell(50, 54, 11, 8, sh(c, 15), shine=True)
    for y in (64, 70, 76):
        a.line((38, y), (62, y), 0.6, sh(c, -70))
    tail = [(50, 88), (66, 94), (78, 82), (78, 62), (66, 46), (54, 40)]
    sway = math.sin(a.t * 1.57) * 1.5
    a.taper([(x + (sway if i > 2 else 0), y) for i, (x, y) in enumerate(tail)], 9, 5, sh(c, -5))
    a.poly([(50, 36), (58, 38), (62, 46), (56, 44)], (240, 235, 150))
    a.glow(52, 38, 5, (190, 255, 120), 0.5)
    a.eyes(50, 52, 4, 1.7, eye)


def treant(a, c, eye, big=False, corrupt=False):
    bark = sh(c, -45) if not corrupt else (70, 60, 50)
    leaf = c if not corrupt else (120, 150, 50)
    for side in (-1, 1):
        a.taper([(50 + side * 8, 88), (50 + side * 24, 94), (50 + side * 36, 90)], 8, 2, bark)
        a.taper([(50 + side * 14, 54), (50 + side * 32, 40), (50 + side * 40, 24 - (a.t % 2))], 9, 3, bark)
        for k, (lx, ly) in enumerate(((40, 22), (46, 30), (34, 30), (42, 38))):
            a.ell(50 + side * lx + side * k, ly + math.sin(a.t * 1.57 + k) * 0.8, 6.5, 5, sh(leaf, 20 * (k % 2)), shine=True)
    a.poly([(30, 92), (36, 50), (44, 34), (56, 34), (64, 50), (70, 92)], bark)
    for lx in (38, 46, 54, 62):
        a.line((lx, 44), (lx + 1, 88), 0.7, sh(bark, -35))
    for k in range(5):
        a.ell(50 + (k - 2) * 7, 30 - abs(k - 2) * 2.5, 9, 7, sh(leaf, 25 * (k % 2) - 10), shine=True)
    a.ell(50, 24, 14, 9, leaf, shine=True)
    for side in (-1, 1):
        a.ell(50 + side * 8, 56, 5, 5.6, (20, 15, 10))
        a.glow(50 + side * 8, 56, 5, eye, 0.55)
        a.ell(50 + side * 8, 56, 2.4, 2.8, eye, ol=False)
        a.line((50 + side * 4, 50), (50 + side * 13, 53), 1.0, (30, 20, 12))
    a.ell(50, 70, 7, 8 + a.t % 2, (25, 18, 12))
    if corrupt:
        for fx, fy in ((38, 74), (62, 66), (44, 82)):
            a.ell(fx, fy, 3.6, 2.6, (200, 90, 220), ol=False)
            a.glow(fx, fy, 6, (200, 90, 220), 0.35)
        for i in range(5):
            a.poly([(34 + i * 8, 40 + (i % 2) * 12), (34 + i * 8 + 3, 33 + (i % 2) * 12), (34 + i * 8 + 6, 40 + (i % 2) * 12)], (90, 70, 55), ol=False)
    elif not big:
        a.curve([(50, 24), (50, 14), (58, 8)], 1.5, (110, 190, 80), ol=False)
        a.ell(60, 8, 5, 3, (140, 220, 90), shine=True)


def mimic(a, c, eye):
    a.rect(16, 58, 84, 90, sh(c, -20), r=4)
    a.rect(16, 72, 84, 76, (90, 90, 105), r=1)
    for x in (22, 78):
        a.rect(x - 3, 58, x + 3, 90, (95, 95, 110), r=1)
    lift = (0, 3, 6, 3)[a.t]
    a.poly([(16, 58), (84, 58), (80, 28 - lift), (20, 28 - lift)], c)
    a.rect(16, 46 - lift * 0.5, 84, 51 - lift * 0.5, (90, 90, 105), r=1)
    a.rect(44, 52, 56, 64, (235, 200, 80), r=1.5)
    a.ell(50, 58, 2, 2, (40, 30, 20), ol=False)
    a.ell(50, 58, 28, 5, (110, 15, 25), ol=False)
    for i in range(7):
        x = 22 + i * 9.4
        a.poly([(x - 3, 56), (x + 3, 56), (x, 63)], (250, 248, 236), ol=False)
        a.poly([(x - 3, 59), (x + 3, 59), (x, 52)], (250, 248, 236), ol=False)
    a.poly([(42, 60), (60, 60), (58, 78 + a.t % 2 * 2), (50, 82), (44, 78)], (225, 90, 120))
    a.line((51, 62), (51, 76), 0.6, (170, 50, 80))
    for side in (-1, 1):
        a.glow(50 + side * 13, 38 - lift * 0.5, 6, eye, 0.5)
        a.ell(50 + side * 13, 38 - lift * 0.5, 4.4, 5.2, (255, 250, 230), w=0.8)
        a.ell(50 + side * 13, 39 - lift * 0.5, 2, 3.4, (25, 20, 15), ol=False)
    for gx, gy in ((12, 90), (24, 94), (80, 93), (90, 88)):
        a.ell(gx, gy, 3.4, 2.6, (240, 205, 70), shine=True)


def elemental(a, c, eye, kind="ice"):
    if kind == "ice":
        a.glow(50, 54, 40, c, 0.28)
        for side in (-1, 1):
            a.poly([(50 + side * 24, 54), (50 + side * 44, 30 - a.t), (50 + side * 36, 62)], sh(c, 10))
            a.poly([(50 + side * 30, 70), (50 + side * 48, 60), (50 + side * 38, 84)], sh(c, -20))
        a.poly([(50, 10), (72, 36), (66, 84), (50, 94), (34, 84), (28, 36)], c)
        a.poly([(50, 10), (72, 36), (50, 46)], sh(c, 50), ol=False)
        a.poly([(50, 46), (72, 36), (66, 84), (50, 94)], sh(c, -25), ol=False)
        a.poly([(50, 10), (28, 36), (50, 46)], sh(c, 25), ol=False)
        a.line((50, 46), (50, 94), 0.6, sh(c, -70))
        a.eyes(50, 38, 8, 3.2, (255, 255, 255), angry=True)
        for i in range(5):
            a.sparkle(14 + i * 17, 24 + (i * 29 + a.t * 6) % 56, 2.0, (240, 252, 255))
    else:
        a.glow(50, 60, 44, (255, 120, 30), 0.35)
        for side in (-1, 1):
            a.curve([(50 + side * 22, 52), (50 + side * 34, 66), (50 + side * 32, 80)], 9, (70, 55, 55), ol=True)
            a.ell(50 + side * 32, 82, 7, 7, (255, 140, 40))
            a.ell(50 + side * 32, 82, 4, 4, (255, 220, 90), ol=False)
        a.poly([(26, 92), (22, 60), (34, 36), (50, 30), (66, 36), (78, 60), (74, 92)], (70, 55, 58))
        a.ell(50, 62, 26, 28, (86, 66, 68), shine=True)
        for pts in (((36, 44), (44, 56), (40, 70)), ((64, 46), (58, 60), (66, 74)), ((46, 74), (54, 82), (50, 90)), ((30, 60), (38, 64))):
            a.curve(list(pts), 1.6, (255, 150, 40), ol=False)
        for i in range(5):
            fx = 34 + i * 8
            a.poly([(fx - 4, 34), (fx + math.sin(a.t * 1.57 + i) * 2, 12 - (i % 2) * 7 - (i == 2) * 6), (fx + 4, 34)], (255, 110 + i * 25, 30), ol=False)
        a.ell(50, 48, 11, 10, (60, 45, 48))
        a.eyes(50, 47, 5, 2.5, (255, 230, 80), angry=True)
        a.poly([(43, 54), (57, 54), (54, 58), (46, 58)], (255, 160, 40), ol=False)


def hydra(a, c, eye, big=False, stone=False):
    base = sh(c, -15)
    a.ell(50, 80, 30 if big else 24, 15, base, shine=True)
    for side in (-1, 1):
        a.poly([(50 + side * 22, 88), (50 + side * 36, 94), (50 + side * 24, 94)], sh(c, -50))
    heads = ((24, 36, 0.6), (50, 20, 0.0), (76, 36, -0.6))
    for i, (hx, hy, lean) in enumerate(heads):
        sway = math.sin(a.t * 1.57 + i * 2) * 2.2
        a.curve([(50 + (hx - 50) * 0.3, 74), (50 + (hx - 50) * 0.7 + sway, 58), (hx + sway, hy + 10)], 9 if big else 7, c, ol=True)
        hx += sway
        a.poly([(hx - 7, hy + 4), (hx + 7, hy + 4), (hx + 5, hy - 8), (hx, hy - 12), (hx - 5, hy - 8)], sh(c, 10))
        a.poly([(hx - 7, hy + 2), (hx - 12, hy - 8), (hx - 4, hy - 3)], sh(c, -40))
        a.poly([(hx + 7, hy + 2), (hx + 12, hy - 8), (hx + 4, hy - 3)], sh(c, -40))
        a.poly([(hx - 5, hy + 4), (hx + 5, hy + 4), (hx + 3, hy + 11), (hx - 3, hy + 11)], sh(c, 30))
        a.eyes(hx, hy - 3, 3.4, 1.7, eye, slit=True, angry=True)
        for k in (-1, 1):
            a.poly([(hx + k * 2.6 - 0.8, hy + 10), (hx + k * 2.6 + 0.8, hy + 10), (hx + k * 2.6, hy + 14)], (250, 248, 238), ol=False)
    if stone:
        for pts in (((34, 70), (40, 80), (36, 90)), ((60, 72), (66, 82)), ((46, 62), (50, 70), (46, 78))):
            a.curve(list(pts), 0.9, sh(base, -80), ol=False)
        for mx, my in ((30, 82), (62, 86), (50, 74)):
            a.ell(mx, my, 3.6, 2.4, (110, 150, 80), ol=False)
    else:
        for i in range(6):
            a.ell(34 + i * 6, 82 + (i % 2) * 3, 1.6, 1.6, sh(c, 45), ol=False)


def chimera(a, c, eye):
    a.curve([(26, 84), (10, 76), (8, 54), (16, 40)], 3.6, (100, 150, 70), ol=True)
    a.ell(14, 36, 5, 4, (100, 150, 70), shine=True)
    a.eyes(14, 35, 1.9, 0.9, (255, 230, 60))
    a.ell(50, 78, 30, 14, sh(c, -15), shine=True)
    for x in (30, 44, 60, 72):
        a.rect(x - 4, 84, x + 4, 95, sh(c, -30), r=2)
    for side in (-1, 1):
        a.poly([(50 + side * 8, 60), (50 + side * 30, 34), (50 + side * 24, 62)], (130, 70, 60))
    for i in range(10):
        ang = math.pi * (0.1 + i * 0.09) + math.pi
        a.poly([(50 + math.cos(ang) * 16, 50 + math.sin(ang) * 18), (50 + math.cos(ang) * 28, 50 + math.sin(ang) * 29),
                (50 + math.cos(ang + 0.3) * 16, 50 + math.sin(ang + 0.3) * 18)], sh(c, -50), ol=False)
    a.ell(50, 52, 17, 17, c, shine=True)
    a.poly([(42, 56), (58, 56), (54, 70), (46, 70)], sh(c, 30))
    a.ell(50, 57, 3.4, 2.4, (40, 25, 25), ol=False)
    for k in (-1, 1):
        a.poly([(50 + k * 3.4 - 1, 66), (50 + k * 3.4 + 1, 66), (50 + k * 3.4, 71)], (250, 248, 238), ol=False)
    a.eyes(50, 47, 7, 2.4, eye, slit=True, angry=True)
    a.poly([(74, 34), (92, 36), (94, 52), (82, 58), (72, 48)], (190, 180, 160))
    a.curve([(76, 34), (70, 22), (80, 14)], 3, (235, 230, 210), ol=True)
    a.curve([(88, 34), (96, 22), (88, 12)], 3, (235, 230, 210), ol=True)
    a.eyes(81, 44, 4, 1.5, (255, 200, 60), slit=True)
    a.poly([(80, 56), (84, 56), (82, 64)], (210, 200, 180))


def horror(a, c, eye, big=False):
    a.glow(50, 52, 42, sh(c, 20), 0.3)
    for i in range(8):
        ang = math.radians(20 + i * 20 + 5)
        ex, ey = 50 - math.cos(ang) * 44, 74 + math.sin(ang) * 22 - 10
        sway = math.sin(a.t * 1.57 + i) * 3
        a.taper([(50 + (ex - 50) * 0.15, 66), (50 + (ex - 50) * 0.55, 76 + sway), (ex + sway, ey + 14)], 9, 2, sh(c, -10 + (i % 2) * 18))
        if i % 2 == 0:
            a.ell(50 + (ex - 50) * 0.55, 76 + sway, 1.5, 1.5, sh(c, 60), ol=False)
    a.ell(50, 44, 28, 26, sh(c, -5), shine=True)
    a.ell(50, 44, 21, 19, (245, 242, 230))
    a.glow(50, 44, 12, eye, 0.55)
    a.ell(50, 44, 11, 11, eye, ol=False)
    a.ell(50, 44, 3.8 + a.t % 2, 10.5, (20, 5, 25), ol=False)
    a.ell(47, 40, 2.2, 2.2, (255, 255, 255), ol=False)
    for ang in (0.2, 1.2, 2.0, 2.9, 3.8, 4.7, 5.5):
        a.line((50 + math.cos(ang) * 16, 44 + math.sin(ang) * 14), (50 + math.cos(ang) * 20, 44 + math.sin(ang) * 18), 0.5, (200, 60, 70))
    a.poly([(30, 62), (70, 62), (64, 76), (50, 70), (36, 76)], (25, 10, 35))
    for i in range(6):
        a.poly([(34 + i * 6, 62), (38 + i * 6, 62), (36 + i * 6, 68)], (245, 240, 230), ol=False)
    for ex, ey in ((22, 36), (78, 38), (30, 24), (70, 22)):
        a.ell(ex, ey, 3.2, 3.2, (245, 242, 230), w=0.7)
        a.ell(ex, ey, 1.4, 1.4, eye, ol=False)


def parasite(a, c, eye):
    a.glow(50, 54, 46, c, 0.35)
    for i in range(8):
        ang = i * math.pi / 4 + a.t * 0.08
        a.taper([(50 + math.cos(ang) * 14, 54 + math.sin(ang) * 14), (50 + math.cos(ang + 0.3) * 30, 54 + math.sin(ang + 0.3) * 30),
                 (50 + math.cos(ang) * 44, 54 + math.sin(ang) * 44)], 7, 1.5, sh(c, -25))
        ex, ey = 50 + math.cos(ang) * 44, 54 + math.sin(ang) * 44
        a.ell(ex, ey, 2.6, 2.6, (250, 245, 255), w=0.7)
        a.ell(ex, ey, 1.2, 1.2, eye, ol=False)
    pts = []
    for i in range(16):
        r = 22 if i % 2 == 0 else 12
        pts.append((50 + math.cos(i * math.pi / 8 - math.pi / 2) * r, 54 + math.sin(i * math.pi / 8 - math.pi / 2) * r))
    a.poly(pts, sh(c, 10))
    a.ell(50, 54, 12, 12, (250, 245, 255))
    a.glow(50, 54, 9, eye, 0.6)
    a.ell(50, 54, 7.2, 7.2, eye, ol=False)
    a.ell(50, 54, 2.4, 6.4, (15, 5, 30), ol=False)
    for i in range(6):
        a.sparkle(14 + (i * 31) % 72, 12 + (i * 47 + a.t * 7) % 80, 1.8, (255, 255, 255))


def phoenix(a, c, eye):
    a.glow(50, 56, 46, (255, 130, 40), 0.35)
    _wings(a, "flame", c, 50, 52, 1.0)
    for i, k in enumerate((-18, -9, 0, 9, 18)):
        a.poly([(50 + k * 0.4 - 4, 74), (50 + k + math.sin(a.t * 1.57 + i) * 2, 98 - abs(k) * 0.4), (50 + k * 0.4 + 4, 74)],
               (255, 100 + i % 3 * 50, 40), ol=(i == 2))
    a.ell(50, 62, 14, 20, c, shine=True)
    a.ell(50, 66, 8, 12, (255, 220, 110), ol=False)
    a.ell(50, 38, 10, 10, c, shine=True)
    for i, k in enumerate((-6, -2, 2, 6)):
        a.poly([(50 + k - 2, 32), (50 + k * 1.6 + math.sin(a.t * 1.57 + i), 14 - (i in (1, 2)) * 5), (50 + k + 2, 32)], (255, 170 + i * 20, 50), ol=False)
    a.poly([(46, 40), (54, 40), (50, 52)], (250, 210, 80))
    a.eyes(50, 36, 5, 1.9, (255, 255, 200))


def dragon(a, c, eye, horn=(235, 228, 205), breath=None, skeletal=False, wing_c=None, big=True):
    _wings(a, "dragon", wing_c or sh(c, -40), 50, 54, 1.0)
    a.poly([(30, 94), (36, 66), (50, 58), (64, 66), (70, 94)], sh(c, -15))
    for i in range(4):
        a.line((38 + i * 8, 70), (38 + i * 8, 92), 0.6, sh(c, -70) if not skeletal else (200, 205, 190))
    for i in range(6):
        a.ell(40 + (i % 3) * 10, 76 + (i // 3) * 8, 3, 2.2, sh(c, 20), ol=False)
    for side in (-1, 1):
        a.curve([(50 + side * 9, 60), (50 + side * 20, 36), (50 + side * 26, 22)], 4, horn, ol=True)
        a.poly([(50 + side * 14, 44), (50 + side * 30, 40), (50 + side * 17, 52)], sh(c, -30))
    a.poly([(30, 38), (70, 38), (74, 56), (60, 70), (40, 70), (26, 56)], c)
    a.poly([(30, 38), (70, 38), (60, 48), (40, 48)], sh(c, 25), ol=False)
    a.poly([(38, 54), (62, 54), (66, 68), (34, 68)], sh(c, 20))
    a.line((50, 36), (50, 52), 0.8, sh(c, -60))
    a.ell(43, 62, 1.8, 1.4, (30, 20, 25), ol=False)
    a.ell(57, 62, 1.8, 1.4, (30, 20, 25), ol=False)
    a.eyes(50, 46, 9, 3.0, eye, slit=True, angry=True)
    a.poly([(36, 68), (64, 68), (60, 76), (40, 76)], (35, 12, 18))
    for i in range(7):
        a.poly([(38 + i * 4.2 - 1.2, 68), (38 + i * 4.2 + 1.2, 68), (38 + i * 4.2, 73)], (250, 248, 236), ol=False)
    if breath:
        a.glow(50, 78, 14, breath, 0.6)
        for i in range(3):
            a.poly([(44 + i * 6 - 3, 74), (44 + i * 6 + math.sin(a.t * 1.57 + i) * 1.5, 88 + i % 2 * 5), (44 + i * 6 + 3, 74)], mix(breath, (255, 240, 150), 0.4), ol=False)
    if skeletal:
        for i in range(4):
            a.curve([(50, 62 + i * 7), (38 - i, 66 + i * 7), (34 - i * 2, 74 + i * 7)], 1.3, (225, 228, 210), ol=False)
            a.curve([(50, 62 + i * 7), (62 + i, 66 + i * 7), (66 + i * 2, 74 + i * 7)], 1.3, (225, 228, 210), ol=False)


def thunderbird(a, c, eye):
    a.glow(50, 50, 44, (255, 240, 120), 0.3)
    flap = (0, 4, 8, 4)[a.t]
    for side in (-1, 1):
        for i in range(7):
            k = i / 6
            tip = (50 + side * (46 - i * 3), 18 + i * 8 - flap * (1 - k))
            a.poly([(50 + side * 8, 44 + i * 2), (tip[0], tip[1] - 3), (tip[0] + side * 2, tip[1] + 6), (50 + side * 10, 52 + i * 3)],
                   sh(c, -10 * i + 20) if i < 6 else sh(c, -40))
    a.poly([(38, 90), (44, 62), (56, 62), (62, 90)], sh(c, -15))
    for side in (-1, 1):
        for k in (-1, 0, 1):
            a.poly([(50 + side * 6 + k * 3 - 1.2, 90), (50 + side * 6 + k * 3 + 1.2, 90), (50 + side * 6 + k * 3, 97)], (240, 200, 80), ol=False)
    a.ell(50, 58, 15, 22, c, shine=True)
    a.ell(50, 64, 9, 14, sh(c, 40), ol=False)
    a.ell(50, 36, 12, 11, c, shine=True)
    for i, k in enumerate((-6, -2, 2, 6)):
        a.poly([(50 + k - 2, 28), (50 + k * 1.5, 12 - (i in (1, 2)) * 5), (50 + k + 2, 28)], sh(c, 30), ol=True)
    a.poly([(44, 38), (56, 38), (50, 54)], (250, 195, 70))
    a.eyes(50, 34, 6, 2.2, (255, 255, 255), angry=True)
    zig = [(8, 70), (18, 62), (14, 54), (26, 48)]
    for side in (-1, 1):
        a.curve([(50 + side * (x - 50) * -1 if False else (50 + side * (50 - x)), y) for x, y in zig], 1.3, (255, 255, 200), ol=False)


def serpent(a, c, eye, ring=False, frost=False):
    gold = (240, 205, 80)
    if ring:
        a.glow(50, 54, 44, c, 0.3)
        pts = []
        for i in range(34):
            ang = math.radians(-60 + i * 10.5 + a.t * 3)
            pts.append((50 + math.cos(ang) * 34, 56 + math.sin(ang) * 34))
        for i, (x, y) in enumerate(pts):
            w = 5 + 6 * math.sin(math.pi * i / 33)
            a.ell(x, y, w, w, sh(c, -30 + (i % 2) * 18), w=0.8)
            a.ell(x, y, w * 0.5, w * 0.5, sh(c, 20), ol=False)
        hx, hy = pts[-1]
        a.poly([(hx - 6, hy - 6), (hx + 10, hy - 4), (hx + 12, hy + 6), (hx - 4, hy + 8)], sh(c, 10))
        for k in (-1, 1):
            a.poly([(hx - 3, hy - 6 + k * 0), (hx - 10, hy - 14), (hx + 2, hy - 7)], gold)
        a.eyes(hx + 3, hy - 1, 4, 1.8, (255, 255, 200), slit=True)
        for i in range(8):
            ang = math.radians(i * 45 + a.t * 11)
            a.sparkle(50 + math.cos(ang) * 22, 56 + math.sin(ang) * 22, 2.2, gold)
        return
    body = []
    for i in range(26):
        k = i / 25
        body.append((50 + math.sin(k * 6.5 + a.t * 0.3) * 24 * (0.4 + k * 0.6), 94 - k * 62))
    for i, (x, y) in enumerate(body):
        w = 15 - i * 0.28
        a.ell(x, y, w / 2, w / 2, sh(c, -22 + (i % 2) * 14), w=0.8)
        if i % 3 == 0:
            a.poly([(x - 1.5, y - w / 2), (x, y - w / 2 - 4), (x + 1.5, y - w / 2)], sh(c, 45), ol=False)
    hx, hy = body[-1]
    a.poly([(hx - 12, hy + 4), (hx - 2, hy - 12), (hx + 14, hy - 6), (hx + 16, hy + 4), (hx + 2, hy + 12)], c)
    for side in (-1, 1):
        a.poly([(hx + side * 4, hy - 6), (hx + side * 14, hy - 20), (hx + side * 8, hy - 4)], (230, 245, 255) if frost else gold)
    a.eyes(hx + 2, hy - 1, 5, 2.2, eye, slit=True, angry=True)
    for k in (-1, 1):
        a.poly([(hx + k * 4 - 1, hy + 8), (hx + k * 4 + 1, hy + 8), (hx + k * 4, hy + 13)], (250, 250, 245), ol=False)
    if frost:
        for i in range(6):
            a.sparkle(14 + (i * 31) % 72, 18 + (i * 41 + a.t * 7) % 70, 2.2, (235, 250, 255))


def golem_big(a, c, eye, kind="bone", rune=(255, 200, 80)):
    if kind == "bone":
        bone = (222, 214, 190)
        for bx, by, r in ((18, 92, 5), (30, 95, 4), (72, 94, 5), (84, 91, 4)):                       # ossos no chão
            a.line((bx - r, by), (bx + r, by - 2), 2.2, bone)
        for side in (-1, 1):
            a.line((50 + side * 12, 74), (50 + side * 14, 92), 6, bone)
            a.ell(50 + side * 14, 93, 7, 3.4, sh(bone, -15))
            a.line((50 + side * 28, 50), (50 + side * 36, 66), 5.2, bone)
            a.line((50 + side * 36, 66), (50 + side * 34, 82), 4.6, bone)
            a.ell(50 + side * 34, 84, 6.5, 6.5, sh(bone, -8), shine=True)
            a.ell(50 + side * 26, 46, 8.5, 7.5, sh(bone, -10), shine=True)
            _skull(a, 50 + side * 26, 46, 4.2, bone, eye)
        a.rect(36, 66, 64, 76, sh(bone, -15), r=3)
        a.line((50, 36), (50, 70), 3, sh(bone, -25))
        for i in range(5):
            y = 44 + i * 6.5
            w = 20 - abs(i - 1.5) * 2.6
            a.curve([(50, y), (50 - w, y + 1), (50 - w + 3, y + 6)], 2.4, bone, ol=True)
            a.curve([(50, y), (50 + w, y + 1), (50 + w - 3, y + 6)], 2.4, bone, ol=True)
        a.glow(50, 56, 14, eye, 0.28)
        _skull(a, 50, 28, 14, bone, eye)
        for side in (-1, 1):
            a.poly([(50 + side * 11, 18), (50 + side * 20, 6), (50 + side * 15, 22)], sh(bone, -20))
    else:  # titan
        stone = sh(c, -45)
        for side in (-1, 1):
            a.rect(50 + side * 14 - 8, 70, 50 + side * 14 + 8, 94, sh(stone, -10), r=3)
            a.rect(50 + side * 14 - 10, 88, 50 + side * 14 + 10, 95, sh(stone, -25), r=2)
        a.rect(26, 34, 74, 76, stone, r=6)
        for pts in (((34, 40), (40, 52), (36, 64)), ((64, 38), (60, 50), (68, 62))):
            a.curve(list(pts), 1.0, sh(stone, -75), ol=False)
        a.glow(50, 56, 15, rune, 0.4)
        for y in (48, 56, 64):
            a.line((38, y), (62, y), 1.1, rune)
        a.line((50, 44), (50, 68), 1.1, rune)
        for side in (-1, 1):
            a.ell(50 + side * 28, 40, 12, 10, sh(stone, 12), shine=True)
            a.curve([(50 + side * 30, 46), (50 + side * 36, 62), (50 + side * 33, 76)], 9, sh(stone, -5), ol=True)
            a.rect(50 + side * 33 - 8, 74, 50 + side * 33 + 8, 88, sh(stone, 10), r=3)
            a.line((50 + side * 33 - 4, 76), (50 + side * 33 - 3, 86), 0.8, sh(stone, -75))
            a.ell(50 + side * 22, 33, 3, 2.2, (110, 150, 80), ol=False)
        a.rect(36, 12, 64, 36, sh(stone, 12), r=4)
        a.rect(40, 20, 60, 26, (20, 15, 20), r=1.2)
        a.glow(50, 23, 13, rune, 0.5)
        a.line((42, 23), (48, 23), 2.0, rune)
        a.line((52, 23), (58, 23), 2.0, rune)
        for i, (fx, fy) in enumerate(((14, 28), (86, 34), (20, 62), (82, 60))):
            a.poly([(fx - 4, fy), (fx, fy - 4 - (a.t + i) % 2 * 1.5), (fx + 4, fy), (fx + 1, fy + 5)], sh(stone, 15))


# ======================================================================
# RECEITAS: cada criatura = (plano de corpo, escala, super?)
#   a = pincel, c = cor do JSON (campo "color"); eye = cor dos olhos
# ======================================================================
def _empress(a, c):
    save, a.dy = a.dy, 0.0
    a.ell(50, 30, 24, 24, (230, 200, 255), ol=False, alpha=0)
    a.curve([(50 + math.cos(math.radians(t)) * 25, 32 + math.sin(math.radians(t)) * 25) for t in range(0, 361, 20)], 1.6, (225, 190, 255), ol=False)
    a.dy = save
    humanoid(a, (70, 40, 110), (170, 100, 250), (240, 200, 255), head="crown", weapon="staff", robe=True,
             cape=(30, 15, 60), extras=("stars",), skin=(215, 195, 235), bulk=1.0)


SPRITES = {
    # ---- inimigos (faixa 1) ----
    "vampire_bat": lambda a, c: bat(a, c, sh(c, -35), (255, 70, 80)),
    "slime_green": lambda a, c: slime(a, c, (20, 25, 20), acid=True),
    "skeleton_archer": lambda a, c: humanoid(a, (95, 80, 65), (150, 120, 80), (120, 255, 170), head="skull", weapon="bow", extras=("belt_skulls",)),
    "dire_wolf": lambda a, c: wolf(a, c, (255, 200, 60)),
    "spore_mushroom": lambda a, c: mushroom(a, c, (30, 20, 30)),
    "imp_flame": lambda a, c: imp(a, c, (255, 235, 70)),
    # ---- faixa 2 ----
    "wail_ghost": lambda a, c: ghost(a, c, mouth=1.0),
    "giant_scorpion": lambda a, c: scorpion(a, c, (255, 60, 60)),
    "shadow_thief": lambda a, c: humanoid(a, c, (170, 60, 90), (255, 230, 120), head="hood", weapon="dagger", extras=("shadow",)),
    "elder_sapling": lambda a, c: treant(a, c, (255, 230, 120), big=False),
    "harpy": lambda a, c: humanoid(a, c, (240, 200, 90), (255, 230, 120), head="human", wings="feather", wing_c=(205, 150, 190),
                                   extras=("talons",), skin=(225, 190, 160), weapon=None),
    "minotaur": lambda a, c: humanoid(a, (110, 70, 50), (200, 160, 90), (255, 90, 60), head="bull", weapon="axe", skin=(165, 105, 75), bulk=1.2),
    # ---- faixa 3 ----
    "spectral_knight": lambda a, c: ghost(a, c, armor=True),
    "basilisk": lambda a, c: serpent(a, c, (190, 255, 150)),
    "lich_acolyte": lambda a, c: humanoid(a, (45, 95, 85), c, (120, 255, 170), head="skull", weapon="staff", robe=True, extras=("wisps",)),
    "mimic_chest": lambda a, c: mimic(a, c, (255, 230, 90)),
    "frost_elemental": lambda a, c: elemental(a, c, (255, 255, 255), "ice"),
    "magma_elemental": lambda a, c: elemental(a, c, (255, 230, 80), "magma"),
    # ---- faixa 4 ----
    "hydra_spawn": lambda a, c: hydra(a, c, (255, 230, 80), big=False),
    "death_knight": lambda a, c: humanoid(a, c, (150, 90, 210), (200, 120, 255), head="horned", weapon="greatsword", plate=True,
                                          cape=(55, 30, 70), bulk=1.1, extras=("gauntlet",)),
    "banshee": lambda a, c: ghost(a, c, mouth=1.0, hair=True, eye=(255, 255, 255)),
    "chimera": lambda a, c: chimera(a, c, (255, 100, 60)),
    "gorgon": lambda a, c: humanoid(a, (55, 115, 80), (230, 200, 100), (240, 230, 80), head="snakes", robe=True, skin=(150, 190, 130)),
    "werewolf": lambda a, c: humanoid(a, (95, 75, 70), (150, 105, 80), (255, 210, 60), head="wolf", hunch=4, bulk=1.15,
                                      skin=(125, 98, 88), extras=("tail", "gauntlet")),
    # ---- faixa 5 ----
    "abyssal_horror": lambda a, c: horror(a, c, (255, 200, 80)),
    "ash_phoenix": lambda a, c: phoenix(a, c, (255, 255, 200)),
    "dracolich_whelp": lambda a, c: dragon(a, (205, 215, 195), (120, 230, 255), skeletal=True, wing_c=(85, 115, 125), breath=(140, 220, 255)),
    "grim_reaper": lambda a, c: humanoid(a, (45, 45, 70), (130, 130, 170), (150, 255, 200), head="hood", weapon="scythe", robe=True, extras=("wisps",)),
    "arch_demon": lambda a, c: humanoid(a, (140, 30, 45), (255, 150, 60), (255, 230, 70), head="demon", weapon="trident", wings="dragon",
                                        wing_c=(95, 20, 35), skin=(205, 65, 65), bulk=1.25, extras=("tail", "flames")),
    "star_parasite": lambda a, c: parasite(a, c, (255, 230, 120)),
    # ---- bosses do Infinito ----
    "boss_inf_bone_colossus": lambda a, c: golem_big(a, c, (255, 150, 50), "bone"),
    "boss_inf_ember_witch": lambda a, c: humanoid(a, sh(c, -55), (255, 150, 50), (255, 240, 120), head="witch", weapon="staff", robe=True,
                                                   extras=("flames",), skin=(240, 205, 175)),
    "boss_inf_frost_wyrm": lambda a, c: serpent(a, c, (210, 245, 255), frost=True),
    "boss_inf_plague_doctor": lambda a, c: humanoid(a, (60, 75, 55), (150, 180, 90), (170, 255, 150), head="beak", weapon="lantern",
                                                    robe=True, cape=(38, 48, 38), extras=("mist",)),
    "boss_inf_shadow_stalker": lambda a, c: humanoid(a, (45, 40, 75), (150, 105, 230), (255, 70, 120), head="demon", weapon="dagger",
                                                     cape=(25, 20, 45), skin=(70, 55, 105), extras=("shadow", "tail")),
    "boss_inf_stone_hydra": lambda a, c: hydra(a, c, (255, 160, 60), big=True, stone=True),
    "boss_inf_crypt_lord": lambda a, c: humanoid(a, (55, 105, 85), (120, 220, 170), (150, 255, 200), head="hood", weapon="staff",
                                                 robe=True, cape=(28, 58, 52), extras=("souls", "chains")),
    "boss_inf_thunder_roc": lambda a, c: thunderbird(a, c, (255, 255, 255)),
    "boss_inf_blighted_ancient": lambda a, c: treant(a, c, (255, 120, 255), big=True, corrupt=True),
    "boss_inf_iron_warden": lambda a, c: humanoid(a, (110, 115, 130), (190, 195, 210), (255, 160, 60), head="helm", weapon="chain",
                                                  plate=True, bulk=1.3, extras=("chains", "gauntlet")),
    # ---- SUPER BOSSES ----
    "boss_inf_lich_king": lambda a, c: humanoid(a, (30, 70, 70), (90, 230, 170), (130, 255, 190), head="crown", weapon="staff", robe=True,
                                                wings="bat", wing_c=(25, 60, 62), extras=("belt_skulls", "wisps"), bulk=1.25, plate=False),
    "boss_inf_ash_dragon": lambda a, c: dragon(a, (185, 65, 40), (255, 220, 70), horn=(60, 40, 40), breath=(255, 140, 40), wing_c=(110, 35, 30)),
    "boss_inf_ruin_titan": lambda a, c: golem_big(a, c, (255, 200, 80), "titan"),
    "boss_inf_void_empress": lambda a, c: _empress(a, c),
    "boss_inf_world_serpent": lambda a, c: serpent(a, c, (255, 255, 200), ring=True),
}
SUPER_GLOW = {"boss_inf_lich_king": (90, 230, 170), "boss_inf_ash_dragon": (255, 120, 40), "boss_inf_ruin_titan": (255, 200, 80),
              "boss_inf_void_empress": (190, 110, 255), "boss_inf_world_serpent": (240, 205, 80)}


# ======================================================================
# GERAÇÃO
# ======================================================================
def render(name, color, is_boss, frame):
    super_glow = SUPER_GLOW.get(name)
    a = Art(scale=1.0, t=frame, dy=0.0)
    ground_shadow(a, 34 if is_boss else 28)
    if super_glow:
        aura(a, super_glow, 0.62, 50)
        runes(a, super_glow, 42, 6)
    elif is_boss:
        aura(a, color, 0.28, 44)
    a.dy = BOB[frame]
    SPRITES[name](a, tuple(color))
    return a.im.resize((W, W), Image.LANCZOS)


def targets():
    with open(os.path.join(ROOT, "data", "enemies.json"), encoding="utf-8") as f:
        data = json.load(f)
    out = []
    for eid, d in data["enemies"].items():
        if eid in SPRITES:
            out.append((eid, d["color"], False, "enemies"))
    for key, d in data.get("infinite_bosses", {}).items():
        out.append((f"boss_inf_{key}", d["color"], True, "bosses"))
    return out


def save_apng(frames, path):
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=[FRAME_MS] * len(frames), loop=0, optimize=True)


def main():
    sheet = "--sheet" in sys.argv
    items = targets()
    missing = [n for n, *_ in items if n not in SPRITES]
    if missing:
        sys.exit("Sem receita de sprite para: " + ", ".join(missing))
    previews = []
    force = "--forcar" in sys.argv
    for name, color, is_boss, folder in items:
        out_dir = os.path.join(ROOT, "assets", "images", folder)
        if not force and os.path.exists(os.path.join(out_dir, name + ".png")):
            # protege as artes novas (ver tools/aplicar_novas_artes.py); use --forcar para sobrescrever
            print("pulado (já existe)", folder, name)
            continue
        frames = [render(name, color, is_boss, f) for f in range(FRAMES)]
        os.makedirs(out_dir, exist_ok=True)
        save_apng(frames, os.path.join(out_dir, name + ".png"))
        previews.append((name, color, frames))
        print("ok", folder, name)
    if sheet:
        cols, cell = 9, 150
        rows = (len(previews) + cols - 1) // cols
        img = Image.new("RGBA", (cols * cell, rows * (cell + 14)), (14, 14, 22, 255))
        draw = ImageDraw.Draw(img)
        for i, (name, color, frames) in enumerate(previews):
            x, y = (i % cols) * cell, (i // cols) * (cell + 14)
            tile = Image.new("RGBA", (cell - 6, cell - 6), (26, 26, 40, 255))
            ImageDraw.Draw(tile).rounded_rectangle([0, 0, cell - 7, cell - 7], 12, outline=tuple(min(255, v + 20) for v in color) + (255,), width=3)
            f = frames[1].resize((cell - 14, cell - 14), Image.LANCZOS)
            tile.alpha_composite(f, (4, 4))
            img.alpha_composite(tile, (x + 3, y + 3))
            draw.text((x + 5, y + cell - 2), name[:24], fill=(200, 200, 220, 255))
        img.save(os.path.join(ROOT, "tools", "sprites_preview.png"))
        print("folha:", os.path.join("tools", "sprites_preview.png"))


if __name__ == "__main__":
    main()
