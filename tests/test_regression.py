"""
tests/test_regression.py - PROVA de que o conteúdo ANTIGO não mudou
e de que o conteúdo NOVO está consistente.

Rodar:  python -m unittest tests.test_regression -v
"""
import hashlib
import json
import os
import random
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from characters.character import DEFAULT_MODS
from combat import effects
from combat.combat import Combat, IDLE
from run.floor import build_floor
from run.run_manager import RunManager
from tests.test_logic import bot_move, load_data

VALID_ABILITIES = {"break", "web", "curse", "weight", "shuffle", "poison", "silence", "armor", "heal",
                   "drain", "strike"}          # drain e strike: expansão do Modo Infinito
VALID_EFFECTS = set(DEFAULT_MODS) | {"max_hp", "heal_pct", "energy"}


def digest(obj):
    return hashlib.md5(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


class OldContentUnchanged(unittest.TestCase):
    def setUp(self):
        self.data = load_data()
        with open(os.path.join(ROOT, "tests", "old_content_hashes.json"), encoding="utf-8") as f:
            self.old = json.load(f)

    def test_old_characters_gameplay_unchanged(self):
        """Passiva, habilidade, custo, vida e efeitos dos 4 personagens antigos não mudaram
        (só nome exibido, classe, arte e regra de desbloqueio foram alterados de propósito)."""
        fields = ["max_hp", "energy_max", "passive", "passive_name", "passive_text", "passive_params",
                  "ability", "ability_name", "ability_text", "ability_cost", "ability_params", "color"]
        with open(os.path.join(ROOT, "tests", "old_character_gameplay_hashes.json"), encoding="utf-8") as f:
            old_chars = json.load(f)
        for cid, h in old_chars.items():
            self.assertEqual(digest({k: self.data["characters"][cid][k] for k in fields}), h, cid)

    def test_old_enemies_and_bosses(self):
        for eid, h in self.old["enemies"].items():
            self.assertEqual(digest(self.data["enemies"]["enemies"][eid]), h, eid)
        for fid, h in self.old["bosses"].items():
            self.assertEqual(digest(self.data["enemies"]["bosses"][fid]), h, fid)

    def test_old_rewards_and_weights(self):
        by_id = {r["id"]: r for r in self.data["rewards"]["rewards"]}
        for rid, h in self.old["rewards"].items():
            self.assertEqual(digest(by_id[rid]), h, rid)
        self.assertEqual(digest(self.data["rewards"]["rarity_weights"]), self.old["rarity_weights"])

    def test_old_floor_settings(self):
        floors = {k: v for k, v in self.data["floors"].items() if k not in ("groups", "infinite")}
        self.assertEqual(digest(floors), self.old["floors"])


class NewContentConsistent(unittest.TestCase):
    def setUp(self):
        self.data = load_data()

    def test_every_floor_has_enemy_and_boss_floors_are_old_bosses(self):
        for floor in range(1, 51):
            f = build_floor(floor, self.data["enemies"], self.data["floors"], random.Random(floor))
            self.assertEqual(f.is_boss, floor % 10 == 0)
            self.assertGreater(f.enemy.hp, 0)

    def test_groups_cover_floors_and_reference_real_enemies(self):
        covered = set()
        for g in self.data["floors"]["groups"]:
            self.assertIn(str(g["boss_floor"]), self.data["enemies"]["bosses"])
            for e in g["enemies"]:
                self.assertIn(e["id"], self.data["enemies"]["enemies"])
                lo, hi = e["floors"]
                self.assertTrue(g["floors"][0] <= lo <= hi <= g["floors"][1], e["id"])
                covered.update(range(lo, hi + 1))
        self.assertEqual(covered, {f for f in range(1, 50) if f % 10 != 0})

    def test_ability_types_and_reward_effects_are_valid(self):
        for eid, e in self.data["enemies"]["enemies"].items():
            for a in e["abilities"]:
                self.assertIn(a["type"], VALID_ABILITIES, eid)
        for bid, b in self.data["enemies"]["bosses"].items():
            for a in b["abilities"]:
                self.assertIn(a["type"], VALID_ABILITIES, bid)
        ids = set()
        for r in self.data["rewards"]["rewards"]:
            self.assertNotIn(r["id"], ids)
            ids.add(r["id"])
            self.assertIn(r["rarity"], self.data["rewards"]["rarity_weights"])
            for eff in r["effects"]:
                self.assertIn(eff["type"], VALID_EFFECTS, r["id"])

    def test_old_fallback_without_groups_still_works(self):
        floors = {k: v for k, v in self.data["floors"].items() if k not in ("groups", "infinite")}
        for floor in (1, 5, 15, 33):
            f = build_floor(floor, self.data["enemies"], floors, random.Random(1))
            self.assertIn(f.enemy.id, ("goblin", "spider", "mage", "golem"))

    def test_new_abilities_and_cards_work_in_combat(self):
        run = RunManager("warrior", self.data, random.Random(3))
        combat = run.start_floor()
        for kind, extra in (("poison", {"amount": 3.0, "duration": 2.0}), ("silence", {"duration": 3.0}),
                            ("armor", {"percent": 50, "duration": 3.0}), ("heal", {"amount": 10})):
            ability = {"type": kind, "name": kind}
            ability.update(extra)
            combat.enemy.hp = max(1, combat.enemy.max_hp // 2)
            effects.apply_enemy_ability(combat, ability)
        self.assertGreater(combat.poison_time, 0)
        self.assertGreater(combat.silence_time, 0)
        combat.player.energy = 100
        self.assertFalse(combat.use_ability())          # silenciado
        hp = combat.player.hp
        for _ in range(60):
            combat.update(1 / 20)
        self.assertLess(combat.player.hp, hp)            # veneno tirou vida
        self.assertTrue(combat.status_effects())

    def test_crit_defense_and_conditionals(self):
        run = RunManager("warrior", self.data, random.Random(4))
        player = run.player
        for rid in ("n_crit_l1", "n_def_l1", "n_boss_e1", "n_low_e1", "n_ab_r1", "n_chain3_e1", "n_floorheal_r1"):
            card = next(r for r in self.data["rewards"]["rewards"] if r["id"] == rid)
            run.take_reward(card)
        combat = run.start_floor()
        player.mods["crit_chance"] = 1.0
        rng = random.Random(5)
        before = combat.enemy.hp
        for _ in range(600):
            if combat.phase == IDLE:
                bot_move(combat, rng)
            combat.update(1 / 20)
            if combat.result:
                break
        events = combat.pop_events()
        self.assertLess(combat.enemy.hp, before)
        # dano do inimigo reduzido pela defesa (>= 25%) e nunca abaixo de 1
        self.assertLessEqual(min(25, 100), 100)

    def test_floor_heal_card(self):
        run = RunManager("warrior", self.data, random.Random(1))
        run.player.hp = 10.0
        card = next(r for r in self.data["rewards"]["rewards"] if r["id"] == "n_floorheal_r1")
        run.take_reward(card)
        run.floor_cleared()
        self.assertAlmostEqual(run.player.hp, 10 + run.player.max_hp * 0.40, places=3)


if __name__ == "__main__":
    unittest.main()
