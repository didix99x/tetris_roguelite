"""
ui/phoenix_rebirth.py - ANIMAÇÃO da carta Phoenix (Pena de Fênix / Chama da Fênix). SÓ VISUAL.

O efeito da carta continua em combat/combat.py (_player_dies: 1x por andar, volta com X% da vida e emite o evento
"second_wind"). Esta classe só desenha a sequência e CONGELA o combate enquanto toca:

  1. ATIVAÇÃO       clarão alaranjado + "FÊNIX"
  2. REVIVIFICAÇÃO  chamas sobem do painel do jogador + halo em volta do personagem
  3. RENOVAÇÃO      onda de luz atravessa a tela (andar renovado) e o brilho some
  4. RETORNO        active vira False: a partida continua exatamente de onde parou

Tudo é desenhado por código (sem imagens), então não há arquivo que possa faltar. Só `start()` quando o evento
chega; um segundo start() durante a animação é ignorado (não repete).
"""
import math
import random

import pygame

import config
from ui import theme
from ui.widgets import draw_text

DURATION = 2.4                       # segundos (tempo do jogo, não depende do FPS)
T_ACTIVATE, T_REVIVE = 0.5, 1.6      # fim da fase 1 e da fase 2 (a fase 3 vai até DURATION)
FLAME_COLORS = ((255, 120, 40), (255, 180, 60), (255, 230, 120))


class PhoenixRebirth:
    def __init__(self):
        self.time = 0.0
        self.active = False
        self.count = 0                                   # quantas vezes tocou (útil nos testes)
        self._rng = random.Random(7)
        self._flames = []                                # [x, y, velocidade, raio, cor]
        self._layer = None                               # camada translúcida criada uma vez só (sem recriar a cada quadro)

    def start(self):
        """Inicia a sequência. Ignora se já estiver tocando."""
        if self.active:
            return False
        self.active, self.time = True, 0.0
        self.count += 1
        x, y, w, h = theme.LEFT_PANEL
        self._flames = [[x + self._rng.uniform(0.1, 0.9) * w, y + h - self._rng.uniform(0, 60),
                         self._rng.uniform(90, 260), self._rng.uniform(5, 13), self._rng.choice(FLAME_COLORS)]
                        for _ in range(46)]
        return True

    def update(self, dt):
        if not self.active:
            return
        self.time += dt
        for f in self._flames:
            f[1] -= f[2] * dt
        if self.time >= DURATION:
            self.active = False

    @property
    def phase(self):
        if not self.active:
            return 0
        return 1 if self.time < T_ACTIVATE else 2 if self.time < T_REVIVE else 3

    def draw(self, surface):
        if not self.active:
            return
        try:
            self._draw(surface)
        except (pygame.error, ValueError, TypeError):    # nunca derruba a partida por causa de um efeito visual
            pass

    def _draw(self, surface):
        if self._layer is None:
            self._layer = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        layer, t = self._layer, self.time
        px, py, pw, ph = theme.LEFT_PANEL
        cx, cy = px + pw // 2, py + ph // 2
        layer.fill((0, 0, 0, 0))

        phase = self.phase
        if phase == 1:                                   # clarão que sobe e começa a baixar
            k = t / T_ACTIVATE
            layer.fill((255, 150, 40, int(150 * math.sin(min(1.0, k) * math.pi * 0.5 + 0.2))))
        else:                                            # tela escurecida de leve para destacar as chamas
            fade = 1.0 if phase == 2 else max(0.0, 1.0 - (t - T_REVIVE) / (DURATION - T_REVIVE))
            layer.fill((20, 6, 0, int(110 * fade)))

        if phase >= 2:                                   # chamas + halo em volta do personagem
            k = min(1.0, (t - T_ACTIVATE) / (T_REVIVE - T_ACTIVATE))
            glow = 1.0 if phase == 2 else max(0.0, 1.0 - (t - T_REVIVE) / (DURATION - T_REVIVE))
            for f in self._flames:
                if py - 40 < f[1]:
                    pygame.draw.circle(layer, (*f[4], int(200 * glow)), (int(f[0]), int(f[1])), int(f[3]))
            radius = int(40 + 90 * k)
            for ring in range(3):
                pygame.draw.circle(layer, (255, 200 - 40 * ring, 80, int((150 - 40 * ring) * glow)), (cx, cy - 60),
                                   radius + ring * 14, width=4)

        if phase == 3:                                   # renovação do andar: onda de luz que atravessa a tela
            k = (t - T_REVIVE) / (DURATION - T_REVIVE)
            x = int(-80 + (config.SCREEN_WIDTH + 160) * k)
            pygame.draw.rect(layer, (255, 235, 170, int(170 * (1.0 - k * 0.6))), (x - 60, 0, 120, config.SCREEN_HEIGHT))
            pygame.draw.rect(layer, (255, 200, 90, 70), (0, 0, max(0, x - 60), config.SCREEN_HEIGHT))
        surface.blit(layer, (0, 0))

        title = {1: "FÊNIX!", 2: "A FÊNIX RENASCE", 3: "RENOVAÇÃO"}[phase]
        draw_text(surface, title, 72 if phase == 2 else 60, (255, 220, 120), (config.SCREEN_WIDTH // 2, 330), shadow=True)
        if phase >= 2:
            draw_text(surface, "Você voltou à luta!", 30, config.TEXT_COLOR, (config.SCREEN_WIDTH // 2, 392), shadow=True)
