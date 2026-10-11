"""ui/boss_offer.py - "UM BOSS ESPECIAL APARECEU!" (ENFRENTAR ou IGNORAR). Usa o mesmo ButtonList do menu."""
import config
from ui.widgets import ButtonList, draw_text


class BossOfferScreen:
    def __init__(self, game):
        self.game = game
        self.buttons = ButtonList(["ENFRENTAR", "IGNORAR"], start_y=380, height=64, gap=20)
        self.time = 0.0
        game.audio.play("enemy_ability")

    def handle_input(self, inp):
        choice = self.buttons.handle(inp, self.game.audio)
        if choice is not None:
            self.game.on_boss_offer(choice == 0)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.fill(config.BACKGROUND_COLOR)
        draw_text(surface, "UM BOSS ESPECIAL APARECEU!", 76, (255, 120, 90), (640, 150))
        draw_text(surface, "Você deseja enfrentá-lo?", 48, config.TEXT_COLOR, (640, 250))
        draw_text(surface, "Se vencer: escolha uma carta LENDÁRIA.", 28, config.ACCENT_COLOR, (640, 312))
        draw_text(surface, "Se perder: a run termina.", 28, (255, 150, 120), (640, 346))
        self.buttons.draw(surface)
        run = self.game.run
        if run:
            draw_text(surface, f"Andar {run.floor_number}", 24, config.MUTED_TEXT_COLOR, (640, 640))
