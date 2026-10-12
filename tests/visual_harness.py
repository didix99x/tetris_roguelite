"""
tests/visual_harness.py - monta a TELA DE BATALHA de verdade (RunManager + Combat reais) sem janela,
para testes e para gerar capturas de tela (PNG) da HUD e dos efeitos.

Usa o pygame oficial se estiver instalado (com driver de vídeo "dummy"); senão, o tests/pygame_lite.py.

Exemplo (gera uma captura):
    python -c "from tests.visual_harness import *; s=make_screen('warrior'); step(s, 30); shot(s, 'captura.png')"
"""
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

try:
    import pygame
    pygame.font.init()
    pygame.display.init()
    pygame.display.set_mode((1, 1))      # video mode (invisível, driver "dummy"): convert_alpha() exige isso
    LITE = False
except ImportError:                      # sem pygame: usa o mini-pygame baseado em Pillow
    from tests import pygame_lite
    pygame = pygame_lite.install()
    LITE = True

import config
from combat.combat import IDLE
from run.run_manager import RunManager
from tests.test_logic import bot_move, load_data


class FakeAudio:
    def play(self, name):
        pass


class FakeGame:
    def __init__(self, run):
        self.run, self.audio = run, FakeAudio()
        self.settings = type("Settings", (), {"get": lambda self, key: {"screen_shake": True}.get(key, 0.5)})()
        self.won = self.lost = False

    def on_battle_won(self):
        self.won = True

    def on_battle_lost(self):
        self.lost = True

    def abandon_run(self):
        pass


class FakeInput:
    click = None
    mouse_pos = (0, 0)

    def pressed(self, name):
        return False


def set_time(ms):
    if LITE:
        pygame.set_ticks(ms)


def make_screen(char="warrior", floor=1, mode="infinite", seed=1, data=None):
    from ui.battle_screen import BattleScreen
    data = data or load_data()
    run = RunManager(char, data, random.Random(seed), mode=mode)
    run.floor_number = floor
    screen = BattleScreen(FakeGame(run))
    screen.banner_time = 0.0
    screen.rng = random.Random(seed + 1)
    return screen


def new_surface():
    return pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))


def step(screen, frames=1, dt=1 / 60, play=True, surface=None):
    """Avança `frames` quadros (com jogadas do bot) e desenha cada um (como o jogo faria)."""
    surface = surface or new_surface()
    for _ in range(frames):
        if play and screen.combat.phase == IDLE and not screen.combat.result:
            bot_move(screen.combat, screen.rng)
        screen.update(dt)
        set_time(int(screen.time * 1000))
        screen.draw(surface)
    return surface


def shot(screen, path, surface=None):
    surface = surface or new_surface()
    set_time(int(screen.time * 1000))
    screen.draw(surface)
    if hasattr(surface, "save"):
        surface.save(path)
    else:
        pygame.image.save(surface, path)
    return surface


def cast(screen, settle_frames=0):
    """Espera o tabuleiro ficar parado e usa a habilidade (como apertar Q). Devolve True se funcionou."""
    for _ in range(600):
        if screen.combat.phase == IDLE and not screen.combat.result:
            break
        step(screen, 1, play=False)
    screen.combat.player.energy = screen.combat.player.energy_max
    ok = screen.combat.use_ability()
    step(screen, 1 + settle_frames, play=False)
    return ok
