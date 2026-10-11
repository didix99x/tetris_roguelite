"""
board/board.py - O TABULEIRO (lógica pura, sem desenhar nada).

grid[y][x] guarda um Block ou None. O cursor ocupa 2 células lado a lado
(cursor_x e cursor_x + 1) e trocar = inverter esses dois blocos.
"""
import random

import config
from board import gravity, matcher
from board.block import Block


class Board:
    def __init__(self, width=None, height=None, rng=None):
        self.width = width or config.BOARD_WIDTH
        self.height = height or config.BOARD_HEIGHT
        self.rng = rng or random.Random()
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]
        self.cursor_x = self.width // 2 - 1
        self.cursor_y = self.height // 2
        self.fill_initial()

    # ---------- consulta ----------
    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get(self, x, y):
        return self.grid[y][x] if self.in_bounds(x, y) else None

    def blocks(self):
        for row in self.grid:
            for block in row:
                if block is not None:
                    yield block

    def count_stones(self):
        return sum(1 for b in self.blocks() if b.is_stone)

    def count_webbed(self):
        return sum(1 for b in self.blocks() if b.is_webbed)

    def any_moving(self):
        return any(b.is_moving() for b in self.blocks())

    # ---------- criação ----------
    def _color_at(self, x, y):
        block = self.get(x, y)
        if block is None or block.is_stone:
            return None
        return block.color_id

    def safe_color(self, x, y):
        """Escolhe uma cor que NÃO forme um match imediato com os vizinhos."""
        banned = set()
        for dx, dy in ((1, 0), (0, 1)):
            a1 = self._color_at(x - dx, y - dy)
            a2 = self._color_at(x - 2 * dx, y - 2 * dy)
            b1 = self._color_at(x + dx, y + dy)
            b2 = self._color_at(x + 2 * dx, y + 2 * dy)
            if a1 and a1 == a2:
                banned.add(a1)
            if b1 and b1 == b2:
                banned.add(b1)
            if a1 and a1 == b1:
                banned.add(a1)
        all_colors = list(range(1, config.NUM_COLORS + 1))
        options = [c for c in all_colors if c not in banned]
        return self.rng.choice(options or all_colors)

    def fill_initial(self):
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = Block(self.safe_color(x, y), x, y)
        if not self.has_possible_move():
            self.reshuffle()

    # ---------- cursor e troca ----------
    def move_cursor(self, dx, dy):
        self.cursor_x = max(0, min(self.width - 2, self.cursor_x + dx))
        self.cursor_y = max(0, min(self.height - 1, self.cursor_y + dy))

    def set_cursor(self, x, y):
        self.cursor_x = max(0, min(self.width - 2, x))
        self.cursor_y = max(0, min(self.height - 1, y))

    def can_swap(self, x, y):
        """Pode trocar o bloco (x, y) com o da direita?"""
        a, b = self.get(x, y), self.get(x + 1, y)
        if a is None or b is None:
            return False
        if a.is_stone or b.is_stone or a.is_webbed or b.is_webbed:
            return False
        return a.color_id != b.color_id

    def swap_cursor(self):
        x, y = self.cursor_x, self.cursor_y
        if not self.can_swap(x, y):
            return False
        a, b = self.grid[y][x], self.grid[y][x + 1]
        self.grid[y][x], self.grid[y][x + 1] = b, a
        a.grid_x, b.grid_x = x + 1, x
        return True

    # ---------- matches ----------
    def find_matches(self):
        return matcher.find_matches(self.grid, self.width, self.height)

    def remove_cells(self, cells):
        """Remove as células dadas e também as PEDRAS vizinhas a elas."""
        to_remove = set(cells)
        for (x, y) in cells:
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                block = self.get(nx, ny)
                if block is not None and block.is_stone:
                    to_remove.add((nx, ny))
        removed = []
        for (x, y) in to_remove:
            block = self.grid[y][x]
            if block is not None:
                removed.append(block)
                self.grid[y][x] = None
        return removed

    def gravity_and_refill(self):
        gravity.apply_gravity(self.grid, self.width, self.height)
        gravity.refill(self.grid, self.width, self.height, self.safe_color)

    # ---------- jogadas possíveis ----------
    def has_possible_move(self):
        for y in range(self.height):
            for x in range(self.width - 1):
                if not self.can_swap(x, y):
                    continue
                a, b = self.grid[y][x], self.grid[y][x + 1]
                self.grid[y][x], self.grid[y][x + 1] = b, a
                found = bool(self.find_matches())
                self.grid[y][x], self.grid[y][x + 1] = a, b
                if found:
                    return True
        return False

    def reshuffle(self):
        """Reembaralha as cores até existir uma jogada e nenhum match pronto."""
        movable = [b for b in self.blocks() if not b.is_stone]
        for _ in range(300):
            colors = [self.rng.randint(1, config.NUM_COLORS) for _ in movable]
            for block, color in zip(movable, colors):
                block.color_id = color
            if not self.find_matches() and self.has_possible_move():
                return

    # ---------- atualização ----------
    def update(self, dt):
        for block in self.blocks():
            block.update(dt)
