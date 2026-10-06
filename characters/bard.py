"""characters/bard.py - BARDO (estilo: suporte / ritmo)."""
from characters.character import Player
from combat import effects


class Bard(Player):
    def on_match(self, combat, level, match_lengths):
        # PASSIVA Melodia Curativa: cada rodada de match recupera vida (mais em chains).
        amount = (self.passive_params.get("heal_per_match", 2)
                  + self.passive_params.get("heal_per_chain_level", 1) * max(0, level - 1))
        before = self.hp
        self.heal(amount)
        healed = self.hp - before
        if healed >= 0.5:
            combat.emit("heal", amount=int(round(healed)))

    def use_ability(self, combat):
        # HABILIDADE Canção Purificadora: limpa teias e pedras e atrasa o inimigo.
        cells = effects.cleanse_board(combat.board)
        combat.emit("burst", cells=cells)
        delay = self.ability_params.get("delay", 5.0)
        combat.enemy_timer += delay
        combat.enemy_cooldown_total = max(combat.enemy_cooldown_total, combat.enemy_timer)
        combat.start_resolve("player")
