"""ui/game_over.py - telas de GAME OVER e VITÓRIA (com parabéns e aviso do Modo Infinito)."""
import pygame

import config
from game.state import GameState
from ui.widgets import draw_panel, draw_text, wrap_text


class GameOverScreen:
    def __init__(self, game, victory):
        self.game = game
        self.victory = victory
        self.run = game.run
        self.first_unlock = victory and game.just_unlocked_infinite
        game.audio.play("win" if victory else "lose")

    def handle_input(self, inp):
        if inp.pressed("swap") or inp.pressed("back") or inp.click:
            self.game.run = None
            self.game.change_state(GameState.MENU)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(config.BACKGROUND_COLOR)
        if self.victory:
            self._draw_victory(surface)
        else:
            self._draw_defeat(surface)

    # ---------------------------------------------------------------- vitória (fim do tutorial)
    def _draw_victory(self, surface):
        run = self.run
        draw_text(surface, "PARABÉNS!", 120, config.ACCENT_COLOR, (640, 120))
        draw_text(surface, "Você concluiu o tutorial do jogo.", 50, config.TEXT_COLOR, (640, 230))
        draw_text(surface, "Agora começa uma nova missão...", 42, config.MUTED_TEXT_COLOR, (640, 320))
        panel = pygame.Rect(200, 380, 880, 150)
        draw_panel(surface, panel, border=config.ACCENT_COLOR)
        draw_text(surface, "Salve nossos heróis do Vórtice Infinito.", 54, (140, 230, 255), (640, 430))
        draw_text(surface, "Procure o MODO INFINITO no menu principal.", 30, config.TEXT_COLOR, (640, 492))
        if run:
            draw_text(surface, f"{run.player.name}  -  {len(run.taken_rewards)} recompensas coletadas",
                      26, config.MUTED_TEXT_COLOR, (640, 580))
<<<<<<< HEAD
        self._draw_points(surface, 612)
        draw_text(surface, "Pressione Enter para voltar ao menu", 30, config.ACCENT_COLOR, (640, 664))

    def _draw_points(self, surface, y):
        """Pontos permanentes ganhos na run (ficam salvos mesmo ao perder)."""
        earned = getattr(self.game, "run_points", 0)
        total = self.game.progress.points
        draw_text(surface, f"+{earned} PONTOS   (total: {total})   -   gaste na LOJA", 28, (255, 215, 90), (640, y))
=======
        draw_text(surface, "Pressione Enter para voltar ao menu", 30, config.ACCENT_COLOR, (640, 650))
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

    # ---------------------------------------------------------------- derrota
    def _draw_defeat(self, surface):
        run = self.run
        draw_text(surface, "GAME OVER", 120, (230, 70, 80), (640, 150))
        draw_text(surface, "Os bônus desta run foram perdidos.", 36, config.TEXT_COLOR, (640, 240))
        if run:
            draw_text(surface, f"Personagem: {run.player.name}", 34, config.TEXT_COLOR, (640, 330))
            draw_text(surface, f"Andar alcançado: {run.floor_number}", 34, config.TEXT_COLOR, (640, 375))
            draw_text(surface, f"Recompensas coletadas: {len(run.taken_rewards)}", 34, config.TEXT_COLOR, (640, 420))
        progress = self.game.progress
        if run and run.mode == "infinite":
            draw_text(surface, f"Melhor andar no Modo Infinito: {progress.best_infinite_floor}", 28,
                      config.MUTED_TEXT_COLOR, (640, 480))
        else:
            draw_text(surface, f"Melhor andar de todos: {progress.best_floor}", 28, config.MUTED_TEXT_COLOR, (640, 480))
<<<<<<< HEAD
        self._draw_points(surface, 540)
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        draw_text(surface, "Pressione Enter para voltar ao menu", 30, config.ACCENT_COLOR, (640, 600))
