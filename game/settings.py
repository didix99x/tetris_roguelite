"""
game/settings.py - CONFIGURAÇÕES do jogador (volume, tela, controles).
Salvas em settings.json na pasta do usuário. Este arquivo NÃO usa pygame
(o Launcher também o utiliza).
"""
import copy
import json
import logging

from paths import user_data_dir

log = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "music_volume": 0.5,
    "sfx_volume": 0.7,
    "window_mode": "windowed",      # "windowed", "fullscreen" ou "borderless"
    "window_width": 1280,
    "window_height": 720,
    # Nomes das teclas (padrão do pygame). Cada ação aceita várias teclas.
    "controls": {
        "left": ["left", "a"],
        "right": ["right", "d"],
        "up": ["up", "w"],
        "down": ["down", "s"],
        "swap": ["return", "space"],
        "ability": ["q", "e"],
        "back": ["escape"],
    },
}

RESOLUTIONS = [(1280, 720), (1600, 900), (1920, 1080)]
WINDOW_MODES = ["windowed", "fullscreen", "borderless"]
WINDOW_MODE_NAMES = {"windowed": "Janela", "fullscreen": "Tela cheia", "borderless": "Sem bordas"}


class Settings:
    def __init__(self):
        self.path = user_data_dir() / "settings.json"
        self.data = copy.deepcopy(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        if not self.path.exists():
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                saved = json.load(f)
            for key, value in saved.items():
                if key == "controls" and isinstance(value, dict):
                    self.data["controls"].update(value)
                elif key in self.data:
                    self.data[key] = value
        except (OSError, ValueError):
            log.exception("Não foi possível ler settings.json; usando o padrão.")

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except OSError:
            log.exception("Não foi possível salvar settings.json")

    def get(self, key):
        return self.data[key]

    def set(self, key, value):
        self.data[key] = value
