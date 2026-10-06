"""
ui/icons.py - ícones da HUD desenhados com formas (sem arquivos de imagem).

Todos têm a mesma forma de uso:   draw_xxx(surface, (centro_x, centro_y), tamanho, cor)
Para criar um ícone novo: copie um deles, mude as formas e registre em ICONS (no fim do arquivo).
"""
import math

import pygame


def _dark(color, amount=90):
    return tuple(max(0, c - amount) for c in color)


def _light(color, amount=70):
    return tuple(min(255, c + amount) for c in color)


def draw_heart(surface, center, size, color):
    cx, cy = center
    r = max(2, int(size * 0.27))
    pts = [(cx - size * 0.5, cy - size * 0.05), (cx + size * 0.5, cy - size * 0.05), (cx, cy + size * 0.5)]
    for dx in (-r, r):
        pygame.draw.circle(surface, _dark(color), (cx + dx, cy - r // 2), r + 1)
    pygame.draw.polygon(surface, _dark(color), [(x, y + 1) for x, y in pts])
    for dx in (-r, r):
        pygame.draw.circle(surface, color, (cx + dx, cy - r // 2), r)
    pygame.draw.polygon(surface, color, pts)
    pygame.draw.circle(surface, _light(color), (cx - r, cy - r), max(1, r // 3))


def draw_bolt(surface, center, size, color):
    cx, cy = center
    s = size / 2
    pts = [(cx + 0.15 * s, cy - s), (cx - 0.65 * s, cy + 0.1 * s), (cx - 0.05 * s, cy + 0.1 * s),
           (cx - 0.25 * s, cy + s), (cx + 0.7 * s, cy - 0.2 * s), (cx + 0.1 * s, cy - 0.2 * s)]
    pygame.draw.polygon(surface, _dark(color), [(x + 1, y + 1) for x, y in pts])
    pygame.draw.polygon(surface, color, pts)


def draw_clock(surface, center, size, color):
    cx, cy = center
    r = max(3, int(size * 0.5))
    pygame.draw.circle(surface, _dark(color, 120), (cx, cy), r)
    pygame.draw.circle(surface, color, (cx, cy), r, max(1, size // 8))
    pygame.draw.line(surface, color, (cx, cy), (cx, cy - r * 0.65), max(1, size // 9))
    pygame.draw.line(surface, color, (cx, cy), (cx + r * 0.5, cy + r * 0.2), max(1, size // 9))


def draw_shield(surface, center, size, color):
    cx, cy = center
    s = size / 2
    pts = [(cx - s * 0.85, cy - s * 0.8), (cx + s * 0.85, cy - s * 0.8), (cx + s * 0.8, cy + s * 0.15),
           (cx, cy + s), (cx - s * 0.8, cy + s * 0.15)]
    pygame.draw.polygon(surface, _dark(color), [(x, y + 1) for x, y in pts])
    pygame.draw.polygon(surface, color, pts)
    pygame.draw.line(surface, _light(color), (cx, cy - s * 0.7), (cx, cy + s * 0.6), max(1, size // 10))


def draw_drop(surface, center, size, color):
    cx, cy = center
    r = max(2, int(size * 0.32))
    pygame.draw.polygon(surface, color, [(cx, cy - size * 0.5), (cx - r, cy + r * 0.1), (cx + r, cy + r * 0.1)])
    pygame.draw.circle(surface, color, (cx, cy + int(r * 0.3)), r)
    pygame.draw.circle(surface, _light(color), (cx - r // 3, cy), max(1, r // 3))


def draw_mute(surface, center, size, color):
    cx, cy = center
    s = size / 2
    pygame.draw.polygon(surface, color, [(cx - s, cy - s * 0.35), (cx - s * 0.4, cy - s * 0.35), (cx + s * 0.1, cy - s * 0.8),
                                         (cx + s * 0.1, cy + s * 0.8), (cx - s * 0.4, cy + s * 0.35), (cx - s, cy + s * 0.35)])
    pygame.draw.line(surface, (255, 90, 90), (cx + s * 0.3, cy - s * 0.6), (cx + s, cy + s * 0.6), max(2, size // 7))
    pygame.draw.line(surface, (255, 90, 90), (cx + s, cy - s * 0.6), (cx + s * 0.3, cy + s * 0.6), max(2, size // 7))


def draw_web(surface, center, size, color):
    cx, cy = center
    s = size / 2
    for k in range(4):
        a = k * math.pi / 4
        pygame.draw.line(surface, color, (cx - math.cos(a) * s, cy - math.sin(a) * s), (cx + math.cos(a) * s, cy + math.sin(a) * s), 1)
    pygame.draw.circle(surface, color, (cx, cy), max(2, int(s * 0.55)), 1)
    pygame.draw.circle(surface, color, (cx, cy), max(3, int(s * 0.95)), 1)


def draw_stone(surface, center, size, color):
    cx, cy = center
    s = size / 2
    pts = [(cx - s * 0.5, cy - s * 0.85), (cx + s * 0.6, cy - s * 0.7), (cx + s, cy + s * 0.1), (cx + s * 0.4, cy + s * 0.85),
           (cx - s * 0.7, cy + s * 0.7), (cx - s, cy - s * 0.1)]
    pygame.draw.polygon(surface, color, pts)
    pygame.draw.polygon(surface, _dark(color, 60), pts, 1)
    pygame.draw.line(surface, _light(color, 50), (cx - s * 0.5, cy - s * 0.55), (cx + s * 0.2, cy - s * 0.45), 1)


def draw_sparkle(surface, center, size, color):
    cx, cy = center
    s = size / 2
    pts = [(cx, cy - s), (cx + s * 0.28, cy - s * 0.28), (cx + s, cy), (cx + s * 0.28, cy + s * 0.28),
           (cx, cy + s), (cx - s * 0.28, cy + s * 0.28), (cx - s, cy), (cx - s * 0.28, cy - s * 0.28)]
    pygame.draw.polygon(surface, color, pts)


def draw_diamond(surface, center, size, color):
    cx, cy = center
    s = size / 2
    pygame.draw.polygon(surface, color, [(cx, cy - s), (cx + s, cy), (cx, cy + s), (cx - s, cy)])


def draw_crown(surface, center, size, color):
    cx, cy = center
    s = size / 2
    pts = [(cx - s, cy + s * 0.6), (cx - s, cy - s * 0.4), (cx - s * 0.5, cy + s * 0.1), (cx, cy - s * 0.8),
           (cx + s * 0.5, cy + s * 0.1), (cx + s, cy - s * 0.4), (cx + s, cy + s * 0.6)]
    pygame.draw.polygon(surface, _dark(color), [(x, y + 1) for x, y in pts])
    pygame.draw.polygon(surface, color, pts)


def draw_skull(surface, center, size, color):
    cx, cy = center
    r = max(3, int(size * 0.42))
    pygame.draw.circle(surface, color, (cx, cy - size // 10), r)
    pygame.draw.rect(surface, color, (cx - r // 2, cy + r // 3, r, r), border_radius=2)
    for dx in (-r // 2, r // 2):
        pygame.draw.circle(surface, (20, 14, 26), (cx + dx, cy - size // 8), max(1, r // 3))


def draw_eye(surface, center, size, color):
    cx, cy = center
    s = size / 2
    pygame.draw.polygon(surface, color, [(cx - s, cy), (cx - s * 0.4, cy - s * 0.55), (cx + s * 0.4, cy - s * 0.55), (cx + s, cy),
                                         (cx + s * 0.4, cy + s * 0.55), (cx - s * 0.4, cy + s * 0.55)])
    pygame.draw.circle(surface, (20, 14, 26), (cx, cy), max(2, int(s * 0.4)))


ICONS = {
    "heart": draw_heart, "bolt": draw_bolt, "clock": draw_clock, "shield": draw_shield, "drop": draw_drop,
    "mute": draw_mute, "web": draw_web, "stone": draw_stone, "sparkle": draw_sparkle, "diamond": draw_diamond,
    "crown": draw_crown, "skull": draw_skull, "eye": draw_eye,
}


def draw_icon(surface, name, center, size, color):
    ICONS[name](surface, center, size, color)


def status_icon(text):
    """Escolhe ícone e cor para um texto de status do combate (ex.: 'Veneno: 4s')."""
    low = text.lower()
    table = (("cegueira", "eye", (230, 70, 80)), ("teia", "web", (210, 210, 230)), ("pedra", "stone", (170, 170, 185)), ("pressão", "bolt", (255, 210, 90)),
             ("pressao", "bolt", (255, 210, 90)), ("veneno", "drop", (140, 230, 90)), ("silêncio", "mute", (200, 200, 220)),
             ("silencio", "mute", (200, 200, 220)), ("blindado", "shield", (150, 190, 255)))
    for key, icon, color in table:
        if key in low:
            return icon, color
    return "diamond", (255, 150, 120)
