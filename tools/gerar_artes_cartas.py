"""
tools/gerar_artes_cartas.py - gera a ARTE DE CADA CARTA em assets/cards/<raridade>/<id_da_carta>.png

    python tools/gerar_artes_cartas.py            -> cria/atualiza os arquivos que NÃO existem ainda (não sobrescreve a sua arte)
    python tools/gerar_artes_cartas.py --force    -> recria TODAS (cuidado: apaga arte que você tenha trocado)
    python tools/gerar_artes_cartas.py --sheet    -> também grava tools/cartas_preview.png

O motivo do desenho vem de (1) o campo "art" da carta em data/rewards.json, se existir, ou (2) do efeito principal da carta.
Cada carta tem variações próprias (cores, brilhos, detalhes) sorteadas a partir do id, então nenhuma é igual a outra.
Para usar uma arte SUA: salve o arquivo com o mesmo nome (ex.: assets/cards/epic/s_inferno.png): o jogo usa o que estiver lá.
"""
import colorsys
import json
import math
import os
import random
import sys
import zlib

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from tools.gerar_sprites import Art, mix, sh, _skull  # noqa: E402

SIZE = 200
RARITIES = ("common", "rare", "epic", "legendary")

PALETTES = {  # motivo: (fundo topo, fundo base, cor principal, cor de destaque)
    "flame": ((70, 20, 10), (20, 8, 6), (255, 110, 40), (255, 220, 100)), "ice": ((15, 40, 70), (6, 14, 30), (130, 210, 255), (230, 250, 255)),
    "heal": ((15, 55, 35), (6, 22, 16), (90, 230, 130), (230, 255, 200)), "shield": ((25, 35, 70), (10, 14, 32), (110, 150, 230), (220, 230, 255)),
    "poison": ((40, 15, 60), (16, 8, 26), (150, 230, 80), (200, 120, 255)), "speed": ((15, 50, 60), (6, 20, 26), (90, 230, 220), (230, 255, 250)),
    "star": ((60, 45, 10), (24, 16, 6), (255, 210, 70), (255, 250, 200)), "sword": ((45, 45, 60), (16, 16, 26), (210, 220, 240), (255, 180, 90)),
    "bolt": ((20, 30, 70), (8, 10, 30), (255, 230, 80), (150, 200, 255)), "rune": ((40, 20, 70), (14, 8, 30), (170, 120, 255), (255, 230, 150)),
    "crown": ((70, 50, 10), (26, 18, 6), (255, 200, 60), (255, 90, 90)), "tower": ((40, 40, 50), (14, 14, 22), (190, 170, 130), (255, 210, 90)),
    "dice": ((55, 20, 30), (22, 8, 12), (240, 235, 225), (220, 60, 70)), "thorns": ((45, 30, 20), (18, 12, 8), (190, 140, 90), (255, 90, 70)),
    "clock": ((30, 40, 60), (10, 14, 26), (150, 190, 230), (255, 220, 120)), "eye": ((50, 20, 50), (20, 8, 22), (255, 120, 200), (255, 240, 160)),
    "links": ((30, 40, 45), (10, 14, 18), (190, 200, 215), (255, 200, 100)), "fang": ((60, 15, 25), (24, 6, 10), (235, 230, 225), (230, 40, 60)),
    "heart": ((70, 15, 30), (26, 6, 12), (240, 70, 100), (255, 200, 210)), "feather": ((70, 35, 10), (26, 12, 6), (255, 150, 50), (255, 230, 120)),
    "hammer": ((45, 40, 40), (18, 14, 14), (170, 175, 190), (255, 150, 60)), "bow": ((20, 50, 30), (8, 20, 12), (150, 220, 100), (240, 220, 160)),
    "book": ((35, 25, 70), (12, 10, 30), (130, 110, 230), (255, 230, 150)), "palm": ((65, 40, 15), (26, 16, 6), (255, 170, 70), (255, 240, 200)),
    "katana": ((50, 15, 20), (20, 6, 8), (220, 225, 235), (220, 50, 60)), "scales": ((60, 50, 15), (24, 20, 6), (255, 215, 90), (255, 250, 200)),
    "daggers": ((35, 20, 55), (14, 8, 22), (200, 200, 220), (190, 90, 255)), "notes": ((15, 55, 45), (6, 22, 18), (90, 230, 170), (220, 255, 240)),
    "halo": ((70, 65, 30), (26, 24, 12), (255, 245, 180), (255, 255, 255)), "axe": ((55, 30, 25), (22, 12, 10), (190, 195, 210), (230, 110, 60)),
    "skull": ((35, 35, 45), (14, 14, 20), (232, 226, 205), (255, 80, 80)), "wind": ((25, 50, 65), (10, 20, 28), (170, 230, 250), (255, 255, 255)),
    "burst": ((70, 30, 10), (26, 12, 6), (255, 160, 50), (255, 240, 150)),
}

# efeito principal -> motivo (a primeira regra que combinar vence)
EFFECT_MOTIF = (("second_wind_pct", "feather"), ("thorns_pct", "thorns"), ("boss_damage_pct", "crown"), ("boss_cooldown_pct", "crown"),
                ("execute_damage_pct", "eye"), ("opener_damage_pct", "eye"), ("momentum_pct", "wind"), ("floor_damage_pct", "tower"),
                ("floor_heal_pct", "tower"), ("crit_chance", "star"), ("crit_damage_pct", "star"), ("crit_energy", "star"), ("crit_heal", "star"),
                ("quick_damage_pct", "speed"), ("chain_damage_pct", "links"), ("chain_start", "links"), ("chain_energy", "links"),
                ("chain3_heal", "links"), ("big_match_damage_pct", "burst"), ("explosion_match5", "burst"), ("explosion_chain", "burst"),
                ("ability_power_pct", "rune"), ("ability_cost_pct", "rune"), ("ability_refund_pct", "rune"), ("ability_heal", "rune"),
                ("energy_gain_pct", "bolt"), ("energy", "bolt"), ("lifesteal_pct", "fang"), ("regen_per_sec", "heal"), ("heal_pct", "heal"),
                ("match_heal", "heal"), ("max_hp", "heart"), ("damage_reduction_pct", "shield"), ("block_chance", "shield"),
                ("status_resist_pct", "shield"), ("enemy_cooldown_pct", "clock"), ("low_hp_damage_pct", "skull"), ("damage_pct", "sword"))


def motif_for(card):
    if card.get("art") in PALETTES:
        return card["art"]
    kinds = [e["type"] for e in card.get("effects", [])]
    for effect, motif in EFFECT_MOTIF:
        if effect in kinds:
            return motif
    return "rune"


def _hue(color, delta):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in color))
    return tuple(int(c * 255) for c in colorsys.hsv_to_rgb((h + delta) % 1.0, s, v))


def _ring(a, cx, cy, rx, ry, w, color, start=0.0, end=math.tau, steps=40):
    pts = [(cx + math.cos(start + (end - start) * i / steps) * rx, cy + math.sin(start + (end - start) * i / steps) * ry) for i in range(steps + 1)]
    a.curve(pts, w, color)


def _rot(pts, ang, cx=50, cy=50):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(cx + (x - cx) * ca - (y - cy) * sa, cy + (x - cx) * sa + (y - cy) * ca) for x, y in pts]


# ---------------------------------------------------------------- motivos (cada um desenha no centro da grade 0..100)
def m_flame(a, r, c, k):
    for i, (col, s) in enumerate(((c, 1.0), (mix(c, k, .5), .72), (k, .45))):
        sway = r.uniform(-6, 6) * (1 - i * .3)
        pts = [(50 + sway, 10 + i * 14), (66, 42), (72, 68), (50, 88), (28, 68), (34, 42)]
        a.poly([(50 + (x - 50) * s, 88 + (y - 88) * s) for x, y in pts], col, ol=(i == 0))
    for _ in range(r.randint(3, 6)):
        a.sparkle(r.uniform(20, 80), r.uniform(10, 60), r.uniform(1.5, 3), k)


def m_ice(a, r, c, k):
    for i in range(r.randint(3, 4)):
        ang = (i - 1) * 0.55 + r.uniform(-.1, .1)
        pts = _rot([(50, 14), (60, 36), (57, 86), (43, 86), (40, 36)], ang, 50, 86)
        a.poly(pts, mix(c, (255, 255, 255), .15 * i) if i else c)
        a.line(_rot([(50, 20)], ang, 50, 86)[0], _rot([(50, 84)], ang, 50, 86)[0], 0.7, sh(c, -70))
    for ang in range(6):
        t = ang * math.pi / 3
        a.line((50 + math.cos(t) * 6, 36 + math.sin(t) * 6), (50 + math.cos(t) * 18, 36 + math.sin(t) * 18), 1.2, k)
    for _ in range(5):
        a.sparkle(r.uniform(12, 88), r.uniform(10, 70), r.uniform(1.5, 3), k)


def m_heal(a, r, c, k):
    a.glow(50, 50, 38, c, .5)
    a.rect(40, 18, 60, 82, c, r=4)
    a.rect(18, 40, 82, 60, c, r=4)
    a.rect(44, 24, 56, 76, mix(c, k, .5), r=3, ol=False)
    for s in (-1, 1):
        for y in (22, 78):
            a.ell(50 + s * r.uniform(24, 32), y + (6 if y > 50 else -6), 7, 4, sh(c, -20), shine=True)
    for _ in range(r.randint(3, 6)):
        a.sparkle(r.uniform(14, 86), r.uniform(10, 90), r.uniform(1.5, 2.8), k)


def m_shield(a, r, c, k):
    a.poly([(20, 18), (80, 18), (78, 56), (50, 88), (22, 56)], c)
    a.poly([(27, 25), (73, 25), (71, 54), (50, 78), (29, 54)], mix(c, (20, 20, 40), .45), ol=False)
    emblem = r.choice(("star", "cross", "gem"))
    if emblem == "cross":
        a.rect(46, 30, 54, 70, k, r=1.5); a.rect(36, 42, 64, 50, k, r=1.5)
    elif emblem == "gem":
        a.poly([(50, 32), (62, 48), (50, 68), (38, 48)], k)
    else:
        a.sparkle(50, 50, 18, k)
    a.line((22, 22), (78, 22), 1.4, mix(c, (255, 255, 255), .5))


def m_poison(a, r, c, k):
    a.rect(42, 14, 58, 30, (150, 110, 70), r=2)
    a.rect(38, 28, 62, 40, sh(k, -40), r=2)
    a.ell(50, 62, 28, 26, (200, 220, 230), ol=True)
    a.ell(50, 66, 24, 20, c)
    a.ell(40, 56, 6, 4, (255, 255, 255), ol=False, alpha=160)
    for _ in range(r.randint(3, 5)):
        a.ell(r.uniform(38, 62), r.uniform(56, 76), r.uniform(2, 4), r.uniform(2, 4), mix(c, (255, 255, 255), .5), alpha=200)
    for i in range(3):
        a.ell(26 + i * 24, 90 - i % 2 * 4, 3, 3, k)


def m_speed(a, r, c, k):
    for i in range(3):
        x = 16 + i * 24
        a.poly([(x, 24), (x + 22, 50), (x, 76), (x + 10, 76), (x + 32, 50), (x + 10, 24)], mix(c, k, i * .25))
    for _ in range(5):
        y = r.uniform(18, 82)
        a.line((r.uniform(4, 20), y), (r.uniform(30, 55), y), 1.2, k)


def m_star(a, r, c, k):
    a.glow(50, 50, 40, c, .55)
    n = r.choice((8, 10, 12))
    pts = []
    for i in range(n * 2):
        rad = 44 if i % 2 == 0 else 17
        ang = i * math.pi / n - math.pi / 2
        pts.append((50 + math.cos(ang) * rad, 50 + math.sin(ang) * rad))
    a.poly(pts, c)
    a.ell(50, 50, 13, 13, k, shine=True)
    for _ in range(4):
        a.sparkle(r.uniform(10, 90), r.uniform(10, 90), r.uniform(1.5, 3), k)


def m_sword(a, r, c, k):
    a.glow(50, 50, 40, k, .35)
    a.poly(_rot([(46, 8), (54, 8), (56, 64), (44, 64)], .75), c)
    a.poly(_rot([(34, 62), (66, 62), (66, 70), (34, 70)], .75), k)
    a.rect(*(_rot([(46, 70)], .75)[0]), *(_rot([(54, 86)], .75)[0]), (110, 70, 45), r=2) if False else a.line(*_rot([(50, 70), (50, 86)], .75), 5, (110, 70, 45))
    a.ell(*_rot([(50, 88)], .75)[0], 5, 5, k, shine=True)
    for _ in range(4):
        a.sparkle(r.uniform(15, 85), r.uniform(10, 60), r.uniform(1.5, 3), k)


def m_bolt(a, r, c, k):
    a.glow(50, 50, 40, c, .5)
    a.poly([(58, 6), (24, 54), (46, 54), (38, 94), (78, 40), (54, 40)], c)
    a.poly([(56, 14), (34, 52), (50, 52), (44, 80), (68, 42), (52, 42)], mix(c, (255, 255, 255), .6), ol=False)
    for _ in range(5):
        a.sparkle(r.uniform(10, 90), r.uniform(10, 90), r.uniform(1.5, 3), k)


def m_rune(a, r, c, k):
    a.glow(50, 50, 40, c, .5)
    _ring(a, 50, 50, 38, 38, 2.2, c)
    _ring(a, 50, 50, 30, 30, 1.2, k)
    n = r.choice((5, 6, 7))
    for i in range(n):
        a1, a2 = i * math.tau / n - 1.57, (i + 2) * math.tau / n - 1.57
        a.line((50 + math.cos(a1) * 30, 50 + math.sin(a1) * 30), (50 + math.cos(a2) * 30, 50 + math.sin(a2) * 30), 1.6, c)
        a.ell(50 + math.cos(a1) * 38, 50 + math.sin(a1) * 38, 3, 3, k)
    a.sparkle(50, 50, 10, k)


def m_crown(a, r, c, k):
    a.glow(50, 54, 38, c, .4)
    a.poly([(16, 76), (12, 30), (32, 52), (50, 20), (68, 52), (88, 30), (84, 76)], c)
    a.rect(16, 74, 84, 86, sh(c, -30), r=2)
    for x, col in ((50, k), (28, (90, 200, 255)), (72, (90, 255, 160))):
        a.ell(x, 62 if x == 50 else 66, 5, 5, col, shine=True)
    for x in (12, 50, 88):
        a.ell(x, 28 if x != 50 else 18, 4, 4, k)


def m_tower(a, r, c, k):
    for i in range(4):
        w = 52 - i * 10
        a.rect(50 - w / 2, 80 - i * 16, 50 + w / 2, 94 - i * 16, mix(c, (30, 30, 50), i * .12), r=2)
    a.line((50, 16), (50, 30), 1.4, (150, 110, 70))
    a.poly([(50, 14), (70, 20), (50, 26)], k)
    for i in range(3):
        a.rect(40 + i * 8 - 1.5, 62 - i * 16, 40 + i * 8 + 1.5, 70 - i * 16, k, r=1, ol=False)
    for _ in range(4):
        a.sparkle(r.uniform(12, 88), r.uniform(8, 60), r.uniform(1.5, 2.6), k)


def m_dice(a, r, c, k):
    for (cx, cy, ang, n) in ((36, 58, -.25, r.randint(2, 6)), (66, 44, .3, r.randint(1, 6))):
        a.poly(_rot([(cx - 18, cy - 18), (cx + 18, cy - 18), (cx + 18, cy + 18), (cx - 18, cy + 18)], ang, cx, cy), c)
        spots = {1: [(0, 0)], 2: [(-8, -8), (8, 8)], 3: [(-9, -9), (0, 0), (9, 9)], 4: [(-8, -8), (8, -8), (-8, 8), (8, 8)],
                 5: [(-9, -9), (9, -9), (0, 0), (-9, 9), (9, 9)], 6: [(-8, -9), (8, -9), (-8, 0), (8, 0), (-8, 9), (8, 9)]}[n]
        for dx, dy in spots:
            px, py = _rot([(cx + dx, cy + dy)], ang, cx, cy)[0]
            a.ell(px, py, 3.2, 3.2, k, ol=False)


def m_thorns(a, r, c, k):
    n = r.randint(10, 14)
    for i in range(n):
        ang = i * math.tau / n
        a.poly([(50 + math.cos(ang - .14) * 30, 50 + math.sin(ang - .14) * 30), (50 + math.cos(ang) * 46, 50 + math.sin(ang) * 46),
                (50 + math.cos(ang + .14) * 30, 50 + math.sin(ang + .14) * 30)], c)
    a.ell(50, 50, 28, 28, mix(c, (30, 20, 20), .4))
    a.ell(50, 50, 14, 14, k, shine=True)


def m_clock(a, r, c, k):
    a.glow(50, 50, 40, c, .35)
    a.ell(50, 50, 38, 38, mix(c, (20, 24, 40), .55))
    _ring(a, 50, 50, 38, 38, 2.4, c)
    for i in range(12):
        ang = i * math.pi / 6
        a.line((50 + math.cos(ang) * 31, 50 + math.sin(ang) * 31), (50 + math.cos(ang) * 35, 50 + math.sin(ang) * 35), 1.4, k)
    h = r.uniform(0, math.tau)
    a.line((50, 50), (50 + math.cos(h) * 20, 50 + math.sin(h) * 20), 2.2, k)
    a.line((50, 50), (50 + math.cos(h + 2) * 28, 50 + math.sin(h + 2) * 28), 1.6, c)
    a.ell(50, 50, 3, 3, k)


def m_eye(a, r, c, k):
    a.glow(50, 50, 40, c, .4)
    a.poly([(8, 50), (30, 28), (70, 28), (92, 50), (70, 72), (30, 72)], (240, 235, 230))
    a.ell(50, 50, 20, 20, c, shine=True)
    a.ell(50, 50, 9, 18, (20, 10, 20), ol=False)
    for ang in range(8):
        t = ang * math.pi / 4 + .2
        a.line((50 + math.cos(t) * 40, 50 + math.sin(t) * 28), (50 + math.cos(t) * 48, 50 + math.sin(t) * 36), 1.4, k)


def m_links(a, r, c, k):
    for i, (cx, cy, rx, ry) in enumerate(((34, 38, 22, 14), (66, 50, 22, 14), (34, 64, 22, 14))):
        _ring(a, cx, cy, rx, ry, 5.5, sh(c, -30 + i * 20))
        _ring(a, cx, cy, rx, ry, 2.4, mix(c, (255, 255, 255), .5))
    a.sparkle(r.uniform(60, 80), r.uniform(20, 30), 4, k)
    a.sparkle(r.uniform(18, 30), r.uniform(70, 84), 3, k)


def m_fang(a, r, c, k):
    for s in (-1, 1):
        a.poly([(50 + s * 24, 18), (50 + s * 8, 26), (50 + s * 14, 74), (50 + s * 22, 40)], c)
    a.poly([(50, 62), (60, 76), (50, 90), (40, 76)], k)
    a.ell(50, 80, 5, 4, mix(k, (255, 255, 255), .3), ol=False)
    for _ in range(3):
        a.ell(r.uniform(30, 70), r.uniform(80, 94), 2.5, 2.5, k, ol=False)


def m_heart(a, r, c, k):
    a.glow(50, 52, 38, c, .5)
    a.ell(36, 38, 18, 18, c, shine=True)
    a.ell(64, 38, 18, 18, c, shine=True)
    a.poly([(19, 46), (81, 46), (50, 88)], c)
    a.ell(36, 34, 5, 3, k, ol=False, alpha=190)
    for _ in range(4):
        a.sparkle(r.uniform(10, 90), r.uniform(10, 90), r.uniform(1.5, 2.6), k)


def m_feather(a, r, c, k):
    a.glow(50, 50, 40, c, .5)
    for i, (col, s) in enumerate(((c, 1), (mix(c, k, .5), .7), (k, .42))):
        pts = _rot([(50, 6), (68, 30), (66, 62), (50, 90), (34, 62), (32, 30)], -.35, 50, 90)
        a.poly([(50 + (x - 50) * s, 90 + (y - 90) * s) for x, y in pts], col, ol=(i == 0))
    a.line((46, 16), (38, 86), 1.2, sh(c, -60))
    for _ in range(5):
        a.sparkle(r.uniform(14, 86), r.uniform(10, 80), r.uniform(1.5, 3), k)


def m_hammer(a, r, c, k):
    a.glow(50, 44, 34, k, .35)
    a.line(*_rot([(50, 40), (50, 92)], .5), 6, (130, 90, 55))
    a.poly(_rot([(26, 16), (74, 16), (74, 44), (26, 44)], .5), c)
    a.poly(_rot([(26, 16), (74, 16), (74, 24), (26, 24)], .5), mix(c, (255, 255, 255), .4), ol=False)
    a.sparkle(r.uniform(60, 82), r.uniform(60, 86), 3.5, k)
    a.sparkle(r.uniform(14, 30), r.uniform(60, 86), 2.8, k)


def m_bow(a, r, c, k):
    a.curve([(32, 10), (70, 50), (32, 90)], 4.5, (130, 90, 55), ol=True)
    a.line((32, 10), (32, 90), .8, (235, 235, 235))
    a.line((26, 50), (84, 50), 1.6, (210, 200, 180))
    a.poly([(84, 46), (96, 50), (84, 54)], c)
    a.poly([(26, 46), (18, 50), (26, 54), (30, 50)], k)
    for _ in range(4):
        a.sparkle(r.uniform(40, 90), r.uniform(12, 88), r.uniform(1.5, 2.6), k)


def m_book(a, r, c, k):
    a.glow(50, 44, 36, k, .35)
    a.poly([(10, 26), (50, 36), (50, 86), (10, 76)], mix(c, (20, 16, 40), .3))
    a.poly([(90, 26), (50, 36), (50, 86), (90, 76)], c)
    for i in range(4):
        a.line((16, 38 + i * 9), (44, 44 + i * 9), 1.0, k)
        a.line((84, 38 + i * 9), (56, 44 + i * 9), 1.0, sh(k, -40))
    a.sparkle(50, 22, 9, k)
    a.ell(50, 12, 3, 3, k)


def m_palm(a, r, c, k):
    for i in range(3):
        _ring(a, 50, 50, 14 + i * 12, 14 + i * 12, 2.6 - i * .5, mix(c, k, i * .3))
    a.ell(50, 50, 13, 15, c, shine=True)
    for i in range(5):
        ang = -1.57 + (i - 2) * .42
        a.curve([(50 + math.cos(ang) * 10, 46 + math.sin(ang) * 12), (50 + math.cos(ang) * 22, 46 + math.sin(ang) * 25)], 4.5, c, ol=True)
    for _ in range(5):
        a.sparkle(r.uniform(10, 90), r.uniform(10, 90), r.uniform(1.5, 2.6), k)


def m_katana(a, r, c, k):
    a.glow(50, 50, 38, k, .3)
    a.curve([(20, 84), (42, 56), (66, 28), (84, 12)], 6, c, ol=True)
    a.curve([(26, 80), (46, 56), (68, 30)], 1.8, mix(c, (255, 255, 255), .6))
    a.line((20, 86), (30, 72), 6, (60, 30, 40))
    a.rect(26, 70, 40, 78, k, r=2)
    for _ in range(4):
        a.sparkle(r.uniform(50, 90), r.uniform(10, 60), r.uniform(1.5, 3), k)


def m_scales(a, r, c, k):
    a.line((50, 14), (50, 86), 3, c)
    a.line((22, 28), (78, 28), 3, c)
    for x in (22, 78):
        a.line((x, 28), (x - 10, 54), 1, k); a.line((x, 28), (x + 10, 54), 1, k)
        a.poly([(x - 14, 54), (x + 14, 54), (x + 8, 62), (x - 8, 62)], c)
    a.rect(34, 84, 66, 92, c, r=2)
    a.sparkle(50, 12, 6, k)


def m_daggers(a, r, c, k):
    for s in (-1, 1):
        a.poly(_rot([(47, 6), (53, 6), (55, 56), (45, 56)], s * .6), c)
        a.line(*_rot([(40, 58), (60, 58)], s * .6), 4, k)
        a.line(*_rot([(50, 60), (50, 84)], s * .6), 5, (90, 55, 70))
    a.glow(50, 50, 20, k, .4)
    a.sparkle(50, 50, 7, k)


def m_notes(a, r, c, k):
    for (x, y, s) in ((34, 70, 1.0), (66, 58, .9), (50, 32, .7)):
        a.ell(x, y, 9 * s, 7 * s, c, shine=True)
        a.line((x + 8 * s, y), (x + 8 * s, y - 32 * s), 2.4, c)
        a.poly([(x + 8 * s, y - 32 * s), (x + 22 * s, y - 24 * s), (x + 8 * s, y - 18 * s)], k)
    for _ in range(5):
        a.sparkle(r.uniform(10, 90), r.uniform(8, 90), r.uniform(1.5, 2.6), k)


def m_halo(a, r, c, k):
    a.glow(50, 50, 42, c, .5)
    _ring(a, 50, 24, 24, 8, 4, c)
    a.rect(44, 38, 56, 88, c, r=3)
    a.rect(28, 52, 72, 64, c, r=3)
    for i in range(12):
        ang = i * math.pi / 6
        a.line((50 + math.cos(ang) * 30, 54 + math.sin(ang) * 30), (50 + math.cos(ang) * 44, 54 + math.sin(ang) * 44), 1.2, k)


def m_axe(a, r, c, k):
    a.line(*_rot([(50, 18), (50, 94)], .35), 6, (130, 90, 55))
    for s in (-1, 1):
        a.poly(_rot([(50, 20), (50 + s * 30, 10), (50 + s * 34, 40), (50, 40)], .35), c)
    a.glow(50, 50, 30, k, .3)
    a.sparkle(r.uniform(12, 24), r.uniform(60, 80), 3, k)
    a.sparkle(r.uniform(76, 88), r.uniform(60, 80), 3, k)


def m_skull(a, r, c, k):
    a.glow(50, 50, 36, k, .35)
    _skull(a, 50, 46, 30, c, k)
    a.line((18, 86), (82, 74), 4, sh(c, -30))
    a.line((18, 74), (82, 86), 4, sh(c, -30))


def m_wind(a, r, c, k):
    for i in range(4):
        y = 22 + i * 18
        a.curve([(10, y), (34, y - 8), (56, y + 6), (78, y - 6), (90 - i * 4, y + 4 - i * 2)], 3.2 - i * .3, mix(c, k, i * .2))
        a.ell(90 - i * 4, y + 4 - i * 2, 4, 4, c, ol=False)
    for _ in range(4):
        a.sparkle(r.uniform(10, 90), r.uniform(10, 90), r.uniform(1.5, 2.6), k)


def m_burst(a, r, c, k):
    a.glow(50, 50, 42, c, .55)
    pts = []
    n = r.randint(9, 13)
    for i in range(n * 2):
        rad = r.uniform(38, 46) if i % 2 == 0 else r.uniform(18, 26)
        ang = i * math.pi / n
        pts.append((50 + math.cos(ang) * rad, 50 + math.sin(ang) * rad))
    a.poly(pts, c)
    a.ell(50, 50, 18, 18, k, shine=True)
    a.ell(50, 50, 9, 9, (255, 255, 255), ol=False)


MOTIFS = {name[2:]: fn for name, fn in globals().items() if name.startswith("m_")}


# ---------------------------------------------------------------- composição
def render(card):
    """Arte 200x200 de uma carta: fundo em degradê + motivo + extras de raridade."""
    motif = motif_for(card)
    seed = zlib.crc32(card["id"].encode("utf-8"))
    r = random.Random(seed)
    top, bot, main, accent = PALETTES[motif]
    jitter = r.uniform(-0.05, 0.05)
    main, accent = _hue(main, jitter), _hue(accent, jitter / 2)
    top, bot = _hue(top, jitter), _hue(bot, jitter)
    bg = Image.new("RGBA", (SIZE, SIZE))
    d = ImageDraw.Draw(bg)
    for y in range(SIZE):
        d.line([(0, y), (SIZE, y)], fill=tuple(int(t + (b - t) * y / SIZE) for t, b in zip(top, bot)) + (255,))
    for _ in range(r.randint(10, 20)):                                    # poeira de fundo (varia por carta)
        x, y, rad = r.randint(0, SIZE), r.randint(0, SIZE), r.randint(1, 3)
        d.ellipse([x - rad, y - rad, x + rad, y + rad], fill=mix(top, accent, .35) + (255,))
    a = Art(scale=0.86, t=0, dy=0.0)
    rarity = card.get("rarity", "common")
    if rarity in ("epic", "legendary"):
        a.glow(50, 50, 46, accent if rarity == "legendary" else main, .35)
    MOTIFS[motif](a, r, main, accent)
    if rarity == "legendary":
        for i in range(10):
            ang = i * math.tau / 10 + r.uniform(-.1, .1)
            a.line((50 + math.cos(ang) * 47, 50 + math.sin(ang) * 47), (50 + math.cos(ang) * 55, 50 + math.sin(ang) * 55), 1.2, (255, 220, 120))
    art = a.im.resize((SIZE, SIZE), Image.LANCZOS)
    if r.random() < 0.5:                                                   # cada carta tem sua composição
        art = art.transpose(Image.FLIP_LEFT_RIGHT)
    art = art.rotate(r.uniform(-9, 9), resample=Image.BICUBIC)
    bg.alpha_composite(art)
    # ---- marcas próprias da carta (ficam por cima da arte) ----
    d = ImageDraw.Draw(bg)
    gem = {"common": (235, 235, 240), "rare": (90, 160, 255), "epic": (190, 100, 255), "legendary": (255, 205, 70)}[rarity]
    d.polygon([(14, 6), (22, 14), (14, 22), (6, 14)], fill=gem, outline=(20, 20, 30))             # selo de raridade
    pips = max(1, min(5, len(card.get("effects", []))))                                          # 1 pontinho por efeito
    for i in range(pips):
        x = SIZE // 2 + (i - (pips - 1) / 2) * 12
        d.ellipse([x - 3, SIZE - 14, x + 3, SIZE - 8], fill=accent, outline=(20, 20, 30))
    corner = r.randint(0, 3)                                                                     # ornamento de canto
    cx, cy = (SIZE - 16, 14) if corner % 2 == 0 else (SIZE - 16, SIZE - 16)
    if corner < 2:
        d.arc([cx - 8, cy - 8, cx + 8, cy + 8], 0, 270, fill=accent, width=2)
    else:
        d.line([(cx - 7, cy), (cx + 7, cy)], fill=accent, width=2)
        d.line([(cx, cy - 7), (cx, cy + 7)], fill=accent, width=2)
    return bg.convert("RGB")


def main():
    force, sheet = "--force" in sys.argv, "--sheet" in sys.argv
    with open(os.path.join(ROOT, "data", "rewards.json"), encoding="utf-8") as f:
        cards = json.load(f)["rewards"]
    made, tiles = 0, []
    for card in cards:
        out_dir = os.path.join(ROOT, "assets", "cards", card["rarity"])
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, card["id"] + ".png")
        if force or not os.path.exists(path):
            render(card).save(path, optimize=True)
            made += 1
        tiles.append(path)
    print(f"{made} arte(s) criada(s); {len(cards)} cartas no total.")
    if sheet:
        cols, cell = 14, 96
        rows = (len(tiles) + cols - 1) // cols
        img = Image.new("RGB", (cols * cell, rows * cell), (14, 14, 22))
        for i, p in enumerate(tiles):
            img.paste(Image.open(p).resize((cell - 4, cell - 4), Image.LANCZOS), ((i % cols) * cell + 2, (i // cols) * cell + 2))
        img.save(os.path.join(ROOT, "tools", "cartas_preview.png"))


if __name__ == "__main__":
    main()
