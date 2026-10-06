"""enemies/spider.py - ARANHA. Habilidade: Web (prende blocos)."""
from enemies.enemy import Enemy


class Spider(Enemy):
    def __init__(self, enemy_id, data, stats):
        super().__init__(enemy_id, data, stats)
        # PASSIVA Teia Grossa: as teias duram mais.
        extra = self.passive_params.get("extra_web_time", 0)
        for ability in self.abilities:
            if ability["type"] == "web":
                ability["duration"] = ability.get("duration", 8.0) + extra
