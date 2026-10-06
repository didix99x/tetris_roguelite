"""
tests/test_logic.py - testes da LÓGICA do jogo (sem janela, sem pygame).

Como rodar (na pasta do projeto):
    python -m unittest tests.test_logic -v
"""
import json
import os
import random
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from board.block import Block
from board.board import Board
from board.matcher import find_matches
from combat import damage
from combat.combat import Combat, IDLE
from run.run_manager import RunManager


def load_data():
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
    out = {}
    for name in ("characters", "enemies", "floors", "rewards"):
        with open(os.path.join(base, name + ".json"), encoding="utf-8") as f:
            out[name] = json.load(f)
    return out


def make_board(rows):
    """Cria um Board a partir de linhas de dígitos (0 = vazio, 6 = pedra)."""
    board = Board(len(rows[0]), len(rows), random.Random(1))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            n = int(ch)
            if n == 0:
                board.grid[y][x] = None
            elif n == 6:
                board.grid[y][x] = Block(6, x, y, "stone")
            else:
                board.grid[y][x] = Block(n, x, y)
    return board


def run_until_idle(combat, limit=2000):
    for _ in range(limit):
        combat.update(1 / 60)
        if combat.phase == IDLE or combat.result:
            return
    raise AssertionError("o puzzle não terminou de resolver (loop infinito?)")


def bot_move(combat, rng):
    """Bot simples: procura uma troca que forme match; senão troca algo."""
    b = combat.board
    for y in range(b.height):
        for x in range(b.width - 1):
            if b.can_swap(x, y):
                a, c = b.grid[y][x], b.grid[y][x + 1]
                b.grid[y][x], b.grid[y][x + 1] = c, a
                found = bool(b.find_matches())
                b.grid[y][x], b.grid[y][x + 1] = a, c
                if found:
                    b.set_cursor(x, y)
                    return combat.try_swap()
    for _ in range(20):
        b.set_cursor(rng.randrange(b.width - 1), rng.randrange(b.height))
        if combat.try_swap():
            return True
    return False


class MatcherTests(unittest.TestCase):
    def test_horizontal_and_vertical(self):
        board = make_board(["11123", "24523", "35423", "45134"])
        matches = find_matches(board.grid, 5, 4)
        sizes = sorted((m.direction, m.length) for m in matches)
        self.assertIn(("h", 3), sizes)
        self.assertIn(("v", 3), sizes)

    def test_two_is_not_a_match(self):
        board = make_board(["1123", "2312", "3231"])
        self.assertEqual(find_matches(board.grid, 4, 3), [])

    def test_stone_never_matches(self):
        board = make_board(["666", "123", "231"])
        self.assertEqual(find_matches(board.grid, 3, 3), [])


class BoardTests(unittest.TestCase):
    def test_initial_board_full_and_without_matches(self):
        for seed in range(30):
            board = Board(rng=random.Random(seed))
            self.assertEqual(sum(1 for _ in board.blocks()), 64)
            self.assertEqual(board.find_matches(), [])
            self.assertTrue(board.has_possible_move())

    def test_swap(self):
        board = make_board(["12", "21"])
        board.set_cursor(0, 0)
        self.assertTrue(board.swap_cursor())
        self.assertEqual(board.grid[0][0].color_id, 2)
        self.assertEqual(board.grid[0][0].grid_x, 0)
        self.assertEqual(board.grid[0][1].grid_x, 1)

    def test_cannot_swap_web_or_stone(self):
        board = make_board(["16", "21"])
        board.set_cursor(0, 0)
        self.assertFalse(board.swap_cursor())
        board = make_board(["12", "21"])
        board.grid[0][0].web_time = 5
        board.set_cursor(0, 0)
        self.assertFalse(board.swap_cursor())

    def test_gravity_and_refill(self):
        board = Board(rng=random.Random(3))
        top = board.grid[0][2]
        board.grid[7][2] = None
        board.gravity_and_refill()
        self.assertEqual(sum(1 for _ in board.blocks()), 64)
        self.assertEqual(top.grid_y, 1)
        self.assertLess(board.grid[0][2].visual_y, 0)

    def test_stone_removed_by_adjacent_match(self):
        board = make_board(["111", "666"])
        removed = board.remove_cells({(0, 0), (1, 0), (2, 0)})
        self.assertEqual(len(removed), 6)


class DamageTests(unittest.TestCase):
    def test_table(self):
        self.assertEqual(damage.calculate_damage([3], 1), 10)
        self.assertEqual(damage.calculate_damage([4], 1), 18)
        self.assertEqual(damage.calculate_damage([5], 1), 28)
        self.assertEqual(damage.calculate_damage([3], 2), 15)
        self.assertEqual(damage.calculate_damage([3], 3), 20)
        self.assertEqual(damage.calculate_damage([3], 4), 25)
        self.assertEqual(damage.calculate_damage([3], 5), 30)
        self.assertEqual(damage.calculate_damage([6], 1), 34)


class CombatTests(unittest.TestCase):
    def setUp(self):
        self.data = load_data()

    def test_player_match_damages_enemy_and_chain_works(self):
        run = RunManager("warrior", self.data, random.Random(5))
        combat = run.start_floor()
        # Monta um tabuleiro manual: trocar (2,0)<->(3,0) cria 111 na linha 0
        # e, depois da queda, deixa tudo previsível.
        combat.board = make_board(["12134555", "34512345", "45123451", "51234512",
                                   "23451234", "34512345", "45123451", "51234512"])
        combat.board.set_cursor(1, 0)
        hp_before = combat.enemy.hp
        self.assertTrue(combat.try_swap())
        run_until_idle(combat)
        self.assertLess(combat.enemy.hp, hp_before)
        events = combat.pop_events()
        self.assertTrue(any(e["type"] == "match" for e in events))

    def test_enemy_attacks_and_hurts_player(self):
        run = RunManager("warrior", self.data, random.Random(7))
        combat = run.start_floor()
        start = combat.player.hp
        for _ in range(60 * 12):
            combat.update(1 / 60)
        self.assertLess(combat.player.hp, start)

    def test_bot_can_clear_floors_and_state_stays_valid(self):
        """Joga com um bot vários andares (inclui bosses) sem travar."""
        for char in ("warrior", "mage", "assassin", "bard"):
            rng = random.Random(11)
            run = RunManager(char, self.data, rng)
            run.data["floors"]["last_floor"] = 50
            for floor in range(1, 51):
                run.floor_number = floor
                combat = run.start_floor()
                guard = 0
                while not combat.result and guard < 60 * 60 * 6:
                    guard += 1
                    if combat.phase == IDLE:
                        if combat.player.can_use_ability():
                            combat.use_ability()
                        else:
                            bot_move(combat, rng)
                    combat.update(1 / 20)
                    combat.pop_events()
                    self.assertEqual(sum(1 for _ in combat.board.blocks()), 64)
                self.assertIsNotNone(combat.result, f"{char} andar {floor} não terminou")
                if combat.result == "lose":
                    break
                run.floor_cleared()
                for reward in run.roll_rewards():
                    pass
                run.take_reward(run.roll_rewards()[0])

    def test_rewards_apply(self):
        run = RunManager("warrior", self.data, random.Random(2))
        p = run.player
        for reward in self.data["rewards"]["rewards"]:
            p.apply_reward(reward)
        self.assertGreater(p.max_hp, 120)
        self.assertGreaterEqual(p.mods["chain_start"], 1)
        self.assertTrue(p.mod_lines())

    def test_bard_heals_and_ability_cleanses(self):
        run = RunManager("bard", self.data, random.Random(9))
        combat = run.start_floor()
        combat.player.hp = 50.0
        # cria teia e pedra e usa a habilidade
        blocks = list(combat.board.blocks())
        blocks[0].web_time = 9.0
        blocks[1].kind = "stone"
        blocks[1].color_id = config.STONE_COLOR_ID
        combat.player.energy = 100
        combat.enemy_timer = 2.0
        self.assertTrue(combat.use_ability())
        run_until_idle(combat)
        self.assertEqual(combat.board.count_stones(), 0)
        self.assertEqual(combat.board.count_webbed(), 0)
        self.assertGreaterEqual(combat.enemy_timer, 6.0)
        # passiva: um match cura
        combat.board = make_board(["12134555", "34512345", "45123451", "51234512",
                                   "23451234", "34512345", "45123451", "51234512"])
        combat.board.set_cursor(1, 0)
        hp_before = combat.player.hp
        combat.try_swap()
        run_until_idle(combat)
        self.assertGreater(combat.player.hp, hp_before)

    def test_all_boss_floors_build(self):
        run = RunManager("warrior", self.data, random.Random(2))
        for floor in (10, 20, 30, 40, 50):
            run.floor_number = floor
            run.start_floor()
            self.assertTrue(run.floor.is_boss)
            self.assertTrue(run.floor.enemy.is_boss)


if __name__ == "__main__":
    unittest.main()
