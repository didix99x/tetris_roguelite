"""
ui/gif_loader.py - carrega GIFs ANIMADOS (o pygame sozinho só lê o 1º quadro).

Usa a biblioteca Pillow para separar os quadros do GIF. Os quadros são
convertidos e redimensionados UMA vez e guardados em cache.
Se o arquivo não existir (ou o Pillow faltar), devolve None e o jogo usa o
desenho provisório.
"""
import logging

import pygame

from paths import asset_path

log = logging.getLogger(__name__)

try:
    from PIL import Image, ImageSequence
except ImportError:           # sem Pillow: o jogo continua com os desenhos provisórios
    Image = None
    ImageSequence = None

_cache = {}


class GifAnimation:
    def __init__(self, frames, durations):
        self.frames = frames                 # lista de Surfaces do pygame
        self.durations = durations           # milissegundos de cada quadro
        self.total = max(1, sum(durations))

    def frame_at(self, ms):
        t = ms % self.total
        for frame, duration in zip(self.frames, self.durations):
            if t < duration:
                return frame
            t -= duration
        return self.frames[-1]


def _to_surface(pil_image):
    data = pil_image.tobytes()
    size = pil_image.size
    maker = getattr(pygame.image, "frombytes", None) or pygame.image.fromstring
    return maker(data, size, "RGBA").convert_alpha()


def load_gif(relative_path, box_w, box_h):
    """Carrega assets/<relative_path> ajustado a uma caixa box_w x box_h
    (mantém a proporção). Devolve GifAnimation ou None."""
    key = (relative_path, box_w, box_h)
    if key in _cache:
        return _cache[key]
    animation = None
    path = asset_path(*relative_path.split("/"))
    if Image is not None and path.exists():
        try:
            with Image.open(path) as gif:
                frames, durations = [], []
                for frame in ImageSequence.Iterator(gif):
                    rgba = frame.convert("RGBA")
                    scale = min(box_w / rgba.width, box_h / rgba.height)
                    size = (max(1, int(rgba.width * scale)), max(1, int(rgba.height * scale)))
                    rgba = rgba.resize(size, Image.LANCZOS)
                    frames.append(_to_surface(rgba))
                    durations.append(max(20, int(frame.info.get("duration", 100))))
            if frames:
                animation = GifAnimation(frames, durations)
        except Exception:
            log.exception("Não foi possível carregar o GIF %s", relative_path)
    _cache[key] = animation
    return animation
