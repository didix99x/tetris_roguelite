"""
game/game.py - O JOGO: janela, loop principal e troca de telas.

Loop:  Input -> Update -> Render -> Clock
O jogo SEMPRE desenha em 1280x720 (canvas) e depois escala para a janela,
mantendo a proporção (faixas pretas se a janela tiver outro formato).
"""
import logging

import pygame

import config
from game.audio import AudioManager
from game.data_loader import load_all
from game import music_map
from game.input import Input
from game.save import Progress
from game.settings import Settings
from game.state import GameState
from run.run_manager import RunManager

log = logging.getLogger(__name__)


class Game:
    def __init__(self):
        pygame.mixer.pre_init(22050, -16, 1, 512)
        pygame.init()
        self.data = load_all()
        self.settings = Settings()
        self.progress = Progress(self.data["characters"])

        self.canvas = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        self.view_scale = 1.0
        self.view_offset = (0, 0)
        self._scaled = None
        self.apply_display_mode()
        pygame.display.set_caption(f"{config.GAME_TITLE} v{config.VERSION}")

        self.clock = pygame.time.Clock()
        self.audio = AudioManager(self.settings)
        self.input = Input(self.settings, self.to_canvas)
        pygame.key.set_repeat(220, 70)

        self.running = True
        self.pending_mode = "story"        # modo escolhido no menu: "story" ou "infinite"
        self.just_unlocked_infinite = False
        self.unlock_notice = []              # personagens desbloqueados agora (mostrado na tela de recompensa)
        self.special_reward_pending = False  # True quando a recompensa atual é a carta LENDÁRIA do Boss especial
        self.bonus_picks_left = 0            # cartas extras a escolher (Yoshi: 3 lendárias)
        self.bonus_picks_total = 0
        self.bonus_rarity = "legendary"
        self.bonus_title = ""
        self.run = None
        self.state = None
        self.screen = None
        self.change_state(GameState.MENU)

    # ------------------------------------------------ janela / escala
    def apply_display_mode(self):
        mode = self.settings.get("window_mode")
        if mode == "fullscreen":
            pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        elif mode == "borderless":
            size = pygame.display.get_desktop_sizes()[0]
            pygame.display.set_mode(size, pygame.NOFRAME)
        else:
            size = (self.settings.get("window_width"), self.settings.get("window_height"))
            pygame.display.set_mode(size, pygame.RESIZABLE)
        self._scaled = None

    def toggle_fullscreen(self):
        mode = self.settings.get("window_mode")
        self.settings.set("window_mode", "windowed" if mode == "fullscreen" else "fullscreen")
        self.apply_display_mode()
        self.settings.save()

    def to_canvas(self, pos):
        """Converte uma posição da janela para a posição no canvas 1280x720."""
        ox, oy = self.view_offset
        return ((pos[0] - ox) / self.view_scale, (pos[1] - oy) / self.view_scale)

    def present(self):
        window = pygame.display.get_surface()
        ww, wh = window.get_size()
        cw, ch = self.canvas.get_size()
        if (ww, wh) == (cw, ch):
            window.blit(self.canvas, (0, 0))
            self.view_scale, self.view_offset = 1.0, (0, 0)
        else:
            scale = min(ww / cw, wh / ch)
            size = (max(1, int(cw * scale)), max(1, int(ch * scale)))
            if self._scaled is None or self._scaled.get_size() != size:
                self._scaled = pygame.Surface(size)
            pygame.transform.scale(self.canvas, size, self._scaled)
            offset = ((ww - size[0]) // 2, (wh - size[1]) // 2)
            window.fill((0, 0, 0))
            window.blit(self._scaled, offset)
            self.view_scale, self.view_offset = scale, offset
        pygame.display.flip()

    # ------------------------------------------------ estados / telas
    def change_state(self, state, **kwargs):
        # Importações aqui dentro evitam dependência circular entre telas e Game.
        from ui.battle_screen import BattleScreen
        from ui.boss_offer import BossOfferScreen
        from ui.character_select import CharacterSelectScreen
        from ui.game_over import GameOverScreen
        from ui.menu import MenuScreen, OptionsScreen
        from ui.reward_screen import RewardScreen

        self.state = state
        if state == GameState.MENU:
            self.screen = MenuScreen(self)
        elif state == GameState.OPTIONS:
            self.screen = OptionsScreen(self)
        elif state == GameState.CHARACTER_SELECT:
            self.screen = CharacterSelectScreen(self)
        elif state == GameState.BATTLE:
            self.screen = BattleScreen(self)
        elif state == GameState.REWARD:
            self.screen = RewardScreen(self, kwargs["rewards"])
        elif state == GameState.BOSS_OFFER:
            self.screen = BossOfferScreen(self)
        elif state == GameState.GAME_OVER:
            self.screen = GameOverScreen(self, victory=False)
        elif state == GameState.VICTORY:
            self.screen = GameOverScreen(self, victory=True)
        enemy_is_boss = state == GameState.BATTLE and self.screen.combat.enemy.is_boss
        self.audio.play_situation(music_map.situation_for(state, self.run, enemy_is_boss))
        log.info("Estado: %s", state)

    # ------------------------------------------------ fluxo da run
    def start_run(self, char_id):
        self.just_unlocked_infinite = False
        self.unlock_notice = []
        self.special_reward_pending = False
        self.bonus_picks_left = self.bonus_picks_total = 0
        self.run = RunManager(char_id, self.data, mode=self.pending_mode,
                              unlocked_characters=self.progress.unlocked)
        self.change_state(GameState.BATTLE)

    def _unlock_defeated_character(self, enemy):
        """Se o inimigo derrotado é um PERSONAGEM jogável, desbloqueia-o para sempre."""
        char_id = getattr(enemy, "character_id", None)
        if char_id and self.progress.unlock_character(char_id):
            char = self.data["characters"][char_id]
            ending = "A" if char.get("gender") == "f" else "O"
            self.unlock_notice.append(f"{char['name'].upper()} DESBLOQUEAD{ending}!")
            self.progress.save()                      # salva na hora: não se perde se a run acabar

    def on_battle_won(self):
        run = self.run
        self._unlock_defeated_character(run.floor.enemy)
        if run.special_active:                       # venceu o BOSS ESPECIAL
            run.special_active = False
            self.special_reward_pending = True
            self.progress.save()
            self.change_state(GameState.REWARD, rewards=run.roll_rewards(only_rarity="legendary"))
            return
        run.floor_cleared()
        if run.mode == "infinite":
            self.progress.record_infinite_floor(run.floor_number)
            self.progress.save()
            bonus = getattr(run.floor.enemy, "reward", None)         # Yoshi (andar 100): 3 cartas lendárias
            if bonus:
                self.bonus_picks_total = self.bonus_picks_left = int(bonus.get("cards", 3))
                self.bonus_rarity = bonus.get("rarity", "legendary")
                self.bonus_title = f"{run.floor.enemy.name.upper()} DERROTADO!"
                self.change_state(GameState.REWARD, rewards=self._roll_bonus_rewards())
                return
            self.change_state(GameState.REWARD, rewards=run.roll_rewards())
            return
        self.progress.record_floor(run.floor_number)
        if run.finished:
            self.progress.runs += 1
            self.progress.wins += 1
            self.just_unlocked_infinite = self.progress.unlock_infinite()
            self.progress.save()
            self.change_state(GameState.VICTORY)
        else:
            self.progress.save()
            self.change_state(GameState.REWARD, rewards=run.roll_rewards())

    def _roll_bonus_rewards(self):
        """3 opções da raridade do bônus, sem repetir cartas que o jogador já pegou neste andar/run."""
        taken = {r["id"] for r in self.run.taken_rewards}
        pool = self.run.roll_rewards(only_rarity=self.bonus_rarity, count=12)
        fresh = [r for r in pool if r["id"] not in taken]
        return (fresh if len(fresh) >= 3 else pool)[:3]

    def on_reward_chosen(self, reward):
        self.run.take_reward(reward)
        self.progress.discover(reward["id"])
        self.unlock_notice = []
        if self.bonus_picks_left > 0:                # próxima carta lendária do Yoshi (1/3, 2/3, 3/3)
            self.bonus_picks_left -= 1
            if self.bonus_picks_left > 0:
                self.change_state(GameState.REWARD, rewards=self._roll_bonus_rewards())
                return
        if self.special_reward_pending:              # carta lendária do Boss especial: o andar já estava avançado
            self.special_reward_pending = False
            self.change_state(GameState.BATTLE)
            return
        self.run.advance_floor()
        if self.run.mode == "infinite" and self.roll_special_boss():
            self.change_state(GameState.BOSS_OFFER)
        else:
            self.change_state(GameState.BATTLE)

    def roll_special_boss(self):
        """Sorteio do encontro especial com Boss (chance em data/floors.json > infinite > special_boss_chance)."""
        if self.run.floor_number == self.data["enemies"].get("yoshi", {}).get("infinite", {}).get("floor"):
            return False                              # o andar do Yoshi nunca tem Boss especial no lugar
        chance = self.data["floors"].get("infinite", {}).get("special_boss_chance", 0.02)
        return self.run.rng.random() < chance

    def on_boss_offer(self, accept):
        """ENFRENTAR (accept=True) começa o combate do Boss especial; IGNORAR segue a run normalmente."""
        self.run.special_active = bool(accept)
        self.change_state(GameState.BATTLE)

    def on_battle_lost(self):
        self.progress.runs += 1
        self.progress.save()
        self.change_state(GameState.GAME_OVER)

    def abandon_run(self):
        self.progress.runs += 1
        self.progress.save()
        self.run = None
        self.change_state(GameState.MENU)

    def quit(self):
        self.running = False

    # ------------------------------------------------ loop principal
    def run_loop(self):
        dt = 0.0
        while self.running:
            # 1) INPUT
            self.input.begin_frame()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                else:
                    self.input.handle_event(event)
            self.screen.handle_input(self.input)
            # 2) UPDATE
            self.screen.update(dt)
            # 3) RENDER
            self.screen.draw(self.canvas)
            self.present()
            # 4) CLOCK
            dt = min(self.clock.tick(config.FPS) / 1000.0, 0.05)
        self.settings.save()
        self.progress.save()
        pygame.quit()
