"""enemies/golem.py - GOLEM. Habilidade: Weight (aumenta a pressão)."""
from enemies.enemy import Enemy


class Golem(Enemy):
    def modify_incoming(self, amount, chain_level, biggest_match):
        # PASSIVA Pele de Pedra: matches de 3 blocos causam menos dano.
        if biggest_match <= 3:
            return int(round(amount * (1.0 - self.passive_params.get("match3_reduction", 0.3))))
        return amount
