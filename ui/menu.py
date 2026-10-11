"""ui/menu.py - MENU PRINCIPAL e tela de OPÇÕES."""
import pygame

import config
from game.settings import RESOLUTIONS, WINDOW_MODE_NAMES, WINDOW_MODES
from game.state import GameState
<<<<<<< HEAD
from game.input import PAD_ACTION_NAMES
from ui.widgets import ButtonList, controller_hint, draw_text
=======
from ui.widgets import ButtonList, draw_text
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f


class MenuScreen:
    def __init__(self, game):
        self.game = game
        self.infinite_open = game.progress.is_infinite_unlocked()
<<<<<<< HEAD
        self.buttons = ButtonList(["JOGAR", "MODO INFINITO", "LOJA", "OPÇÕES", "SAIR"], start_y=284, height=50, gap=12,
=======
        self.buttons = ButtonList(["JOGAR", "MODO INFINITO", "OPÇÕES", "SAIR"], start_y=300, height=54, gap=14,
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
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
<<<<<<< HEAD
            self.game.audio.play("select")
            self.game.change_state(GameState.SHOP)
        elif choice == 3:
            self.game.change_state(GameState.OPTIONS)
        elif choice == 4:
=======
            self.game.change_state(GameState.OPTIONS)
        elif choice == 3:
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
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
<<<<<<< HEAD
        info += f"   Pontos: {progress.points}"
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        draw_text(surface, info, 24, config.MUTED_TEXT_COLOR, (640, 686))


class OptionsScreen:
<<<<<<< HEAD
    """OPÇÕES. Duas páginas na mesma tela: GERAL (som, tela) e CONTROLE / JOYSTICK (botões do controle, remapeamento).
    Trocar de página: LB/RB (Xbox), L1/R1 (PlayStation), PageUp/PageDown, ou o item "CONTROLE / JOYSTICK" da página Geral."""
    PAGES = ("GERAL", "CONTROLE / JOYSTICK")
    WAIT_LIMIT = 8.0                 # segundos esperando um botão no remapeamento (depois cancela sozinho)

=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    def __init__(self, game):
        self.game = game
        self.settings = game.settings
        self.selected = 0
<<<<<<< HEAD
        self.items = ["music", "sfx", "shake", "mode", "resolution", "pad", "back"]
        self.rects = [pygame.Rect(340, 208 + i * 60, 600, 50) for i in range(len(self.items))]
        # ---- página CONTROLE / JOYSTICK ----
        self.page = 0
        self.pad_rows = [a for a, _ in PAD_ACTION_NAMES] + ["reset", "back"]
        self.pad_rects = [pygame.Rect(340, 262 + i * 36, 600, 32) for i in range(len(self.pad_rows))]
        self.pad_selected = 0
        self.waiting = None          # ação aguardando um botão do controle (ou None)
        self.wait_time = 0.0
        self.message, self.message_time = "", 0.0
        self.time = 0.0
=======
        self.items = ["music", "sfx", "mode", "resolution", "back"]
        self.rects = [pygame.Rect(340, 250 + i * 72, 600, 56) for i in range(len(self.items))]
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

    def _adjust(self, item, direction):
        s = self.settings
        audio = self.game.audio
<<<<<<< HEAD
        if item == "pad":
            if direction > 0:                            # abre a página CONTROLE / JOYSTICK
                self.page = 1
            return
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        if item in ("music", "sfx"):
            key = "music_volume" if item == "music" else "sfx_volume"
            value = round(max(0.0, min(1.0, s.get(key) + 0.1 * direction)), 1)
            s.set(key, value)
            audio.apply_volumes()
            audio.play("select")
<<<<<<< HEAD
        elif item == "shake":
            s.set("screen_shake", not s.get("screen_shake"))
            audio.play("select")
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
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
<<<<<<< HEAD
        self._stop_waiting()
        self.settings.save()
        self.game.change_state(GameState.MENU)

    def _handle_general(self, inp):
=======
        self.settings.save()
        self.game.change_state(GameState.MENU)

    def handle_input(self, inp):
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
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

<<<<<<< HEAD
    def handle_input(self, inp):
        if self.waiting is None:                         # (durante o remapeamento as abas não trocam)
            if inp.pressed("tab_next"):
                self.page = (self.page + 1) % len(self.PAGES)
                return
            if inp.pressed("tab_prev"):
                self.page = (self.page - 1) % len(self.PAGES)
                return
        if self.page == 0:
            self._handle_general(inp)
        else:
            self._handle_pad_page(inp)

    # ------------------------------------------------ página CONTROLE / JOYSTICK
    def _say(self, text, seconds=5.0):
        self.message, self.message_time = text, seconds

    def _stop_waiting(self):
        self.waiting = None
        if hasattr(self.game.input, "capture_pad"):
            self.game.input.capture_pad = False          # os botões voltam a funcionar como comandos

    def _start_waiting(self, action):
        pad = self.game.input
        if not pad.pad_connected():
            self._say("Nenhum controle conectado. Conecte um controle para remapear (teclado e mouse seguem funcionando).")
            return
        self.waiting, self.wait_time = action, 0.0
        pad.capture_pad = True                            # o botão apertado agora NÃO executa ação de jogo
        self._say("")

    def _activate_pad_row(self, row):
        if row == "back":
            self.page = 0
        elif row == "reset":
            self.game.input.reset_pad_defaults()
            self._say("Controles do joystick restaurados para o padrão.")
        else:
            self._start_waiting(row)

    def _handle_pad_page(self, inp):
        pad = self.game.input
        if self.waiting is not None:
            if inp.pressed("back"):                       # Esc (teclado) cancela: o comando anterior é mantido
                self._stop_waiting()
                self._say("Remapeamento cancelado. O botão anterior foi mantido.")
            elif inp.pad_pressed:                         # primeiro botão apertado no controle
                ok, text = pad.set_pad_button(self.waiting, inp.pad_pressed[0])
                self._say(text, 6.0)
                if ok:
                    self._stop_waiting()
                else:
                    self.wait_time = 0.0                  # conflito: avisa e continua esperando outro botão
            return
        if inp.pressed("back"):
            self.page = 0
            return
        if inp.pressed("up"):
            self.pad_selected = (self.pad_selected - 1) % len(self.pad_rows)
        if inp.pressed("down"):
            self.pad_selected = (self.pad_selected + 1) % len(self.pad_rows)
        if inp.pressed("swap"):
            self._activate_pad_row(self.pad_rows[self.pad_selected])
            return
        for i, rect in enumerate(self.pad_rects):
            if rect.collidepoint(inp.mouse_pos):
                self.pad_selected = i
            if inp.click and rect.collidepoint(inp.click):
                self._activate_pad_row(self.pad_rows[i])
                return

    def update(self, dt):
        self.time += dt
        if self.message_time > 0:
            self.message_time -= dt
        if self.waiting is not None:
            self.wait_time += dt
            if not self.game.input.pad_connected():       # controle desconectado no meio da configuração
                self._stop_waiting()
                self._say("O controle foi desconectado. Remapeamento cancelado (use o teclado para voltar).", 6.0)
            elif self.wait_time > self.WAIT_LIMIT:
                self._stop_waiting()
                self._say("Tempo esgotado. Remapeamento cancelado; o botão anterior foi mantido.")
=======
    def update(self, dt):
        pass
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

    def _label(self, item):
        s = self.settings
        if item == "music":
            return f"Música: {round(s.get('music_volume') * 100)}%"
        if item == "sfx":
            return f"Efeitos: {round(s.get('sfx_volume') * 100)}%"
<<<<<<< HEAD
        if item == "shake":
            return f"Tremor de tela: {'ON' if s.get('screen_shake') else 'OFF'}"
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        if item == "mode":
            return f"Modo de tela: {WINDOW_MODE_NAMES[s.get('window_mode')]}"
        if item == "resolution":
            return f"Tamanho da janela: {s.get('window_width')}x{s.get('window_height')}"
<<<<<<< HEAD
        if item == "pad":
            return "CONTROLE / JOYSTICK   >"
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        return "VOLTAR"

    def draw(self, surface):
        surface.fill(config.BACKGROUND_COLOR)
<<<<<<< HEAD
        draw_text(surface, "OPÇÕES", 64, config.TEXT_COLOR, (640, 96))
        self._draw_page_tabs(surface)
        if self.page == 1:
            self._draw_pad_page(surface)
            return
=======
        draw_text(surface, "OPÇÕES", 72, config.TEXT_COLOR, (640, 130))
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        for i, (item, rect) in enumerate(zip(self.items, self.rects)):
            active = i == self.selected
            pygame.draw.rect(surface, (60, 60, 90) if active else (35, 35, 55), rect, border_radius=10)
            pygame.draw.rect(surface, config.ACCENT_COLOR if active else (80, 80, 110), rect,
                             width=3 if active else 2, border_radius=10)
            draw_text(surface, self._label(item), 32,
                      config.ACCENT_COLOR if active else config.TEXT_COLOR, rect.center)
<<<<<<< HEAD
        draw_text(surface, controller_hint(self.game, "Setas: escolher e ajustar   Enter: mudar   Esc: voltar   F11: tela cheia   PgUp/PgDn: página",
                                           (("move", "escolher"), ("swap", "mudar"), ("back", "voltar"), ("tabs", "página"))),
                  24, config.MUTED_TEXT_COLOR, (640, 690))

    def _draw_page_tabs(self, surface):
        for i, name in enumerate(self.PAGES):
            rect = pygame.Rect(340 + i * 304, 140, 296, 36)
            active = i == self.page
            pygame.draw.rect(surface, (60, 60, 98) if active else (32, 32, 50), rect, border_radius=10)
            pygame.draw.rect(surface, config.ACCENT_COLOR if active else (80, 80, 110), rect, width=3 if active else 2, border_radius=10)
            draw_text(surface, name, 22, config.TEXT_COLOR if active else config.MUTED_TEXT_COLOR, rect.center)

    def _draw_pad_page(self, surface):
        pad = self.game.input
        connected = pad.pad_connected()
        draw_text(surface, f"Controle: {pad.pad_name() or 'nenhum detectado'}", 24, config.TEXT_COLOR, (340, 202), "midleft")
        status = "CONECTADO" if connected else "DESCONECTADO (teclado e mouse funcionam normalmente)"
        draw_text(surface, f"Estado: {status}", 22, (120, 230, 140) if connected else (255, 150, 110), (340, 232), "midleft")
        names = dict(PAD_ACTION_NAMES)
        for i, (row, rect) in enumerate(zip(self.pad_rows, self.pad_rects)):
            active = i == self.pad_selected
            waiting = row == self.waiting
            pygame.draw.rect(surface, (90, 70, 40) if waiting else (60, 60, 90) if active else (35, 35, 55), rect, border_radius=8)
            pygame.draw.rect(surface, (255, 190, 90) if waiting else config.ACCENT_COLOR if active else (80, 80, 110), rect,
                             width=3 if (active or waiting) else 2, border_radius=8)
            color = config.ACCENT_COLOR if active else config.TEXT_COLOR
            if row in names:
                draw_text(surface, names[row], 24, color, (rect.x + 14, rect.centery), "midleft")
                if waiting:                                     # aviso visível: este comando espera um botão
                    blink = 255 if int(self.time * 3) % 2 == 0 else 170
                    draw_text(surface, "AGUARDANDO BOTÃO...", 22, (255, blink, 90), (rect.right - 14, rect.centery), "midright")
                else:
                    draw_text(surface, pad.button_text(row), 22, color, (rect.right - 14, rect.centery), "midright")
            else:
                draw_text(surface, "RESTAURAR PADRÃO" if row == "reset" else "VOLTAR", 24, color, rect.center)
        if self.waiting is not None:
            seconds = max(0, int(self.WAIT_LIMIT - self.wait_time) + 1)
            draw_text(surface, f"Pressione o botão desejado no controle ({seconds}s)   Esc: cancelar", 22, (255, 190, 90), (640, 672))
        elif self.message_time > 0 and self.message:
            draw_text(surface, self.message, 20, (255, 215, 130), (640, 672))
        else:
            draw_text(surface, "D-Pad e analógico sempre movem o cursor; os botões extras de direção são opcionais.", 20,
                      config.MUTED_TEXT_COLOR, (640, 672))
        draw_text(surface, controller_hint(self.game, "Setas: escolher   Enter: remapear   Esc: voltar   PgUp/PgDn: página",
                                           (("move", "escolher"), ("swap", "remapear"), ("tabs", "página"))),
                  22, config.MUTED_TEXT_COLOR, (640, 700))
=======
        draw_text(surface, "Setas: escolher e ajustar   Enter: mudar   Esc: voltar   F11: tela cheia",
                  24, config.MUTED_TEXT_COLOR, (640, 680))
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
