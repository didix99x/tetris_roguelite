"""
ui/portraits.py - ARTE PROVISÓRIA (retratos desenhados com formas).

Quando você tiver arte de verdade, troque o conteúdo de draw_portrait()
por um blit de imagem (assets/images/...). O resto do jogo não muda.
Os retratos são desenhados UMA vez e guardados em cache (bom desempenho).
"""
import math

import pygame

from ui.gif_loader import load_gif

_cache = {}


def _shade(color, amount):
    return tuple(max(0, min(255, c + amount)) for c in color)


def _face(s, cx, cy, r, skin, eye=(20, 20, 30)):
    pygame.draw.circle(s, skin, (cx, cy), r)
    pygame.draw.circle(s, _shade(skin, -50), (cx, cy), r, 3)
    pygame.draw.circle(s, eye, (cx - r // 3, cy - r // 6), max(2, r // 7))
    pygame.draw.circle(s, eye, (cx + r // 3, cy - r // 6), max(2, r // 7))


def _paint(kind, size, color, boss):
    s = pygame.Surface((size, size), pygame.SRCALPHA)
    u = size / 100.0                      # unidade: o desenho é pensado em 100x100
    P = lambda x, y: (int(x * u), int(y * u))
    R = lambda v: max(1, int(v * u))
    dark = _shade(color, -60)
    light = _shade(color, 50)
    skin = (235, 200, 160)

    pygame.draw.rect(s, (26, 26, 40), (0, 0, size, size), border_radius=R(14))

    if kind == "warrior":
        pygame.draw.rect(s, color, (*P(28, 58), R(44), R(34)), border_radius=R(6))      # corpo
        _face(s, *P(50, 42), R(20), skin)
        pygame.draw.arc(s, (190, 190, 205), (*P(28, 14), R(44), R(44)), 0, 3.14159, R(8))  # capacete
        pygame.draw.rect(s, (190, 190, 205), (*P(46, 8), R(8), R(14)), border_radius=R(3))
        pygame.draw.line(s, (220, 220, 235), P(82, 88), P(82, 40), R(6))                # espada
        pygame.draw.line(s, (150, 110, 60), P(74, 74), P(90, 74), R(5))
    elif kind == "mage":
        pygame.draw.polygon(s, color, [P(24, 94), P(76, 94), P(66, 56), P(34, 56)])     # manto
        _face(s, *P(50, 44), R(18), skin)
        pygame.draw.polygon(s, dark, [P(26, 34), P(74, 34), P(50, 4)])                  # chapéu
        pygame.draw.rect(s, light, (*P(26, 32), R(48), R(6)), border_radius=R(3))
        pygame.draw.circle(s, (120, 230, 255), P(82, 40), R(7))                         # orbe
        pygame.draw.line(s, (150, 110, 60), P(82, 46), P(82, 92), R(4))
    elif kind == "assassin":
        pygame.draw.rect(s, dark, (*P(28, 58), R(44), R(34)), border_radius=R(6))
        pygame.draw.circle(s, color, P(50, 42), R(24))                                  # capuz
        pygame.draw.ellipse(s, (20, 20, 30), (*P(36, 34), R(28), R(18)))
        pygame.draw.circle(s, (255, 80, 80), P(43, 43), R(3))
        pygame.draw.circle(s, (255, 80, 80), P(57, 43), R(3))
        pygame.draw.line(s, (220, 220, 235), P(14, 86), P(34, 62), R(4))                # adagas
        pygame.draw.line(s, (220, 220, 235), P(86, 86), P(66, 62), R(4))
    elif kind == "bard":
        pygame.draw.polygon(s, color, [P(24, 94), P(76, 94), P(66, 56), P(34, 56)])     # vestido
        pygame.draw.circle(s, (110, 62, 30), P(50, 40), R(24))                          # cabelo
        _face(s, *P(50, 44), R(17), skin)
        pygame.draw.circle(s, (240, 190, 70), P(34, 28), R(5))                          # flor
        pygame.draw.ellipse(s, (210, 160, 90), (*P(28, 62), R(36), R(26)))              # alaúde
        pygame.draw.circle(s, (80, 50, 30), P(46, 75), R(5))
        pygame.draw.line(s, (150, 110, 60), P(60, 66), P(88, 46), R(4))
    elif kind == "judge":
        pygame.draw.rect(s, (30, 30, 50), (*P(26, 58), R(48), R(36)), border_radius=R(6))     # toga
        pygame.draw.rect(s, (235, 235, 245), (*P(44, 58), R(12), R(20)))
        _face(s, *P(50, 40), R(19), skin)
        pygame.draw.ellipse(s, (235, 235, 245), (*P(28, 14), R(44), R(22)))                   # peruca
        pygame.draw.rect(s, (150, 100, 50), (*P(72, 70), R(10), R(18)), border_radius=R(3))  # martelo
        pygame.draw.rect(s, color, (*P(66, 62), R(22), R(10)), border_radius=R(3))
    elif kind == "cleric":
        pygame.draw.polygon(s, (240, 240, 235), [P(24, 94), P(76, 94), P(66, 56), P(34, 56)])
        pygame.draw.rect(s, color, (*P(46, 60), R(8), R(30)))
        _face(s, *P(50, 42), R(18), skin)
        pygame.draw.arc(s, (255, 230, 120), (*P(32, 6), R(36), R(14)), 0, 3.14159 * 2, R(4))  # auréola
        pygame.draw.line(s, (255, 230, 120), P(82, 40), P(82, 88), R(4))                      # cajado
        pygame.draw.circle(s, (255, 230, 120), P(82, 36), R(7), R(3))
    elif kind == "blacksmith":
        pygame.draw.rect(s, (90, 60, 40), (*P(26, 56), R(48), R(38)), border_radius=R(6))    # avental
        _face(s, *P(50, 40), R(19), skin)
        pygame.draw.rect(s, (60, 40, 30), (*P(32, 18), R(36), R(10)), border_radius=R(4))    # faixa
        pygame.draw.rect(s, (150, 150, 165), (*P(70, 62), R(24), R(12)), border_radius=R(3))  # martelo
        pygame.draw.line(s, (150, 100, 50), P(76, 74), P(76, 94), R(5))
    elif kind == "archer":
        pygame.draw.rect(s, color, (*P(28, 58), R(44), R(34)), border_radius=R(6))
        _face(s, *P(50, 42), R(19), skin)
        pygame.draw.polygon(s, dark, [P(26, 34), P(74, 34), P(50, 8)])                        # capuz
        pygame.draw.arc(s, (150, 100, 50), (*P(60, 28), R(34), R(60)), 4.7, 7.8, R(4))        # arco
        pygame.draw.line(s, (230, 230, 230), P(77, 30), P(77, 86), R(2))
        pygame.draw.line(s, (200, 200, 210), P(46, 70), P(90, 58), R(3))                      # flecha
    elif kind == "monk":
        pygame.draw.polygon(s, color, [P(24, 94), P(76, 94), P(68, 56), P(32, 56)])
        pygame.draw.rect(s, (240, 240, 240), (*P(28, 70), R(44), R(7)))                       # faixa
        pygame.draw.circle(s, skin, P(50, 40), R(20))                                         # careca
        pygame.draw.circle(s, _shade(skin, -50), P(50, 40), R(20), 3)
        pygame.draw.circle(s, (20, 20, 30), P(43, 39), R(3))
        pygame.draw.circle(s, (20, 20, 30), P(57, 39), R(3))
        pygame.draw.circle(s, (255, 230, 120), P(18, 70), R(7))                               # punho de energia
    elif kind == "fairy":
        pygame.draw.ellipse(s, (200, 240, 255), (*P(8, 26), R(34), R(46)))                    # asas
        pygame.draw.ellipse(s, (200, 240, 255), (*P(58, 26), R(34), R(46)))
        pygame.draw.circle(s, color, P(50, 56), R(16))
        _face(s, *P(50, 36), R(14), skin)
        pygame.draw.circle(s, (255, 255, 160), P(84, 20), R(5))                               # brilho
    elif kind == "dragon":
        pygame.draw.polygon(s, dark, [P(8, 60), P(30, 40), P(30, 80)])                        # asa
        pygame.draw.polygon(s, dark, [P(92, 60), P(70, 40), P(70, 80)])
        pygame.draw.ellipse(s, color, (*P(28, 26), R(44), R(58)))
        pygame.draw.polygon(s, (240, 230, 200), [P(34, 30), P(30, 8), P(42, 26)])            # chifres
        pygame.draw.polygon(s, (240, 230, 200), [P(66, 30), P(70, 8), P(58, 26)])
        pygame.draw.circle(s, (255, 220, 60), P(41, 44), R(4))
        pygame.draw.circle(s, (255, 220, 60), P(59, 44), R(4))
        pygame.draw.polygon(s, (255, 150, 40), [P(42, 70), P(50, 84), P(58, 70)])
    elif kind == "zombie":
        pygame.draw.rect(s, (70, 80, 70), (*P(28, 62), R(44), R(32)), border_radius=R(6))
        pygame.draw.circle(s, color, P(50, 42), R(24))
        pygame.draw.circle(s, (240, 240, 200), P(41, 40), R(6))
        pygame.draw.circle(s, (240, 240, 200), P(59, 40), R(6))
        pygame.draw.circle(s, (120, 0, 0), P(42, 41), R(2))
        pygame.draw.line(s, (60, 20, 20), P(40, 58), P(60, 56), R(3))
        pygame.draw.line(s, color, P(20, 66), P(44, 72), R(7))                                # braço esticado
    elif kind == "necromancer":
        pygame.draw.polygon(s, dark, [P(20, 94), P(80, 94), P(66, 40), P(34, 40)])            # manto
        pygame.draw.circle(s, (230, 230, 220), P(50, 42), R(16))                              # caveira
        pygame.draw.circle(s, (120, 255, 150), P(44, 40), R(4))
        pygame.draw.circle(s, (120, 255, 150), P(56, 40), R(4))
        pygame.draw.polygon(s, color, [P(24, 36), P(76, 36), P(50, 4)])                       # capuz
        pygame.draw.circle(s, (120, 255, 150), P(84, 50), R(7))                               # orbe
    elif kind == "void":
        pygame.draw.circle(s, dark, P(50, 54), R(30))
        pygame.draw.circle(s, color, P(50, 50), R(24))
        pygame.draw.circle(s, (255, 255, 255), P(40, 46), R(5))
        pygame.draw.circle(s, (255, 255, 255), P(60, 46), R(5))
        pygame.draw.circle(s, (20, 0, 30), P(40, 46), R(2))
        pygame.draw.circle(s, (20, 0, 30), P(60, 46), R(2))
        pygame.draw.arc(s, (20, 0, 30), (*P(36, 56), R(28), R(18)), 3.4, 6.0, R(4))
    elif kind == "goblin":
        pygame.draw.polygon(s, color, [P(10, 40), P(32, 46), P(30, 60)])                # orelhas
        pygame.draw.polygon(s, color, [P(90, 40), P(68, 46), P(70, 60)])
        pygame.draw.rect(s, dark, (*P(30, 66), R(40), R(26)), border_radius=R(6))
        _face(s, *P(50, 46), R(24), color, (255, 230, 60))
        pygame.draw.polygon(s, (240, 240, 230), [P(42, 60), P(46, 70), P(50, 60)])
        pygame.draw.polygon(s, (240, 240, 230), [P(50, 60), P(54, 70), P(58, 60)])
    elif kind == "spider":
        for i, ang in enumerate((-60, -30, 10, 40)):
            for side in (-1, 1):
                x0, y0 = 50 + side * 14, 56
                x1, y1 = 50 + side * (34 + i * 3), 30 + i * 18 + ang // 6
                pygame.draw.line(s, dark, P(x0, y0), P(x1, y1), R(4))
                pygame.draw.line(s, dark, P(x1, y1), P(50 + side * 44, y1 + 14), R(4))
        pygame.draw.circle(s, color, P(50, 64), R(22))
        pygame.draw.circle(s, light, P(50, 40), R(14))
        for dx in (-5, 5):
            pygame.draw.circle(s, (255, 80, 80), P(50 + dx, 38), R(3))
    elif kind == "mage_enemy":
        pygame.draw.polygon(s, dark, [P(22, 94), P(78, 94), P(66, 54), P(34, 54)])
        _face(s, *P(50, 44), R(18), (170, 150, 190), (255, 90, 255))
        pygame.draw.polygon(s, color, [P(26, 34), P(74, 34), P(58, 2)])
        pygame.draw.circle(s, (255, 90, 255), P(18, 56), R(8))
    elif kind == "golem":
        pygame.draw.rect(s, dark, (*P(22, 40), R(56), R(52)), border_radius=R(6))
        pygame.draw.rect(s, color, (*P(30, 12), R(40), R(34)), border_radius=R(6))
        pygame.draw.rect(s, (255, 190, 60), (*P(38, 24), R(8), R(8)))
        pygame.draw.rect(s, (255, 190, 60), (*P(54, 24), R(8), R(8)))
        pygame.draw.rect(s, color, (*P(6, 44), R(18), R(40)), border_radius=R(5))
        pygame.draw.rect(s, color, (*P(76, 44), R(18), R(40)), border_radius=R(5))
    else:  # desconhecido: bloco com interrogação simples
        pygame.draw.rect(s, color, (*P(25, 25), R(50), R(50)), border_radius=R(8))

    if boss:  # coroa + moldura dourada
        pygame.draw.polygon(s, (255, 205, 60), [P(28, 14), P(36, 0), P(44, 12), P(50, -2),
                                                 P(56, 12), P(64, 0), P(72, 14)])
        pygame.draw.rect(s, (255, 205, 60), (0, 0, size, size), width=R(4), border_radius=R(14))
    else:
        pygame.draw.rect(s, _shade(color, 20), (0, 0, size, size), width=R(3), border_radius=R(14))
    return s


def portrait_kind(entity):
    """Descobre qual desenho usar (personagem ou inimigo)."""
    if hasattr(entity, "char_id"):
        return entity.char_id
    if getattr(entity, "character_id", None):
        return entity.character_id        # personagem como inimigo: usa o desenho do personagem
    if getattr(entity, "portrait", None):
        return entity.portrait            # desenho provisório indicado no JSON ("portrait"), usado só sem arquivo de arte
    if entity.is_boss:
        return "boss"
    family = getattr(entity, "family", entity.id)
    return {"mage": "mage_enemy"}.get(family, family)


def _art_location(entity):
    """Pasta e nome do arquivo de arte: characters/<id>, enemies/<id> ou bosses/<id>."""
    if hasattr(entity, "char_id"):
        return "characters", [getattr(entity, "image_id", None) or entity.char_id, entity.char_id]
    if getattr(entity, "art_folder", None):                     # inimigo que é um personagem jogável
        return entity.art_folder, [entity.image_id, getattr(entity, "character_id", None) or entity.image_id]
    if getattr(entity, "is_boss", False):
        return "bosses", [entity.image_id, entity.id]          # ex.: boss_10
    # inimigo comum: arte própria (ex.: goblin_archer) e, se não existir, a da família (goblin)
    return "enemies", [entity.image_id, entity.id, getattr(entity, "family", entity.id)]


ART_EXTENSIONS = (".gif", ".png", ".webp", ".jpg", ".jpeg")
_art_lookup = {}


def _find_animation(entity, size):
    """Procura assets/images/<pasta>/<id>.(gif|png|webp|jpg). Devolve None se não achar."""
    folder, ids = _art_location(entity)
    key = (folder, tuple(ids), size)
    if key in _art_lookup:
        return _art_lookup[key]
    found = None
    for art_id in dict.fromkeys(ids):               # sem repetir, mantendo a ordem
        for ext in ART_EXTENSIONS:
            found = load_gif(f"images/{folder}/{art_id}{ext}", size - 8, size - 8)
            if found is not None:
                break
        if found is not None:
            break
    _art_lookup[key] = found
    return found


def _super_frame(surface, pos, size):
    """SUPER BOSS: moldura dourada e vermelha que pulsa (por cima da arte)."""
    pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 280.0)
    pygame.draw.rect(surface, (255, int(150 + 80 * pulse), 50), (pos[0], pos[1], size, size), width=4, border_radius=14)
    pygame.draw.rect(surface, (230, 50, 60), (pos[0] - 4, pos[1] - 4, size + 8, size + 8), width=2, border_radius=18)


def draw_portrait(surface, pos, size, entity):
    """Desenha o retrato de 'entity' (Player ou Enemy), com o canto superior esquerdo em 'pos'."""
    _draw_portrait(surface, pos, size, entity)
    if getattr(entity, "is_super", False):
        _super_frame(surface, pos, size)


def _draw_portrait(surface, pos, size, entity):
    # 1) GIF/animação em assets/images/<pasta>/<id>.gif (se existir)
    animation = _find_animation(entity, size)
    if animation is not None:
        color = tuple(entity.color)
        key = ("gifframe", size, color)
        frame_bg = _cache.get(key)
        if frame_bg is None:
            frame_bg = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.rect(frame_bg, (26, 26, 40), (0, 0, size, size), border_radius=14)
            pygame.draw.rect(frame_bg, _shade(color, 20), (0, 0, size, size), width=3, border_radius=14)
            _cache[key] = frame_bg
        surface.blit(frame_bg, pos)
        frame = animation.frame_at(pygame.time.get_ticks())
        surface.blit(frame, (pos[0] + (size - frame.get_width()) // 2,
                             pos[1] + (size - frame.get_height()) // 2))
        return

    # 2) desenho provisório
    kind = portrait_kind(entity)
    color = tuple(entity.color)
    boss = bool(getattr(entity, "is_boss", False))
    if kind == "boss":                       # boss usa o desenho do seu "tipo" por nome
        kind = {"Rainha Aranha": "spider", "Lorde Goblin": "goblin", "Arquimago Sombrio": "mage_enemy",
                "Golem Colossal": "golem"}.get(entity.name, "golem")
    key = (kind, size, color, boss)
    image = _cache.get(key)
    if image is None:
        image = _paint(kind, size, color, boss)
        _cache[key] = image
    surface.blit(image, pos)
