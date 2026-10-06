"""
ui/board_view.py - DESENHA o tabuleiro (a lógica está em board/).

A posição do tabuleiro é calculada para ficar centralizado. Se mudar
BOARD_WIDTH / BOARD_HEIGHT / BLOCK_SIZE em config.py, ele se ajusta sozinho.
"""
import math

import pygame

import config


def _lighter(color, amount=45):
    return tuple(min(255, c + amount) for c in color)


def _darker(color, amount=45):
    return tuple(max(0, c - amount) for c in color)


class BoardView:
    def __init__(self):
        size = config.BLOCK_SIZE
        self.width_px = config.BOARD_WIDTH * size
        self.height_px = config.BOARD_HEIGHT * size
        self.x = (config.SCREEN_WIDTH - self.width_px) // 2
        self.y = (config.SCREEN_HEIGHT - self.height_px) // 2 + config.BOARD_Y_OFFSET
        self.rect = pygame.Rect(self.x, self.y, self.width_px, self.height_px)

    def cell_center(self, gx, gy):
        size = config.BLOCK_SIZE
        return (self.x + gx * size + size // 2, self.y + gy * size + size // 2)

    def cell_at(self, pos):
        """Célula (x, y) sob a posição do mouse, ou None se fora do tabuleiro."""
        if not self.rect.collidepoint(pos):
            return None
        size = config.BLOCK_SIZE
        return (int((pos[0] - self.x) // size), int((pos[1] - self.y) // size))

    def draw(self, surface, board, time, offset=(0, 0), show_cursor=True):
        size = config.BLOCK_SIZE
        ox, oy = int(self.x + offset[0]), int(self.y + offset[1])
        frame = pygame.Rect(ox, oy, self.width_px, self.height_px)
        pygame.draw.rect(surface, (12, 12, 20), frame.inflate(16, 16), border_radius=12)
        pygame.draw.rect(surface, (90, 90, 120), frame.inflate(16, 16), width=3, border_radius=12)
        pygame.draw.rect(surface, (24, 24, 36), frame)
        for gx in range(1, board.width):
            pygame.draw.line(surface, (34, 34, 50), (ox + gx * size, oy), (ox + gx * size, oy + self.height_px))
        for gy in range(1, board.height):
            pygame.draw.line(surface, (34, 34, 50), (ox, oy + gy * size), (ox + self.width_px, oy + gy * size))

        old_clip = surface.get_clip()
        surface.set_clip(frame)
        for block in board.blocks():
            self._draw_block(surface, block, ox, oy, time)
        surface.set_clip(old_clip)

        if show_cursor:
            self._draw_cursor(surface, board, ox, oy, time)

    def _draw_block(self, surface, block, ox, oy, time):
        size = config.BLOCK_SIZE
        margin = 3
        x = ox + block.visual_x * size + margin
        y = oy + block.visual_y * size + margin
        side = size - 2 * margin
        base = config.BLOCK_COLORS.get(block.color_id, (200, 200, 200))

        if block.clearing:
            shrink = block.clear_progress * side * 0.5
            rect = pygame.Rect(int(x + shrink), int(y + shrink),
                               int(side - 2 * shrink), int(side - 2 * shrink))
            flash = int(255 * (1 - block.clear_progress))
            color = (min(255, base[0] + flash // 2), min(255, base[1] + flash // 2), min(255, base[2] + flash // 2))
            pygame.draw.rect(surface, color, rect, border_radius=8)
            return

        rect = pygame.Rect(int(x), int(y), side, side)
        if block.is_stone:
            pygame.draw.rect(surface, base, rect, border_radius=8)
            pygame.draw.rect(surface, _darker(base, 35), rect, width=3, border_radius=8)
            pygame.draw.line(surface, _darker(base, 40), (rect.left + 10, rect.top + 14), (rect.right - 14, rect.centery), 3)
            pygame.draw.line(surface, _darker(base, 40), (rect.centerx, rect.centery), (rect.left + 18, rect.bottom - 10), 3)
            return

        pygame.draw.rect(surface, base, rect, border_radius=8)
        pygame.draw.rect(surface, _darker(base), rect, width=3, border_radius=8)
        shine = pygame.Rect(rect.x + 7, rect.y + 6, side // 2, side // 5)
        pygame.draw.rect(surface, _lighter(base), shine, border_radius=4)

        if block.is_webbed:
            white = (235, 235, 245)
            pygame.draw.line(surface, white, rect.topleft, rect.bottomright, 2)
            pygame.draw.line(surface, white, rect.topright, rect.bottomleft, 2)
            pygame.draw.line(surface, white, (rect.centerx, rect.top), (rect.centerx, rect.bottom), 2)
            pygame.draw.line(surface, white, (rect.left, rect.centery), (rect.right, rect.centery), 2)
            pygame.draw.circle(surface, white, rect.center, side // 4, 2)

    def _draw_cursor(self, surface, board, ox, oy, time):
        size = config.BLOCK_SIZE
        pulse = 0.5 + 0.5 * math.sin(time * 8)
        color = (255, int(200 + 55 * pulse), int(80 + 100 * pulse))
        rect = pygame.Rect(ox + board.cursor_x * size, oy + board.cursor_y * size, size * 2, size)
        pygame.draw.rect(surface, color, rect.inflate(2, 2), width=4, border_radius=10)
        pygame.draw.line(surface, color, (rect.centerx, rect.top + 6), (rect.centerx, rect.bottom - 6), 2)
