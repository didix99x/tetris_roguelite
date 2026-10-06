"""ui/menu.py - MENU PRINCIPAL e tela de OPÇÕES."""
import pygame

import config
from game.settings import RESOLUTIONS, WINDOW_MODE_NAMES, WINDOW_MODES
from game.state import GameState
from ui.widgets import ButtonList, draw_text


class MenuScreen:
    def __init__(self, game):
        self.game = game
        self.infinite_open = game.progress.is_infinite_unlocked()
        self.buttons = ButtonList(["JOGAR", "MODO INFINITO", "OPÇÕES", "SAIR"], start_y=300, height=54, gap=14,
                                  disabled=() if self.infinite_open else (1,))
        self.time = 0.0
        self.message_time = 0.0

    def handle_input(self, inp):
        choice = self.buttons.handle(inp, self.game.audio)
        if choice == 0:
            self.game.audio.play("select")
            self.game.pending_mode = "story"
            self.game.change_state(GameState.CHARACTER_SELECT)
        elif choice == 1:
            if self.infinite_open:
                self.game.audio.play("select")
                self.game.pending_mode = "infinite"
                self.game.change_state(GameState.CHARACTER_SELECT)
            else:                                  # bloqueado: só avisa
                self.game.audio.play("fail")
                self.message_time = 3.5
        elif choice == 2:
            self.game.change_state(GameState.OPTIONS)
        elif choice == 3:
            self.game.quit()

    def update(self, dt):
        self.time += dt
        if self.message_time > 0:
            self.message_time -= dt

    def draw(self, surface):
        surface.fill(config.BACKGROUND_COLOR)
        # Blocos decorativos
        for i in range(5):
            color = config.BLOCK_COLORS[i + 1]
            x = 640 - 5 * 36 + i * 72
            y = 70 + int(6 * pygame.math.Vector2(0, 1).rotate(self.time * 120 + i * 50).y)
            pygame.draw.rect(surface, color, (x, y, 60, 60), border_radius=10)
        draw_text(surface, config.GAME_TITLE.upper(), 96, config.TEXT_COLOR, (640, 200))
        draw_text(surface, f"v{config.VERSION}", 28, config.MUTED_TEXT_COLOR, (640, 258))
        self.buttons.draw(surface)
        progress = self.game.progress
        if self.message_time > 0:
            last = self.game.data["floors"]["last_floor"]
            draw_text(surface, f"Termine o jogo (derrote o chefe do andar {last}) para desbloquear o Modo Infinito.",
                      28, (255, 150, 120), (640, 640))
        info = f"Melhor andar: {progress.best_floor}   Runs: {progress.runs}   Vitórias: {progress.wins}"
        if self.infinite_open:
            info += f"   Infinito: andar {progress.best_infinite_floor}"
        draw_text(surface, info, 24, config.MUTED_TEXT_COLOR, (640, 686))


class OptionsScreen:
    def __init__(self, game):
        self.game = game
        self.settings = game.settings
        self.selected = 0
        self.items = ["music", "sfx", "mode", "resolution", "back"]
        self.rects = [pygame.Rect(340, 250 + i * 72, 600, 56) for i in range(len(self.items))]

    def _adjust(self, item, direction):
        s = self.settings
        audio = self.game.audio
        if item in ("music", "sfx"):
            key = "music_volume" if item == "music" else "sfx_volume"
            value = round(max(0.0, min(1.0, s.get(key) + 0.1 * direction)), 1)
            s.set(key, value)
            audio.apply_volumes()
            audio.play("select")
        elif item == "mode":
            index = (WINDOW_MODES.index(s.get("window_mode")) + direction) % len(WINDOW_MODES)
            s.set("window_mode", WINDOW_MODES[index])
            self.game.apply_display_mode()
        elif item == "resolution":
            current = (s.get("window_width"), s.get("window_height"))
            index = RESOLUTIONS.index(current) if current in RESOLUTIONS else 0
            width, height = RESOLUTIONS[(index + direction) % len(RESOLUTIONS)]
            s.set("window_width", width)
            s.set("window_height", height)
            if s.get("window_mode") == "windowed":
                self.game.apply_display_mode()

    def _back(self):
        self.settings.save()
        self.game.change_state(GameState.MENU)

    def handle_input(self, inp):
        if inp.pressed("back"):
            self._back()
            return
        if inp.pressed("up"):
            self.selected = (self.selected - 1) % len(self.items)
        if inp.pressed("down"):
            self.selected = (self.selected + 1) % len(self.items)
        item = self.items[self.selected]
        if inp.pressed("left"):
            self._adjust(item, -1)
        if inp.pressed("right"):
            self._adjust(item, 1)
        if inp.pressed("swap"):
            if item == "back":
                self._back()
            else:
                self._adjust(item, 1)
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(inp.mouse_pos):
                self.selected = i
            if inp.click and rect.collidepoint(inp.click):
                if self.items[i] == "back":
                    self._back()
                else:
                    self._adjust(self.items[i], 1)

    def update(self, dt):
        pass

    def _label(self, item):
        s = self.settings
        if item == "music":
            return f"Música: {round(s.get('music_volume') * 100)}%"
        if item == "sfx":
            return f"Efeitos: {round(s.get('sfx_volume') * 100)}%"
        if item == "mode":
            return f"Modo de tela: {WINDOW_MODE_NAMES[s.get('window_mode')]}"
        if item == "resolution":
            return f"Tamanho da janela: {s.get('window_width')}x{s.get('window_height')}"
        return "VOLTAR"

    def draw(self, surface):
        surface.fill(config.BACKGROUND_COLOR)
        draw_text(surface, "OPÇÕES", 72, config.TEXT_COLOR, (640, 130))
        for i, (item, rect) in enumerate(zip(self.items, self.rects)):
            active = i == self.selected
            pygame.draw.rect(surface, (60, 60, 90) if active else (35, 35, 55), rect, border_radius=10)
            pygame.draw.rect(surface, config.ACCENT_COLOR if active else (80, 80, 110), rect,
                             width=3 if active else 2, border_radius=10)
            draw_text(surface, self._label(item), 32,
                      config.ACCENT_COLOR if active else config.TEXT_COLOR, rect.center)
        draw_text(surface, "Setas: escolher e ajustar   Enter: mudar   Esc: voltar   F11: tela cheia",
                  24, config.MUTED_TEXT_COLOR, (640, 680))
