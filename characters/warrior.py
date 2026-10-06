"""characters/warrior.py - GUERREIRO (estilo: chains)."""
from characters.character import Player


class Warrior(Player):
    def damage_multiplier(self, chain_level, quick):
        # PASSIVA Fúria: cada nível de chain acima de 1 aumenta o dano.
        per_level = self.passive_params.get("chain_bonus_per_level", 0.15)
        return 1.0 + per_level * max(0, chain_level - 1)

    def use_ability(self, combat):
        # HABILIDADE Golpe Poderoso: dano direto no inimigo.
        combat.deal_damage_to_enemy(self.ability_params.get("damage", 45),
                                    label=self.ability_name)
