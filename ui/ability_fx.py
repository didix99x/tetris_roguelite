"""
ui/ability_fx.py - EFEITOS VISUAIS das habilidades (e impactos). SÓ DESENHO: não lê nem altera o combate.

Como funciona:
  - A tela de batalha (ui/battle_screen.py) recebe os eventos do combate ("ability", "damage_enemy"...) e chama
    AbilityFX.trigger(...) / AbilityFX.react(...). Nada aqui devolve valores para o jogo.
  - Cada personagem tem um ESTILO (CHARACTER_STYLE). Um estilo é uma função que agenda pequenos efeitos
    (anel, brilho, corte, projétil, faíscas, notas, pilar de luz...) com atrasos, usando fx.add(tipo, ...).
  - Intensidade, velocidade e tamanho: ui/theme.py > EFFECTS e STYLE_TUNING.

Para associar um efeito a uma habilidade existente: troque o valor em CHARACTER_STYLE.
Para criar uma variação: copie um estilo, mude os números, registre em STYLES e aponte CHARACTER_STYLE para ele.
"""
import math
import random

import pygame

import config
from ui import theme

# ---------------------------------------------------------------- estilos por personagem
CHARACTER_STYLE = {
    "warrior": "slash_heavy",      # Golpe Poderoso
    "assassin": "slash_cross",     # Execução
    "mage": "arcane_swirl",        # Alquimia
    "bard": "song_waves",          # Canção Purificadora
    "cleric": "holy_light",        # Luz Divina
    "blacksmith": "forge_sparks",  # Forja Reforçada
    "archer": "arrow_volley",      # Chuva de Flechas
    "judge": "gavel_strike",       # Martelo da Justiça
    "monk": "resonant_palm",       # Palma Ressonante
    "yoshi": "slash_cross",        # Iai Relâmpago
}

_glow_cache = {}


def _lerp(a, b, t):
    return a + (b - a) * t


def _ease_out(u):
    return 1.0 - (1.0 - u) ** 3


def _col(color, alpha):
    return (int(color[0]), int(color[1]), int(color[2]), max(0, min(255, int(alpha))))


def _mix(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1[:3], c2[:3]))


def _glow_surface(radius, color):
    """Brilho radial (guardado em cache; é desenhado várias vezes sem custo)."""
    radius = max(8, int(radius) // 8 * 8)
    key = (radius, tuple(color[:3]))
    surf = _glow_cache.get(key)
    if surf is None:
        if len(_glow_cache) > 120:
            _glow_cache.clear()
        surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        steps = 14
        for i in range(steps):
            r = int(radius * (1 - i / steps))
            pygame.draw.circle(surf, _col(color, 255 * ((i + 1) / steps) ** 2.2), (radius, radius), r)
        _glow_cache[key] = surf
    return surf


# ---------------------------------------------------------------- desenho de cada tipo de efeito
def _d_ring(layer, u, p):
    r = _lerp(p["r0"], p["r1"], _ease_out(u))
    pygame.draw.circle(layer, _col(p["color"], 255 * (1 - u) ** 1.4 * p["a"]), (int(p["x"]), int(p["y"])), max(1, int(r)),
                       max(1, int(p["w"] * (1 - 0.6 * u))))


def _d_glow(layer, u, p):
    r = _lerp(p["r0"], p["r1"], _ease_out(u))
    surf = _glow_surface(r, p["color"])
    surf.set_alpha(int(255 * min(1.0, p["a"]) * (1 - u) ** 1.2))
    layer.blit(surf, (int(p["x"] - surf.get_width() // 2), int(p["y"] - surf.get_height() // 2)))


def _d_slash(layer, u, p):
    (x0, y0), (x1, y1) = p["p0"], p["p1"]
    head = _ease_out(min(1.0, u * 1.7))
    tail = max(0.0, head - 0.55)
    ax, ay = _lerp(x0, x1, tail), _lerp(y0, y1, tail)
    bx, by = _lerp(x0, x1, head), _lerp(y0, y1, head)
    length = math.hypot(x1 - x0, y1 - y0) or 1
    nx, ny = -(y1 - y0) / length, (x1 - x0) / length
    mx, my = (ax + bx) / 2, (ay + by) / 2
    w = p["w"] * (1 - 0.5 * u)
    alpha = 255 * min(1.0, (1 - u) * 2.2) * p["a"]
    pygame.draw.polygon(layer, _col(p["color"], alpha), [(ax, ay), (mx + nx * w, my + ny * w), (bx, by), (mx - nx * w * 0.4, my - ny * w * 0.4)])
    pygame.draw.line(layer, _col((255, 255, 255), alpha), (ax, ay), (bx, by), max(1, int(w * 0.25)))


def _d_orb(layer, u, p):
    e = _ease_out(u) if p.get("ease", True) else u
    for i in range(5):                                           # rastro
        k = max(0.0, e - i * 0.05)
        x = _lerp(p["p0"][0], p["p1"][0], k) + math.sin(k * 8 + p["ph"]) * p["wob"]
        y = _lerp(p["p0"][1], p["p1"][1], k) - math.sin(k * math.pi) * p["arc"] + math.cos(k * 8 + p["ph"]) * p["wob"] * 0.5
        pygame.draw.circle(layer, _col(p["color"], 230 * (1 - i / 5) * (1 - 0.6 * u) * p["a"]), (int(x), int(y)),
                           max(1, int(p["r"] * (1 - i * 0.14))))
        if i == 0:
            pygame.draw.circle(layer, _col((255, 255, 255), 220 * p["a"]), (int(x), int(y)), max(1, int(p["r"] * 0.45)))


def _d_arrow(layer, u, p):
    e = _ease_out(u)
    x = _lerp(p["p0"][0], p["p1"][0], e)
    y = _lerp(p["p0"][1], p["p1"][1], e) - math.sin(e * math.pi) * p["arc"]
    px = _lerp(p["p0"][0], p["p1"][0], max(0.0, e - 0.03))
    py = _lerp(p["p0"][1], p["p1"][1], max(0.0, e - 0.03)) - math.sin(max(0.0, e - 0.03) * math.pi) * p["arc"]
    ang = math.atan2(y - py, x - px)
    tx, ty = x - math.cos(ang) * 26, y - math.sin(ang) * 26
    alpha = 255 * (1 - max(0.0, u - 0.85) / 0.15) * p["a"]
    pygame.draw.line(layer, _col(p["color"], alpha * 0.5), (tx - math.cos(ang) * 22, ty - math.sin(ang) * 22), (tx, ty), 2)
    pygame.draw.line(layer, _col((230, 220, 190), alpha), (tx, ty), (x, y), 3)
    pygame.draw.polygon(layer, _col((255, 255, 255), alpha), [(x + math.cos(ang) * 9, y + math.sin(ang) * 9),
                                                              (x + math.cos(ang + 2.5) * 6, y + math.sin(ang + 2.5) * 6),
                                                              (x + math.cos(ang - 2.5) * 6, y + math.sin(ang - 2.5) * 6)])


def _d_spark(layer, u, p):
    t = u * p["life"]
    x = p["x"] + p["vx"] * t
    y = p["y"] + p["vy"] * t + 0.5 * p["g"] * t * t
    vx, vy = p["vx"], p["vy"] + p["g"] * t
    n = math.hypot(vx, vy) or 1
    ln = p["len"] * (1 - 0.7 * u)
    pygame.draw.line(layer, _col(p["color"], 255 * (1 - u) * p["a"]), (x, y), (x - vx / n * ln, y - vy / n * ln), max(1, int(p["w"])))


def _d_mote(layer, u, p):
    t = u * p["life"]
    x = p["x"] + math.sin(t * 5 + p["ph"]) * p["wob"]
    y = p["y"] + p["vy"] * t
    r = max(1, int(p["r"] * (1 - 0.5 * u)))
    a = 255 * math.sin(math.pi * min(1.0, u * 1.05)) * p["a"]
    pygame.draw.circle(layer, _col(p["color"], a * 0.55), (int(x), int(y)), r + 2)
    pygame.draw.circle(layer, _col((255, 255, 255), a), (int(x), int(y)), max(1, r - 1))


def _d_note(layer, u, p):
    x = _lerp(p["p0"][0], p["p1"][0], u)
    y = _lerp(p["p0"][1], p["p1"][1], u) + math.sin(u * 9 + p["ph"]) * 16
    a = 255 * math.sin(math.pi * u) * p["a"]
    c = _col(p["color"], a)
    pygame.draw.circle(layer, c, (int(x), int(y)), 6)
    pygame.draw.line(layer, c, (x + 5, y), (x + 5, y - 20), 3)
    pygame.draw.polygon(layer, c, [(x + 5, y - 20), (x + 15, y - 14), (x + 5, y - 11)])


def _d_pillar(layer, u, p):
    w = p["w"] * (1 - 0.55 * u) * (0.6 + 0.4 * min(1.0, u * 6))
    a = 255 * (1 - u) ** 1.3 * p["a"]
    for i in range(5):
        k = 1 - i / 5
        pygame.draw.rect(layer, _col(_mix(p["color"], (255, 255, 255), i / 5), a * (0.18 + 0.2 * i)),
                         (int(p["x"] - w * k / 2), int(p["y0"]), max(1, int(w * k)), int(p["y1"] - p["y0"])))


def _d_rune(layer, u, p):
    a = 255 * math.sin(math.pi * u) * p["a"]
    cx, cy, r = int(p["x"]), int(p["y"]), p["r"] * (0.85 + 0.15 * u)
    pygame.draw.circle(layer, _col(p["color"], a), (cx, cy), int(r), 3)
    pygame.draw.circle(layer, _col(p["color"], a * 0.7), (cx, cy), int(r * 0.72), 2)
    rot = u * 3.2
    for k in range(6):
        ang = rot + k * math.pi / 3
        pygame.draw.line(layer, _col(p["color"], a * 0.8), (cx + math.cos(ang) * r * 0.72, cy + math.sin(ang) * r * 0.72),
                         (cx + math.cos(ang + math.pi * 2 / 3) * r * 0.72, cy + math.sin(ang + math.pi * 2 / 3) * r * 0.72), 2)
        pygame.draw.circle(layer, _col((255, 255, 255), a), (int(cx + math.cos(ang) * r), int(cy + math.sin(ang) * r)), 4)


def _d_wave(layer, u, p):
    r = _lerp(p["r0"], p["r1"], _ease_out(u))
    rect = (int(p["x"] - r), int(p["y"] - r), int(r * 2), int(r * 2))
    pygame.draw.arc(layer, _col(p["color"], 255 * (1 - u) * p["a"]), rect, p["ang"] - 0.8, p["ang"] + 0.8, max(1, int(5 * (1 - u) + 1)))


def _d_flash_rect(layer, u, p):
    pygame.draw.rect(layer, _col(p["color"], p["peak"] * (1 - u) ** 1.5 * p["a"]), p["rect"], border_radius=p.get("radius", 14))


def _d_rays(layer, u, p):
    r0, r1 = _lerp(p["r0"], p["r1"], _ease_out(u) * 0.7), _lerp(p["r0"], p["r1"], _ease_out(u))
    for k in range(p["n"]):
        ang = k * 2 * math.pi / p["n"] + p["ph"]
        pygame.draw.line(layer, _col(p["color"], 255 * (1 - u) * p["a"]), (p["x"] + math.cos(ang) * r0, p["y"] + math.sin(ang) * r0),
                         (p["x"] + math.cos(ang) * r1, p["y"] + math.sin(ang) * r1), max(1, int(p["w"] * (1 - u))))


DRAW = {"ring": _d_ring, "glow": _d_glow, "slash": _d_slash, "orb": _d_orb, "arrow": _d_arrow, "spark": _d_spark, "mote": _d_mote,
        "note": _d_note, "pillar": _d_pillar, "rune": _d_rune, "wave": _d_wave, "flash_rect": _d_flash_rect, "rays": _d_rays}


# ---------------------------------------------------------------- o motor
class AbilityFX:
    def __init__(self):
        self.items = []
        self.layer = None
        self.rng = random.Random()                 # só para variar o desenho (nunca usado pela gameplay)
        self.scale = 1.0
        self.intensity = 1.0
        self.last_style = None
        self.last_style_time = 0.0
        self.clock = 0.0

    # ---- ajustes (ui/theme.py) ----
    @property
    def cfg(self):
        return theme.EFFECTS

    def enabled(self):
        return bool(self.cfg.get("enabled", True))

    def n(self, count):
        """Quantidade de partículas já multiplicada pela intensidade."""
        return max(1, int(round(count * self.intensity)))

    def add(self, kind, delay=0.0, life=0.5, **p):
        if len(self.items) >= int(self.cfg.get("max_items", 170)):
            return
        p.setdefault("a", min(1.0, 0.55 + 0.45 * self.intensity))
        p["life"] = life
        self.items.append([-delay, life, kind, p])

    # ---- ciclo de vida ----
    def update(self, dt):
        self.clock += dt
        if not self.items:
            return
        speed = float(self.cfg.get("speed", 1.0))
        for item in self.items:
            item[0] += dt * speed
        self.items = [i for i in self.items if i[0] < i[1]]

    def draw(self, surface):
        if not self.items:
            return
        if self.layer is None:
            self.layer = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.layer.fill((0, 0, 0, 0))
        for t, life, kind, p in self.items:
            if t >= 0:
                DRAW[kind](self.layer, max(0.0, min(1.0, t / life)), p)
        surface.blit(self.layer, (0, 0))

    # ---- entrada ----
    def _tune(self, key):
        tune = theme.STYLE_TUNING.get(key, {})
        self.scale = float(self.cfg.get("size", 1.0)) * float(tune.get("size", 1.0))
        self.intensity = max(0.1, float(self.cfg.get("intensity", 1.0)) * float(tune.get("intensity", 1.0)))

    def style_color(self, char_id, fallback=(140, 230, 255)):
        return theme.STYLE_COLORS.get(char_id, fallback)

    def trigger(self, char_id, ctx):
        """Habilidade usada: agenda o estilo do personagem. Devolve a cor (para texto/clarão)."""
        color = self.style_color(char_id)
        if not self.enabled():
            return color
        self._tune(char_id)
        ctx = dict(ctx, color=color)
        STYLES.get(CHARACTER_STYLE.get(char_id), style_generic)(self, ctx)
        self.last_style, self.last_style_time = char_id, self.clock
        return color

    def react(self, kind, event, ctx, cell_center=None):
        """Efeitos pequenos de impacto para eventos comuns do combate (brilho, faíscas)."""
        if not self.enabled() or not self.cfg.get("hit_effects", True):
            return
        self._tune("hit")
        E, P, rng = ctx["E"], ctx["P"], self.rng
        if kind == "damage_enemy":
            amount = event.get("amount", 0)
            big = amount >= 40
            self.add("flash_rect", life=0.16, rect=ctx["enemy_rect"], color=(255, 255, 255), peak=150 if big else 90)
            for _ in range(self.n(8 if big else 3)):
                a = rng.uniform(0, math.tau)
                v = rng.uniform(110, 260 if big else 190)
                self.add("spark", life=0.35, x=E[0], y=E[1], vx=math.cos(a) * v, vy=math.sin(a) * v - 40, g=500,
                         color=(255, 225, 130), len=14, w=2)
            if big:
                self.add("ring", life=0.3, x=E[0], y=E[1], r0=12, r1=60 * self.scale, color=(255, 230, 150), w=4)
        elif kind == "damage_player":
            self.add("flash_rect", life=0.22, rect=ctx["player_rect"], color=(255, 60, 60), peak=170)
            self.add("ring", life=0.3, x=P[0], y=P[1], r0=14, r1=62 * self.scale, color=(255, 90, 90), w=4)
        elif kind == "crit":
            self.add("rays", life=0.4, x=E[0], y=E[1], r0=16, r1=84 * self.scale, n=10, color=(255, 190, 90), w=4, ph=rng.random())
        elif kind in ("heal", "enemy_heal"):
            c = P if kind == "heal" else E
            for i in range(self.n(5)):
                self.add("mote", delay=i * 0.05, life=0.8, x=c[0] + rng.uniform(-40, 40), y=c[1] + 40, vy=-60, wob=6, ph=i, r=4,
                         color=(120, 240, 150))
        elif kind == "enemy_ability":
            self.add("ring", life=0.4, x=E[0], y=E[1], r0=16, r1=72 * self.scale, color=(255, 140, 100), w=4)
            self.add("flash_rect", life=0.25, rect=ctx["enemy_rect"], color=(255, 120, 80), peak=110)
        elif kind == "win":
            for i in range(3):
                self.add("ring", delay=i * 0.12, life=0.6, x=E[0], y=E[1], r0=14, r1=(90 + 40 * i) * self.scale, color=(255, 225, 120), w=5)
            for _ in range(self.n(24)):
                a = rng.uniform(0, math.tau)
                v = rng.uniform(120, 340)
                self.add("spark", life=0.7, x=E[0], y=E[1], vx=math.cos(a) * v, vy=math.sin(a) * v - 80, g=420,
                         color=rng.choice(((255, 225, 120), (255, 255, 255), (255, 170, 80))), len=16, w=3)
        elif kind == "burst" and cell_center and self.clock - self.last_style_time < 0.4:
            color = theme.STYLE_COLORS.get(self.last_style, (200, 220, 255))
            for (px, py) in cell_center[:12]:
                self.add("ring", life=0.4, x=px, y=py, r0=6, r1=30 * self.scale, color=color, w=3)
                self.add("mote", life=0.6, x=px, y=py, vy=-50, wob=4, ph=px, r=3, color=color)


# ---------------------------------------------------------------- ESTILOS (um por habilidade)
def _cast_aura(fx, c, P):
    fx.add("ring", life=0.3, x=P[0], y=P[1], r0=70 * fx.scale, r1=18, color=c, w=4)          # carregando (anel que fecha)
    fx.add("glow", life=0.5, x=P[0], y=P[1], r0=20, r1=95 * fx.scale, color=c, a=0.9)


def style_generic(fx, ctx):
    _cast_aura(fx, ctx["color"], ctx["P"])


def style_slash_heavy(fx, ctx):                      # Golpe Poderoso
    c, P, E, s = ctx["color"], ctx["P"], ctx["E"], fx.scale
    _cast_aura(fx, c, P)
    fx.add("slash", delay=0.12, life=0.28, p0=(E[0] - 70 * s, E[1] - 70 * s), p1=(E[0] + 70 * s, E[1] + 70 * s), w=20 * s, color=c)
    fx.add("slash", delay=0.2, life=0.25, p0=(E[0] + 60 * s, E[1] - 50 * s), p1=(E[0] - 60 * s, E[1] + 60 * s), w=9 * s, color=(255, 230, 170))
    fx.add("ring", delay=0.22, life=0.4, x=E[0], y=E[1], r0=10, r1=100 * s, color=c, w=7)
    fx.add("glow", delay=0.2, life=0.4, x=E[0], y=E[1], r0=20, r1=110 * s, color=c, a=1.0)
    for _ in range(fx.n(14)):
        a = fx.rng.uniform(0, math.tau)
        v = fx.rng.uniform(120, 340)
        fx.add("spark", delay=0.22, life=0.5, x=E[0], y=E[1], vx=math.cos(a) * v, vy=math.sin(a) * v - 60, g=520, color=(255, 190, 110), len=16, w=3)


def style_slash_cross(fx, ctx):                      # Execução
    c, P, E, s = ctx["color"], ctx["P"], ctx["E"], fx.scale
    fx.add("glow", life=0.3, x=P[0], y=P[1], r0=14, r1=70 * s, color=c, a=0.8)
    for i, ((x0, y0), (x1, y1)) in enumerate((((-80, -50), (80, 50)), ((80, -50), (-80, 50)), ((-90, 0), (90, 6)))):
        fx.add("slash", delay=0.1 + 0.07 * i, life=0.2, p0=(E[0] + x0 * s, E[1] + y0 * s), p1=(E[0] + x1 * s, E[1] + y1 * s),
               w=(12 if i < 2 else 6) * s, color=c if i < 2 else (255, 255, 255))
    fx.add("ring", delay=0.3, life=0.45, x=E[0], y=E[1], r0=8, r1=84 * s, color=c, w=5)
    fx.add("flash_rect", delay=0.3, life=0.3, rect=ctx["enemy_rect"], color=(255, 255, 255), peak=170)
    for _ in range(fx.n(12)):
        a = fx.rng.uniform(0, math.tau)
        v = fx.rng.uniform(100, 280)
        fx.add("spark", delay=0.3, life=0.5, x=E[0], y=E[1], vx=math.cos(a) * v, vy=math.sin(a) * v, g=300, color=c, len=18, w=3)


def style_arcane_swirl(fx, ctx):                     # Alquimia
    c, P, B, s = ctx["color"], ctx["P"], ctx["B"], fx.scale
    _cast_aura(fx, c, P)
    fx.add("rune", life=0.9, x=B[0], y=B[1], r=170 * s, color=c)
    fx.add("rune", delay=0.15, life=0.8, x=B[0], y=B[1], r=105 * s, color=(120, 200, 255))
    for i in range(fx.n(8)):
        fx.add("orb", delay=0.04 * i, life=0.55, p0=P, p1=(B[0] + fx.rng.uniform(-90, 90), B[1] + fx.rng.uniform(-90, 90)),
               r=6 * s, color=c, arc=40, wob=12, ph=i)
    fx.add("ring", delay=0.4, life=0.5, x=B[0], y=B[1], r0=20, r1=230 * s, color=c, w=6)


def style_song_waves(fx, ctx):                       # Canção Purificadora
    c, P, B, E, s = ctx["color"], ctx["P"], ctx["B"], ctx["E"], fx.scale
    _cast_aura(fx, c, P)
    for i in range(3):
        fx.add("wave", delay=0.08 * i, life=0.7, x=P[0], y=P[1], r0=30, r1=(260 + 60 * i) * s, color=c, ang=0.0)
    for i in range(fx.n(7)):
        fx.add("note", delay=0.06 * i, life=0.9, p0=(P[0] + 30, P[1] - 10), p1=(B[0] + fx.rng.uniform(-120, 120), B[1] + fx.rng.uniform(-120, 90)),
               color=c if i % 2 else (200, 255, 230), ph=i)
    fx.add("flash_rect", delay=0.25, life=0.5, rect=ctx["attack_bar"], color=c, peak=200, radius=9)       # "atrasa o inimigo"
    fx.add("ring", delay=0.3, life=0.5, x=B[0], y=B[1], r0=30, r1=240 * s, color=(210, 255, 235), w=4)


def style_holy_light(fx, ctx):                       # Luz Divina
    c, P, s = ctx["color"], ctx["P"], fx.scale
    fx.add("pillar", life=0.9, x=P[0], y0=P[1] - 170 * s, y1=P[1] + 70, w=96 * s, color=c)
    fx.add("glow", life=0.8, x=P[0], y=P[1], r0=30, r1=130 * s, color=c, a=1.0)
    for i in range(3):
        fx.add("ring", delay=0.1 * i, life=0.7, x=P[0], y=P[1], r0=20, r1=(100 + 30 * i) * s, color=c, w=5)
    for i in range(fx.n(12)):
        fx.add("mote", delay=0.04 * i, life=1.0, x=P[0] + fx.rng.uniform(-55, 55), y=P[1] + 55, vy=-90, wob=8, ph=i, r=4, color=(255, 240, 160))
    fx.add("rays", delay=0.1, life=0.6, x=P[0], y=P[1], r0=30, r1=120 * s, n=12, color=(255, 250, 200), w=3, ph=0.2)


def style_forge_sparks(fx, ctx):                     # Forja Reforçada
    c, P, s = ctx["color"], ctx["P"], fx.scale
    for k in range(3):                                  # três marteladas
        fx.add("ring", delay=0.14 * k, life=0.3, x=P[0], y=P[1] + 30, r0=8, r1=(58 + 8 * k) * s, color=c, w=5)
        for _ in range(fx.n(10)):
            a = fx.rng.uniform(math.pi * 1.1, math.pi * 1.9)
            v = fx.rng.uniform(140, 330)
            fx.add("spark", delay=0.14 * k, life=0.6, x=P[0], y=P[1] + 30, vx=math.cos(a) * v, vy=math.sin(a) * v, g=640,
                   color=(255, 200, 100), len=14, w=3)
    fx.add("glow", delay=0.28, life=0.7, x=P[0], y=P[1], r0=40, r1=120 * s, color=c, a=0.9)
    r = (P[0] - 78 * s, P[1] - 78 * s, 156 * s, 156 * s)                                        # "escudo" que reforça a defesa
    fx.add("flash_rect", delay=0.4, life=0.6, rect=r, color=(255, 190, 110), peak=130, radius=26)


def style_arrow_volley(fx, ctx):                     # Chuva de Flechas
    c, P, E, s = ctx["color"], ctx["P"], ctx["E"], fx.scale
    fx.add("glow", life=0.3, x=P[0], y=P[1], r0=12, r1=60 * s, color=c, a=0.7)
    for i in range(5):
        tgt = (E[0] + fx.rng.uniform(-30, 30), E[1] + fx.rng.uniform(-30, 30))
        fx.add("arrow", delay=0.08 * i, life=0.42, p0=(P[0] + 40, P[1] - 10), p1=tgt, arc=70 + 10 * i, color=c)
        fx.add("ring", delay=0.08 * i + 0.4, life=0.25, x=tgt[0], y=tgt[1], r0=4, r1=26 * s, color=(255, 240, 190), w=3)
        for _ in range(fx.n(3)):
            a = fx.rng.uniform(0, math.tau)
            fx.add("spark", delay=0.08 * i + 0.4, life=0.35, x=tgt[0], y=tgt[1], vx=math.cos(a) * 150, vy=math.sin(a) * 150, g=300,
                   color=(255, 240, 180), len=10, w=2)


def style_gavel_strike(fx, ctx):                     # Martelo da Justiça
    c, E, s = ctx["color"], ctx["E"], fx.scale
    fx.add("glow", life=0.3, x=ctx["P"][0], y=ctx["P"][1], r0=14, r1=64 * s, color=c, a=0.7)
    fx.add("pillar", delay=0.1, life=0.45, x=E[0], y0=0, y1=E[1] + 10, w=84 * s, color=c)
    fx.add("ring", delay=0.3, life=0.5, x=E[0], y=E[1], r0=10, r1=110 * s, color=c, w=8)
    fx.add("ring", delay=0.36, life=0.5, x=E[0], y=E[1], r0=10, r1=70 * s, color=(255, 255, 255), w=4)
    fx.add("rays", delay=0.3, life=0.45, x=E[0], y=E[1], r0=24, r1=120 * s, n=14, color=c, w=4, ph=0.1)
    fx.add("glow", delay=0.3, life=0.5, x=E[0], y=E[1], r0=20, r1=120 * s, color=c, a=1.0)
    fx.add("flash_rect", delay=0.5, life=0.7, rect=ctx["attack_bar"], color=c, peak=230, radius=9)       # "atrasa o ataque"
    fx.add("ring", delay=0.5, life=0.7, x=ctx["attack_bar"][0] + ctx["attack_bar"][2] // 2, y=ctx["attack_bar"][1] + 9,
           r0=10, r1=40, color=c, w=2)


def style_resonant_palm(fx, ctx):                    # Palma Ressonante
    c, P, E, s = ctx["color"], ctx["P"], ctx["E"], fx.scale
    _cast_aura(fx, c, P)
    for i in range(3):
        fx.add("orb", delay=0.1 * i, life=0.4, p0=P, p1=E, r=(16 - 3 * i) * s, color=c, arc=0, wob=0, ph=0, a=0.9)
        fx.add("ring", delay=0.1 * i, life=0.5, x=P[0], y=P[1], r0=14, r1=(80 + 20 * i) * s, color=c, w=5)
    for i in range(3):
        fx.add("ring", delay=0.42 + 0.07 * i, life=0.5, x=E[0], y=E[1], r0=10, r1=(60 + 28 * i) * s, color=c if i % 2 == 0 else (255, 240, 200), w=6 - i)
    fx.add("glow", delay=0.42, life=0.5, x=E[0], y=E[1], r0=20, r1=100 * s, color=c, a=1.0)
    for _ in range(fx.n(12)):
        a = fx.rng.uniform(0, math.tau)
        fx.add("spark", delay=0.42, life=0.5, x=E[0], y=E[1], vx=math.cos(a) * 240, vy=math.sin(a) * 240, g=200, color=(255, 210, 120), len=16, w=3)


STYLES = {"slash_heavy": style_slash_heavy, "slash_cross": style_slash_cross, "arcane_swirl": style_arcane_swirl,
          "song_waves": style_song_waves, "holy_light": style_holy_light, "forge_sparks": style_forge_sparks,
          "arrow_volley": style_arrow_volley, "gavel_strike": style_gavel_strike, "resonant_palm": style_resonant_palm}
