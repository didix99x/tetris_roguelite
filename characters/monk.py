"""characters/monk.py - YUKO, o MONGE (velocidade, combos, energia, sequências)."""
from characters.character import Player


class Monk(Player):
    def on_match(self, combat, level, match_lengths):
        # PASSIVA Chi em Fluxo: cada nível de chain acima de x1 gera energia extra.
        if level >= 2:
            self.add_energy((level - 1) * self.passive_params.get("energy_per_chain_level", 5))

    def use_ability(self, combat):
        # HABILIDADE Palma Ressonante: dano cresce com a MAIOR chain feita na batalha.
        params = self.ability_params
        levels = min(combat.chain.best, params.get("max_chain_levels", 5))
        damage = params.get("base_damage", 20) + params.get("damage_per_chain_level", 10) * levels
        combat.deal_damage_to_enemy(damage, label=self.ability_name)
