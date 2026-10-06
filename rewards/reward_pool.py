"""
rewards/reward_pool.py - SORTEIA as 3 recompensas oferecidas.

Quanto maior o "weight" da raridade (data/rewards.json), mais comum ela é.
Cada recompensa pode ter "min_floor": só aparece a partir desse andar.
"""
import random


def roll_rewards(rewards_data, count, floor_number, rng=None, only_rarity=None):
    """only_rarity (ex.: "legendary") oferece SOMENTE cartas dessa raridade (usado pelo Boss especial)."""
    rng = rng or random.Random()
    weights = rewards_data["rarity_weights"]
    pool = [r for r in rewards_data["rewards"] if r.get("min_floor", 1) <= floor_number]
    if only_rarity:
        pool = [r for r in pool if r["rarity"] == only_rarity] or \
               [r for r in rewards_data["rewards"] if r["rarity"] == only_rarity]
    picks = []
    for _ in range(count):
        if not pool:
            break
        chosen = rng.choices(pool, weights=[weights[r["rarity"]] for r in pool], k=1)[0]
        picks.append(chosen)
        pool = [r for r in pool if r["id"] != chosen["id"]]
    return picks
