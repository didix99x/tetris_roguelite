"""
ui/boss_warning.py - MENSAGEM DE APARIÇÃO do boss (ex.: "CUIDADO! VOCÊ ENCONTROU YOSHI, O REI DO TETRIS").

SÓ DESENHO. O texto e a duração vêm do JSON do boss (data/enemies.json > yoshi > infinite > appearance_message).
Aparência (cor, tamanhos, tempo da animação): constantes no topo deste arquivo.
"""
import math

import pygame

import config
from ui.widgets import render_text

COLOR = (255, 45, 45)            # vermelho da mensagem
GLOW = (120, 10, 15)             # contorno escuro atrás do texto
BAND = (30, 0, 4)                # faixa escura atrás
BIG_SIZE, SMALL_SIZE = 88, 46    # tamanho da 1ª linha ("CUIDADO!") e da 2ª
ENTER_TIME = 0.45                # duração da animação de entrada (s)
FADE_TIME = 0.7                  # duração do desaparecimento (s)
CENTER_Y = 192                   # posição vertical (acima do nome do boss)


class AppearanceWarning:
    def __init__(self, text, seconds=4.0):
        head, _, rest = text.partition("! ")
        self.lines = [(head + "!", BIG_SIZE), (rest, SMALL_SIZE)] if rest else [(text, SMALL_SIZE + 10)]
        self.seconds = float(seconds)
        self.t = 0.0
        self.band = pygame.Surface((config.SCREEN_WIDTH, 150), pygame.SRCALPHA)

    @property
    def active(self):
        return self.t < self.seconds

    def update(self, dt):
        self.t += dt

    def draw(self, surface):
        if not self.active:
            return
        t = self.t
        enter = min(1.0, t / ENTER_TIME)
        fade = min(1.0, (self.seconds - t) / FADE_TIME)
        ease = 1.0 - (1.0 - enter) ** 3
        scale = 2.4 - 1.4 * ease                                  # entra grande e "encaixa"
        shake = (1.0 - enter) * 12 + (4 if t < 0.9 else 0) * max(0.0, 1 - t)
        alpha = int(190 * min(1.0, enter * 2) * fade)
        self.band.fill((*BAND, max(0, alpha)))
        surface.blit(self.band, (0, CENTER_Y - 75))
        pulse = 0.85 + 0.15 * math.sin(t * 9)
        color = tuple(int(c * pulse) for c in COLOR)
        total_h = sum(int(size * 0.8) for _, size in self.lines)
        y = CENTER_Y - total_h // 2 + 6
        for text, size in self.lines:
            image = render_text(text, size, color)
            shadow = render_text(text, size, GLOW)
            w, h = image.get_size()
            nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
            if (nw, nh) != (w, h):
                image, shadow = pygame.transform.scale(image, (nw, nh)), pygame.transform.scale(shadow, (nw, nh))
            ox = int(math.sin(t * 60) * shake)
            cx = config.SCREEN_WIDTH // 2 + ox
            for dx, dy in ((-3, 3), (3, 3), (0, 5)):
                self._blit(surface, shadow, cx + dx, y + dy, fade)
            self._blit(surface, image, cx, y, fade)
            y += int(size * 0.8)

    @staticmethod
    def _blit(surface, image, cx, cy, fade):
        if fade < 1.0:
            image = image.copy()
            image.set_alpha(int(255 * max(0.0, fade)))
        surface.blit(image, (cx - image.get_width() // 2, cy - image.get_height() // 2))
