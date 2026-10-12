"""
tests/test_enemy_art.py - confere as ARTES de inimigos, chefes, super chefes e personagens.

    python -m unittest tests.test_enemy_art -v

Cobre: cada ID tem arquivo de arte e o jogo o encontra; as artes dos personagens continuam
em assets/images/characters; o mapa de artes é coerente; e a pasta assets/ copiada para
release\\Game (como o build faz) é achada pelo jogo "congelado" (PyInstaller).
Não gera nem testa o .exe de verdade (isso só dá para fazer no Windows).
"""
import json
import os
import shutil
import sys
import tempfile
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from tests import visual_harness  # noqa: F401  (instala pygame ou o mini-pygame ANTES de importar ui/)
from bosses.boss import Boss
from enemies.enemy import Enemy
from tests.test_logic import load_data
from ui import portraits

IMAGES = os.path.join(ROOT, "assets", "images")
STATS = {"hp": 1, "damage": 1, "cooldown": 1}

# IDs que NÃO ganharam arte nova (a entrega não tinha imagem para eles). Continuam com o desenho provisório.
# Se você colocar a arte deles, tire o ID daqui.
SEM_ARTE_NOVA = {"spider", "golem", "boss_50"}


def art_file(entity):
    """Primeiro arquivo que o jogo acharia para a entidade (mesma regra de ui/portraits.py)."""
    folder, ids = portraits._art_location(entity)
    for art_id in dict.fromkeys(ids):
        for ext in portraits.ART_EXTENSIONS:
            path = os.path.join(IMAGES, folder, art_id + ext)
            if os.path.exists(path):
                return path
    return None


class Base(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = load_data()
        cls.enemies = cls.data["enemies"]

    def all_entities(self):
        out = []
        for eid, d in self.enemies["enemies"].items():
            out.append((eid, Enemy(eid, d, STATS)))
        for key, d in self.enemies["bosses"].items():
            out.append((f"boss_{key}", Boss(f"boss_{key}", d, STATS)))
        for key, d in self.enemies["infinite_bosses"].items():
            out.append((f"boss_inf_{key}", Boss(f"boss_inf_{key}", d, STATS)))
        return out


class EnemyAndBossArt(Base):
    def test_every_enemy_boss_and_super_boss_has_art_except_known_gaps(self):
        sem_arte = {eid for eid, ent in self.all_entities() if art_file(ent) is None}
        self.assertEqual(sem_arte, SEM_ARTE_NOVA, "IDs sem nenhum arquivo de arte (nem da família)")

    def test_each_id_has_its_own_file_not_a_shared_one(self):
        # todo ID, exceto as lacunas conhecidas e os que dependem da família (Bruxo usa a do Mago), tem arquivo próprio
        sem_proprio_ok = SEM_ARTE_NOVA | {"mage_warlock"}
        usados = {}
        for eid, ent in self.all_entities():
            if eid in sem_proprio_ok:
                continue
            path = art_file(ent)
            self.assertIsNotNone(path, eid)
            self.assertEqual(os.path.splitext(os.path.basename(path))[0], eid, f"{eid} está usando arte de outro ID")
            usados.setdefault(path, []).append(eid)
        for path, ids in usados.items():
            self.assertEqual(len(ids), 1, f"{path} usado por {ids}")

    def test_files_are_valid_images_and_all_different(self):
        from PIL import Image
        digests = {}
        for eid, ent in self.all_entities():
            path = art_file(ent)
            if path is None or os.path.splitext(os.path.basename(path))[0] != eid:
                continue          # sem arte, ou usando a da família (ex.: Bruxo -> Mago Sombrio)
            with Image.open(path) as im:
                im.load()
                self.assertGreaterEqual(min(im.size), 128, path)
                self.assertIsNotNone(im.convert("RGBA").getbbox(), path)
                digests.setdefault(im.convert("RGBA").tobytes(), []).append(eid)
        # A CONFIRMAR: a entrega trouxe o MESMO arquivo para "mimico" (void_mimic) e "espectro lamentoso" (wail_ghost)
        repetidas = [ids for ids in digests.values() if len(ids) > 1 and sorted(ids) != ["void_mimic", "wail_ghost"]]
        self.assertEqual(repetidas, [], "duas entidades com a mesma imagem")

    def test_game_loader_actually_loads_each_art(self):
        # passa pelo mesmo caminho do jogo (ui/portraits._find_animation -> ui/gif_loader.load_gif)
        for eid, ent in self.all_entities():
            if eid in SEM_ARTE_NOVA:
                continue
            animation = portraits._find_animation(ent, 128)
            self.assertIsNotNone(animation, f"o jogo não carregou a arte de {eid}")
            self.assertGreaterEqual(len(animation.frames), 1)

    def test_mapping_file_is_consistent(self):
        with open(os.path.join(ROOT, "tools", "mapa_artes_inimigos.json"), encoding="utf-8") as f:
            mapa = json.load(f)["mapa"]
        destinos = list(mapa.values())
        self.assertEqual(len(destinos), len(set(destinos)), "dois arquivos de origem apontam para o mesmo ID")
        ids_validos = (set(f"enemies/{i}" for i in self.enemies["enemies"])
                       | set(f"bosses/boss_{k}" for k in self.enemies["bosses"])
                       | set(f"bosses/boss_inf_{k}" for k in self.enemies["infinite_bosses"]))
        for destino in destinos:
            self.assertIn(destino, ids_validos, f"{destino} não é um ID do jogo")
            self.assertTrue(os.path.exists(os.path.join(IMAGES, destino + ".png")), destino)


class CharacterArt(Base):
    def test_playable_characters_still_use_the_characters_folder(self):
        for cid, c in self.data["characters"].items():
            if not isinstance(c, dict) or "name" not in c:
                continue
            who = types.SimpleNamespace(char_id=cid, image_id=c.get("image"), color=tuple(c.get("color", (150, 150, 150))), name=c["name"])
            folder, ids = portraits._art_location(who)
            self.assertEqual(folder, "characters", cid)
            path = art_file(who)
            if path is not None:
                self.assertTrue(path.startswith(os.path.join(IMAGES, "characters")), f"{cid} usa arte fora de characters/: {path}")

    def test_character_gifs_are_found_and_untouched_by_enemy_art(self):
        for gif in ("assassin.gif", "bard.gif", "yoshi.gif"):
            self.assertTrue(os.path.exists(os.path.join(IMAGES, "characters", gif)), gif)
        for cid in ("assassin", "bard"):
            c = self.data["characters"][cid]
            who = types.SimpleNamespace(char_id=cid, image_id=c.get("image"), color=(150, 150, 150), name=c["name"])
            self.assertTrue(art_file(who).endswith(cid + ".gif"))
            self.assertIsNotNone(portraits._find_animation(who, 128), cid)
        # nenhum arquivo de inimigo/chefe tem nome de personagem jogável
        # (o inimigo "mage" = Mago Sombrio existe desde sempre e fica em enemies/, sem relação com o personagem Breno)
        ids_de_inimigos = set(self.enemies["enemies"]) | {f"boss_{k}" for k in self.enemies["bosses"]} | {f"boss_inf_{k}" for k in self.enemies["infinite_bosses"]}
        nomes_de_arte_de_personagem = {c.get("image") for c in self.data["characters"].values() if isinstance(c, dict)} - ids_de_inimigos
        for folder in ("enemies", "bosses"):
            for name in os.listdir(os.path.join(IMAGES, folder)):
                base = os.path.splitext(name)[0]
                if base in ("LEIA-ME", ".gitkeep") or not name.lower().endswith(portraits.ART_EXTENSIONS):
                    continue
                self.assertIn(base, ids_de_inimigos, f"{folder}/{name} não é arte de inimigo/chefe")
                self.assertNotIn(base, nomes_de_arte_de_personagem, name)

    def test_character_as_boss_and_yoshi_use_character_art(self):
        yoshi = self.enemies["yoshi"]["story"]
        ent = Boss("boss_yoshi", yoshi, STATS)
        self.assertEqual(portraits._art_location(ent)[0], "characters")
        self.assertTrue(art_file(ent).endswith("yoshi.gif"))
        supremo = Boss("boss_yoshi_supreme", self.enemies["yoshi"]["infinite"], STATS)
        self.assertTrue(art_file(supremo).endswith("yoshi.gif"))
        # personagem como chefe do Infinito (mesma montagem de run/floor.py): pasta characters/
        c = self.data["characters"]["bard"]
        ent = Boss("boss_char_bard", {"name": c["name"], "color": c.get("color", (150, 150, 150)), "image": c.get("image"),
                                       "art_folder": "characters", "character_id": "bard"}, STATS)
        self.assertEqual(portraits._art_location(ent)[0], "characters")
        self.assertTrue(art_file(ent).endswith("bard.gif"))


class PackagedBuild(Base):
    """Simula o que o build faz: copia assets/ e data/ para release/Game e roda com sys.frozen."""

    def test_assets_copied_like_build_game_bat_are_found_when_frozen(self):
        with open(os.path.join(ROOT, "build_game.bat"), encoding="utf-8", errors="ignore") as f:
            bat = f.read().lower()
        self.assertIn("xcopy /e /i /y assets release\\game\\assets", bat)
        self.assertIn("xcopy /e /i /y data release\\game\\data", bat)
        tmp = tempfile.mkdtemp()
        try:
            game = os.path.join(tmp, "release", "Game")
            shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(game, "assets"))
            shutil.copytree(os.path.join(ROOT, "data"), os.path.join(game, "data"))
            import paths
            old_frozen, old_exe = getattr(sys, "frozen", None), sys.executable
            sys.frozen, sys.executable = True, os.path.join(game, "RogueToca.exe")
            try:
                self.assertTrue(paths.is_frozen())
                faltando = []
                for eid, ent in self.all_entities():
                    if eid in SEM_ARTE_NOVA:
                        continue
                    folder, ids = portraits._art_location(ent)
                    achou = any(paths.asset_path("images", folder, i + ext).exists()
                                for i in dict.fromkeys(ids) for ext in portraits.ART_EXTENSIONS)
                    if not achou:
                        faltando.append(eid)
                self.assertEqual(faltando, [])
                for gif in ("assassin.gif", "bard.gif", "yoshi.gif"):
                    self.assertTrue(paths.asset_path("images", "characters", gif).exists(), gif)
            finally:
                sys.executable = old_exe
                if old_frozen is None:
                    del sys.frozen
                else:
                    sys.frozen = old_frozen
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_launcher_checks_assets_folder_that_holds_the_art(self):
        src = open(os.path.join(ROOT, "launcher.py"), encoding="utf-8").read()
        self.assertIn('"assets"', src)
        self.assertIn("RogueToca.exe", src)


if __name__ == "__main__":
    unittest.main()
