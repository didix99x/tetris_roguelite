"""characters/cleric.py - MAIZONA, a CLÉRIGA (cura, sobrevivência, proteção)."""
from characters.character import Player
from combat import effects


class Cleric(Player):
    def __init__(self, char_id, data):
        super().__init__(char_id, data)
        # PASSIVA Bênção Constante: regeneração (usa o mesmo bônus das cartas de regeneração).
        self.mods["regen_per_sec"] += self.passive_params.get("regen_per_sec", 0.8)

    def use_ability(self, combat):
        # HABILIDADE Luz Divina: cura e limpa veneno, teias e pedras.
        before = self.hp
        self.heal(self.max_hp * self.ability_params.get("heal_pct", 0.25))
        healed = int(round(self.hp - before))
        if healed > 0:
            combat.emit("heal", amount=healed)
        combat.poison_time = 0.0
        combat.silence_time = 0.0
        cells = effects.cleanse_board(combat.board)
        combat.emit("burst", cells=cells)
        combat.start_resolve("player")
