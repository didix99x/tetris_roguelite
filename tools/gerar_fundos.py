"""
tools/gerar_fundos.py - gera os FUNDOS dos temas em assets/backgrounds/<tema>/ (1280x720, JPG).

    python tools/gerar_fundos.py            -> cria só os que NÃO existem (não sobrescreve os seus)
    python tools/gerar_fundos.py --force    -> recria todos
Temas: spiders, goblins, mages, golems, bosses, infinite. Cada um tem default.jpg e variacao.jpg.
Para usar o SEU fundo: salve uma imagem (png/jpg, de preferência 1280x720) na pasta do tema.
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1280, 720


def gradient(top, bottom):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(t + (b - t) * k) for t, b in zip(top, bottom)))
    return img


def glow(img, x, y, r, color, alpha=170):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).ellipse([x - r, y - r, x + r, y + r], fill=color + (alpha,))
    layer = layer.filter(ImageFilter.GaussianBlur(r * 0.6))
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"))


def spiders(rng, variant):
    img = gradient((18, 16, 28), (6, 6, 12)) if variant == 0 else gradient((14, 22, 24), (4, 8, 10))
    d = ImageDraw.Draw(img)
    for cx, cy in ((rng.randint(100, 400), rng.randint(0, 120)), (rng.randint(850, 1180), rng.randint(0, 160))):
        for k in range(10):
            a = k * math.pi / 5
            d.line([(cx, cy), (cx + math.cos(a) * 520, cy + math.sin(a) * 520)], fill=(120, 120, 150), width=1)
        for ring in range(1, 9):
            pts = [(cx + math.cos(k * math.pi / 5) * ring * 60, cy + math.sin(k * math.pi / 5) * ring * 60 * 0.97) for k in range(11)]
            d.line(pts, fill=(100, 100, 130), width=1)
    for _ in range(7):
        x, y = rng.randint(40, 1240), rng.randint(60, 260)
        d.line([(x, 0), (x, y)], fill=(110, 110, 140), width=1)
        d.ellipse([x - 9, y - 7, x + 9, y + 9], fill=(8, 8, 14))
        for s in (-1, 1):
            for l in range(3):
                d.line([(x, y + 2), (x + s * (16 + l * 5), y - 8 + l * 7)], fill=(8, 8, 14), width=2)
        d.ellipse([x - 3, y - 2, x - 1, y], fill=(255, 60, 60)); d.ellipse([x + 1, y - 2, x + 3, y], fill=(255, 60, 60))
    glow(img, 640, 700, 420, (60, 90, 120), 70)
    return img


def goblins(rng, variant):
    img = gradient((22, 40, 30), (8, 16, 12)) if variant == 0 else gradient((40, 28, 18), (14, 10, 8))
    d = ImageDraw.Draw(img)
    for layer, (col, base) in enumerate((((16, 30, 22), 470), ((10, 20, 15), 540))):
        pts = [(0, H)] + [(x, base + math.sin(x / 140 + layer * 2 + rng.random()) * 40) for x in range(0, W + 40, 40)] + [(W, H)]
        d.polygon(pts, fill=col)
    for x in (180, 520, 900, 1160):
        y = rng.randint(500, 580)
        d.polygon([(x - 60, y), (x, y - 90), (x + 60, y)], fill=(34, 24, 18))
        d.polygon([(x - 14, y), (x, y - 40), (x + 14, y)], fill=(8, 6, 5))
        glow(img, x, y - 20, 80, (255, 140, 40), 90)
    for x in (80, 700, 1100):
        d.line([(x, 560), (x, 470)], fill=(60, 40, 25), width=5)
        glow(img, x, 462, 60, (255, 170, 60), 150)
        d.ellipse([x - 7, 452, x + 7, 472], fill=(255, 190, 80))
    return img


def mages(rng, variant):
    img = gradient((28, 16, 52), (8, 6, 22)) if variant == 0 else gradient((16, 22, 56), (6, 8, 24))
    d = ImageDraw.Draw(img)
    for _ in range(90):
        x, y, r = rng.randint(0, W), rng.randint(0, 420), rng.choice((1, 1, 2))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(200, 200, 255))
    for x in (120, 360, 920, 1160):
        d.rectangle([x - 22, 150, x + 22, H], fill=(24, 18, 44))
        d.polygon([(x - 34, 150), (x, 60), (x + 34, 150)], fill=(30, 22, 54))
        for yy in range(220, 600, 90):
            d.rectangle([x - 6, yy, x + 6, yy + 26], fill=(255, 220, 130))
    for _ in range(10):
        x, y = rng.randint(240, 1040), rng.randint(60, 420)
        d.polygon([(x, y - 10), (x + 6, y), (x, y + 10), (x - 6, y)], fill=(170, 120, 255))
        glow(img, x, y, 30, (150, 100, 255), 110)
    glow(img, 640, 720, 500, (110, 70, 200), 90)
    return img


def golems(rng, variant):
    img = gradient((52, 44, 38), (16, 12, 10)) if variant == 0 else gradient((40, 46, 52), (12, 14, 16))
    d = ImageDraw.Draw(img)
    for _ in range(14):
        x, y = rng.randint(0, W), rng.randint(300, 700)
        w, h = rng.randint(60, 200), rng.randint(40, 120)
        shade = rng.randint(24, 46)
        d.polygon([(x, y), (x + w * .3, y - h), (x + w, y - h * .6), (x + w * 1.1, y)], fill=(shade, shade - 4, shade - 8))
    for x in (160, 560, 760, 1100):
        h = rng.randint(220, 420)
        d.rectangle([x - 36, 720 - h, x + 36, 720], fill=(58, 50, 44))
        d.rectangle([x - 44, 720 - h - 16, x + 44, 720 - h], fill=(70, 60, 52))
        for k in range(3):
            d.line([(x - 14, 720 - h + 30 + k * 40), (x + 14, 720 - h + 40 + k * 40)], fill=(255, 150, 50), width=2)
    glow(img, 640, 380, 300, (255, 130, 40), 45)
    return img


def bosses(rng, variant):
    img = gradient((60, 10, 14), (10, 2, 4)) if variant == 0 else gradient((40, 8, 40), (8, 2, 10))
    d = ImageDraw.Draw(img)
    for x in range(60, W, 230):
        d.rectangle([x - 34, 0, x + 34, H], fill=(24, 6, 8))
        d.rectangle([x - 44, 0, x + 44, 40], fill=(34, 10, 12))
        glow(img, x, 300, 80, (255, 60, 40), 70)
    for k in range(5):
        x = 140 + k * 250
        d.ellipse([x - 16, 640, x + 16, 676], fill=(150, 140, 120))
        d.ellipse([x - 8, 652, x - 3, 660], fill=(10, 4, 4)); d.ellipse([x + 3, 652, x + 8, 660], fill=(10, 4, 4))
    glow(img, 640, 0, 380, (255, 40, 30), 110)
    return img


def infinite(rng, variant):
    img = gradient((10, 8, 34), (2, 2, 10)) if variant == 0 else gradient((24, 6, 40), (4, 2, 12))
    d = ImageDraw.Draw(img)
    for _ in range(160):
        x, y, r = rng.randint(0, W), rng.randint(0, H), rng.choice((1, 1, 2, 3))
        d.ellipse([x - r, y - r, x + r, y + r], fill=(rng.randint(160, 255), rng.randint(160, 255), 255))
    for arm in range(3):
        pts = []
        for t in range(0, 360, 4):
            rad = t * 1.1
            a = math.radians(t * 1.6 + arm * 120)
            pts.append((640 + math.cos(a) * rad, 330 + math.sin(a) * rad * 0.6))
        d.line(pts, fill=(120, 80, 220), width=3)
    glow(img, 640, 330, 220, (140, 90, 255), 120)
    glow(img, 640, 330, 70, (255, 255, 255), 160)
    return img


THEMES = {"spiders": spiders, "goblins": goblins, "mages": mages, "golems": golems, "bosses": bosses, "infinite": infinite}


def main():
    force = "--force" in sys.argv
    made = 0
    for name, fn in THEMES.items():
        folder = os.path.join(ROOT, "assets", "backgrounds", name)
        os.makedirs(folder, exist_ok=True)
        for variant, fname in enumerate(("default.jpg", "variacao.jpg")):
            path = os.path.join(folder, fname)
            if force or not os.path.exists(path):
                fn(random.Random(f"{name}{variant}"), variant).save(path, quality=84, optimize=True)
                made += 1
    print(f"{made} fundo(s) criado(s).")


if __name__ == "__main__":
    main()
