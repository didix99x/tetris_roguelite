"""characters/judge.py - JUIZ (personagem inicial, equilibrado)."""
from characters.character import Player


class Judge(Player):
    def damage_multiplier(self, chain_level, quick):
        # PASSIVA Imparcialidade: bônus fixo de dano em todos os matches.
        return 1.0 + self.passive_params.get("damage_bonus", 0.10)

    def use_ability(self, combat):
        # HABILIDADE Martelo da Justiça: dano direto + atrasa o próximo ataque do inimigo.
        combat.deal_damage_to_enemy(self.ability_params.get("damage", 35), label=self.ability_name)
        combat.enemy_timer += self.ability_params.get("delay", 2.5)
        combat.enemy_cooldown_total = max(combat.enemy_cooldown_total, combat.enemy_timer)
