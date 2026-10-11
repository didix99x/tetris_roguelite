"""characters/assassin.py - ASSASSINO (estilo: velocidade)."""
from characters.character import Player


class Assassin(Player):
    def damage_multiplier(self, chain_level, quick):
        # PASSIVA Ritmo Letal: matches feitos logo depois do anterior dão bônus.
        if quick:
            return 1.0 + self.passive_params.get("quick_bonus", 0.30)
        return 1.0

    def use_ability(self, combat):
        # HABILIDADE Execução: mata inimigo com pouca vida; senão causa dano.
        enemy = combat.enemy
        params = self.ability_params
        low = enemy.hp <= enemy.max_hp * params.get("execute_threshold", 0.30)
        if low and not enemy.is_boss:
            amount = enemy.hp
        elif low and enemy.is_boss:
            amount = enemy.max_hp * params.get("boss_damage_pct", 0.15)
        else:
            amount = params.get("damage", 30)
        combat.deal_damage_to_enemy(amount, label=self.ability_name)
