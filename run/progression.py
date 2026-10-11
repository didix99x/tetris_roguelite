"""
run/progression.py - como os inimigos ficam mais fortes a cada andar.
Os números ficam em data/floors.json (seção "scaling").
"""
from combat import damage


def scale_stats(enemy_data, floor_number, scaling):
    steps = floor_number - 1
    hp = enemy_data["hp"] * (1.0 + scaling["hp_per_floor"] * steps)
    damage = enemy_data["damage"] * (1.0 + scaling["damage_per_floor"] * steps)
    factor = max(scaling["min_cooldown_factor"], 1.0 + scaling["cooldown_per_floor"] * steps)
    cooldown = enemy_data["cooldown"] * factor
    bonus = (steps // 10) * scaling.get("ability_amount_per_10_floors", 0)
    return {
        "hp": int(round(hp)),
        "damage": max(1, int(round(damage))),
        "cooldown": cooldown,
        "ability_bonus": bonus,
    }


# ======================================================================
# MODO INFINITO: o escalonamento considera o ANDAR e a FORÇA DO JOGADOR.
# Os números ficam em data/floors.json > infinite > scaling.
# ======================================================================
def _curve(steps, rate, knee_steps, tail_rate, cap):
    """Cresce linear até o 'joelho' (igual ao modo normal) e, depois, mais devagar. Nunca passa de cap."""
    full = min(steps, knee_steps) * rate + max(0, steps - knee_steps) * rate * tail_rate
    return min(cap, 1.0 + full)


def player_power(player, base_max_hp, floor_number=1, is_boss=False):
    """Mede a força do jogador usando só os atributos que ele já tem (mods das cartas, vida máx.).

    Devolve {"offense", "defense", "power"}; 1.0 = personagem sem nenhuma carta.
      offense: dano, crítico, chain, explosões, habilidades, energia e condicionais.
      defense: vida máxima, defesa, esquiva, vampirismo, regeneração, cura e resistências.
      power:   média geométrica das duas (usada para cadência e habilidades dos inimigos).
    """
    m = player.mods
    g = lambda key: float(m.get(key, 0.0))
    crit = 1.0 + min(1.0, g("crit_chance")) * (damage.CRIT_BASE_MULTIPLIER - 1.0 + g("crit_damage_pct"))
    floor_bonus = min(damage.FLOOR_DAMAGE_CAP, g("floor_damage_pct") * floor_number)
    conditional = (0.5 * g("big_match_damage_pct") + 0.5 * g("quick_damage_pct") + 0.3 * g("execute_damage_pct")
                   + 0.4 * g("opener_damage_pct") + 0.5 * g("momentum_pct") * damage.MOMENTUM_MAX_STACKS
                   + 0.3 * g("low_hp_damage_pct") + (g("boss_damage_pct") if is_boss else 0.0))
    skills = 0.3 * (g("ability_power_pct") + g("energy_gain_pct") - g("ability_cost_pct")
                    + 0.01 * g("chain_energy") + 0.01 * g("crit_energy") + g("ability_refund_pct"))
    offense = ((1.0 + g("damage_pct") + floor_bonus + conditional) * (1.0 + 0.5 * g("chain_damage_pct")) * crit
               * (1.0 + 0.03 * g("explosion_match5") + 0.04 * g("explosion_chain")) * (1.0 + 0.12 * g("chain_start"))
               * (1.0 + skills) * (1.0 + 0.3 * min(damage.MAX_THORNS, g("thorns_pct"))))
    reduction = max(-0.5, min(damage.MAX_DAMAGE_REDUCTION, g("damage_reduction_pct")))
    sustain = (3.0 * g("lifesteal_pct") + 0.05 * g("regen_per_sec") + 0.002 * g("chain3_heal") + 0.5 * g("floor_heal_pct")
               + 0.5 * g("enemy_cooldown_pct") + 0.5 * (g("boss_cooldown_pct") if is_boss else 0.0)
               + 0.01 * (g("match_heal") + g("crit_heal") + g("ability_heal")) + 0.15 * (1 if g("second_wind_pct") > 0 else 0)
               + 0.15 * min(damage.MAX_STATUS_RESIST, g("status_resist_pct")))
    defense = ((player.max_hp / max(1.0, float(base_max_hp))) / (1.0 - reduction)
               / (1.0 - min(damage.MAX_BLOCK_CHANCE, g("block_chance"))) * (1.0 + sustain))
    offense, defense = max(0.25, offense), max(0.25, defense)
    return {"offense": offense, "defense": defense, "power": (offense * defense) ** 0.5}


def scale_stats_infinite(enemy_data, floor_number, scaling, infinite_settings=None, power=None):
    """Como scale_stats, mas para o Modo Infinito:
      1) o crescimento por andar é IGUAL ao modo normal até `knee_floor` e depois fica mais lento (`tail_rate`),
         com tetos para vida (`hp_mult_cap`), dano (`damage_mult_cap`) e bônus de habilidade (`ability_bonus_cap`);
      2) com `power` (de player_power), o inimigo se adapta ao jogador, SEM virar esponja de vida:
         vida sobe com o ataque dele, dano sobe com a defesa dele, e inimigos fortes ainda atacam um pouco mais
         rápido e com habilidades mais fortes. Tudo com tetos; nunca fica mais fácil que só pelo andar."""
    cfg = (infinite_settings or {}).get("scaling")
    if not cfg:
        return scale_stats(enemy_data, floor_number, scaling)
    steps = floor_number - 1
    knee = max(0, int(cfg.get("knee_floor", 50)) - 1)
    tail = float(cfg.get("tail_rate", 0.35))
    hp_mult = _curve(steps, scaling["hp_per_floor"], knee, tail, float(cfg.get("hp_mult_cap", 12.0)))
    dmg_mult = _curve(steps, scaling["damage_per_floor"], knee, tail, float(cfg.get("damage_mult_cap", 6.0)))
    cooldown_factor = max(scaling["min_cooldown_factor"], 1.0 + scaling["cooldown_per_floor"] * steps)
    bonus = min(int(cfg.get("ability_bonus_cap", 6)), (steps // 10) * scaling.get("ability_amount_per_10_floors", 0))

    pcfg = cfg.get("player_power", {})
    if power and pcfg.get("enabled", True):
        hp_mult *= min(float(pcfg.get("hp_cap", 2.0)), max(1.0, 1.0 + float(pcfg.get("hp_per_offense", 0.6)) * (power["offense"] - 1.0)))
        dmg_mult *= min(float(pcfg.get("damage_cap", 1.6)), max(1.0, 1.0 + float(pcfg.get("damage_per_defense", 0.5)) * (power["defense"] - 1.0)))
        cooldown_factor *= min(1.0, max(float(pcfg.get("cooldown_floor", 0.85)), 1.0 - float(pcfg.get("cooldown_per_power", 0.06)) * (power["power"] - 1.0)))
        bonus += min(int(pcfg.get("ability_cap", 2)), max(0, int((power["power"] - 1.0) * float(pcfg.get("ability_per_power", 1.0)))))
    cooldown = max(enemy_data["cooldown"] * cooldown_factor,
                   min(float(cfg.get("min_cooldown_seconds", 2.5)), enemy_data["cooldown"]))
    return {
        "hp": int(round(enemy_data["hp"] * hp_mult)),
        "damage": max(1, int(round(enemy_data["damage"] * dmg_mult))),
        "cooldown": cooldown,
        "ability_bonus": bonus,
    }
