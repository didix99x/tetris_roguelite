"""
rewards/reward.py - utilidades para recompensas.

Uma recompensa é um dicionário vindo de data/rewards.json:
  id, name, description, rarity, effects: [{type, value}, ...]
"""
import config


def rarity_color(reward):
    return config.RARITY_COLORS.get(reward["rarity"], (200, 200, 200))


def rarity_name(reward):
    return config.RARITY_NAMES.get(reward["rarity"], reward["rarity"])
