"""characters/mage.py - MAGO (estilo: manipulação de cores)."""
from characters.character import Player
from combat import effects


class Mage(Player):
    def energy_bonus(self, match_lengths):
        # PASSIVA: matches grandes geram energia extra.
        per_block = self.passive_params.get("energy_per_extra_block", 8)
        return sum(max(0, n - 3) * per_block for n in match_lengths)

    def use_ability(self, combat):
        # HABILIDADE Alquimia: pinta blocos com a cor dominante e
        # deixa o puzzle resolver os matches (e chains) que surgirem.
        cells = effects.recolor_to_dominant(combat.board, self.ability_params.get("blocks", 6))
        combat.emit("burst", cells=cells)
        combat.start_resolve("player")
