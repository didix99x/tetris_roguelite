"""characters/archer.py - ROMULO, o ARQUEIRO (precisão, dano consistente, combos)."""
from characters.character import Player


class Archer(Player):
    def __init__(self, char_id, data):
        super().__init__(char_id, data)
        # PASSIVA Olhos de Águia (parte 1): chance de crítico (mesmo bônus das cartas de crítico).
        self.mods["crit_chance"] += self.passive_params.get("crit_chance", 0.10)

    def on_match(self, combat, level, match_lengths):
        # PASSIVA Olhos de Águia (parte 2): chains x3+ devolvem energia.
        if level >= 3:
            self.add_energy(self.passive_params.get("chain3_energy", 8))

    def use_ability(self, combat):
        # HABILIDADE Chuva de Flechas: várias flechas de dano fixo.
        total = self.ability_params.get("arrows", 5) * self.ability_params.get("damage_each", 9)
        combat.deal_damage_to_enemy(total, label=self.ability_name)
