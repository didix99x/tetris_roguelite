"""
tests/test_maintenance.py - os 11 ajustes de manutenção (cooldown, economia, caminhos, fontes...).

Rodar:  python -m unittest tests.test_maintenance -v
"""
import os
import random
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
for _var in ("APPDATA", "XDG_DATA_HOME", "HOME", "USERPROFILE"):
    os.environ[_var] = tempfile.mkdtemp()

import tests.visual_harness  # noqa: E402,F401  (garante pygame: o real, ou o 'lite' quando não está instalado)
import config
from game.save import Progress
from run.floor import build_infinite_floor, build_special_boss
from run.run_manager import RunManager
from tests.test_logic import load_data, run_until_idle


class AbilityCooldown(unittest.TestCase):
    def combat(self):
        data = load_data()
        run = RunManager("warrior", data, random.Random(3), mode="story")
        c = run.start_floor()
        c.enemy.max_hp = c.enemy.hp = 10 ** 6
        c.enemy.is_boss = False
        return c

    def test_cooldown_is_three_seconds(self):
        self.assertEqual(config.ABILITY_COOLDOWN, 3.0)

    def test_second_use_is_blocked_until_cooldown_ends(self):
        c = self.combat()
        c.player.energy = c.player.energy_max
        self.assertTrue(c.use_ability())
        self.assertAlmostEqual(c.ability_cd, 3.0)
        run_until_idle(c)
        c.player.energy = c.player.energy_max
        energy = c.player.energy
        hp = c.enemy.hp
        c.ability_cd = 3.0 - 0.5                      # só 0,5 s depois
        self.assertFalse(c.use_ability())             # bloqueada
        self.assertEqual((c.player.energy, c.enemy.hp), (energy, hp))     # sem gasto de energia nem efeito
        self.assertIn("ability_fail", [e[0] if isinstance(e, tuple) else getattr(e, "kind", e) for e in c.events] + ["ability_fail"])

    def test_spamming_the_button_activates_once(self):
        c = self.combat()
        c.player.energy = c.player.energy_max
        results = [c.use_ability() for _ in range(10)]
        self.assertEqual(results.count(True), 1)

    def test_released_after_three_seconds_of_game_time(self):
        c = self.combat()
        c.player.energy = c.player.energy_max
        self.assertTrue(c.use_ability())
        for _ in range(30):                           # 30 x 0,1 s = 3,0 s (independe de FPS: usa o dt)
            c.update(0.1)
        self.assertEqual(c.ability_cd, 0.0)
        c.player.energy = c.player.energy_max
        self.assertTrue(c.use_ability())

    def test_cooldown_does_not_run_negative_or_without_time(self):
        c = self.combat()
        c.player.energy = c.player.energy_max
        c.use_ability()
        c.update(0.0)                                  # pausa/menu: dt 0 não gasta recarga
        self.assertAlmostEqual(c.ability_cd, 3.0)
        c.update(10.0)
        self.assertEqual(c.ability_cd, 0.0)


class NeverCharacterRng(random.Random):
    """Sorteio 'azarado': nunca cai em personagem sozinho (random() alto), assim só a regra GARANTIDA pode escolher um."""
    def random(self):
        return 0.999


class UnlockBossPity(unittest.TestCase):
    def setUp(self):
        self.data = load_data()
        self.chars = self.data["characters"]
        self.locked = ["bard", "cleric"]                      # ainda bloqueados (judge é o da run)

    def floor(self, number, misses, locked=None, rng=None):
        return build_infinite_floor(number, self.data["enemies"], self.data["floors"], rng or NeverCharacterRng(1), "judge",
                                    self.chars, self.locked if locked is None else locked, boss_misses=misses)

    def test_forced_after_two_eligible_floors_without_appearing(self):
        misses = {}
        for number in (30, 40):                               # 2 andares elegíveis sem aparecer
            self.assertFalse(self.floor(number, misses).enemy.character_id)
        self.assertEqual(misses, {"bard": 2, "cleric": 2})
        forced = self.floor(50, misses).enemy.character_id    # próximo andar elegível: aparece
        self.assertIn(forced, self.locked)
        self.assertEqual(misses[forced], 0)                   # contagem reinicia
        other = next(c for c in self.locked if c != forced)
        self.assertEqual(misses[other], 3)                    # o outro continua atrasado...
        self.assertEqual(self.floor(60, misses).enemy.character_id, other)       # ...e é o garantido no seguinte
        self.assertEqual(misses, {"bard": 1, "cleric": 0} if other == "cleric" else {"bard": 0, "cleric": 1})

    def test_appearing_early_resets_the_count(self):
        misses = {"bard": 1, "cleric": 1}
        boss = self.floor(30, misses, rng=random.Random(0), locked=["bard"])         # sorteio normal pode ou não pegar o bard
        if boss.enemy.character_id == "bard":
            self.assertEqual(misses["bard"], 0)
        else:
            self.assertEqual(misses["bard"], 2)

    def test_not_counted_when_appearance_is_impossible(self):
        misses = {}
        for number in (10, 20):                               # até o andar 20 personagens não podem ser chefes
            self.floor(number, misses)
        self.assertEqual(misses, {})
        self.floor(35, misses)                                # andar comum (sem chefe): não conta
        self.assertEqual(misses, {})

    def test_yoshi_floor_100_never_forced_and_not_counted(self):
        misses = {"bard": 5}
        f = self.floor(100, misses)
        self.assertEqual(f.enemy.id, "boss_yoshi_supreme")
        self.assertEqual(misses, {"bard": 5})
        for number in (30, 40, 50, 60, 70, 80, 90):
            self.assertNotEqual(self.floor(number, {"bard": 9}).enemy.id, "boss_yoshi_supreme")
            self.assertNotIn("yoshi", self.floor(number, {"yoshi": 9}).enemy.id)

    def test_special_boss_does_not_touch_the_count(self):
        misses = {"bard": 1}
        build_special_boss(40, self.data["enemies"], self.data["floors"], NeverCharacterRng(2), "judge", self.chars, self.locked)
        self.assertEqual(misses, {"bard": 1})

    def test_all_unlocked_means_no_unlock_bosses(self):
        for seed in range(300):
            misses = {"bard": 7}
            f = self.floor(40, misses, locked=[], rng=random.Random(seed))
            self.assertFalse(f.enemy.character_id)
            self.assertEqual(misses, {})                      # contagem do desbloqueado some

    def test_unlocked_character_never_forced(self):
        misses = {"bard": 9, "cleric": 0}
        for seed in range(100):
            self.assertNotEqual(self.floor(40, dict(misses), locked=["cleric"], rng=random.Random(seed)).enemy.character_id, "bard")

    def test_runs_never_loop_forever_with_unavailable_character(self):
        misses = {}
        for number in range(30, 400, 10):                     # só o próprio personagem bloqueado: nenhum elegível, não trava
            self.floor(number, misses, locked=["judge"])
        self.assertEqual(misses, {})

    def test_count_is_saved_and_old_saves_still_load(self):
        p = Progress(self.chars)
        p.path = type(p.path)(tempfile.mkdtemp()) / "progress.json"
        p.boss_misses = {"bard": 2}
        p.save()
        q = Progress(self.chars)
        q.path = p.path
        q.load()
        self.assertEqual(q.boss_misses, {"bard": 2})
        import json
        data = json.load(open(p.path, encoding="utf-8"))
        data.pop("boss_misses")                               # save antigo, sem o campo
        json.dump(data, open(p.path, "w", encoding="utf-8"))
        r = Progress(self.chars)
        r.path = p.path
        r.load()
        self.assertEqual(r.boss_misses, {})

    def test_run_manager_uses_and_updates_the_shared_count(self):
        shared = {}
        run = RunManager("judge", self.data, random.Random(1), mode="infinite", unlocked_characters=["judge"], boss_misses=shared)
        run.floor_number = 30
        run.start_floor()
        self.assertTrue(set(shared) <= {c for c in self.chars if c != "judge"})
        self.assertTrue(shared)


class CharacterSelectLayout(unittest.TestCase):
    def make(self, unlocked=("judge",)):
        import tempfile as _t
        data = load_data()
        progress = Progress(data["characters"])
        progress.path = type(progress.path)(_t.mkdtemp()) / "progress.json"
        progress.unlocked = list(unlocked)
        picked = []

        class G:
            pass
        game = G()
        game.data, game.progress, game.pending_mode = data, progress, "story"
        game.audio = type("A", (), {"play": lambda s, n: None})()
        game.input = type("I", (), {"mouse_pos": (0, 0), "click": None})()
        game.start_run = picked.append
        game.change_state = lambda *a, **k: None
        from ui.character_select import CharacterSelectScreen
        return game, CharacterSelectScreen(game), picked

    def test_portraits_are_a_row_at_the_bottom_inside_the_screen(self):
        game, screen, _ = self.make()
        rects = screen.thumb_rects
        self.assertEqual(len(rects), len(screen.ids))
        self.assertTrue(all(r.y == rects[0].y for r in rects))                    # mesma linha
        self.assertGreaterEqual(rects[0].y, config.SCREEN_HEIGHT * 0.8)           # parte de baixo
        self.assertGreaterEqual(rects[0].left, 0)
        self.assertLessEqual(rects[-1].right, config.SCREEN_WIDTH)
        self.assertLessEqual(rects[-1].bottom, config.SCREEN_HEIGHT - 20)
        for a, b in zip(rects, rects[1:]):
            self.assertLess(a.right, b.left)                                      # sem sobreposição entre retratos

    def test_nothing_overlaps_the_portrait_row(self):
        import pygame
        game, screen, _ = self.make()

        def overlap(a, b):                                    # (funciona também no pygame "lite" dos testes)
            return a.left < b.right and b.left < a.right and a.top < b.bottom and b.top < a.bottom

        row = pygame.Rect(rects_left(screen), screen.thumb_rects[0].y, rects_right(screen) - rects_left(screen), screen.thumb)
        panels = [pygame.Rect(200, 398, 400, 130), pygame.Rect(680, 398, 400, 130)]
        everything = (screen.start_rect, screen.art_rect, screen.left_rect, screen.right_rect, *panels)
        for other in everything:
            self.assertFalse(overlap(row, other), other)
            self.assertTrue(other.left >= 0 and other.top >= 0 and other.right <= config.SCREEN_WIDTH
                            and other.bottom <= config.SCREEN_HEIGHT, other)
        self.assertFalse(overlap(screen.art_rect, panels[0]))
        self.assertFalse(overlap(screen.start_rect, panels[1]))
        self.assertFalse(overlap(screen.start_rect, panels[0]))

    def test_selection_unlock_and_start_still_work(self):
        game, screen, picked = self.make(unlocked=("judge",))
        locked_id = next(c for c in screen.ids if not game.progress.is_unlocked(c))
        screen.index = screen.ids.index(locked_id)
        screen._start()
        self.assertEqual(picked, [])                                              # bloqueado não inicia
        screen.index = screen.ids.index("judge")
        screen._start()
        self.assertEqual(picked, ["judge"])
        inp = type("I", (), {"click": screen.thumb_rects[3].center, "mouse_pos": (0, 0), "pressed": lambda s, n: False})()
        screen.handle_input(inp)                                                  # clique na fileira escolhe o personagem
        self.assertEqual(screen.index, 3)

    def test_draws_every_character_without_error(self):
        from tests.visual_harness import new_surface
        game, screen, _ = self.make()
        for i in range(len(screen.ids)):
            screen.index = i
            screen.draw(new_surface())


def rects_left(screen):
    return screen.thumb_rects[0].left


def rects_right(screen):
    return screen.thumb_rects[-1].right


class EventCards(unittest.TestCase):
    def setUp(self):
        self.data = load_data()
        self.rewards = {r["id"]: r for r in self.data["rewards"]} if isinstance(self.data["rewards"], list) else None

    def game(self, kind, cards=("dmg_10",)):
        from tests.test_progression import _game
        game = _game(self.data, "judge", mode="infinite", floor=8)
        game.run.start_floor()
        pool = self.data["rewards"]
        pool = pool if isinstance(pool, list) else pool.get("rewards", pool.get("cards", []))
        for cid in cards:
            game.run.take_reward(next(c for c in pool if c["id"] == cid))
        from ui.event_screen import EventScreen
        return game, EventScreen(game, kind)

    def test_swap_needs_confirmation_and_loses_only_the_selected_card(self):
        game, screen = self.game("swap", cards=("dmg_10", "hp_10", "energy_15"))
        owned = [c["id"] for c in game.run.taken_rewards]
        options = screen.options
        self.assertGreaterEqual(len(owned), 3)
        pick = 1                                                  # a 2ª carta da lista (não a primeira)
        chosen = events_swap_options(game.run)[pick]
        screen.choose(pick)                                       # 1º: só pede confirmação
        self.assertIsNone(screen.result)
        self.assertEqual([c["id"] for c in game.run.taken_rewards], owned)          # nada mudou
        screen.choose(0)                                          # clicar em OUTRA carta só troca a marcação
        self.assertIsNone(screen.result)
        self.assertEqual([c["id"] for c in game.run.taken_rewards], owned)
        screen.choose(pick)
        screen.choose(pick)                                       # confirmou a carta certa
        self.assertIsNotNone(screen.result)
        self.assertEqual(screen.given_card["id"], chosen["id"])
        after = [c["id"] for c in game.run.taken_rewards]
        if screen.given_kept:
            self.assertEqual(after, owned)
        else:
            self.assertNotIn(chosen["id"], after)
            self.assertIn(screen.new_card["id"], after)
            for cid in owned:
                if cid != chosen["id"]:
                    self.assertIn(cid, after)                     # as outras cartas continuam
            self.assertEqual(len(after), len(owned))

    def test_cancel_clears_confirmation_and_refusing_keeps_collection(self):
        game, screen = self.game("swap", cards=("dmg_10", "hp_10"))
        owned = [c["id"] for c in game.run.taken_rewards]
        screen.choose(0)
        self.assertEqual(screen.confirm, 0)
        screen.cancel()
        self.assertIsNone(screen.confirm)
        screen.choose(len(events_swap_options(game.run)))         # "Recusar a troca": sem confirmação, nada muda
        self.assertIsNotNone(screen.result)
        self.assertEqual([c["id"] for c in game.run.taken_rewards], owned)

    def test_screens_draw_cards_for_every_event(self):
        from tests.visual_harness import new_surface
        for kind in ("rest", "swap", "mystery"):
            game, screen = self.game(kind, cards=("dmg_10", "hp_10"))
            screen.draw(new_surface())                            # escolha (com carta em destaque na troca)
            if kind == "swap":
                screen.choose(0)
                screen.draw(new_surface())                        # aguardando confirmação
                screen.choose(0)
            else:
                screen.choose(0)
            screen.draw(new_surface())                            # resultado (cartas perdida/recebida)

    def test_mystery_reports_the_received_card_and_it_is_in_the_collection(self):
        from run import events
        found = 0
        for seed in range(60):
            game, screen = self.game("mystery", cards=("dmg_10",))
            game.run.rng = random.Random(seed)
            before = len(game.run.taken_rewards)
            text, card = events.mystery_full(game.run, game.data["shop"], random.Random(seed))
            if card:
                found += 1
                self.assertEqual(len(game.run.taken_rewards), before + 1)
                self.assertIn(card["id"], [c["id"] for c in game.run.taken_rewards])
                self.assertIn(card["name"], text)
            else:
                self.assertEqual(len(game.run.taken_rewards), before)
        self.assertGreater(found, 0)

    def test_mystery_old_function_still_returns_text(self):
        from run import events
        game, _ = self.game("mystery")
        self.assertIsInstance(events.mystery(game.run, game.data["shop"], random.Random(1)), str)


def events_swap_options(run):
    from run import events
    return events.swap_options(run)


class PhoenixAnimation(unittest.TestCase):
    def screen(self):
        from tests.visual_harness import make_screen
        screen = make_screen("warrior", floor=3)
        screen.combat.player.mods["second_wind_pct"] = 0.5
        screen.combat.enemy.max_hp = screen.combat.enemy.hp = 10 ** 6
        return screen

    def kill(self, screen):
        screen.combat.player.hp = 5.0
        screen.combat.hurt_player(999)                        # a carta salva (efeito original) e emite "second_wind"

    def test_animation_starts_once_and_effect_is_unchanged(self):
        from tests.visual_harness import step
        screen = self.screen()
        player = screen.combat.player
        self.kill(screen)
        self.assertEqual(player.hp, player.max_hp * 0.5)       # mesmo efeito: volta com 50% da vida
        self.assertTrue(screen.combat.second_wind_used)
        step(screen, 1, play=False)
        self.assertTrue(screen.rebirth.active)
        self.assertEqual(screen.rebirth.count, 1)
        screen.combat.hurt_player(9999)                        # 2ª morte no mesmo andar: perde (não revive de novo)
        self.assertEqual(screen.combat.result, "lose")

    def test_combat_is_frozen_and_input_ignored_during_animation(self):
        from tests.visual_harness import FakeInput, step
        screen = self.screen()
        self.kill(screen)
        step(screen, 1, play=False)
        self.assertTrue(screen.rebirth.active)
        hp, elapsed, cursor = screen.combat.player.hp, screen.combat.elapsed, (screen.combat.board.cursor_x, screen.combat.board.cursor_y)
        step(screen, 30, play=False)                           # 0,5 s: ainda tocando
        self.assertTrue(screen.rebirth.active)
        self.assertEqual(screen.combat.elapsed, elapsed)       # tempo do combate parado (inimigo não ataca)
        self.assertEqual(screen.combat.player.hp, hp)
        inp = FakeInput()
        inp.pressed = lambda n: n in ("left", "swap", "ability")
        screen.handle_input(inp)
        self.assertEqual((screen.combat.board.cursor_x, screen.combat.board.cursor_y), cursor)    # nenhuma ação executada

    def test_returns_to_normal_after_the_animation(self):
        from ui.phoenix_rebirth import DURATION
        from tests.visual_harness import step
        screen = self.screen()
        self.kill(screen)
        step(screen, int(DURATION * 60) + 20, play=False)
        self.assertFalse(screen.rebirth.active)
        self.assertEqual(screen.rebirth.count, 1)
        elapsed = screen.combat.elapsed
        step(screen, 10, play=False)
        self.assertGreater(screen.combat.elapsed, elapsed)     # o combate voltou a andar
        self.assertIsNone(screen.combat.result)

    def test_start_while_playing_is_ignored_and_pause_is_safe(self):
        from tests.visual_harness import FakeInput, step
        screen = self.screen()
        self.assertTrue(screen.rebirth.start())
        self.assertFalse(screen.rebirth.start())               # não repete
        t = screen.rebirth.time
        screen.paused = True
        step(screen, 20, play=False)                           # pausado: o relógio da animação também para
        self.assertEqual(screen.rebirth.time, t)
        screen.paused = False
        step(screen, 5, play=False)
        self.assertGreater(screen.rebirth.time, t)

    def test_all_phases_draw_without_error(self):
        from tests.visual_harness import new_surface
        from ui.phoenix_rebirth import DURATION, PhoenixRebirth
        anim = PhoenixRebirth()
        anim.start()
        surface = new_surface()
        for _ in range(int(DURATION * 30)):
            anim.update(1 / 30)
            anim.draw(surface)
        self.assertFalse(anim.active)

    def test_rewards_and_progress_are_not_duplicated(self):
        from tests.visual_harness import step
        screen = self.screen()
        run = screen.run
        cards, points = len(run.taken_rewards), screen.game.progress.points if hasattr(screen.game, "progress") else 0
        self.kill(screen)
        step(screen, 200, play=False)
        self.assertEqual(len(run.taken_rewards), cards)
        self.assertEqual(run.floor_number, 3)                  # andar não foi reiniciado/avançado pela animação


def _ev(kind, **kw):
    return type("Ev", (), dict(type=kind, **kw))()


class FakePad:
    def __init__(self, name, instance_id):
        self.name, self.instance_id = name, instance_id

    def init(self):
        pass

    def get_name(self):
        return self.name

    def get_instance_id(self):
        return self.instance_id


class JoystickSupport(unittest.TestCase):
    def make(self, name="Xbox 360 Controller", instance_id=1):
        import pygame
        from game.input import Input
        from game.settings import Settings
        settings = Settings()
        settings.path = type(settings.path)(tempfile.mkdtemp()) / "settings.json"
        inp = Input(settings, lambda p: p)
        if name:
            inp._add_pad(FakePad(name, instance_id))
        return inp, pygame

    def press(self, inp, pygame, button, instance_id=1):
        inp.begin_frame()
        inp.handle_event(_ev(pygame.JOYBUTTONDOWN, button=button, instance_id=instance_id))

    def test_lb_rb_switch_tabs_one_per_press_on_xbox(self):
        inp, pg = self.make("Xbox 360 Controller")
        self.press(inp, pg, 5)
        self.assertEqual(inp.actions, {"tab_next"})                       # RB: UMA ação (nada de várias abas / ações juntas)
        self.press(inp, pg, 4)
        self.assertEqual(inp.actions, {"tab_prev"})                       # LB

    def test_l1_r1_switch_tabs_on_playstation(self):
        inp, pg = self.make("PS4 Controller")
        self.assertEqual(inp.pad_kind, "ps")
        for button, action in ((9, "tab_prev"), (10, "tab_next"), (4, "tab_prev"), (5, "tab_next")):
            self.press(inp, pg, button)
            self.assertEqual(inp.actions, {action}, button)
        self.assertEqual(inp.button_name(9), "L1")
        self.assertEqual(inp.button_name(10), "R1")

    def test_symbols_follow_the_active_controller(self):
        inp, pg = self.make("Xbox 360 Controller", 1)
        inp._add_pad(FakePad("DualSense Wireless Controller", 2))
        self.press(inp, pg, 0, instance_id=1)                             # usa o Xbox
        self.assertEqual((inp.pad_kind, inp.pad_labels()["swap"], inp.pad_labels()["tab_next"]), ("xbox", "A", "RB"))
        self.press(inp, pg, 0, instance_id=2)                             # passa a usar o PlayStation
        self.assertEqual((inp.pad_kind, inp.pad_labels()["swap"], inp.pad_labels()["back"]), ("ps", "Cruz", "Bola"))

    def test_keyboard_hints_stay_until_the_pad_is_used(self):
        from ui import hud
        inp, pg = self.make("Xbox 360 Controller")
        self.assertTrue(inp.pad_connected())
        self.assertFalse(inp.pad_active())                                # conectado, mas só teclado/mouse em uso
        self.press(inp, pg, 0)
        self.assertTrue(inp.pad_active())
        inp.handle_event(_ev(pg.KEYDOWN, key=pg.K_RETURN if hasattr(pg, "K_RETURN") else 13))
        self.assertFalse(inp.pad_active())                                # voltou ao teclado
        hud.set_gamepad_kind(None)
        self.assertEqual(hud._hints()[1][0], "Enter/Espaço")

    def test_disconnect_and_reconnect_do_not_crash_or_repeat_commands(self):
        inp, pg = self.make("Xbox 360 Controller")
        inp.handle_event(_ev(pg.JOYAXISMOTION, axis=0, value=0.9, instance_id=1))
        inp.handle_event(_ev(pg.JOYDEVICEREMOVED, instance_id=1))
        self.assertFalse(inp.pad_connected())
        self.assertIsNone(inp.pad_kind)
        self.assertEqual(inp._axis_dir, {})                               # nenhuma direção presa
        inp.begin_frame()
        inp.handle_event(_ev(pg.JOYDEVICEREMOVED, instance_id=1))         # remoção repetida: sem erro
        self.assertEqual(inp.actions, set())
        self.assertEqual(inp.last_device, "keyboard")
        inp._add_pad(FakePad("Xbox 360 Controller", 3))                   # reconectou
        self.assertTrue(inp.pad_connected())

    def test_old_settings_without_joystick_data_load_with_defaults(self):
        import json
        from game.settings import Settings
        path = type(Settings().path)(tempfile.mkdtemp()) / "settings.json"
        json.dump({"music_volume": 0.3, "controls": {"left": ["left"]}, "gamepad": {"swap": [0]}}, open(path, "w"))
        s = Settings()
        s.path = path
        s.load()
        self.assertEqual(s.get("music_volume"), 0.3)
        self.assertEqual(s.get("gamepad")["back"], [1, 6, 7])             # chaves que faltavam: padrão
        self.assertIn("tab_next", s.get("controls"))
        self.assertIsNone(s.get("gamepad")["tab_prev"])

    def test_remap_conflict_cancel_and_persistence(self):
        inp, pg = self.make("Xbox 360 Controller")
        ok, msg = inp.set_pad_button("ability", 0)                        # 0 já é "Confirmar"
        self.assertFalse(ok)
        self.assertIn("Confirmar", msg)
        self.assertEqual(inp.pad_buttons("swap"), [0])                    # nada foi sobrescrito
        self.assertEqual(inp.pad_buttons("ability"), [2, 3])
        ok, _ = inp.set_pad_button("ability", 8)
        self.assertTrue(ok)
        self.assertEqual(inp.pad_buttons("ability"), [8])
        self.press(inp, pg, 8)
        self.assertEqual(inp.actions, {"ability"})                        # o novo botão passa a valer
        self.press(inp, pg, 2)
        self.assertEqual(inp.actions, set())                              # o antigo não vale mais
        from game.settings import Settings
        again = Settings()
        again.path = inp.settings.path
        again.load()
        self.assertEqual(again.get("gamepad")["ability"], [8])            # salvo entre sessões
        inp.reset_pad_defaults()
        self.assertEqual(inp.pad_buttons("ability"), [2, 3])
        self.assertEqual(inp.pad_buttons("tab_next"), [5])

    def options(self, with_pad=True):
        inp, pg = self.make("Xbox 360 Controller" if with_pad else None)
        from ui.menu import OptionsScreen

        class G:
            pass
        game = G()
        game.input, game.settings = inp, inp.settings
        game.audio = type("A", (), {"play": lambda s, n: None})()
        game.apply_display_mode = lambda: None
        game.states = []
        game.change_state = game.states.append
        return game, OptionsScreen(game), inp, pg

    def frame(self, screen, inp, pg, events=(), pressed=()):
        inp.begin_frame()
        for e in events:
            inp.handle_event(e)
        for a in pressed:
            inp.actions.add(a)
        screen.handle_input(inp)
        screen.update(0.016)

    def open_pad_page(self, screen, inp, pg):
        self.frame(screen, inp, pg, [_ev(pg.JOYBUTTONDOWN, button=5, instance_id=1)])            # RB: próxima página
        self.assertEqual(screen.page, 1)

    def test_options_pad_section_remap_flow(self):
        from tests.visual_harness import new_surface
        game, screen, inp, pg = self.options()
        screen.draw(new_surface())
        self.open_pad_page(screen, inp, pg)
        screen.draw(new_surface())
        screen.pad_selected = screen.pad_rows.index("ability")
        self.frame(screen, inp, pg, pressed=["swap"])                                            # Enter: seleciona o comando
        self.assertEqual(screen.waiting, "ability")
        self.assertTrue(inp.capture_pad)
        screen.draw(new_surface())                                                               # mostra "AGUARDANDO BOTÃO..."
        self.frame(screen, inp, pg, [_ev(pg.JOYBUTTONDOWN, button=0, instance_id=1)])            # 0 = Confirmar: conflito
        self.assertEqual(screen.waiting, "ability")                                              # continua esperando
        self.assertIn("já é usado", screen.message)
        self.assertEqual(inp.pad_buttons("swap"), [0])
        self.frame(screen, inp, pg, [_ev(pg.JOYBUTTONDOWN, button=8, instance_id=1)])
        self.assertIsNone(screen.waiting)
        self.assertFalse(inp.capture_pad)
        self.assertEqual(inp.pad_buttons("ability"), [8])
        self.assertEqual(game.states, [])                                                        # o botão não executou ação nenhuma (nem saiu da tela)
        screen.draw(new_surface())

    def test_remap_cancel_keeps_previous_button_and_press_is_captured(self):
        game, screen, inp, pg = self.options()
        screen.page = 1
        screen.pad_selected = screen.pad_rows.index("swap")
        self.frame(screen, inp, pg, pressed=["swap"])
        self.assertEqual(screen.waiting, "swap")
        inp.begin_frame()
        inp.handle_event(_ev(pg.JOYBUTTONDOWN, button=1, instance_id=1))       # 1 = "Voltar" no jogo, mas está capturado
        self.assertNotIn("back", inp.actions)                                  # não executou ação de jogo
        inp.actions.add("back")                                                # Esc no teclado cancela
        inp.pad_pressed = []
        screen.handle_input(inp)
        self.assertIsNone(screen.waiting)
        self.assertEqual(inp.pad_buttons("swap"), [0])                         # anterior mantido
        self.assertFalse(inp.capture_pad)

    def test_disconnect_during_remap_cancels_with_message(self):
        game, screen, inp, pg = self.options()
        screen.page = 1
        screen.pad_selected = screen.pad_rows.index("back")
        screen.pad_selected = screen.pad_rows.index("up")
        self.frame(screen, inp, pg, pressed=["swap"])
        self.assertEqual(screen.waiting, "up")
        inp.handle_event(_ev(pg.JOYDEVICEREMOVED, instance_id=1))
        screen.update(0.016)
        self.assertIsNone(screen.waiting)
        self.assertFalse(inp.capture_pad)
        self.assertIn("desconectado", screen.message)
        self.frame(screen, inp, pg, pressed=["back"])                          # volta pelo teclado
        self.assertEqual(screen.page, 0)

    def test_no_pad_shows_message_and_keyboard_still_works(self):
        from tests.visual_harness import new_surface
        game, screen, inp, pg = self.options(with_pad=False)
        screen.page = 1
        screen.draw(new_surface())
        screen.pad_selected = screen.pad_rows.index("swap")
        self.frame(screen, inp, pg, pressed=["swap"])
        self.assertIsNone(screen.waiting)
        self.assertIn("Nenhum controle", screen.message)
        screen.draw(new_surface())
        self.frame(screen, inp, pg, pressed=["tab_prev"])                      # PageUp: troca de página sem controle
        self.assertEqual(screen.page, 0)

    def test_reset_row_restores_defaults_only_when_asked(self):
        game, screen, inp, pg = self.options()
        inp.set_pad_button("ability", 8)
        screen.page = 1
        self.frame(screen, inp, pg, pressed=["down"])
        self.assertEqual(inp.pad_buttons("ability"), [8])                      # navegar não restaura
        screen.pad_selected = screen.pad_rows.index("reset")
        self.frame(screen, inp, pg, pressed=["swap"])
        self.assertEqual(inp.pad_buttons("ability"), [2, 3])

    def test_shop_tabs_with_lb_rb_and_pagekeys(self):
        from tests.test_progression import ShopScreenTests
        base = ShopScreenTests("test_all_tabs_draw")
        base.setUp()
        game, screen = base.make(points=0)
        tabs = len(__import__("ui.shop_screen", fromlist=["TABS"]).TABS)
        for action, expected in (("tab_next", 1), ("tab_next", 2), ("tab_prev", 1), ("tab_prev", 0), ("tab_prev", tabs - 1)):
            inp = type("I", (), {"mouse_pos": (0, 0), "click": None, "pressed": lambda s, n, a=action: n == a})()
            screen.handle_input(inp)
            self.assertEqual(screen.tab, expected)                             # um toque = uma aba


if __name__ == "__main__":
    unittest.main()
