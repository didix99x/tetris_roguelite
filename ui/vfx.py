"""ui/vfx.py - efeitos visuais simples: textos flutuantes, partículas e tremor de tela."""
import random

import pygame

import config
from ui.widgets import draw_text


class VFX:
    def __init__(self):
        self.texts = []       # [texto, x, y, cor, tamanho, vida, vida_total]
        self.particles = []   # [x, y, vx, vy, vida, cor]
        self.shake_time = 0.0
        self.shake_power = 0.0
<<<<<<< HEAD
        self.shake_enabled = True
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        self.flash_color = None
        self.flash_time = 0.0
        self.flash_strength = 1.0

    def add_text(self, text, x, y, color=config.TEXT_COLOR, size=40, life=1.0):
        self.texts.append([text, x, y, color, size, life, life])

    def add_burst(self, x, y, color, count=8):
        if len(self.particles) > 350:
            return
        for _ in range(count):
            self.particles.append([x, y, random.uniform(-160, 160), random.uniform(-240, 40),
                                   random.uniform(0.35, 0.7), color])

    def add_shake(self, power=6.0, time=0.25):
<<<<<<< HEAD
        if not self.shake_enabled:             # Opções > TREMOR DE TELA: desligado
            return
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        self.shake_power = max(self.shake_power, power)
        self.shake_time = max(self.shake_time, time)

    def add_flash(self, color, time=0.25, strength=1.0):
        self.flash_color = color
        self.flash_time = time
        self.flash_strength = strength

    def shake_offset(self):
        if self.shake_time <= 0:
            return (0, 0)
        p = self.shake_power
        return (random.uniform(-p, p), random.uniform(-p, p))

    def update(self, dt):
        for t in self.texts:
            t[2] -= 45 * dt
            t[5] -= dt
        self.texts = [t for t in self.texts if t[5] > 0]
        for p in self.particles:
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            p[3] += 600 * dt
            p[4] -= dt
        self.particles = [p for p in self.particles if p[4] > 0]
        if self.shake_time > 0:
            self.shake_time -= dt
        if self.flash_time > 0:
            self.flash_time -= dt

    def draw(self, surface):
        for x, y, _, _, life, color in self.particles:
            pygame.draw.circle(surface, color, (int(x), int(y)), 3 if life > 0.3 else (2 if life > 0.15 else 1))
        for text, x, y, color, size, life, total in self.texts:
            draw_text(surface, text, size, color, (int(x), int(y)), shadow=True)
        if self.flash_time > 0 and self.flash_color:
            overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            alpha = int(110 * self.flash_strength * min(1.0, self.flash_time / 0.25))
            overlay.fill((*self.flash_color, alpha))
            surface.blit(overlay, (0, 0))
