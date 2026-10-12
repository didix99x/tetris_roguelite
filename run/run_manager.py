"""
run/run_manager.py - controla UMA RUN (do andar 1 até a vitória ou morte).

Tudo que existe só durante a run (HP atual, bônus de recompensas, andar)
fica aqui. Ao morrer, este objeto é descartado e os bônus se perdem.
O que é PERMANENTE fica em game/save.py.
"""
import random

from characters import create_character
from combat.combat import Combat
from rewards.reward_pool import roll_rewards
from game import shop as shop_logic
from run.floor import build_floor, build_infinite_floor, build_special_boss


class RunManager:
    def __init__(self, char_id, data, rng=None, mode="story", unlocked_characters=None, upgrades=None,
                 blocked_cards=None, boss_misses=None):
        self.data = data
        self.rng = rng or random.Random()
        # upgrades permanentes (Loja): {"vida": n, "dano": n, "defesa": n, "passiva": n}. Sem upgrades = personagem idêntico.
        self.upgrades = dict(upgrades or {})
        self.blocked_cards = set(blocked_cards or ())         # cartas da Loja não compradas / exclusivas de outro personagem
        shop = data.get("shop")
        char_data = shop_logic.upgraded_character_data(shop, data["characters"], char_id, self.upgrades) \
            if shop and self.upgrades else data["characters"][char_id]
        self.player = create_character(char_id, char_data)
        if shop and self.upgrades:
            shop_logic.apply_upgrade_mods(shop, self.player, self.upgrades)
        self.floor_number = 1
        # personagens ainda bloqueados (só importa no Modo Infinito: eles podem aparecer como inimigos)
        self.unlocked_characters = list(unlocked_characters) if unlocked_characters is not None else None
        # histórico de aparição dos chefes de desbloqueio {personagem: andares elegíveis sem aparecer}; o Game passa o do save
        self.boss_misses = boss_misses if boss_misses is not None else {}
        self.special_active = False           # True durante o combate do Boss especial
        self.super_state = {"cycle": [], "by_floor": {}}   # rodízio dos personagens como SUPER CHEFES (andar 110+)
        self.void_fury_shown = set()          # marcos (100, 200...) cuja tela da Fúria do Vazio já foi mostrada nesta run
        self.mode = mode                      # "story" (história) ou "infinite" (modo infinito)
        self.last_floor = None if mode == "infinite" else data["floors"]["last_floor"]
        self.floor = None
        self.taken_rewards = []
        self.finished = False
        self.active_synergies = []            # ids das sinergias já ativas nesta run
        self.new_synergies = []               # nomes recém-ativados (a tela de batalha mostra e limpa)
        self.swaps_used = 0                   # trocas de carta usadas (limite por run: data/shop.json > events)

    def start_floor(self):
        """Cria o inimigo do andar atual e devolve a Batalha."""
        if self.mode == "infinite":
            extra = dict(own_character=self.player.char_id, characters_data=self.data["characters"],
                         locked_characters=self.locked_characters(), player=self.player,
                         base_max_hp=self.data["characters"][self.player.char_id]["max_hp"], boss_misses=self.boss_misses)
            if not self.special_active:
                extra["super_state"] = self.super_state
            builder = build_special_boss if self.special_active else build_infinite_floor
            self.floor = builder(self.floor_number, self.data["enemies"], self.data["floors"], self.rng, **extra)
        else:
            self.floor = build_floor(self.floor_number, self.data["enemies"],
                                     self.data["floors"], self.rng)
        return Combat(self.player, self.floor.enemy, self.floor_number, self.rng)

    def locked_characters(self):
        """Ids dos personagens que o jogador ainda não desbloqueou."""
        if self.unlocked_characters is None:
            return []
        return [c for c in self.data["characters"] if c not in self.unlocked_characters]

    def floor_cleared(self):
        """Chamado quando o inimigo morre: cura um pouco e vê se a run acabou."""
        pct = self.data["floors"].get("heal_after_floor_pct", 0.25) + self.player.mods["floor_heal_pct"]
        self.player.heal(self.player.max_hp * pct)
        self.finished = self.last_floor is not None and self.floor_number >= self.last_floor

    def roll_rewards(self, only_rarity=None, count=3):
        return roll_rewards(self.data["rewards"], count, self.floor_number, self.rng, only_rarity=only_rarity,
                            blocked_ids=self.blocked_cards)

    def take_reward(self, reward):
        self.player.apply_reward(reward)
        self.taken_rewards.append(reward)
        self._check_synergies()

    def _check_synergies(self):
        """Sinergias (data/rewards.json > synergies): quando o jogador tem TODAS as cartas do conjunto, ganha o bônus extra."""
        have = {r["id"] for r in self.taken_rewards}
        for syn in self.data["rewards"].get("synergies", []):
            if syn["id"] not in self.active_synergies and all(c in have for c in syn["cards"]):
                self.active_synergies.append(syn["id"])
                self.player.apply_reward({"effects": syn["effects"]})
                self.player.synergies.append(syn["name"])
                self.new_synergies.append(syn["name"])
    def advance_floor(self):
        self.floor_number += 1
