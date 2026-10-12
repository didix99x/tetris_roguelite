"""
tests/test_final_update.py - atualização final: 9 personagens, desbloqueio, inimigos do Infinito,
personagens como inimigos, Boss especial (2%).

Rodar:  python -m unittest tests.test_final_update -v
"""
import json
import os
import random
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
for _var in ("APPDATA", "XDG_DATA_HOME", "HOME", "USERPROFILE"):   # saves de teste, não mexe nos seus (Windows usa APPDATA)
    os.environ[_var] = tempfile.mkdtemp()

from characters import character_title, create_character, unlock_hint
from combat.combat import IDLE
from game.save import Progress
from rewards.reward_pool import roll_rewards
from run.floor import build_infinite_floor, build_special_boss
from run.run_manager import RunManager
from tests.test_logic import bot_move, load_data, run_until_idle

ROSTER = [("judge", "Juiz", "—"), ("bard", "Tulipa", "Bardo"), ("assassin", "Tali", "Assassina"),
          ("cleric", "Maizona", "Clériga"), ("blacksmith", "Caique", "Ferreiro"), ("mage", "Breno", "Mago"),
          ("archer", "Romulo", "Arqueiro"), ("warrior", "Matheuzim", "Guerreiro"), ("monk", "Yuko", "Monge")]


def fresh_progress(data, path=None):
    progress = Progress(data["characters"])
    progress.path = path or (type(progress.path)(tempfile.mkdtemp()) / "progress.json")
    progress.unlocked = []
    progress.update_unlocks()
    return progress


class Roster(unittest.TestCase):
    def setUp(self):
        self.data = load_data()

    def test_original_nine_characters_unchanged_and_yoshi_added_last(self):
        chars = self.data["characters"]
        listed = [(c, chars[c]["name"], chars[c]["class"]) for c in chars]
        self.assertEqual(listed[:9], ROSTER)                          # os 9 originais, intactos e na mesma ordem
        self.assertEqual(listed[9:], [("yoshi", "Yoshi", "Samurai")])  # Yoshi: 10º personagem (desbloqueio especial)

    def test_only_judge_starts_unlocked(self):
        progress = fresh_progress(self.data)
        self.assertEqual(progress.unlocked, ["judge"])
        for cid, _, _ in ROSTER[1:]:
            self.assertFalse(progress.is_unlocked(cid), cid)

    def test_every_character_has_passive_ability_cost_and_text(self):
        for cid, c in self.data["characters"].items():
            for key in ("passive_name", "passive_text", "ability_name", "ability_text", "ability_cost", "max_hp"):
                self.assertTrue(c.get(key), (cid, key))
            self.assertGreater(c["ability_cost"], 0)

    def test_dynamic_unlock_hint_and_title(self):
        chars = self.data["characters"]
        self.assertEqual(unlock_hint(chars["bard"]), "Derrote Tulipa no Modo Infinito para desbloquear este personagem.")
        self.assertEqual(unlock_hint(chars["cleric"]), "Derrote Maizona no Modo Infinito para desbloquear este personagem.")
        self.assertEqual(unlock_hint(chars["judge"]), "")
        self.assertEqual(character_title(chars["bard"]), "Tulipa - Bardo")
        self.assertEqual(character_title(chars["assassin"]), "Tali - Assassina")
        self.assertEqual(character_title(chars["judge"]), "Juiz")
        self.assertEqual(len({unlock_hint(chars[c]) for c, _, _ in ROSTER[1:]}), 8)    # nenhuma repetida

    def test_art_names_are_defined(self):
        for cid, c in self.data["characters"].items():
            self.assertTrue(c.get("image"), cid)


class Abilities(unittest.TestCase):
    """Cada personagem: a habilidade gasta o custo e produz o efeito prometido."""

    def setUp(self):
        self.data = load_data()

    def combat(self, cid, seed=1):
        run = RunManager(cid, self.data, random.Random(seed), mode="infinite")
        run.floor_number = 3
        combat = run.start_floor()
        combat.enemy.hp = combat.enemy.max_hp = 5000
        combat.enemy_timer = 999
        combat.player.energy = 100
        return combat

    def use(self, combat):
        cost = combat.player.current_ability_cost()
        before = combat.player.energy
        self.assertTrue(combat.use_ability())
        run_until_idle(combat)
        self.assertAlmostEqual(before - combat.player.energy, cost, delta=60)   # (energia pode subir pelos matches)
        return cost

    def test_energy_is_spent_and_blocked_when_insufficient(self):
        for cid in self.data["characters"]:
            combat = self.combat(cid)
            cost = combat.player.current_ability_cost()
            combat.player.energy = cost - 1
            self.assertFalse(combat.use_ability(), cid)
            combat.player.energy = cost
            self.assertTrue(combat.use_ability(), cid)
            self.assertLess(combat.player.energy, cost, cid)

    def test_judge(self):
        c = self.combat("judge")
        hp, timer = c.enemy.hp, c.enemy_timer
        self.use(c)
        self.assertEqual(hp - c.enemy.hp, 35)
        self.assertAlmostEqual(c.enemy_timer, timer + 2.5, places=1)
        self.assertAlmostEqual(c.player.damage_multiplier(1, False), 1.10)

    def test_cleric(self):
        c = self.combat("cleric")
        c.player.hp = 20.0
        c.poison_time = 5.0
        blocks = list(c.board.blocks())
        blocks[0].web_time = 9.0
        blocks[1].kind, blocks[1].color_id = "stone", 6
        self.use(c)
        self.assertGreater(c.player.hp, 20 + 0.25 * c.player.max_hp - 3)
        self.assertEqual(c.poison_time, 0.0)
        self.assertEqual((c.board.count_stones(), c.board.count_webbed()), (0, 0))
        self.assertGreater(c.player.mods["regen_per_sec"], 0.7)

    def test_blacksmith(self):
        c = self.combat("blacksmith")
        base = c.player.mods["damage_reduction_pct"]
        self.assertAlmostEqual(base, 0.12)
        for i in range(6):
            c.player.energy = 100
            c.player.hp = 50.0
            c.ability_cd = 0.0                      # (passaram os 3 s de recarga entre um uso e outro)
            self.use(c)
        self.assertAlmostEqual(c.player.mods["damage_reduction_pct"], 0.12 + 4 * 0.06)   # limite de 4 usos
        self.assertGreater(c.player.hp, 50)

    def test_archer(self):
        c = self.combat("archer")
        hp = c.enemy.hp
        self.assertAlmostEqual(c.player.mods["crit_chance"], 0.10)
        self.use(c)
        self.assertEqual(hp - c.enemy.hp, 45)
        c.player.energy = 0
        c.player.on_match(c, 3, [3])
        self.assertEqual(c.player.energy, 8)
        c.player.on_match(c, 2, [3])
        self.assertEqual(c.player.energy, 8)

    def test_monk(self):
        c = self.combat("monk")
        c.player.energy = 0
        c.player.on_match(c, 3, [3])
        self.assertEqual(c.player.energy, 10)           # (3-1)*5
        hp = c.enemy.hp
        c.player.energy = 100
        c.chain.best = 0
        c.use_ability()
        self.assertEqual(hp - c.enemy.hp, 20)
        run_until_idle(c)
        c.chain.best = 3
        c.player.energy = 100
        c.ability_cd = 0.0                          # (passaram os 3 s de recarga)
        hp = c.enemy.hp
        c.use_ability()
        self.assertEqual(hp - c.enemy.hp, 20 + 10 * 3)

    def test_existing_four_still_work(self):
        c = self.combat("warrior")
        hp = c.enemy.hp
        self.use(c)
        self.assertEqual(hp - c.enemy.hp, 45)
        c = self.combat("assassin")
        self.use(c)
        c = self.combat("mage")
        self.use(c)
        c = self.combat("bard")
        c.enemy_timer = 3.0
        self.use(c)
        self.assertGreaterEqual(c.enemy_timer, 7.9)

    def test_all_nine_survive_a_bot_fight(self):
        for cid in self.data["characters"]:
            rng = random.Random(4)
            c = self.combat(cid, seed=4)
            c.enemy.hp = c.enemy.max_hp = 150
            c.enemy_timer = 999
            for _ in range(4000):
                if c.phase == IDLE:
                    if c.player.can_use_ability():
                        c.use_ability()
                    else:
                        bot_move(c, rng)
                c.update(1 / 20)
                c.pop_events()
                if c.result:
                    break
            self.assertEqual(c.result, "win", cid)


class UnlockByDefeat(unittest.TestCase):
    def setUp(self):
        self.data = load_data()

    def test_unlock_persists_after_save_and_reload_and_run_loss(self):
        progress = fresh_progress(self.data)
        path = progress.path
        self.assertTrue(progress.unlock_character("bard"))
        self.assertFalse(progress.unlock_character("bard"))
        progress.save()
        again = Progress(self.data["characters"])
        again.path = path
        again.load()
        again.update_unlocks()
        self.assertTrue(again.is_unlocked("bard"))
        self.assertTrue(again.is_unlocked("judge"))
        self.assertFalse(again.is_unlocked("cleric"))

    def test_old_save_relocks_characters_that_were_given_automatically(self):
        progress = Progress(self.data["characters"])
        path = type(progress.path)(tempfile.mkdtemp()) / "progress.json"
        path.write_text(json.dumps({"best_floor": 50, "wins": 1, "unlocked": ["warrior", "mage", "assassin", "bard"]}),
                        encoding="utf-8")
        progress.path = path
        progress.unlocked = []
        progress.load()
        progress.update_unlocks()
        self.assertEqual(progress.unlocked, ["judge"])
        self.assertTrue(progress.is_infinite_unlocked())       # o resto do progresso é mantido

    def test_unknown_character_is_not_unlocked(self):
        self.assertFalse(fresh_progress(self.data).unlock_character("ninguem"))


class InfiniteContent(unittest.TestCase):
    def setUp(self):
        self.data = load_data()

    def build(self, floor, seed, own="judge", locked=None):
        if locked is None:                          # padrão: todos bloqueados (só os bloqueados são chefes de desbloqueio)
            locked = list(self.data["characters"])
        return build_infinite_floor(floor, self.data["enemies"], self.data["floors"], random.Random(seed), own,
                                    self.data["characters"], locked)

    def test_exclusive_enemies_appear_when_their_floor_is_reached(self):
        seen = {}
        for floor in (1, 5, 15, 25, 36):
            seen[floor] = {self.build(floor, s).enemy.id for s in range(500)}
        self.assertIn("fairy", seen[1])
        self.assertNotIn("zombie", seen[1])
        self.assertIn("zombie", seen[5])
        self.assertNotIn("dragon", seen[15])
        self.assertIn("necromancer", seen[15])
        self.assertIn("dragon", seen[25])
        self.assertEqual(self.data["enemies"]["enemies"]["fairy"]["name"], "Fada")
        self.assertEqual(self.data["enemies"]["enemies"]["dragon"]["name"], "Dragão")

    def test_exclusive_enemies_are_not_in_story_mode(self):
        from run.floor import build_floor
        for floor in range(1, 50):
            for seed in range(20):
                f = build_floor(floor, self.data["enemies"], self.data["floors"], random.Random(seed))
                self.assertNotIn(f.enemy.id, ("fairy", "zombie", "necromancer", "dragon"))

    def test_characters_never_appear_as_regular_enemies_only_as_bosses(self):
        for floor in (1, 5, 8, 15, 23, 38, 47, 61, 99):
            for seed in range(300):
                f = self.build(floor, seed, locked=list(self.data["characters"]))
                self.assertFalse(f.is_boss)
                self.assertIsNone(f.enemy.character_id, (floor, seed))
        for floor in (10, 20):                                       # até o andar 20: nunca personagem
            seen = {self.build(floor, s, locked=list(self.data["characters"])).enemy.character_id for s in range(800)}
            self.assertEqual(seen, {None}, floor)
        for floor in (30, 60):                                       # acima do andar 20 eles aparecem como chefe
            seen = {self.build(floor, s, locked=list(self.data["characters"])).enemy.character_id for s in range(800)}
            self.assertTrue(seen - {None}, floor)

    def test_character_boss_uses_data_from_characters_json(self):
        for seed in range(800):
            f = self.build(60, seed, locked=["bard"])
            if f.enemy.character_id == "bard":
                self.assertTrue(f.is_boss and f.enemy.is_boss)
                self.assertEqual(f.enemy.name, "Tulipa - Bardo")
                self.assertEqual(f.enemy.art_folder, "characters")
                self.assertEqual(f.enemy.color, tuple(self.data["characters"]["bard"]["color"]))
                return
        self.fail("Tulipa nunca apareceu como chefe")

    def _boss_pick_pool(self, floor, roll, locked="all", weight=2, own="judge", chance=0.3, after=20):
        """Lista EXATA de onde o chefe é sorteado, dado o resultado `roll` (0..1) da etapa 'é personagem?'.
        Sem aleatoriedade e sem depender do seu balanceamento."""
        import copy
        from run.floor import _pick_infinite_boss

        class Capture:
            def random(self):
                return roll

            def choice(self, seq):
                self.seq = list(seq)
                return self.seq[0]

        if locked == "all":
            locked = list(self.data["characters"])
        floors = copy.deepcopy(self.data["floors"])
        floors.setdefault("infinite", {}).update({"include_character_bosses": True, "exclude_own_character": True,
                                                  "locked_character_boss_weight": weight,
                                                  "character_boss_chance": chance, "locked_character_boss_chance": chance,
                                                  "character_boss_after_floor": after})
        rng = Capture()
        _pick_infinite_boss(floor, self.data["enemies"], floors, rng, own, self.data["characters"], locked)
        return [entry[0] for entry in rng.seq]

    def test_character_boss_chance_is_30_percent_and_only_after_floor_20(self):
        for floor in (10, 20):                       # até o andar 20: sempre chefe da história, mesmo com sorte máxima
            ids = self._boss_pick_pool(floor, roll=0.0)
            self.assertTrue(all(i.startswith("boss_") and not i.startswith("boss_char_") for i in ids), (floor, ids))
        for floor in (30, 40, 100):
            self.assertTrue(all(i.startswith("boss_char_") for i in self._boss_pick_pool(floor, roll=0.29)), floor)
            self.assertTrue(all(not i.startswith("boss_char_") for i in self._boss_pick_pool(floor, roll=0.30)), floor)
            self.assertTrue(all(not i.startswith("boss_char_") for i in self._boss_pick_pool(floor, roll=0.99)), floor)

    def test_character_boss_rate_is_about_50_percent_in_real_draws(self):
        # chance configurada em data/floors.json > infinite > locked_character_boss_chance (50% enquanto há bloqueados)
        for floor in (30, 70):
            hits = sum(1 for seed in range(5000) if self.build(floor, seed).enemy.character_id)
            self.assertAlmostEqual(hits / 5000, 0.50, delta=0.04, msg=floor)
        for floor in (10, 20):
            self.assertFalse(any(self.build(floor, seed).enemy.character_id for seed in range(3000)))

    def test_special_boss_follows_the_same_floor_rule(self):
        from run.floor import build_special_boss
        for floor in (3, 15, 20):
            for seed in range(400):
                f = build_special_boss(floor, self.data["enemies"], self.data["floors"], random.Random(seed),
                                       "judge", self.data["characters"], [])
                self.assertIsNone(f.enemy.character_id, (floor, seed))

    def test_chance_and_floor_are_configurable(self):
        self.assertTrue(all(i.startswith("boss_char_") for i in self._boss_pick_pool(10, 0.0, chance=1.0, after=0)))
        self.assertTrue(all(not i.startswith("boss_char_") for i in self._boss_pick_pool(60, 0.0, chance=0.0)))

    def test_only_locked_characters_are_unlock_bosses_and_own_never(self):
        ids = self._boss_pick_pool(60, 0.0, locked=["bard", "cleric"])
        self.assertEqual(sorted(ids), ["boss_char_bard", "boss_char_cleric"])        # só os bloqueados entram no sorteio
        ids = self._boss_pick_pool(60, 0.0, locked=["bard", "judge"], own="judge")
        self.assertEqual(ids, ["boss_char_bard"])                                    # o próprio nunca
        ids = self._boss_pick_pool(60, 0.0, locked=[])                               # todos desbloqueados: nenhum personagem-chefe
        self.assertTrue(all(not i.startswith("boss_char_") for i in ids), ids)
        # e, na prática, o sorteio real nunca devolve o próprio personagem
        for seed in range(500):
            self.assertNotEqual(self.build(60, seed, own="judge", locked=["bard"]).enemy.character_id, "judge")

    def test_every_character_can_be_a_boss_with_correct_name(self):
        names = {}
        for seed in range(2000):
            f = self.build(60, seed, own="judge", locked=list(self.data["characters"]))
            if f.enemy.character_id:
                names[f.enemy.character_id] = f.enemy.name
        self.assertEqual(set(names), {c for c, _, _ in ROSTER} - {"judge"})
        self.assertEqual(names["assassin"], "Tali - Assassina")
        self.assertEqual(names["monk"], "Yuko - Monge")

    def test_new_enemies_work_in_combat(self):
        run = RunManager("judge", self.data, random.Random(2), mode="infinite")
        for eid in ("fairy", "zombie", "necromancer", "dragon", "boss_char_cleric"):
            from enemies.enemy import Enemy
            from run.progression import scale_stats
            if eid.startswith("boss_char_"):
                f = build_special_boss(30, self.data["enemies"], self.data["floors"], random.Random(1), "judge",
                                       self.data["characters"], None)
                enemy = f.enemy
            else:
                d = self.data["enemies"]["enemies"][eid]
                enemy = Enemy(eid, d, scale_stats(d, 20, self.data["floors"]["scaling"]))
            from combat.combat import Combat
            combat = Combat(run.player, enemy, 20, random.Random(3))
            combat.enemy_timer = 0
            for _ in range(400):
                combat.update(1 / 20)
                combat.pop_events()
            self.assertGreater(combat.player.max_hp, 0)


class SpecialBoss(unittest.TestCase):
    def setUp(self):
        self.data = load_data()

    def test_chance_is_two_percent_and_configurable(self):
        self.assertEqual(self.data["floors"]["infinite"]["special_boss_chance"], 0.02)

    def test_special_boss_is_a_normal_boss_but_stronger(self):
        floors = self.data["floors"]
        f = build_special_boss(30, self.data["enemies"], floors, random.Random(5), "judge", self.data["characters"], None)
        self.assertTrue(f.is_boss and f.enemy.is_boss)
        self.assertIn("(Especial)", f.enemy.name)

    def test_only_legendary_cards_after_special_boss(self):
        for floor in (1, 3, 10, 40):
            for seed in range(30):
                cards = roll_rewards(self.data["rewards"], 3, floor, random.Random(seed), only_rarity="legendary")
                self.assertEqual(len(cards), 3)
                self.assertTrue(all(c["rarity"] == "legendary" for c in cards))

    def test_normal_rewards_unchanged(self):
        seen = set()
        for seed in range(300):
            seen |= {c["rarity"] for c in roll_rewards(self.data["rewards"], 3, 10, random.Random(seed))}
        self.assertEqual(seen, {"common", "rare", "epic", "legendary"})


if __name__ == "__main__":
    unittest.main()
