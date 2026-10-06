"""
tests/test_visual.py - HUD e efeitos visuais das habilidades.

Garante que (1) tudo desenha sem erro, (2) cada habilidade tem um efeito, (3) os efeitos são leves e
terminam, e (4) a parte visual NÃO muda a gameplay (mesma batalha com e sem desenho => mesmo resultado).

Usa o pygame oficial se existir; senão o mini-pygame de tests/pygame_lite.py.
Rodar:  python -m unittest tests.test_visual -v
"""
import os
import random
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tests.visual_harness import cast, make_screen, new_surface, pygame, shot, step  # noqa: E402
from tests.test_logic import bot_move, load_data  # noqa: E402

from combat.combat import Combat, IDLE  # noqa: E402
from run.run_manager import RunManager  # noqa: E402
from ui import ability_fx, theme  # noqa: E402

CHARACTERS = ("warrior", "assassin", "mage", "bard", "cleric", "blacksmith", "archer", "judge", "monk")


class HudDraws(unittest.TestCase):
    def test_hud_draws_for_every_character_and_state(self):
        data = load_data()
        for ch in CHARACTERS:
            for floor, mode in ((3, "infinite"), (10, "story"), (30, "infinite")):
                screen = make_screen(ch, floor=floor, mode=mode, data=data)
                step(screen, 20)
                screen.combat.player.hp = 5                     # vida baixa
                screen.combat.poison_time = 4
                screen.combat.silence_time = 2
                screen.combat.haste_time = 3
                for key in ("damage_pct", "crit_chance", "regen_per_sec", "lifesteal_pct", "block_chance", "thorns_pct"):
                    screen.combat.player.mods[key] = 0.2
                screen.draw(new_surface())

    def test_super_boss_and_boss_tags_draw(self):
        data = load_data()
        screen = make_screen("warrior", floor=40, data=data)
        enemy = screen.combat.enemy
        enemy.is_boss = True
        for is_super in (False, True):
            enemy.is_super = is_super
            screen.draw(new_surface())

    def test_draw_bar_and_panel_keep_the_old_signatures(self):
        from ui.widgets import draw_bar, draw_panel
        surf = new_surface()
        draw_bar(surf, (10, 10, 200, 24), 5, 10, (200, 60, 60))                      # forma antiga
        draw_bar(surf, (10, 10, 200, 24), 5, 10, (200, 60, 60), "5 / 10")
        draw_bar(surf, (10, 10, 200, 24), 0, 10, (200, 60, 60), "0 / 10")
        draw_bar(surf, (10, 10, 200, 24), 10, 0, (200, 60, 60))                       # max 0 não pode quebrar
        draw_panel(surf, (30, 30, 200, 100))                                           # outras telas usam assim
        draw_panel(surf, (30, 30, 200, 100), border=(255, 210, 80))

    def test_bar_trail_follows_damage_then_settles(self):
        from unittest import mock
        from ui import widgets
        widgets.reset_bar_animation()
        clock = {"ms": 0}                                   # relógio falso: o teste controla o tempo (pygame real ou simulado)
        with mock.patch.object(pygame.time, "get_ticks", lambda: clock["ms"]):
            surf = new_surface()
            widgets.draw_bar(surf, (10, 10, 200, 24), 100, 100, (200, 60, 60), key="t")
            clock["ms"] = 16
            widgets.draw_bar(surf, (10, 10, 200, 24), 40, 100, (200, 60, 60), key="t")
            self.assertGreater(widgets._bar_state["t"][0], 40)                         # rastro ainda visível
            for ms in range(32, 3000, 16):
                clock["ms"] = ms
                widgets.draw_bar(surf, (10, 10, 200, 24), 40, 100, (200, 60, 60), key="t")
            self.assertEqual(widgets._bar_state["t"][0], 40)

    def test_all_icons_draw(self):
        from ui import icons
        surf = new_surface()
        for name in icons.ICONS:
            icons.draw_icon(surf, name, (50, 50), 20, (255, 200, 100))
        for text in ("Teias: 3", "Pedras: 2", "Pressão: 4s", "Veneno: 3s", "Silêncio: 2s", "Inimigo blindado: 5s", "outro"):
            name, color = icons.status_icon(text)
            self.assertIn(name, icons.ICONS)

    def test_font_can_be_configured_and_falls_back(self):
        from ui import widgets
        old = theme.FONT_PATH
        try:
            theme.FONT_PATH = "assets/fonts/nao_existe.ttf"
            widgets._fonts.clear()
            widgets.draw_text(new_surface(), "teste", 30, (255, 255, 255), (50, 50))
        finally:
            theme.FONT_PATH = old
            widgets._fonts.clear()


class AbilityEffects(unittest.TestCase):
    def test_every_character_has_a_registered_style_and_color(self):
        data = load_data()
        for ch in data["characters"]:
            self.assertIn(ch, ability_fx.CHARACTER_STYLE, ch)
            self.assertIn(ability_fx.CHARACTER_STYLE[ch], ability_fx.STYLES, ch)
            self.assertIn(ch, theme.STYLE_COLORS, ch)
        self.assertEqual(len(ability_fx.STYLES), 9)
        for kind in ("ring", "glow", "slash", "orb", "arrow", "spark", "mote", "note", "pillar", "rune", "wave", "flash_rect", "rays"):
            self.assertIn(kind, ability_fx.DRAW)

    def test_using_each_ability_spawns_effects_that_finish(self):
        data = load_data()
        for ch in CHARACTERS:
            screen = make_screen(ch, floor=5, data=data)
            step(screen, 20)
            self.assertTrue(cast(screen), ch)
            self.assertGreater(len(screen.fx.items), 3, ch)
            self.assertLessEqual(len(screen.fx.items), theme.EFFECTS["max_items"])
            for i in range(150):                                    # 2,5 s depois não sobra nada
                screen.update(1 / 60)
                if i % 25 == 0:
                    screen.draw(new_surface())
            self.assertEqual(screen.fx.items, [], ch)

    def test_effect_count_is_bounded_even_if_spammed(self):
        fx = ability_fx.AbilityFX()
        ctx = make_screen("archer").fx_ctx
        for _ in range(60):
            for ch in CHARACTERS:
                fx.trigger(ch, ctx)
        self.assertLessEqual(len(fx.items), theme.EFFECTS["max_items"])

    def test_effects_can_be_turned_off_and_tuned(self):
        saved = dict(theme.EFFECTS)
        try:
            theme.EFFECTS["enabled"] = False
            screen = make_screen("mage", floor=5)
            step(screen, 20)
            cast(screen)
            self.assertEqual(screen.fx.items, [])
            theme.EFFECTS.update(enabled=True, intensity=0.3, size=0.6)
            low = ability_fx.AbilityFX()
            low.trigger("warrior", screen.fx_ctx)
            theme.EFFECTS.update(intensity=2.0, size=1.5)
            high = ability_fx.AbilityFX()
            high.trigger("warrior", screen.fx_ctx)
            self.assertGreater(len(high.items), len(low.items))
        finally:
            theme.EFFECTS.clear()
            theme.EFFECTS.update(saved)

    def test_hit_reactions_never_crash(self):
        screen = make_screen("warrior", floor=3)
        ctx = screen.fx_ctx
        for kind, event in (("damage_enemy", {"amount": 5}), ("damage_enemy", {"amount": 90}), ("damage_player", {"amount": 9}),
                            ("crit", {}), ("heal", {"amount": 4}), ("enemy_heal", {"amount": 4}), ("enemy_ability", {"name": "x"}),
                            ("win", {}), ("burst", {"cells": []}), ("swap", {})):
            screen.fx.react(kind, event, ctx, [(400, 300)] if kind == "burst" else None)
        screen.fx.update(0.1)
        screen.fx.draw(new_surface())

    def test_effect_module_never_touches_combat(self):
        for name in ("ui/ability_fx.py", "ui/hud.py", "ui/icons.py", "ui/theme.py"):
            src = open(os.path.join(ROOT, name), encoding="utf-8").read()
            self.assertNotRegex(src, r"\bimport combat\b|\bfrom combat\b", name)
            self.assertIsNone(re.search(r"\b(combat|player|enemy)\.[A-Za-z_\.\[\]\"']+\s*(=|\+=|-=)(?!=)", src), name)
            self.assertNotRegex(src, r"\.(take_damage|heal|add_energy|spend_ability|deal_damage_to_enemy|use_ability|try_swap)\(", name)


class GameplayUnchanged(unittest.TestCase):
    """A mesma batalha, com e sem a interface desenhando, termina IDÊNTICA."""

    def snapshot(self, combat):
        board = tuple(tuple(b.color_id for b in combat.board.blocks()) for _ in (0,))
        return (round(combat.player.hp, 4), round(combat.player.energy, 4), combat.enemy.hp, combat.result, combat.chain.count,
                board, combat.board.cursor_x, combat.board.cursor_y)

    def run_plain(self, ch, floor, seed):
        run = RunManager(ch, load_data(), random.Random(seed), mode="infinite")
        run.floor_number = floor
        combat = run.start_floor()
        rng = random.Random(seed + 1)
        for frame in range(450):
            if combat.phase == IDLE and not combat.result:
                bot_move(combat, rng)
            if frame in (150, 300) and combat.phase == IDLE:
                combat.player.energy = combat.player.energy_max
                combat.use_ability()
            combat.update(1 / 60)
            combat.pop_events()
        return self.snapshot(combat)

    def run_with_ui(self, ch, floor, seed):
        screen = make_screen(ch, floor=floor, seed=seed)
        screen.banner_time = 0
        combat = screen.combat
        rng = random.Random(seed + 1)
        surface = new_surface()
        for frame in range(450):
            if combat.phase == IDLE and not combat.result:
                bot_move(combat, rng)
            if frame in (150, 300) and combat.phase == IDLE:
                combat.player.energy = combat.player.energy_max
                combat.use_ability()
            screen.update(1 / 60)               # a tela chama combat.update + processa eventos + efeitos
            if frame % 3 == 0:
                screen.draw(surface)            # desenha HUD, tabuleiro e efeitos
        return self.snapshot(combat)

    def test_same_result_with_and_without_ui_for_every_character(self):
        for i, ch in enumerate(CHARACTERS):
            self.assertEqual(self.run_plain(ch, 4 + i, 10 + i), self.run_with_ui(ch, 4 + i, 10 + i), ch)

    def test_effects_disabled_gives_the_same_result_too(self):
        saved = dict(theme.EFFECTS)
        try:
            a = self.run_with_ui("warrior", 6, 3)
            theme.EFFECTS["enabled"] = False
            b = self.run_with_ui("warrior", 6, 3)
        finally:
            theme.EFFECTS.clear()
            theme.EFFECTS.update(saved)
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
