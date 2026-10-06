"""
combat/effects.py - EFEITOS que mexem no tabuleiro.

Usados pelas habilidades dos inimigos/bosses e pela habilidade do Mago.
Cada função devolve a lista de células afetadas: (x, y, cor) - serve
para os efeitos visuais.
"""
import logging
from collections import Counter

import config
from combat import damage

log = logging.getLogger(__name__)


def _resist(combat):
    """Fator das cartas de resistência: 1.0 = nenhuma; 0.5 = efeitos duram metade."""
    return 1.0 - min(damage.MAX_STATUS_RESIST, combat.player.mods.get("status_resist_pct", 0.0))


def _normal_blocks(board):
    return [b for b in board.blocks() if not b.is_stone and not b.clearing]


def break_blocks(board, amount):
    """BREAK: destrói blocos aleatórios."""
    blocks = _normal_blocks(board)
    board.rng.shuffle(blocks)
    cells = []
    for block in blocks[:amount]:
        cells.append((block.grid_x, block.grid_y, block.color_id))
        board.grid[block.grid_y][block.grid_x] = None
    return cells


def web_blocks(board, amount, duration):
    """WEB: prende blocos em teia (não podem ser trocados por um tempo)."""
    blocks = [b for b in _normal_blocks(board) if not b.is_webbed]
    board.rng.shuffle(blocks)
    cells = []
    for block in blocks[:amount]:
        block.web_time = duration
        cells.append((block.grid_x, block.grid_y, block.color_id))
    return cells


def curse_blocks(board, amount):
    """CURSE: transforma blocos em PEDRA (somem quando um match acontece ao lado)."""
    room = max(0, config.MAX_STONES - board.count_stones())
    blocks = _normal_blocks(board)
    board.rng.shuffle(blocks)
    cells = []
    for block in blocks[:min(amount, room)]:
        cells.append((block.grid_x, block.grid_y, block.color_id))
        block.kind = "stone"
        block.color_id = config.STONE_COLOR_ID
        block.web_time = 0.0
    return cells


def shuffle_blocks(board, amount):
    """EMBARALHAR: troca a cor de blocos aleatórios."""
    blocks = _normal_blocks(board)
    board.rng.shuffle(blocks)
    cells = []
    for block in blocks[:amount]:
        options = [c for c in range(1, config.NUM_COLORS + 1) if c != block.color_id]
        block.color_id = board.rng.choice(options)
        cells.append((block.grid_x, block.grid_y, block.color_id))
    return cells


def recolor_to_dominant(board, amount):
    """Habilidade do MAGO: pinta alguns blocos com a cor mais comum do tabuleiro."""
    blocks = _normal_blocks(board)
    if not blocks:
        return []
    dominant = Counter(b.color_id for b in blocks).most_common(1)[0][0]
    others = [b for b in blocks if b.color_id != dominant]
    board.rng.shuffle(others)
    cells = []
    for block in others[:amount]:
        block.color_id = dominant
        cells.append((block.grid_x, block.grid_y, block.color_id))
    return cells


def cleanse_board(board):
    """Habilidade do BARDO: remove todas as teias e transforma pedras em blocos normais."""
    cells = []
    for block in board.blocks():
        if block.is_stone:
            block.kind = "normal"
            block.color_id = board.rng.randint(1, config.NUM_COLORS)
            cells.append((block.grid_x, block.grid_y, block.color_id))
        elif block.is_webbed:
            block.web_time = 0.0
            cells.append((block.grid_x, block.grid_y, block.color_id))
    return cells


def apply_enemy_ability(combat, ability):
    """Executa uma habilidade de inimigo.

    Devolve (modo, células):
      modo "gravity" = blocos sumiram, precisa de queda/preenchimento;
      modo "check"   = cores mudaram, precisa procurar matches;
      modo "none"    = nada mais a fazer.
    """
    kind = ability["type"]
    board = combat.board
    if kind == "break":
        return "gravity", break_blocks(board, int(ability["amount"]))
    if kind == "web":
        return "none", web_blocks(board, int(ability["amount"]), ability.get("duration", 8.0) * _resist(combat))
    if kind == "curse":
        return "none", curse_blocks(board, int(ability["amount"]))
    if kind == "shuffle":
        return "check", shuffle_blocks(board, int(ability["amount"]))
    if kind == "weight":
        combat.haste_time = ability.get("duration", 6.0) * _resist(combat)
        combat.haste_factor = ability.get("speed", 1.8)
        return "none", []
    # ---- habilidades novas (extensão; as antigas acima não mudaram) ----
    if kind == "poison":      # veneno: tira HP do jogador por segundo
        combat.poison_dps = max(combat.poison_dps, float(ability.get("amount", 1.0)))
        combat.poison_time = max(combat.poison_time, float(ability.get("duration", 5.0)) * _resist(combat))
        return "none", []
    if kind == "silence":     # silêncio: o jogador não pode usar habilidade
        combat.silence_time = max(combat.silence_time, float(ability.get("duration", 4.0)) * _resist(combat))
        return "none", []
    if kind == "blind":       # cegueira do Yoshi: efeito SÓ VISUAL (a tela escurece). Nada do jogo muda. Não é reduzida por cartas.
        combat.blind_total = combat.blind_time = float(ability.get("duration", 2.0))
        return "none", []
    if kind == "drain":       # drenar: tira energia do jogador (a habilidade fica mais longe)
        combat.player.energy = max(0.0, combat.player.energy - float(ability.get("amount", 10)))
        return "none", []
    if kind == "strike":      # golpe extra: "amount" = % do ataque normal do inimigo (escala com o andar).
        # Respeita defesa, esquiva, espinhos e segunda chance.
        combat.hurt_player(max(1, int(round(combat.enemy.attack_damage() * float(ability.get("amount", 50)) / 100.0))))
        return "none", []
    if kind == "armor":       # armadura: o inimigo recebe menos dano dos matches
        combat.enemy_armor_pct = float(ability.get("percent", 30))
        combat.enemy_armor_time = float(ability.get("duration", 6.0))
        return "none", []
    if kind == "heal":        # cura: o inimigo recupera % da vida máxima
        enemy = combat.enemy
        healed = min(enemy.max_hp - enemy.hp, int(round(enemy.max_hp * float(ability.get("amount", 8)) / 100)))
        if healed > 0:
            enemy.hp += healed
            combat.emit("enemy_heal", amount=healed)
        return "none", []
    log.warning("Habilidade de inimigo desconhecida: %s", kind)
    return "none", []
