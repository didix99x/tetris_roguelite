"""enemies/goblin.py - GOBLIN. Habilidade: Break (destrói blocos)."""
from enemies.enemy import Enemy


class Goblin(Enemy):
    def cooldown_factor(self):
        # PASSIVA Frenesi: com pouca vida, ataca mais rápido.
        if self.hp_fraction() < self.passive_params.get("hp_threshold", 0.5):
            return self.passive_params.get("cooldown_factor", 0.75)
        return 1.0
