"""characters/blacksmith.py - CAIQUE, o FERREIRO (resistência, defesa, durabilidade)."""
from characters.character import Player


class Blacksmith(Player):
    def __init__(self, char_id, data):
        super().__init__(char_id, data)
        # PASSIVA Armadura Forjada: defesa fixa (usa o mesmo bônus das cartas de defesa).
        self.mods["damage_reduction_pct"] += self.passive_params.get("damage_reduction", 0.12)
        self.forge_stacks = 0

    def use_ability(self, combat):
        # HABILIDADE Forja Reforçada: cura um pouco e ganha defesa permanente (até o limite).
        params = self.ability_params
        if self.forge_stacks < params.get("max_stacks", 4):
            self.forge_stacks += 1
            self.mods["damage_reduction_pct"] += params.get("defense_gain", 0.06)
        before = self.hp
        self.heal(self.max_hp * params.get("heal_pct", 0.10))
        healed = int(round(self.hp - before))
        if healed > 0:
            combat.emit("heal", amount=healed)
