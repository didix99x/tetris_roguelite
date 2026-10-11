"""run/floor.py - monta o ANDAR: escolhe e cria o inimigo (ou boss)."""
import random
from dataclasses import dataclass

from bosses.boss import Boss
from bosses.yoshi import YoshiBoss
from characters import character_title
from enemies.enemy import Enemy
from enemies.goblin import Goblin
from enemies.golem import Golem
from enemies.mage_enemy import MageEnemy
from enemies.spider import Spider
from run.progression import player_power, scale_stats, scale_stats_infinite

ENEMY_CLASSES = {
    "goblin": Goblin,
    "spider": Spider,
    "mage": MageEnemy,
    "golem": Golem,
}


@dataclass
class Floor:
    number: int
    enemy: Enemy
    is_boss: bool


def _boss_data(bosses, floor_number):
    """Boss do andar; se não existir um específico, usa o último definido."""
    key = str(floor_number)
    if key in bosses:
        return key, bosses[key]
    older = [int(k) for k in bosses if int(k) <= floor_number]
    key = str(max(older) if older else min(int(k) for k in bosses))
    return key, bosses[key]


def _group_pool(floors_data, enemies_data, floor_number):
    """Inimigos do GRUPO TEMÁTICO deste andar (floors.json > "groups").
    Devolve [] se não houver grupo (aí vale a regra antiga por min_floor)."""
    for group in floors_data.get("groups", []):
        low, high = group["floors"]
        if low <= floor_number <= high:
            return [e["id"] for e in group["enemies"]
                    if e["floors"][0] <= floor_number <= e["floors"][1]
                    and e["id"] in enemies_data["enemies"]]
    return []


def yoshi_floor(enemies_data, mode):
    """Andar do Yoshi: mode "story" (boss do andar 50) ou "infinite" (boss supremo do andar 100). None se não existir."""
    return enemies_data.get("yoshi", {}).get(mode, {}).get("floor")


def build_floor(floor_number, enemies_data, floors_data, rng=None):
    rng = rng or random.Random()
    scaling = floors_data["scaling"]
    if floor_number == yoshi_floor(enemies_data, "story"):      # Yoshi: boss comum do andar 50 (NÃO desbloqueia o personagem)
        data = enemies_data["yoshi"]["story"]
        return Floor(floor_number, Boss("boss_yoshi", data, scale_stats(data, floor_number, scaling)), True)
    if floor_number % floors_data["boss_every"] == 0:
        key, data = _boss_data(enemies_data["bosses"], floor_number)
        stats = scale_stats(data, floor_number, scaling)
        return Floor(floor_number, Boss(f"boss_{key}", data, stats), True)

    eligible = _group_pool(floors_data, enemies_data, floor_number) or [
        eid for eid, d in enemies_data["enemies"].items()
        if d.get("min_floor", 1) <= floor_number and not d.get("group_only")]
    enemy_id = rng.choice(eligible)
    data = enemies_data["enemies"][enemy_id]
    stats = scale_stats(data, floor_number, scaling)
    enemy_class = ENEMY_CLASSES.get(enemy_id, Enemy)
    return Floor(floor_number, enemy_class(enemy_id, data, stats), False)


def _character_enemy_data(char_id, combat_data, characters_data):
    """Dados de inimigo de um PERSONAGEM jogável. Nome, classe, cor e arte vêm de
    data/characters.json (nada duplicado); só vida/dano/habilidades vêm de enemies.json > character_bosses."""
    data = dict(combat_data)
    char = (characters_data or {}).get(char_id)
    if char:
        data["name"] = character_title(char)
        data["color"] = list(char.get("color", [150, 150, 150]))
        data["image"] = char.get("image", char_id)
    else:
        data.setdefault("name", char_id.title())
    data["art_folder"] = "characters"
    data["family"] = char_id
    data["character_id"] = char_id
    data.setdefault("title", "Personagem")
    return data


def _pick_infinite_boss(floor_number, enemies_data, floors_data, rng, own_character, characters_data,
<<<<<<< HEAD
                        locked_characters, boss_misses=None, track=False):
=======
                        locked_characters):
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    """Sorteia um boss do Infinito (da história ou um personagem jogável). Devolve (id, dados).

    Em DUAS etapas (valores em data/floors.json > infinite):
      1) Personagem só entra no sorteio ACIMA do andar `character_boss_after_floor` (padrão 20, ou seja,
         a partir do andar 30) e, aí, com chance `character_boss_chance` (padrão 0.30 = 30%).
      2) Sorteado "personagem": escolhe entre os personagens (os ainda bloqueados têm
         `locked_character_boss_weight` fichas). Senão: escolhe entre os chefes da história.
    Se não houver personagem elegível, o chefe é sempre da história.

<<<<<<< HEAD
    CHEFES DE DESBLOQUEIO: só os personagens AINDA BLOQUEADOS entram no sorteio de personagens (quando todos já
    foram desbloqueados, deixam de aparecer). Com algum bloqueado a chance sobe para `locked_character_boss_chance`
    (padrão 0.5). Aparição GARANTIDA: `boss_misses` {personagem: andares elegíveis seguidos sem aparecer}; ao chegar em
    `boss_pity_floors` (padrão 2) o personagem é o chefe do PRÓXIMO andar elegível. Só conta andar de chefe em que
    ele poderia aparecer (acima de `character_boss_after_floor`, e nunca o personagem da run). `track=True` atualiza
    a contagem (só o andar normal de chefe; o Boss especial e o andar do Yoshi não contam).

=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    Chefes EXCLUSIVOS DO INFINITO (data/enemies.json > infinite_bosses, ids `boss_inf_<chave>`):
      cada um tem `min_floor` (só aparece a partir desse andar). Os normais entram na mesma lista dos chefes
      da história; os SUPER BOSSES (`"super": true`) são mais raros: só aparecem com chance `super_boss_chance`
      (padrão 15%) nos andares de chefe em que algum já esteja liberado.
    """
    every = floors_data["boss_every"]
    settings = floors_data.get("infinite", {})
    story = [(f"boss_{key}", data) for key, data in enemies_data["bosses"].items()
             if int(key) <= max(every, floor_number)]
    characters = []
<<<<<<< HEAD
    entries = {}                       # personagem ainda bloqueado e elegível neste andar -> (id do chefe, dados)
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    if settings.get("include_character_bosses", True) and floor_number > int(settings.get("character_boss_after_floor", 20)):
        locked = set(locked_characters or [])
        for char_id, combat_data in enemies_data.get("character_bosses", {}).items():
            if settings.get("exclude_own_character", True) and char_id == own_character:
                continue
<<<<<<< HEAD
            if char_id not in locked:      # já desbloqueado: não volta como chefe de desbloqueio
                continue
            entry = (f"boss_char_{char_id}", _character_enemy_data(char_id, combat_data, characters_data))
            entries[char_id] = entry
            characters.append(entry)
=======
            entry = (f"boss_char_{char_id}", _character_enemy_data(char_id, combat_data, characters_data))
            characters.append(entry)
            if char_id in locked:          # personagem ainda bloqueado: mais fichas no sorteio entre personagens
                characters.extend([entry] * (int(settings.get("locked_character_boss_weight", 2)) - 1))
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    infinite = [(f"boss_inf_{key}", data) for key, data in enemies_data.get("infinite_bosses", {}).items()
                if int(data.get("min_floor", every)) <= floor_number]
    supers = [entry for entry in infinite if entry[1].get("super")]
    regular = [entry for entry in infinite if not entry[1].get("super")]
<<<<<<< HEAD
    chance = float(settings.get("locked_character_boss_chance", settings.get("character_boss_chance", 0.30)))
    misses = boss_misses if boss_misses is not None else {}
    limit = int(settings.get("boss_pity_floors", 2))
    picked = None
    overdue = [c for c in entries if misses.get(c, 0) >= limit]
    if overdue:                                                  # aparição garantida (ex.: 2 andares elegíveis sem aparecer)
        worst = max(misses.get(c, 0) for c in overdue)
        picked = rng.choice([c for c in overdue if misses.get(c, 0) == worst])
        result = entries[picked]
    elif characters and (not story or rng.random() < chance):
        result = rng.choice(characters)
        picked = result[0][len("boss_char_"):]
    elif supers and rng.random() < float(settings.get("super_boss_chance", 0.15)):
        result = rng.choice(supers)
    else:
        result = rng.choice(story + regular)
    if track:
        for gone in [c for c in misses if c not in (locked_characters or [])]:
            misses.pop(gone, None)                               # já desbloqueado: a contagem some
        for char_id in entries:
            misses[char_id] = 0 if char_id == picked else misses.get(char_id, 0) + 1
    return result
=======
    chance = float(settings.get("character_boss_chance", 0.30))
    if characters and (not story or rng.random() < chance):
        return rng.choice(characters)
    if supers and rng.random() < float(settings.get("super_boss_chance", 0.15)):
        return rng.choice(supers)
    return rng.choice(story + regular)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f


def _infinite_stats(data, floor_number, floors_data, player, base_max_hp, is_boss):
    """Atributos do inimigo no Infinito: andar + força do jogador (run/progression.py)."""
    power = player_power(player, base_max_hp, floor_number, is_boss) if player is not None else None
    return scale_stats_infinite(data, floor_number, floors_data["scaling"], floors_data.get("infinite", {}), power)


def build_infinite_floor(floor_number, enemies_data, floors_data, rng=None, own_character=None,
<<<<<<< HEAD
                         characters_data=None, locked_characters=None, player=None, base_max_hp=None, boss_misses=None):
=======
                         characters_data=None, locked_characters=None, player=None, base_max_hp=None):
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    """Andar do MODO INFINITO.

    - Monstros: sorteados entre os temas já liberados (a cada 10 andares entra um tema novo),
      mais os inimigos exclusivos do Infinito (Fada, Zumbi, Necromante, Dragão).
      Os personagens jogáveis NÃO aparecem como monstros comuns: só como CHEFE.
    - Bosses (andar múltiplo de 10): chefes da história já liberados; a partir do andar 30
      (acima de `character_boss_after_floor`) há 30% de chance (`character_boss_chance`) de o chefe
      ser um personagem jogável (menos o que o jogador usa). Derrotar um personagem bloqueado o desbloqueia.
    - Inimigos exclusivos do Infinito (data/floors.json > infinite > exclusive_enemies): cada um com
      `from_floor`, `to_floor` (opcional) e `weight`, para distribuir o conteúdo pela progressão.
    - Força: andar + força do jogador (`player`), com curva suave e tetos (run/progression.py).
    """
    rng = rng or random.Random()
    scaling = floors_data["scaling"]
    every = floors_data["boss_every"]
    settings = floors_data.get("infinite", {})

    if floor_number == yoshi_floor(enemies_data, "infinite"):    # YOSHI, o Rei do Tetris: SÓ neste andar (nunca é sorteado)
        data = enemies_data["yoshi"]["infinite"]
        stats = _infinite_stats(data, floor_number, floors_data, player, base_max_hp, True)
        return Floor(floor_number, YoshiBoss("boss_yoshi_supreme", data, stats, enemies_data), True)

    if floor_number % every == 0:
        boss_id, data = _pick_infinite_boss(floor_number, enemies_data, floors_data, rng,
<<<<<<< HEAD
                                            own_character, characters_data, locked_characters,
                                            boss_misses=boss_misses, track=True)
=======
                                            own_character, characters_data, locked_characters)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        stats = _infinite_stats(data, floor_number, floors_data, player, base_max_hp, True)
        return Floor(floor_number, Boss(boss_id, data, stats), True)

    groups = floors_data.get("groups", [])
    relative = (floor_number - 1) % every + 1          # 1..9 dentro do ciclo de 10 andares
    unlocked = min(len(groups), (floor_number - 1) // every + 1)
    eligible = []
    for group in groups[:unlocked]:
        start = group["floors"][0]
        for entry in group["enemies"]:
            low, high = entry["floors"]
            if low - (start - 1) <= relative <= high - (start - 1) and entry["id"] in enemies_data["enemies"]:
                eligible.append(entry["id"])
    for extra in settings.get("exclusive_enemies", []):          # exclusivos do Infinito
        if (extra.get("from_floor", 1) <= floor_number <= extra.get("to_floor", float("inf"))
                and extra["id"] in enemies_data["enemies"]):
            eligible.extend([extra["id"]] * int(extra.get("weight", 1)))
    if not eligible:                                    # sem grupos: usa a regra normal
        return build_floor(floor_number, enemies_data, floors_data, rng)
    enemy_id = rng.choice(eligible)
    data = enemies_data["enemies"][enemy_id]
    stats = _infinite_stats(data, floor_number, floors_data, player, base_max_hp, False)
    return Floor(floor_number, ENEMY_CLASSES.get(enemy_id, Enemy)(enemy_id, data, stats), False)


def build_special_boss(floor_number, enemies_data, floors_data, rng=None, own_character=None,
<<<<<<< HEAD
                       characters_data=None, locked_characters=None, player=None, base_max_hp=None, boss_misses=None):
=======
                       characters_data=None, locked_characters=None, player=None, base_max_hp=None):
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    """BOSS ESPECIAL (encontro de 2% do Modo Infinito): usa o mesmo sistema de Boss,
    só um pouco mais forte (special_boss_hp_factor / special_boss_damage_factor)."""
    rng = rng or random.Random()
    settings = floors_data.get("infinite", {})
    boss_id, data = _pick_infinite_boss(max(floor_number, floors_data["boss_every"]), enemies_data, floors_data,
                                        rng, own_character, characters_data, locked_characters)
    stats = _infinite_stats(data, floor_number, floors_data, player, base_max_hp, True)
    stats["hp"] = int(stats["hp"] * settings.get("special_boss_hp_factor", 1.4))
    stats["damage"] = max(1, int(round(stats["damage"] * settings.get("special_boss_damage_factor", 1.15))))
    boss = Boss(boss_id, data, stats)
    boss.name = f"{boss.name} (Especial)"
    return Floor(floor_number, boss, True)
