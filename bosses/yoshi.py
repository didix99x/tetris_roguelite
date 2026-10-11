"""
bosses/yoshi.py - YOSHI, O REI DO TETRIS (boss supremo do andar 100 do Modo Infinito).

Ele recebe uma COMBINAÇÃO das passivas de TODOS os inimigos do jogo, calculada na hora a partir de
data/enemies.json (as passivas originais dos inimigos NÃO são alteradas; nada é copiado para o arquivo):
  - armor, match3_reduction, chain1_reduction   -> o MAIOR valor encontrado (chain1 vira 'chain_armor' do Boss)
  - enrage_hp / hp_threshold                    -> o MAIOR limite de vida;   enrage_factor / cooldown_factor -> o MENOR fator
  - extra_web_time                              -> o MAIOR tempo extra (somado às teias dele)
  - regen_pct, attack_heal_pct                  -> o MAIOR valor
Se criar um inimigo novo com uma dessas passivas, o Yoshi já herda automaticamente.
"""
from bosses.boss import Boss

# passivas que o Yoshi sabe combinar (um teste confere que TODAS as chaves usadas pelos inimigos estão aqui)
SUPPORTED_PASSIVES = {"armor", "match3_reduction", "chain1_reduction", "enrage_hp", "enrage_factor", "hp_threshold",
                      "cooldown_factor", "extra_web_time", "regen_pct", "attack_heal_pct"}
# o Goblin usa estes valores quando o JSON não os define (enemies/goblin.py)
_CLASS_DEFAULTS = {"goblin": {"hp_threshold": 0.5, "cooldown_factor": 0.75}}


def merge_enemy_passives(enemies):
    """Devolve as passivas combinadas de todos os inimigos de data/enemies.json > enemies."""
    best = {"armor": 0.0, "match3_reduction": 0.0, "chain1_reduction": 0.0, "extra_web_time": 0.0, "regen_pct": 0.0,
            "attack_heal_pct": 0.0}
    thresholds, factors = [], []
    for enemy_id, data in enemies.items():
        params = dict(_CLASS_DEFAULTS.get(enemy_id, {}))
        params.update(data.get("passive_params", {}))
        for key in best:
            best[key] = max(best[key], float(params.get(key, 0.0)))
        for limit_key, factor_key in (("enrage_hp", "enrage_factor"), ("hp_threshold", "cooldown_factor")):
            if limit_key in params:
                thresholds.append(float(params[limit_key]))
                factors.append(float(params.get(factor_key, 0.75)))
    merged = {k: v for k, v in best.items() if v > 0}
    if thresholds:
        merged["enrage_hp"], merged["enrage_factor"] = max(thresholds), min(factors)
    return merged


class YoshiBoss(Boss):
    def __init__(self, boss_id, data, stats, enemies_data):
        super().__init__(boss_id, data, stats)
        merged = merge_enemy_passives(enemies_data["enemies"])
        # data > yoshi > infinite > passive_scale: reduz só as passivas de CURA (a vida do Yoshi é enorme; sem isso ele seria imbatível)
        for key, factor in data.get("passive_scale", {}).items():
            if key in merged:
                merged[key] *= float(factor)
        self.merged_passives = merged
        own = dict(self.mechanics)
        mech = dict(own)
        for key in ("armor", "match3_reduction", "regen_pct", "attack_heal_pct"):
            if key in merged:
                mech[key] = max(own.get(key, 0.0), merged[key])
        if "chain1_reduction" in merged:                       # no Boss, "chains x1 reduzidos" se chama chain_armor
            mech["chain_armor"] = max(own.get("chain_armor", 0.0), merged["chain1_reduction"])
        if "enrage_hp" in merged:
            mech["enrage_hp"] = max(own.get("enrage_hp", 0.0), merged["enrage_hp"])
            mech["enrage_factor"] = min(own.get("enrage_factor", 1.0), merged["enrage_factor"])
        self.mechanics = mech
        extra = merged.get("extra_web_time", 0.0)              # passiva da Aranha: teias duram mais
        for ability in self.abilities:
            if ability["type"] == "web":
                ability["duration"] = ability.get("duration", 8.0) + extra
