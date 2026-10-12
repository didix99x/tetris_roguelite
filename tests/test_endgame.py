"""
tests/test_endgame.py - Modo Infinito depois do andar 100: Fúria do Vazio, super chefes, tela de desbloqueio e Tali.

    python -m unittest tests.test_endgame -v
"""
import math
import os
import random
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tests import visual_harness  # noqa: F401  (instala pygame ou o mini-pygame ANTES de importar ui/)
import pygame

from bosses.yoshi import YoshiBoss
from game.state import GameState
from run.floor import (_infinite_stats, build_infinite_floor, build_special_boss, super_boss_kind, _character_enemy_data)
from run.progression import apply_void_fury, scale_stats_infinite
from tests.test_logic import load_data
from tests.test_yoshi import _game
from ui import portraits
from ui.unlock_screen import ANIMATION_TIME, UnlockScreen
from ui.void_fury_screen import BUTTONS_AT, VoidFuryScreen

ALL_CHARS = {"warrior", "mage", "assassin", "bard", "judge", "cleric", "blacksmith", "archer", "monk"}


class FakeInput:
    def __init__(self, swap=False, click=None, back=False, mouse=(0, 0), down=False):
        self.swap, self.click, self.back, self.mouse_pos, self.down = swap, click, back, mouse, down

    def pressed(self, name):
        return {"swap": self.swap, "back": self.back, "down": self.down}.get(name, False)


def surface():
    return pygame.Surface((1280, 720))


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.e, cls.f, cls.c = cls.data["enemies"], cls.data["floors"], cls.data["characters"]

    def build(self, floor, seed=1, own="judge", state=None):
        return build_infinite_floor(floor, self.e, self.f, random.Random(seed), own, self.c, list(self.c), super_state=state)


# ======================================================================
class SuperBossProgression(Base):
    def test_yoshi_stays_the_floor_100_boss_with_original_stats(self):
        fl = self.build(100)
        self.assertIsInstance(fl.enemy, YoshiBoss)
        self.assertEqual(fl.enemy.id, "boss_yoshi_supreme")
        self.assertEqual(fl.enemy.name, self.e["yoshi"]["infinite"]["name"])
        legacy = scale_stats_infinite(self.e["yoshi"]["infinite"], 100, self.f["scaling"], self.f["infinite"], None)
        self.assertEqual((fl.enemy.max_hp, fl.enemy.damage), (legacy["hp"], legacy["damage"]))      # sem Fúria do Vazio

    def test_floor_105_is_an_existing_super_boss_not_a_playable_character(self):
        for seed in range(30):
            enemy = self.build(105, seed=seed).enemy
            self.assertTrue(enemy.is_boss and enemy.is_super, enemy.id)
            self.assertTrue(enemy.id.startswith("boss_inf_"), enemy.id)
            self.assertIsNone(getattr(enemy, "character_id", None))
            self.assertIn(enemy.id[len("boss_inf_"):], self.e["infinite_bosses"])

    def test_playable_characters_become_super_bosses_only_from_110(self):
        for floor in range(101, 110):                       # nada de personagem antes do 110
            enemy = self.build(floor, own="none").enemy
            self.assertIsNone(getattr(enemy, "character_id", None), floor)
        enemy = self.build(110, own="none").enemy
        self.assertTrue(enemy.is_boss and enemy.is_super)
        self.assertIn(enemy.character_id, ALL_CHARS)

    def test_a_super_boss_every_5_floors_forever(self):
        state = {"cycle": [], "by_floor": {}}
        for floor in list(range(101, 400)) + [1000, 1005, 5000, 100005]:
            kind = super_boss_kind(floor, self.e, self.f)
            fl = self.build(floor, seed=floor, state=state)
            self.assertEqual(fl.is_boss, floor % 5 == 0, floor)
            self.assertEqual(kind is not None, floor % 5 == 0, floor)
            if floor % 5 == 0:
                self.assertTrue(fl.enemy.is_super, floor)
                self.assertEqual(kind, "existing" if floor == 105 else "character", floor)

    def test_before_100_the_boss_floors_are_unchanged(self):
        for floor in range(1, 100):
            self.assertIsNone(super_boss_kind(floor, self.e, self.f))
            fl = self.build(floor, seed=floor)
            self.assertEqual(fl.is_boss, floor % 10 == 0, floor)
            if fl.is_boss:                                   # nenhum personagem vira SUPER antes do 110
                self.assertFalse(getattr(fl.enemy, "is_super", False) and getattr(fl.enemy, "character_id", None), floor)

    def test_characters_rotate_without_repeating_until_all_appeared(self):
        state = {"cycle": [], "by_floor": {}}
        order = [self.build(f, seed=f, own="judge", state=state).enemy.character_id for f in range(110, 110 + 5 * 24, 5)]
        pool = ALL_CHARS - {"judge"}                         # o personagem da run nunca é o chefe
        for start in range(0, len(order), len(pool)):
            block = order[start:start + len(pool)]
            if len(block) == len(pool):
                self.assertEqual(set(block), pool, order)
        self.assertNotIn("judge", order)

    def test_same_floor_gives_the_same_character_when_rebuilt(self):
        state = {"cycle": [], "by_floor": {}}
        first = self.build(110, seed=1, state=state).enemy.character_id
        again = self.build(110, seed=2, state=state).enemy.character_id
        self.assertEqual(first, again)
        self.assertEqual(len(state["cycle"]), 1)

    def test_character_super_bosses_keep_name_identity_and_have_own_kit(self):
        for cid in sorted(ALL_CHARS):
            enemy = self.build(115, seed=3, own="none", state={"cycle": [c for c in ALL_CHARS if c != cid], "by_floor": {}}).enemy
            self.assertEqual(enemy.character_id, cid)
            self.assertIn(self.c[cid]["name"], enemy.name)
            self.assertEqual(enemy.image_id, self.c[cid]["image"])
            base_types = [a["type"] for a in self.e["character_bosses"][cid]["abilities"]]
            self.assertGreater(len(enemy.abilities), len(base_types))        # kit normal + habilidades próprias do super
            self.assertTrue(enemy.mechanics.get("phase_three_hp") or enemy.mechanics.get("enrage_hp"))

    def test_super_bosses_use_run_rotation_through_the_run_manager(self):
        from run.run_manager import RunManager
        run = RunManager("judge", self.data, random.Random(5), mode="infinite")
        seen = []
        for floor in (105, 110, 115, 120):
            run.floor_number = floor
            run.start_floor()
            run.start_floor()                                  # reconstruir o mesmo andar não gasta o rodízio
            seen.append(getattr(run.floor.enemy, "character_id", None))
        self.assertIsNone(seen[0])
        self.assertEqual(len({s for s in seen[1:]}), 3)


# ======================================================================
class VoidFuryDifficulty(Base):
    def stats(self, floor, data=None, boss=False):
        data = data or self.e["enemies"]["goblin_warrior"]
        return _infinite_stats(data, floor, self.f, None, None, boss)

    def test_common_enemies_have_at_least_10000_hp_from_floor_100(self):
        ids = list(self.e["enemies"])
        for floor in (100, 101, 104, 106, 150, 199, 200, 350, 1000, 12345):
            for eid in ids:
                self.assertGreaterEqual(self.stats(floor, self.e["enemies"][eid])["hp"], 10000, (floor, eid))

    def test_built_floors_have_10000_hp_in_real_runs(self):
        from characters import create_character
        player = create_character("judge", self.c["judge"])
        for floor in (101, 102, 103, 104, 106, 107, 108, 109, 111, 150, 204):
            fl = build_infinite_floor(floor, self.e, self.f, random.Random(floor), "judge", self.c, [], player, self.c["judge"]["max_hp"])
            self.assertGreaterEqual(fl.enemy.max_hp, 10000, (floor, fl.enemy.id))
        for floor in (105, 110, 200):
            fl = build_infinite_floor(floor, self.e, self.f, random.Random(floor), "judge", self.c, [], player, self.c["judge"]["max_hp"])
            self.assertGreaterEqual(fl.enemy.max_hp, 25000, (floor, fl.enemy.id))      # chefes: bem mais que os comuns

    def test_difficulty_grows_every_floor_and_jumps_every_100(self):
        previous = self.stats(100)
        for floor in range(101, 400):
            now = self.stats(floor)
            self.assertGreater(now["hp"], previous["hp"], floor)
            self.assertGreaterEqual(now["damage"], previous["damage"], floor)
            if floor % 100 == 0:                                                   # marco: salto enorme
                self.assertGreater(now["hp"], previous["hp"] * 4, floor)
                self.assertGreater(now["damage"], previous["damage"] * 1.8, floor)
            else:
                self.assertLess(now["hp"], previous["hp"] * 1.5, floor)
            previous = now

    def test_200_300_400_are_much_harder_than_the_floors_before(self):
        for milestone in (200, 300, 400, 500):
            before, after = self.stats(milestone - 1), self.stats(milestone)
            self.assertGreater(after["hp"], 4 * before["hp"])

    def test_super_bosses_scale_with_the_current_floor(self):
        data = self.e["infinite_bosses"]["lich_king"]
        values = [self.stats(f, data, True)["hp"] for f in (105, 155, 205, 305, 505)]
        self.assertEqual(values, sorted(values))
        self.assertEqual(len(set(values)), 5)
        char = _character_enemy_data("mage", self.e["character_bosses"]["mage"], self.c, self.e["super_character_bosses"]["mage"])
        chars = [self.stats(f, char, True)["hp"] for f in (110, 160, 210, 310)]
        self.assertEqual(chars, sorted(chars))
        self.assertGreater(chars[0], self.stats(110, self.e["enemies"]["goblin"])["hp"] * 2)

    def test_special_boss_also_gets_the_fury(self):
        fl = build_special_boss(150, self.e, self.f, random.Random(3), "judge", self.c, list(self.c))
        self.assertGreaterEqual(fl.enemy.max_hp, 25000)

    def test_numbers_stay_valid_for_absurd_floors(self):
        cfg = self.f["infinite"]["void_fury"]
        for floor in (10 ** 3, 10 ** 4, 10 ** 6, 10 ** 9, 10 ** 15):
            for boss in (False, True):
                s = apply_void_fury({"hp": 1500, "damage": 40, "cooldown": 4.0, "ability_bonus": 6}, floor, cfg, None, boss, boss)
                for key in ("hp", "damage"):
                    self.assertIsInstance(s[key], int)
                    self.assertTrue(1 <= s[key] <= 10 ** 15)
                self.assertTrue(math.isfinite(s["cooldown"]) and s["cooldown"] >= 2.5)
                self.assertLessEqual(s["ability_bonus"], cfg["ability_bonus_cap"])
        s = apply_void_fury({"hp": 0, "damage": 0, "cooldown": 1.0, "ability_bonus": 0}, 150, cfg)
        self.assertGreaterEqual(s["hp"], 10000)

    def test_floors_before_100_are_untouched(self):
        cfg = self.f["infinite"]["void_fury"]
        for floor in range(1, 100):
            for eid in ("goblin", "spider_venom", "dragon", "void_horror"):
                data = self.e["enemies"][eid]
                legacy = scale_stats_infinite(data, floor, self.f["scaling"], self.f["infinite"], None)
                self.assertEqual(self.stats(floor, data), legacy, (floor, eid))
        self.assertEqual(apply_void_fury({"hp": 5, "damage": 5, "cooldown": 5.0}, 99, cfg), {"hp": 5, "damage": 5, "cooldown": 5.0})

    def test_story_mode_is_not_affected(self):
        from run.floor import build_floor
        from run.progression import scale_stats
        for floor in range(1, 51):
            fl = build_floor(floor, self.e, self.f, random.Random(floor))
            if fl.enemy.id == "boss_yoshi":
                continue
            data = (self.e["enemies"].get(fl.enemy.id) or self.e["bosses"].get(fl.enemy.id.replace("boss_", "")))
            self.assertEqual(fl.enemy.max_hp, scale_stats(data, floor, self.f["scaling"])["hp"], floor)


# ======================================================================
class VoidFuryEvent(Base):
    def yoshi_game(self):
        game = _game(self.data, "judge", mode="infinite", floor=100)
        game.run.start_floor()
        return game

    def test_event_is_not_shown_before_or_during_the_yoshi_fight(self):
        game = self.yoshi_game()
        self.assertEqual(game.void_fury_milestone(), 0)               # durante o combate
        game.run.floor.enemy.hp = 0
        game.on_battle_won()                                          # derrotou: cartas lendárias primeiro
        self.assertNotEqual(game.state, GameState.VOID_FURY)
        if game.state == GameState.UNLOCK:                            # (Yoshi desbloqueado: tela própria antes das cartas)
            game.state, game.state_args = game.state_args["next_state"], game.state_args["next_kwargs"]
        for _ in range(3):
            self.assertEqual(game.state, GameState.REWARD)            # as 3 cartas lendárias vêm ANTES do evento
            game.on_reward_chosen(game.state_args["rewards"][0])
        self.assertEqual(game.state, GameState.VOID_FURY)             # só depois de concluir o andar 100
        self.assertEqual(game.state_args["milestone"], 100)
        self.assertEqual(game.run.floor_number, 100)                  # não avançou sozinho
        self.assertGreaterEqual(game.progress.best_infinite_floor, 100)   # conclusão registrada ANTES da tela

    def test_other_floors_never_show_it(self):
        for floor in (1, 40, 99, 101, 105, 110, 150, 199, 250):
            game = _game(self.data, "judge", mode="infinite", floor=floor)
            game.progress.best_infinite_floor = floor
            self.assertEqual(game.void_fury_milestone(), 0, floor)
        story = _game(self.data, "judge", mode="story", floor=50)
        self.assertEqual(story.void_fury_milestone(), 0)

    def test_continue_goes_to_101_and_does_not_repeat(self):
        game = self.yoshi_game()
        game.progress.best_infinite_floor = 100
        game.state_args = {}
        game.on_void_fury_choice(True)
        self.assertEqual(game.run.floor_number, 101)
        self.assertEqual(game.state, GameState.BATTLE)
        game.run.floor_number = 100                                   # mesmo marco de novo: não repete
        self.assertEqual(game.void_fury_milestone(), 0)

    def test_event_returns_at_200_300_and_400(self):
        game = _game(self.data, "judge", mode="infinite", floor=100)
        for milestone in (100, 200, 300, 400):
            game.run.floor_number = milestone
            game.progress.best_infinite_floor = milestone
            self.assertEqual(game.void_fury_milestone(), milestone)
            game.run.void_fury_shown.add(milestone)
            self.assertEqual(game.void_fury_milestone(), 0)

    def test_give_up_ends_the_attempt_and_keeps_permanent_progress(self):
        game = self.yoshi_game()
        game.run.floor.enemy.hp = 0
        game.on_battle_won()
        points, unlocked, best = game.progress.points, game.progress.is_unlocked("yoshi"), game.progress.best_infinite_floor
        runs = game.progress.runs
        game.run.floor_number = 100
        game.on_void_fury_choice(False)
        self.assertIsNone(game.run)
        self.assertEqual(game.state, GameState.MENU)
        self.assertEqual((game.progress.points, game.progress.is_unlocked("yoshi"), game.progress.best_infinite_floor), (points, unlocked, best))
        self.assertTrue(unlocked)
        self.assertEqual(game.progress.runs, runs + 1)
        from game.save import Progress
        again = Progress(self.data["characters"])
        again.path = game.progress.path
        again.load()
        self.assertTrue(again.is_unlocked("yoshi"))
        self.assertGreaterEqual(again.best_infinite_floor, 100)

    # ------------------------------------------------ a tela em si
    def make_screen(self):
        game = self.yoshi_game()
        game.progress.best_infinite_floor = 100
        game.state_args = {}
        return game, VoidFuryScreen(game, 100)

    def test_screen_shows_the_required_message_and_covers_everything(self):
        game, screen = self.make_screen()
        canvas = surface()
        canvas.fill((1, 254, 3))                                      # cor de "sentinela": nada pode sobrar
        for t in (0.0, 1.0, 2.5, BUTTONS_AT + 0.1):
            screen.t = t
            screen.draw(canvas)
            for pos in ((5, 5), (640, 360), (1270, 715), (300, 640), (900, 150), (100, 500)):
                self.assertNotEqual(tuple(canvas.get_at(pos))[:3], (1, 254, 3), (t, pos))
        from ui import void_fury_screen
        self.assertEqual(void_fury_screen.TITLE, "O VAZIO ESTÁ FURIOSO COM A SUA PRESENÇA.")

    def test_nothing_closes_the_screen_by_accident(self):
        game, screen = self.make_screen()
        game.run.floor_number = 100
        screen.update(0.5)
        screen.handle_input(FakeInput(swap=True))                     # durante a animação
        screen.handle_input(FakeInput(click=(640, 500), mouse=(640, 500)))
        self.assertEqual(game.run.floor_number, 100)
        screen.update(BUTTONS_AT)
        screen.handle_input(FakeInput(back=True))                     # Esc
        screen.handle_input(FakeInput(click=(20, 20), mouse=(20, 20)))        # clique fora dos botões
        self.assertIsNotNone(game.run)
        self.assertEqual(game.run.floor_number, 100)

    def test_continue_button_and_confirmed_give_up(self):
        game, screen = self.make_screen()
        screen.update(BUTTONS_AT + 0.1)
        screen.handle_input(FakeInput(swap=True))                     # CONTINUAR (selecionado por padrão)
        self.assertEqual(game.run.floor_number, 101)
        game, screen = self.make_screen()
        screen.update(BUTTONS_AT + 0.1)
        screen.handle_input(FakeInput(down=True))
        screen.handle_input(FakeInput(swap=True))                     # DESISTIR -> pede confirmação
        self.assertEqual(screen.mode, "confirm")
        self.assertIsNotNone(game.run)
        screen.handle_input(FakeInput(swap=True))                     # VOLTAR (padrão da confirmação)
        self.assertEqual(screen.mode, "choice")
        self.assertIsNotNone(game.run)


# ======================================================================
class UnlockScreenTests(Base):
    def flow_game(self):
        game = _game(self.data, "judge", mode="infinite", floor=100)
        game.run.start_floor()
        game.run.floor.enemy.hp = 0
        game.on_battle_won()
        return game

    def test_unlock_comes_before_the_cards_in_its_own_state(self):
        game = self.flow_game()
        self.assertEqual(game.state, GameState.UNLOCK)
        self.assertEqual(game.state_args["next_state"], GameState.REWARD)
        self.assertIn("rewards", game.state_args["next_kwargs"])

    def test_reward_screen_no_longer_draws_the_message_under_the_cards(self):
        src = open(os.path.join(ROOT, "ui", "reward_screen.py"), encoding="utf-8").read()
        self.assertNotIn("unlock_notice", src)

    def test_unlock_screen_covers_everything_and_waits_for_the_animation(self):
        game = self.flow_game()
        order = []
        game.change_state = lambda state, **kw: order.append((state, kw))
        game.pending_unlocks = ["assassin"]          # Tali
        screen = UnlockScreen(game, GameState.REWARD, {"rewards": []})
        canvas = surface()
        canvas.fill((1, 254, 3))
        screen.draw(canvas)
        screen.t = 1.0
        screen.draw(canvas)
        for pos in ((5, 5), (640, 360), (1270, 715), (200, 640), (1000, 150), (640, 700)):
            self.assertNotEqual(tuple(canvas.get_at(pos))[:3], (1, 254, 3), pos)
        screen.t = 0.2
        screen.handle_input(FakeInput(swap=True))
        screen.handle_input(FakeInput(click=(10, 10)))
        self.assertEqual(order, [])                                    # durante a animação não continua
        screen.update(ANIMATION_TIME)
        screen.draw(canvas)
        screen.handle_input(FakeInput(swap=True))
        self.assertEqual(order, [(GameState.REWARD, {"rewards": []})])
        self.assertEqual(game.pending_unlocks, [])

    def test_several_unlocks_are_shown_one_after_the_other(self):
        game = self.flow_game()
        order = []
        game.change_state = lambda state, **kw: order.append(state)
        game.pending_unlocks = ["assassin", "bard"]
        screen = UnlockScreen(game, GameState.REWARD, {"rewards": []})
        screen.update(ANIMATION_TIME + 0.1)
        screen.handle_input(FakeInput(swap=True))
        self.assertEqual(order, [])
        self.assertEqual(screen.char_id, "bard")
        screen.update(ANIMATION_TIME + 0.1)
        screen.draw(surface())
        screen.handle_input(FakeInput(click=(5, 5)))
        self.assertEqual(order, [GameState.REWARD])


# ======================================================================
class TaliAsEnemy(Base):
    def entity(self, cid="assassin", super_data=None):
        data = _character_enemy_data(cid, self.e["character_bosses"][cid], self.c, super_data)
        from bosses.boss import Boss
        return Boss(f"boss_char_{cid}", data, {"hp": 1, "damage": 1, "cooldown": 1})

    def test_tali_enemy_uses_her_character_art_in_battle_and_in_the_bestiary(self):
        from ui.shop_screen import ShopScreen
        battle = self.entity()
        folder, names = portraits._art_location(battle)
        self.assertEqual(folder, "characters")
        self.assertIn("assassin", names)
        self.assertIsNotNone(portraits._find_animation(battle, 128))
        shop = types.SimpleNamespace(data=self.data)
        data = ShopScreen._entity_data(shop, "boss_char_assassin")
        ent = types.SimpleNamespace(id="boss_char_assassin", color=tuple(data["color"]), name=data["name"], image_id=data.get("image", "x"),
                                    art_folder=data.get("art_folder"), family=data.get("family", "x"), portrait=data.get("portrait"),
                                    is_boss=True, is_super=False, character_id=data.get("character_id"))
        self.assertIsNotNone(portraits._find_animation(ent, 96))       # o Bestiário antes não achava a arte da Tali
        self.assertEqual(portraits._art_location(ent)[0], "characters")

    def test_super_tali_boss_keeps_name_art_and_super_frame(self):
        ent = self.entity("assassin", self.e["super_character_bosses"]["assassin"])
        self.assertTrue(ent.is_super)
        self.assertIn("Tali", ent.name)
        self.assertIsNotNone(portraits._find_animation(ent, 128))
        portraits.draw_portrait(surface(), (10, 10), 128, ent)

    def test_playable_tali_art_is_the_same_file(self):
        who = types.SimpleNamespace(char_id="assassin", image_id=self.c["assassin"]["image"], color=(150, 90, 200), name="Tali")
        self.assertEqual(portraits._art_location(who), ("characters", ["tali", "assassin"]))
        self.assertIsNotNone(portraits._find_animation(who, 128))

    def test_optional_separate_enemy_art_is_preferred_when_present(self):
        enemy = self.entity()
        folder, names = portraits._art_location(enemy)
        self.assertEqual(names[0], "tali_enemy")                       # arte própria de inimigo (opcional) vem primeiro
        self.assertIn("tali", names)

    def test_other_characters_are_not_mixed_up(self):
        for cid in ALL_CHARS:
            folder, names = portraits._art_location(self.entity(cid))
            self.assertEqual(folder, "characters")
            self.assertIn(cid, names)
            self.assertIn(self.c[cid]["image"], names)


if __name__ == "__main__":
    unittest.main()
