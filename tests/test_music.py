"""tests/test_music.py - escolha da música por situação (sem pygame, em pasta temporária)."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import music_map
from game.state import GameState


class Run:
    def __init__(self, mode):
        self.mode = mode


class MusicChoice(unittest.TestCase):
    def folder(self, *names):
        folder = Path(tempfile.mkdtemp())
        for name in names:
            (folder / name).write_bytes(b"x")
        return [folder]

    def test_silence_without_files(self):
        self.assertIsNone(music_map.find_track("battle", self.folder()))

    def test_generic_music_is_used_everywhere(self):
        folders = self.folder("music.ogg")
        for situation in music_map.SITUATION_TRACKS:
            self.assertEqual(music_map.find_track(situation, folders).name, "music.ogg")

    def test_specific_beats_fallbacks(self):
        folders = self.folder("music.ogg", "battle.mp3", "boss.ogg", "menu.wav")
        self.assertEqual(music_map.find_track("menu", folders).name, "menu.wav")
        self.assertEqual(music_map.find_track("battle", folders).name, "battle.mp3")
        self.assertEqual(music_map.find_track("boss", folders).name, "boss.ogg")
        self.assertEqual(music_map.find_track("victory", folders).name, "music.ogg")

    def test_fallback_chain_for_infinite_boss(self):
        self.assertEqual(music_map.find_track("infinite_boss", self.folder("boss.ogg", "battle.ogg")).name, "boss.ogg")
        self.assertEqual(music_map.find_track("infinite_boss", self.folder("infinite.ogg", "battle.ogg")).name, "infinite.ogg")
        self.assertEqual(music_map.find_track("infinite_boss", self.folder("battle.ogg")).name, "battle.ogg")
        self.assertEqual(music_map.find_track("reward", self.folder("battle.ogg")).name, "battle.ogg")

    def test_extension_priority_and_second_folder(self):
        folders = self.folder("menu.mp3", "menu.ogg") + self.folder("battle.ogg")
        self.assertEqual(music_map.find_track("menu", folders).name, "menu.ogg")
        self.assertEqual(music_map.find_track("battle", folders).name, "battle.ogg")

    def test_find_tracks_lists_all_candidates_in_order(self):
        folders = self.folder("music.ogg", "battle.mp3", "boss.ogg")
        names = [p.name for p in music_map.find_tracks("boss", folders)]
        self.assertEqual(names, ["boss.ogg", "battle.mp3", "music.ogg"])
        self.assertEqual(music_map.find_tracks("menu", self.folder()), [])

    def test_detect_format_by_content_not_extension(self):
        folder = Path(tempfile.mkdtemp())
        cases = {"a.ogg": (b"OggS" + b"\0" * 40 + b"vorbis", "ogg"), "b.ogg": (b"ID3\x03" + b"\0" * 20, "mp3"),
                 "c.ogg": (b"\xff\xfb\x90\x00" + b"\0" * 20, "mp3"), "d.ogg": (b"RIFF\0\0\0\0WAVEfmt ", "wav"),
                 "e.ogg": (b"OggS" + b"\0" * 20 + b"OpusHead", "opus"), "f.ogg": (b"\0\0\0\x20ftypM4A ", "m4a"),
                 "g.ogg": (b"lixo qualquer", None)}
        for name, (data, expected) in cases.items():
            (folder / name).write_bytes(data)
            self.assertEqual(music_map.detect_format(folder / name), expected, name)
        self.assertIsNone(music_map.detect_format(folder / "nao_existe.ogg"))

    def test_situation_for_states(self):
        f = music_map.situation_for
        for state in (GameState.MENU, GameState.OPTIONS, GameState.CHARACTER_SELECT):
            self.assertEqual(f(state), "menu")
        self.assertEqual(f(GameState.BATTLE, Run("story"), False), "battle")
        self.assertEqual(f(GameState.BATTLE, Run("story"), True), "boss")
        self.assertEqual(f(GameState.BATTLE, Run("infinite"), False), "infinite")
        self.assertEqual(f(GameState.BATTLE, Run("infinite"), True), "infinite_boss")
        self.assertEqual(f(GameState.REWARD), "reward")
        self.assertEqual(f(GameState.VICTORY), "victory")
        self.assertEqual(f(GameState.GAME_OVER), "game_over")


if __name__ == "__main__":
    unittest.main()
