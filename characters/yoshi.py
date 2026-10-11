"""characters/yoshi.py - YOSHI (samurai, estilo: disciplina). Desbloqueado ao derrotar o Yoshi do andar 100 do Infinito."""
from characters.character import Player


class Yoshi(Player):
    def damage_multiplier(self, chain_level, quick):
        # PASSIVA Desembainhar: matches feitos SEM pressa (fora da janela de "jogada rápida") causam mais dano.
        if not quick:
            return 1.0 + self.passive_params.get("unhurried_bonus", 0.30)
        return 1.0

    def use_ability(self, combat):
        # HABILIDADE Iai Relâmpago: corte rápido (mais forte contra bosses) e recupera um pouco de vida.
        params = self.ability_params
        amount = params.get("damage", 42)
        if combat.enemy.is_boss:
            amount *= 1.0 + params.get("boss_bonus_pct", 0.25)
        combat.deal_damage_to_enemy(amount, label=self.ability_name)
        self.heal(params.get("heal", 6))
