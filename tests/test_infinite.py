"""
tests/test_infinite.py - Modo Infinito: andares aleatórios, bosses (inclusive personagens),
desbloqueio e salvamento.

Rodar:  python -m unittest tests.test_infinite -v
"""
import os
import random
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
for _var in ("APPDATA", "XDG_DATA_HOME", "HOME", "USERPROFILE"):   # saves de teste, não mexe nos seus (Windows usa APPDATA)
    os.environ[_var] = tempfile.mkdtemp()

from combat.combat import IDLE
from game.save import Progress
from run.floor import build_infinite_floor
from run.run_manager import RunManager
from tests.test_logic import bot_move, load_data


class InfiniteFloors(unittest.TestCase):
    def setUp(self):
        self.data = load_data()

    def build(self, floor, seed=1, own=None):
        # (todos os personagens ainda bloqueados: só os bloqueados aparecem como chefes de desbloqueio)
        return build_infinite_floor(floor, self.data["enemies"], self.data["floors"], random.Random(seed), own,
                                    self.data["characters"], list(self.data["characters"]))

    def test_any_floor_builds_forever(self):
        for floor in list(range(1, 130)) + [500, 1000]:
            f = self.build(floor, seed=floor)
            self.assertEqual(f.is_boss, floor % 10 == 0)
            self.assertGreater(f.enemy.hp, 0)

    def test_monsters_are_random(self):
        seen = {self.build(5, seed=s).enemy.id for s in range(80)}
        self.assertGreater(len(seen), 1)

    def test_early_floors_only_use_unlocked_themes(self):
        spiders = {e["id"] for e in self.data["floors"]["groups"][0]["enemies"]}
        # exclusivos do Infinito ativos no andar 3 (Fada e os da expansão que já começaram): vêm dos dados
        spiders |= {e["id"] for e in self.data["floors"]["infinite"]["exclusive_enemies"]
                    if e.get("from_floor", 1) <= 3 <= e.get("to_floor", 10 ** 9)}
        self.assertIn("fairy", spiders)
        for seed in range(60):
            self.assertIn(self.build(3, seed).enemy.id, spiders)
        for seed in range(300):                  # temas ainda bloqueados NUNCA aparecem no andar 3
            self.assertFalse(self.build(3, seed).enemy.id.startswith(("goblin", "mage", "golem", "void_")))
        late = {self.build(45, seed).enemy.id for seed in range(300)}
        self.assertTrue(any(i.startswith("void_") for i in late))
        self.assertTrue(any(i.startswith("goblin") or i == "goblin" for i in late))

    def test_bosses_are_random_and_can_be_playable_characters(self):
        ids = {self.build(60, seed).enemy.id for seed in range(200)}
        self.assertTrue(any(i.startswith("boss_char_") for i in ids))
        self.assertTrue(any(i.startswith("boss_") and not i.startswith("boss_char_") for i in ids))

    def test_first_boss_floor_uses_only_unlocked_story_boss(self):
        ids = {self.build(10, s).enemy.id for s in range(400)}
        story = {i for i in ids if i.split("_")[-1].isdigit()}          # chefes da história: boss_10, boss_20...
        self.assertEqual(story, {"boss_10"})
        # chefes exclusivos do Infinito só entram a partir do seu min_floor
        for i in ids - story:
            self.assertTrue(i.startswith("boss_inf_"), i)
            self.assertLessEqual(self.data["enemies"]["infinite_bosses"][i[len("boss_inf_"):]]["min_floor"], 10)

    def test_own_character_is_not_a_boss(self):
        for seed in range(150):
            self.assertNotEqual(self.build(30, seed, own="warrior").enemy.id, "boss_char_warrior")

    def test_character_boss_has_art_info(self):
        for seed in range(300):
            enemy = self.build(40, seed).enemy
            if enemy.id.startswith("boss_char_"):
                self.assertEqual(enemy.art_folder, "characters")
                self.assertTrue(enemy.is_boss)
                return
        self.fail("nenhum boss-personagem sorteado")


class InfiniteRun(unittest.TestCase):
    def setUp(self):
        self.data = load_data()

    def test_run_never_finishes(self):
        run = RunManager("bard", self.data, random.Random(1), mode="infinite")
        self.assertIsNone(run.last_floor)
        run.floor_number = 50
        run.start_floor()
        run.floor_cleared()
        self.assertFalse(run.finished)
        run.floor_number = 300
        run.floor_cleared()
        self.assertFalse(run.finished)

    def test_story_run_still_finishes_at_last_floor(self):
        run = RunManager("warrior", self.data, random.Random(1))
        run.floor_number = run.last_floor
        run.floor_cleared()
        self.assertTrue(run.finished)

    def test_bot_plays_infinite_floors_including_character_boss(self):
        for char in ("warrior", "assassin"):
            rng = random.Random(8)
            run = RunManager(char, self.data, rng, mode="infinite")
            for floor in (1, 2, 10, 20, 30):
                run.floor_number = floor
                combat = run.start_floor()
                guard = 0
                while not combat.result and guard < 20000:
                    guard += 1
                    if combat.phase == IDLE:
                        if combat.player.can_use_ability():
                            combat.use_ability()
                        else:
                            bot_move(combat, rng)
                    combat.update(1 / 20)
                    combat.pop_events()
                self.assertIsNotNone(combat.result)
                if combat.result == "lose":
                    break
                run.floor_cleared()
                run.take_reward(run.roll_rewards()[0])


class InfiniteUnlock(unittest.TestCase):
    def test_locked_until_victory_then_saved(self):
        data = load_data()
        progress = Progress(data["characters"])
        progress.path = type(progress.path)(tempfile.mkdtemp()) / "progress.json"
        progress.infinite_unlocked = False
        progress.wins = 0
        self.assertFalse(progress.is_infinite_unlocked())
        self.assertTrue(progress.unlock_infinite())          # primeira vez
        self.assertFalse(progress.unlock_infinite())         # segunda vez: não é "novo"
        progress.record_infinite_floor(17)
        progress.save()
        again = Progress(data["characters"])
        again.path = progress.path
        again.load()
        self.assertTrue(again.is_infinite_unlocked())
        self.assertEqual(again.best_infinite_floor, 17)

    def test_old_save_with_a_win_unlocks_infinite(self):
        import json
        data = load_data()
        progress = Progress(data["characters"])
        path = type(progress.path)(tempfile.mkdtemp()) / "progress.json"
        path.write_text(json.dumps({"best_floor": 50, "runs": 3, "wins": 1}), encoding="utf-8")
        progress.path = path
        progress.infinite_unlocked = False
        progress.load()
        self.assertTrue(progress.is_infinite_unlocked())

    def test_fresh_save_is_locked(self):
        import json
        data = load_data()
        progress = Progress(data["characters"])
        path = type(progress.path)(tempfile.mkdtemp()) / "progress.json"
        path.write_text(json.dumps({"best_floor": 12, "runs": 2, "wins": 0}), encoding="utf-8")
        progress.path = path
        progress.infinite_unlocked = False
        progress.load()
        self.assertFalse(progress.infinite_unlocked)


if __name__ == "__main__":
    unittest.main()
