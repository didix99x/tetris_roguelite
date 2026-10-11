"""
ui/battle_screen.py - a TELA DE BATALHA.

Liga: entrada do jogador -> Combat (lógica) -> desenho (tabuleiro, HUD, efeitos).
Também transforma os "eventos" do Combat em sons e efeitos visuais.
"""
import config
import pygame
from combat.combat import IDLE
from game.audio import chain_sound
from ui import theme
from ui.ability_fx import AbilityFX
from ui.backgrounds import draw_background
from ui.board_view import BoardView
from ui.hint import draw_hint, find_hint
from ui.boss_warning import AppearanceWarning
from ui.hud import draw_hud
from ui.phoenix_rebirth import PhoenixRebirth
from ui.portraits import draw_portrait
from ui.vfx import VFX
from ui.widgets import draw_text, wrap_text


class BattleScreen:
    def __init__(self, game):
        self.game = game
        self.run = game.run
        self.combat = self.run.start_floor()
        self.view = BoardView()
        self.vfx = VFX()
        self.idle = 0.0                                  # segundos sem o jogador agir (dica de jogada)
        self.hint = None                                 # (x, y) da dica atual
        self.hint_after = float(game.run.data.get("shop", {}).get("hint", {}).get("idle_seconds", 6.0))
        self._mouse = None
        self.vfx.shake_enabled = bool(game.settings.get("screen_shake"))
        self.fx = AbilityFX()                       # efeitos das habilidades (ui/ability_fx.py)
        self.fx_ctx = self._build_fx_context()
        self.time = 0.0
        self.paused = False
        self.rebirth = PhoenixRebirth()          # animação da carta Phoenix (só visual; congela o combate enquanto toca)
        self.end_timer = 0.0
        self.banner_time = 2.2
        message = getattr(self.combat.enemy, "appearance_message", None)      # ex.: Yoshi, o Rei do Tetris (andar 100)
        if self.combat.enemy.is_boss:
            game.audio.play("boss")                                      # som grave de entrada do chefe
        self.warning = AppearanceWarning(message["text"], message.get("seconds", 4.0)) if message else None
        self.intro_band = pygame.Surface((config.SCREEN_WIDTH, 200), pygame.SRCALPHA)
        self.blind_layer = pygame.Surface((self.view.width_px + 16, self.view.height_px + 16), pygame.SRCALPHA)
        self.overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 170))

    def _update_hint(self, dt):
        """Dica de jogada: depois de alguns segundos parado, destaca (SEM executar) uma troca possível."""
        if self.paused or self.combat.result or self.combat.phase != IDLE or self.banner_time > 0 or self.rebirth.active:
            self.idle, self.hint = 0.0, None
            return
        self.idle += dt
        if self.idle >= self.hint_after and self.hint is None:
            self.hint = find_hint(self.combat.board)

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
        if any(inp.pressed(n) for n in ("left", "right", "up", "down", "swap", "ability", "back")) or inp.click or \
                (self._mouse is not None and inp.mouse_pos != self._mouse):
            self.idle, self.hint = 0.0, None                # o jogador voltou a jogar: a dica some
        self._mouse = inp.mouse_pos
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
        if self.rebirth.active:                 # durante a animação da Phoenix ninguém joga (evita ação em estado inválido)
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
        if self.rebirth.active:                 # Phoenix: o combate fica congelado (inimigo, veneno, tempo) até a animação acabar
            self.rebirth.update(dt)
        else:
            self.combat.update(dt)
        self._process_events()
        self.vfx.update(dt)
        self.fx.update(dt)
        self._update_hint(dt)
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
                audio.play("match_big" if len(event["cells"]) >= 4 else "match")
                for (x, y, color_id) in event["cells"]:
                    px, py = view.cell_center(x, y)
                    vfx.add_burst(px, py, config.BLOCK_COLORS.get(color_id, (255, 255, 255)), 4)
            elif kind == "chain":
                audio.play(chain_sound(event["level"]))          # x2, x3, x4+: cada vez mais agudo e forte
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
            elif kind == "second_wind":
                if self.rebirth.start():        # 1x por andar (o combate já garante); um 2º aviso durante a animação é ignorado
                    audio.play("reward")
                    vfx.add_shake(5, 0.3)
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
        draw_background(surface, self.combat.enemy, self.run.floor_number, self.run.mode)      # fundo do tema (só visual)
        offset = self.vfx.shake_offset()
        draw_hud(surface, self.combat, self.run)
        self.view.draw(surface, self.combat.board, self.time, offset,
                       show_cursor=not self.combat.result)
        if self.hint:
            draw_hint(surface, self.view, self.hint, self.time)
        self.fx.draw(surface)
        self._draw_blind(surface)
        self.vfx.draw(surface)

        if self.banner_time > 0 and not self.paused:
            enemy = self.combat.enemy
            if enemy.is_boss:
                # apresentação rápida do chefe: faixa escura, retrato e nome deslizando (dura o mesmo que o banner)
                elapsed = 2.2 - self.banner_time
                slide = 1.0 - (1.0 - min(1.0, elapsed / 0.35)) ** 3
                self.intro_band.fill((0, 0, 0, int(175 * min(1.0, elapsed * 5) * min(1.0, self.banner_time / 0.4))))
                surface.blit(self.intro_band, (0, 240))
                pygame.draw.line(surface, enemy.color, (0, 240), (int(config.SCREEN_WIDTH * slide), 240), 4)
                pygame.draw.line(surface, enemy.color, (config.SCREEN_WIDTH, 440), (int(config.SCREEN_WIDTH * (1 - slide)), 440), 4)
                draw_portrait(surface, (int(-150 + 196 * slide), 290), 130, enemy)
                offset = int((1.0 - slide) * -420)
                if getattr(enemy, "is_super", False):
                    draw_text(surface, "SUPER BOSS", 40, (255, 90, 70), (640 + offset, 262))
                draw_text(surface, f"ANDAR {self.run.floor_number}", 48, config.ACCENT_COLOR, (640 + offset, 300))
                draw_text(surface, enemy.name.upper(), 72, enemy.color, (640 + offset, 360), shadow=True)
                for i, line in enumerate(wrap_text(enemy.passive_label(), 26, 900)[:3]):
                    draw_text(surface, line, 26, config.TEXT_COLOR, (640, 415 + i * 30))
            else:
                draw_text(surface, f"ANDAR {self.run.floor_number}", 60, config.ACCENT_COLOR, (640, 330))
                draw_text(surface, f"{enemy.name} apareceu!", 36, config.TEXT_COLOR, (640, 380))

        if self.warning and self.warning.active and not self.paused:
            self.warning.draw(surface)
        if self.rebirth.active and not self.paused:
            self.rebirth.draw(surface)

        if self.paused:
            surface.blit(self.overlay, (0, 0))
            draw_text(surface, "PAUSADO", 80, config.ACCENT_COLOR, (640, 290))
            draw_text(surface, "Enter: continuar     Q: abandonar a run     Esc: continuar",
                      30, config.TEXT_COLOR, (640, 370))
