"""
ui/unlock_screen.py - TELA EXCLUSIVA de PERSONAGEM DESBLOQUEADO.

Aparece logo depois de derrotar um personagem (Modo Infinito), ANTES da escolha de cartas. É uma tela
inteira (não é um texto por cima das cartas), então nada da batalha, das cartas ou da HUD fica na frente.
Animação: raios e anéis, retrato que desce com brilho, confetes, mensagem de comemoração.
O jogador só continua depois da animação (Enter, clique ou o botão de confirmar do controle).
"""
import math
import random
import types

import pygame

import config
from characters import character_title
from game.state import GameState
from ui.portraits import draw_portrait
from ui.widgets import draw_panel, draw_text

PORTRAIT = 220
ANIMATION_TIME = 1.6          # segundos até aceitar "continuar"
CONFETTI = ((255, 215, 90), (140, 230, 255), (255, 120, 170), (150, 255, 160))


def _ease_out(x):
    x = max(0.0, min(1.0, x))
    return 1.0 - (1.0 - x) ** 3


def _who(char_id, data):
    return types.SimpleNamespace(char_id=char_id, color=tuple(data.get("color", (150, 150, 150))),
                                 name=data["name"], image_id=data.get("image"))


class UnlockScreen:
    def __init__(self, game, next_state, next_kwargs=None):
        self.game = game
        self.next_state = next_state
        self.next_kwargs = next_kwargs or {}
        self.queue = list(game.pending_unlocks)
        game.pending_unlocks = []                     # esta tela cuida deles; não aparecem de novo
        self.total = max(1, len(self.queue))
        self.rng = random.Random(7)
        self.confetti = []
        self._start_current()
        game.audio.play("win")

    # ------------------------------------------------------------ personagem atual
    def _start_current(self):
        self.t = 0.0
        self.char_id = self.queue[0] if self.queue else None
        self.confetti = [[self.rng.uniform(0, config.SCREEN_WIDTH), self.rng.uniform(-400, 0),
                          self.rng.uniform(-30, 30), self.rng.uniform(90, 220), self.rng.choice(CONFETTI),
                          self.rng.uniform(0, 6.28)] for _ in range(90)]

    def _finish_current(self):
        if self.queue:
            self.queue.pop(0)
        if self.queue:
            self._start_current()
            self.game.audio.play("win")
            return
        self.game.change_state(self.next_state, **self.next_kwargs)

    # ------------------------------------------------------------ loop
    def handle_input(self, inp):
        if self.t < ANIMATION_TIME:                   # durante a animação nenhum comando faz a tela sumir
            return
        if inp.pressed("swap") or inp.click:
            self._finish_current()

    def update(self, dt):
        self.t += dt
        for c in self.confetti:
            c[0] += (c[2] + math.sin(self.t * 3 + c[5]) * 40) * dt
            c[1] += c[3] * dt
            if c[1] > config.SCREEN_HEIGHT + 10:
                c[1] = -10

    def draw(self, surface):
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        surface.fill((10, 12, 28))
        if self.char_id is None:
            return
        data = self.game.data["characters"][self.char_id]
        cx, cy = w // 2, 300
        t = self.t
        # raios girando
        spin = t * 0.35
        for i in range(16):
            a0 = spin + i * (math.tau / 16)
            a1 = a0 + math.tau / 32
            r = 900
            pts = [(cx, cy), (cx + math.cos(a0) * r, cy + math.sin(a0) * r), (cx + math.cos(a1) * r, cy + math.sin(a1) * r)]
            shade = 30 + int(14 * math.sin(t * 2 + i))
            pygame.draw.polygon(surface, (shade, shade + 10, shade + 40), pts)
        # anéis que se expandem
        for k in range(4):
            phase = (t * 0.6 + k * 0.25) % 1.0
            radius = int(60 + phase * 420)
            level = int(200 * (1 - phase))
            pygame.draw.circle(surface, (level // 2, level, min(255, level + 40)), (cx, cy), radius, 3)
        # confetes
        for x, y, _, _, color, _ in self.confetti:
            pygame.draw.rect(surface, color, (int(x), int(y), 6, 10))
        # retrato: desce com brilho
        slide = _ease_out(t / 0.9)
        py = int(cy - PORTRAIT // 2 - (1 - slide) * 260)
        glow = 0.5 + 0.5 * math.sin(t * 4)
        pygame.draw.circle(surface, (40 + int(40 * glow), 60 + int(60 * glow), 110), (cx, py + PORTRAIT // 2), PORTRAIT // 2 + 34, 0)
        draw_portrait(surface, (cx - PORTRAIT // 2, py), PORTRAIT, _who(self.char_id, data))
        pygame.draw.rect(surface, config.ACCENT_COLOR, (cx - PORTRAIT // 2 - 4, py - 4, PORTRAIT + 8, PORTRAIT + 8), width=4, border_radius=10)
        # textos
        appear = _ease_out((t - 0.5) / 0.6)
        ending = "A" if data.get("gender") == "f" else "O"
        title_y = int(60 - (1 - appear) * 40)
        draw_text(surface, "NOVO HERÓI DESBLOQUEADO!", 44, (255, 215, 90), (cx, title_y), shadow=True)
        if t > 0.7:
            draw_text(surface, f"{data['name'].upper()} DESBLOQUEAD{ending}!", 64, (140, 230, 255), (cx, 470), shadow=True)
            draw_text(surface, character_title(data), 30, config.TEXT_COLOR, (cx, 520))
        if t > 1.1:
            pulse = 0.5 + 0.5 * math.sin(t * 5)
            draw_text(surface, "PARABÉNS! SALVE OS HERÓIS DO VÓRTICE.", 32,
                      (255, int(190 + 40 * pulse), 90), (cx, 574), shadow=True)
        if self.total > 1:
            done = self.total - len(self.queue) + 1
            draw_text(surface, f"{done}/{self.total}", 24, config.MUTED_TEXT_COLOR, (w - 60, 40))
        if t >= ANIMATION_TIME:
            if int(t * 2) % 2 == 0:
                draw_text(surface, "Pressione Enter ou clique para continuar", 28, config.ACCENT_COLOR, (cx, 664))
