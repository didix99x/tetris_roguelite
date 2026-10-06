"""
game/save.py - PROGRESSO PERMANENTE (separado da run).

Guarda: melhor andar, personagens desbloqueados, recompensas descobertas,
quantidade de runs/vitórias. A run em andamento NÃO é salva aqui.
"""
import json
import logging

import config

from paths import user_data_dir

log = logging.getLogger(__name__)

SAVE_VERSION = 2   # 2 = personagens passam a ser desbloqueados derrotando-os no Modo Infinito


class Progress:
    def __init__(self, characters_data):
        self.characters_data = characters_data
        self.path = user_data_dir() / "progress.json"
        self.best_floor = 0
        self.runs = 0
        self.wins = 0
        self.discovered_rewards = []
        self.unlocked = []
        self.infinite_unlocked = False
        self.best_infinite_floor = 0
        self.load()
        self.update_unlocks()

    def load(self):
        if not self.path.exists():
            return
        try:
            with open(self.path, encoding="utf-8") as f:
                data = json.load(f)
            self.best_floor = int(data.get("best_floor", 0))
            self.runs = int(data.get("runs", 0))
            self.wins = int(data.get("wins", 0))
            self.discovered_rewards = list(data.get("discovered_rewards", []))
            self.unlocked = list(data.get("unlocked", []))
            if int(data.get("save_version", 1)) < SAVE_VERSION:
                # Save antigo: os personagens eram liberados automaticamente (não foram conquistados).
                # Volta só os liberados por padrão; o restante agora se conquista no Modo Infinito.
                self.unlocked = []
            # quem já zerou o jogo antes desta versão também ganha o modo infinito
            self.infinite_unlocked = bool(data.get("infinite_unlocked", self.wins > 0))
            self.best_infinite_floor = int(data.get("best_infinite_floor", 0))
        except (OSError, ValueError):
            log.exception("Não foi possível ler progress.json; começando do zero.")

    def save(self):
        data = {
            "best_floor": self.best_floor,
            "runs": self.runs,
            "wins": self.wins,
            "discovered_rewards": self.discovered_rewards,
            "unlocked": self.unlocked,
            "save_version": SAVE_VERSION,
            "infinite_unlocked": self.infinite_unlocked,
            "best_infinite_floor": self.best_infinite_floor,
        }
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except OSError:
            log.exception("Não foi possível salvar progress.json")

    def update_unlocks(self):
        """Libera os personagens "default" (e, em dados antigos, os de 'unlock_floor' alcançado).
        Personagens "defeat_in_infinite" só são liberados por unlock_character()."""
        for char_id, data in self.characters_data.items():
            if char_id in self.unlocked:
                continue
            rule = data.get("unlock")
            if rule == "default" or (rule is None and data.get("unlock_floor", 0) <= self.best_floor):
                self.unlocked.append(char_id)

    def is_infinite_unlocked(self):
        return self.infinite_unlocked or config.DEBUG_UNLOCK_INFINITE

    def unlock_infinite(self):
        """Libera o Modo Infinito. Devolve True se foi a PRIMEIRA vez."""
        first_time = not self.infinite_unlocked
        self.infinite_unlocked = True
        return first_time

    def record_infinite_floor(self, floor_number):
        if floor_number > self.best_infinite_floor:
            self.best_infinite_floor = floor_number

    def unlock_character(self, char_id):
        """Desbloqueia um personagem PARA SEMPRE. Devolve True se era novo (precisa chamar save())."""
        if char_id in self.unlocked or char_id not in self.characters_data:
            return False
        self.unlocked.append(char_id)
        return True

    def is_unlocked(self, char_id):
        return char_id in self.unlocked

    def record_floor(self, floor_number):
        if floor_number > self.best_floor:
            self.best_floor = floor_number
            self.update_unlocks()

    def discover(self, reward_id):
        if reward_id not in self.discovered_rewards:
            self.discovered_rewards.append(reward_id)
