"""
ui/character_select.py - tela de ESCOLHA DE PERSONAGEM.

<<<<<<< HEAD
- Fileira na PARTE DE BAIXO da tela: TODOS os personagens (os bloqueados aparecem escurecidos, com cadeado).
- Centro: o personagem selecionado (setas < > ou clique na fileira).
=======
- Coluna da esquerda: TODOS os personagens (os bloqueados aparecem escurecidos, com cadeado).
- Centro: o personagem selecionado (setas < > ou clique na coluna).
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
- Mouse sobre um personagem BLOQUEADO: aparece como desbloqueá-lo (texto dinâmico por personagem).
- Bloqueados não podem iniciar uma partida.
"""
import types

import pygame

import config
from characters import character_title, unlock_hint
from game.state import GameState
from ui.portraits import draw_portrait
from ui.widgets import draw_lock, draw_panel, draw_text, draw_tooltip, draw_wrapped

<<<<<<< HEAD
THUMB = 64          # tamanho das miniaturas da fileira inferior
THUMB_GAP = 8       # espaço entre elas
THUMB_Y = 608       # posição Y da fileira (parte de baixo da tela)
THUMB_MARGIN = 40   # margem lateral mínima da fileira
=======
THUMB = 58          # tamanho das miniaturas da coluna
THUMB_GAP = 6       # espaço entre elas
THUMB_X = 30        # posição X da coluna
THUMB_Y = 96        # posição Y da primeira miniatura
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f


def _who(char_id, data):
    """Objeto leve com o que draw_portrait precisa (arte, cor)."""
    return types.SimpleNamespace(char_id=char_id, color=tuple(data.get("color", (150, 150, 150))),
                                 name=data["name"], image_id=data.get("image"))


class CharacterSelectScreen:
    def __init__(self, game):
        self.game = game
        self.ids = list(game.data["characters"].keys())
        self.index = 0
<<<<<<< HEAD
        self.left_rect = pygame.Rect(400, 190, 70, 120)
        self.right_rect = pygame.Rect(810, 190, 70, 120)
        self.start_rect = pygame.Rect(490, 540, 300, 52)
        self.art_rect = pygame.Rect(540, 150, 200, 200)
        n = len(self.ids)             # com muitos personagens as miniaturas encolhem para caber na largura (com 9-10, tamanho normal)
        self.thumb = min(THUMB, (config.SCREEN_WIDTH - 2 * THUMB_MARGIN - (n - 1) * THUMB_GAP) // n)
        row_width = n * self.thumb + (n - 1) * THUMB_GAP
        x0 = (config.SCREEN_WIDTH - row_width) // 2                      # fileira centralizada
        self.thumb_rects = [pygame.Rect(x0 + i * (self.thumb + THUMB_GAP), THUMB_Y, self.thumb, self.thumb)
=======
        self.left_rect = pygame.Rect(180, 300, 70, 120)
        self.right_rect = pygame.Rect(1030, 300, 70, 120)
        self.start_rect = pygame.Rect(490, 620, 300, 56)
        self.art_rect = pygame.Rect(540, 190, 200, 200)
        n = len(self.ids)             # com 10+ personagens as miniaturas encolhem para caber na tela (com 9, tamanho normal)
        self.thumb = min(THUMB, (config.SCREEN_HEIGHT - 30 - THUMB_Y - (n - 1) * THUMB_GAP) // n)
        self.thumb_rects = [pygame.Rect(THUMB_X, THUMB_Y + i * (self.thumb + THUMB_GAP), self.thumb, self.thumb)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
                            for i in range(n)]
        self.shade_thumb = pygame.Surface((self.thumb, self.thumb), pygame.SRCALPHA)
        self.shade_thumb.fill((0, 0, 0, 160))
        self.shade_art = pygame.Surface(self.art_rect.size, pygame.SRCALPHA)
        self.shade_art.fill((0, 0, 0, 170))

    # ------------------------------------------------------------ dados
    def _data(self, char_id):
        return self.game.data["characters"][char_id]

    def _unlocked(self, char_id):
        return self.game.progress.is_unlocked(char_id)

    def _current(self):
        char_id = self.ids[self.index]
        return char_id, self._data(char_id)

    # ------------------------------------------------------------ ações
    def _change(self, direction):
        self.index = (self.index + direction) % len(self.ids)
        self.game.audio.play("select")

    def _start(self):
        char_id, data = self._current()
        if self._unlocked(char_id):
            self.game.audio.play("select")
            self.game.start_run(char_id)
        else:
            self.game.audio.play("fail")           # bloqueado: não inicia

    def handle_input(self, inp):
        if inp.pressed("back"):
            self.game.change_state(GameState.MENU)
            return
        if inp.pressed("left"):
            self._change(-1)
        if inp.pressed("right"):
            self._change(1)
        if inp.pressed("swap"):
            self._start()
        if inp.click:
            for i, rect in enumerate(self.thumb_rects):
                if rect.collidepoint(inp.click):
                    self.index = i
                    self.game.audio.play("select")
                    return
            if self.left_rect.collidepoint(inp.click):
                self._change(-1)
            elif self.right_rect.collidepoint(inp.click):
                self._change(1)
            elif self.start_rect.collidepoint(inp.click):
                self._start()

    def update(self, dt):
        pass

    # ------------------------------------------------------------ desenho
    def _hovered_locked(self, mouse):
        """(id, dados) do personagem BLOQUEADO sob o mouse, ou None."""
        for i, rect in enumerate(self.thumb_rects):
            if rect.collidepoint(mouse):
                cid = self.ids[i]
                return None if self._unlocked(cid) else (cid, self._data(cid))
        if self.art_rect.collidepoint(mouse):
            char_id, data = self._current()
            return (char_id, data) if not self._unlocked(char_id) else None
        return None

    def draw(self, surface):
        surface.fill(config.BACKGROUND_COLOR)
        char_id, data = self._current()
        unlocked = self._unlocked(char_id)
<<<<<<< HEAD
        draw_text(surface, "ESCOLHA SEU PERSONAGEM", 48, config.TEXT_COLOR, (640, 34))
        if self.game.pending_mode == "infinite":
            draw_text(surface, "MODO INFINITO", 32, config.ACCENT_COLOR, (1240, 30), "topright")

        # ---- fileira inferior com todos os personagens ----
=======
        draw_text(surface, "ESCOLHA SEU PERSONAGEM", 54, config.TEXT_COLOR, (640, 50))
        if self.game.pending_mode == "infinite":
            draw_text(surface, "MODO INFINITO", 32, config.ACCENT_COLOR, (1240, 30), "topright")

        # ---- coluna com todos os personagens ----
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        for i, (cid, rect) in enumerate(zip(self.ids, self.thumb_rects)):
            cdata = self._data(cid)
            draw_portrait(surface, rect.topleft, self.thumb, _who(cid, cdata))
            if not self._unlocked(cid):
                surface.blit(self.shade_thumb, rect.topleft)
                draw_lock(surface, rect.center, 26)
            selected = i == self.index
            pygame.draw.rect(surface, config.ACCENT_COLOR if selected else (70, 70, 95), rect,
                             width=3 if selected else 1, border_radius=8)

        # ---- personagem selecionado ----
<<<<<<< HEAD
        draw_text(surface, data["name"].upper(), 56, config.ACCENT_COLOR if unlocked else (150, 150, 165), (640, 84))
        cls = data.get("class", "")
        sub = f"{cls}  |  Estilo: {data['style']}" if cls and cls != "—" else f"Estilo: {data['style']}"
        draw_text(surface, sub, 26, config.MUTED_TEXT_COLOR, (640, 122))
=======
        draw_text(surface, data["name"].upper(), 64, config.ACCENT_COLOR if unlocked else (150, 150, 165), (640, 115))
        cls = data.get("class", "")
        sub = f"{cls}  |  Estilo: {data['style']}" if cls and cls != "—" else f"Estilo: {data['style']}"
        draw_text(surface, sub, 28, config.MUTED_TEXT_COLOR, (640, 160))
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

        draw_portrait(surface, self.art_rect.topleft, 200, _who(char_id, data))
        if not unlocked:
            surface.blit(self.shade_art, self.art_rect.topleft)
            draw_lock(surface, self.art_rect.center, 80)

        for rect, label in ((self.left_rect, "<"), (self.right_rect, ">")):
            pygame.draw.rect(surface, (45, 45, 70), rect, border_radius=12)
            pygame.draw.rect(surface, (110, 110, 150), rect, width=2, border_radius=12)
            draw_text(surface, label, 70, config.TEXT_COLOR, rect.center)
<<<<<<< HEAD
        draw_text(surface, f"{self.index + 1} / {len(self.ids)}", 24, config.MUTED_TEXT_COLOR, (520, 372))
        draw_text(surface, f"HP: {data['max_hp']}", 32, config.TEXT_COLOR, (760, 372))

        draw_panel(surface, (200, 398, 400, 130))
        draw_text(surface, "PASSIVA", 22, config.MUTED_TEXT_COLOR, (216, 408), "topleft")
        draw_text(surface, data["passive_name"], 32, config.ACCENT_COLOR, (216, 430), "topleft")
        draw_wrapped(surface, data["passive_text"], 24, config.TEXT_COLOR, (216, 462), 368, 22)

        draw_panel(surface, (680, 398, 400, 130))
        draw_text(surface, "HABILIDADE", 22, config.MUTED_TEXT_COLOR, (696, 408), "topleft")
        draw_text(surface, f"{data['ability_name']}  (custo {data['ability_cost']})", 32,
                  config.ACCENT_COLOR, (696, 430), "topleft")
        draw_wrapped(surface, data["ability_text"], 24, config.TEXT_COLOR, (696, 462), 368, 22)
=======
        draw_text(surface, f"{self.index + 1} / {len(self.ids)}", 24, config.MUTED_TEXT_COLOR, (640, 405))
        draw_text(surface, f"HP: {data['max_hp']}", 36, config.TEXT_COLOR, (640, 440))

        draw_panel(surface, (200, 470, 400, 130))
        draw_text(surface, "PASSIVA", 22, config.MUTED_TEXT_COLOR, (216, 480), "topleft")
        draw_text(surface, data["passive_name"], 32, config.ACCENT_COLOR, (216, 502), "topleft")
        draw_wrapped(surface, data["passive_text"], 24, config.TEXT_COLOR, (216, 534), 368, 22)

        draw_panel(surface, (680, 470, 400, 130))
        draw_text(surface, "HABILIDADE", 22, config.MUTED_TEXT_COLOR, (696, 480), "topleft")
        draw_text(surface, f"{data['ability_name']}  (custo {data['ability_cost']})", 32,
                  config.ACCENT_COLOR, (696, 502), "topleft")
        draw_wrapped(surface, data["ability_text"], 24, config.TEXT_COLOR, (696, 534), 368, 22)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

        if unlocked:
            pygame.draw.rect(surface, (70, 120, 70), self.start_rect, border_radius=12)
            pygame.draw.rect(surface, (150, 240, 150), self.start_rect, width=3, border_radius=12)
            draw_text(surface, "INICIAR RUN  [Enter]", 32, config.TEXT_COLOR, self.start_rect.center)
        else:
<<<<<<< HEAD
            draw_lock(surface, (250, 566), 28)
            draw_text(surface, f"BLOQUEADO - {unlock_hint(data)}", 28, (255, 190, 120), (640, 566))
=======
            draw_lock(surface, (250, 648), 28)
            draw_text(surface, f"BLOQUEADO - {unlock_hint(data)}", 28, (255, 190, 120), (640, 648))
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        draw_text(surface, "Esc: voltar", 22, config.MUTED_TEXT_COLOR, (80, 696))

        # ---- informação ao passar o mouse sobre um bloqueado ----
        hovered = self._hovered_locked(self.game.input.mouse_pos)
        if hovered:
            hid, hdata = hovered
            draw_tooltip(surface, self.game.input.mouse_pos, character_title(hdata).upper(), unlock_hint(hdata))
