"""ui/reward_screen.py - ESCOLHA UMA RECOMPENSA (1 de 3)."""
<<<<<<< HEAD
import math

=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
import pygame

import config
from rewards.reward import rarity_color, rarity_name
<<<<<<< HEAD
from ui.card_art import draw_card_face
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
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
        for i, text in enumerate(self.game.unlock_notice):          # "TULIPA DESBLOQUEADA!"
<<<<<<< HEAD
            draw_text(surface, text, 44, (140, 230, 255), (640, 590 + i * 40), shadow=True)
        if self.game.unlock_notice:                                 # cena curta de herói desbloqueado
            pulse = 0.5 + 0.5 * math.sin(pygame.time.get_ticks() / 260.0)
            draw_text(surface, "SALVE OS HERÓIS DO VÓRTICE.", 30, tuple(int(c) for c in (255, 190 + 40 * pulse, 90)),
                      (640, 600 + len(self.game.unlock_notice) * 40), shadow=True)

        for i, (reward, rect) in enumerate(zip(self.rewards, self.rects)):
            draw_card_face(surface, rect, reward, active=(i == self.selected))      # arte + moldura da raridade (ui/card_art.py)
=======
            draw_text(surface, text, 44, (140, 230, 255), (640, 590 + i * 40))

        for i, (reward, rect) in enumerate(zip(self.rewards, self.rects)):
            color = rarity_color(reward)
            active = i == self.selected
            pygame.draw.rect(surface, (50, 50, 78) if active else (32, 32, 50), rect, border_radius=14)
            pygame.draw.rect(surface, color, rect, width=5 if active else 2, border_radius=14)
            draw_text(surface, rarity_name(reward).upper(), 28, color, (rect.centerx, rect.y + 36))
            draw_text(surface, reward["name"], 40, config.TEXT_COLOR, (rect.centerx, rect.y + 90))
            draw_wrapped(surface, reward["description"], 30, config.TEXT_COLOR,
                         (rect.x + 24, rect.y + 150), rect.width - 48, 34)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        draw_text(surface, "Setas: escolher   Enter ou clique: confirmar", 24, config.MUTED_TEXT_COLOR, (640, 640))
