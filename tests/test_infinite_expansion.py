"""
tests/test_infinite_expansion.py - EXPANSÃO FINAL DO MODO INFINITO:
15 bosses (5 Super Bosses), 30 inimigos, escalonamento por andar + força do jogador,
45 cartas novas, sprites e as mecânicas novas.

Rodar:  python -m unittest tests.test_infinite_expansion -v
"""
import copy
import os
import random
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from bosses.boss import Boss
from characters.character import DEFAULT_MODS
from combat import damage, effects
from combat.combat import Combat, IDLE
from enemies.enemy import Enemy
from run.floor import build_floor, build_infinite_floor, build_special_boss
from run.progression import player_power, scale_stats, scale_stats_infinite
from run.run_manager import RunManager
from tests.test_logic import bot_move, load_data

ABILITIES = {"break", "web", "curse", "weight", "shuffle", "poison", "silence", "armor", "heal", "drain", "strike"}
BOSS_MECHANICS = {"chain_armor", "enrage_hp", "enrage_factor", "phase_two_hp", "phase_two_boost", "phase_three_hp",
                  "phase_three_factor", "phase_three_boost", "armor", "match3_reduction", "regen_pct", "attack_heal_pct"}
ENEMY_PASSIVES = {"armor", "chain1_reduction", "match3_reduction", "enrage_hp", "enrage_factor", "regen_pct",
                  "attack_heal_pct", "hp_threshold", "cooldown_factor", "extra_web_time"}

OLD_ENEMIES = {"goblin", "spider", "mage", "golem", "fairy", "zombie", "necromancer", "dragon"}


def new_enemy_ids(data):
    groups = {e["id"] for g in data["floors"]["groups"] for e in g["enemies"]}
    return [i for i, d in data["enemies"]["enemies"].items() if d.get("infinite_only") and i not in groups
            and i not in OLD_ENEMIES]


class Base(unittest.TestCase):
    def setUp(self):
        self.data = load_data()
        self.enemies = self.data["enemies"]
        self.floors = self.data["floors"]

    def infinite(self, floor, seed, own="warrior", **kw):
<<<<<<< HEAD
        return build_infinite_floor(floor, self.enemies, self.floors, random.Random(seed), own, self.data["characters"],
                                    list(self.data["characters"]), **kw)
=======
        return build_infinite_floor(floor, self.enemies, self.floors, random.Random(seed), own, self.data["characters"], [], **kw)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f

    def fresh_combat(self, char="warrior", floor=1, seed=1):
        run = RunManager(char, self.data, random.Random(seed), mode="infinite")
        run.floor_number = floor
        return run, run.start_floor()


# ======================================================================
# 1) 15 NOVOS BOSSES (5 SUPER)
# ======================================================================
class NewBosses(Base):
    def test_exactly_15_bosses_and_5_super(self):
        bosses = self.enemies["infinite_bosses"]
        self.assertEqual(len(bosses), 15)
        supers = [k for k, b in bosses.items() if b.get("super")]
        self.assertEqual(len(supers), 5)
        self.assertEqual(len(bosses) - len(supers), 10)

    def test_every_boss_is_complete_and_valid(self):
        names, art = set(), set()
        for key, b in self.enemies["infinite_bosses"].items():
            for field in ("name", "hp", "damage", "cooldown", "color", "mechanic_name", "mechanic_text", "mechanics",
                          "abilities", "min_floor", "portrait"):
                self.assertIn(field, b, f"{key}.{field}")
            self.assertGreater(b["hp"], 0)
            self.assertGreater(b["damage"], 0)
            self.assertGreaterEqual(len(b["abilities"]), 3, key)
            self.assertNotIn(b["name"], names)
            names.add(b["name"])
            for ability in b["abilities"]:
                self.assertIn(ability["type"], ABILITIES, key)
            self.assertTrue(set(b["mechanics"]) <= BOSS_MECHANICS, key)
            self.assertTrue(b["mechanics"], f"{key} precisa de pelo menos uma mecânica própria")
            art.add(os.path.join(ROOT, "assets", "images", "bosses", f"boss_inf_{key}.png"))
        self.assertTrue(all(os.path.exists(p) for p in art), "falta sprite de algum boss")

    def test_super_bosses_are_rarer_stronger_and_special(self):
        bosses = self.enemies["infinite_bosses"]
        supers = [b for b in bosses.values() if b.get("super")]
        normals = [b for b in bosses.values() if not b.get("super")]
        self.assertGreater(sum(b["hp"] for b in supers) / 5, 1.5 * sum(b["hp"] for b in normals) / 10)
        self.assertGreater(min(b["hp"] for b in supers), max(b["hp"] for b in normals) * 0.9)
        for b in supers:
            self.assertGreaterEqual(len(b["abilities"]), 4)
            self.assertTrue(any("phase_three_hp" in b["mechanics"] or "regen_pct" in b["mechanics"]
                                or "attack_heal_pct" in b["mechanics"] for _ in [0]), b["name"])
            self.assertIn("SUPER", b["title"])
        # sempre a partir de um andar mais alto que o dos normais mais fracos
        self.assertGreater(min(b["min_floor"] for b in supers), min(b["min_floor"] for b in normals))

    def test_boss_objects_expose_super_flag(self):
        for key, data in self.enemies["infinite_bosses"].items():
            boss = Boss(f"boss_inf_{key}", data, scale_stats(data, 30, self.floors["scaling"]))
            self.assertEqual(boss.is_super, bool(data.get("super")))
            self.assertTrue(boss.is_boss)
            self.assertTrue(boss.passive_label())

    def test_progression_by_floor_min_floors_spread(self):
        mins = sorted(b["min_floor"] for b in self.enemies["infinite_bosses"].values())
        self.assertEqual(mins[0], 10)
        self.assertGreaterEqual(mins[-1], 60)
        self.assertGreaterEqual(len(set(mins)), 6)

    def test_new_bosses_appear_only_from_their_min_floor_and_supers_are_rare(self):
        counts = {"super": 0, "boss": 0}
        seen = set()
        for floor in range(10, 121, 10):
            for seed in range(120):
                f = self.infinite(floor, seed)
                self.assertTrue(f.is_boss)
                if f.enemy.id.startswith("boss_inf_"):
                    key = f.enemy.id[len("boss_inf_"):]
                    self.assertLessEqual(self.enemies["infinite_bosses"][key]["min_floor"], floor, (key, floor))
                    seen.add(key)
                    if f.enemy.is_super:
                        counts["super"] += 1
                counts["boss"] += 1
        self.assertEqual(seen, set(self.enemies["infinite_bosses"]), "todos os 15 devem poder aparecer")
        share = counts["super"] / counts["boss"]
        self.assertLess(share, 0.2)          # raros...
        self.assertGreater(share, 0.03)      # ...mas existem

    def test_no_super_boss_below_floor_30_and_characters_rule_kept(self):
        for floor in (10, 20):
            for seed in range(300):
                e = self.infinite(floor, seed).enemy
                self.assertFalse(e.is_super)
                self.assertIsNone(e.character_id)
        self.assertTrue(any(self.infinite(30, s).enemy.character_id for s in range(200)))

    def test_boss_mechanics_work(self):
        stats = {"hp": 1000, "damage": 10, "cooldown": 6.0, "ability_bonus": 0}
        base = {"name": "T", "abilities": [{"type": "break", "name": "b", "amount": 10}]}
        boss = Boss("t", dict(base, mechanics={"armor": 0.2, "match3_reduction": 0.5}), stats)
        self.assertEqual(boss.modify_incoming(100, 2, 4), 80)            # só armadura
        self.assertEqual(boss.modify_incoming(100, 2, 3), 40)            # armadura + match 3
        boss = Boss("t", dict(base, mechanics={"phase_two_hp": 0.6, "phase_two_boost": 1.4, "phase_three_hp": 0.3,
                                               "phase_three_factor": 0.7, "phase_three_boost": 1.8}), stats)
        self.assertEqual(boss.next_ability()["amount"], 10)
        boss.hp = 500
        self.assertEqual(boss.next_ability()["amount"], 14)
        self.assertEqual(boss.cooldown_factor(), 1.0)
        boss.hp = 200
        self.assertEqual(boss.next_ability()["amount"], 18)
        self.assertAlmostEqual(boss.cooldown_factor(), 0.7)
        boss = Boss("t", dict(base, mechanics={"regen_pct": 0.01, "attack_heal_pct": 0.05}), stats)
        self.assertAlmostEqual(boss.regen_per_sec(), 10.0)
        self.assertEqual(boss.attack_heal(), 50)
        # bosses antigos continuam iguais
        old = Boss("boss_30", self.enemies["bosses"]["30"], stats)
        self.assertEqual(old.modify_incoming(100, 1, 3), 100)

    def test_regen_and_attack_heal_work_in_combat(self):
        run, combat = self.fresh_combat()
        combat.enemy.passive_params = {"regen_pct": 0.05, "attack_heal_pct": 0.1}
        combat.enemy.hp = combat.enemy.max_hp // 2
        before = combat.enemy.hp
        for _ in range(60):
            combat.update(1 / 20)
            if combat.phase != IDLE:
                break
        self.assertGreater(combat.enemy.hp, before)
        self.assertIsInstance(combat.enemy.hp, int)
        combat.enemy.hp = combat.enemy.max_hp // 2
        combat.enemy_timer = 0.0
        combat._enemy_attack()
        self.assertTrue(any(e["type"] == "enemy_heal" for e in combat.pop_events()))

    def test_every_new_boss_survives_a_fight(self):
        for key in self.enemies["infinite_bosses"]:
            for floor in (self.enemies["infinite_bosses"][key]["min_floor"], 90):
                run, _ = self.fresh_combat(floor=floor)
                data = self.enemies["infinite_bosses"][key]
                boss = Boss(f"boss_inf_{key}", data, scale_stats_infinite(data, floor, self.floors["scaling"], self.floors["infinite"]))
                combat = Combat(run.player, boss, floor, random.Random(3))
                run.player.max_hp = run.player.hp = 100000
                rng = random.Random(4)
                for _ in range(900):
                    if combat.phase == IDLE:
                        bot_move(combat, rng)
                    combat.update(1 / 20)
                    combat.pop_events()
                    if combat.result:
                        break
                self.assertEqual(sum(1 for _ in combat.board.blocks()), 64, key)       # o puzzle segue íntegro


# ======================================================================
# 2) 30 NOVOS INIMIGOS
# ======================================================================
class NewEnemies(Base):
    def test_exactly_30_new_enemies_with_identity(self):
        ids = new_enemy_ids(self.data)
        self.assertEqual(len(ids), 30)
        names, signatures = set(), set()
        for eid in ids:
            d = self.enemies["enemies"][eid]
            for field in ("name", "hp", "damage", "cooldown", "color", "abilities", "passive_name", "passive_text",
                          "passive_params", "family", "portrait"):
                self.assertIn(field, d, f"{eid}.{field}")
            self.assertGreater(d["hp"], 0)
            self.assertGreater(d["cooldown"], 0)
            self.assertNotIn(d["name"], names)
            names.add(d["name"])
            self.assertTrue(d["passive_params"], eid)
            self.assertTrue(set(d["passive_params"]) <= ENEMY_PASSIVES, eid)
            for ability in d["abilities"]:
                self.assertIn(ability["type"], ABILITIES, eid)
            sig = (tuple(a["type"] for a in d["abilities"]), tuple(sorted(d["passive_params"].items())), d["hp"], d["damage"])
            self.assertNotIn(sig, signatures, f"{eid} é uma cópia disfarçada de outro inimigo")
            signatures.add(sig)
            self.assertTrue(os.path.exists(os.path.join(ROOT, "assets", "images", "enemies", eid + ".png")), eid)

    def test_new_enemies_use_new_abilities_and_traits_somewhere(self):
        types = {a["type"] for i in new_enemy_ids(self.data) for a in self.enemies["enemies"][i]["abilities"]}
        self.assertTrue({"drain", "strike"} <= types)
        traits = {k for i in new_enemy_ids(self.data) for k in self.enemies["enemies"][i]["passive_params"]}
        self.assertTrue({"regen_pct", "attack_heal_pct", "armor", "chain1_reduction", "match3_reduction", "enrage_hp"} <= traits)

    def test_distributed_across_progression(self):
        entries = {e["id"]: e for e in self.floors["infinite"]["exclusive_enemies"]}
        froms = sorted(entries[i]["from_floor"] for i in new_enemy_ids(self.data))
        self.assertLessEqual(froms[0], 1)
        self.assertGreaterEqual(froms[-1], 90)
        for lo, hi in ((1, 15), (10, 30), (25, 50), (45, 70), (70, 100)):
            self.assertGreaterEqual(sum(1 for f in froms if lo <= f <= hi), 3, (lo, hi))

    def test_new_enemies_never_appear_in_story_mode(self):
        ids = set(new_enemy_ids(self.data))
        for floor in range(1, 51):
            for seed in range(25):
                f = build_floor(floor, self.enemies, self.floors, random.Random(seed * 100 + floor))
                self.assertNotIn(f.enemy.id, ids)

    def test_each_new_enemy_appears_inside_its_window_only(self):
        entries = {e["id"]: e for e in self.floors["infinite"]["exclusive_enemies"]}
        seen = set()
        for floor in list(range(1, 121)):
            if floor % 10 == 0:
                continue
            for seed in range(14):
                eid = self.infinite(floor, seed * 7 + floor).enemy.id
                if eid in entries:
                    e = entries[eid]
                    self.assertTrue(e["from_floor"] <= floor <= e.get("to_floor", 10 ** 9), (eid, floor))
                    seen.add(eid)
        self.assertTrue(set(new_enemy_ids(self.data)) <= seen, set(new_enemy_ids(self.data)) - seen)

    def test_old_enemies_still_appear_late(self):
        late = {self.infinite(95, s).enemy.id for s in range(500)}
        self.assertTrue(late & {"goblin", "spider", "mage", "golem", "void_herald", "goblin_champion", "golem_iron"} or
                        any(i.split("_")[0] in ("goblin", "spider", "mage", "golem", "void") for i in late))
        self.assertTrue(late & {"fairy", "zombie", "necromancer", "dragon"})

    def test_every_new_enemy_fights_without_errors_at_two_floors(self):
        for eid in new_enemy_ids(self.data):
            data = self.enemies["enemies"][eid]
            for floor in (12, 80):
                run, _ = self.fresh_combat(floor=floor)
                enemy = Enemy(eid, data, scale_stats_infinite(data, floor, self.floors["scaling"], self.floors["infinite"]))
                combat = Combat(run.player, enemy, floor, random.Random(5))
                run.player.max_hp = run.player.hp = 100000
                rng = random.Random(6)
                for _ in range(700):
                    if combat.phase == IDLE:
                        bot_move(combat, rng)
                    combat.update(1 / 20)
                    combat.pop_events()
                    if combat.result:
                        break
                self.assertEqual(sum(1 for _ in combat.board.blocks()), 64, eid)

    def test_drain_and_strike_abilities(self):
        run, combat = self.fresh_combat()
        combat.player.energy = 60
        effects.apply_enemy_ability(combat, {"type": "drain", "name": "d", "amount": 25})
        self.assertEqual(combat.player.energy, 35)
        effects.apply_enemy_ability(combat, {"type": "drain", "name": "d", "amount": 99})
        self.assertEqual(combat.player.energy, 0)
        combat.enemy.damage = 20
        hp = combat.player.hp
        effects.apply_enemy_ability(combat, {"type": "strike", "name": "s", "amount": 50})
        self.assertEqual(round(hp - combat.player.hp), 10)                        # 50% de 20
        combat.player.mods["damage_reduction_pct"] = 0.5
        hp = combat.player.hp
        effects.apply_enemy_ability(combat, {"type": "strike", "name": "s", "amount": 100})
        self.assertEqual(round(hp - combat.player.hp), 10)                        # defesa vale no golpe


# ======================================================================
# 3) ESCALONAMENTO
# ======================================================================
class FakePlayer:
    def __init__(self, max_hp=120, **mods):
        self.max_hp = max_hp
        self.mods = dict(DEFAULT_MODS)
        self.mods.update(mods)


class Scaling(Base):
    def stats(self, data, floor, power=None):
        return scale_stats_infinite(data, floor, self.floors["scaling"], self.floors["infinite"], power)

    def test_identical_to_normal_scaling_up_to_the_knee(self):
        goblin = self.enemies["enemies"]["goblin"]
        for floor in (1, 10, 25, 50):
            self.assertEqual(self.stats(goblin, floor), scale_stats(goblin, floor, self.floors["scaling"]), floor)

    def test_grows_with_floor_but_slower_after_the_knee_and_is_capped(self):
        boss = self.enemies["bosses"]["50"]
        prev = 0
        for floor in range(1, 400, 7):
            hp = self.stats(boss, floor)["hp"]
            self.assertGreaterEqual(hp, prev)
            prev = hp
        linear_100 = scale_stats(boss, 100, self.floors["scaling"])
        new_100 = self.stats(boss, 100)
        self.assertLess(new_100["hp"], linear_100["hp"])
        self.assertLess(new_100["damage"], linear_100["damage"])
        cap = self.floors["infinite"]["scaling"]
        huge = self.stats(boss, 100000)
        self.assertLessEqual(huge["hp"], boss["hp"] * cap["hp_mult_cap"] + 1)
        self.assertLessEqual(huge["damage"], boss["damage"] * cap["damage_mult_cap"] + 1)
        self.assertLessEqual(huge["ability_bonus"], cap["ability_bonus_cap"])
        self.assertGreaterEqual(huge["cooldown"], min(cap["min_cooldown_seconds"], boss["cooldown"]) - 1e-9)

    def test_player_power_is_one_without_cards_and_grows_with_cards(self):
        base = player_power(FakePlayer(), 120)
        self.assertAlmostEqual(base["offense"], 1.0)
        self.assertAlmostEqual(base["defense"], 1.0)
        self.assertAlmostEqual(base["power"], 1.0)
        strong = player_power(FakePlayer(180, damage_pct=1.0, crit_chance=0.3, damage_reduction_pct=0.3, lifesteal_pct=0.1), 120)
        self.assertGreater(strong["offense"], 2.0)
        self.assertGreater(strong["defense"], 1.8)
        self.assertGreater(strong["power"], base["power"])

    def test_every_new_mod_counts_toward_power(self):
        base = player_power(FakePlayer(), 120)
        for mod in DEFAULT_MODS:
            value = {"max_hp": 0, "ability_cost_pct": -0.4}.get(mod, 0.4)
            if mod in ("chain_start",):
                value = 1
            p = player_power(FakePlayer(**{mod: value}), 120, floor_number=30, is_boss=True)
            self.assertGreaterEqual(p["power"], base["power"] - 1e-9, mod)

    def test_enemy_adapts_to_player_without_becoming_a_sponge(self):
        goblin = self.enemies["enemies"]["goblin_champion"]
        floor = 30
        plain = self.stats(goblin, floor)
        strong_power = player_power(FakePlayer(220, damage_pct=1.5, crit_chance=0.4, chain_damage_pct=0.5,
                                               damage_reduction_pct=0.4, lifesteal_pct=0.12), 120)
        adapted = self.stats(goblin, floor, strong_power)
        self.assertGreater(adapted["hp"], plain["hp"])
        self.assertGreater(adapted["damage"], plain["damage"])
        self.assertLess(adapted["cooldown"], plain["cooldown"])                    # ataca mais rápido
        self.assertGreater(adapted["ability_bonus"], plain["ability_bonus"])       # habilidades mais fortes
        cfg = self.floors["infinite"]["scaling"]["player_power"]
        self.assertLessEqual(adapted["hp"], plain["hp"] * cfg["hp_cap"] + 1)       # tetos
        self.assertLessEqual(adapted["damage"], plain["damage"] * cfg["damage_cap"] + 1)
        # HP cresce MENOS que a força do jogador: ele continua sentindo progressão
        self.assertLess(adapted["hp"] / plain["hp"], strong_power["offense"])

    def test_weak_player_is_never_easier_than_floor_only(self):
        goblin = self.enemies["enemies"]["goblin"]
        weak = player_power(FakePlayer(60, damage_reduction_pct=-0.2), 120)
        self.assertEqual(self.stats(goblin, 20, weak), self.stats(goblin, 20))

    def test_boss_damage_cards_only_count_against_bosses(self):
        p = FakePlayer(boss_damage_pct=1.0)
        self.assertAlmostEqual(player_power(p, 120, 30, False)["offense"], 1.0)
        self.assertGreater(player_power(p, 120, 30, True)["offense"], 1.5)

    def test_run_manager_passes_the_players_strength(self):
        run_a, combat_a = self.fresh_combat(floor=40)
        run_b = RunManager("warrior", self.data, random.Random(1), mode="infinite")
        run_b.floor_number = 40
        for cid in ("i_pact_e1", "i_crown_l1", "n_def_l1", "i_exec_e1"):
            run_b.take_reward(next(r for r in self.data["rewards"]["rewards"] if r["id"] == cid))
        combat_b = run_b.start_floor()
        if combat_a.enemy.id == combat_b.enemy.id:
            self.assertGreater(combat_b.enemy.max_hp, combat_a.enemy.max_hp)
        # na mesma criatura, a diferença vem só do jogador
        data = self.enemies["enemies"]["goblin"]
        a = scale_stats_infinite(data, 40, self.floors["scaling"], self.floors["infinite"], player_power(run_a.player, 120))
        b = scale_stats_infinite(data, 40, self.floors["scaling"], self.floors["infinite"], player_power(run_b.player, 120))
        self.assertGreater(b["hp"], a["hp"])

    def test_story_mode_is_untouched(self):
        for floor in (1, 17, 33, 50):
            f = build_floor(floor, self.enemies, self.floors, random.Random(floor))
            if floor == 50:                                           # andar 50 da história: Yoshi (boss comum)
                data = self.enemies["yoshi"]["story"]
            else:
                data = self.enemies["bosses"][str(floor)] if f.is_boss else self.enemies["enemies"][f.enemy.id]
            self.assertEqual(f.enemy.max_hp, scale_stats(data, floor, self.floors["scaling"])["hp"])

    def test_special_boss_also_uses_new_scaling(self):
        f = build_special_boss(60, self.enemies, self.floors, random.Random(2), "warrior", self.data["characters"], [],
                               player=FakePlayer(), base_max_hp=120)
        self.assertTrue(f.enemy.is_boss)
        self.assertGreater(f.enemy.max_hp, 0)

    def test_infinite_run_with_all_new_cards_keeps_working(self):
        for char in ("warrior", "mage"):
            run = RunManager(char, self.data, random.Random(7), mode="infinite")
            cards = [r for r in self.data["rewards"]["rewards"] if r["id"].startswith("i_")]
            rng = random.Random(8)
            for floor in range(1, 16):
                run.floor_number = floor
                combat = run.start_floor()
                run.player.hp = run.player.max_hp
                for _ in range(1500):
                    if combat.phase == IDLE:
                        bot_move(combat, rng)
                    combat.update(1 / 20)
                    combat.pop_events()
                    if combat.result:
                        break
                self.assertIsNotNone(combat.result, (char, floor))
                if combat.result == "lose":
                    break
                run.floor_cleared()
                run.take_reward(cards[(floor * 3) % len(cards)])


# ======================================================================
# 4) CARTAS NOVAS
# ======================================================================
class NewCards(Base):
    def cards(self):
        return [r for r in self.data["rewards"]["rewards"] if r["id"].startswith("i_")]

    def test_at_least_40_new_cards_with_all_rarities(self):
        cards = self.cards()
        self.assertGreaterEqual(len(cards), 40)
        rarities = {c["rarity"] for c in cards}
        self.assertEqual(rarities, {"common", "rare", "epic", "legendary"})
        self.assertGreaterEqual(sum(1 for c in cards if c["rarity"] == "legendary"), 6)
        ids = [r["id"] for r in self.data["rewards"]["rewards"]]
        self.assertEqual(len(ids), len(set(ids)))

    def test_cards_are_valid_and_apply(self):
        valid = set(DEFAULT_MODS) | {"max_hp", "heal_pct", "energy"}
        for c in self.cards():
            self.assertTrue(c["description"] and c["name"] and c["category"])
            self.assertLessEqual(len(c["description"]), 90, c["id"])
            self.assertTrue(c["effects"])
            for e in c["effects"]:
                self.assertIn(e["type"], valid, c["id"])
            run = RunManager("warrior", self.data, random.Random(1))
            run.take_reward(c)
            self.assertTrue(run.player.mod_lines() or any(e["type"] in ("max_hp",) for e in c["effects"]), c["id"])

    def test_builds_not_just_damage(self):
        cards = self.cards()
        only_damage = [c["id"] for c in cards if {e["type"] for e in c["effects"]} <= {"damage_pct", "chain_damage_pct"}]
        self.assertEqual(only_damage, [])
        kinds = {e["type"] for c in cards for e in c["effects"]}
        self.assertGreaterEqual(len(kinds), 25)
        self.assertGreaterEqual(len({c["category"] for c in cards}), 12)
        for needed in ("crítico", "combo", "energia", "habilidade", "defesa", "velocidade", "risco", "sinergia",
                       "condicional", "boss", "infinito"):
            self.assertIn(needed, {c["category"] for c in cards}, needed)
        self.assertTrue({c["category"] for c in cards} & {"cura", "regeneração"})
        multi = [c for c in cards if len(c["effects"]) >= 2]
        self.assertGreaterEqual(len(multi), 30)

    def test_legendaries_have_unique_effects(self):
<<<<<<< HEAD
        old_types = {e["type"] for r in self.data["rewards"]["rewards"]
                     if not r["id"].startswith("i_") and not r.get("shop") for e in r["effects"]}
=======
        old_types = {e["type"] for r in self.data["rewards"]["rewards"] if not r["id"].startswith("i_") for e in r["effects"]}
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
        legends = [c for c in self.cards() if c["rarity"] == "legendary"]
        unique = [c["id"] for c in legends if {e["type"] for e in c["effects"]} - old_types]
        self.assertGreaterEqual(len(unique), 7)
        self.assertEqual(len({tuple(sorted(e["type"] for e in c["effects"])) for c in legends}), len(legends))

    def test_risk_cards_have_a_real_cost(self):
        for cid in ("i_gamble_r1", "i_pact_e1", "i_glass_e1", "i_bloodsteel_l1"):
            card = next(c for c in self.cards() if c["id"] == cid)
            costs = [e for e in card["effects"] if (e["type"] in ("max_hp", "damage_reduction_pct") and e["value"] < 0)]
            self.assertTrue(costs, cid)
        run = RunManager("warrior", self.data, random.Random(1))
        hp = run.player.max_hp
        run.take_reward(next(c for c in self.cards() if c["id"] == "i_pact_e1"))
        self.assertEqual(run.player.max_hp, hp - 25)
        self.assertLessEqual(run.player.hp, run.player.max_hp)
        self.assertGreaterEqual(run.player.hp, 1)

    def test_rewards_pool_offers_new_cards_by_floor_and_rarity(self):
        from rewards.reward_pool import roll_rewards
        seen = set()
        for seed in range(400):
            for c in roll_rewards(self.data["rewards"], 3, 30, random.Random(seed)):
                seen.add(c["id"])
        for seed in range(60):                                         # lendárias são raras: sorteio só entre elas
            for c in roll_rewards(self.data["rewards"], 8, 30, random.Random(seed), only_rarity="legendary"):
                seen.add(c["id"])
        self.assertTrue({c["id"] for c in self.cards()} <= seen, {c["id"] for c in self.cards()} - seen)
        for seed in range(100):
            for c in roll_rewards(self.data["rewards"], 3, 1, random.Random(seed)):
                self.assertLessEqual(c.get("min_floor", 1), 1)
        legend = {c["id"] for c in roll_rewards(self.data["rewards"], 8, 30, random.Random(1), only_rarity="legendary")}
        self.assertTrue(legend)
        rare_share = {}
        for seed in range(2000):
            for c in roll_rewards(self.data["rewards"], 3, 50, random.Random(seed)):
                rare_share[c["rarity"]] = rare_share.get(c["rarity"], 0) + 1
        total = sum(rare_share.values())
        self.assertLess(rare_share["legendary"] / total, 0.04)         # lendárias continuam raras
        self.assertGreater(rare_share["common"] / total, 0.45)


class NewCardMechanics(Base):
    """Cada efeito novo, isolado e com número exato."""

    def setUp(self):
        super().setUp()
        self.run = RunManager("mage", self.data, random.Random(1), mode="infinite")      # mago: sem passiva de dano
        self.combat = self.run.start_floor()
        self.combat.enemy.max_hp = self.combat.enemy.hp = 100000
        self.combat.enemy.passive_params = {}
        self.mods = self.run.player.mods
        self.combat.chain.count = 1

    def hit(self, lengths=(3,), level=1):
        before = self.combat.enemy.hp
        self.combat._deal_match_damage(list(lengths), level, 0)
        return before - self.combat.enemy.hp

    def test_big_match_and_quick_and_opener_and_execute(self):
        base = self.hit()
        self.mods["big_match_damage_pct"] = 0.5
        self.assertEqual(self.hit((3,)), base)                                   # só vale em match 4+
        self.assertAlmostEqual(self.hit((4,)) / (base * 18 / 10 * 1.5), 1, delta=0.02)
        self.mods["quick_damage_pct"] = 1.0
        self.combat.quick_active = False
        self.assertEqual(self.hit(), base)
        self.combat.quick_active = True
        self.assertEqual(self.hit(), base * 2)
        self.combat.quick_active = False
        self.mods["opener_damage_pct"] = 1.0
        self.assertEqual(self.hit(), base * 2)                                   # inimigo com 100% de vida
        self.combat.enemy.hp = int(self.combat.enemy.max_hp * 0.5)
        self.assertEqual(self.hit(), base)
        self.mods["execute_damage_pct"] = 3.0
        self.combat.enemy.hp = int(self.combat.enemy.max_hp * 0.2)
        self.assertEqual(self.hit(), base * 4)

    def test_momentum_stacks_and_resets_when_hit(self):
        base = self.hit()
        self.mods["momentum_pct"] = 0.1
        self.combat.momentum = 0
        first = self.hit()
        second = self.hit()
        self.assertEqual(first, base)
        self.assertEqual(second, int(round(base * 1.1)))
        for _ in range(20):
            self.hit()
        self.assertEqual(self.combat.momentum, damage.MOMENTUM_MAX_STACKS)       # teto
        self.combat.hurt_player(1)
        self.assertEqual(self.combat.momentum, 0)

    def test_floor_damage_is_capped(self):
        base = self.hit()
        self.mods["floor_damage_pct"] = 0.01
        self.combat.floor_number = 10
        self.assertEqual(self.hit(), int(round(base * 1.1)))
        self.combat.floor_number = 1000
        self.assertEqual(self.hit(), int(round(base * (1 + damage.FLOOR_DAMAGE_CAP))))

    def test_energy_heal_and_crit_cards(self):
        self.mods["chain_energy"] = 5
        self.combat.player.energy = 0
        self.combat._give_energy(0, [3], 3)
        with_card = self.combat.player.energy
        self.mods["chain_energy"] = 0
        self.combat.player.energy = 0
        self.combat._give_energy(0, [3], 3)
        self.assertAlmostEqual(with_card - self.combat.player.energy, 10)       # (3-1) * 5
        self.mods.update(crit_chance=1.0, crit_energy=7, crit_heal=9)
        self.combat.player.hp = 50.0
        self.combat.player.energy = 0
        self.hit()
        self.assertEqual(self.combat.player.energy, 7)
        self.assertEqual(self.combat.player.hp, 59.0)

    def test_match_heal(self):
        self.mods["match_heal"] = 3
        self.combat.player.hp = 40.0
        self.combat.board = make_board_with_match(self.combat)
        self.combat.start_resolve("player")
        self.assertGreaterEqual(self.combat.player.hp, 43.0)

    def test_ability_refund_and_heal(self):
        self.mods.update(ability_refund_pct=0.5, ability_heal=10)
        player = self.combat.player
        player.energy = player.energy_max
        player.hp = 30.0
        cost = player.current_ability_cost()
        self.assertTrue(self.combat.use_ability())
        self.assertGreaterEqual(player.energy, player.energy_max - cost + cost * 0.5 - 1e-6)
        self.assertGreaterEqual(player.hp, 40.0)

    def test_block_thorns_and_defense_and_vulnerability(self):
        class Fixed:
            def __init__(self, v):
                self.v = v

            def random(self):
                return self.v

        self.combat.player.max_hp = 1000
        self.combat.player.hp = 1000.0
        self.combat.rng = Fixed(0.0)
        self.mods["block_chance"] = 0.3
        hp = self.combat.player.hp
        self.assertEqual(self.combat.hurt_player(20), 0)
        self.assertEqual(self.combat.player.hp, hp)
        self.assertTrue(any(e["type"] == "block" for e in self.combat.pop_events()))
        self.combat.rng = Fixed(0.99)
        self.assertEqual(self.combat.hurt_player(20), 20)
        self.mods["block_chance"] = 5.0                                           # teto de esquiva (50%)
        self.combat.rng = Fixed(0.6)
        self.assertEqual(self.combat.hurt_player(10), 10)
        self.mods["block_chance"] = 0.0
        self.mods["thorns_pct"] = 0.5
        before = self.combat.enemy.hp
        self.combat.hurt_player(40)
        self.assertEqual(before - self.combat.enemy.hp, 20)
        self.mods["thorns_pct"] = 0.0
        self.mods["damage_reduction_pct"] = -0.25                                 # vulnerabilidade
        hp = self.combat.player.hp
        self.combat.hurt_player(40)
        self.assertEqual(hp - self.combat.player.hp, 50)

    def test_status_resist_shortens_effects(self):
        self.mods["status_resist_pct"] = 0.5
        effects.apply_enemy_ability(self.combat, {"type": "poison", "name": "p", "amount": 1.0, "duration": 8.0})
        effects.apply_enemy_ability(self.combat, {"type": "silence", "name": "s", "duration": 6.0})
        effects.apply_enemy_ability(self.combat, {"type": "weight", "name": "w", "duration": 10.0, "speed": 2.0})
        self.assertAlmostEqual(self.combat.poison_time, 4.0)
        self.assertAlmostEqual(self.combat.silence_time, 3.0)
        self.assertAlmostEqual(self.combat.haste_time, 5.0)
        self.mods["status_resist_pct"] = 9.0                                      # teto de 75%
        effects.apply_enemy_ability(self.combat, {"type": "silence", "name": "s", "duration": 8.0})
        self.assertAlmostEqual(self.combat.silence_time, 3.0)                     # max(3.0, 2.0)

    def test_boss_cooldown_only_vs_bosses(self):
        self.mods["boss_cooldown_pct"] = 0.5
        self.assertEqual(self.combat._slow_pct(), 0.0)
        self.combat.enemy.is_boss = True
        self.assertEqual(self.combat._slow_pct(), 0.5)

    def test_second_wind_once_per_floor(self):
        self.mods["second_wind_pct"] = 0.5
        player = self.combat.player
        player.hp = 5.0
        self.combat.hurt_player(999)
        self.assertIsNone(self.combat.result)
        self.assertEqual(player.hp, player.max_hp * 0.5)
        self.assertTrue(self.combat.second_wind_used)
        self.combat.hurt_player(9999)
        self.assertEqual(self.combat.result, "lose")
        # um novo andar (novo Combat) renova a segunda chance
        self.assertFalse(self.run.start_floor().second_wind_used)

    def test_second_wind_also_saves_from_poison(self):
        self.mods["second_wind_pct"] = 0.4
        self.combat.player.hp = 1.0
        self.combat.poison_time, self.combat.poison_dps = 5.0, 50.0
        self.combat.update(0.1)
        self.assertIsNone(self.combat.result)
        self.assertTrue(self.combat.second_wind_used)

    def test_negative_max_hp_card_keeps_player_alive(self):
        run = RunManager("warrior", self.data, random.Random(1))
        run.player.hp = 5.0
        run.take_reward({"id": "x", "effects": [{"type": "max_hp", "value": -500}]})
        self.assertGreaterEqual(run.player.max_hp, 1)
        self.assertGreaterEqual(run.player.hp, 1.0)

    def test_hud_lines_exist_for_every_new_mod(self):
        run = RunManager("warrior", self.data, random.Random(1))
        for card in [r for r in self.data["rewards"]["rewards"] if r["id"].startswith("i_")]:
            run.take_reward(card)
        text = " | ".join(run.player.mod_lines())
        for word in ("Match 4+", "rápida", "Finalizar", "Abertura", "Impulso", "Por andar", "Esquiva", "Espinhos",
                     "Resist.", "Boss ataca", "Segunda chance", "devolve", "energia", "cura"):
            self.assertIn(word, text, word)


def make_board_with_match(combat):
    from tests.test_logic import make_board
    return make_board(["12345123", "21534215", "34252143", "45123412", "11134512", "23451234", "34512345", "45123451"])


# ======================================================================
# 5) SPRITES
# ======================================================================
class Sprites(Base):
    def test_every_new_entity_has_a_distinct_animated_sprite(self):
        from PIL import Image, ImageSequence
        files = [os.path.join(ROOT, "assets", "images", "enemies", i + ".png") for i in new_enemy_ids(self.data)]
        files += [os.path.join(ROOT, "assets", "images", "bosses", f"boss_inf_{k}.png") for k in self.enemies["infinite_bosses"]]
        self.assertEqual(len(files), 45)
        digests = set()
        for path in files:
            with Image.open(path) as im:
                frames = [f.convert("RGBA") for f in ImageSequence.Iterator(im)]
            self.assertEqual(len(frames), 4, path)
            self.assertIsNotNone(frames[0].getbbox(), path)
            self.assertNotEqual(frames[0].tobytes(), frames[2].tobytes(), f"{path} não está animado")
            alpha = frames[0].getchannel("A")
            self.assertLess(alpha.getpixel((0, 0)), 40, "fundo deve ser transparente")
            digests.add(frames[0].tobytes())
        self.assertEqual(len(digests), 45)

    def test_art_lookup_names_match_what_the_game_loads(self):
        # o jogo procura enemies/<image_id|id|family> e bosses/<image_id|id>: o id é o nome do arquivo
        for i in new_enemy_ids(self.data):
            self.assertEqual(Enemy(i, self.enemies["enemies"][i], {"hp": 1, "damage": 1, "cooldown": 1}).image_id, i)
        for k, d in self.enemies["infinite_bosses"].items():
            self.assertEqual(Boss(f"boss_inf_{k}", d, {"hp": 1, "damage": 1, "cooldown": 1}).image_id, f"boss_inf_{k}")

    def test_fallback_portrait_kind_is_a_known_drawing(self):
        known = {"warrior", "mage", "assassin", "bard", "judge", "cleric", "blacksmith", "archer", "monk", "fairy", "dragon",
                 "zombie", "necromancer", "void", "goblin", "spider", "mage_enemy", "golem"}
        for d in list(self.enemies["enemies"].values())[-30:] + list(self.enemies["infinite_bosses"].values()):
            self.assertIn(d["portrait"], known)
        src = open(os.path.join(ROOT, "ui", "portraits.py"), encoding="utf-8").read()
        for kind in known - {"warrior", "mage", "assassin", "bard", "judge", "cleric", "blacksmith", "archer", "monk"}:
            self.assertIn(f'kind == "{kind}"' if kind != "mage_enemy" else '"mage_enemy"', src)


# ======================================================================
# 6) COMPATIBILIDADE
# ======================================================================
class Compatibility(Base):
    def test_old_content_untouched_and_story_mode_runs(self):
        run = RunManager("warrior", self.data, random.Random(2))
        rng = random.Random(3)
        for floor in range(1, 11):
            run.floor_number = floor
            combat = run.start_floor()
            run.player.max_hp = run.player.hp = 100000
            for _ in range(1500):
                if combat.phase == IDLE:
                    bot_move(combat, rng)
                combat.update(1 / 20)
                combat.pop_events()
                if combat.result:
                    break
            self.assertEqual(combat.result, "win", floor)
            self.assertEqual(combat.enemy.is_boss, floor % 10 == 0)
            run.floor_cleared()

    def test_no_economy_or_shop_added(self):
        text = open(os.path.join(ROOT, "data", "rewards.json"), encoding="utf-8").read().lower()
        import re
<<<<<<< HEAD
        # Loja de PONTOS permanentes existe (fora da run); o que continua proibido é ouro/moeda/inventário DENTRO da run
        for banned in (r"\bgold\b", r"\bouro\b", r"\bmoedas?\b", r"inventári"):
=======
        for banned in (r"\bgold\b", r"\bouro\b", r"\bmoedas?\b", r"\bloja\b", r"\bshop\b", r"inventári"):
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
            self.assertIsNone(re.search(banned, text), banned)
        self.assertFalse({"gold", "coins", "shop"} & set(DEFAULT_MODS))

    def test_floors_json_top_level_only_changed_inside_infinite(self):
        self.assertEqual(self.floors["scaling"]["hp_per_floor"], 0.12)
        self.assertEqual(self.floors["last_floor"], 50)
        self.assertIn("scaling", self.floors["infinite"])


if __name__ == "__main__":
    unittest.main()
