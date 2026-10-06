"""
game/input.py - ENTRADA (teclado e mouse).

As teclas vêm de settings.json ("controls"). O resto do jogo não pergunta
"qual tecla?", pergunta "qual AÇÃO?": left, right, up, down, swap,
ability, back.

Quer mudar as teclas? Edite o "controls" do settings.json
(nomes de teclas do pygame: "left", "a", "return", "space", "escape"...).
"""
import logging

import pygame

log = logging.getLogger(__name__)

# Só estas ações repetem quando a tecla fica pressionada.
REPEATABLE = {"left", "right", "up", "down"}


class Input:
    def __init__(self, settings, to_canvas):
        self.settings = settings
        self.to_canvas = to_canvas    # converte posição da janela -> posição do jogo
        self.keymap = {}
        self.rebuild_keymap()
        self._held = set()
        self.actions = set()
        self.click = None             # posição do clique deste frame (ou None)
        self.mouse_pos = (0, 0)

    def rebuild_keymap(self):
        self.keymap = {}
        for action, names in self.settings.get("controls").items():
            for name in names:
                try:
                    code = pygame.key.key_code(name)
                except ValueError:
                    log.warning("Tecla desconhecida em settings.json: %s", name)
                    continue
                self.keymap.setdefault(code, []).append(action)

    def begin_frame(self):
        self.actions.clear()
        self.click = None
        self.mouse_pos = self.to_canvas(pygame.mouse.get_pos())

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            for action in self.keymap.get(event.key, []):
                if event.key in self._held and action not in REPEATABLE:
                    continue
                self.actions.add(action)
            self._held.add(event.key)
        elif event.type == pygame.KEYUP:
            self._held.discard(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.click = self.to_canvas(event.pos)

    def pressed(self, action):
        return action in self.actions
