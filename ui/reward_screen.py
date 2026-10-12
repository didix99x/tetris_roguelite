"""ui/reward_screen.py - ESCOLHA UMA RECOMPENSA (1 de 3)."""
import pygame

import config
from rewards.reward import rarity_color, rarity_name
from ui.card_art import draw_card_face
from ui.widgets import draw_text, draw_wrapped


class RewardScreen:
    def __init__(self, game, rewards):
        self.game = game
        self.rewards = rewards
        self.selected = 0
        self.rects = [pygame.Rect(95 + i * 370, 200, 340, 330) for i in range(len(rewards))]
        game.audio.play("reward")

    def _choose(self, index):
        self.game.on_reward_chosen(self.rewards[index])

    def handle_input(self, inp):
        if inp.pressed("left"):
            self.selected = (self.selected - 1) % len(self.rewards)
            self.game.audio.play("select")
        if inp.pressed("right"):
            self.selected = (self.selected + 1) % len(self.rewards)
            self.game.audio.play("select")
        if inp.pressed("swap"):
            self._choose(self.selected)
            return
        for i, rect in enumerate(self.rects):
            if rect.collidepoint(inp.mouse_pos):
                self.selected = i
            if inp.click and rect.collidepoint(inp.click):
                self._choose(i)
                return

    def update(self, dt):
        pass

    def draw(self, surface):
        run = self.game.run
        surface.fill(config.BACKGROUND_COLOR)
        special = self.game.special_reward_pending
        if self.game.bonus_picks_left > 0:                 # cartas lendárias do Yoshi: "CARTA LENDÁRIA (1/3)"
            n = self.game.bonus_picks_total - self.game.bonus_picks_left + 1
            draw_text(surface, self.game.bonus_title, 40, config.ACCENT_COLOR, (640, 60))
            draw_text(surface, f"ESCOLHA UMA CARTA LENDÁRIA ({n}/{self.game.bonus_picks_total})", 54,
                      config.RARITY_COLORS["legendary"], (640, 120))
            draw_text(surface, f"HP: {int(run.player.hp)} / {run.player.max_hp}", 26, config.MUTED_TEXT_COLOR, (640, 165))
        elif special:
            draw_text(surface, "BOSS ESPECIAL DERROTADO!", 40, config.ACCENT_COLOR, (640, 60))
            draw_text(surface, "ESCOLHA UMA CARTA LENDÁRIA", 60, config.RARITY_COLORS["legendary"], (640, 120))
            draw_text(surface, f"HP: {int(run.player.hp)} / {run.player.max_hp}", 26, config.MUTED_TEXT_COLOR, (640, 165))
        else:
            draw_text(surface, f"ANDAR {run.floor_number} CONCLUÍDO", 40, config.ACCENT_COLOR, (640, 60))
            draw_text(surface, "ESCOLHA UMA RECOMPENSA", 60, config.TEXT_COLOR, (640, 120))
            pct = round((run.data["floors"].get("heal_after_floor_pct", 0.25) + run.player.mods["floor_heal_pct"]) * 100)
            draw_text(surface, f"Você recuperou {pct}% da vida.  HP: {int(run.player.hp)} / {run.player.max_hp}",
                      26, config.MUTED_TEXT_COLOR, (640, 165))
        # (o aviso de personagem desbloqueado agora tem tela própria: ui/unlock_screen.py, mostrada ANTES das cartas)

        for i, (reward, rect) in enumerate(zip(self.rewards, self.rects)):
            draw_card_face(surface, rect, reward, active=(i == self.selected))      # arte + moldura da raridade (ui/card_art.py)
        draw_text(surface, "Setas: escolher   Enter ou clique: confirmar", 24, config.MUTED_TEXT_COLOR, (640, 640))
