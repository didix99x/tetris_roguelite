"""
ui/battle_screen.py - a TELA DE BATALHA.

Liga: entrada do jogador -> Combat (lógica) -> desenho (tabuleiro, HUD, efeitos).
Também transforma os "eventos" do Combat em sons e efeitos visuais.
"""
import config
import pygame
from ui import theme
from ui.ability_fx import AbilityFX
from ui.board_view import BoardView
from ui.boss_warning import AppearanceWarning
from ui.hud import draw_hud
from ui.vfx import VFX
from ui.widgets import draw_text, wrap_text


class BattleScreen:
    def __init__(self, game):
        self.game = game
        self.run = game.run
        self.combat = self.run.start_floor()
        self.view = BoardView()
        self.vfx = VFX()
        self.fx = AbilityFX()                       # efeitos das habilidades (ui/ability_fx.py)
        self.fx_ctx = self._build_fx_context()
        self.time = 0.0
        self.paused = False
        self.end_timer = 0.0
        self.banner_time = 2.2
        message = getattr(self.combat.enemy, "appearance_message", None)      # ex.: Yoshi, o Rei do Tetris (andar 100)
        self.warning = AppearanceWarning(message["text"], message.get("seconds", 4.0)) if message else None
        self.blind_layer = pygame.Surface((self.view.width_px + 16, self.view.height_px + 16), pygame.SRCALPHA)
        self.overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 170))

    def _draw_blind(self, surface):
        """CEGUEIRA do Yoshi: escurece a área de jogo pelo tempo restante de combat.blind_time (2 s). SÓ visual:
        o jogo continua funcionando por baixo e volta ao normal sozinho quando o tempo acaba."""
        left = self.combat.blind_time
        if left <= 0:
            return
        total = self.combat.blind_total or 2.0
        alpha = 248 * max(0.0, min(1.0, (total - left) / 0.15, left / 0.25))     # escurece rápido, clareia suave
        self.blind_layer.fill((4, 2, 8, int(alpha)))
        surface.blit(self.blind_layer, (self.view.x - 8, self.view.y - 8))
        if alpha > 120:
            draw_text(surface, "CEGO!", 64, (170, 20, 30), (self.view.x + self.view.width_px // 2, self.view.y + self.view.height_px // 2))

    def _build_fx_context(self):
        """Pontos da tela usados pelos efeitos (vêm de ui/theme.py, os mesmos da HUD)."""
        px, py, ps = theme.PLAYER_PORTRAIT
        ex, ey, es = theme.ENEMY_PORTRAIT
        return {"P": (px + ps // 2, py + ps // 2), "E": (ex + es // 2, ey + es // 2),
                "B": (self.view.x + self.view.width_px // 2, self.view.y + self.view.height_px // 2),
                "player_rect": pygame.Rect(px, py, ps, ps), "enemy_rect": pygame.Rect(ex, ey, es, es),
                "attack_bar": theme.ATTACK_BAR_RECT}

    # ------------------------------------------------ entrada
    def handle_input(self, inp):
        combat = self.combat
        if combat.result:
            return
        if inp.pressed("back"):
            self.paused = not self.paused
            return
        if self.paused:
            if inp.pressed("swap"):
                self.paused = False
            elif inp.pressed("ability"):
                self.game.abandon_run()
            return

        if inp.pressed("left"):
            combat.move_cursor(-1, 0)
        if inp.pressed("right"):
            combat.move_cursor(1, 0)
        if inp.pressed("up"):
            combat.move_cursor(0, -1)
        if inp.pressed("down"):
            combat.move_cursor(0, 1)
        if inp.pressed("swap"):
            combat.try_swap()
        if inp.pressed("ability"):
            combat.use_ability()

        # Mouse: clique move o cursor; clicar de novo no mesmo par troca.
        if inp.click:
            cell = self.view.cell_at(inp.click)
            if cell:
                x = min(cell[0], combat.board.width - 2)
                if (x, cell[1]) == (combat.board.cursor_x, combat.board.cursor_y):
                    combat.try_swap()
                else:
                    combat.set_cursor(x, cell[1])
                    self.game.audio.play("select")

    # ------------------------------------------------ atualização
    def update(self, dt):
        if self.paused:
            return
        self.time += dt
        if self.banner_time > 0:
            self.banner_time -= dt
        if self.warning:
            self.warning.update(dt)
        self.combat.update(dt)
        self._process_events()
        self.vfx.update(dt)
        self.fx.update(dt)
        if self.combat.result:
            self.end_timer += dt
            if self.end_timer > 1.4:
                if self.combat.result == "win":
                    self.game.on_battle_won()
                else:
                    self.game.on_battle_lost()

    def _process_events(self):
        audio = self.game.audio
        view, vfx = self.view, self.vfx
        center_x = config.SCREEN_WIDTH // 2
        for event in self.combat.pop_events():
            kind = event["type"]
            cells = [view.cell_center(x, y) for (x, y, _c) in event.get("cells", ())] if kind == "burst" else None
            self.fx.react(kind, event, self.fx_ctx, cells)           # impactos visuais (só desenho)
            if kind == "swap":
                audio.play("swap")
            elif kind in ("swap_fail", "ability_fail"):
                audio.play("fail")
            elif kind == "match":
                audio.play("match")
                for (x, y, color_id) in event["cells"]:
                    px, py = view.cell_center(x, y)
                    vfx.add_burst(px, py, config.BLOCK_COLORS.get(color_id, (255, 255, 255)), 4)
            elif kind == "chain":
                audio.play("chain")
                vfx.add_text(f"CHAIN x{event['level']}", center_x, view.y + 40, config.ACCENT_COLOR,
                             52 + 6 * min(event["level"], 6), 1.2)
                vfx.add_shake(3 + event["level"], 0.2)
            elif kind == "explosion":
                audio.play("hit")
                vfx.add_shake(6, 0.25)
                for (x, y, color_id) in event["cells"]:
                    px, py = view.cell_center(x, y)
                    vfx.add_burst(px, py, (255, 200, 90), 6)
            elif kind == "damage_enemy":
                audio.play("hit")
                text = f"-{event['amount']}"
                if event.get("label"):
                    text = f"{event['label']} {text}"
                big = event["amount"] >= 40
                vfx.add_text(text, center_x, 140, (255, 220, 120) if big else (255, 255, 255),
                             44 if big else 34, 0.9)
                if big:
                    vfx.add_shake(5, 0.2)
            elif kind == "damage_player":
                audio.play("hurt")
                vfx.add_text(f"-{event['amount']}", 190, 200, (255, 90, 90), 38, 0.9)
                vfx.add_shake(7, 0.3)
                vfx.add_flash((200, 30, 30), 0.25)
            elif kind == "ability":
                audio.play("ability")
                color = self.fx.trigger(self.combat.player.char_id, self.fx_ctx)      # efeito próprio do personagem
                vfx.add_text(event["name"].upper(), center_x, view.y + view.height_px // 2, color, 56, 1.1)
                vfx.add_flash(color, 0.2, strength=theme.EFFECTS.get("flash_scale", 1.0) * 0.8)
            elif kind == "crit":
                vfx.add_text("CRÍTICO!", center_x, 150, (255, 120, 80), 44, 0.8)
            elif kind == "enemy_heal":
                vfx.add_text(f"+{event['amount']}", center_x, 140, (120, 240, 140), 34, 0.9)
            elif kind == "heal":
                vfx.add_text(f"+{event['amount']}", 190, 290, (120, 240, 140), 34, 0.9)
            elif kind == "burst":
                for (x, y, color_id) in event["cells"]:
                    px, py = view.cell_center(x, y)
                    vfx.add_burst(px, py, config.BLOCK_COLORS.get(color_id, (255, 255, 255)), 8)
            elif kind == "enemy_ability":
                audio.play("enemy_ability")
                vfx.add_text(event["name"].upper(), center_x, view.y + 30, (255, 140, 100), 48, 1.2)
                for (x, y, color_id) in event["cells"]:
                    px, py = view.cell_center(x, y)
                    vfx.add_burst(px, py, (255, 120, 90), 5)
            elif kind == "shuffle":
                vfx.add_text("REEMBARALHANDO!", center_x, view.y + view.height_px // 2, (255, 255, 255), 44, 1.2)
            elif kind == "win":
                audio.play("win")
                vfx.add_text("INIMIGO DERROTADO!", center_x, view.y + view.height_px // 2,
                             config.ACCENT_COLOR, 64, 1.6)
                vfx.add_flash((255, 230, 120), 0.3)
            elif kind == "lose":
                audio.play("lose")
                vfx.add_text("VOCÊ CAIU...", center_x, view.y + view.height_px // 2, (255, 90, 90), 64, 1.6)

    # ------------------------------------------------ desenho
    def draw(self, surface):
        surface.fill(config.BACKGROUND_COLOR)
        offset = self.vfx.shake_offset()
        draw_hud(surface, self.combat, self.run)
        self.view.draw(surface, self.combat.board, self.time, offset,
                       show_cursor=not self.combat.result)
        self.fx.draw(surface)
        self._draw_blind(surface)
        self.vfx.draw(surface)

        if self.banner_time > 0 and not self.paused:
            enemy = self.combat.enemy
            if enemy.is_boss:
                if getattr(enemy, "is_super", False):
                    draw_text(surface, "SUPER BOSS", 40, (255, 90, 70), (640, 262))
                draw_text(surface, f"ANDAR {self.run.floor_number}", 48, config.ACCENT_COLOR, (640, 300))
                draw_text(surface, enemy.name.upper(), 72, enemy.color, (640, 360))
                for i, line in enumerate(wrap_text(enemy.passive_label(), 26, 900)[:3]):
                    draw_text(surface, line, 26, config.TEXT_COLOR, (640, 415 + i * 30))
            else:
                draw_text(surface, f"ANDAR {self.run.floor_number}", 60, config.ACCENT_COLOR, (640, 330))
                draw_text(surface, f"{enemy.name} apareceu!", 36, config.TEXT_COLOR, (640, 380))

        if self.warning and self.warning.active and not self.paused:
            self.warning.draw(surface)

        if self.paused:
            surface.blit(self.overlay, (0, 0))
            draw_text(surface, "PAUSADO", 80, config.ACCENT_COLOR, (640, 290))
            draw_text(surface, "Enter: continuar     Q: abandonar a run     Esc: continuar",
                      30, config.TEXT_COLOR, (640, 370))
