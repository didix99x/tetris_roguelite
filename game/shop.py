"""
game/shop.py - LÓGICA da Loja, dos upgrades e dos pontos permanentes (sem pygame).

A interface (ui/shop_screen.py) e o gameplay (run/run_manager.py) usam AS MESMAS funções daqui,
então o que a tela mostra é exatamente o que o jogo aplica.
Todos os números vêm de data/shop.json (e os valores-base dos personagens, de data/characters.json).
"""
import copy
import math

ATTRIBUTES = ("vida", "dano", "defesa", "passiva")


# ---------------------------------------------------------------- pontos
def award_points(progress, amount):
    amount = int(amount)
    if amount > 0:
        progress.points += amount
    return max(0, amount)


def scaled_points(shop, amount):
    """Aplica o multiplicador de pontos (data/shop.json > points > multiplier) uma única vez, arredondando ao inteiro mais próximo."""
    return int(round(amount * float(shop["points"].get("multiplier", 1.0))))


def points_for_floor(shop, mode, floor_number, is_boss, is_super=False, victory=False):
    """Pontos por concluir um andar. Devolve (pontos, [textos])."""
    cfg = shop["points"]
    total = cfg["floor_clear_infinite"] if mode == "infinite" else cfg["floor_clear"]
    notes = []
    if is_boss:
        total += cfg["super_boss_defeat"] if is_super else cfg["boss_defeat"]
    if victory:
        total += cfg["story_victory"]
        notes.append("VITÓRIA")
    return scaled_points(shop, total), notes


def claim_milestone(progress, shop, mode, floor_number):
    """Marco de andar (uma vez só). Devolve os pontos ganhos (0 se não há marco novo)."""
    table = shop["points"]["milestones"].get(mode, {})
    key = f"{mode}:{floor_number}"
    if str(floor_number) in table and key not in progress.claimed_milestones:
        progress.claimed_milestones.append(key)
        return award_points(progress, scaled_points(shop, table[str(floor_number)]))
    return 0


# ---------------------------------------------------------------- cartas da Loja
def shop_cards(rewards_data):
    """Cartas que só entram nas runs depois de compradas (campo "shop": true em data/rewards.json)."""
    return [r for r in rewards_data["rewards"] if r.get("shop")]


def card_cost(shop, card):
    base = card.get("cost", shop["card_costs"][card["rarity"]])
    return int(round(base * float(shop.get("card_price_multiplier", 1.0))))      # preço base x multiplicador (uma vez só)


def card_state(progress, card):
    """BLOQUEADA (faltam pontos) / DISPONIVEL (dá para comprar) / DESBLOQUEADA."""
    if card["id"] in progress.purchased_cards:
        return "DESBLOQUEADA"
    return "BLOQUEADA"


def can_buy_card(progress, shop, card):
    if card["id"] in progress.purchased_cards:
        return False, "JÁ DESBLOQUEADA"
    if progress.points < card_cost(shop, card):
        return False, "PONTOS INSUFICIENTES"
    return True, ""


def card_display_state(progress, shop, card):
    """Estado mostrado na Loja: BLOQUEADA, DISPONÍVEL (tem pontos) ou DESBLOQUEADA."""
    if card["id"] in progress.purchased_cards:
        return "DESBLOQUEADA"
    return "DISPONÍVEL" if progress.points >= card_cost(shop, card) else "BLOQUEADA"


def buy_card(progress, shop, card):
    """Compra: verifica pontos, desconta, desbloqueia para sempre e salva na hora. Devolve (ok, mensagem)."""
    ok, why = can_buy_card(progress, shop, card)
    if not ok:
        return False, why
    progress.points -= card_cost(shop, card)
    progress.purchased_cards.append(card["id"])
    progress.save()
    return True, "CARTA DESBLOQUEADA"


def blocked_card_ids(progress, rewards_data, char_id):
    """Cartas que NÃO podem sair nas recompensas desta run: da Loja ainda não compradas e exclusivas de outro personagem."""
    blocked = set()
    for r in rewards_data["rewards"]:
        if r.get("shop") and r["id"] not in progress.purchased_cards:
            blocked.add(r["id"])
        if r.get("character") and r["character"] != char_id:
            blocked.add(r["id"])
    return blocked


# ---------------------------------------------------------------- upgrades
def level_of(progress, char_id, attr):
    return int(progress.upgrades.get(char_id, {}).get(attr, 0))


def max_level(shop):
    return int(shop["upgrades"]["max_level"])


def upgrade_cost(shop, attr, level):
    """Custo para subir DO nível `level` para `level + 1` (None se já está no máximo)."""
    if level >= max_level(shop):
        return None
    base = shop["upgrades"]["cost_table"][level]
    return int(round(base * shop["upgrades"]["attributes"][attr].get("cost_mult", 1.0)))


def _passive_rule(shop, char_id):
    return shop["upgrades"]["passive"][char_id]


def upgrade_value(shop, characters, char_id, attr, level):
    """Valor REAL do atributo no nível `level` (o mesmo usado no jogo)."""
    cfg = shop["upgrades"]["attributes"][attr]
    if attr == "vida":
        return characters[char_id]["max_hp"] + cfg["per_level"] * level
    if attr in ("dano", "defesa"):
        return cfg["per_level"] * level
    rule = _passive_rule(shop, char_id)
    base = characters[char_id]["passive_params"][rule["param"]]
    return base + rule["per_level"] * level


def format_value(shop, char_id, attr, value):
    """Texto do valor (ex.: '+12%', '105 HP')."""
    if attr == "vida":
        return f"{round(value)} HP"
    if attr in ("dano", "defesa"):
        return f"+{round(value * 100)}%" if attr == "dano" else f"{round(value * 100)}%"
    fmt = _passive_rule(shop, char_id)["fmt"]
    if fmt == "pct":
        return f"{round(value * 100, 1):g}%"
    if fmt == "hp":
        return f"{round(value, 1):g} HP"
    if fmt == "hps":
        return f"{round(value, 2):g} HP/s"
    return f"{round(value, 1):g}"


def upgrade_info(progress, shop, characters, char_id, attr):
    """Tudo que a tela precisa de um upgrade: nível, valores atual/próximo, aumento e custo."""
    level = level_of(progress, char_id, attr)
    top = max_level(shop)
    cur = upgrade_value(shop, characters, char_id, attr, level)
    nxt = upgrade_value(shop, characters, char_id, attr, min(top, level + 1))
    inc = nxt - cur
    if attr == "vida":
        inc_text = f"+{round(inc)} HP"
    elif attr in ("dano", "defesa"):
        inc_text = f"+{round(inc * 100)}%"
    else:
        rule = _passive_rule(shop, char_id)
        unit = {"pct": "%", "hp": " HP", "hps": " HP/s", "en": ""}[rule["fmt"]]
        scale = 100 if rule["fmt"] == "pct" else 1
        inc_text = f"+{round(inc * scale, 2):g}{unit}"
    return {"attr": attr, "level": level, "max": top, "at_max": level >= top,
            "current": format_value(shop, char_id, attr, cur), "next": format_value(shop, char_id, attr, nxt),
            "increase": inc_text, "cost": upgrade_cost(shop, attr, level),
            "label": shop["upgrades"]["attributes"][attr]["label"], "text": shop["upgrades"]["attributes"][attr]["text"],
            "what": _passive_rule(shop, char_id)["what"] if attr == "passiva" else None}


def can_upgrade(progress, shop, characters, char_id, attr):
    if char_id not in characters or not progress.is_unlocked(char_id):
        return False, "DESBLOQUEIE ESTE PERSONAGEM PARA LIBERAR OS UPGRADES."
    info = upgrade_info(progress, shop, characters, char_id, attr)
    if info["at_max"]:
        return False, "MÁXIMO"
    if progress.points < info["cost"]:
        return False, "PONTOS INSUFICIENTES"
    return True, ""


def buy_upgrade(progress, shop, characters, char_id, attr):
    ok, why = can_upgrade(progress, shop, characters, char_id, attr)
    if not ok:
        return False, why
    info = upgrade_info(progress, shop, characters, char_id, attr)
    progress.points -= info["cost"]
    progress.upgrades.setdefault(char_id, {})[attr] = info["level"] + 1
    progress.save()
    return True, "UPGRADE COMPRADO"


# ---------------------------------------------------------------- aplicação no gameplay
def upgraded_character_data(shop, characters, char_id, levels):
    """Cópia dos dados do personagem com VIDA e PASSIVA melhoradas (a passiva é lida no __init__ de alguns personagens).
    Com todos os níveis em 0 devolve dados idênticos aos originais."""
    data = copy.deepcopy(characters[char_id])
    levels = levels or {}
    data["max_hp"] = int(upgrade_value(shop, characters, char_id, "vida", levels.get("vida", 0)))
    rule = _passive_rule(shop, char_id)
    data["passive_params"][rule["param"]] = upgrade_value(shop, characters, char_id, "passiva", levels.get("passiva", 0))
    return data


def apply_upgrade_mods(shop, player, levels):
    """DANO e DEFESA entram nos bônus que o combate já usa (damage_pct e damage_reduction_pct)."""
    levels = levels or {}
    attrs = shop["upgrades"]["attributes"]
    player.mods["damage_pct"] += attrs["dano"]["per_level"] * levels.get("dano", 0)
    player.mods["damage_reduction_pct"] += attrs["defesa"]["per_level"] * levels.get("defesa", 0)
