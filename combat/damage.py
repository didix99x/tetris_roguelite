"""
combat/damage.py - TODOS os valores de dano do puzzle.

Quer mudar o quanto o puzzle machuca? É aqui.
"""

# Dano base por tamanho do match.
MATCH_DAMAGE = {
    3: 10,   # Match 3 = 10 dano
    4: 18,   # Match 4 = 18 dano
    5: 28,   # Match 5 = 28 dano
}

# Para matches maiores que 5: dano extra por bloco acima de 5.
DAMAGE_PER_EXTRA_BLOCK = 6

# Multiplicador de dano de acordo com a chain.
CHAIN_MULTIPLIERS = {
    1: 1.0,
    2: 1.5,
    3: 2.0,
    4: 2.5,
}

# Depois da última chain da tabela, cada nível extra soma isto.
CHAIN_STEP_AFTER_TABLE = 0.5

# Dano por bloco destruído por uma explosão (recompensas).
EXPLOSION_DAMAGE_PER_BLOCK = 4


def match_damage(length):
    if length in MATCH_DAMAGE:
        return MATCH_DAMAGE[length]
    biggest = max(MATCH_DAMAGE)
    if length > biggest:
        return MATCH_DAMAGE[biggest] + (length - biggest) * DAMAGE_PER_EXTRA_BLOCK
    return MATCH_DAMAGE[min(MATCH_DAMAGE)]


def chain_multiplier(level):
    if level < 1:
        return 1.0
    if level in CHAIN_MULTIPLIERS:
        return CHAIN_MULTIPLIERS[level]
    top = max(CHAIN_MULTIPLIERS)
    return CHAIN_MULTIPLIERS[top] + (level - top) * CHAIN_STEP_AFTER_TABLE


def calculate_damage(match_lengths, chain_level, damage_pct=0.0,
                     chain_damage_pct=0.0, extra_multiplier=1.0):
    """Dano total de uma rodada de matches.

    damage_pct        bônus geral de dano (0.10 = +10%)
    chain_damage_pct  bônus que só vale a partir da chain x2
    extra_multiplier  multiplicador da passiva do personagem
    """
    base = sum(match_damage(n) for n in match_lengths)
    multiplier = chain_multiplier(chain_level)
    if chain_level >= 2:
        multiplier *= 1.0 + chain_damage_pct
    total = base * multiplier * (1.0 + damage_pct) * extra_multiplier
    return int(round(total))

# ---- Constantes das cartas novas (críticos e efeitos condicionais) ----
CRIT_BASE_MULTIPLIER = 1.5     # dano de um crítico (1.5 = +50%); cartas podem somar
LOW_HP_THRESHOLD = 0.30        # "vida baixa" = abaixo de 30% da vida máxima
MAX_DAMAGE_REDUCTION = 0.75    # a defesa nunca reduz mais que 75% do dano recebido

# ---- Constantes das cartas do Modo Infinito (limites para nada ficar quebrado) ----
EXECUTE_THRESHOLD = 0.30       # "finalizar": inimigo com menos de 30% de vida
OPENER_THRESHOLD = 0.70        # "abertura": inimigo com mais de 70% de vida
MOMENTUM_MAX_STACKS = 8        # acúmulos máximos do "impulso" (golpes seguidos sem ser atingido)
FLOOR_DAMAGE_CAP = 0.60        # bônus máximo de dano por andar vencido (+60%)
MAX_BLOCK_CHANCE = 0.50        # esquiva máxima de ataques
MAX_THORNS = 1.00              # espinhos devolvem no máximo 100% do dano recebido
MAX_STATUS_RESIST = 0.75       # resistência máxima a veneno/silêncio/pressão/teias
