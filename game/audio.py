"""
game/audio.py - ÁUDIO (música, efeitos, volume).

Os efeitos são SINTETIZADOS no código (sem arquivos). Para usar seus próprios sons, coloque
assets/sounds/sfx/<nome>.wav (ou .ogg); os nomes estão em SOUND_DEFS.
A MÚSICA de cada situação (menu, batalha, chefe...) é escolhida em game/music_map.py:
coloque os arquivos em assets/sounds/bgm/ (veja os nomes lá).
Se o computador não tiver áudio, o jogo continua normalmente, mudo.
"""
import array
import logging
import math
import os
import random

import pygame

from game import music_map
from paths import base_dir

log = logging.getLogger(__name__)

# nome -> lista de notas. Cada nota: (frequência Hz, duração s)  OU  dict:
#   {"f": Hz, "d": s, "to": Hz final (varredura), "w": "sine"|"square"|"saw"|"tri", "v": volume 0-1,
#    "h": [(múltiplo, volume)] harmônicos, "n": mistura de ruído 0-1}
# Para TROCAR um som por um arquivo seu: coloque assets/sounds/sfx/<nome>.wav (ou .ogg). Veja COMO_EDITAR_O_JOGO.md.
def _n(f, d, **kw):
    note = {"f": f, "d": d}
    note.update(kw)
    return note


SOUND_DEFS = {
    "swap": [_n(380, 0.05, to=520, w="tri", v=0.5)],
    "match": [_n(660, 0.07, w="sine", h=[(2, .3)]), _n(880, 0.10, w="sine", h=[(2, .3), (3, .1)])],
    "match_big": [_n(660, 0.06, h=[(2, .3)]), _n(880, 0.06, h=[(2, .3)]), _n(1175, 0.16, h=[(2, .35), (3, .15)])],
    # CHAINS: quanto maior o nível, mais agudo e mais forte (x1 = som normal de match)
    "chain_2": [_n(587, 0.05, h=[(2, .3)]), _n(740, 0.05, h=[(2, .3)]), _n(880, 0.10, h=[(2, .3)])],
    "chain_3": [_n(659, 0.05, h=[(2, .35)]), _n(830, 0.05, h=[(2, .35)]), _n(988, 0.05, h=[(2, .35)]), _n(1318, 0.13, h=[(2, .4), (3, .2)], v=0.9)],
    "chain_4": [_n(196, 0.07, w="saw", v=0.7), _n(659, 0.05, h=[(2, .4)]), _n(830, 0.05, h=[(2, .4)]), _n(988, 0.05, h=[(2, .4)]),
                _n(1318, 0.07, h=[(2, .4), (3, .2)]), _n(1760, 0.24, h=[(2, .5), (3, .25)], v=1.0), _n(110, 0.18, n=0.6, to=60, v=0.8)],
    "hit": [_n(240, 0.09, to=110, w="saw", n=0.45, v=0.8)],
    "hurt": [_n(160, 0.14, to=70, w="saw", n=0.5, v=0.9), _n(90, 0.12, w="square", v=0.5)],
    "ability": [_n(330, 0.20, to=990, w="saw", h=[(2, .3)], v=0.8), _n(1320, 0.14, h=[(2, .4)], v=0.7)],
    "enemy_ability": [_n(220, 0.18, to=120, w="saw", n=0.2), _n(120, 0.16, w="square", v=0.6)],
    "select": [_n(600, 0.04, w="sine", v=0.7)],
    "fail": [_n(170, 0.10, to=110, w="saw", v=0.7)],
    "reward": [_n(523, 0.08, h=[(2, .3)]), _n(659, 0.08, h=[(2, .3)]), _n(784, 0.18, h=[(2, .3), (3, .15)])],
    "win": [_n(523, 0.10, h=[(2, .3)]), _n(659, 0.10, h=[(2, .3)]), _n(784, 0.10, h=[(2, .3)]), _n(1047, 0.30, h=[(2, .4), (3, .2)])],
    "lose": [_n(400, 0.16, w="saw", v=0.7), _n(300, 0.16, w="saw", v=0.7), _n(200, 0.34, w="saw", to=130, v=0.8)],
    "boss": [_n(95, 0.45, to=55, w="saw", n=0.25, v=0.9), _n(140, 0.30, to=80, w="square", v=0.5)],
}
SOUND_DEFS["chain"] = SOUND_DEFS["chain_2"]            # nome antigo continua existindo


def chain_sound(level):
    """Nome do som de uma chain: x2, x3, x4 ou mais (maior = mais agudo e intenso)."""
    return f"chain_{max(2, min(4, int(level)))}"


def synth(notes, rate, channels=1, volume=0.35):
    """Gera as amostras (array 'h') de uma lista de notas. Sem pygame: pode ser testada isoladamente."""
    samples = array.array("h")
    rng = random.Random(7)                                   # ruído sempre igual (som estável)
    for note in notes:
        if not isinstance(note, dict):
            note = {"f": note[0], "d": note[1], "w": "square"}
        freq, dur = float(note["f"]), float(note["d"])
        end = float(note.get("to", freq))
        shape, vol, noise = note.get("w", "sine"), float(note.get("v", 1.0)), float(note.get("n", 0.0))
        harmonics = note.get("h", ())
        total = max(1, int(rate * dur))
        phase = 0.0
        attack = min(0.008, dur / 4)
        for i in range(total):
            k = i / total
            phase += 2 * math.pi * (freq + (end - freq) * k) / rate
            if shape == "square":
                wave = 1.0 if math.sin(phase) >= 0 else -1.0
            elif shape == "saw":
                wave = ((phase / math.pi) % 2.0) - 1.0
            elif shape == "tri":
                wave = 2.0 * abs(((phase / math.pi) % 2.0) - 1.0) - 1.0
            else:
                wave = math.sin(phase)
            for mult, hv in harmonics:
                wave += hv * math.sin(phase * mult)
            if harmonics:
                wave /= 1.0 + sum(hv for _, hv in harmonics)
            if noise:
                wave = wave * (1 - noise) + (rng.random() * 2 - 1) * noise
            t = i / rate
            envelope = min(1.0, t / attack) * (1.0 - k) ** 1.3              # ataque curto + queda suave
            value = int(32767 * volume * vol * wave * envelope)
            value = max(-32767, min(32767, value))
            for _ in range(channels):
                samples.append(value)
    return samples


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
        return pygame.mixer.Sound(buffer=synth(notes, self.rate, self.channels, volume).tobytes())

    def _build_sounds(self):
        """Cria os sons por código; se existir assets/sounds/sfx/<nome>.wav|ogg, usa o arquivo no lugar."""
        for name, notes in SOUND_DEFS.items():
            try:
                self.sounds[name] = self._load_sfx_file(name) or self._make_tone(notes)
            except Exception:
                log.exception("Falha ao criar o som %s", name)

    def _load_sfx_file(self, name):
        for ext in (".wav", ".ogg"):
            path = os.path.join(str(base_dir()), "assets", "sounds", "sfx", name + ext)
            if os.path.exists(path):
                try:
                    return pygame.mixer.Sound(path)
                except Exception:
                    log.exception("Não foi possível carregar o som %s", path)
        return None

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
