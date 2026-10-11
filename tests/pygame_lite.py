"""
tests/pygame_lite.py - mini "pygame" feito em cima do Pillow, SÓ para desenvolvimento e testes.

Serve para rodar e RENDERIZAR a interface (HUD, efeitos) em computadores sem pygame
(ex.: servidores de teste) e gerar capturas de tela em PNG. NÃO é usado pelo jogo:
no jogo de verdade o pygame é o oficial.

Cobre só o que a pasta ui/ usa: Surface, Rect, draw.*, font.Font, time.get_ticks, image.frombytes.
Limitações (de propósito): sem recorte (set_clip é ignorado) e sem antialiasing nas formas.
"""
import math
import os
import sys
import types

from PIL import Image, ImageChops, ImageDraw, ImageFont

SRCALPHA = 0x00010000
<<<<<<< HEAD
KEYDOWN, KEYUP, MOUSEBUTTONDOWN = 768, 769, 1025
JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN, JOYDEVICEADDED, JOYDEVICEREMOVED = 1536, 1538, 1540, 1541, 1542
QUIT = 256
=======
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
BLEND_ADD = 1
BLEND_RGBA_ADD = 6
BLEND_RGB_ADD = 1
BLEND_RGBA_MULT = 8

_FONT_PATHS = ("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
               "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")


def _rgba(color, alpha=None):
    c = tuple(int(v) for v in color)
    if len(c) == 3:
        c = c + (255 if alpha is None else alpha,)
    return c


class Rect:
    _ANCHORS = ("topleft", "topright", "bottomleft", "bottomright", "midtop", "midbottom", "midleft", "midright", "center")

    def __init__(self, *args):
        if len(args) == 1:
            args = tuple(args[0])
        if len(args) == 2:
            args = (args[0][0], args[0][1], args[1][0], args[1][1])
        object.__setattr__(self, "x", args[0])
        object.__setattr__(self, "y", args[1])
        object.__setattr__(self, "w", args[2])
        object.__setattr__(self, "h", args[3])

    def __iter__(self):
        return iter((self.x, self.y, self.w, self.h))

    def __getitem__(self, i):
        return (self.x, self.y, self.w, self.h)[i]

    def __repr__(self):
        return f"Rect({self.x}, {self.y}, {self.w}, {self.h})"

    def __getattr__(self, name):
        x, y, w, h = self.x, self.y, self.w, self.h
        table = {"width": w, "height": h, "left": x, "top": y, "right": x + w, "bottom": y + h, "size": (w, h),
                 "centerx": x + w // 2, "centery": y + h // 2, "center": (x + w // 2, y + h // 2),
                 "topleft": (x, y), "topright": (x + w, y), "bottomleft": (x, y + h), "bottomright": (x + w, y + h),
                 "midtop": (x + w // 2, y), "midbottom": (x + w // 2, y + h), "midleft": (x, y + h // 2),
                 "midright": (x + w, y + h // 2)}
        if name in table:
            return table[name]
        raise AttributeError(name)

    def __setattr__(self, name, value):
        w, h = self.w, self.h
        if name in ("x", "y", "w", "h"):
            object.__setattr__(self, name, value)
        elif name in ("width", "height"):
            object.__setattr__(self, "w" if name == "width" else "h", value)
        elif name in ("left", "top"):
            object.__setattr__(self, "x" if name == "left" else "y", value)
        elif name == "right":
            object.__setattr__(self, "x", value - w)
        elif name == "bottom":
            object.__setattr__(self, "y", value - h)
        elif name == "centerx":
            object.__setattr__(self, "x", value - w // 2)
        elif name == "centery":
            object.__setattr__(self, "y", value - h // 2)
        elif name in self._ANCHORS:
            px, py = value
            fx = {"topleft": 0, "bottomleft": 0, "midleft": 0, "topright": w, "bottomright": w, "midright": w}.get(name, w // 2)
            fy = {"topleft": 0, "topright": 0, "midtop": 0, "bottomleft": h, "bottomright": h, "midbottom": h}.get(name, h // 2)
            object.__setattr__(self, "x", px - fx)
            object.__setattr__(self, "y", py - fy)
        else:
            raise AttributeError(name)

    def collidepoint(self, pos):
        return self.x <= pos[0] < self.x + self.w and self.y <= pos[1] < self.y + self.h

    def inflate(self, dx, dy):
        return Rect(self.x - dx // 2, self.y - dy // 2, self.w + dx, self.h + dy)

    def copy(self):
        return Rect(self.x, self.y, self.w, self.h)

    def move(self, dx, dy):
        return Rect(self.x + dx, self.y + dy, self.w, self.h)


class Surface:
    def __init__(self, size, flags=0):
        self.alpha_mode = bool(flags & SRCALPHA)
        self.img = Image.new("RGBA" if self.alpha_mode else "RGB", (int(size[0]), int(size[1])), (0, 0, 0, 0) if self.alpha_mode else (0, 0, 0))
        self._alpha = 255
        self._clip = None
        self._backup = None

    @classmethod
    def from_image(cls, img):
        s = cls(img.size, SRCALPHA)
        s.img = img.convert("RGBA")
        return s

    def _draw(self):
        return ImageDraw.Draw(self.img)

    def _c(self, color):
        c = _rgba(color)
        return c if self.alpha_mode else c[:3]

    def get_size(self):
        return self.img.size

    def get_width(self):
        return self.img.size[0]

    def get_height(self):
        return self.img.size[1]

    def get_rect(self, **kw):
        r = Rect(0, 0, *self.img.size)
        for k, v in kw.items():
            setattr(r, k, v)
        return r

    def convert_alpha(self):
        return self

    def convert(self):
        return self

    def copy(self):
        s = Surface(self.img.size, SRCALPHA if self.alpha_mode else 0)
        s.img = self.img.copy()
        s._alpha = self._alpha
        return s

    def set_alpha(self, value):
        self._alpha = 255 if value is None else int(value)

    def get_at(self, pos):
        px = self.img.getpixel((int(pos[0]), int(pos[1])))
        return px if len(px) == 4 else px + (255,)

    def get_clip(self):
        return self._clip or self.get_rect()

    def set_clip(self, rect):
        """Recorte simulado: guarda uma cópia e, ao remover o recorte, restaura tudo que ficou fora dele."""
        full = (0, 0, *self.img.size)
        if rect is None or tuple(Rect(rect)) == full:
            if self._clip is not None and self._backup is not None:
                c = self._clip
                box = (c.x, c.y, c.x + c.w, c.y + c.h)
                restored = self._backup
                restored.paste(self.img.crop(box), box)
                self.img = restored
            self._clip, self._backup = None, None
        else:
            self._clip, self._backup = Rect(rect), self.img.copy()

    def fill(self, color, rect=None):
        if rect is None:
            self.img.paste(self._c(color), (0, 0, *self.img.size))
        else:
            r = Rect(rect)
            self.img.paste(self._c(color), (r.x, r.y, r.x + r.w, r.y + r.h))

    def blit(self, src, dest, area=None, special_flags=0):
        pos = (dest.x, dest.y) if isinstance(dest, Rect) else (int(dest[0]), int(dest[1]))
        img = src.img
        if area is not None:
            a = Rect(area)
            img = img.crop((a.x, a.y, a.x + a.w, a.y + a.h))
        if src.alpha_mode and src._alpha < 255:
            img = img.copy()
            alpha = img.getchannel("A").point(lambda v: v * src._alpha // 255)
            img.putalpha(alpha)
        if special_flags in (BLEND_ADD, BLEND_RGBA_ADD):
            box = (pos[0], pos[1], pos[0] + img.size[0], pos[1] + img.size[1])
            base = self.img.crop(box).convert("RGB")
            add = ImageChops.add(base, img.convert("RGB"))
            self.img.paste(add if not self.alpha_mode else add.convert("RGBA"), pos)
            return
        if self.alpha_mode:
            region = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
            region.paste(img.convert("RGBA"), pos)
            self.img = Image.alpha_composite(self.img, region)
        elif src.alpha_mode:
            self.img.paste(img.convert("RGB"), pos, img.getchannel("A"))
        else:
            self.img.paste(img, pos)

    def save(self, path):
        self.img.convert("RGB").save(path)


# ---------------------------------------------------------------- draw
def _rect_draw(surface, color, rect, width=0, border_radius=0):
    r = Rect(rect)
    if r.w <= 0 or r.h <= 0:
        return
    box = [r.x, r.y, r.x + r.w - 1, r.y + r.h - 1]
    d, c = surface._draw(), surface._c(color)
    kw = {"fill": c if width == 0 else None, "outline": c if width else None, "width": width or 1}
    if border_radius:
        d.rounded_rectangle(box, radius=min(border_radius, r.w // 2, r.h // 2), **kw)
    else:
        d.rectangle(box, **kw)


def _circle_draw(surface, color, center, radius, width=0):
    cx, cy = center
    r = max(0, radius)
    if r <= 0:
        return
    c = surface._c(color)
    surface._draw().ellipse([cx - r, cy - r, cx + r, cy + r], fill=c if width == 0 else None,
                            outline=c if width else None, width=width or 1)


def _ellipse_draw(surface, color, rect, width=0):
    r = Rect(rect)
    if r.w <= 0 or r.h <= 0:
        return
    c = surface._c(color)
    surface._draw().ellipse([r.x, r.y, r.x + r.w - 1, r.y + r.h - 1], fill=c if width == 0 else None,
                            outline=c if width else None, width=width or 1)


def _line_draw(surface, color, p0, p1, width=1):
    surface._draw().line([tuple(p0), tuple(p1)], fill=surface._c(color), width=max(1, int(width)))


def _lines_draw(surface, color, closed, points, width=1):
    pts = [tuple(p) for p in points] + ([tuple(points[0])] if closed else [])
    surface._draw().line(pts, fill=surface._c(color), width=max(1, int(width)), joint="curve")


def _polygon_draw(surface, color, points, width=0):
    pts = [tuple(p) for p in points]
    c = surface._c(color)
    if width == 0:
        surface._draw().polygon(pts, fill=c)
    else:
        surface._draw().line(pts + [pts[0]], fill=c, width=width, joint="curve")


def _arc_draw(surface, color, rect, start, stop, width=1):
    r = Rect(rect)
    surface._draw().arc([r.x, r.y, r.x + r.w - 1, r.y + r.h - 1], -math.degrees(stop), -math.degrees(start),
                        fill=surface._c(color), width=max(1, int(width)))


# ---------------------------------------------------------------- font
class Font:
    def __init__(self, path, size):
        px = max(6, int(size * 0.6875))         # o pygame reduz a fonte padrão assim
        for candidate in ((path,) if path else ()) + _FONT_PATHS:
            if candidate and os.path.exists(candidate):
                self.font = ImageFont.truetype(candidate, px)
                break
        else:
            self.font = ImageFont.load_default(px)
        asc, desc = self.font.getmetrics()
        self.height = asc + desc

    def size(self, text):
        return (int(self.font.getlength(text)) + 1, self.height)

    def get_height(self):
        return self.height

    def render(self, text, antialias, color, background=None):
        w, h = self.size(text)
        s = Surface((max(1, w), h), SRCALPHA)
        ImageDraw.Draw(s.img).text((0, 0), text, font=self.font, fill=_rgba(color))
        return s


# ---------------------------------------------------------------- módulo
_state = {"ticks": 0}


def _frombytes(data, size, fmt):
    return Surface.from_image(Image.frombytes(fmt, size, data))


def _transform_scale(surface, size, dest=None):
    s = Surface(size, SRCALPHA if surface.alpha_mode else 0)
    s.img = surface.img.resize(tuple(size))
    return s


def install():
    """Registra este módulo como 'pygame' (só se o pygame de verdade não existir)."""
    mod = types.ModuleType("pygame")
    mod.Surface, mod.Rect, mod.SRCALPHA = Surface, Rect, SRCALPHA
    mod.BLEND_ADD, mod.BLEND_RGBA_ADD, mod.BLEND_RGB_ADD, mod.BLEND_RGBA_MULT = BLEND_ADD, BLEND_RGBA_ADD, BLEND_RGB_ADD, BLEND_RGBA_MULT
    mod.draw = types.SimpleNamespace(rect=_rect_draw, circle=_circle_draw, ellipse=_ellipse_draw, line=_line_draw,
                                     lines=_lines_draw, polygon=_polygon_draw, arc=_arc_draw)
    mod.font = types.SimpleNamespace(Font=Font, init=lambda: None)
    mod.time = types.SimpleNamespace(get_ticks=lambda: _state["ticks"])
<<<<<<< HEAD
    mod.image = types.SimpleNamespace(frombytes=_frombytes, fromstring=_frombytes, load=lambda p: Surface.from_image(Image.open(p)))
    mod.transform = types.SimpleNamespace(scale=_transform_scale, smoothscale=_transform_scale)
    mod.KEYDOWN, mod.KEYUP, mod.MOUSEBUTTONDOWN, mod.QUIT = KEYDOWN, KEYUP, MOUSEBUTTONDOWN, QUIT
    mod.JOYAXISMOTION, mod.JOYHATMOTION, mod.JOYBUTTONDOWN = JOYAXISMOTION, JOYHATMOTION, JOYBUTTONDOWN
    mod.JOYDEVICEADDED, mod.JOYDEVICEREMOVED = JOYDEVICEADDED, JOYDEVICEREMOVED
    mod.key = types.SimpleNamespace(key_code=lambda name: sum(ord(c) * (i + 1) for i, c in enumerate(name)))
    mod.mouse = types.SimpleNamespace(get_pos=lambda: (0, 0))
    mod.joystick = types.SimpleNamespace(init=lambda: None, get_count=lambda: 0)
=======
    mod.image = types.SimpleNamespace(frombytes=_frombytes, fromstring=_frombytes)
    mod.transform = types.SimpleNamespace(scale=_transform_scale)
>>>>>>> 04f156348c1ca60f01179e24fd224faa5e8fad3f
    mod.lite = True
    mod.set_ticks = lambda ms: _state.__setitem__("ticks", int(ms))
    sys.modules["pygame"] = mod
    return mod
