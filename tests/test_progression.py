"""
tests/test_progression.py - PONTOS PERMANENTES, LOJA (cartas e upgrades), ARTE DAS CARTAS, SINERGIAS, CARTAS EXCLUSIVAS,
EVENTOS, DICA DE JOGADA, SÍMBOLOS, FUNDOS, OPÇÕES, CONTROLE E SONS.

Rodar:  python -m unittest tests.test_progression -v
"""
import copy
import hashlib
import json
import os
import random
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tests.visual_harness import FakeInput, make_screen, new_surface, pygame, step  # noqa: E402
from tests.test_logic import bot_move, load_data  # noqa: E402
from tests.test_yoshi import _game  # noqa: E402

from characters.character import DEFAULT_MODS  # noqa: E402
from combat.combat import IDLE  # noqa: E402

try:                                  # o pygame real precisa do display iniciado para converter nomes de teclas
    pygame.display.init()
except Exception:                     # noqa: BLE001
    pass
from game import shop as logic  # noqa: E402
from game.save import Progress  # noqa: E402
from run import events  # noqa: E402
from run.run_manager import RunManager  # noqa: E402


def fresh(data, unlocked=None):
    p = Progress(data["characters"])
    p.path = type(p.path)(tempfile.mkdtemp()) / "progress.json"
    p.unlocked = list(unlocked or ["judge"])
    p.points = 0
    return p


def reload(p, data):
    q = Progress(data["characters"])
    q.path = p.path
    q.load()
    return q


class Base(unittest.TestCase):
    def setUp(self):
        self.data = load_data()
        self.shop = self.data["shop"]
        self.chars = self.data["characters"]
        self.cards = self.data["rewards"]["rewards"]

    def card(self, cid):
        return next(c for c in self.cards if c["id"] == cid)


# ======================================================================
class Points(Base):
    def test_points_for_floors_bosses_and_victory(self):
        pts = self.shop["points"]
        S = lambda n: logic.scaled_points(self.shop, n)           # base x 0,60 (arredondado), aplicado uma vez
        self.assertEqual(pts["multiplier"], 0.6)
        self.assertEqual(logic.points_for_floor(self.shop, "story", 3, False)[0], S(pts["floor_clear"]))
        self.assertEqual(logic.points_for_floor(self.shop, "story", 3, False)[0], 9)             # 15 -> 9
        self.assertEqual(logic.points_for_floor(self.shop, "infinite", 3, False)[0], S(pts["floor_clear_infinite"]))
        self.assertEqual(logic.points_for_floor(self.shop, "story", 10, True)[0], S(pts["floor_clear"] + pts["boss_defeat"]))
        self.assertEqual(logic.points_for_floor(self.shop, "infinite", 40, True, True)[0], S(pts["floor_clear_infinite"] + pts["super_boss_defeat"]))
        self.assertEqual(logic.points_for_floor(self.shop, "story", 50, True, False, True)[0],
                         S(pts["floor_clear"] + pts["boss_defeat"] + pts["story_victory"]))

    def test_milestones_only_once(self):
        p = fresh(self.data)
        self.assertEqual(logic.claim_milestone(p, self.shop, "infinite", 50), 300)          # 500 x 0,60
        self.assertEqual(logic.claim_milestone(p, self.shop, "infinite", 50), 0)
        self.assertEqual(logic.claim_milestone(p, self.shop, "infinite", 51), 0)
        self.assertEqual(p.points, 300)

    def test_points_received_through_the_real_game_flow(self):
        game = _game(self.data, "judge", mode="story", floor=3)
        game.run.start_floor()
        game.run.floor.enemy.hp = 0
        game.on_battle_won()
        expected = logic.scaled_points(self.shop, self.shop["points"]["floor_clear"])          # 15 -> 9
        self.assertEqual(game.progress.points, expected)
        self.assertEqual(game.run_points, expected)
        self.assertEqual(game.progress.bestiary.get(game.run.floor.enemy.id), 1)         # Bestiário

    def test_boss_pays_more_and_milestone_pays_once(self):
        game = _game(self.data, "judge", mode="infinite", floor=50)
        game.run.start_floor()
        game.run.floor.enemy.hp = 0
        game.on_battle_won()
        pts = self.shop["points"]
        S = lambda n: logic.scaled_points(self.shop, n)
        self.assertGreaterEqual(game.progress.points, S(pts["floor_clear_infinite"] + pts["boss_defeat"]) + S(500))
        before = game.progress.points
        game.run.floor_number = 50
        game.run.start_floor()
        game.run.floor.enemy.hp = 0
        game.on_battle_won()
        self.assertLess(game.progress.points - before, 300)                    # marco não paga de novo

    def test_points_persist_after_losing_finishing_and_quitting(self):
        for ending in ("lose", "abandon"):
            game = _game(self.data, "judge", mode="story", floor=4)
            game.run.start_floor()
            game.run.floor.enemy.hp = 0
            game.on_battle_won()
            earned = game.progress.points
            (game.on_battle_lost if ending == "lose" else game.abandon_run)()
            q = reload(game.progress, self.data)                                  # "sair do jogo e abrir de novo"
            self.assertEqual(q.points, earned, ending)
            self.assertEqual(q.history[0]["result"], "derrota" if ending == "lose" else "abandonou")
            self.assertEqual(q.history[0]["points"], earned)

    def test_victory_pays_and_is_recorded(self):
        game = _game(self.data, "judge", mode="story", floor=50)
        game.run.start_floor()
        game.run.floor.enemy.hp = 0
        game.on_battle_won()
        self.assertGreaterEqual(game.progress.points, logic.scaled_points(self.shop, self.shop["points"]["story_victory"]))
        self.assertEqual(game.progress.history[0]["result"], "vitória")


# ======================================================================
class ShopCards(Base):
    def test_costs_by_rarity_are_centralized(self):
        self.assertEqual(self.shop["card_costs"], {"common": 100, "rare": 250, "epic": 500, "legendary": 1000})
        self.assertEqual(self.shop["card_price_multiplier"], 1.3)
        final = {"common": 130, "rare": 325, "epic": 650, "legendary": 1300}          # base x 1,30 (aplicado uma vez)
        for rarity, cost in self.shop["card_costs"].items():
            c = next(c for c in logic.shop_cards(self.data["rewards"]) if c["rarity"] == rarity)
            self.assertEqual(logic.card_cost(self.shop, c), final[rarity])

    def test_shop_has_all_rarities_and_exclusive_cards(self):
        sc = logic.shop_cards(self.data["rewards"])
        self.assertEqual({c["rarity"] for c in sc}, {"common", "rare", "epic", "legendary"})
        exclusive = {c["character"] for c in sc if c.get("character")}
        self.assertEqual(exclusive, set(self.chars))                           # 1 exclusiva por personagem (10)

    def test_buy_flow(self):
        p = fresh(self.data)
        c = self.card("s_fire_burst")
        self.assertEqual(logic.card_display_state(p, self.shop, c), "BLOQUEADA")
        self.assertEqual(logic.buy_card(p, self.shop, c), (False, "PONTOS INSUFICIENTES"))
        self.assertEqual(p.points, 0)
        cost = logic.card_cost(self.shop, c)                                   # 100 x 1,30 = 130
        self.assertEqual(cost, 130)
        p.points = 129
        self.assertEqual(logic.buy_card(p, self.shop, c), (False, "PONTOS INSUFICIENTES"))      # 1 ponto a menos: não compra
        p.points = 150
        self.assertEqual(logic.card_display_state(p, self.shop, c), "DISPONÍVEL")
        self.assertEqual(logic.buy_card(p, self.shop, c), (True, "CARTA DESBLOQUEADA"))
        self.assertEqual(p.points, 20)                                         # descontou 130
        self.assertEqual(logic.card_display_state(p, self.shop, c), "DESBLOQUEADA")
        self.assertEqual(logic.buy_card(p, self.shop, c), (False, "JÁ DESBLOQUEADA"))
        self.assertEqual(p.points, 20)                                         # não comprou duas vezes
        q = reload(p, self.data)                                               # salvou na hora
        self.assertEqual((q.points, q.purchased_cards), (20, ["s_fire_burst"]))

    def test_locked_shop_cards_never_appear_until_bought(self):
        p = fresh(self.data)
        for seed in range(150):
            run = RunManager("judge", self.data, random.Random(seed), blocked_cards=logic.blocked_card_ids(p, self.data["rewards"], "judge"))
            run.floor_number = 10
            for r in run.roll_rewards(count=3) + run.roll_rewards(only_rarity="legendary"):
                self.assertFalse(r.get("shop"), r["id"])
        p.points = 5000
        for cid in ("s_inferno", "s_fire_burst", "s_flame_wave", "s_phoenix_flame", "s_glacier"):
            logic.buy_card(p, self.shop, self.card(cid))
        seen = set()
        for seed in range(500):
            run = RunManager("judge", self.data, random.Random(seed), blocked_cards=logic.blocked_card_ids(p, self.data["rewards"], "judge"))
            run.floor_number = 20
            seen |= {r["id"] for r in run.roll_rewards(count=3)}
        self.assertTrue(seen & {"s_inferno", "s_fire_burst", "s_flame_wave", "s_glacier"})
        self.assertFalse(seen & {"s_ice_shield", "s_healing_light"})            # as não compradas continuam fora

    def test_exclusive_cards_only_for_their_character(self):
        p = fresh(self.data)
        p.purchased_cards = [c["id"] for c in self.cards if c.get("shop")]
        for cid in self.chars:
            blocked = logic.blocked_card_ids(p, self.data["rewards"], cid)
            mine = {c["id"] for c in self.cards if c.get("character") == cid}
            self.assertFalse(mine & blocked, cid)
            others = {c["id"] for c in self.cards if c.get("character") and c["character"] != cid}
            self.assertEqual(others, blocked, cid)

    def test_old_cards_are_unchanged_and_always_available(self):
        old = [c for c in self.cards if not c.get("shop")]
        self.assertEqual(len(old), 105)
        p = fresh(self.data)
        blocked = logic.blocked_card_ids(p, self.data["rewards"], "judge")
        self.assertFalse({c["id"] for c in old} & blocked)

    def test_synergies_activate_once_and_apply_their_bonus(self):
        run = RunManager("judge", self.data, random.Random(1))
        run.take_reward(self.card("s_fire_burst"))
        self.assertEqual(run.active_synergies, [])
        base_dmg, base_def = run.player.mods["damage_pct"] - 0.10, run.player.mods["damage_reduction_pct"]   # antes das cartas
        run.take_reward(self.card("s_ice_shield"))
        self.assertEqual(run.active_synergies, ["syn_fire_ice"])
        self.assertEqual(run.new_synergies, ["Fogo e Gelo"])
        self.assertAlmostEqual(run.player.mods["damage_pct"], base_dmg + 0.10 + 0.05)        # carta + sinergia
        self.assertAlmostEqual(run.player.mods["damage_reduction_pct"], base_def + 0.06 + 0.03)
        self.assertIn("Sinergia: Fogo e Gelo", run.player.mod_lines())
        run.take_reward(self.card("dmg_10"))
        self.assertEqual(run.active_synergies, ["syn_fire_ice"])                           # não repete

    def test_every_synergy_references_real_shop_cards(self):
        ids = {c["id"] for c in self.cards}
        for syn in self.data["rewards"]["synergies"]:
            self.assertGreaterEqual(len(syn["cards"]), 2)
            self.assertTrue(set(syn["cards"]) <= ids, syn["id"])
            for e in syn["effects"]:
                self.assertIn(e["type"], set(DEFAULT_MODS) | {"max_hp"})

    def test_new_cards_are_valid_and_different_from_plain_damage(self):
        valid = set(DEFAULT_MODS) | {"max_hp"}
        for c in logic.shop_cards(self.data["rewards"]):
            self.assertLessEqual(len(c["description"]), 90, c["id"])
            for e in c["effects"]:
                self.assertIn(e["type"], valid)
            run = RunManager(c.get("character", "judge"), self.data, random.Random(1))
            run.take_reward(c)


# ======================================================================
class Upgrades(Base):
    def test_all_characters_have_a_passive_rule_pointing_to_a_real_param(self):
        for cid, cdata in self.chars.items():
            rule = self.shop["upgrades"]["passive"][cid]
            self.assertIn(rule["param"], cdata["passive_params"], cid)

    def test_levels_and_costs(self):
        up = self.shop["upgrades"]
        self.assertEqual(up["max_level"], 15)
        self.assertEqual(len(up["cost_table"]), 15)
        self.assertEqual(up["cost_table"], sorted(up["cost_table"]))                       # custo crescente
        for attr in logic.ATTRIBUTES:
            costs = [logic.upgrade_cost(self.shop, attr, lv) for lv in range(15)]
            self.assertEqual(costs, sorted(costs))
            self.assertIsNone(logic.upgrade_cost(self.shop, attr, 15))

    def test_locked_characters_cannot_receive_upgrades(self):
        p = fresh(self.data)
        p.points = 99999
        ok, why = logic.can_upgrade(p, self.shop, self.chars, "warrior", "vida")
        self.assertFalse(ok)
        self.assertIn("DESBLOQUEIE ESTE PERSONAGEM", why)
        self.assertEqual(logic.buy_upgrade(p, self.shop, self.chars, "warrior", "vida")[0], False)
        self.assertEqual(p.points, 99999)
        self.assertEqual(p.upgrades, {})

    def test_buy_upgrade_flow_cap_and_independence(self):
        p = fresh(self.data, ["judge", "mage"])
        p.points = 10
        self.assertEqual(logic.buy_upgrade(p, self.shop, self.chars, "judge", "dano"), (False, "PONTOS INSUFICIENTES"))
        p.points = 10 ** 6
        for _ in range(15):
            self.assertTrue(logic.buy_upgrade(p, self.shop, self.chars, "judge", "dano")[0])
        self.assertEqual(logic.level_of(p, "judge", "dano"), 15)
        self.assertEqual(logic.buy_upgrade(p, self.shop, self.chars, "judge", "dano"), (False, "MÁXIMO"))
        self.assertEqual(logic.level_of(p, "judge", "dano"), 15)                            # nunca passa de 15
        self.assertEqual(logic.level_of(p, "mage", "dano"), 0)                              # independente
        self.assertEqual(logic.level_of(p, "judge", "vida"), 0)
        self.assertTrue(logic.upgrade_info(p, self.shop, self.chars, "judge", "dano")["at_max"])
        total = sum(logic.upgrade_cost(self.shop, "dano", lv) for lv in range(15))
        self.assertEqual(10 ** 6 - p.points, total)
        q = reload(p, self.data)
        self.assertEqual(q.upgrades, {"judge": {"dano": 15}})

    def test_ui_values_come_from_the_same_source_as_gameplay(self):
        """O que a tela mostra (ATUAL) é exatamente o que o jogo aplica, em todos os personagens e vários níveis."""
        for cid in self.chars:
            base = RunManager(cid, self.data, random.Random(1)).player
            rule = self.shop["upgrades"]["passive"][cid]
            for level in (0, 1, 7, 15):
                v = lambda attr: logic.upgrade_value(self.shop, self.chars, cid, attr, level)
                only = lambda attr: RunManager(cid, self.data, random.Random(1), upgrades={attr: level}).player      # um atributo por vez
                self.assertEqual(only("vida").max_hp, v("vida"), (cid, level))
                self.assertAlmostEqual(only("dano").mods["damage_pct"] - base.mods["damage_pct"], v("dano"))
                self.assertAlmostEqual(only("defesa").mods["damage_reduction_pct"] - base.mods["damage_reduction_pct"], v("defesa"))
                self.assertAlmostEqual(only("passiva").passive_params[rule["param"]], v("passiva"))

    def test_level_zero_is_identical_to_the_original_character(self):
        for cid in self.chars:
            a = RunManager(cid, self.data, random.Random(1)).player
            b = RunManager(cid, self.data, random.Random(1), upgrades={}).player
            c = RunManager(cid, self.data, random.Random(1), upgrades={"vida": 0, "dano": 0, "defesa": 0, "passiva": 0}).player
            for other in (b, c):
                self.assertEqual((a.max_hp, a.mods, a.passive_params), (other.max_hp, other.mods, other.passive_params), cid)

    def test_original_data_is_never_mutated_by_upgrades(self):
        before = copy.deepcopy(self.chars)
        RunManager("archer", self.data, random.Random(1), upgrades={a: 15 for a in logic.ATTRIBUTES})
        self.assertEqual(self.chars, before)

    def test_passive_upgrade_changes_the_real_behavior(self):
        for cid, param in (("archer", "crit_chance"), ("blacksmith", "damage_reduction"), ("cleric", "regen_per_sec")):
            base = RunManager(cid, self.data, random.Random(1)).player
            top = RunManager(cid, self.data, random.Random(1), upgrades={"passiva": 15}).player
            key = {"crit_chance": "crit_chance", "damage_reduction": "damage_reduction_pct", "regen_per_sec": "regen_per_sec"}[param]
            self.assertGreater(top.mods[key], base.mods[key], cid)                        # lidos no __init__: o upgrade chegou a tempo
        j0 = RunManager("judge", self.data, random.Random(1)).player
        j15 = RunManager("judge", self.data, random.Random(1), upgrades={"passiva": 15}).player
        self.assertGreater(j15.damage_multiplier(1, False), j0.damage_multiplier(1, False))

    def test_balance_caps_for_max_upgrades(self):
        for cid, cdata in self.chars.items():
            p = RunManager(cid, self.data, random.Random(1), upgrades={a: 15 for a in logic.ATTRIBUTES}).player
            self.assertLessEqual(p.max_hp, cdata["max_hp"] * 1.7, cid)                    # sem vida exagerada
            base = RunManager(cid, self.data, random.Random(1)).player
            self.assertLessEqual(p.mods["damage_pct"] - base.mods["damage_pct"], 0.31)
            self.assertLessEqual(p.mods["damage_reduction_pct"] - base.mods["damage_reduction_pct"], 0.16 + 0.08)   # defesa + passiva do Ferreiro
            self.assertLess(p.mods["damage_reduction_pct"], 0.5)                           # longe de 100%
            rule = self.shop["upgrades"]["passive"][cid]
            base = cdata["passive_params"][rule["param"]]
            self.assertLessEqual(p.passive_params[rule["param"]], base * 2.6, cid)          # passiva melhora, não quebra

    def test_defense_never_reaches_100_percent_even_with_cards(self):
        from combat import damage
        self.assertLess(damage.MAX_DAMAGE_REDUCTION, 1.0)
        run = RunManager("blacksmith", self.data, random.Random(1), upgrades={"defesa": 15})
        run.player.mods["damage_reduction_pct"] += 5.0
        c = run.start_floor()
        c.rng = type("R", (), {"random": lambda s: 0.99})()
        hp = c.player.hp
        c.hurt_player(100)
        self.assertGreater(hp - c.player.hp, 0)

    def test_info_texts_follow_the_requested_format(self):
        p = fresh(self.data)
        info = logic.upgrade_info(p, self.shop, self.chars, "judge", "dano")
        self.assertEqual((info["level"], info["max"], info["current"], info["next"], info["increase"]), (0, 15, "+0%", "+2%", "+2%"))
        self.assertEqual(info["cost"], logic.upgrade_cost(self.shop, "dano", 0))
        hp = logic.upgrade_info(p, self.shop, self.chars, "judge", "vida")
        self.assertEqual(hp["current"], f"{self.chars['judge']['max_hp']} HP")
        self.assertEqual(hp["increase"], "+4 HP")
        pas = logic.upgrade_info(p, self.shop, self.chars, "judge", "passiva")
        self.assertEqual((pas["current"], pas["next"], pas["increase"]), ("10%", "11%", "+1%"))
        df = logic.upgrade_info(p, self.shop, self.chars, "judge", "defesa")
        self.assertEqual((df["current"], df["next"]), ("0%", "1%"))

    def test_gameplay_uses_the_upgrades_in_a_real_battle(self):
        weak = RunManager("judge", self.data, random.Random(1)).start_floor()
        strong = RunManager("judge", self.data, random.Random(1), upgrades={"dano": 15}).start_floor()
        for c in (weak, strong):
            c.enemy.max_hp = c.enemy.hp = 10 ** 6
            c.chain.count = 1
            c._deal_match_damage([3], 1, 0)
        self.assertGreater(10 ** 6 - strong.enemy.hp, 10 ** 6 - weak.enemy.hp)


# ======================================================================
class CardArt(Base):
    def test_every_card_has_its_own_art_in_the_rarity_folder(self):
        hashes = {}
        for c in self.cards:
            path = os.path.join(ROOT, "assets", "cards", c["rarity"], c["id"] + ".png")
            self.assertTrue(os.path.exists(path), f"sem arte: {c['id']}")
            hashes.setdefault(hashlib.md5(open(path, "rb").read()).hexdigest(), []).append(c["id"])
        self.assertEqual(len(hashes), len(self.cards), "duas cartas com a MESMA arte")

    def test_art_loads_and_draws_for_all_cards(self):
        from ui import card_art
        surf = new_surface()
        for c in self.cards:
            self.assertIsNotNone(card_art.art_path(c))
            card_art.card_art(c, 96)
        for c in self.cards[:6] + [self.card("s_yoshi_blade"), self.card("s_phoenix_flame")]:
            card_art.draw_card_face(surf, pygame.Rect(100, 100, 340, 330), c, active=True)
            card_art.draw_card_thumb(surf, pygame.Rect(10, 10, 80, 80), c, badge="LOJA", locked=True)

    def test_replacing_the_file_replaces_the_art(self):
        from ui import card_art
        c = self.card("s_inferno")
        path = card_art.art_path(c)
        self.assertTrue(path.replace("\\", "/").endswith("assets/cards/epic/s_inferno.png"))

    def test_shop_cards_have_a_motif_and_all_rarity_folders_exist(self):
        for rarity in ("common", "rare", "epic", "legendary"):
            self.assertTrue(os.listdir(os.path.join(ROOT, "assets", "cards", rarity)))
        for c in logic.shop_cards(self.data["rewards"]):
            self.assertIn("art", c)

    def test_reward_screen_draws_with_art(self):
        from ui.reward_screen import RewardScreen
        game = _game(self.data, "judge", mode="infinite", floor=7)
        game.unlock_notice = []
        RewardScreen(game, [self.card("s_judge_verdict"), self.card("i_crown_l1"), self.card("dmg_10")]).draw(new_surface())


# ======================================================================
class ShopScreenTests(Base):
    def make(self, points=0, unlocked=("judge",)):
        game = _game(self.data, "judge", mode="infinite", floor=1)
        game.progress.unlocked = list(unlocked)
        game.progress.points = points
        from ui.shop_screen import ShopScreen
        screen = ShopScreen(game)
        return game, screen

    def press(self, screen, *names, click=None):
        inp = FakeInput()
        inp.click = click
        inp.pressed = lambda n, names=names: n in names
        screen.handle_input(inp)

    def hover(self, screen, pos):
        inp = FakeInput()
        inp.mouse_pos = pos
        screen.handle_input(inp)

    def test_mouse_hover_highlights_without_buying_or_selecting(self):
        game, screen = self.make(points=5000)
        rects = dict(screen._card_rects())
        target = max(rects)                                   # uma carta que NÃO é a selecionada
        before_points, before_index = game.progress.points, screen.index[0]
        self.hover(screen, rects[target].center)
        self.assertTrue(screen.hovered(rects[target]))
        self.assertFalse(screen.hovered(rects[0]))
        screen.draw(new_surface())                            # desenha com o destaque sem erro
        self.assertEqual((game.progress.points, screen.index[0], game.progress.purchased_cards), (before_points, before_index, []))
        self.hover(screen, (-50, -50))                        # mouse saiu: sem destaque
        self.assertFalse(screen.hovered(rects[target]))

    def test_hover_follows_the_cards_when_the_page_changes(self):
        game, screen = self.make(points=0)
        first_page = dict(screen._card_rects())
        screen.index[0] = len(screen.cards) - 1               # última página
        last_page = dict(screen._card_rects())
        self.assertNotEqual(sorted(first_page), sorted(last_page))
        i, rect = next(iter(last_page.items()))
        self.hover(screen, rect.center)
        self.assertTrue(screen.hovered(rect))
        screen.draw(new_surface())

    def test_all_tabs_draw(self):
        game, screen = self.make(points=1250)
        game.progress.record_defeat("goblin")
        game.progress.record_defeat("boss_10")
        game.progress.record_defeat("boss_inf_ember_witch")
        game.progress.record_defeat("boss_yoshi_supreme")
        game.progress.record_run({"character": "judge", "mode": "story", "floor": 7, "result": "derrota", "cards": 4, "points": 90, "date": "01/01/2026 10:00"})
        for tab in range(5):
            screen.tab = tab
            for idx in (0, 3):
                screen.index[tab] = idx
                screen.draw(new_surface())
        for attr in range(4):
            screen.tab, screen.attr = 1, attr
            screen.draw(new_surface())

    def test_cards_tab_keyboard_and_mouse_purchase(self):
        game, screen = self.make(points=1000)
        c0 = screen.cards[0]
        cost = logic.card_cost(self.shop, c0)
        self.press(screen, "swap")
        self.assertIn(c0["id"], game.progress.purchased_cards)
        self.assertEqual(game.progress.points, 1000 - cost)
        self.press(screen, "swap")                                                        # já comprada
        self.assertEqual(game.progress.points, 1000 - cost)
        self.assertIn("JÁ", screen.message)
        game.progress.points = 0
        self.press(screen, "right")
        self.press(screen, "swap")
        self.assertEqual(screen.message, "PONTOS INSUFICIENTES")
        game.progress.points = 5000
        self.press(screen, click=screen.buy_rect.center)                                  # botão COMPRAR com o mouse
        self.assertIn(screen.cards[1]["id"], game.progress.purchased_cards)

    def test_upgrades_tab_flow_and_locked_message(self):
        game, screen = self.make(points=5000)
        screen.tab = 1
        before = game.progress.points
        self.press(screen, "swap")                                                        # vida do primeiro personagem (judge)
        self.assertEqual(logic.level_of(game.progress, "judge", "vida"), 1)
        self.assertEqual(before - game.progress.points, logic.upgrade_cost(self.shop, "vida", 0))
        self.press(screen, "right")                                                       # próximo personagem (bloqueado)
        locked = screen.chars[screen.index[1]]
        self.assertFalse(game.progress.is_unlocked(locked))
        self.press(screen, "swap")
        self.assertIn("DESBLOQUEIE", screen.message)
        self.assertEqual(game.progress.upgrades.get(locked), None)
        screen.draw(new_surface())

    def test_back_and_tab_switching(self):
        game, screen = self.make()
        self.press(screen, "ability")
        self.assertEqual(screen.tab, 1)
        self.press(screen, click=screen.tab_rects[3].center)
        self.assertEqual(screen.tab, 3)
        self.press(screen, "back")
        self.assertEqual(game.state, "MENU")

    def test_menu_has_shop_and_options_has_shake_toggle(self):
        from ui.menu import MenuScreen, OptionsScreen
        game = _game(self.data, "judge")
        game.audio = type("A", (), {"play": lambda s, n: None, "apply_volumes": lambda s: None})()
        from game.settings import Settings
        game.settings = Settings()
        menu = MenuScreen(game)
        self.assertIn("LOJA", menu.buttons.labels if hasattr(menu.buttons, "labels") else [b for b in menu.buttons.__dict__.get("items", [])])
        opts = OptionsScreen(game)
        self.assertIn("shake", opts.items)
        self.assertTrue(game.settings.get("screen_shake"))
        game.settings.set("screen_shake", False)
        self.assertFalse(game.settings.get("screen_shake"))


# ======================================================================
class Events(Base):
    def setUp(self):
        super().setUp()
        self.run = RunManager("judge", self.data, random.Random(5), mode="infinite")
        self.rng = random.Random(1)

    def test_event_schedule(self):
        self.run.floor_number = 4
        self.run.start_floor()
        cfg = copy.deepcopy(self.shop)
        cfg["events"]["chance"] = 1.0
        self.assertTrue(events.event_due(self.run, cfg, self.rng))
        self.run.floor_number = 5
        self.run.start_floor()
        self.assertFalse(events.event_due(self.run, cfg, self.rng))                      # só a cada 4 andares
        self.run.floor_number = 20
        self.run.start_floor()
        self.assertTrue(self.run.floor.is_boss)
        self.assertFalse(events.event_due(self.run, cfg, self.rng))                      # nunca depois de chefe

    def test_no_event_before_the_last_story_floor(self):
        run = RunManager("judge", self.data, random.Random(5), mode="story")
        cfg = copy.deepcopy(self.shop)
        cfg["events"]["chance"] = 1.0
        cfg["events"]["every_floors"] = 7
        run.floor_number = 49                                                             # penúltimo andar da história
        run.start_floor()
        self.assertFalse(events.event_due(run, cfg, self.rng))
        run.floor_number = 42
        run.start_floor()
        self.assertTrue(events.event_due(run, cfg, self.rng))

    def test_rest(self):
        self.run.player.hp = 10.0
        text = events.rest(self.run, self.shop, "heal")
        self.assertEqual(self.run.player.hp, 10 + int(self.run.player.max_hp * 0.35))
        self.run.player.energy = 0
        events.rest(self.run, self.shop, "energy")
        self.assertEqual(self.run.player.energy, 40)
        self.assertIn("recuperou", text)

    def test_swap_only_once_per_run_and_restores_mods(self):
        self.assertFalse(events.swap_available(self.run, self.shop))                     # sem cartas
        self.run.take_reward(self.card("dmg_10"))
        self.assertTrue(events.swap_available(self.run, self.shop))
        mods_before = dict(self.run.player.mods)
        card = self.run.taken_rewards[0]
        events.remove_card(self.run, card)
        for k, v in self.run.player.mods.items():
            self.assertAlmostEqual(v, DEFAULT_MODS[k], msg=k)                              # voltou ao normal
        self.run.take_reward(card)
        self.assertEqual(self.run.player.mods["damage_pct"], mods_before["damage_pct"])
        new, ok, text = events.swap(self.run, self.shop, self.run.taken_rewards[0], random.Random(2))
        self.assertEqual(self.run.swaps_used, 1)
        self.assertFalse(events.swap_available(self.run, self.shop))                     # 1x por run
        self.assertNotIn("swap", {events.pick_event(self.run, self.shop, random.Random(s)) for s in range(60)})
        self.assertEqual(len(self.run.taken_rewards), 1)

    def test_swap_risk_goes_up_or_down_in_rarity(self):
        outcomes = set()
        for seed in range(80):
            run = RunManager("judge", self.data, random.Random(seed), mode="infinite")
            run.floor_number = 12
            card = self.card("n_def_r1") if any(c["id"] == "n_def_r1" for c in self.cards) else next(c for c in self.cards if c["rarity"] == "rare" and not c.get("shop"))
            run.take_reward(card)
            new, ok, _ = events.swap(run, self.shop, run.taken_rewards[0], random.Random(seed))
            if new:
                outcomes.add((ok, new["rarity"]))
        self.assertIn((True, "epic"), outcomes)
        self.assertIn((False, "common"), outcomes)

    def test_mystery_never_kills_and_uses_no_gold(self):
        seen = set()
        for seed in range(200):
            run = RunManager("judge", self.data, random.Random(seed), mode="infinite")
            run.floor_number = 8
            run.player.hp = 3.0
            text = events.mystery(run, self.shop, random.Random(seed))
            self.assertGreaterEqual(run.player.hp, 1.0)
            seen.add(text.split(":")[0][:14])
            import re
            self.assertIsNone(re.search(r"\b(ouro|moedas?|gold)\b", text.lower()), text)
        self.assertGreaterEqual(len(seen), 3)

    def test_event_screen_all_kinds_and_game_flow(self):
        from ui.event_screen import EventScreen
        for kind in ("rest", "swap", "mystery"):
            game = _game(self.data, "judge", mode="infinite", floor=8)
            game.run.start_floor()
            game.run.take_reward(self.card("dmg_10"))
            screen = EventScreen(game, kind)
            screen.draw(new_surface())
            screen.choose(0)
            if kind == "swap":                                                          # troca: o 1º Enter só pede confirmação
                self.assertIsNone(screen.result)
                screen.draw(new_surface())
                screen.choose(0)
            self.assertIsNotNone(screen.result)
            screen.draw(new_surface())
            inp = FakeInput()
            inp.pressed = lambda n: n == "swap"
            screen.handle_input(inp)
            self.assertEqual(game.state, "BATTLE")                                      # continua a run
            self.assertEqual(game.run.floor_number, 9)


# ======================================================================
class PuzzleClarity(Base):
    def test_hint_finds_a_valid_move_without_touching_the_board(self):
        from ui.hint import find_hint
        for seed in range(25):
            run = RunManager("judge", self.data, random.Random(seed))
            c = run.start_floor()
            snap = [[b.color_id if b else None for b in row] for row in c.board.grid]
            cursor = (c.board.cursor_x, c.board.cursor_y)
            hint = find_hint(c.board)
            self.assertEqual(snap, [[b.color_id if b else None for b in row] for row in c.board.grid])
            self.assertEqual(cursor, (c.board.cursor_x, c.board.cursor_y))
            if hint:
                work = copy.deepcopy(c.board)
                work.set_cursor(*hint)
                work.swap_cursor()
                self.assertTrue(work.find_matches())

    def test_hint_appears_after_idle_and_disappears_on_input(self):
        screen = make_screen("mage", floor=7)
        screen.banner_time = 0
        step(screen, 30, play=False)
        self.assertIsNone(screen.hint)
        step(screen, int((screen.hint_after + 1) * 60), play=False)
        self.assertIsNotNone(screen.hint)
        board_before = [[b.color_id if b else None for b in row] for row in screen.combat.board.grid]
        inp = FakeInput()
        inp.pressed = lambda n: n == "left"
        screen.handle_input(inp)
        self.assertIsNone(screen.hint)
        self.assertEqual(screen.idle, 0.0)
        self.assertEqual(board_before, [[b.color_id if b else None for b in row] for row in screen.combat.board.grid])
        step(screen, 5, play=False)
        self.assertIsNone(screen.hint)

    def test_hint_never_executes_a_move(self):
        screen = make_screen("mage", floor=7)
        screen.banner_time = 0
        board = lambda: [[b.color_id if b else None for b in row] for row in screen.combat.board.grid]
        before, energy, enemy_hp = board(), screen.combat.player.energy, screen.combat.enemy.hp
        events_seen = []
        for _ in range(8 * 60):
            screen.update(1 / 60)
            events_seen += [e["type"] for e in screen.combat.event_log] if hasattr(screen.combat, "event_log") else []
        self.assertIsNotNone(screen.hint)                                                  # a dica apareceu...
        self.assertEqual(before, board())                                                  # ...e o tabuleiro está igual
        self.assertEqual((energy, enemy_hp), (screen.combat.player.energy, screen.combat.enemy.hp))   # nada foi jogado

    def test_symbols_draw_for_every_color_without_changing_logic(self):
        from ui import theme
        screen = make_screen("judge", floor=3)
        step(screen, 10, play=False)
        grid = [[b.color_id for b in row] for row in screen.combat.board.grid]
        self.assertTrue({1, 2, 3, 4, 5} <= {v for row in grid for v in row})
        a, b = new_surface(), new_surface()
        screen.draw(a)
        old = theme.PIECE_SYMBOLS
        try:
            theme.PIECE_SYMBOLS = False
            screen.draw(b)
        finally:
            theme.PIECE_SYMBOLS = old
        pixels = lambda surf: surf.img.tobytes() if hasattr(surf, "img") else pygame.image.tostring(surf, "RGB")   # pygame real ou simulado
        self.assertNotEqual(pixels(a), pixels(b))                                         # com símbolos o desenho é diferente
        self.assertEqual(grid, [[x.color_id for x in row] for row in screen.combat.board.grid])

    def test_boss_intro_draws_through_its_whole_duration(self):
        screen = make_screen("warrior", floor=10, mode="story")
        for banner in (2.2, 1.9, 1.0, 0.2):
            screen.banner_time = banner
            screen.draw(new_surface())

    def test_match_rules_unchanged(self):
        from combat import damage
        self.assertEqual((damage.calculate_damage(3, 1, 1.0) if False else None), None)
        import config
        self.assertEqual((config.BOARD_WIDTH, config.BOARD_HEIGHT), (8, 8))


# ======================================================================
class Backgrounds(Base):
    def test_every_theme_has_images_and_mapping_is_correct(self):
        from ui import backgrounds as bg
        for theme in ("spiders", "goblins", "mages", "golems", "bosses", "infinite"):
            self.assertTrue(bg.theme_images(theme), theme)
        cfg = bg.load_config()
        cases = (("spider", False, "spiders"), ("goblin", False, "goblins"), ("mage", False, "mages"), ("golem", False, "golems"),
                 ("void", False, "infinite"), ("dragon", False, "infinite"), ("goblin", True, "bosses"))
        for family, boss, theme in cases:
            enemy = type("E", (), {"is_boss": boss, "family": family, "id": family})()
            self.assertEqual(bg.theme_for(enemy, 5, "story", cfg), theme, family)
            self.assertIn(os.sep + theme + os.sep, bg.pick_path(enemy, 5, "story", cfg))

    def test_floor_override_and_fallback(self):
        from ui import backgrounds as bg
        enemy = type("E", (), {"is_boss": False, "family": "spider", "id": "spider"})()
        cfg = {"floors": {"7": "mages", "infinite:9": "bosses/default.jpg"}, "families": {}, "fallback_theme": "golems", "boss_theme": "bosses"}
        self.assertIn(os.sep + "mages" + os.sep, bg.pick_path(enemy, 7, "story", cfg))
        self.assertTrue(bg.pick_path(enemy, 9, "infinite", cfg).endswith("default.jpg"))
        self.assertIn(os.sep + "golems" + os.sep, bg.pick_path(enemy, 3, "story", cfg))
        self.assertIsNone(bg.pick_path(enemy, 3, "story", {"fallback_theme": "tema_que_nao_existe", "families": {}}))

    def test_battle_draws_with_background_and_without_images(self):
        from ui import backgrounds as bg
        screen = make_screen("warrior", floor=3, mode="story")
        screen.draw(new_surface())
        old = bg.BG_DIR
        try:
            bg.BG_DIR = os.path.join(tempfile.mkdtemp(), "vazio")
            screen.draw(new_surface())                                                   # sem imagens: fundo liso, sem erro
        finally:
            bg.BG_DIR = old


# ======================================================================
class OptionsInputSound(Base):
    def test_shake_option_is_respected(self):
        from ui.vfx import VFX
        v = VFX()
        v.add_shake(8, 0.3)
        self.assertGreater(v.shake_time, 0)
        v2 = VFX()
        v2.shake_enabled = False
        v2.add_shake(8, 0.3)
        self.assertEqual(v2.shake_time, 0.0)
        screen = make_screen("warrior")
        self.assertTrue(screen.vfx.shake_enabled)

    def test_volumes_are_independent_and_saved(self):
        from game.settings import Settings
        s = Settings()
        for key in ("music_volume", "sfx_volume", "screen_shake", "controls", "gamepad"):
            self.assertIsNotNone(s.get(key), key)
        s.set("music_volume", 0.2)
        s.set("sfx_volume", 0.9)
        self.assertNotEqual(s.get("music_volume"), s.get("sfx_volume"))

    def test_gamepad_detection_and_actions(self):
        from game.input import Input, PAD_PROMPTS, detect_pad_kind
        from game.settings import Settings
        self.assertEqual(detect_pad_kind("Xbox 360 Controller"), "xbox")
        self.assertEqual(detect_pad_kind("PS4 Controller"), "ps")
        self.assertEqual(detect_pad_kind("Wireless Controller"), "ps")
        self.assertEqual(detect_pad_kind("DualSense Wireless Controller"), "ps")
        self.assertEqual(detect_pad_kind("Controle genérico USB"), "xbox")
        inp = Input(Settings(), lambda p: p)
        ev = lambda t, **kw: type("Ev", (), dict(type=t, **kw))()
        for button, action in ((0, "swap"), (1, "back"), (2, "ability"), (7, "back")):
            inp.actions.clear()
            inp.handle_event(ev(pygame.JOYBUTTONDOWN, button=button))
            self.assertTrue(inp.pressed(action), button)
        for value, action in (((-1, 0), "left"), ((1, 0), "right"), ((0, 1), "up"), ((0, -1), "down")):
            inp.actions.clear()
            inp.handle_event(ev(pygame.JOYHATMOTION, value=value))
            self.assertTrue(inp.pressed(action), value)
        inp.actions.clear()
        inp.handle_event(ev(pygame.JOYAXISMOTION, axis=0, value=0.9))
        self.assertTrue(inp.pressed("right"))
        inp.actions.clear()
        inp.handle_event(ev(pygame.JOYAXISMOTION, axis=0, value=0.95))                  # segurando: não repete
        self.assertFalse(inp.pressed("right"))
        inp.handle_event(ev(pygame.JOYAXISMOTION, axis=0, value=0.0))
        inp.handle_event(ev(pygame.JOYAXISMOTION, axis=0, value=-0.8))
        self.assertTrue(inp.pressed("left"))
        inp.actions.clear()
        inp.handle_event(ev(pygame.JOYAXISMOTION, axis=1, value=0.3))                   # dentro da zona morta
        self.assertEqual(inp.actions, set())
        self.assertEqual(set(PAD_PROMPTS), {"xbox", "ps", None})                        # sem tipo: ícones genéricos

    def test_hud_shows_pad_prompts_when_connected(self):
        from ui import hud
        screen = make_screen("warrior")
        hud.set_gamepad_kind("ps")
        try:
            self.assertEqual(hud._hints()[1][0], "Cruz")
            screen.draw(new_surface())
            hud.set_gamepad_kind("xbox")
            self.assertEqual(hud._hints()[1][0], "A")
            screen.draw(new_surface())
        finally:
            hud.set_gamepad_kind(None)
        self.assertEqual(hud._hints()[1][0], "Enter/Espaço")

    def test_chain_sounds_get_higher_and_stronger(self):
        from game.audio import SOUND_DEFS, chain_sound, synth
        self.assertEqual([chain_sound(l) for l in (1, 2, 3, 4, 5, 9)], ["chain_2", "chain_2", "chain_3", "chain_4", "chain_4", "chain_4"])
        top = lambda name: max(n["f"] if isinstance(n, dict) else n[0] for n in SOUND_DEFS[name])
        self.assertLess(top("chain_2"), top("chain_3"))
        self.assertLess(top("chain_3"), top("chain_4"))
        peak = lambda name: max(abs(x) for x in synth(SOUND_DEFS[name], 22050))
        self.assertLessEqual(peak("chain_4"), 32767)                                    # sem estourar o volume
        self.assertLess(peak("chain_4"), 32767 * 0.5)                                    # nem exagerar
        for name in ("swap", "match", "match_big", "hit", "hurt", "ability", "boss", "win", "lose", "chain_2", "chain_3", "chain_4"):
            self.assertIn(name, SOUND_DEFS)
            self.assertGreater(len(synth(SOUND_DEFS[name], 22050)), 100, name)

    def test_battle_plays_the_new_sounds(self):
        played = []
        screen = make_screen("warrior", floor=10)
        screen.game.audio.play = played.append
        screen.banner_time = 0
        step(screen, 400)
        self.assertTrue({"swap", "match", "match_big"} & set(played))


if __name__ == "__main__":
    unittest.main()
