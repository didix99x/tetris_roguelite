"""ui/event_screen.py - EVENTO ENTRE ANDARES (descanso, troca arriscada, sala misteriosa). Lógica em run/events.py."""
import pygame

import config
from run import events
from ui.card_art import draw_card_face
from ui.widgets import draw_panel, draw_text, draw_wrapped

TITLES = {"rest": "DESCANSO", "swap": "TROCA ARRISCADA", "mystery": "SALA MISTERIOSA"}
INTRO = {"rest": "Uma fogueira ilumina o corredor. É seguro descansar aqui.",
         "swap": "Um mercador sombrio oferece trocar uma das suas cartas. Pode ser uma bênção... ou não.",
         "mystery": "Uma porta antiga se abre sozinha. O que haverá lá dentro?"}


class EventScreen:
    def __init__(self, game, kind=None):
        self.game = game
        self.run = game.run
        self.shop = game.data["shop"]
        self.rng = game.run.rng
        self.kind = kind or events.pick_event(self.run, self.shop, self.rng)
        self.result = None            # texto do resultado (depois de escolher)
        self.new_card = None          # carta RECEBIDA (swap / sala misteriosa)
        self.given_card = None        # carta ENTREGUE na troca (ou MANTIDA, se nada de útil apareceu)
        self.given_kept = False
        self.confirm = None           # índice da carta da troca aguardando confirmação (None = nenhuma)
        self.selected = 0
        self.options = self._options()
        wide = 980 if self.kind != "swap" else 620          # na troca sobra espaço à direita para a carta em destaque
        self.rects = [pygame.Rect(150, 300 + i * 70, wide, 58) for i in range(len(self.options))]
        game.audio.play("reward")

    def _options(self):
        if self.kind == "rest":
            cfg = self.shop["events"]
            return [f"Descansar: recuperar {int(cfg['rest_heal_pct'] * 100)}% da vida", f"Meditar: ganhar {cfg['rest_energy']} de energia"]
        if self.kind == "swap":
            return [f"Trocar: {c['name']}" for c in events.swap_options(self.run)] + ["Recusar a troca"]
        return ["Entrar na sala", "Seguir em frente"]

    def choose(self, i):
        if self.result is not None:
            return
        if self.kind == "rest":
            self.result = events.rest(self.run, self.shop, "heal" if i == 0 else "energy")
        elif self.kind == "swap":
            cards = events.swap_options(self.run)
            if i < len(cards):
                if self.confirm != i:                      # 1º: só marca a carta e pede confirmação (nada é perdido ainda)
                    self.confirm = i
                    self.selected = i
                    return
                card = cards[i]                            # 2º: confirmou ESTA carta
                self.new_card, _ok, self.result = events.swap(self.run, self.shop, card, self.rng)
                self.given_card = card
                self.given_kept = self.new_card is None    # sem troca: a carta continua com o jogador
            else:
                self.result = "Você recusou a oferta."
        else:
            if i == 0:
                self.result, self.new_card = events.mystery_full(self.run, self.shop, self.rng)
            else:
                self.result = "Você seguiu em frente."
        self.confirm = None
        self.rects = []

    def cancel(self):
        """Voltar: desfaz a confirmação pendente (a troca só acontece depois do 2º Enter/clique na mesma carta)."""
        self.confirm = None

    def _preview_card(self):
        """Carta da troca em destaque (a selecionada, ou a que aguarda confirmação)."""
        cards = events.swap_options(self.run)
        index = self.confirm if self.confirm is not None else self.selected
        return cards[index] if index < len(cards) else None
    def handle_input(self, inp):
        if self.result is not None:
            if inp.pressed("swap") or inp.click:
                self.game.on_event_done()
            return
        if inp.pressed("back"):
            self.cancel()
        if inp.pressed("up"):
            self.selected = (self.selected - 1) % len(self.options)
        if inp.pressed("down"):
            self.selected = (self.selected + 1) % len(self.options)
        if inp.pressed("swap"):
            self.choose(self.selected)
            return
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(inp.mouse_pos):
                self.selected = i
            if inp.click and rect.collidepoint(inp.click):
                self.choose(i)
                return

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(config.BACKGROUND_COLOR)
        draw_text(surface, f"ANDAR {self.run.floor_number} CONCLUÍDO", 30, config.MUTED_TEXT_COLOR, (640, 50))
        draw_text(surface, TITLES[self.kind], 62, config.ACCENT_COLOR, (640, 112), shadow=True)
        draw_wrapped(surface, INTRO[self.kind], 28, config.TEXT_COLOR, (190, 170), 900, 34)
        draw_text(surface, f"Vida: {int(self.run.player.hp)} / {self.run.player.max_hp}   Energia: {int(self.run.player.energy)}", 24,
                  config.MUTED_TEXT_COLOR, (640 if self.kind != "swap" else 460, 260))
        for i, (text, rect) in enumerate(zip(self.options, self.rects)):
            active = i == self.selected
            pygame.draw.rect(surface, (60, 60, 98) if active else (32, 32, 50), rect, border_radius=12)
            pygame.draw.rect(surface, config.ACCENT_COLOR if active else (80, 80, 110), rect, width=4 if active else 2, border_radius=12)
            draw_text(surface, text, 26 if self.kind == "swap" else 30, config.TEXT_COLOR, rect.center)
        if self.kind == "swap" and self.result is None:
            self._draw_swap_preview(surface)
        if self.result is not None:
            self._draw_result(surface)

    # ------------------------------------------------------------ cartas envolvidas
    def _draw_swap_preview(self, surface):
        """Carta que seria ENTREGUE (nome, arte, raridade e efeito completos) + o que a troca pode render + confirmação."""
        card = self._preview_card()
        if card is None:
            return
        pending = self.confirm is not None
        draw_text(surface, "VOCÊ ENTREGA", 24, (255, 120, 120), (950, 292))
        draw_card_face(surface, pygame.Rect(800, 306, 300, 330), card, active=True)
        cfg = self.shop["events"]
        fail = int(cfg["swap_fail_chance"] * 100)
        draw_wrapped(surface, f"Recebe uma carta aleatória de raridade acima ({100 - fail}%) ou abaixo ({fail}%).", 20,
                     config.MUTED_TEXT_COLOR, (150, 660 if not pending else 652), 620, 22)
        if pending:
            draw_text(surface, f"Entregar {card['name']}?  Enter / clique de novo: confirmar   Esc: cancelar", 22, (255, 190, 90), (460, 696))

    def _draw_result(self, surface):
        """Resultado: carta PERDIDA/MANTIDA e carta RECEBIDA lado a lado, com raridade e efeito completos."""
        has_cards = self.new_card is not None or self.given_card is not None
        if not has_cards:
            draw_panel(surface, (150, 300, 980, 200))
            draw_wrapped(surface, self.result, 32, config.TEXT_COLOR, (190, 330), 900, 38)
            draw_text(surface, "Enter ou clique: continuar", 26, config.ACCENT_COLOR, (640, 560))
            return
        x = 130
        if self.given_card is not None:
            label, color = ("MANTIDA", (150, 200, 255)) if self.given_kept else ("PERDIDA", (255, 120, 120))
            draw_text(surface, label, 26, color, (x + 150, 292))
            draw_card_face(surface, pygame.Rect(x, 306, 300, 330), self.given_card)
            x += 330
        if self.new_card is not None:
            draw_text(surface, "RECEBIDA", 26, (120, 230, 140), (x + 150, 292))
            draw_card_face(surface, pygame.Rect(x, 306, 300, 330), self.new_card, active=True)
            x += 330
        draw_panel(surface, (x, 306, 1150 - x, 250))
        draw_wrapped(surface, self.result, 28, config.TEXT_COLOR, (x + 16, 322), 1150 - x - 32, 34)
        draw_text(surface, "Enter ou clique: continuar", 26, config.ACCENT_COLOR, (640, 680))
