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
<<<<<<< HEAD
    "screen_shake": True,            # tremor de tela ligado/desligado (Opções)
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
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
<<<<<<< HEAD
        "tab_prev": ["pageup"],       # trocar de aba/página nos menus (no controle: LB / L1)
        "tab_next": ["pagedown"],     # (no controle: RB / R1)
    },
    # Controle (Xbox/PlayStation/compatíveis): número do botão -> ação. D-pad e analógico esquerdo movem sozinhos.
    # Xbox: A=0 B=1 X=2 Y=3 | PlayStation: X(cruz)=0 O(bola)=1 Quadrado=2 Triângulo=3 | 6 e 7 = Select/Start/Options (pausa/voltar)
    # Remapeável em Opções > CONTROLE / JOYSTICK. "up/down/left/right": botões EXTRAS (o D-pad e o analógico sempre funcionam).
    # "tab_prev"/"tab_next": None = padrão do tipo de controle (Xbox LB/RB, PlayStation L1/R1); uma lista = botões escolhidos.
    "gamepad": {
        "swap": [0],
        "back": [1, 6, 7],
        "ability": [2, 3],
        "up": [],
        "down": [],
        "left": [],
        "right": [],
        "tab_prev": None,
        "tab_next": None,
        "deadzone": 0.55,
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
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
<<<<<<< HEAD
                if key in ("controls", "gamepad") and isinstance(value, dict):
                    self.data[key].update(value)           # chaves que faltam (save antigo) ficam com o padrão
=======
                if key == "controls" and isinstance(value, dict):
                    self.data["controls"].update(value)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
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
