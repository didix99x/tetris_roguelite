"""
ui/hud.py - HUD (interface durante a batalha). SÓ DESENHA: não altera nada do combate.

Onde mudar cada coisa (detalhes em COMO_EDITAR_O_JOGO.md > "Visual: HUD e efeitos"):
  posições e tamanhos -> ui/theme.py (seção 3)       cores e fonte -> ui/theme.py (seções 1 e 2)
  barras (degradê, brilho, rastro)  -> ui/widgets.py > draw_bar
  painéis e caixas                  -> ui/widgets.py > draw_panel / draw_inner_box
  ícones                            -> ui/icons.py

Blocos (base 1280x720):
  topo:     placa do inimigo (nome, vida, passiva)
  esquerda: painel do jogador (retrato, vida, energia, habilidade, passiva)
  direita:  painel do andar (retrato do inimigo, chain, próximo ataque, efeitos, bônus)
  embaixo:  teclas
"""
import math

import pygame

import config
from ui import icons, theme
from ui.portraits import draw_portrait
from ui.widgets import (draw_bar, draw_inner_box, draw_panel, draw_text, draw_wrapped, reset_bar_animation,
                        wrap_text)

_last_combat = None


def draw_hud(surface, combat, run):
    global _last_combat
    if combat is not _last_combat:            # nova batalha: zera o "rastro" das barras
        reset_bar_animation()
        _last_combat = combat
    _draw_enemy(surface, combat)
    _draw_player(surface, combat)
    _draw_right_panel(surface, combat, run)
    _draw_hints(surface)


# ---------------------------------------------------------------- peças
def _pulse(speed=260.0):
    return 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / speed)


def _mix(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def _chip(surface, text, size, color, anchor, pos, icon=None):
    """Etiqueta arredondada (ex.: BOSS). Devolve o retângulo desenhado."""
    img = pygame.Rect(0, 0, 0, 0)
    from ui.widgets import render_text
    label = render_text(text, size, color)
    pad, icon_w = 9, (size - 2 if icon else 0)
    rect = pygame.Rect(0, 0, label.get_width() + pad * 2 + icon_w + (4 if icon else 0), size + 8)
    setattr(rect, anchor, pos)
    pygame.draw.rect(surface, _mix(color, (14, 14, 22), 0.82), rect, border_radius=rect.height // 2)
    pygame.draw.rect(surface, color, rect, width=2, border_radius=rect.height // 2)
    tx = rect.x + pad
    if icon:
        icons.draw_icon(surface, icon, (tx + icon_w // 2, rect.centery), icon_w, color)
        tx += icon_w + 4
    surface.blit(label, (tx, rect.centery - label.get_height() // 2))
    return rect


def _portrait_frame(surface, box, color, spread=10):
    """Brilho suave em volta do retrato (anéis que vão se misturando ao painel)."""
    x, y, size = box
    base = (33, 33, 50)
    for i, k in enumerate((0.10, 0.18, 0.30, 0.45)):
        pad = spread - i * max(1, spread // 5)
        pygame.draw.rect(surface, _mix(base, color, k), (x - pad - 4, y - pad - 4, size + 2 * pad + 8, size + 2 * pad + 8),
                         width=3, border_radius=18 + pad)


# ---------------------------------------------------------------- inimigo (topo)
def _draw_enemy(surface, combat):
    enemy = combat.enemy
    draw_panel(surface, theme.ENEMY_PLATE)
    is_super = getattr(enemy, "is_super", False)
    color = enemy.color if enemy.is_boss else theme.TEXT
    name_rect = draw_text(surface, enemy.name.upper(), 34, color, (640, theme.ENEMY_NAME_Y), shadow=True)
    if enemy.is_boss:
        tag, tag_color = ("SUPER BOSS", theme.SUPER_TAG) if is_super else ("BOSS", theme.BOSS_TAG)
        _chip(surface, tag, 20, tag_color, "midright", (name_rect.left - 12, theme.ENEMY_NAME_Y),
              icon="skull" if is_super else "crown")
    draw_bar(surface, theme.ENEMY_BAR, enemy.hp, enemy.max_hp, theme.ENEMY_HP, f"{enemy.hp} / {enemy.max_hp}", key="enemy_hp")
    label = enemy.passive_label()
    if label:
        lines = wrap_text(label, 21, 580)
        draw_text(surface, lines[0] if len(lines) == 1 else lines[0] + "...", 21, theme.TEXT_MUTED, (640, theme.ENEMY_PASSIVE_Y))


# ---------------------------------------------------------------- jogador (esquerda)
def _draw_player(surface, combat):
    player = combat.player
    x, y, w, h = theme.LEFT_PANEL
    draw_panel(surface, theme.LEFT_PANEL)
    draw_text(surface, player.name.upper(), 32, theme.ACCENT, (x + w // 2, y + 20), shadow=True)
    pygame.draw.line(surface, theme.PANEL_BORDER, (x + 24, y + 38), (x + w - 24, y + 38))
    px, py, ps = theme.PLAYER_PORTRAIT
    _portrait_frame(surface, theme.PLAYER_PORTRAIT, player.color)
    draw_portrait(surface, (px, py), ps, player)

    hp = int(round(player.hp))
    low = hp > 0 and hp <= player.max_hp * 0.3
    bx, by, bw, bh = theme.PLAYER_HP_BAR
    draw_text(surface, "VIDA", 22, theme.TEXT_MUTED, (50, by - 22), "topleft")
    draw_bar(surface, theme.PLAYER_HP_BAR, hp, player.max_hp, theme.HP_LOW if low else theme.HP, f"{hp} / {player.max_hp}",
             key="player_hp", glow=theme.HP_LOW if low else None, icon=(icons.draw_heart, (235, 80, 95)))

    cost = player.current_ability_cost()
    ex, ey, ew, eh = theme.PLAYER_ENERGY_BAR
    draw_text(surface, "ENERGIA", 22, theme.TEXT_MUTED, (50, ey - 22), "topleft")
    draw_bar(surface, theme.PLAYER_ENERGY_BAR, player.energy, player.energy_max, theme.ENERGY,
             f"{int(player.energy)} / {player.energy_max}", key="player_energy",
             marker=min(0.99, cost / player.energy_max) if player.energy_max else None,
             icon=(icons.draw_bolt, (255, 220, 90)))

<<<<<<< HEAD
    _draw_ability_box(surface, player, cost, getattr(combat, "ability_cd", 0.0))
=======
    _draw_ability_box(surface, player, cost)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

    ox, oy, ow, oh = theme.PASSIVE_BOX
    draw_inner_box(surface, theme.PASSIVE_BOX)
    draw_text(surface, "PASSIVA", 20, theme.TEXT_MUTED, (ox + 14, oy + 10), "topleft")
    draw_text(surface, player.passive_name, 26, theme.TEXT, (ox + 14, oy + 30), "topleft")
    draw_wrapped(surface, player.passive_text, 21, theme.TEXT_MUTED, (ox + 14, oy + 58), ow - 28, 21)


<<<<<<< HEAD
def _draw_ability_box(surface, player, cost, cooldown=0.0):
    ax, ay, aw, ah = theme.ABILITY_BOX
    ready = player.can_use_ability() and cooldown <= 0
=======
def _draw_ability_box(surface, player, cost):
    ax, ay, aw, ah = theme.ABILITY_BOX
    ready = player.can_use_ability()
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    draw_inner_box(surface, theme.ABILITY_BOX, glow=theme.READY if ready else None)
    badge = (ax + 32, ay + ah // 2)
    badge_color = theme.READY if ready else player.color
    pygame.draw.circle(surface, _mix(badge_color, (14, 14, 22), 0.75), badge, 22)
    pygame.draw.circle(surface, badge_color if ready else _mix(badge_color, (60, 60, 80), 0.4), badge, 22, 3)
    icons.draw_icon(surface, "sparkle", badge, 24 + int(4 * _pulse(200.0)) if ready else 22,
                    (255, 255, 255) if ready else _mix(badge_color, (255, 255, 255), 0.4))
    draw_text(surface, "HABILIDADE", 19, theme.TEXT_MUTED, (ax + 66, ay + 9), "topleft")
    draw_text(surface, player.ability_name, 27, theme.TEXT, (ax + 66, ay + 26), "topleft")
<<<<<<< HEAD
    if cooldown > 0:                                                  # recarga: tempo restante + barrinha
        draw_text(surface, f"RECARGA  {cooldown:.1f}s", 27, (255, 190, 90), (ax + 66, ay + 54), "topleft", shadow=True)
        frac = max(0.0, min(1.0, 1.0 - cooldown / max(0.001, config.ABILITY_COOLDOWN)))
        pygame.draw.rect(surface, (40, 40, 60), (ax + 66, ay + ah - 9, aw - 80, 4), border_radius=2)
        pygame.draw.rect(surface, (255, 190, 90), (ax + 66, ay + ah - 9, int((aw - 80) * frac), 4), border_radius=2)
    elif ready:
=======
    if ready:
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        draw_text(surface, "PRONTA  [Q]", 27, _mix(theme.READY, (255, 255, 255), 0.25 * _pulse(220.0)), (ax + 66, ay + 54),
                  "topleft", shadow=True)
    else:
        missing = max(0, int(math.ceil(cost - player.energy)))
        draw_text(surface, f"Custo {cost}  -  faltam {missing}", 23, theme.TEXT_MUTED, (ax + 66, ay + 57), "topleft")


# ---------------------------------------------------------------- andar e inimigo (direita)
def _draw_right_panel(surface, combat, run):
    x, y, w, h = theme.RIGHT_PANEL
    draw_panel(surface, theme.RIGHT_PANEL)
    cx = x + w // 2
    if run.last_floor is None:
        draw_text(surface, f"ANDAR {run.floor_number}", 34, theme.ACCENT, (cx - 38, y + 18), shadow=True)
        _chip(surface, "INFINITO", 18, (150, 190, 255), "midleft", (cx + 40, y + 18), icon="sparkle")
    else:
        draw_text(surface, f"ANDAR {run.floor_number} / {run.last_floor}", 34, theme.ACCENT, (cx, y + 17), shadow=True)
        track = pygame.Rect(x + 40, y + 32, w - 80, 4)                          # progresso da torre
        pygame.draw.rect(surface, (20, 20, 32), track, border_radius=3)
        fill = max(5, int(track.width * min(1.0, run.floor_number / max(1, run.last_floor))))
        pygame.draw.rect(surface, theme.ACCENT, (track.x, track.y, fill, track.height), border_radius=3)
    ex, ey, es = theme.ENEMY_PORTRAIT
    enemy = combat.enemy
    ring = theme.SUPER_TAG if getattr(enemy, "is_super", False) else (enemy.color if enemy.is_boss else (90, 90, 130))
    _portrait_frame(surface, theme.ENEMY_PORTRAIT, ring, spread=6)
    draw_portrait(surface, (ex, ey), es, enemy)

    _draw_chain(surface, combat)

    ax, ay, aw, ah = theme.ATTACK_BAR_RECT
    progress = combat.enemy_progress()
    danger = progress > 0.8
    draw_text(surface, "PRÓXIMO ATAQUE", 21, theme.TEXT_MUTED, (ax + 26, ay - 22), "topleft")
    icons.draw_clock(surface, (ax + 8, ay - 11), 15, theme.ATTACK_BAR_DANGER if danger else theme.TEXT_MUTED)
    draw_bar(surface, theme.ATTACK_BAR_RECT, progress, 1.0, theme.ATTACK_BAR_DANGER if danger else theme.ATTACK_BAR,
             key=None, glow=theme.ATTACK_BAR_DANGER if danger else None)

    top = theme.EFFECTS_TOP
    draw_text(surface, "EFEITOS", 21, theme.TEXT_MUTED, (940, top), "topleft")
    effects = combat.status_effects()
    if not effects:
        draw_text(surface, "nenhum", 21, theme.TEXT_DIM, (940, top + 26), "topleft")
    for i, text in enumerate(effects[:3]):
        row_y = top + 36 + i * 25
        icon, color = icons.status_icon(text)
        pygame.draw.rect(surface, (40, 28, 34), (936, row_y - 12, 298, 23), border_radius=7)
        icons.draw_icon(surface, icon, (952, row_y), 16, color)
        draw_text(surface, text, 22, theme.STATUS, (968, row_y), "midleft")

    top = theme.BONUS_TOP
    draw_text(surface, "BÔNUS DA RUN", 21, theme.TEXT_MUTED, (940, top), "topleft")
    lines = combat.player.mod_lines()
    if not lines:
        draw_text(surface, "nenhum ainda", 21, theme.TEXT_DIM, (940, top + 26), "topleft")
    shown = lines if len(lines) <= 5 else lines[:4] + [f"+{len(lines) - 4} outros bônus"]
    for i, text in enumerate(shown):
        row_y = top + 34 + i * 21
        icons.draw_diamond(surface, (948, row_y), 7, theme.BONUS)
        draw_text(surface, text, 21, theme.BONUS, (960, row_y), "midleft")


def _draw_chain(surface, combat):
    level = combat.chain_level if combat.chain.count > 0 and combat.source == "player" else (
        combat.chain_display_level if combat.chain_display_time > 0 else 0)
    cx, cy = theme.CHAIN_CENTER
    pill = pygame.Rect(0, 0, 190, 40)
    pill.center = (cx, cy)
    if level >= 2:
        glow = _pulse(150.0)
        pygame.draw.rect(surface, _mix((60, 45, 14), theme.ACCENT, 0.25 * glow), pill.inflate(8, 8), border_radius=24)
        pygame.draw.rect(surface, (44, 34, 14), pill, border_radius=20)
        pygame.draw.rect(surface, theme.ACCENT, pill, width=3, border_radius=20)
        draw_text(surface, f"CHAIN x{level}", 36, theme.ACCENT, pill.center, shadow=True)
    elif level == 1:
        pygame.draw.rect(surface, (30, 30, 46), pill, border_radius=20)
        pygame.draw.rect(surface, (120, 120, 150), pill, width=2, border_radius=20)
        draw_text(surface, "CHAIN x1", 30, theme.TEXT, pill.center)
    else:
        pygame.draw.rect(surface, (24, 24, 38), pill, border_radius=20)
        pygame.draw.rect(surface, (50, 50, 72), pill, width=2, border_radius=20)
        draw_text(surface, "CHAIN", 26, (90, 90, 110), pill.center)


# ---------------------------------------------------------------- teclas (embaixo)
_HINTS = (("Setas/WASD", "mover"), ("Enter/Espaço", "trocar"), ("Q", "habilidade"), ("Esc", "pausa"))
<<<<<<< HEAD
_PAD_KIND = [None]          # tipo do controle EM USO ("xbox", "ps") ou None (a barra mostra o teclado)
_PAD_LABELS = [None]        # botões configurados (mostrados na barra); None = padrão do tipo


def set_gamepad_kind(kind, labels=None):
    """Chamado pelo jogo: se o jogador está usando o controle, a barra de baixo mostra os botões dele
    (já com o remapeamento). `labels` = Input.pad_labels(). Com teclado/mouse a barra continua sendo a do teclado."""
    _PAD_KIND[0] = kind
    _PAD_LABELS[0] = labels


def _hints():
    if _PAD_KIND[0] is None:
        return _HINTS
    from game.input import PAD_PROMPTS
    p = _PAD_LABELS[0] or PAD_PROMPTS[_PAD_KIND[0]]
    return ((p["move"], "mover"), (p["swap"], "trocar"), (p["ability"], "habilidade"), (p["back"], "pausa"))
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f


def _draw_hints(surface):
    from ui.widgets import render_text
    items, total = [], 0
<<<<<<< HEAD
    for key, label in _hints():
=======
    for key, label in _HINTS:
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        k, t = render_text(key, 19, theme.TEXT), render_text(label, 20, theme.TEXT_MUTED)
        items.append((k, t))
        total += k.get_width() + 16 + 8 + t.get_width() + 30
    x = (config.SCREEN_WIDTH - (total - 30)) // 2
    y = theme.HINT_Y
    for k, t in items:
        cap = pygame.Rect(x, y - 12, k.get_width() + 16, 24)
        pygame.draw.rect(surface, (46, 46, 66), cap, border_radius=6)
        pygame.draw.rect(surface, (96, 96, 128), cap, width=2, border_radius=6)
        pygame.draw.line(surface, (20, 20, 32), (cap.x + 4, cap.bottom - 2), (cap.right - 4, cap.bottom - 2), 2)
        surface.blit(k, (cap.x + 8, cap.centery - k.get_height() // 2))
        x = cap.right + 8
        surface.blit(t, (x, y - t.get_height() // 2))
        x += t.get_width() + 30
