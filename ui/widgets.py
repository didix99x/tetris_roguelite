"""ui/widgets.py - funções de desenho reutilizáveis (texto, barras, botões)."""
import math
import os

import pygame

import config
from ui import theme

_fonts = {}
_text_cache = {}
_fill_cache = {}
_panel_cache = {}
_bar_state = {}          # animação das barras: chave -> [valor mostrado, último instante em ms]


def get_font(size):
    """Fonte do jogo. Para trocar a fonte/tamanho geral, edite FONT_PATH e FONT_SCALE em ui/theme.py."""
    font = _fonts.get(size)
    if font is None:
        path = theme.FONT_PATH
        if path and not os.path.isabs(path):
            path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path)
        px = max(8, int(size * theme.FONT_SCALE))
        try:
            font = pygame.font.Font(path if path and os.path.exists(path) else None, px)
        except (OSError, RuntimeError):
            font = pygame.font.Font(None, px)
        _fonts[size] = font
    return font


def render_text(text, size, color):
    """Texto já renderizado (com cache, para não refazer a cada frame)."""
    key = (text, size, color)
    image = _text_cache.get(key)
    if image is None:
        if len(_text_cache) > 600:
            _text_cache.clear()
        image = get_font(size).render(text, True, color)
        _text_cache[key] = image
    return image


def draw_text(surface, text, size, color, pos, anchor="center", shadow=False):
    """Desenha texto. 'anchor' diz qual ponto do texto fica em 'pos'
    (center, topleft, topright, midtop, midleft, midright...). shadow=True põe uma sombra (mais legível)."""
    image = render_text(text, size, color)
    rect = image.get_rect()
    setattr(rect, anchor, pos)
    if shadow:
        surface.blit(render_text(text, size, (0, 0, 0)), rect.move(1, 2))
    surface.blit(image, rect)
    return rect


def wrap_text(text, size, max_width):
    """Quebra um texto em linhas que cabem em max_width pixels."""
    font = get_font(size)
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(surface, text, size, color, topleft, max_width, line_height=None):
    """Desenha texto com quebra de linha. Devolve o Y logo abaixo do texto."""
    line_height = line_height or size + 4
    x, y = topleft
    for line in wrap_text(text, size, max_width):
        draw_text(surface, line, size, color, (x, y), "topleft")
        y += line_height
    return y


def _lerp(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def _lighter(color, amount):
    return tuple(min(255, c + amount) for c in color)


def _darker(color, amount):
    return tuple(max(0, c - amount) for c in color)


def _row_inset(row, height, radius):
    """Quanto a linha 'row' entra para dentro por causa do canto arredondado."""
    if radius <= 0:
        return 0
    if row < radius:
        dy = radius - row - 0.5
    elif row >= height - radius:
        dy = row - (height - radius) + 0.5
    else:
        return 0
    return int(round(radius - math.sqrt(max(0.0, radius * radius - dy * dy))))


def gradient_fill(width, height, top, bottom, radius=6):
    """Superfície com degradê vertical e cantos arredondados (guardada em cache)."""
    key = (width, height, top, bottom, radius)
    surf = _fill_cache.get(key)
    if surf is None:
        if len(_fill_cache) > 500:
            _fill_cache.clear()
        surf = pygame.Surface((max(1, width), max(1, height)), pygame.SRCALPHA)
        radius = min(radius, height // 2, width // 2)
        for row in range(height):
            inset = _row_inset(row, height, radius)
            color = _lerp(top, bottom, row / max(1, height - 1))
            pygame.draw.line(surf, color, (inset, row), (width - 1 - inset, row))
        _fill_cache[key] = surf
    return surf


def reset_bar_animation():
    """Zera o 'rastro' das barras (chamado ao começar uma nova batalha)."""
    _bar_state.clear()


def _animated_value(key, value):
    """Valor suavizado de uma barra: sobe rápido, desce devagar (mostra o rastro do dano). Só visual."""
    now = pygame.time.get_ticks()
    state = _bar_state.get(key)
    if state is None:
        _bar_state[key] = [float(value), now]
        return float(value)
    shown, last = state
    dt = max(0.0, min(0.1, (now - last) / 1000.0))
    if value >= shown:
        shown = float(value)
    else:
        shown = max(float(value), shown - (shown - value) * min(1.0, dt * 3.0))
        if shown - value < 0.5:
            shown = float(value)
    state[0], state[1] = shown, now
    return shown


def draw_bar(surface, rect, value, max_value, color, label=None, key=None, marker=None, glow=None, icon=None):
    """Barra de vida/energia (estilo novo). Os 6 primeiros parâmetros são os de sempre.
    key    : nome único -> liga o "rastro" que mostra o dano recebido (só visual)
    marker : fração 0..1 onde desenhar uma marcação (ex.: custo da habilidade na barra de energia)
    glow   : cor de um brilho pulsante na borda (ex.: vida baixa)
    icon   : (função_de_ícone, cor) desenhado à esquerda, fora da barra"""
    rect = pygame.Rect(rect)
    radius = min(7, rect.height // 2)
    pygame.draw.rect(surface, theme.BAR_BACK, rect, border_radius=radius)
    pygame.draw.rect(surface, (30, 30, 46), rect.inflate(-4, -4), border_radius=max(1, radius - 2))
    fraction = 0.0 if max_value <= 0 else max(0.0, min(1.0, value / max_value))
    inner_w = rect.width - 4
    if key is not None and max_value > 0:
        shown = max(0.0, min(1.0, _animated_value(key, value) / max_value))
        if shown > fraction + 0.002:
            trail_w = int(inner_w * shown)
            surface.blit(gradient_fill(trail_w, rect.height - 4, theme.BAR_TRAIL, _darker(theme.BAR_TRAIL, 60), radius - 2),
                         (rect.x + 2, rect.y + 2))
    if fraction > 0:
        fill_w = max(6, int(inner_w * fraction))
        fill_h = rect.height - 4
        surface.blit(gradient_fill(fill_w, fill_h, _lighter(color, 55), _darker(color, 45), radius - 2), (rect.x + 2, rect.y + 2))
        gloss = pygame.Rect(rect.x + 5, rect.y + 4, max(1, fill_w - 6), max(1, fill_h // 3))
        pygame.draw.rect(surface, _lighter(color, 95), gloss, border_radius=max(1, gloss.height // 2))
        pygame.draw.rect(surface, _lighter(color, 130), (rect.x + 2 + fill_w - 3, rect.y + 5, 2, max(1, fill_h - 6)))
    for tick in range(1, 10):                                   # divisões a cada 10%
        tx = rect.x + 2 + int(inner_w * tick / 10)
        pygame.draw.line(surface, (20, 20, 32), (tx, rect.y + rect.height - 6), (tx, rect.y + rect.height - 3))
    if marker is not None and 0.0 < marker < 1.0:
        mx = rect.x + 2 + int(inner_w * marker)
        reached = fraction >= marker
        mark = (255, 235, 140) if reached else (225, 225, 240)
        pygame.draw.polygon(surface, mark, [(mx - 4, rect.y - 6), (mx + 4, rect.y - 6), (mx, rect.y)])
        pygame.draw.line(surface, mark, (mx, rect.bottom - 3), (mx, rect.bottom + 3), 2)
    border = theme.BAR_BORDER
    if glow:
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 140.0)
        border = _lerp(theme.BAR_BORDER, glow, 0.5 + 0.5 * pulse)
        pygame.draw.rect(surface, _darker(glow, 120), rect.inflate(6, 6), width=2, border_radius=radius + 3)
    pygame.draw.rect(surface, border, rect, width=2, border_radius=radius)
    if icon:
        icon[0](surface, (rect.x - 14, rect.centery), min(18, rect.height), icon[1])
    if label:
        draw_text(surface, label, max(18, rect.height - 6), config.TEXT_COLOR, rect.center, shadow=True)


def draw_panel(surface, rect, color=config.PANEL_COLOR, border=(70, 70, 95)):
    """Painel com sombra suave, degradê e brilho no topo. (Assinatura igual à antiga.)"""
    rect = pygame.Rect(rect)
    if color == config.PANEL_COLOR:
        top, bottom = theme.PANEL_TOP, theme.PANEL_BOTTOM
    else:
        top, bottom = _lighter(color, 8), _darker(color, 8)
    shadow = pygame.Rect(rect.x + 3, rect.y + 6, rect.width, rect.height)
    pygame.draw.rect(surface, theme.SHADOW, shadow, border_radius=14)
    surface.blit(gradient_fill(rect.width, rect.height, top, bottom, 12), rect.topleft)
    pygame.draw.rect(surface, border, rect, width=2, border_radius=12)
    pygame.draw.line(surface, _lighter(top, 26), (rect.x + 14, rect.y + 2), (rect.right - 14, rect.y + 2))


def draw_inner_box(surface, rect, border=None, glow=None):
    """Caixa interna (habilidade, passiva...), mais escura que o painel."""
    rect = pygame.Rect(rect)
    pygame.draw.rect(surface, theme.PANEL_INNER, rect, border_radius=9)
    if glow:
        pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 170.0)
        pygame.draw.rect(surface, _darker(glow, 150 - int(60 * pulse)), rect.inflate(6, 6), width=3, border_radius=12)
    pygame.draw.rect(surface, glow or border or theme.PANEL_INNER_BORDER, rect, width=2, border_radius=9)


class ButtonList:
    """Lista vertical de botões controlada por teclado e mouse."""

    def __init__(self, labels, center_x=640, start_y=320, width=380, height=56, gap=18, disabled=()):
        self.labels = list(labels)
        self.disabled = set(disabled)     # índices bloqueados: aparecem, mas o menu não os abre
        self.selected = 0
        self.rects = [pygame.Rect(center_x - width // 2, start_y + i * (height + gap), width, height)
                      for i in range(len(self.labels))]

    def handle(self, inp, audio=None):
        """Devolve o índice escolhido (Enter ou clique) ou None."""
        if inp.pressed("up"):
            self.selected = (self.selected - 1) % len(self.labels)
            if audio:
                audio.play("select")
        if inp.pressed("down"):
            self.selected = (self.selected + 1) % len(self.labels)
            if audio:
                audio.play("select")
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(inp.mouse_pos):
                self.selected = i
            if inp.click and rect.collidepoint(inp.click):
                return i
        if inp.pressed("swap"):
            return self.selected
        return None

    def draw(self, surface):
        for i, rect in enumerate(self.rects):
            active = i == self.selected
            locked = i in self.disabled
            pygame.draw.rect(surface, (60, 60, 90) if active else (35, 35, 55), rect, border_radius=10)
            pygame.draw.rect(surface, (110, 110, 125) if (locked and active) else
                             (config.ACCENT_COLOR if active else (80, 80, 110)),
                             rect, width=3 if active else 2, border_radius=10)
            if locked:
                draw_text(surface, self.labels[i], 30, (120, 120, 140), (rect.centerx, rect.centery - 8))
                draw_text(surface, "BLOQUEADO", 20, (200, 120, 110), (rect.centerx, rect.centery + 16))
            else:
                draw_text(surface, self.labels[i], 34,
                          config.ACCENT_COLOR if active else config.TEXT_COLOR, rect.center)


def draw_lock(surface, center, size, color=(240, 200, 90)):
    """Cadeado desenhado com formas (a fonte padrão não tem o símbolo)."""
    cx, cy = center
    w, h = int(size * 0.7), int(size * 0.5)
    body = pygame.Rect(cx - w // 2, cy - h // 4, w, h)
    sh_w = int(w * 0.6)
    pygame.draw.arc(surface, color, (cx - sh_w // 2, cy - h // 4 - int(size * 0.38), sh_w, int(size * 0.7)),
                    0, 3.14159, max(2, size // 9))
    pygame.draw.rect(surface, color, body, border_radius=max(2, size // 10))
    pygame.draw.circle(surface, (30, 30, 40), (cx, cy + h // 8), max(2, size // 10))


def draw_tooltip(surface, mouse_pos, title, text, locked=True, width=320):
    """Caixa de informação perto do mouse (título com cadeado + texto com quebra de linha)."""
    lines = wrap_text(text, 24, width - 24)
    height = 52 + 26 * len(lines)
    x = min(mouse_pos[0] + 18, config.SCREEN_WIDTH - width - 8)
    y = min(mouse_pos[1] + 18, config.SCREEN_HEIGHT - height - 8)
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (20, 20, 34), rect, border_radius=8)
    pygame.draw.rect(surface, config.ACCENT_COLOR, rect, width=2, border_radius=8)
    tx = x + 12
    if locked:
        draw_lock(surface, (x + 22, y + 24), 22)
        tx = x + 40
    draw_text(surface, title, 26, config.ACCENT_COLOR, (tx, y + 12), "topleft")
    for i, line in enumerate(lines):
        draw_text(surface, line, 24, config.TEXT_COLOR, (x + 12, y + 46 + i * 26), "topleft")
