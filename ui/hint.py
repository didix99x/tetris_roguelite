"""
ui/hint.py - DICA DE JOGADA (só visual).

find_hint procura uma troca que forma match numa CÓPIA do tabuleiro: o tabuleiro real nunca é tocado
e nenhuma jogada é executada. O destaque aparece depois de alguns segundos parado
(data/shop.json > hint > idle_seconds) e some assim que o jogador age.
"""
import copy
import math

import pygame


def find_hint(board):
    """(x, y) da troca (x,y)<->(x+1,y) que forma match, ou None. Não altera o tabuleiro recebido."""
    work = copy.deepcopy(board)
    for y in range(work.height):
        for x in range(work.width - 1):
            if not work.can_swap(x, y):
                continue
            work.set_cursor(x, y)
            work.swap_cursor()
            found = bool(work.find_matches())
            work.swap_cursor()                    # desfaz (na cópia)
            if found:
                return (x, y)
    return None


def draw_hint(surface, view, hint, time):
    """Contorno azul-claro pulsando em volta das duas peças da dica."""
    import config
    size = config.BLOCK_SIZE
    pulse = 0.5 + 0.5 * math.sin(time * 5)
    rect = pygame.Rect(view.x + hint[0] * size, view.y + hint[1] * size, size * 2, size)
    color = (int(110 + 80 * pulse), int(200 + 40 * pulse), 255)
    pygame.draw.rect(surface, color, rect.inflate(-2, -2), width=4, border_radius=10)
    pygame.draw.polygon(surface, color, [(rect.centerx - 7, rect.top - 9), (rect.centerx + 7, rect.top - 9), (rect.centerx, rect.top - 1)])
