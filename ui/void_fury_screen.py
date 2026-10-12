"""
ui/void_fury_screen.py - "O VAZIO ESTÁ FURIOSO COM A SUA PRESENÇA."

Tela especial do Modo Infinito: só aparece DEPOIS de derrotar o chefe e concluir o andar 100 (e 200, 300...),
nunca antes nem durante o combate. É uma tela inteira (fica acima de tudo) e exige uma escolha explícita:
  CONTINUAR -> segue para o próximo andar (a tela não se repete no mesmo marco);
  DESISTIR  -> pede confirmação e encerra a tentativa (o que já foi salvo continua salvo).
Enquanto a animação toca (e nunca por Esc ou clique fora dos botões) a tela não some.
"""
import math
import random

import pygame

import config
from ui.widgets import ButtonList, draw_text, wrap_text

BUTTONS_AT = 3.4           # segundos até os botões aparecerem/funcionarem
TITLE = "O VAZIO ESTÁ FURIOSO COM A SUA PRESENÇA."


class VoidFuryScreen:
    def __init__(self, game, milestone):
        self.game = game
        self.milestone = milestone
        self.t = 0.0
        self.mode = "choice"                       # "choice" ou "confirm" (DESISTIR)
        self.buttons = ButtonList(["CONTINUAR", "DESISTIR"], start_y=470, height=60, gap=16, width=360)
        self.confirm = ButtonList(["SIM, DESISTIR", "VOLTAR"], start_y=470, height=60, gap=16, width=360)
        rng = random.Random(milestone)
        self.embers = [[rng.uniform(0, config.SCREEN_WIDTH), rng.uniform(0, config.SCREEN_HEIGHT),
                        rng.uniform(20, 70), rng.uniform(0, 6.28)] for _ in range(70)]
        game.audio.play("enemy_ability")

    # ------------------------------------------------------------ entrada
    def handle_input(self, inp):
        if self.t < BUTTONS_AT:                    # nada fecha a tela durante a animação
            return
        buttons = self.buttons if self.mode == "choice" else self.confirm
        choice = buttons.handle(inp, self.game.audio)
        if choice is None:
            return                                 # Esc, clique fora dos botões etc. não fazem nada
        if self.mode == "choice":
            if choice == 0:
                self.game.on_void_fury_choice(True)
            else:
                self.mode = "confirm"
                self.confirm.selected = 1          # começa em VOLTAR (mais seguro)
        else:
            if choice == 0:
                self.game.on_void_fury_choice(False)
            else:
                self.mode = "choice"

    def update(self, dt):
        self.t += dt
        for e in self.embers:                      # brasas sombrias subindo
            e[1] -= e[2] * dt
            if e[1] < -10:
                e[1] = config.SCREEN_HEIGHT + 10

    # ------------------------------------------------------------ desenho
    def _vortex(self, surface, cx, cy):
        t = self.t
        for k in range(9):
            radius = 60 + k * 62 + int(8 * math.sin(t * 1.5 + k))
            level = max(0, 90 - k * 8)
            color = (level + 30, 8, level + 20)
            rect = pygame.Rect(cx - radius, cy - int(radius * 0.55), radius * 2, int(radius * 1.1))
            start = t * (0.6 + k * 0.05) + k
            pygame.draw.arc(surface, color, rect, start, start + 3.6, 5)
        pygame.draw.circle(surface, (0, 0, 0), (cx, cy), 70 + int(6 * math.sin(t * 2)))

    def draw(self, surface):
        w, h = config.SCREEN_WIDTH, config.SCREEN_HEIGHT
        t = self.t
        surface.fill((6, 2, 10))
        self._vortex(surface, w // 2, 250)
        for x, y, _, phase in self.embers:
            level = 80 + int(60 * math.sin(t * 2 + phase))
            pygame.draw.circle(surface, (level + 60, 20, level), (int(x), int(y)), 2)
        # pulsos vermelhos nas bordas
        pulse = 0.5 + 0.5 * math.sin(t * 3)
        edge = (int(60 + 80 * pulse), 0, int(20 + 20 * pulse))
        pygame.draw.rect(surface, edge, (0, 0, w, h), width=10)

        fade = max(0.0, min(1.0, (t - 0.6) / 1.0))
        if fade > 0:
            shake = int(3 * math.sin(t * 40)) if t < 2.0 else 0
            color = (int(255 * fade), int(70 * fade), int(90 * fade))
            lines = wrap_text(TITLE, 62, w - 160)
            for i, line in enumerate(lines):
                draw_text(surface, line, 62, color, (w // 2 + shake, 90 + i * 70), shadow=True)
        if t > 2.0:
            sub = "Você ultrapassou os limites conhecidos. Os próximos andares serão muito mais perigosos."
            if self.milestone > 100:
                sub = f"Você concluiu o andar {self.milestone}. A fúria do Vazio cresce, e os próximos andares serão ainda mais perigosos."
            for i, line in enumerate(wrap_text(sub, 30, w - 260)):
                draw_text(surface, line, 30, config.TEXT_COLOR, (w // 2, 250 + i * 38), shadow=True)
        if t > 2.7:
            draw_text(surface, f"Andar {self.milestone} concluído  -  inimigos e super chefes mais fortes a cada andar.", 24,
                      (200, 150, 170), (w // 2, 350))
        if t >= BUTTONS_AT:
            if self.mode == "choice":
                self.buttons.draw(surface)
                draw_text(surface, "CONTINUAR: andar " + str(self.milestone + 1) + " do Modo Infinito.   DESISTIR: encerra esta tentativa.",
                          22, config.MUTED_TEXT_COLOR, (w // 2, 640))
            else:
                draw_text(surface, "Desistir agora encerra esta tentativa.", 34, (255, 150, 120), (w // 2, 420))
                self.confirm.draw(surface)
                draw_text(surface, "Seu progresso permanente e os desbloqueios continuam salvos.", 22,
                          config.MUTED_TEXT_COLOR, (w // 2, 640))
