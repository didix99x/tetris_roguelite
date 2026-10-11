"""
ui/backgrounds.py - FUNDOS DAS BATALHAS (só visual: nunca interfere no puzzle, na HUD ou nas regras).

Como o fundo é escolhido (data/backgrounds.json):
  1) fundo fixo do andar ("floors": {"7": "mages"} ou {"infinite:100": "bosses/default.jpg"});
  2) chefe  -> tema "bosses";
  3) senão, pela família do inimigo ("families": spider -> spiders, goblin -> goblins...);
  4) senão, o tema "fallback_theme".
Dentro de uma pasta de tema, o jogo alterna entre as imagens conforme o andar. Sem imagem = fundo liso de sempre.
"""
import json
import os

import pygame

import config
from paths import base_dir

ROOT = str(base_dir())          # paths.py: pasta do projeto (dev) ou pasta do .exe (empacotado)
BG_DIR = os.path.join(ROOT, "assets", "backgrounds")
EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")
_config = None
_cache = {}


def load_config():
    global _config
    if _config is None:
        try:
            with open(os.path.join(ROOT, "data", "backgrounds.json"), encoding="utf-8") as f:
                _config = json.load(f)
        except (OSError, ValueError):
            _config = {}
    return _config


def theme_images(theme):
    folder = os.path.join(BG_DIR, theme)
    if not os.path.isdir(folder):
        return []
    return sorted(os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(EXTENSIONS))


def theme_for(enemy, floor_number, mode, cfg=None):
    """Nome do tema (pasta) para esta batalha."""
    cfg = cfg or load_config()
    if enemy.is_boss:
        return cfg.get("boss_theme", "bosses")
    family = getattr(enemy, "family", None) or enemy.id
    return cfg.get("families", {}).get(family, cfg.get("fallback_theme", "infinite"))


def pick_path(enemy, floor_number, mode, cfg=None):
    """Caminho da imagem de fundo (ou None)."""
    cfg = cfg or load_config()
    floors = cfg.get("floors", {})
    for key in (f"{mode}:{floor_number}", str(floor_number)):
        value = floors.get(key)
        if value and not key.startswith("_"):
            direct = os.path.join(BG_DIR, value)
            if os.path.isfile(direct):
                return direct
            images = theme_images(value)
            if images:
                return images[floor_number % len(images)]
    images = theme_images(theme_for(enemy, floor_number, mode, cfg))
    return images[floor_number % len(images)] if images else None


def background_surface(path, dim):
    """Imagem do tamanho da tela, já escurecida (para a HUD e as peças continuarem legíveis). Fica em cache."""
    key = (path, dim)
    surf = _cache.get(key)
    if surf is None:
        if len(_cache) > 12:
            _cache.clear()
        surf = pygame.transform.smoothscale(pygame.image.load(path).convert(), (config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        shade = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
        shade.fill((6, 6, 12, int(dim)))
        surf.blit(shade, (0, 0))
        _cache[key] = surf
    return surf


def draw_background(surface, enemy, floor_number, mode):
    path = pick_path(enemy, floor_number, mode)
    if path:
        try:
            surface.blit(background_surface(path, load_config().get("dim", 150)), (0, 0))
        except (pygame.error, OSError):          # imagem corrompida: segue com o fundo liso
            pass
