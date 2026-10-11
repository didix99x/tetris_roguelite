"""enemies/mage_enemy.py - MAGO inimigo. Habilidade: Curse (blocos viram pedra)."""
from enemies.enemy import Enemy


class MageEnemy(Enemy):
    def modify_incoming(self, amount, chain_level, biggest_match):
        # PASSIVA Barreira Arcana: chains x1 causam menos dano.
        if chain_level < 2:
            return int(round(amount * (1.0 - self.passive_params.get("chain1_reduction", 0.2))))
        return amount
