"""
ui/card_art.py - ARTE E APARÊNCIA DAS CARTAS (recompensa, Loja e Álbum usam as mesmas funções).

A arte de cada carta é o arquivo  assets/cards/<raridade>/<id_da_carta>.png  (trocar o arquivo = trocar a arte,
sem mexer em código). Se a raridade da carta mudar, o jogo também procura o id nas outras pastas.
A moldura (cor por raridade) é desenhada aqui, por cima.
"""
import os

import pygame

import config
from paths import base_dir
from rewards.reward import rarity_color, rarity_name
from ui.widgets import draw_text, draw_wrapped, get_font

ROOT = str(base_dir())          # paths.py: pasta do projeto (dev) ou pasta do .exe (empacotado)
RARITY_FOLDERS = ("common", "rare", "epic", "legendary")
_cache = {}


def art_path(card):
    """Caminho do arquivo de arte da carta (None se não existir em nenhuma pasta de raridade)."""
    for folder in (card.get("rarity", "common"),) + RARITY_FOLDERS:
        path = os.path.join(ROOT, "assets", "cards", folder, card["id"] + ".png")
        if os.path.exists(path):
            return path
    return None


def card_art(card, size, locked=False):
    """Surface quadrada (size x size) com a arte da carta; locked=True => escurecida (silhueta)."""
    key = (card["id"], size, locked)
    surf = _cache.get(key)
    if surf is None:
        if len(_cache) > 600:
            _cache.clear()
        path = art_path(card)
        if path:
            surf = pygame.transform.smoothscale(pygame.image.load(path).convert_alpha(), (size, size))
        else:                                                    # nunca deveria acontecer (um teste confere); só não quebra o jogo
            surf = pygame.Surface((size, size))
            surf.fill((40, 40, 60))
        if locked:
            surf = surf.copy()
            shade = pygame.Surface((size, size), pygame.SRCALPHA)
            shade.fill((8, 8, 16, 205))
            surf.blit(shade, (0, 0))
            pygame.draw.circle(surf, (120, 120, 150), (size // 2, size // 2 + size // 12), size // 7, 3)       # cadeado
            pygame.draw.rect(surf, (120, 120, 150), (size // 2 - size // 8, size // 2 + size // 12, size // 4, size // 6), border_radius=3)
        _cache[key] = surf
    return surf


def fit_text(surface, text, max_size, color, center, max_width, min_size=20):
    """Escreve o nome encolhendo a fonte até caber em max_width."""
    size = max_size
    while size > min_size and get_font(size).size(text)[0] > max_width:
        size -= 2
    draw_text(surface, text, size, color, center, shadow=True)


def draw_card_face(surface, rect, card, active=False, locked=False):
    """Carta completa (como na tela de recompensa): moldura, raridade, arte, nome e descrição."""
    color = rarity_color(card)
    pygame.draw.rect(surface, (50, 50, 78) if active else (32, 32, 50), rect, border_radius=14)
    pygame.draw.rect(surface, color, rect, width=5 if active else 2, border_radius=14)
    draw_text(surface, rarity_name(card).upper(), 22, color, (rect.centerx, rect.y + 22))
    art = card_art(card, 120, locked)
    surface.blit(art, (rect.centerx - 60, rect.y + 36))
    pygame.draw.rect(surface, color, (rect.centerx - 62, rect.y + 34, 124, 124), width=3, border_radius=8)
    fit_text(surface, card["name"], 34, config.TEXT_COLOR, (rect.centerx, rect.y + 178), rect.width - 28)
    if card.get("character"):
        draw_text(surface, "EXCLUSIVA", 18, (255, 215, 90), (rect.centerx, rect.y + 200))
        top = rect.y + 212
    else:
        top = rect.y + 202
    draw_wrapped(surface, card["description"], 24, config.TEXT_COLOR, (rect.x + 20, top), rect.width - 40, 26)


def draw_card_thumb(surface, rect, card, badge=None, locked=False, active=False):
    """Miniatura (Loja/Álbum): arte quadrada na altura do retângulo + moldura da raridade. badge: texto curto opcional."""
    color = rarity_color(card)
    size = min(rect.width, rect.height)
    surface.blit(card_art(card, size, locked), (rect.x, rect.y))
    pygame.draw.rect(surface, (255, 255, 255) if active else color, (rect.x, rect.y, size, size), width=4 if active else 2, border_radius=6)
    if badge:
        draw_text(surface, badge, 16, (255, 255, 255), (rect.x + size // 2, rect.bottom - 10), shadow=True)
