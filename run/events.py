"""
run/events.py - EVENTOS ENTRE ANDARES (sem pygame). Números em data/shop.json > events.

  DESCANSO         recupera vida (rest_heal_pct) OU energia (rest_energy)
  TROCA ARRISCADA  troca uma carta sua por outra: com chance de dar errado (swap_fail_chance). 1x por run (swap_max_per_run)
  SALA MISTERIOSA  situação aleatória (bênção, barganha, armadilha ou nada). Pesos em mystery_weights.

Tudo reutiliza o que já existe: cura do Player, take_reward (cartas) e o sorteio de recompensas. Não há ouro.
"""
RARITIES = ("common", "rare", "epic", "legendary")


def event_due(run, shop, rng):
    """Há evento depois deste andar? (a cada `every_floors` andares, nunca depois de boss nem no último andar)."""
    cfg = shop["events"]
    floor = run.floor_number
    if run.floor.is_boss or floor % cfg["every_floors"] != 0:
        return False
    if run.last_floor is not None and floor >= run.last_floor - 1:
        return False
    return rng.random() < cfg["chance"]


def pick_event(run, shop, rng):
    """Sorteia o tipo de evento. A troca só entra se ainda há troca disponível e o jogador tem cartas."""
    kinds = ["rest", "mystery"]
    if swap_available(run, shop):
        kinds.append("swap")
    return rng.choice(kinds)


def swap_available(run, shop):
    return run.swaps_used < shop["events"]["swap_max_per_run"] and any(not r.get("synergy") for r in run.taken_rewards)


# ---------------------------------------------------------------- descanso
def rest(run, shop, choice):
    """choice: 'heal' ou 'energy'. Devolve o texto do resultado."""
    cfg = shop["events"]
    if choice == "heal":
        amount = int(run.player.max_hp * cfg["rest_heal_pct"])
        run.player.heal(amount)
        return f"Você descansou e recuperou {amount} de vida."
    run.player.add_energy(cfg["rest_energy"])
    return f"Você meditou e ganhou {cfg['rest_energy']} de energia."


# ---------------------------------------------------------------- troca arriscada
def swap_options(run):
    """Cartas que o jogador pode oferecer (as 5 mais recentes)."""
    return list(run.taken_rewards)[-5:]


def remove_card(run, card):
    """Desfaz os efeitos da carta (todos os bônus são somas, então basta aplicar o inverso)."""
    for index, taken in enumerate(run.taken_rewards):
        if taken is card or taken["id"] == card["id"]:
            del run.taken_rewards[index]
            break
    run.player.apply_reward({"effects": [{"type": e["type"], "value": -e["value"]} for e in card["effects"]]})


def swap(run, shop, card, rng):
    """Troca `card` por outra. Sucesso: raridade acima (ou igual se lendária). Falha: raridade abaixo. Devolve (nova_carta, ok, texto)."""
    cfg = shop["events"]
    ok = rng.random() >= cfg["swap_fail_chance"]
    index = RARITIES.index(card["rarity"])
    target = RARITIES[min(len(RARITIES) - 1, index + 1)] if ok else RARITIES[max(0, index - 1)]
    have = {r["id"] for r in run.taken_rewards}
    options = [r for r in run.roll_rewards(only_rarity=target, count=12) if r["id"] not in have and r["id"] != card["id"]]
    run.swaps_used += 1
    if not options:
        return None, True, "Nada de útil apareceu: você ficou com a sua carta."
    remove_card(run, card)
    new = rng.choice(options)
    run.take_reward(new)
    word = "Deu certo!" if ok else "Deu errado..."
    return new, ok, f"{word} {card['name']} virou {new['name']}."


# ---------------------------------------------------------------- sala misteriosa
def mystery(run, shop, rng):
    """Resultado aleatório. Devolve o texto."""
    return mystery_full(run, shop, rng)[0]


def mystery_full(run, shop, rng):
    """Igual a mystery(), mas devolve (texto, carta_recebida_ou_None) para a tela mostrar a carta."""
    weights = shop["events"]["mystery_weights"]
    kind = rng.choices(list(weights), weights=list(weights.values()))[0]
    if kind == "blessing":
        card = rng.choice(run.roll_rewards(count=6) or [None])
        if card:
            run.take_reward(card)
            return f"Uma luz estranha envolve você... Bênção: {card['name']}!", card
    if kind == "bargain":
        cost = int(run.player.hp * 0.2)
        card = rng.choice(run.roll_rewards(only_rarity="epic", count=6) or [None])
        if card and run.player.hp - cost >= 1:
            run.player.hp -= cost
            run.take_reward(card)
            return f"Um vulto oferece um trato: você paga {cost} de vida e recebe {card['name']}!", card
    if kind == "trap":
        cost = max(1, int(run.player.max_hp * 0.15))
        run.player.hp = max(1.0, run.player.hp - cost)
        return f"Era uma armadilha! Você perdeu {cost} de vida.", None
    return "A sala está vazia... só o eco dos seus passos.", None
