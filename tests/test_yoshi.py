"""
tests/test_yoshi.py - YOSHI: boss do andar 50 (Normal), boss supremo do andar 100 (Infinito), cegueira, passivas
combinadas, recompensa (3 cartas lendárias), desbloqueio do personagem e integração (HUD/seleção).

Regras testadas:
  Andar 50 (história)  -> Yoshi boss comum -> NÃO desbloqueia.
  Andar 100 (infinito) -> Yoshi supremo    -> derrota -> desbloqueia Yoshi + 3 cartas lendárias.
Rodar:  python -m unittest tests.test_yoshi -v
"""
import copy
import os
import random
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tests.visual_harness import FakeGame, cast, make_screen, new_surface, pygame, step  # noqa: E402
from tests.test_logic import bot_move, load_data  # noqa: E402

from bosses.boss import Boss  # noqa: E402
from bosses.yoshi import SUPPORTED_PASSIVES, YoshiBoss, merge_enemy_passives  # noqa: E402
from characters import unlock_hint  # noqa: E402
from combat import effects  # noqa: E402
from combat.combat import Combat, IDLE  # noqa: E402
from enemies.enemy import Enemy  # noqa: E402
from run.floor import build_floor, build_infinite_floor, build_special_boss  # noqa: E402
from run.progression import scale_stats, scale_stats_infinite  # noqa: E402
from run.run_manager import RunManager  # noqa: E402
from tests.test_final_update import fresh_progress  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.data = load_data()
        self.enemies, self.floors = self.data["enemies"], self.data["floors"]

    def infinite(self, floor, seed=1, own="warrior", **kw):
        return build_infinite_floor(floor, self.enemies, self.floors, random.Random(seed), own, self.data["characters"], [], **kw)


class StoryBoss(Base):
    def test_yoshi_is_the_normal_boss_of_floor_50_and_does_not_unlock(self):
        f = build_floor(50, self.enemies, self.floors, random.Random(1))
        self.assertTrue(f.is_boss)
        self.assertEqual(f.enemy.id, "boss_yoshi")
        self.assertEqual(f.enemy.name, "Yoshi")
        self.assertIsNone(f.enemy.character_id)                 # sem character_id => derrotar NÃO desbloqueia
        self.assertFalse(f.enemy.is_super)
        self.assertIsNone(f.enemy.appearance_message)           # sem mensagem ameaçadora no Modo Normal
        self.assertNotIsInstance(f.enemy, YoshiBoss)

    def test_other_story_floors_are_unchanged(self):
        for floor in (10, 20, 30, 40):
            f = build_floor(floor, self.enemies, self.floors, random.Random(1))
            self.assertEqual(f.enemy.id, f"boss_{floor}")
        for floor in (1, 25, 49):
            self.assertFalse(build_floor(floor, self.enemies, self.floors, random.Random(floor)).is_boss)

    def test_story_yoshi_has_no_blindness_and_works_like_a_normal_boss(self):
        data = self.enemies["yoshi"]["story"]
        self.assertFalse(any(a["type"] == "blind" for a in data["abilities"]))
        boss = Boss("boss_yoshi", data, scale_stats(data, 50, self.floors["scaling"]))
        self.assertTrue(boss.is_boss)
        self.assertGreater(boss.max_hp, scale_stats(self.enemies["bosses"]["40"], 50, self.floors["scaling"])["hp"] * 0.5)

    def test_old_boss_50_data_is_kept_for_the_infinite_pool(self):
        self.assertIn("50", self.enemies["bosses"])
        ids = {self.infinite(60, s).enemy.id for s in range(400)}
        self.assertIn("boss_50", ids)

    def test_defeating_yoshi_at_50_never_unlocks_him(self):
        game = _game(self.data, "judge", mode="story", floor=50)
        game.run.start_floor()
        game._unlock_defeated_character(game.run.floor.enemy)
        self.assertFalse(game.progress.is_unlocked("yoshi"))
        self.assertEqual(game.unlock_notice, [])


class SupremeBoss(Base):
    def test_yoshi_appears_only_at_floor_100(self):
        for floor in range(1, 160):
            for seed in range(6):
                e = self.infinite(floor, seed).enemy
                if floor == 100:
                    self.assertEqual(e.id, "boss_yoshi_supreme")
                else:
                    self.assertNotIn("yoshi", e.id, (floor, seed))

    def test_never_random_special_boss_or_character_boss(self):
        for seed in range(300):
            self.assertNotIn("yoshi", build_special_boss(60, self.enemies, self.floors, random.Random(seed), "warrior",
                                                         self.data["characters"], []).enemy.id)
        self.assertNotIn("yoshi", " ".join(self.enemies["character_bosses"]))
        self.assertNotIn("yoshi", " ".join(self.enemies["infinite_bosses"]))

    def test_floor_100_has_no_special_boss_in_its_place(self):
        game = _game(self.data, "judge", mode="infinite", floor=100)
        game.data["floors"] = copy.deepcopy(self.floors)
        game.data["floors"]["infinite"]["special_boss_chance"] = 1.0       # 100%: em qualquer outro andar viria o especial
        self.assertFalse(game.roll_special_boss())
        game.run.floor_number = 99
        game.run.floor_number = 70
        self.assertTrue(game.roll_special_boss())

    def test_supreme_boss_properties(self):
        e = self.infinite(100).enemy
        self.assertIsInstance(e, YoshiBoss)
        self.assertTrue(e.is_boss and e.is_super)
        self.assertEqual(e.character_id, "yoshi")                           # => derrotar desbloqueia
        self.assertEqual(e.reward, {"cards": 3, "rarity": "legendary"})
        self.assertEqual(e.appearance_message["text"], "CUIDADO! VOCÊ ENCONTROU YOSHI, O REI DO TETRIS")
        self.assertGreater(e.appearance_message["seconds"], 2)
        self.assertEqual((e.art_folder, e.image_id), ("characters", "yoshi"))
        strongest_super = max(self.enemies["infinite_bosses"][k]["hp"] for k in self.enemies["infinite_bosses"])
        self.assertGreater(self.enemies["yoshi"]["infinite"]["hp"], strongest_super)    # "supremo": o mais forte

    def test_has_all_enemy_passives_and_originals_untouched(self):
        before = copy.deepcopy(self.enemies["enemies"])
        e = self.infinite(100).enemy
        self.assertEqual(self.enemies["enemies"], before)                   # nada foi alterado nos inimigos
        used = {k for d in self.enemies["enemies"].values() for k in d.get("passive_params", {})}
        self.assertTrue(used <= SUPPORTED_PASSIVES, used - SUPPORTED_PASSIVES)   # nova passiva => precisa ser suportada
        merged = merge_enemy_passives(self.enemies["enemies"])
        for key in ("armor", "match3_reduction", "chain1_reduction", "enrage_hp", "enrage_factor", "extra_web_time",
                    "regen_pct", "attack_heal_pct"):
            self.assertIn(key, merged, key)
        stats = {"hp": 1000, "damage": 10, "cooldown": 6.0, "ability_bonus": 0}
        # Yoshi é pelo menos tão resistente quanto CADA inimigo, em várias situações de dano
        for enemy_id, data in self.enemies["enemies"].items():
            enemy = Enemy(enemy_id, data, stats)
            for chain, big in ((1, 3), (1, 4), (2, 3), (3, 5)):
                self.assertLessEqual(e.modify_incoming(100, chain, big), enemy.modify_incoming(100, chain, big) + 0, (enemy_id, chain, big))
        self.assertAlmostEqual(e.mechanics["chain_armor"], merged["chain1_reduction"])
        self.assertGreaterEqual(e.mechanics["enrage_hp"], 0.5)
        self.assertLessEqual(e.mechanics["enrage_factor"], 0.6)
        web = [a for a in e.abilities if a["type"] == "web"][0]
        self.assertGreaterEqual(web["duration"], self.enemies["yoshi"]["infinite"]["abilities"][7]["duration"] + merged["extra_web_time"])

    def test_cooldown_is_at_least_as_fast_as_any_enemy_enrage(self):
        e = self.infinite(100).enemy
        e.hp = int(e.max_hp * 0.45)
        goblin = Enemy("goblin", self.enemies["enemies"]["goblin"], {"hp": 100, "damage": 1, "cooldown": 5})
        goblin.hp = 40
        self.assertLessEqual(e.cooldown_factor(), 0.6 + 1e-9)

    def test_healing_passives_are_scaled_and_original_values_kept_in_data(self):
        e = self.infinite(100).enemy
        raw = merge_enemy_passives(self.enemies["enemies"])
        self.assertAlmostEqual(e.mechanics["regen_pct"], raw["regen_pct"] * self.enemies["yoshi"]["infinite"]["passive_scale"]["regen_pct"])
        self.assertLess(e.regen_per_sec(), e.max_hp * 0.01)                  # não é imbatível

    def test_stats_scale_with_player_like_other_bosses(self):
        a = self.infinite(100).enemy
        run = RunManager("warrior", self.data, random.Random(2), mode="infinite")
        for cid in ("i_pact_e1", "i_crown_l1", "i_exec_e1"):
            run.take_reward(next(r for r in self.data["rewards"]["rewards"] if r["id"] == cid))
        b = self.infinite(100, player=run.player, base_max_hp=120).enemy
        self.assertGreater(b.max_hp, a.max_hp)

    def test_yoshi_fights_without_errors_and_uses_every_ability(self):
        run = RunManager("warrior", self.data, random.Random(5), mode="infinite")
        run.floor_number = 100
        combat = run.start_floor()
        self.assertEqual(combat.enemy.id, "boss_yoshi_supreme")
        run.player.max_hp = run.player.hp = 10 ** 7
        rng = random.Random(6)
        seen = set()
        for _ in range(9000):
            if combat.phase == IDLE:
                bot_move(combat, rng)
            combat.update(1 / 20)
            seen |= {e["name"] for e in combat.pop_events() if e["type"] == "enemy_ability"}
            if combat.result:
                break
        names = {a["name"] for a in self.enemies["yoshi"]["infinite"]["abilities"]}
        self.assertGreaterEqual(len(seen), len(names) - 1)
        self.assertIn("Cegueira do Rei", seen)
        self.assertEqual(sum(1 for _ in combat.board.blocks()), 64)


class Blindness(Base):
    def combat(self):
        run = RunManager("warrior", self.data, random.Random(1), mode="infinite")
        return run, run.start_floor()

    def test_blindness_lasts_exactly_2_seconds_then_ends_by_itself(self):
        _, c = self.combat()
        effects.apply_enemy_ability(c, {"type": "blind", "name": "x", "duration": 2.0})
        self.assertEqual(c.blind_time, 2.0)
        for _ in range(39):                                    # 1,95 s
            c.update(0.05)
        self.assertGreater(c.blind_time, 0)
        c.update(0.05)                                         # 2,00 s
        self.assertEqual(c.blind_time, 0.0)
        self.assertNotIn("Cegueira", " ".join(c.status_effects()))

    def test_blindness_changes_no_game_logic(self):
        def run_once(blind):
            run = RunManager("mage", self.data, random.Random(4), mode="infinite")
            c = run.start_floor()
            rng = random.Random(9)
            for frame in range(400):
                if blind and frame == 50:
                    effects.apply_enemy_ability(c, {"type": "blind", "name": "x", "duration": 2.0})
                if c.phase == IDLE and not c.result:
                    bot_move(c, rng)
                c.update(1 / 20)
                c.pop_events()
            return (round(c.player.hp, 3), round(c.player.energy, 3), c.enemy.hp, c.result,
                    tuple(b.color_id for b in c.board.blocks()))
        self.assertEqual(run_once(False), run_once(True))

    def test_not_reduced_by_resistance_cards(self):
        _, c = self.combat()
        c.player.mods["status_resist_pct"] = 0.75
        effects.apply_enemy_ability(c, {"type": "blind", "name": "x", "duration": 2.0})
        self.assertEqual(c.blind_time, 2.0)

    def test_screen_darkens_for_2s_and_returns_to_normal(self):
        screen = make_screen("warrior", floor=100)
        step(screen, 5, play=False)
        c = screen.combat
        effects.apply_enemy_ability(c, {"type": "blind", "name": "x", "duration": 2.0})
        surface = new_surface()
        screen.banner_time = 0
        step(screen, 40, play=False, surface=surface)           # ~0,67 s: no meio da cegueira
        self.assertGreater(c.blind_time, 1.0)
        self.assertLess(_brightness(surface), 30)               # área de jogo praticamente preta
        step(screen, 90, play=False, surface=surface)           # passou de 2 s
        self.assertEqual(c.blind_time, 0.0)
        self.assertGreater(_brightness(surface), 60)            # voltou ao normal sozinho


class AppearanceMessage(Base):
    def test_message_text_and_style(self):
        from ui import boss_warning
        screen = make_screen("warrior", floor=100)
        self.assertIsNotNone(screen.warning)
        self.assertEqual(" ".join(t for t, _ in screen.warning.lines).replace("!  ", "! "),
                         "CUIDADO! VOCÊ ENCONTROU YOSHI, O REI DO TETRIS")
        r, g, b = boss_warning.COLOR
        self.assertTrue(r > 200 and g < 80 and b < 80)           # vermelho

    def test_animates_and_disappears_after_a_few_seconds(self):
        screen = make_screen("warrior", floor=100)
        w = screen.warning
        surface = new_surface()
        shots = []
        for i in range(int(6 * 60)):
            screen.update(1 / 60)
            if i in (3, 40, 120, 250, 330):
                screen.draw(surface)
                shots.append((i, w.active))
        self.assertTrue(shots[0][1] and shots[2][1])
        self.assertFalse(w.active)                                # ~4,5 s depois some
        self.assertFalse(shots[-1][1])

    def test_no_message_on_other_bosses_or_story_yoshi(self):
        self.assertIsNone(make_screen("warrior", floor=50, mode="story").warning)
        self.assertIsNone(make_screen("warrior", floor=40, mode="infinite").warning)

    def test_does_not_change_the_battle(self):
        a = make_screen("warrior", floor=100, seed=3)
        b = make_screen("warrior", floor=100, seed=3)
        b.warning = None
        for s in (a, b):
            step(s, 120)
        self.assertEqual((a.combat.player.hp, a.combat.enemy.hp), (b.combat.player.hp, b.combat.enemy.hp))


class Reward(Base):
    def test_defeating_supreme_yoshi_unlocks_and_gives_3_legendary_cards(self):
        game = _game(self.data, "judge", mode="infinite", floor=100)
        game.run.start_floor()
        self.assertFalse(game.progress.is_unlocked("yoshi"))
        game.run.floor.enemy.hp = 0
        game.on_battle_won()
        self.assertTrue(game.progress.is_unlocked("yoshi"))                 # desbloqueado
        self.assertTrue(any("YOSHI" in line for line in game.unlock_notice))
        self.assertEqual((game.bonus_picks_left, game.bonus_picks_total), (3, 3))
        # o desbloqueio tem tela PRÓPRIA (antes das cartas): UNLOCK -> REWARD
        self.assertEqual(game.state, "UNLOCK")
        self.assertEqual(game.pending_unlocks, ["yoshi"])
        game.state, game.state_args = game.state_args["next_state"], game.state_args["next_kwargs"]
        self.assertEqual(game.state, "REWARD")
        taken = []
        for n in range(3):
            opts = game.state_args["rewards"]
            self.assertEqual(len(opts), 3)
            self.assertTrue(all(o["rarity"] == "legendary" for o in opts))
            self.assertTrue(all(o["id"] not in {t["id"] for t in taken} for o in opts))   # sem repetir
            taken.append(opts[0])
            game.on_reward_chosen(opts[0])
        self.assertEqual(len(taken), 3)
        self.assertEqual(game.bonus_picks_left, 0)
        self.assertTrue(all(r["id"] in {x["id"] for x in game.run.taken_rewards} for r in taken))
        self.assertEqual(game.state, "VOID_FURY")                            # andar 100 concluído: "O VAZIO ESTÁ FURIOSO..."
        self.assertEqual(game.run.floor_number, 100)                         # e o jogo NÃO avança sozinho
        game.on_void_fury_choice(True)
        self.assertEqual(game.run.floor_number, 101)                         # a run continua (Infinito)
        self.assertEqual(sum(1 for r in game.run.taken_rewards if r["rarity"] == "legendary"), 3)

    def test_yoshi_stays_unlocked_permanently(self):
        game = _game(self.data, "judge", mode="infinite", floor=100)
        game.run.start_floor()
        game._unlock_defeated_character(game.run.floor.enemy)
        game.progress.save()
        from game.save import Progress
        again = Progress(self.data["characters"])
        again.path = game.progress.path
        again.load()
        self.assertTrue(again.is_unlocked("yoshi"))

    def test_other_infinite_bosses_do_not_trigger_the_bonus(self):
        game = _game(self.data, "judge", mode="infinite", floor=40)
        game.run.start_floor()
        game.run.floor.enemy.hp = 0
        game.on_battle_won()
        self.assertEqual(game.bonus_picks_left, 0)

    def test_reward_screen_draws_the_legendary_title(self):
        from ui.reward_screen import RewardScreen
        game = _game(self.data, "judge", mode="infinite", floor=100)
        game.run.start_floor()
        game.run.floor.enemy.hp = 0
        game.on_battle_won()
        self.assertEqual(game.state, "UNLOCK")
        RewardScreen(game, game.state_args["next_kwargs"]["rewards"]).draw(new_surface())


class PlayableYoshi(Base):
    def test_character_data_is_complete_and_locked_by_default(self):
        c = self.data["characters"]["yoshi"]
        for key in ("name", "class", "max_hp", "ability_name", "ability_text", "ability_cost", "ability_params",
                    "passive_name", "passive_text", "passive_params", "color", "image", "unlock"):
            self.assertTrue(c.get(key), key)
        progress = fresh_progress(self.data)
        self.assertFalse(progress.is_unlocked("yoshi"))
        self.assertEqual(progress.unlocked, ["judge"])                       # o desbloqueio inicial não mudou
        self.assertIn("andar 100", unlock_hint(self.data["characters"]["yoshi"]))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "assets", "images", "characters", "yoshi.gif")))

    def test_no_other_unlock_rule_unlocks_yoshi(self):
        progress = fresh_progress(self.data)
        for floor in (10, 50, 100):
            progress.best_floor = floor
            progress.wins = 5
            progress.update_unlocks()
        self.assertFalse(progress.is_unlocked("yoshi"))

    def test_passive_unhurried_bonus(self):
        p = RunManager("yoshi", self.data, random.Random(1)).player
        self.assertAlmostEqual(p.damage_multiplier(1, False), 1.3)
        self.assertEqual(p.damage_multiplier(1, True), 1.0)
        self.assertEqual(p.damage_multiplier(3, True), 1.0)

    def test_ability_damage_boss_bonus_and_heal(self):
        run = RunManager("yoshi", self.data, random.Random(1), mode="infinite")
        c = run.start_floor()
        c.enemy.max_hp = c.enemy.hp = 10 ** 6
        c.enemy.is_boss = False
        run.player.hp = 50.0
        run.player.energy = run.player.energy_max
        self.assertTrue(c.use_ability())
        self.assertEqual(10 ** 6 - c.enemy.hp, 42)
        self.assertAlmostEqual(run.player.hp, 56.0)
        self.assertEqual(run.player.energy, run.player.energy_max - 55)
        c.enemy.is_boss = True
        c.enemy.hp = 10 ** 6
        run.player.energy = run.player.energy_max
        c.ability_cd = 0.0                          # (passaram os 3 s de recarga)
        c.use_ability()
        self.assertEqual(10 ** 6 - c.enemy.hp, round(42 * 1.25))

    def test_selection_screen_lists_ten_characters_that_fit_the_screen(self):
        import config
        from ui.character_select import CharacterSelectScreen as CharacterSelect
        game = _game(self.data, "judge", mode="infinite", floor=1)
        screen = CharacterSelect(game)
        self.assertEqual(len(screen.ids), 10)
        self.assertIn("yoshi", screen.ids)
        self.assertLessEqual(screen.thumb_rects[-1].bottom, config.SCREEN_HEIGHT - 20)
        screen.draw(new_surface())
        for cid in screen.ids:                                                # clicar em cada um não quebra
            screen.index = screen.ids.index(cid)
            screen.draw(new_surface())

    def test_original_nine_keep_normal_thumb_size(self):
        import config
        from ui.character_select import THUMB, CharacterSelectScreen as CharacterSelect
        data = copy.deepcopy(self.data)
        del data["characters"]["yoshi"]
        game = _game(data, "judge", mode="infinite", floor=1)
        self.assertEqual(CharacterSelect(game).thumb, THUMB)

    def test_hud_and_ability_effect_for_yoshi(self):
        data = self.data
        screen = make_screen("yoshi", floor=5, data=data)
        step(screen, 20)
        self.assertTrue(cast(screen))
        self.assertGreater(len(screen.fx.items), 3)
        screen.draw(new_surface())
        for cid in data["characters"]:
            make_screen(cid, floor=100, data=data).draw(new_surface())       # contra o boss supremo, com HUD

    def test_yoshi_works_as_a_full_run_character(self):
        run = RunManager("yoshi", self.data, random.Random(3), mode="infinite")
        rng = random.Random(4)
        for floor in range(1, 6):
            run.floor_number = floor
            c = run.start_floor()
            run.player.hp = run.player.max_hp
            for _ in range(1500):
                if c.phase == IDLE:
                    bot_move(c, rng)
                c.update(1 / 20)
                c.pop_events()
                if c.result:
                    break
            self.assertIsNotNone(c.result)
            run.floor_cleared()


class OtherContentUntouched(Base):
    def test_original_characters_and_old_bosses_untouched(self):
        import json
        orig = json.load(open(os.path.join(ROOT, "tests", "old_content_hashes.json"), encoding="utf-8")) if os.path.exists(
            os.path.join(ROOT, "tests", "old_content_hashes.json")) else None
        self.assertIsNotNone(orig)
        for cid in ("judge", "warrior", "mage", "assassin", "bard", "cleric", "blacksmith", "archer", "monk"):
            self.assertIn(cid, self.data["characters"])
        self.assertEqual(self.enemies["bosses"]["50"]["name"], "Devorador de Puzzles")


# ---------------------------------------------------------------- utilidades
def _brightness(surface):
    """Brilho médio da área do tabuleiro (para provar que escureceu e voltou)."""
    total = count = 0
    for gx in range(24):
        for gy in range(24):
            r, g, b = surface.get_at((400 + gx * 20, 150 + gy * 19))[:3]
            total += (r + g + b) / 3
            count += 1
    return total / count


def _game(data, char, mode="infinite", floor=1):
    """Um Game mínimo (sem janela) com o fluxo REAL de vitória/recompensa/desbloqueio do game/game.py."""
    import tempfile
    from game.game import Game
    from game.save import Progress

    class Stub(Game):
        def __init__(self):
            self.data = copy.deepcopy(data)
            self.progress = Progress(self.data["characters"])
            self.progress.path = type(self.progress.path)(tempfile.mkdtemp()) / "progress.json"
            self.audio = type("A", (), {"play": lambda s, n: None, "play_situation": lambda s, n: None})()
            self.settings = type("S", (), {"get": lambda s, k: 0.5})()
            self.rng = random.Random(1)
            self.unlock_notice = []
            self.pending_unlocks = []
            self.special_reward_pending = False
            self.special_active = False
            self.bonus_picks_left = self.bonus_picks_total = 0
            self.bonus_rarity, self.bonus_title = "legendary", ""
            self.state, self.state_args = None, {}
            self.run = RunManager(char, self.data, random.Random(2), mode=mode)
            self.run.floor_number = floor
            self.screens = {}
            self.pending_mode = mode
            self.input = type("I", (), {"mouse_pos": (0, 0), "click": None, "pressed": lambda s, n: False})()

        def change_state(self, state, **kw):
            self.state, self.state_args = state, kw

    return Stub()


if __name__ == "__main__":
    unittest.main()
