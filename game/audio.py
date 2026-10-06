"""
game/audio.py - ÁUDIO (música, efeitos, volume).

Os efeitos são PLACEHOLDERS: bipes gerados no código, sem arquivos.
A MÚSICA de cada situação (menu, batalha, chefe...) é escolhida em game/music_map.py:
coloque os arquivos em assets/sounds/bgm/ (veja os nomes lá).
Se o computador não tiver áudio, o jogo continua normalmente, mudo.
"""
import array
import logging
import math

import pygame

from game import music_map

log = logging.getLogger(__name__)

# nome -> lista de (frequência em Hz, duração em segundos)
SOUND_DEFS = {
    "swap": [(300, 0.03)],
    "match": [(660, 0.07), (880, 0.09)],
    "chain": [(523, 0.06), (659, 0.06), (784, 0.06), (1047, 0.14)],
    "hit": [(220, 0.08), (160, 0.06)],
    "hurt": [(140, 0.12), (100, 0.14)],
    "ability": [(440, 0.05), (660, 0.05), (990, 0.14)],
    "enemy_ability": [(200, 0.10), (150, 0.10), (120, 0.14)],
    "select": [(600, 0.04)],
    "fail": [(150, 0.08)],
    "reward": [(523, 0.08), (659, 0.08), (784, 0.16)],
    "win": [(523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.25)],
    "lose": [(400, 0.15), (300, 0.15), (200, 0.3)],
}


class AudioManager:
    def __init__(self, settings):
        self.settings = settings
        self.enabled = False
        self.sounds = {}
        self.current_track = None      # arquivo de música tocando agora
        self._failed = set()           # arquivos que o pygame não conseguiu carregar
        self._music_file = None        # arquivo aberto quando a música é carregada pelo conteúdo
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 1, 512)
            self.rate, self.size, self.channels = pygame.mixer.get_init()
            if self.size != -16:
                raise RuntimeError("formato de áudio não suportado")
            self.enabled = True
        except Exception:
            log.exception("Áudio indisponível; o jogo seguirá sem som.")
            return
        self._build_sounds()
        self.apply_volumes()

    def _make_tone(self, notes, volume=0.35):
        samples = array.array("h")
        for freq, duration in notes:
            total = int(self.rate * duration)
            for i in range(total):
                t = i / self.rate
                wave = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0  # onda quadrada
                envelope = 1.0 - i / total
                value = int(32767 * volume * wave * envelope)
                for _ in range(self.channels):
                    samples.append(value)
        return pygame.mixer.Sound(buffer=samples.tobytes())

    def _build_sounds(self):
        for name, notes in SOUND_DEFS.items():
            try:
                self.sounds[name] = self._make_tone(notes)
            except Exception:
                log.exception("Falha ao criar o som %s", name)

    def play_situation(self, situation):
        """Toca a música da situação (\"menu\", \"battle\", \"boss\"...). Se já é a que está
        tocando, não reinicia. Se um arquivo não carregar (codec/arquivo ruim), tenta o próximo
        da lista de reservas e registra o motivo em logs/game.log. Sem arquivo nenhum: silêncio."""
        if not self.enabled:
            return
        candidates = [p for p in music_map.find_tracks(situation) if p not in self._failed]
        wanted = candidates[0] if candidates else None
        if wanted == self.current_track:
            return
        try:
            if wanted is None:
                self.current_track = None
                pygame.mixer.music.stop()
                log.info("Sem música para '%s' (coloque arquivos em assets/sounds/bgm).", situation)
                return
        except Exception:
            log.exception("Não foi possível parar a música")
            return
        for path in candidates:
            if path == self.current_track:       # o reserva já está tocando: não reinicia
                return
            try:
                self._load_music(path)
                pygame.mixer.music.play(-1, fade_ms=400)
                pygame.mixer.music.set_volume(float(self.settings.get("music_volume")))
                self.current_track = path
                log.info("Música '%s': %s", situation, path.name)
                return
            except Exception as err:
                self._failed.add(path)
                log.error("Não foi possível tocar %s (%s). Reexporte como .ogg Vorbis ou .mp3 padrão.", path, err)
        self.current_track = None
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass

    def _load_music(self, path):
        """Carrega pelo formato REAL do arquivo (pelo conteúdo). Se a extensão mentir
        (ex.: um .mp3 renomeado para .ogg), o pygame recebe a dica certa do formato."""
        real = music_map.detect_format(path)
        ext = path.suffix.lower().lstrip(".")
        if real in ("ogg", "mp3", "wav", "flac") and real != ext:
            log.warning("%s tem extensão .%s mas o conteúdo é %s; carregando como %s.", path.name, ext, real, real)
            handle = open(path, "rb")
            try:
                pygame.mixer.music.load(handle, real)
            except Exception:
                handle.close()
                raise
            old, self._music_file = self._music_file, handle
            if old:
                old.close()
            return
        pygame.mixer.music.load(str(path))
        if self._music_file:
            self._music_file.close()
            self._music_file = None

    def apply_volumes(self):
        if not self.enabled:
            return
        sfx = float(self.settings.get("sfx_volume"))
        for sound in self.sounds.values():
            sound.set_volume(sfx)
        try:
            pygame.mixer.music.set_volume(float(self.settings.get("music_volume")))
        except Exception:
            pass

    def play(self, name):
        if self.enabled and name in self.sounds:
            self.sounds[name].play()
